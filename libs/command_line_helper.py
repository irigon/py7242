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
                          '\t\t\tconnects to a registered peer.',
                          self.connect)
        self.register_cmd('clear',
                          '\t\t\t\t\tclear screen.',
                          self.clear)
        self.register_cmd('exit', '\t\t\t\t\texit program', self.exit)
        self.register_cmd('help', '\t\t\t\t\tshow this help', self.help)
        self.register_cmd('next_hop $id',
                          '\t\t\tset peer $id as default route.',
                          self.next_hop)
        self.register_cmd('reconnect $id',
                          '\t\t\trestarts connection to peer.',
                          self.reconnect)
        self.register_cmd('register $id $ip $port', 'register/update peer node', self.register)
        self.register_cmd('send $message $id',
                          '\t\tsend message (array of bytes) to a peer.',
                          self.send)
        self.register_cmd('show_peers',
                          '\t\t\tshow registered ids.',
                          self.show_peers)
        self.register_cmd('startserver $port',
                          '\t\tstart tcpserver at port "port".',
                          self.tcpserver)
        self.register_cmd('statusserver', '\t\t\tinform about tcpserver status [running/stopped]', self.tcpserver)
        self.register_cmd('stopserver', '\t\t\tstop tcp server', self.tcpserver)
        self.register_cmd('unregister $id', '\t\tdelete peer from list', self.unregister)

        self.register_cmd('upcn_register $id',
                          '\t\tregister node with upcn a running server. ',
                          self.register_upcn_node)


    def register_cmd(self, alias, help,  func):
        cmd_name = alias.split()[0]
        self.valid_commands[cmd_name] = (alias, help, func)

    def parse(self, cmd, *args):
        if cmd in self.valid_commands:
            arg_len = len(self.valid_commands[cmd][0].split())-1

            if len(args) == arg_len:
                method = self.valid_commands[cmd][2]
                method(*args)
            else:
                print('{} expects {} parameters, but {} were given.'.format(cmd, arg_len, len(args)))
        else:
            print('Invalid input. Try "help" for valid commands.')

    ## -- Commands

    def clear(self, *args):
        os.system('clear')

    def connect(self, *args):
        print('Mock: connect')

    def exit(self, *args):
        self.controller.exit()

    def help(self, *args):
        print('Command line help: ')
        for c in sorted(self.valid_commands):
            print('    {}: {}'.format(*self.valid_commands[c][:2]))

    def next_hop(self, *args):
        print('Mock: set_next_hop')

    def show_peers(self, *args):
        if len(self.controller.peers) > 0:
            for p in self.controller.peers:
                print("id: {}, ip: {}, port: {}".format(p, *self.controller.peers[p]))
        else:
            print('No peers registered yet. ')

    def tcpserver(self, *args):
        print('Mock: tcpserver')

    def register(self, *args):
        if len(args) != 3:
            print ('{} arguments. 3 needed. Usage: register $id $ip $port'.format(len(args)))
        else:
            self.controller.register(*args)

    def register_upcn_node(self, *args):
        print('Mock: register_upcn_node')

    def reconnect(self, *args):
        print('Mock: reconnect')

    def unregister(self, *args):
        if len(args) != 1:
            print ('{} arguments. 1 needed. Usage: unregister $id'.format(len(args)))
        else:
            self.controller.unregister(*args)

    def send(self, *args):
        print('Mock: send')
