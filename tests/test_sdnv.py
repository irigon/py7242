import unittest
import sys, os

sys.path.insert(0, os.path.abspath('.'))
from libs.sdnv import SDNV


class TestSDVN(unittest.TestCase):

    def setUp(self):
        pass

    # tests from https://tools.ietf.org/html/rfc5050
    def test_encode(self):
        encoded = SDNV(0xABC).encode()
        self.assertEqual(encoded, b'\x95<')     # 10010101 00111100
        decoded = SDNV(encoded).decode()
        self.assertEqual(decoded, 0xABC)

        encoded = SDNV(0x1234).encode()
        self.assertEqual(encoded, b'\xa44')     # 10100100 00110100
        decoded = SDNV(encoded).decode()
        self.assertEqual(decoded, 0x1234)

        encoded = SDNV(0x4234).encode()
        self.assertEqual(encoded, b'\x81\x844') # 10000001 10000100 00110100
        decoded = SDNV(encoded).decode()
        self.assertEqual(decoded, 0x4234)

        encoded = SDNV(0x7F).encode()
        self.assertEqual(encoded, b'\x7f')      # 01111111
        decoded = SDNV(encoded).decode()
        self.assertEqual(decoded, 0x7F)

        encoded = SDNV(0x0).encode()
        self.assertEqual(encoded, b'\x00')
        decoded = SDNV(encoded).decode()
        self.assertEqual(decoded, 0x0)

