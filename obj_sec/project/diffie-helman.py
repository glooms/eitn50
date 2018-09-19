from random import randint

class Client:

    def __init__(self, p=23, g=5):
        self.p = p
        self.g = g

    def pair(self, client):
        self.client = client
        client.set_base(self.p, self.g)
        self.client.pair(self)

    def set_base(self, p, g):
        self.p = p
        self.g = g

    def new_secret(self):
        self.private_secret = randint(0, 10)

    def send(self):
        return self.g ** self.private_secret % self.p

    def compute_shared_secret(self, d):
        self.new_secret()
        
        self.shared_secret = d ** self.private_secret % self.p




