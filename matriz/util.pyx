import socket


def check_rtsp_port(address='127.0.0.1', port=8554):
    s = socket.socket()
    try:
        s.connect((address, int(port)))
    except socket.error as e:
        return False
    return True
