#!/usr/bin/env python
"""
TODO: Standardize response messages
{
    "clients": [{"stream": True|False, "name": "montemor|porto|lisboa|monitor",
          "ip": "111.111.11.11", "port": 8554}],
    "message": "some string",
    "label": "some string"
}
"""

from flask import Flask
from flask.ext.uwsgi_websocket import GeventWebSocket, GeventWebSocketClient

import socket

import os
import json
from subprocess import Popen, PIPE, STDOUT

import logging

LOGGER_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger(__name__)
logging.basicConfig(
    format=LOGGER_FORMAT,
    level=logging.DEBUG)


if "MATRIZ_CONFIG_FILE" in os.environ:
    config_file = os.environ['MATRIZ_CONFIG_FILE']
else:
    config_file = 'clients.json'

if os.path.exists(config_file):
    cfg = open(config_file, 'r')
    config = json.load(cfg)
    try:
        client_keys = [client["key"] for client in config['client_keys']]
        monitor_key = config['monitor_key']["key"]
    except:
        print "Bad configuration file: %s" % (config_file)
        exit(1)
    cfg.close()

else:
    print "No configuration file found"
    exit(1)

clients = {}
# webclients = []
monitor = False
clients_for_web = {
    "lisboa": False,
    "porto": False,
    "montemor": False,
    "refresh": False,
    "restart": False
}


app = Flask(__name__)
websocket = GeventWebSocket(app)


def config_liq():
    """
    Change IPs for lisboa,porto,montemor
    Restart Liquidsoap if necessary
    """

    liq_file = "/etc/liquidsoap/matriz.liq"
    info = {}
    # logging.debug("config_liq getclients() %s" % get_clients()[0])

    for i in get_clients()[0]:
        info[i["name"]] = i["ip"]

    seds = []
    for k, v in info.iteritems():
        seds += ['-e', 's/^%s .*/%s = "%s"/' % (k, k, v)]
    # logging.debug("Func liq_restart [seds]: %s" % seds)

    cmd = ['sed', '-i'] + seds + [liq_file]
    # logging.debug("Func liq_restart [cmd_sed]: %s" % cmd)
    p = Popen(cmd)
    p.wait()
    # TODO: Check if uptime is less then 10 sec - do not restart
    cmd = ['sudo', '/usr/local/bin/supervisorctl', 'restart', 'liquidsoap']
    p = Popen(cmd, stdout=PIPE, stderr=STDOUT)
    out, err = p.communicate()
    logging.debug("[Func liq_restart]: %s" % cmd)
    logging.debug("[stdout] '%s'" % out)
    # logging.debug("[stderr] '%s'" % err)
    return True


def check_rtsp_port(address=None, port=8554):
    s = socket.socket()
    s.settimeout(5.0)
    con = True
    try:
        s.connect((address, int(port)))
        con = True
        mes = "Port %d at %s is open" % (int(port), address,)
    except socket.error as e:
        con = False
        mes = "%s" % e

    return (con, mes)


def get_clients(web=False, rliq=False, refresh=False):

    if web:
        cl_w = {'restart': rliq, "refresh": refresh}
        for c in clients:
            clients_for_web[clients[c].name] = clients[c].stream
            cl_w[clients[c].name] = clients[c].stream
        for k, v in clients_for_web.iteritems():
            if k not in cl_w:
                cl_w[k] = False
        return cl_w
    else:
        cl = [{"ip": clients[c].ip, "stream": clients[c].stream,
               "name": clients[c].name, "port": clients[c].port} for c in client_keys if c in clients]
    return (cl, len(cl))


def sanitize_to_json(s):
    """
    Convert the string that come through the websockets to json
    We get it an escaped string
    """
    return json.loads(s.decode('string-escape').strip('"'))


class Client(object):

    webclients = []

    def __init__(self, ws=False):
        # logging.debug("Initiating client:")
        # logging.debug(ws.environ['REMOTE_ADDR'])
        self.ws = ws
        self.stream = False
        self.ip = False
        self.key = False
        self.name = ""
        self.registered = False

        if isinstance(ws, GeventWebSocketClient):
            self.ip = ws.environ['REMOTE_ADDR']
            self.ws_id = ws.id

    def register(self):
        # logging.debug("Starting Register")
        restart_liquidsoap = False
        if self.key in client_keys:
            rtsp_port = self.port
            response = {"name": self.name, "ip": self.ip, "port": rtsp_port}

            # logging.debug("checking port")
            check = check_rtsp_port(address=self.ip, port=rtsp_port)

            if check[0]:
                # logging.debug("istream is True")
                self.stream = True
            else:
                # logging.debug("stream is False")
                self.stream = False
            response.update({"stream": self.stream, "message": check[1]})
            logging.debug("[Register %s] %s" % (response["name"], response))

            self.registered = True
            clients[self.key] = self
            c = get_clients()
            response.update({"clients": c[0], "n_clients": c[1]})
            self.ws.send(json.dumps(response))
            msg = "[%s] connected to config server" % self.name
            self.broadcast({"message": msg, "clients": get_clients()[0]})
            self.monitor({"action": "register", "clients": get_clients()[0],
                          "message": "[%s] connected with IP %s" % (self.name, self.ip)})
            config_liq()

        elif self.key == monitor_key:
            global monitor
            monitor = self
            self.name = "monitor"
            c = get_clients()
            if not c[1]:
                self.monitor(
                    {"status": "ok", "message": "No clients connected"})
            else:
                self.monitor({"status": "ok",
                              "message": "\n".join(["[%s] connected with IP %s" % (t["name"], t["ip"])
                                                    for t in c[0]])})
        elif self.name == "webclient":
            # self.registered = True
            self.webclients += [self]
            self.web = True
            cl = get_clients(web=True, rliq=restart_liquidsoap)
            logging.debug("For WEBCLIENT: %s" % (cl, ))
            self.ws.send(json.dumps(cl))

        else:
            self.deregister()
        # logging.debug("End Register")

    def deregister(self):
        # TODO: Check if rtsp stream is up and broadcast to clients
        if self.name == "monitor":
            global monitor
            monitor = False
        elif self.registered:
            del clients[self.key]
            clients_for_web[self.name] = False
            logging.debug("[%s] DeRegistered" % (self.name))
        self.ws.close()
        self.monitor(
            {"status": "ok", "message": "[%s] disconnected" %
                    (self.name), "clients": get_clients()[0]})
        msg = "[%s] disconnected from config server" % self.name
        self.broadcast({"message": msg,
                        "clients": get_clients()[0]})

    def monitor(self, m):
        if not isinstance(monitor, Client):
            logging.debug("No monitor to send message")
            return False
        info = "Connected clients: %d" % (len(clients) - 1)
        message = json.dumps({"message": m["message"],
                              "info": info,
                              "clients": get_clients()[0]})
        monitor.ws.send(message)

    def broadcast(self, msg, web=True, rliq=False):
        # logging.debug("Broadcast message [%s]: %s" % (type(msg), msg))
        msg.update({"name": self.name,
                    "clients": get_clients()[0]})
        msgj = json.dumps(msg)
        for c in client_keys:
            if c in clients and c != self.key:
                clients[c].ws.send(msgj)

        if web:
            if "refresh" in msg:
                refresh = True
            else:
                refresh = False

            webcl = json.dumps(
                get_clients(web=True, rliq=rliq, refresh=refresh))
            logging.debug("Web Message: %s" % (webcl,))
            for wc in self.webclients:
                wc.ws.send(webcl)
            return True

        self.monitor(msg)


@websocket.route('/config')
def socket_ws(ws):
    client = Client(ws=ws)
    response = ws.receive()
    # Message comes escaped
    try:
        msg = sanitize_to_json(response)
    except:
        msg = {}
    # if msg["name"] == "webclient":
    #    print msg
    if "register" in msg and "name" in msg and "key" in msg:
        client.name = msg["name"]
        client.key = msg["key"]
        if "port" in msg:
            client.port = msg["port"]
        client.register()
    else:
        ws.close()
    while ws.connected is True:
        msg = ws.receive()
        try:
            msg = sanitize_to_json(msg)
        except:
            msg = {}
            continue
        if "deregister" in msg:
            break
        elif "refresh" in msg:
            client.broadcast(msg, rliq=False)
            logging.debug("[288]brodcast_message: %s" % (msg, ))
            continue
        elif not msg:
            continue
        msg.update({"clients": get_clients()[0]})
        client.broadcast(msg)
    # if client.name != "webclient":
    client.deregister()


def main():
    app.run(gevent=100)

if __name__ == "__main__":
#    app.run(debug=True,
#            https="127.0.0.1:8080,fake_server.crt,fake_server.key,HIGH,!fake_ca.crt",
#            master=True,
#            processes=1,
#            threads=1,
#            gevent=100)

    app.run(debug=True,
            gevent=100)
