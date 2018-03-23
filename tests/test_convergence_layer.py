import unittest
import sys, os

sys.path.insert(0, os.path.abspath('.'))

from libs.tcpcl_convergence_layer import TCPCL_CL

# A TCP convergence layer shall have one tcp connection.
# When the convergence layer is destroyed, the tcp connection is also destroyed
# The send method sends data through the socket connection
# The register method is tested in the "test_convergence_layer" test
# The restart method restarts the socket connection (will that change the descriptor)

class TestTCPCLConnection(unittest.TestCase):

    def setUp(self):
        pass

    def test_enc_dec_header(self):
        tcpcl = TCPCL_CL('testCL')
        curr_encoded_header = tcpcl.encode_header()
        encoded_header = b'dtn!\x03\x00\x00\x00\x06testCL'
        self.assertEqual(curr_encoded_header, encoded_header)
