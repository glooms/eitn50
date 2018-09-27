import socket
import sys
import thread

class Peer(object):

    def __init__(self, host, remote, host_port, remote_port, log_name):
        self.host = host
        self.remote = remote
        self.host_port = host_port
        self.remote_port = remote_port
        self._host_socket = self._setup_socket()
        self._remote_socket = self._setup_socket(False)
        self._log_file = open(log_name, 'w')
        self._log_cnt = 0

    def _setup_socket(self, host=True):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if host:
                s.bind((self.host, self.host_port))
            else:
                s.connect((self.remote, self.remote_port))
        except Exception as e:
            print e
            sys.exit()
        return s

    def send(self, msg):
        self._remote_socket.send(msg)

    def _receive(self, data):
        print ' '.join(['{0:X}'.format(ord(d)).zfill(2) for d in data])

    def start(self):
        self.server_thread = thread.start_new_thread(self._listen, ())

    def _listen(self):
        while 1:
            data, addr = self._host_socket.recvfrom(64)
            self._receive(data)
    
    def log(self, text):
        if len(text) > 80:
            text = text[:80] + '...'
        self._log_file.write('Entry %d:\t%s\n' % (self._log_cnt, text))
        self._log_file.flush()
        self._log_cnt += 1

