from libs import sdnv, flags
import socket
import selectors

class TCPCL_Connection:
    def __init__(self, sock, selector):
        self.socket = sock
        self.socket.setblocking(False)
        self.peer_id = None
        self.out_msg_queue = []
        self.selector = selector
        self.data = None

    def __del__(self):
        print('Cleaning up connection to {}'.format(self.peer_id))
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def register_callback(self, callback):
        # on a callback, we need
        self.data = {'func':callback, 'tcpcl_conn':self}

    def register_event(self, event):
        try:
            self.selector.register(self.socket, event, self.data)
        except (ValueError, KeyError) as mesg:
            print('Invalid event mask or file descriptor: ', mesg)
            raise

    def set_selector_flags(self, flags):
        assert self.data is not None, 'Calback on socket {} was not registered'.format(self.socket.getpeername())
        try:
            self.selector.modify(self.socket, flags, self.data)
        except (ValueError, KeyError) as msg:
            print('Error modifying selectors flag: {}'.format(msg))

    def getpeername(self):
        return self.socket.getpeername()

    def restart(self, conn_id):
        pass

    # callback to be called after enqueue in msg_queue
    def send(self):
        if len(self.out_msg_queue) > 0:
            to_send = self.out_msg_queue.pop(0)
            sentbytes = self.socket.send(to_send)
            to_send = to_send[sentbytes:]
            if to_send: # enqueue the rest
                self.out_msg_queue.insert(0, to_send)
        else:   # queue empty
            self.set_selector_flags(selectors.EVENT_READ)

    # wrapper for adding data to be sent over network
    def enqueue(self, data):
        self.out_msg_queue.append(data)