#!/usr/bin/env python
from __future__ import print_function
import time
import random
import sys
import ssl
import os
import json
import argparse
import logging
import atexit
import signal
import threading

import websocket
import miniupnpc

from time import strftime


from gi.repository import GObject, Gst
import gi
gi.require_version('Gst', '1.0')


from emitter import Emitter
from receiver import Receiver
from util import check_rtsp_port
from jack_client import JackClient


BANNER = """
*************************************************************
                      Matriz - Cliente
*************************************************************
"""

EMITTER_BIN = '../gst-src/emitter'
RECEIVER_BIN = '../gst-src/receiver'
SERVER_URL = "wss://matriz.stress.fm/config"

CONFIG = {
    "python": True,
    "receive": True,
    "key": "key2",
    "name": "",
    "url": "ws://matriz.stress.fm/config",
    "port": 8554,
    "record": False,
    "client_pem": "",
    "client_crt": "",
    "ca_crt": ""
}

LOGGER_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logger = logging.getLogger(__name__)


def _create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file',
                        type=str,
                        nargs="?",
                        default="client.json")
    parser.add_argument('-d',
                        '--debug',
                        action="store_true",
                        default=False)
    return parser


def main(arguments=sys.argv[1:]):
    parser = _create_parser()
    args = parser.parse_args(arguments)
    print(BANNER)
    if not(os.path.exists(args.config_file)):
        raise IOError("file {} does not exist!\n".format(args.config_file))
    print("\n*******************" +
          "  Program Started at: " +
          strftime("%Y-%m-%d %H:%M:%S") +
          "  ******************\n\n")
    if args.debug:
        logging.basicConfig(
            format=LOGGER_FORMAT,
            level=logging.DEBUG)
    else:
        # Log info and above to console
        logging.basicConfig(
            # format='%(levelname)s: %(message)s',
            format=LOGGER_FORMAT,
            level=logging.INFO
        )
    logging.debug("Options:")
    for key, value in (vars(args)).items():
        logging.debug("{0}: {1}".format(key, value))
    # Read config file
    with open(args.config_file) as f:
        config = json.load(f)
        logging.debug(config)
        CONFIG.update(config)
        config = CONFIG
        logging.debug(config)
    # Actually run the program
    matriz = Matriz(config)
    matriz()
    print("\n********************" +
          "  Program Ended at: " +
          strftime("%Y-%m-%d %H:%M:%S") +
          "  *******************\n\n")


class Matriz:

    emitter = False

    def __init__(self, config=None):
        self.config_server_url = config["url"]
        self.port = config["port"]
        self.python = config["python"]
        self.receive = config["receive"]
        self.name = config["name"]
        self.key = config["key"]
        self.record = config["record"]
        self.upnp_client = miniupnpc.UPnP()
        self.connection_attempts = 0
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.cleanup)
        GObject.threads_init()
        Gst.init(None)

    def on_message(self, ws, message):
        try:
            message = json.loads(message)
            logging.debug("Received message from server:")
            logging.debug(message)
        except:
            logging.debug("[Error] Couldn't read message: %s" % (message, ))
            return
        if not self.receive:
            return
        logging.debug("Running receivers: {}".format(Receiver.receivers))
        for client in message["clients"]:
            name = client["name"]
            if name in Receiver.receivers:
                logging.debug("Receiver for {} already running".format(name))
                continue
            elif name != self.name:
                logging.debug("Starting receiver for {}".format(name))
                receiver = Receiver(**client)
                receiver()
        # Check connected receivers and disconnect any that is not
        # on the client list obtained from server
        connected_client_names = [client["name"]
                                  for client in message["clients"]
                                  if client["name"] != self.name]
        for client_name in Receiver.receivers.copy():
            if client_name not in connected_client_names:
                Receiver.receivers[client_name].stop()
                logging.info("Receiver for {} disconnected".format(client_name))
        if "message" in message:
            logging.debug(message["message"])
        else:
            logging.debug(message)

    def on_error(self, ws, error):
        logging.info("ON_ERROR %s" % error)

    def on_close(self, ws):
        logging.info("### closed ###")

    def on_open(self, ws):
        first_message = json.dumps({
            "register": "",
            "name": self.name,
            "key": self.key,
            "port": self.port,
        })
        # print first_message
        ws.send(first_message)

        def run(*args):
            while True:
                a = raw_input("Waiting for commands...\n")
                if a == "end":
                    self.cleanup()
                    break
                elif a == "deregister":
                    ws.send(json.dumps({"deregister": "deregister"}))
                    break
            time.sleep(1)
            ws.close()
            logging.debug("Thread terminating...")
        # thread.start_new_thread(run, ())
        t = threading.Thread(target=run, args=())
        t.daemon = True
        t.start()

    def cleanup(self):
        logging.info("Performing cleanup.")
        for receiver in Receiver.receivers.copy():
            logging.debug("Shutting down receiver for {}.".format(receiver))
            Receiver.receivers[receiver].stop()
        if self.emitter is not None:
            logging.debug("Not shutting down emitter.")

    def get_port(self):
        logging.debug('Discovering... delay={}ums'.format(self.upnp_client.discoverdelay))
        ndevices = self.upnp_client.discover()
        logging.debug('{} device(s) detected'.format(ndevices))
        # select an igd
        logging.debug("Selecting IGD")
        self.upnp_client.selectigd()
        # display information about the IGD and the internet connection
        logging.debug('local ip address: {}'.format(self.upnp_client.lanaddr))
        externalipaddress = self.upnp_client.externalipaddress()
        logging.debug('external ip address: {}'.format(externalipaddress))
        logging.debug(self.upnp_client.statusinfo())
        logging.debug(self.upnp_client.connectiontype())

        while True and self.port < 65536:
            r = self.upnp.getgenericportmapping(self.port)
            if r is None:
                break
            logging.debug("port {} is occupied. Trying port {}".format(self.port, self.port + 2))
            self.port += 2
        self.upnp_client.addportmapping(self.port,
                                        'TCP',
                                        self.upnp_client.lanaddr,
                                        self.port,
                                        '{} - Matriz emitter'.format(self.name),
                                        '')

    def start_loop(self):
        self.loop = threading.Thread(target=GObject.MainLoop().run)
        self.loop.daemon = True
        self.loop.start()

    def __call__(self):
        self.start_loop()
        # self.get_port()
        self.emitter = Emitter(port=self.port, record=self.record)
        self.emitter()
        while not check_rtsp_port(port=self.port):
            time.sleep(0.1)
        # self.jack_client = JackClient()
        # self.jack_client()
        self.connect()

    def connect(self):
        time.sleep(random.randrange(0, 2**self.connection_attempts))
        self.connection_attempts += 1
        # websocket.enableTrace(True)
        ws = websocket.WebSocketApp(self.config_server_url,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        ws.on_open = self.on_open
        if self.config_server_url.startswith("wss://"):
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_REQUIRED,
                                   "ca_certs": ca_cert,
                                   "ssl_version": ssl.PROTOCOL_TLSv1_2,
                                   "keyfile": client_pem,
                                   "certfile": client_crt})
        else:
            ws.run_forever()

    def debug(self):
        import code
        code.interact(local=locals())


if __name__ == "__main__":
    main()
