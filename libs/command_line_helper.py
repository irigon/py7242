import fcntl
import sys
import os
import traceback
import selectors


class CLH:
    def __init__(self, controller):
        self.controller = controller
        self.valid_commands = dict()
        self.register_known_commands()

    def register_callback(self, selector, callback):
        self.set_input_nonblocking()
        selector.register(sys.stdin, selectors.EVENT_READ, {'func':callback})

    def set_input_nonblocking(self):
        orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

    def register_known_commands(self):
        self.register_cmd('clear',
                          '\t\t\t\t\tclear screen.',
                          self.clear)
        self.register_cmd('connect $addr $port',
                          '\t\t\tconnects to a registered peer.',
                          self.connect)
        self.register_cmd('disconnect $id',
                          '\t\t\tdisconnects to a registered peer.',
                          self.disconnect)
        self.register_cmd('exit', '\t\t\t\t\texit program', self.exit)
        self.register_cmd('help', '\t\t\t\t\tshow this help', self.help)
        self.register_cmd('next_hop $id',
                          '\t\t\tset peer $id as default route.',
                          self.next_hop)
        self.register_cmd('reconnect $id',
                          '\t\t\trestarts connection to peer.',
                          self.reconnect)
        self.register_cmd('register $id $ip $port', 'register/update peer node', self.register)
        self.register_cmd('send_to $id $message',
                          '\tsend message (array of bytes) to a peer.',
                          self.send_to)
        self.register_cmd('show_peers',
                          '\t\t\tshow registered ids.',
                          self.show_peers)
        self.register_cmd('server_start $port $conn',
                          '\tstart server on port $port for at most $maxconn connections.',
                          self.server_start)
        self.register_cmd('server_status',
                          '\t\t\tquery server status.',
                          self.server_status)
        self.register_cmd('server_stop',
                          '\t\t\tstop server.',
                          self.server_stop)
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
                try:
                    method(*args)
                except Exception:
                    print('Error -- exception raised when trying to call method: {}, params: {}'.format(cmd, args))
                    print('Stacktrace: ')
                    traceback.print_exc()
            else:
                print('{} expects {} parameters, but {} were given.'.format(cmd, arg_len, len(args)))
        else:
            print('Invalid input. Try "help" for valid commands.')

    ## -- Commands

    def clear(self, *args):
        os.system('clear')

    def connect(self, *args):
        self.controller.cl.connect(args[0], int(args[1]))

    def disconnect(self, *args):
        print('Mock: disconnect')

    def exit(self, *args):
        self.controller.exit()

    def help(self, *args):
        print('Command line help: ')
        for c in sorted(self.valid_commands):
            print('    {}: {}'.format(*self.valid_commands[c][:2]))

    def next_hop(self, *args):
        self.controller.cl.set_next_hop(*args)

    def show_peers(self, *args):
        self.controller.cl.show_peers()

    def server_start(self, *args):
        self.controller.server_start(int(args[0]), int(args[1]))

    def server_status(self, *args):
        self.controller.server_status()

    def server_stop(self, *args):
        self.controller.server_stop()

    def register(self, *args):
        self.controller.register_id_manually(args[0], args[1], int(args[2]))

    def register_upcn_node(self, *args):
        print('Mock: register_upcn_node')

    def reconnect(self, *args):
        print('Mock: reconnect')

    def unregister(self, *args):
        if len(args) != 1:
            print ('{} arguments. 1 needed. Usage: unregister $id'.format(len(args)))
        else:
            self.controller.unregister(*args)

    def send_to(self, *args):
        self.controller.cl.send_to(*args)