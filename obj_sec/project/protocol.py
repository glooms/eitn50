from enum import Enum

'''
    Protocol proposal:

    The header is a total of 4 bytes.

    First 7 bits represents what action is performed.
    
    100000: Establish base
    010000: Establish secret
    001000: Send obj (ENC)

    8th bit represents an ack, so 0b01000001 would be secret ack.

    Since we are limited to send only 64 byte messages,
    the data has to be divided into packets and we have to
    communicate how many packages should be received.

    Therefore I propose the second byte keeping track of just that.
    One solution is by having the first 4 bits indicate the amount of packets
    being sent and the following 4 indicating which packet it is.
    E.g.:   0x31 first packet of 3 incoming.
            0x32 second
            0x33 last
   
    The common secret will be the key to open the object.

    The following 2 bytes will contain a session id so that packets can be
    tracked, somewhat. We might not want to send this unencrypted.
'''


class Protocol(Enum):
    BASE    = 0b10000000 # Contains the base parameters
    SECRET  = 0b01000000 # Contains information to setup a common secret
    SEND    = 0b00100000 # Contains encrypted objects
    ACK     = 0b00000001 # Acknowledge 

    SECRET_ACK = SECRET + ACK
    SEND_ACK = SEND + ACK
