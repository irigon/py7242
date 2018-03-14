import selectors
import sys

from libs import tcpcl_convergence_layer
from libs import tcp_server
from libs import command_line_helper



class TCPCL_Controller:

    # design decisions:
    # tcpcl & CLH are created on init, in order to break as
    # soon as possible in case of CL creation errors.

    def __init__(self, tcpcl_id):
        self.id = tcpcl_id
        self.tcpcl = tcpcl_convergence_layer.TCPCL_CL(self.id)
        self.clh = command_line_helper.CLH(self)
        self.selector = selectors.DefaultSelector()
        self.selector.register(sys.stdin, selectors.EVENT_READ, self.recv_user_input)
        self.tcp_server = None    # tcp_server is optional, do not instantiate on creation
        self.peers = dict()
        self.shutdown = False

    # register a peer
    def register(self, tcpcl_id, ip, port):
        print('Registering tcpcl_id {}:ip {}:port {}'.format(tcpcl_id, ip, port))
        self.peers[tcpcl_id] = (ip, port)

    def unregister(self, tcpcl_id):
        self.peers.pop(tcpcl_id)


    # register a peer in upcn. The peer should be already locally registered
    def upcn_register(self, tcpcl_id):
        assert tcpcl_id in self.peers
        pass

    # start listening in port 'port' for connections
    def start_server(self, port):
        if self.tcp_server is None:         # New server
            self.tcp_server = tcp_server.TCP_Server(port, max_conn=5)
        elif self.tcp_server.is_running():  # For simplicity we will start at most one server
            return
        else:                               # Restart if it was stopped
            self.tcp_server.start()

    # start a connection to a already registered peer
    def start_client(self, tcpcl_id):
        assert tcpcl_id in self.peers
        pass

    def recv_user_input(self, stdin, controller):
        input_line = stdin.read()
        if input_line == '':           # ctrl + d
            print('User pressed ctrl+d, exiting...')
            self.exit()
        else:
            args = input_line.rstrip().split()
            if len(args) > 0:
                self.clh.parse(*args) # ignore input as \n or \r, process otherwise

    def exit(self):
        self.shutdown = True




