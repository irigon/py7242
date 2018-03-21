import selectors
import sys
import logging

from libs import tcpcl_convergence_layer
from libs import tcp_server
from libs import command_line_helper
from libs import sdnv


class TCPCL_Controller:

    # design decisions:
    # cl & CLH are created on init, in order to break as
    # soon as possible in case of CL creation errors.
    def __init__(self, cl_id):
        logging.getLogger(__name__)
        logging.info('Initializing TCPCL_Controller')
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
        logging.debug('registering_id_manually(ns:{})'.format(ns))
        # if cl_id exists, ignore
        if ns.id in self.cl.connections:
            logging.warning('{} is already set to the connection: {}. Ignoring...'.
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
        logging.debug('unregister')

    # register a peer in upcn. The peer should be already locally registered
    def upcn_register(self, ns):
        pass
    
    def server(self, ns):
        if ns.action == 'start':
            logging.debug('On server start - ns: {}'.format(ns))
            if ns.max_conn is None or ns.port is None:
                logging.warning('On server start parameters "max_con" and "port" are required.')
                return
            if self.tcp_server is None:  # New server
                self.tcp_server = tcp_server.TCP_Server(ns.max_conn, self.cl.recv_new_connection, self.selector)
            elif self.tcp_server.is_running():  # For simplicity we will start at most one server
                logging.warning('Server is already running. Stop it first.')
                return
            self.tcp_server.start(ns.port)
        elif ns.action == 'stop':
            logging.debug('server stop - ns: {}'.format(ns))
            if self.tcp_server:
                self.tcp_server.stop()
                logging.info('Stopping server...')
            else:
                logging.warning('There is no server running')
        elif ns.action == 'status':
            logging.debug('server status - ns: {}'.format(ns))
            if self.tcp_server is not None and self.tcp_server.is_running():
                logging.info('Server is running')
            else:
                logging.info('Server is not running')

    def recv_user_input(self, stdin, data, mask):
        logging.debug('On revc_user_input. Data: {}'.format(data))
        input_line = stdin.read()
        if input_line == '':           # ctrl + d
            logging.info('User pressed ctrl+d, exiting...')
            self.exit()
        else:
            args = input_line.rstrip().split()
            if len(args) > 0:
                #self.clh.parse(*args) # ignore input as \n or \r, process otherwise
                self.clh.new_parser(*args) # ignore input as \n or \r, process otherwise
        sys.stdout.write('tcpcl> ')
        sys.stdout.flush()

    def exit(self):
        logging.info('On exit...')
        self.shutdown = True




