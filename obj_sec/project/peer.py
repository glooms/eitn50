import socket
import sys
import thread

class Peer:

    def __init__(self, host='', server_port=5000, client_port=5001):
        self.host = host
        self.server_port = server_port
        self.client_port = client_port
        self.server_socket = self.setup_socket()
        self.client_socket = self.setup_socket(False)
        self.msg_buffer = []

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

    def start(self):
        self.server_thread = thread.start_new_thread(self.listen, ())

    def listen(self):
        while 1:
            data, addr = self.server_socket.recvfrom(1024)
            self.msg_buffer += [data]
            print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()


if __name__ == '__main__':
    a = Peer()
    b = Peer('', 5001, 5000)
    a.start()
    b.start()
