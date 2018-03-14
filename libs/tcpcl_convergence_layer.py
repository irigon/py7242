from libs import sdnv
import socket

class TCPCL_CL:

    def __init__(self, tcpcl_id):
        self.id = tcpcl_id
        self.header = self.create_header()
        self.connections=dict()
        self.next_hop = None

    def create_header(self):
        enc_id  = self.id.encode("ascii")
        enc_len = sdnv.encode(len(enc_id))
        return  b'dtn!\x03\x00\x00\x00\x05' + enc_len + enc_id

    def get_socket_from_id(self, id):
        conn = [ x for x in self.connections if self.connections[x][0] == id ]
        if len(conn) != 1:
            print ('Error -- There should be one connection with id {}, but {} were found.'.format(id, len(conn)))
            return
        return self.connections[conn[0]][1]

    def set_next_hop(self, tcpcl_id):
        self.sock_next_hop = self.get_socket_from_id(tcpcl_id)

    # connect as client to a server. E.g: upcn
    # ignore if connection is already stablished
    def connect (self, sock, data):
        peer_id = data['peer_id']

    def reconnect(self, tcpcl_id):
        pass

    # for simplicity we just assume that socket will be able to send.
    def send_to(self, peer_id, data):
        sock = self.get_socket_from_id(peer_id)
        if sock is not None:
            sock.sendall(data.encode())

    # receive data from network
    # on \0 shutdown, close socket and remove from connections
    def receive(self, sock, data):
        txt = sock.recv(1024)

        if not txt:
            print('Got disconnected. Cleaning up...')
            data['selector'].unregister(sock)
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

        print('Received {} on "receive"'.format(txt))

    def add_connection(self, sock, addr):
        # id not yet set, set it to None
        self.connections[addr]=[None, sock]

if __name__ == '__main__':
    cl = TCPCL_CL('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    print("{}".format(cl.header))
    pass
