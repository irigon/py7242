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
    def connect (self, sock, data):
        peer_id = data['peer_id']

    def reconnect(self, tcpcl_id):
        pass

    # for simplicity we just assume that socket will be able to send.
    def send_to(self, peer_id, data):
        conn = self.connections[peer_id]
        # enqueue and register read & write #TODO
        conn.socket.sendall(data.encode())

    def send(self):
        pass

    # receive data from network
    # on \0 shutdown, close socket and remove from connections
    def receive(self, sock, data):
        txt = sock.recv(1024)

        if not txt:
            print('Got disconnected. Cleaning up...')
            try:
                data['selector'].unregister(sock)
            except (KeyError, ValueError) as msg:
                print('Error unregistered socket: {}'.format(msg))
                raise
            finally:
                connection = data['tcpcl_conn']
                if connection.peer_id is None: # remove from the noname list
                    del self.unnamed_connections[connection.getpeername()]
                else:
                    del self.connections[connection.peer_id]

        print('Received {} on "receive"'.format(txt))

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
    def recv_new_connection(self, sock, data):
        new_conn, addr = sock.accept()
        new_conn.setblocking(False)
        print('Accepting connection from {}'.format(addr))
        tc = tcpcl_connection.TCPCL_Connection(new_conn)
        data = {'func':self.receive, 'tcpcl_conn':tc, 'selector':self.selector}
        try:
            self.selector.register(new_conn, selectors.EVENT_READ, data)
        except (ValueError, KeyError) as mesg:
            print('Invalid event mask or file descriptor', mesg)
            del(tc)
            raise
        else:
            peers = tc.getpeername()
            self.unnamed_connections[peers] = tc
    def add_connection(self, sock):
        # id not yet set, set it to None
        self.connections[sock]=[None, []]

    def get_unnamed_conn_index(self, peername):
        return next((idx for idx, tc_conn in enumerate(self.unnamed_connections)
                     if tc_conn.getpeername() == peername), None)

    def set_connection_id(self, new_id, peername):
        if peername in self.unnamed_connections:
            self.connections[new_id] = self.unnamed_connections.pop(peername)
        else:
            print('There is no registered node on {}'.format(peername))

if __name__ == '__main__':
    cl = TCPCL_CL('TestingCreation')
    print("{}".format(cl.header))
    pass
