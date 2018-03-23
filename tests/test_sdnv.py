import unittest
import sys, os

sys.path.insert(0, os.path.abspath('.'))
from libs import sdnv
from libs.tcpcl_convergence_layer import TCPCL_CL

class TestSDVN(unittest.TestCase):

    def setUp(self):
        pass

    # tests from https://tools.ietf.org/html/rfc5050
    def test_enc_dec(self):
        encoded = sdnv.encode(0xABC)
        self.assertEqual(encoded, b'\x95<')     # 10010101 00111100
        decoded = sdnv.decode(encoded)
        self.assertEqual(decoded[0], 0xABC)

        encoded = sdnv.encode(0x1234)
        self.assertEqual(encoded, b'\xa44')     # 10100100 00110100
        decoded = sdnv.decode(encoded)
        self.assertEqual(decoded[0], 0x1234)

        encoded = sdnv.encode(0x4234)
        self.assertEqual(encoded, b'\x81\x844') # 10000001 10000100 00110100
        decoded = sdnv.decode(encoded)
        self.assertEqual(decoded[0], 0x4234)

        encoded = sdnv.encode(0x7F)
        self.assertEqual(encoded, b'\x7f')      # 01111111
        decoded = sdnv.decode(encoded)
        self.assertEqual(decoded[0], 0x7F)

        encoded = sdnv.encode(0x0)
        self.assertEqual(encoded, b'\x00')
        decoded = sdnv.decode(encoded)
        self.assertEqual(decoded[0], 0x0)





