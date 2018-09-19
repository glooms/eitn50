from peer import Peer
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, ParameterFormat

'''
    Proposed communication protocol
    00000001 Handshake
'''

class DHPeer(Peer):
    
    def __init__(self, **kwargs):
        super(DHPeer, self).__init__(**kwargs)

    def gen_params(self):
        self.params = dh.generate_parameters(
            generator=2,
            key_size=512,
            backend=default_backend()
        )

    def send_params(self):
        param_bytes = self.params.parameter_bytes(Encoding.DER, ParameterFormat.PKCS3)
        print [hex(ord(x)) for x in param_bytes]
        super(DHPeer, self).send(param_bytes) # Too big.. doesn't send it all
        
    def start_handshake(self):
        self.private_key = self.params.generate_private_key()
        self.public_key = self.private_key.generate_public_key()


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
