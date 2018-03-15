from libs import sdnv, flags

class TCPCL_Connection:
    def __init__(self, s):
        self.socket = s
        self.msg_queue = []
        self.peer_id = None

    def getpeername(self):
        return self.socket.getpeername()


    def restart(self, conn_id):
        pass

    def send(self, data):
        pass
