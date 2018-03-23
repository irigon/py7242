# Self-Delimiting Numeric Values (SDVNs) -- https://tools.ietf.org/html/rfc5050
import struct

from libs import flags

# given a big int, return an array of encoded bytes
def encode(data):
    encoded = b''
    hbit = 0
    while True:
        byte = hbit | (data & 0x7f)
        hbit = 1 << 7                       # just first byte with hbit==0
        encoded = struct.pack('B', byte) + encoded
        data = data >> 7                    # consume next 7 bits
        if data == 0:
            break
    return encoded

# given an array of bytes, return an int
def decode(data, offset=0):
    decoded = 0
    for idx, ch in enumerate(data[offset:]):
        decoded <<=7
        decoded |= (ch & 0x7f)
        if not ch & 0x80:
            break
    return decoded, idx + 1                # size = idx+1

'''
# https://tools.ietf.org/html/rfc5050#section-4.5
# [sdvn] fields have variable size
# [x], means that it takes x bytes (size)
def serialize_bundle(flags, destination, source, report_to, custodian, creation_ts, lifetime, dict, payload):
    # [1] add version
    msg = b"\x06"    # version 6

    # [sdvn] addr proc flags (bundle processing control)
    msg += encode(flags)

    # [sdvn] add block length
    payload = bytearray()
    payload += flags.BPCF_v6.BLOCK_TYPE_PAYLOAD   # type payload
    # [sdvn] add destination scheme offset
    # [sdvn] add destination ssp offset
    # [sdvn] add source scheme offset
    # [sdvn] add source ssp offset
    # [sdvn] add report-to scheme offset
    # [sdvn] add report to ssp offset
    # [sdvn] add custodian scheme offset
    # [sdvn] add custodian ssp offset
    # [sdvn in the primary block] add creation timestamp time
    # [sdvn in the primary block] add creation timestamp sequenc number
    # [sdvn in the primary block] add lifetime
    # [sdvn in the primary block] add dictionary length
    # add dictionary byte array
    # add fragment offset if fragment flag in the block's processing flags byte is set to 1
    # total application data unit length (present if the block's processing flags byte is set to 1
    ### Payload
    # [sdvn in the payload] add block processing control ("Proc.")
    # [sdvn in the payload] add block length field of the payload
    pass
'''