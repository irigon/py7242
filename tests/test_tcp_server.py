import unittest
import os, sys
import socket
import threading
import time
import selectors


sys.path.insert(0, os.path.abspath('.'))

from libs import tcp_server


# TODO:
# currently I dont test multiple connections against the server (since it blocks on listen)

## the next function simulates a user connecting to the server
def user_connecting(port, id=0):
    #time.sleep(0.5)  # wait the thread to connect to the server, so mytrigger should be called and output set to 1
    with  socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        host = '127.0.0.1'
        print("{} connecting to {}:{}".format(id, host, port))
        s.connect((host, port))
        s.setblocking(False)
        s.sendall(b'data... ')
        time.sleep(1)


def is_port_openned(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('127.0.0.1', port))
    return result == 0

class TestTCPServer(unittest.TestCase):

    def setUp(self):
        self.myport = 10000

    # Verify that a high port is free, start the tcp server on this port and verify that it is used afterwards
    # Call server stop and verify that the port is not used anymore
    # Restart reconnection and verify that no error occurs and that the port is open
    def test_create_tcp_server(self):
        ts = tcp_server.TCP_Server(self.myport, 1)
        self.assertFalse(is_port_openned(self.myport))
        ts.start()
        self.assertTrue(ts.is_running())
        self.assertTrue(is_port_openned(self.myport))
        ts.stop()
        self.assertFalse(is_port_openned(self.myport))

    # test if an event is triggered "on_connect" event
    def test_connect(self):
        output=0

        # if my trigger is called, it set the output variable to 1
        def mytrigger(input):
            return input + 1

        # this is usually part of the TCPCL_Controller.
        # In order to test TCP_Server separately, we created a standalone instance
        m_selector = selectors.DefaultSelector()

        # Instantiate TCP_Server and start listening to self.myport
        ts = tcp_server.TCP_Server(self.myport, max_conn=1, selector=m_selector)
        ts.start()

        # register callback
        m_selector.register(ts.socket, selectors.EVENT_READ, mytrigger)

        # create the client thread
        # this could be in fact done in the non blocking, non threading way:
        # https://docs.python.org/3/howto/sockets.html
        t = threading.Thread(target=user_connecting, args=(self.myport,))
        t.daemon = True
        t.start()

        # the main thread should capture the connection request and trigger "mytrigger", updating output
        for k, mask in m_selector.select():
            callback = k.data
            output = callback(output)

        self.assertEqual(output, 1)

