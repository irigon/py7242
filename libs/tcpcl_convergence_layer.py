import socket
import selectors
from libs import sdnv
from libs import tcpcl_connection

class TCPCL_CL:

    def __init__(self, tcpcl_id, selector):
        self.id = tcpcl_id
        self.selector = selector
        self.connections=dict()
        self.next_hop = None
        self.header = None
        self.unnamed_connections = dict()   # (ip, dst): connection_obj

    # https://tools.ietf.org/html/rfc7242#section-4.1
    def get_header(self):
        assert self.id is not None, 'TCPCL id not set'
        if self.header is None:
            enc_id  = self.id.encode("ascii")
            enc_len = sdnv.encode(len(enc_id))
            self.header =  b'dtn!\x03\x00\x00\x00\x05' + enc_len + enc_id
        return self.header

    # is basically set default route.
    # when a send is used to an id that is unknown, the message is sent to the next hop.
    # if next_hop is not set, an exception should be raised.
    def set_next_hop(self, tcpcl_id):
        assert tcpcl_id in self.connections, "{} is not a valid id".format(tcpcl_id)
        self.sock_next_hop = self.connections[tcpcl_id]
        print('Next hop set to {}: {}'.format(tcpcl_id, self.connections[tcpcl_id].getpeername()))

    # connect as client to a server. E.g: upcn
    # ignore if connection is already stablished
    # Tries to establish the connection, setting a trigger for read and write and inserting the header in the out queue
    # on write trigger, send the first queue element if the list is not empty.
    #   unsubscribe ON_WRITE
    def connect (self, addr, port):
        peer = (addr, port)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(False)
        tc = tcpcl_connection.TCPCL_Connection(s, self.selector)
        tc.register_callback(self.receive_socket_signal)
        tc.register_event(selectors.EVENT_WRITE | selectors.EVENT_READ)
        tc.enqueue(self.get_header())
        try:
            s.connect(peer)
        except BlockingIOError:
            print('Blocking I/O error on connecting to {}'.format(peer))


    def reconnect(self, tcpcl_id):
        pass

    # send_to is currently used for debugging, when sending from command line
    #
    def send_to(self, peer_id, str_data):
        conn = self.connections[peer_id]
        self.send(conn, str_data.encode())

    def send(self, conn, byte_data):
        # enqueue and register read & write #TODO
        conn.enqueue(byte_data)
        # register event write if not registered yet
        conn.set_selector_flags(selectors.EVENT_WRITE | selectors.EVENT_READ)

    # receive data from network
    # on \0 shutdown, close socket and remove from connections
    def receive_socket_signal(self, sock, data, mask):
        if mask & selectors.EVENT_READ:
            txt = sock.recv(1024)
            connection = data['tcpcl_conn']
            if not txt:
                print('Got disconnected. Cleaning up...')
                try:
                    self.selector.unregister(sock)
                except (KeyError, ValueError) as msg:
                    print('Error unregistered socket: {}'.format(msg))
                    raise
                finally:
                    if connection.peer_id is None: # remove from the noname list
                        del self.unnamed_connections[connection.getpeername()]
                    else:
                        del self.connections[connection.peer_id]
            elif self.is_header(txt):
                self.receive_header(txt, connection)
            elif self.is_datasegment(txt):
                self.receive_bundle(txt, connection)
            else:
                print('ERROR - Corrupted packet ignored')

        elif mask & selectors.EVENT_WRITE:
            print('Selectors.write')
            data['tcpcl_conn'].send()
        else:
            print('Warning: que mascara é essa?')

    def show_peers(self):
        print('Registered peers:')
        for c in self.connections:
            print(' {}: {} '.format(self.connections[c].peer_id, self.connections[c].getpeername()))

        if len(self.unnamed_connections) > 0:
            print('Unnamed peers:')
            for c in self.unnamed_connections:
                print(' {}: {} '.format('None', self.unnamed_connections[c].getpeername()))

    # receive connection from tcp server.
    # since we don't know the peer's id, we add to a list of unamed_connections, untill
    # the header is received or the connection is closed
    def recv_new_connection(self, sock, data, mask):
        new_conn, addr = sock.accept()
        print('Accepting connection from {}'.format(addr))

        # every connection should have its selector, since we need to
        # turn the selector on/off for write independently
        tc = tcpcl_connection.TCPCL_Connection(new_conn, self.selector)
        tc.register_callback(self.receive_socket_signal)
        tc.register_event(selectors.EVENT_READ)
        peers = tc.getpeername()
        self.unnamed_connections[peers] = tc
        # send_header
        self.send(tc, self.get_header())


    # yet to be implemented
    def add_connection(self, sock):
        pass

    def get_unnamed_conn_index(self, peername):
        return next((idx for idx, tc_conn in enumerate(self.unnamed_connections)
                     if tc_conn.getpeername() == peername), None)

    def set_connection_id(self, new_id, peername):
        if peername in self.unnamed_connections:
            self.connections[new_id] = self.unnamed_connections.pop(peername)
        else:
            print('There is no registered node on {}'.format(peername))

    def receive_header(self, data, tcpcl_conn):
        print('header received: {} : {}'.format(data, data.hex()))
        result = self.decode_tcpcl_contact_header(data)
        tcpcl_conn.peer_id=result['eid']
        self.connections[tcpcl_conn.peer_id]=tcpcl_conn
        pass

    def receive_bundle(self, data):
        print('bundle received: {} : {}'.format(data, data.hex()))
        pass

    def is_header(self, data):
        return data.startswith(b'dtn!')

    def decode(self, header):
        pass

    def sdnv_read(self, buffer, offset=0):
        pass

if __name__ == '__main__':
    cl = TCPCL_CL('TestingCreation')
    print("{}".format(cl.header))
    pass
