import selectors
import socket
import sys
import os
import fcntl

m_selector = selectors.DefaultSelector()

# set sys.stdin non-blocking
def set_input_nonblocking():
    orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

GO_ON = True

def create_socket(port, max_conn):
    server_addr = ('localhost', port)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setblocking(False)
    server.bind(server_addr)
    server.listen(max_conn)
    return server

def read(conn, mask):
    global GO_ON
    client_address = conn.getpeername()
    data = conn.recv(1024)
    print('Got {} from {}'.format(data, client_address))
    if not data:
        GO_ON = False

def accept(sock, mask):
    new_conn, addr = sock.accept()
    new_conn.setblocking(False)
    print('Accepting connection from {}'.format(addr))
    m_selector.register(new_conn, selectors.EVENT_READ, read)

def from_keyboard(arg1, arg2):
    print('User input: {}'.format(arg1.read()))


set_input_nonblocking()

# listen to port 10000, at most 10 connections
server = create_socket(10000, 10)

m_selector.register(server, selectors.EVENT_READ, accept)
m_selector.register(sys.stdin, selectors.EVENT_READ, from_keyboard)

while GO_ON:
    print('Waiting...')
    for k, mask in m_selector.select():
        callback = k.data
        callback(k.fileobj, mask)


# deregister
# close connection
# close select