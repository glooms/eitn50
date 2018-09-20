import socket
import sys
import thread

class Peer(object):

    def __init__(self, host, server_port, client_port):
        self.host = host
        self.server_port = server_port
        self.client_port = client_port
        self.server_socket = self.setup_socket()
        self.client_socket = self.setup_socket(False)
        self.buffer = []

    def setup_socket(self, server=True):
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
        self.client_socket.send(msg)

    def set_receive(self, func):
        self.receive = func

    def receive(self, data):
        print ' '.join(['{0:X}'.format(ord(d)).zfill(2) for d in data])

    def start(self):
        self.server_thread = thread.start_new_thread(self.listen, ())

    def listen(self):
        while 1:
            data, addr = self.server_socket.recvfrom(64)
            self.receive(data)


