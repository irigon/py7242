import argparse
import fcntl
import sys
import os
import selectors
import logging

class CLH:
    def __init__(self, controller):
        logging.getLogger(__name__)
        logging.info('Initializing {}'.format(__class__.__name__))
        self.controller = controller
        self.valid_commands = dict()
        self.register_cmds()
        self.conf_parser()

    def register_callback(self, selector, callback):
        self.set_input_nonblocking()
        selector.register(sys.stdin, selectors.EVENT_READ, {'func':callback})

    def set_input_nonblocking(self):
        orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

    def register_cmds(self):
        for func in [self.clear, self.connect, self.disconnect, self.exit, self.nexthop,
                     self.show_peers, self.server, self.register, self.register_upcn_node,
                     self.reconnect, self.unregister, self.send_to]:
            self.valid_commands[func.__name__] = func

    def conf_parser(self):
        self.parser = argparse.ArgumentParser(usage='%(prog)s [options]')
        subparsers = self.parser.add_subparsers(title='commands', description='list of available commands')
        sp_connect = subparsers.add_parser('connect', description='connect to a tcpcl node')
        sp_connect.add_argument('addr', type=str, help='destination address')
        sp_connect.add_argument('port', type=int, help='destination port')
        sp_disconnect = subparsers.add_parser('disconnect', description='disconnects from a registered peer')
        sp_disconnect.add_argument('id', type=str, help='peer id')
        sp_exit = subparsers.add_parser('exit', description='exit tcpcl')
        sp_next_hop = subparsers.add_parser('nexthop', description='set "default route"')
        sp_next_hop.add_argument('id', type=str, help='next hop id')
        sp_reconnect = subparsers.add_parser('reconnect', description='restarts connection to peer')
        sp_reconnect.add_argument('id', type=str, help='peer id')
        sp_register = subparsers.add_parser('register', description='register/update peer node (debug)')
        sp_register.add_argument('id', type=str, help='peer id')
        sp_register.add_argument('ip', type=str, help='peer ip address')
        sp_register.add_argument('port', type=int, help='peer port')
        sp_register_upcn = subparsers.add_parser('register_upcn', description='register/update peer node (debug)')
        sp_register_upcn.add_argument('upcn_id', type=str, help='upcn id')
        sp_register_upcn.add_argument('node_id', type=str, help='node id to be registered')
        sp_register_upcn.add_argument('path', type=str, help='path to the contact map file')
        #sp_send = subparsers.add_parser('send', description='send bundle to a peer')
        #sp_send.add_argument('id', type=str, help='peer id')
        #sp_send.add_argument('message', type=str, help='a string to be sent')
        sp_send_to = subparsers.add_parser('send_to', description='send a string to a peer')
        sp_send_to.add_argument('id', type=str, help='peer id')
        sp_send_to.add_argument('message', type=str, help='a string to be sent')
        sp_show = subparsers.add_parser('show_peers', description='show system information')
        sp_server = subparsers.add_parser('server', description='tcp server commands')
        sp_server.add_argument('action', choices=['start', 'stop', 'status'], type=str, help='start/stop/status')
        sp_server.add_argument('port', nargs='?', type=int, help='port number to which the server should listen')
        sp_server.add_argument('max_conn', nargs='?', type=int, help='max number of connections the server should handle')
        sp_unregister = subparsers.add_parser('unregister', description='unregister node (debug)')
        sp_unregister.add_argument('id', type=str, help='peer id')

    def new_parser(self, *arglist):
        try:
            nspace=self.parser.parse_args(arglist)
        except:
            if sys.exc_info()[1].code == 0:  # valid command as --help/-h, invalid commands have code (2)
                pass
            else:
                print('{} is not a valid command. Try -h/--help'.format(list(arglist)))
        else:
            method_name=arglist[0]
            if method_name in self.valid_commands:
                self.valid_commands[method_name](nspace)


    ## -- Commands

    def clear(self, ns):
        os.system('clear')

    def connect(self, ns):
        self.controller.cl.connect(ns)

    def disconnect(self, ns):
        logging.info('Mock: disconnect')

    def exit(self, ns):
        self.controller.exit()

    def nexthop(self, ns):
        self.controller.cl.set_next_hop(ns)

    def show_peers(self, *args):
        self.controller.cl.show_peers()

    def server(self, ns):
        self.controller.server(ns)

    def register(self, ns):
        self.controller.register_id_manually(ns)

    def register_upcn_node(self, ns):
        logging.info('Mock: register_upcn_node')

    def reconnect(self, ns):
        logging.info('Mock: reconnect')

    def unregister(self, ns):
        self.controller.unregister(ns)

    def send_to(self, ns):
        self.controller.cl.send_to(ns)

    def register_upcn(self, ns):
        pass # to be implemented