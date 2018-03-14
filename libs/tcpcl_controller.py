import selectors
import sys

from libs import tcpcl_convergence_layer
from libs import tcp_server
from libs import command_line_helper



class TCPCL_Controller:

    # design decisions:
    # cl & CLH are created on init, in order to break as
    # soon as possible in case of CL creation errors.

    def __init__(self, cl_id):
        self.id = cl_id
        self.cl = tcpcl_convergence_layer.TCPCL_CL(self.id)
        self.clh = command_line_helper.CLH(self)
        self.selector = selectors.DefaultSelector()
        data = {'func':self.recv_user_input}
        self.selector.register(sys.stdin, selectors.EVENT_READ, data)
        self.tcp_server = None    # tcp_server is optional, do not instantiate on creation
        self.peers = dict()
        self.shutdown = False

    # register a peer
    def register(self, cl_id, ip, port):
        print('Registering cl_id {}:ip {}:port {}'.format(cl_id, ip, port))
        self.peers[cl_id] = (ip, port)

    def unregister(self, cl_id):
        self.peers.pop(cl_id)


    # register a peer in upcn. The peer should be already locally registered
    def upcn_register(self, cl_id):
        assert cl_id in self.peers
        pass

    # start listening in port 'port' for connections
    def server_start(self, port, max_conn):
        if self.tcp_server is None:         # New server
            self.tcp_server = tcp_server.TCP_Server(max_conn, self.recv_new_connection, self.selector)
        elif self.tcp_server.is_running():  # For simplicity we will start at most one server
            print('Server is already running. Stop it first.')
            return
        self.tcp_server.start(port)

    # stop connection
    # clean up
    def server_stop(self):
        if self.tcp_server:
            self.tcp_server.stop()
        else:
            print('There is no server running')

    def server_status(self):
        if self.tcp_server is not None and self.tcp_server.is_running():
            print('Server is running')
        else:
            print('Server is not running')


    '''
    # start a connection to a already registered peer
    def start_client(self, cl_id):
        if cl_id not in self.peers:
            print('cl_id {} not known. Register it first.'.format(cl_id))
            return
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(0)    # non-blocking socket
        # an event will be triggered in case the connection was successfuly.
        data = {'func':self.cl.connect}
        self.selector.register(s, selectors.EVENT_WRITE, data)
        self.cl.connect(s)

        # should I also create an event for read?
    '''

    def recv_user_input(self, stdin, data):
        input_line = stdin.read()
        if input_line == '':           # ctrl + d
            print('User pressed ctrl+d, exiting...')
            self.exit()
        else:
            args = input_line.rstrip().split()
            if len(args) > 0:
                self.clh.parse(*args) # ignore input as \n or \r, process otherwise

    def recv_new_connection(self, sock, data):
        new_conn, addr = sock.accept()
        new_conn.setblocking(False)
        print('Accepting connection from {}'.format(addr))
        data = {'func':self.cl.receive, 'selector':self.selector}
        self.selector.register(new_conn, selectors.EVENT_READ, data)

    def exit(self):
        self.shutdown = True




