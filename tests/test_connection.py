import unittest
import sys, os
import selectors
import socket

sys.path.insert(0, os.path.abspath('.'))

from libs import tcpcl_connection

class TestTCPCL_Connection(unittest.TestCase):

    def setUp(self):
        self.selector = selectors.DefaultSelector()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tc_conn = tcpcl_connection.TCPCL_Connection(self.socket, self.selector)

    def tearDown(self):
        self.selector.close()

    def test_tcpcl_register(self):
        func = lambda x: x
        self.tc_conn.register_callback(func)
        self.assertEquals(self.tc_conn.data['func'], func)

    def test_enqueue(self):
        self.tc_conn.enqueue('bla')
        self.assertEqual(self.tc_conn.out_msg_queue[0], 'bla')



