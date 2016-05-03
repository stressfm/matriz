#!/usr/bin/env python
import websocket
try:
    import thread
except ImportError:  # TODO use Threading instead of _thread in python3
    import _thread as thread
import threading
import time
import sys
import ssl
import os
import json

from subprocess import Popen, PIPE
import threading

cfg_file = 'monitor.json'
ca_cert = "ca.crt"

if not os.path.exists(cfg_file):
    print "No configuration file %s" % (cfg_file,)
    exit(1)

try:
    f = open(cfg_file, 'r')
    cfg = json.load(f)
    client_pem = cfg["client_pem"]
    client_crt = cfg["client_crt"]
    if "key" not in cfg:
        print "error reading %s" % (cfg_file)
        exit(1)
    monitor_key = cfg['key']
    cfg["name"] = cfg["key"]
    ws_url = cfg['url']
    f.close()
except:
    print "error reading %s" % (cfg_file)
    exit(1)


def on_message(ws, message):
    try:
        message = json.loads(message)
    except:
        print "[Error] Couldn't read message: %s" % (message, )
        # return False
        message = {}

    if "info" in message:
        print "info: %s" % message["info"]
    if "message" in message:
        print "message: %s" % message["message"]
    else:
        print "Debug: %s" % message


def on_error(ws, error):
    print "ON_ERROR %s" % error


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    first_message = json.dumps({
        "register": "",
        "name": cfg["name"],
        "key": cfg["key"]
    })
    # first_message = {
    #     "register": "",
    #     "name": cfg["name"],
    #     "key": cfg["key"]
    #     }
    ws.send(first_message)
    def run(*args):
        #for i in range(3):
    # send the message, then wait
    # so thread doesn't exit and socket
    # isn't closed
         #   ws.send("Hello %d" % i)
         #   time.sleep(1)
        while True:
            r = raw_input()
            if r == "refresh":
                print r
                ws.send(json.dumps({"refresh": True}))
            if r == "exit":
                print "EXIT"
                ws.close()
                break

        print "EXITED"

        #time.sleep(1)
        ws.close()
        print("Thread terminating...")

    #thread.start_new_thread(run, ())
    t = threading.Thread(target=run, args=(ws,))
    t.daemon = True
    t.start()



def main():
    # websocket.enableTrace(True)
    if len(sys.argv) < 2:
        host = ws_url
    else:
        host = sys.argv[1]
    ws = websocket.WebSocketApp(host,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    if host.startswith("wss://"):
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_REQUIRED,
                               "ca_certs": ca_cert,
                               "ssl_version": ssl.PROTOCOL_TLSv1_2,
                               "keyfile": client_pem,
                               "certfile": client_crt})
    else:
        ws.run_forever()


if __name__ == "__main__":
    main()
