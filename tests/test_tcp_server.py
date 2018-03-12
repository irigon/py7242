import unittest
import os, sys
import socket
import threading
import time
import selectors


sys.path.insert(0, os.path.abspath('.'))

from libs import tcp_server


# TODO:
# currently I dont know how to test multiple connections against the server (since it blocks on listen)
# the register callback is also currently not tested

## the next function simulates a user connecting to the server
def user_connecting(port):
    time.sleep(0.5)  # wait the thread to connect to the server, so mytrigger should be called and output set to 1
    with  socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        host = '127.0.0.1'
        print("connecting to {}:{}".format(host, port))
        s.connect((host, port))
        s.sendall(b'data... ')


def is_port_openned(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('127.0.0.1', port))
    return result == 0

class TestTCPServer(unittest.TestCase):

    # Verify that a high port is free, start the tcp server on this port and verify that it is used afterwards
    # Call server stop and verify that the port is not used anymore
    # Restart reconnection and verify that no error occurs and that the port is open
    def test_create_tcp_server(self):
        myport = 10000
        ts = tcp_server.TCP_Server(myport, 1)
        self.assertFalse(is_port_openned(myport))
        ts.start()
        self.assertTrue(ts.is_running())
        self.assertTrue(is_port_openned(myport))
        ts.stop()
        self.assertFalse(is_port_openned(myport))

    # test if an event is triggered on connection event
    def test_connect(self):
        output=0
        def mytrigger(input):
            return input + 1    # if my trigger is called, it set the output variable to 1
        myport = 10000
        m_selector = selectors.DefaultSelector()

        ts = tcp_server.TCP_Server(myport, 1, m_selector)
        ts.start()
        # set callback
        m_selector.register(ts.socket, selectors.EVENT_READ, mytrigger)

        t = threading.Thread(target=user_connecting, args=(myport,))
        t.daemon = True
        t.start()
        for k, mask in m_selector.select():
            callback = k.data
            output = callback(output)

        self.assertEqual(output, 1)






