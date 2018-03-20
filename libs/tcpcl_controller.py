import selectors

from libs import tcpcl_convergence_layer
from libs import tcp_server
from libs import command_line_helper



class TCPCL_Controller:

    # design decisions:
    # cl & CLH are created on init, in order to break as
    # soon as possible in case of CL creation errors.
    def __init__(self, cl_id):
        self.id = cl_id
        self.selector = selectors.DefaultSelector()
        self.cl = tcpcl_convergence_layer.TCPCL_CL(self.id, self.selector)
        self.clh = command_line_helper.CLH(self)
        self.clh.register_callback(self.selector, self.recv_user_input)
        self.tcp_server = None    # tcp_server is optional, do not instantiate on creation
        self.shutdown = False

    # this function is called from command line and it is a wrapper for the function
    # that belongs to convergence layer, that sets the id when the header arrives
    def register_id_manually(self, ns):
        # if cl_id exists, ignore
        if ns.id in self.cl.connections:
            print('{} is already set to the connection: {}. Ignoring...'.
                  format(ns.id, self.cl.connections[ns.id].getpeername()))
            return

        # if (ip, port) exists, rename it.
        for list in [self.cl.connections, self.cl.unnamed_connections]:
            for key, conn in list.items():
                if conn.getpeername() == (ns.ip, ns.port):
                    item = list.pop(key)
                    item.peer_id = ns.id
                    break
        self.cl.connections[ns.id]=item


    def unregister(self, ns):
        pass


    # register a peer in upcn. The peer should be already locally registered
    def upcn_register(self, ns):
        pass

    def server(self, ns):
        if ns.action == 'start':
            if ns.max_conn is None or ns.port is None:
                print('On server start parameters "max_con" and "port" are required.')
                return
            if self.tcp_server is None:  # New server
                self.tcp_server = tcp_server.TCP_Server(ns.max_conn, self.cl.recv_new_connection, self.selector)
            elif self.tcp_server.is_running():  # For simplicity we will start at most one server
                print('Server is already running. Stop it first.')
                return
            self.tcp_server.start(ns.port)
        elif ns.action == 'stop':
            if self.tcp_server:
                self.tcp_server.stop()
                print('Stopping server...')
            else:
                print('There is no server running')
        elif ns.action == 'status':
            if self.tcp_server is not None and self.tcp_server.is_running():
                print('Server is running')
            else:
                print('Server is not running')

    def recv_user_input(self, stdin, data, mask):
        input_line = stdin.read()
        if input_line == '':           # ctrl + d
            print('User pressed ctrl+d, exiting...')
            self.exit()
        else:
            args = input_line.rstrip().split()
            if len(args) > 0:
                #self.clh.parse(*args) # ignore input as \n or \r, process otherwise
                self.clh.new_parser(*args) # ignore input as \n or \r, process otherwise

    def exit(self):
        self.shutdown = True




