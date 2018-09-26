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

    Let l be the number of packets being sent.

    The first packet will have this byte set to l - 1.

    The following packets will count upwards, starting at 0 until l - 2.
    We will in this way be able to send data up to 60 * 256 bytes divided into a maximum
    of 256 packets.

    The common secret will be the key to open the object.

    The following 2 bytes will contain a session id so that packets can be
    tracked, somewhat. We might not want to send this unencrypted.
'''


class Protocol:
    BASE    = 0b10000000 # Contains the base parameters
    SECRET  = 0b01000000 # Contains information to setup a common secret
    SEND    = 0b00100000 # Contains encrypted objects
    ACK     = 0b00000001 # Acknowledge 

    SECRET_ACK = SECRET + ACK
    SEND_ACK = SEND + ACK
