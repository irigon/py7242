import fcntl
import sys
import os

class CLH:
    def __init__(self, controller):
        self.set_input_nonblocking()
        self.valid_commands = dict()
        self.register_known_commands()
        self.controller = controller

    def set_input_nonblocking(self):
        orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

    def register_known_commands(self):
        self.register_cmd('connect $id',
                          '\t\t\tconnects to a registered peer. ',
                          self.connect)
        self.register_cmd('exit', '\t\t\t\t\texit program', self.exit)
        self.register_cmd('help', '\t\t\t\t\tshow this help', self.help)
        self.register_cmd('next_hop $id',
                          '\t\t\tset peer $id as default route. ',
                          self.next_hop)
        self.register_cmd('reconnect $id',
                          '\t\t\trestarts connection to peer.',
                          self.reconnect)
        self.register_cmd('register $id $ip $port', 'register peer node', self.register)
        self.register_cmd('send $message $id',
                          '\t\tsend message (array of bytes) to a peer). ',
                          self.send)
        self.register_cmd('startserver $port',
                          '\t\tstart tcpserver at port "port" (default port:10000)',
                          self.tcpserver)
        self.register_cmd('statusserver', '\t\t\tinform about tcpserver status [running/stopped]', self.tcpserver)
        self.register_cmd('stopserver', '\t\t\tstop tcp server', self.tcpserver)
        self.register_cmd('upcn_register $id',
                          '\t\tregister node with upcn a running server. ',
                          self.register_upcn_node)


    def register_cmd(self, alias, help,  func):
        cmd_name = alias.split()[0]
        self.valid_commands[cmd_name] = (help, func)

    def parse(self, cmd, *args, **kwargs):
        if cmd in self.valid_commands:
            method = self.valid_commands[cmd][1]
            return method(args, kwargs)
        else:
            print('Invalid input. Try "help" for valid commands.')
            return 0

    ## -- Commands

    def connect(self, *args, **kwargs):
        print('Mock: connect')
        return 0

    def exit(self, *args, **kwargs):
        return -1

    def help(self, *args, **kwargs):
        print('Command line help: ')
        for c in sorted(self.valid_commands):
            print('    {}: {}'.format(c, self.valid_commands[c][0]))
        return 0

    def next_hop(self, *args, **kwargs):
        print('Mock: set_next_hop')
        return 0

    def tcpserver(self, *args, **kwargs):
        print('Mock: tcpserver')
        return 0

    def register(self, *args, **kwargs):
        print('Mock: register_node')
        return 0

    def register_upcn_node(self, *args, **kwargs):
        print('Mock: register_upcn_node')
        return 0

    def reconnect(self, *args, **kwargs):
        print('Mock: reconnect')
        return 0

    def send(self, *args, **kwargs):
        print('Mock: send')
        return 0
