import fcntl
import sys
import os

class Parser:
    def __init__(self):
        pass

    def set_input_nonblocking(self):
        orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

    def show_commands(self):
        print('exit/quit: exit program')
        print('help/h/?: show this help')

    def from_keyboard(self, stdin, selector):
        line = stdin.read()
        if line == 'exit\n' or line == 'quit\n':
            quit()
        elif line == 'help\n' or line == 'h\n' or line == '?':
            self.show_commands()
        else:
            print('Invalid input: {}. Valid input are:'.format(line))
            self.show_commands()


