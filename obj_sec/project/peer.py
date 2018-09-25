import socket
import sys
import thread

class Peer(object):

    def __init__(self, host, server_port, client_port):
        self.host = host
        self.server_port = server_port
        self.client_port = client_port
        self._server_socket = self._setup_socket()
        self._client_socket = self._setup_socket(False)

    def _setup_socket(self, server=True):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if server:
                s.bind((self.host, self.server_port))
            else:
                s.connect((self.host, self.client_port))
        except e:
            print e
            sys.exit()
        return s

    def send(self, msg):
        self._client_socket.send(msg)

    def _receive(self, data):
        print ' '.join(['{0:X}'.format(ord(d)).zfill(2) for d in data])

    def start(self):
        self.server_thread = thread.start_new_thread(self._listen, ())

    def _listen(self):
        while 1:
            data, addr = self._server_socket.recvfrom(64)
            self._receive(data)
