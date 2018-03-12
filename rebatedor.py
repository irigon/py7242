import selectors
import sys
from libs.tcpcl import TCPCL
from libs import parser

m_selector = selectors.DefaultSelector()

GO_ON = True

def quit():
    global GO_ON
    print('Exiting...')
    GO_ON = False

# listen to port 10000, at most 10 connections
my_tcpcl = TCPCL('dtn:1')
my_tcpcl.create_socket(42420, 10)

p = parser.Parser()
p.set_input_nonblocking()

m_selector.register(my_tcpcl.server, selectors.EVENT_READ, my_tcpcl.accept)
m_selector.register(sys.stdin, selectors.EVENT_READ, p.from_keyboard)

while GO_ON:
    sys.stdout.write('>>> ')
    sys.stdout.flush()
    for k, mask in m_selector.select():
        callback = k.data
        callback(k.fileobj, m_selector)

# unregister events
m_selector.unregister(sys.stdin)
#  close select
m_selector.close()
