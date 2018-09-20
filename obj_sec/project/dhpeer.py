from peer import Peer
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, ParameterFormat, PublicFormat, load_der_parameters, load_der_public_key

'''
    Protocol proposal:

    First byte represents what action is performed.
    
    0x01: Establish base
    0x11: Base established
    0x02: Establish secret
    0x22: Secret established
    0x03: Send encrypted stuff

    Since we are limited to send only 64 byte messages,
    the data has to be divided into packets and we have to
    communicate how many packages should be received.

    Therefore I propose the second byte keeping track of just that.
    One solution is by having the first 4 bits indicate the amount of packets
    being sent and the following 4 indicating which packet it is.
    E.g.:   0x31 first packet of 3 incoming.
            0x32 second
            0x33 last
'''


class DHPeer(Peer):
    
    def __init__(self, **kwargs):
        super(DHPeer, self).__init__(**kwargs)
        self.backend = default_backend()
        self.buffer = []
        self.remaining = {}

    def gen_params(self):
        self.params = dh.generate_parameters(
            generator=2,
            key_size=512,
            backend=self.backend
        )

    def send(self, packet_type, data=None):
        if data:
            packets = [data[i * 62: (i + 1) * 62] for i in xrange(len(data) / 62 + 1)]
            pack_count = len(packets) * 16
            for i, packet in enumerate(packets): 
                header = chr(packet_type) + chr(pack_count + i + 1)
                super(DHPeer, self).send(header + packet)
        else:
            header = chr(packet_type) + chr(0x11)
            super(DHPeer, self).send(header)

    def send_params(self):
        param_bytes = self.params.parameter_bytes(Encoding.DER, ParameterFormat.PKCS3)
        self.send(0x01, param_bytes)

    def send_param_ack(self):
        self.send(0x11)

    def init_handshake(self):
        self.private_key = self.params.generate_private_key()
        public_key = self.private_key.public_key()
        self.send_public_key(public_key)

    def ack_handshake(self, peer_key):
        self.private_key = self.params.generate_private_key()
        public_key = self.private_key.public_key()
        self.send_public_key_ack(public_key)
        self.exchange(peer_key)

    def exchange(self, peer_key):
        self.shared_key = self.private_key.exchange(peer_key)

    def send_public_key(self, pub_key):
        pub_key_bytes = pub_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
        self.send(0x02, pub_key_bytes)

    def send_public_key_ack(self, pub_key):
        pub_key_bytes = pub_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
        self.send(0x22, pub_key_bytes)

    def receive(self, data):
        self.buffer += [data]
        self.handle_header(data[:2])

    def handle_header(self, header):
        data_flag = ord(header[0])
        if not data_flag in self.remaining:
            self.remaining[data_flag] = (ord(header[1]) & 0xF0) >> 4
        self.remaining[data_flag] -= 1
        if self.remaining[data_flag]:
            return
        packets = self.all_received(data_flag)
        if packets:
            if data_flag == 0x01:
                self.load_params(packets)
                self.send_param_ack()
            elif data_flag == 0x11:
                # Nothing, base established
                pass
            elif data_flag == 0x02:
                peer_key = self.load_peer_key(packets)
                self.ack_handshake(peer_key)
            elif data_flag == 0x22:
                peer_key = self.load_peer_key(packets)
                self.exchange(peer_key)
                pass


    def all_received(self, data_flag):
        f = lambda x : ord(x[0]) == data_flag
        packets = filter(f, self.buffer)
        flags = [ord(p[1]) for p in packets]
        cnt = flags[0] & 0xF0
        indexes = [f & 0x0F for f in flags]
        r = range(1, cnt + 1)
        for i in indexes:
            if not i in r:
                return None
        return packets

    def load(self, packets):
        data = []
        for packet in packets:
            data += self.strip_packet(packet)
        return data

    def load_params(self, packets):
        param_data = self.load(packets)
        self.params = load_der_parameters(param_data, self.backend)

    def load_peer_key(self, packets):
        key_data = self.load(packets)
        return load_der_public_key(key_data, self.backend)

    def strip_packet(self, packet):
        return packet[2:]


def test(port1=5000, port2=5001):
    a = DHPeer(host='', server_port=port1, client_port=port2)
    b = DHPeer(host='', server_port=port2, client_port=port1)
    a.start()
    b.start()
    return (a, b)

if __name__ == '__main__':
    a, b = test()
    a.gen_params()
    a.send_params()
    a.init_handshake()

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
