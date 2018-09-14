import json


# This file is written in python 2.7
# I recommend importing it into shell, e.g. by: python -i <name of this file>

class HexBuffer:

    _buffer = []
    FAT1 = []
    FAT2 = []
    dir_structure = {'root': []}

    def __init__(self, fp='part1/image.dat'):
        self.f = open(fp, 'rb') # Open the filepath 'fp' as binary
        self.load(350) # This is the whole file
        self.get_FATs()

    def load(self, step=1, size=512): # Load the next sector into the buffer
        # Reads the next 'size' (default=512) bytes as hexadecimal numbers padded to two digits.
        self._buffer += [format(ord(b), 'X').zfill(2) for b in self.f.read(step * size)]

    def get(self, i, k=1, dec=True): # Gets the bytes from i to i + k.
        # Default k=1 meaning only the byte at offset i is returned.
        # If the dec flag is True (as is default) the retrieved information is
        # returned in decimal format, otherwise in hexadecimal.
        s = ''.join(self._buffer[i:i + k][::-1])
        if dec:
            return hex_to_dec(s)
        return s

    def get_as_str(self, i, k=1): # Gets the bytes from i to i + k as a string.
        return ''.join([hex_to_char(x) for x in self._buffer[i:i + k]])

    def get_cluster(self, i):
        k = i * 512
        return self._buffer[k:k + 512]

    def hex_dump(self, i, k=1): # Returns the contents of the buffer from i to i + k
        return ' '.join(self._buffer[i:i + k])

    def get_FATs(self):
        self.FAT1 = self._FAT_decode(self.hex_dump(512, 512 * 9))
        self.FAT2 = self._FAT_decode(self.hex_dump(512 * 10, 512 * 9))

    def _FAT_decode(self, dump):
        arr = dump.split(' ')
        fat = []
        for i in xrange(0, len(arr), 3):
            fat += [arr[i + 1][0] + arr[i]]
            fat += [arr[i + 2] + arr[i + 1][1]]
        return fat

    def get_cluster_chain(self, a):
        chain = []
        while a not in chain and a < len(self.FAT1) - 3 and a > 1:
            chain += [a]
            a = hex_to_dec(self.FAT1[a])
        return chain

    def read_cluster_chain(self, a):
        content = []
        chain = self.get_cluster_chain(a)
        print chain
        for c in chain:
            content += self.get_cluster(31 + c)
        return content
    
    def explore_dir(self, d):
        if not 'dir' in d['attr']:
            return
        chain = self.get_cluster_chain(d['first_clust'])
        content = []
        for index in chain:
            content += self.explore_cluster(index)
        self.dir_structure[d['name']] = content
        for d in content:
            if '.' in d['name']:
                continue
            self.explore_dir(d)

    def explore_cluster(self, index, logical=True):
        i = index
        if logical:
            if i < 2:
                return
            i += 31
        elif i < 19:
            return
        i *= 512
        stop = i + 512
        content = []
        while i < stop:
            if self._buffer[i] == '00':
                pass
            elif not self.get(i + 11) & 7:
                content += [{
                    'name': self.get_as_str(i, 8),
                    'ext': self.get_as_str(i + 8, 3),
                    'attr': interpret_attributes(self.get(i + 11)),
                    'cr_time': dec_to_time(self.get(i + 14, 2)),
                    'cr_date': dec_to_date(self.get(i + 16, 2)),
                    'last_acc': dec_to_date(self.get(i + 18, 2)),
                    'lw_time': dec_to_time(self.get(i + 22, 2)),
                    'lw_date': dec_to_date(self.get(i + 24, 2)),
                    'first_clust': self.get(i + 26, 2),
                    'abs_offset': i,
                    'filesize': self.get(i + 28, 4)
                }]
            i += 32
        return content

    def simple_dir_struct(self):
        ds = {}
        for k, v in self.dir_structure.iteritems():
            ds[k] = [d['name'] for d in v]
        return ds


def hex_to_dec(x): # Hexadecimal number to decimal
    s = str(x)
    return int(s, 16)


def hex_to_char(x): # Hexadecimal number to character
    return chr(hex_to_dec(x)).decode('latin-1')


def dec_to_date(x):
    b = '{0:b}'.format(x).zfill(16)
    day = int(b[:4][::-1], 2)
    month = int(b[5:8][::-1], 2)
    year = 1980 + int(b[9:][::-1], 2)
    return '%d-%02d-%02d' % (day, month, year)


def dec_to_time(x):
    b = '{0:b}'.format(x).zfill(16)[::-1]
    s = int(b[:4][::-1], 2) * 2
    m = int(b[5:10][::-1], 2)
    h = int(b[11:][::-1], 2)
    return '%02d:%02d:%02d' % (h, m, s)


def interpret_attributes(x):
    attr = []
    if x & 1:
        attr += ['read-only']
    if x & 2:
        attr += ['hidden']
    if x & 4:
        attr += ['system']
    if x & 8:
        attr += ['vol id']
    if x & 16:
        attr += ['dir']
    if x & 32:
        attr += ['archive']
    return attr


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
    for i in xrange(19, 33):
        hb.dir_structure['root'] += hb.explore_cluster(i, False)
    for d in hb.dir_structure['root']:
        hb.explore_dir(d)
