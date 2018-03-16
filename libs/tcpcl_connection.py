from libs import sdnv, flags
import socket

class TCPCL_Connection:
    def __init__(self, s):
        self.socket = s
        self.peer_id = None
        self.out_msg_queue = []

    def __del__(self):
        print('Cleaning up connection to {}'.format(self.peer_id))
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def getpeername(self):
        return self.socket.getpeername()

    def restart(self, conn_id):
        pass

    # callback to be called after enqueue in msg_queue
    def send(self, data):
        pass
