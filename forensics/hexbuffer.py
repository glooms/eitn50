import json

# This file is written in python 2.7
# I recommend importing it into shell, e.g. by: python -i <name of this file>

class HexBuffer:

    _buffer = []

    def __init__(self, fp='part1/image.dat'):
        self.f = open(fp, 'rb') # Open the filepath 'fp' as binary
        self.load()

    def load(self, size=512): # Load the next sector into the buffer
        # Reads the next 'size' (default=512) bytes as hexadecimal numbers padded to two digits.
        self._buffer += [format(ord(b), 'X').zfill(2) for b in self.f.read(512)]

    def get(self, i, k=1, dec=True): # Gets the bytes from i to i + k.
        # Default k=1 meaning only the byte at offset i is returned.
        # If the dec flag is True (as is default) the retrieved information is
        # returned in decimal format, otherwise in hexadecimal.
        s = ''.join(self._buffer[i:i + k])
        if dec:
            return hex_to_dec(s)
        return s

    def get_as_str(self, i, k=1): # Gets the bytes from i to i + k as a string.
        return ''.join([hex_to_char(x) for x in self._buffer[i:i + k]])

    def hex_dump(self, i, k=1): # Returns the contents of the buffer from i to i + k
        return ' '.join(self._buffer[i:i + k])


def hex_to_dec(x): # Hexadecimal number to decimal
    s = str(x)
    return int(s, 16)


def hex_to_char(x): # Hexadecimal number to character
    return chr(hex_to_dec(x))


def pp(d): # Pretty print dictionaries/lists.
    print json.dumps(d, indent=2, sort_keys=True)


if __name__ == '__main__': # Main method in python
    hb = HexBuffer() # Create an instance of HexBuffer class
    boot_info = { # A dictionary (approx Java's Map), containing the boot information.
            'bootaddress' : hb.get(1),
            'oem_name': hb.get_as_str(3, 8),
            'bytes_per_sector' : hb.get(11, 2),
            'sectors_per_cluster' : hb.get(13),
            'reserved_sectors' : hb.get(14, 2),
            'num_fats' : hb.get(16),
            'root_entries' : hb.get(17, 2),
            'total_sector_count' : hb.get(19, 2),
            'media' : hb.get(21, 1, False),
            'fat_size' : hb.get(22, 2),
            'sector_per_track' : hb.get(24, 2),
            'num_heads' : hb.get(26, 2),
            'hidden_sectors' : hb.get(28, 4),
            'drive_number' : hb.get(36),
            'volume_serial_number' : hb.get(39, 4),
            'volume_label' : hb.get_as_str(43, 11),
            'filesys_type' : hb.get_as_str(54, 8),
            'boot_signature' : hb.get(510, 2, False)
    }
