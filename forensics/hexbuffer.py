class HexBuffer:

    _buffer = []

    def __init__(self, fp='part1/image.dat'):
        self.f = open(fp, 'rb')
        self.load()

    def load(self, size=512):
        self._buffer += [format(ord(b), 'X').zfill(2) for b in self.f.read(512)]

    def get(self, i, k=1, dec=True):
        s = ''.join(self._buffer[i:i + k])
        if dec:
            return hex_to_dec(s)
        return s

    def get_as_str(self, i, k=1):
        return ''.join([hex_to_char(x) for x in self._buffer[i:i + k]])


def hex_to_dec(x):
    s = str(x)
    return int(s, 16)

def hex_to_char(x):
    return chr(hex_to_dec(x))

hb = HexBuffer()

boot_info = {
        'bootaddress' : hb.get(1),
        'oem_name': hb.get_as_str(3, 8),
        'bytes_per_sector' : hb.get(11, 2),
        'sectors_per_cluster' : hb.get(13),
        'reserved_sectors' : hb.get(14, 2),
        'num_fats' : hb.get(16),
        'root_entries' : hb.get(17, 2),
        'total_sector_count' : hb.get(19, 2),
        'media' : hb.get(21, 1, False), #?
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

import json
print json.dumps(boot_info, indent=2, sort_keys=True)
