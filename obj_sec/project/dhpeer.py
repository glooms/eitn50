from peer import Peer
from protocol import Protocol
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.serialization import Encoding, ParameterFormat, PublicFormat, load_der_parameters, load_der_public_key
from jose import jwt

class DHPeer(Peer):
    
    def __init__(self, **kwargs):
        super(DHPeer, self).__init__(**kwargs)
        self.backend = default_backend()
        self.buffer_limit = 300
        self.session_counter = 0
        self._buffer = []
        self._remaining = {}
        self._sending_obj = None

    def setup_base(self):
        self._gen_params()
        self._send_params()

    def _gen_params(self):
        self.log('Generating parameters.')
        self.params = dh.generate_parameters(
            generator=2,
            key_size=512,
            backend=self.backend
        )

    def send(self, obj):
        self._sending_obj = obj
        self._init_handshake()

    def _send(self, packet_type, data=None):
        if data and len(data) > 60 * 0x7F:
            print 'Packet too big to send. It is %d bytes, max is %d' % (len(data), 60 * 0x7F)
            return
        session = '{0:b}'.format(self.session_counter).zfill(16)
        session_str = chr(int(session[:8], 2)) + chr(int(session[8:], 2))
        if data:
            packets = [data[i * 60: (i + 1) * 60] for i in xrange(len(data) / 60 + 1)]
            for i, packet in enumerate(packets):
                pack_id = i - 1
                if pack_id == -1:
                    pack_id = len(packets) - 1
                header = chr(packet_type) + chr(pack_id) + session_str
                payload = header + packet
                super(DHPeer, self).send(payload)
        else:
            header = chr(packet_type) + chr(0x11) + session_str
            super(DHPeer, self).send(header)
        self.session_counter += 1

    def _send_obj(self):
        obj = self._sending_obj
        self.log('Encrypting object.')
        enc_obj = jwt.encode(obj, self.shared_key, algorithm='HS256')
        self.log('Sending object.')
        self._send(Protocol.SEND.value, enc_obj)
        self._sending_obj = None

    def _decrypt(self, enc_obj):
        self.log('Object received.')
        self.log('Decrypting object.')
        obj = jwt.decode(u''.join(enc_obj), self.shared_key, algorithms='HS256')
        return obj

    def _send_params(self):
        self.log('Sending parameters.')
        param_bytes = self.params.parameter_bytes(Encoding.DER, ParameterFormat.PKCS3)
        self._send(Protocol.BASE.value, param_bytes)

    def _init_handshake(self):
        self.log('Generating private key.')
        self.private_key = self.params.generate_private_key()
        self.log('Generating public key.')
        public_key = self.private_key.public_key()
        self._send_public_key(public_key)

    def _ack_handshake(self, peer_key):
        self.log('Received peer public key.')
        self.log('Generating private key.')
        self.private_key = self.params.generate_private_key()
        self.log('Generating public key.')
        public_key = self.private_key.public_key()
        self._send_public_key_ack(public_key)
        self._exchange(peer_key)

    def _exchange(self, peer_key):
        self.log('Computing shared key.')
        self.shared_key = self.private_key.exchange(peer_key)

    def _send_public_key(self, pub_key):
        self.log('Sending public key.')
        pub_key_bytes = pub_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
        self._send(Protocol.SECRET.value, pub_key_bytes)

    def _send_public_key_ack(self, pub_key):
        self.log('Sending public key.')
        pub_key_bytes = pub_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
        self._send(Protocol.SECRET_ACK.value, pub_key_bytes)

    def _receive(self, data):
        self._buffer += [data]
        self._handle_header(data[:4])
        if len(self._buffer) > self.buffer_limit:
            self._buffer = self._buffer[-20:]

    def _handle_header(self, header):
        data_flag = ord(header[0])
        if not data_flag in self._remaining:
            self._remaining[data_flag] = ord(header[1]) + 1
        self._remaining[data_flag] -= 1
        if self._remaining[data_flag]:
            return
        session_id = header[2:]
        packets = self._all_received(data_flag, session_id)
        if packets:
            if data_flag == Protocol.BASE.value:
                self._load_params(packets)
            elif data_flag == Protocol.SECRET.value:
                peer_key = self._load_peer_key(packets)
                self._ack_handshake(peer_key)
            elif data_flag == Protocol.SECRET_ACK.value:
                peer_key = self._load_peer_key(packets)
                self._exchange(peer_key)
                if self._sending_obj:
                    self._send_obj()
            elif data_flag == Protocol.SEND.value:
                enc_obj = self._load_enc_obj(packets)
                obj = self._decrypt(enc_obj)
                self.received_object = obj

    def _all_received(self, data_flag, session_id):
        f = lambda x : ord(x[0]) == data_flag and x[2:4] == session_id
        packets = filter(f, self._buffer)
        flags = [ord(p[1]) for p in packets]
        cnt = flags[0]
        r = range(0, cnt + 1)
        for f in flags:
            if not f in r:
                return None
        del(self._remaining[data_flag])
        return packets

    def _load(self, packets):
        data = []
        for packet in packets:
            data += self._strip_packet(packet)
        return data

    def _load_params(self, packets):
        self.log('Received parameters.')
        param_data = self._load(packets)
        self.params = load_der_parameters(param_data, self.backend)

    def _load_peer_key(self, packets):
        key_data = self._load(packets)
        return load_der_public_key(key_data, self.backend)

    def _load_enc_obj(self, packets):
        return self._load(packets)

    def _strip_packet(self, packet):
        return packet[4:]


def test(port1=5000, port2=5001):
    a = DHPeer(host='', server_port=port1, client_port=port2, log_name='a.log')
    b = DHPeer(host='', server_port=port2, client_port=port1, log_name='b.log')
    a.start()
    b.start()
    return (a, b)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print 'TEST MODE'
        print 'Run with host, server_port, client_port and' \
                'log file name arguments for normal mode.'
        a, b = test()
        a.setup_base()
        d = {'swe': 'Hej', 'en': 'Hello', 'pt': 'Ola'}
        a.send(d)
    elif len(sys.argv) == 5:
        host, sp, cp, log_name = sys.argv[1:]
        peer = DHPeer(host=host, server_port=int(sp), client_port=int(cp), log_name=log_name)
        peer.start()


def run_tests():
    test1()
    test2()
    test3()
    test4()

def test1():
    p_a = a.params.parameter_numbers()._p
    p_b = b.params.parameter_numbers()._p
    assert p_a == p_b
    print 'Test 1 passed.'

def test2():
    s_a = a.shared_key
    s_b = b.shared_key
    assert s_a == s_b
    print 'Test 2 passed.'

def test3():
    sent_obj = d
    rec_obj = b.received_object
    assert sent_obj == rec_obj
    print 'Test 3 passed.'

def test4():
    large_obj = {u'' + str(i) :range(100) for i in xrange(18)}
    b.send(large_obj)
    import time; time.sleep(1)
    rec_obj = a.received_object
    assert large_obj == rec_obj
    print 'Test 4 passed.'
