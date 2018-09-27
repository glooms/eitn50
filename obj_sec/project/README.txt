To run the code in testmode write:

python -i dhpeer.py

which will give you a python shell context with two peers a and b.

To setup a peer write:

python -i dhpeer.py <host_ip> <remote_ip> <host_port> <remote_port> <log_file_name>

in the python shell you should have a peer which you can use to send python dicts.

Example:

peer.send({'msg': 'Are you there peer?'})

You can examine the log files to get details of what has transpired.
The objects sent and received are printed in clear text in the log file (although, only the first 80 characters are included)

You can examine the last received object by:

peer.last_received()


Note that the cryptography and jose directories are include libraries. The only files you need to examine is dhpeer.py, peer.py and protocol.py. 
