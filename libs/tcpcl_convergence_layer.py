from libs import sdnv
from libs import tcpcl_connection

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

    def set_next_hop(self, selftcpcl_id):
        self.next_hop = selftcpcl_id

    def connect (self, tcpcl_id):
        if self.next_hop is None:
            print("You must set next hop")
            return 1
        if tcpcl_id not in self.connections:
            print("tcpcl_id {} not found. Your id must registered".format(tcpcl_id))
            return 1


    def reconnect(self, tcpcl_id):
        pass

    # for simplicity we just assume that socket will be able to send.
    def send(self, dst, data):
        pass

    # create a tcpcl connection passing the socket
    # register events with receive function
    def create_connection(self, conn):
        pass

    # receive data from network
    # on \0 shutdown, close socket and remove from connections
    def receive(self, data):
        pass


if __name__ == '__main__':
    cl = TCPCL_CL('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    print("{}".format(cl.header))
    pass
