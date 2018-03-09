# Self-Delimiting Numeric Values (SDVNs) -- https://tools.ietf.org/html/rfc5050

import struct

class SDNV:
    # data should be an array of bytes
    def __init__(self, data):
        self.data = data

    # given a big int, return an array of encoded bytes
    def encode(data):
        encoded = b''
        hbit = 0
        while True:
            byte = hbit | (data & 0x7f)
            hbit = 1 << 7                       # just first byte with hbit==0
            encoded = struct.pack('B', byte) + encoded
            data = data >> 7          # consume next 7 bits
            if data == 0:
                break
        return encoded

    # given an array of bytes, return an int
    def decode(data):
        decoded = 0
        for byte in data:
            decoded <<=7
            decoded |= (byte & 0x7f)
        return decoded

