import selectors
import struct
import socket
from libs import sdnv

class TCPCL:
    def __init__(self, TCPCL_ID):
        self.TCPCL_ID = TCPCL_ID
        self.keepalive_interval = 0     # isn't this out of its place?
        self.connection_flag = 0
        self.conn_list = []

    def __del__(self):
        if len(self.conn_list) > 0:
            for server in self.conn_list:
                server.shutdown(socket.SHUT_RDWR)
                server.close()

    def create_socket(self, port, max_conn):
        server_addr = ('localhost', port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.setblocking(False)
        self.server.bind(server_addr)
        self.server.listen(max_conn)

    def accept(self, sock, selector):
        new_conn, addr = sock.accept()
        new_conn.setblocking(False)
        print('Accepting connection from {}'.format(addr))
        selector.register(new_conn, selectors.EVENT_READ, self.read)
        self.conn_list.append(new_conn)
        # send header
        self.send_header(new_conn)

    def read(self, conn, selector):
        global GO_ON
        client_address = conn.getpeername()
        data = conn.recv(1024)
        print('Got {} from {}'.format(data, client_address))

        # disconnected, unregister connection
        if not data:
            print('Got disconnected. Cleaning up...')
            selector.unregister(conn)
            self.conn_list.remove(conn)

    # register the underlying TCP connection, as client or server
    def register_tcp(self):
        pass

    def send_header(self, conn):
        try:
            conn.sendall(self.create_header())
        except:
            print('Error sending header')

    def create_header(self):
        # https://tools.ietf.org/html/rfc7242#section-4.1
        header = bytearray(b'dtn!\x03\x00\x00\x00\x05')
        source_eid_ascii = self.TCPCL_ID.encode("ascii")
        header += sdnv.SDNV.encode(len(source_eid_ascii))
        header += source_eid_ascii
        return header