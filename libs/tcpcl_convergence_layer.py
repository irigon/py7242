import socket
import selectors
from libs import sdnv
from libs import tcpcl_connection

class TCPCL_CL:

    def __init__(self, tcpcl_id, selector):
        self.id = tcpcl_id
        self.selector = selector
        self.connections=dict()     # sock:[id, msg_buffer[]], sock:tcpcl_connection
        self.next_hop = None
        self.header = None
        self.unnamed_connections = []   # connections without identification

    # https://tools.ietf.org/html/rfc7242#section-4.1
    def get_header(self):
        assert self.id is not None, 'TCPCL id not set'
        if self.header is None:
            enc_id  = self.id.encode("ascii")
            enc_len = sdnv.encode(len(enc_id))
            self.header =  b'dtn!\x03\x00\x00\x00\x05' + enc_len + enc_id
        return self.header

    # get a list of connections that have this id as peer_id
    def get_connections_from_id(self, id):
        sock = [ x for x in self.connections if self.connections[x][0] == id ]
        return sock

    # this is a narrow case of the function above, when we want to assure that there is exactly one connection
    def get_unique_connection_from_id(self, id):
        conns = self.get_connections_from_id(id)
        assert len(conns) == 1, 'Connection to {} should be exactly one. Returned: {}'.format(id, conns)
        return conns[0]

    # is basically set default route.
    # when a send is used to an id that is unknown, the message is sent to the next hop.
    # if next_hop is not set, an exception should be raised.
    def set_next_hop(self, tcpcl_id):
        try:
            sock = self.get_unique_connection_from_id(tcpcl_id)
        except AssertionError:
            print('#connections with id={} != 1'.format(tcpcl_id))
        else:
            self.sock_next_hop = sock
            print('Next hop set to {}: {}'.format(sock[0], sock))

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
        sock = self.get_unique_connection_from_id(peer_id)
        if sock is not None:
            # enqueue and register read & write #TODO
            sock.sendall(data.encode())

    # receive data from network
    # on \0 shutdown, close socket and remove from connections
    def receive(self, sock, data):
        txt = sock.recv(1024)

        if not txt:
            print('Got disconnected. Cleaning up...')
            try:
                data['selector'].unregister(sock)
            except KeyError:
                print('Trying to unregister an unregistered socket')
                raise
            except ValueError:
                print('Invalid object (fileno() has an invalid return value or is inexistent.')
                raise
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

        print('Received {} on "receive"'.format(txt))

    def add_connection(self, sock):
        # id not yet set, set it to None
        self.connections[sock]=[None, []]

    def show_peers(self):
        print('Registered peers:')
        for c in self.connections:
            print(' {}: {} '.format(self.connections[c].peer_id, self.connections[c].getpeername()))

        if len(self.unnamed_connections) > 0:
            print('Unnamed peers:')
            for c in self.unnamed_connections:
                print(' {}: {} '.format('None', c.getpeername()))

    # receive connection from tcp server.
    # since we don't know the peer's id, we add to a list of unamed_connections, untill
    # the header is received or the connection is closed
    def recv_new_connection(self, sock, data):
        new_conn, addr = sock.accept()
        new_conn.setblocking(False)
        print('Accepting connection from {}'.format(addr))
        tc = tcpcl_connection.TCPCL_Connection(new_conn)
        data = {'func':self.receive, 'tcpcl_conn':tc}
        try:
            self.selector.register(new_conn, selectors.EVENT_READ, data)
        except (ValueError, KeyError) as mesg:
            print('Invalid event mask or file descriptor', mesg)
            del(tc)
            raise
        else:
            self.unnamed_connections.append(tc)

    def set_connection_id(self, new_id, peername):

        index = next((idx for idx, tc_conn in enumerate(self.unnamed_connections)
                     if tc_conn.getpeername() == peername), None)
        if index is not None:   # element exists
            obj = self.unnamed_connections[index]
            obj.peer_id = new_id
            self.connections[new_id] = obj
            self.unnamed_connections.remove(obj)
        else:
            print('There is no registered node on {}'.format(peername))

if __name__ == '__main__':
    cl = TCPCL_CL('TestingCreation')
    print("{}".format(cl.header))
    pass
