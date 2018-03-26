import socket
import selectors
import struct
from libs import sdnv
from libs import tcpcl_connection
from libs import flags
import logging

class TCPCL_CL:

    def __init__(self, tcpcl_id, selector=None):
        logging.getLogger(__name__)
        logging.info('Initializing {}'.format(__class__.__name__))
        self.tcpcl_id = tcpcl_id
        self.selector = selector
        self.connections=dict()
        self.next_hop = None
        self.header = None
        self.unnamed_connections = dict()   # (ip, dst): connection_obj

    # https://tools.ietf.org/html/rfc7242#section-4.1
    def encode_header(self, magic=b'dtn!', version=b'\x03', flags=b'\x00', keepalive=b'\x00\x00'):
        assert self.tcpcl_id is not None, 'TCPCL id not set'
        if self.header is None:
            enc_id  = self.tcpcl_id.encode("ascii")
            enc_len = sdnv.encode(len(enc_id))
            self.header = magic + version + flags + keepalive + enc_len + enc_id
        return self.header

    def decode_header(self, h):
        assert h[:4] == b'dtn!', 'header should start with "dtn!"'
        assert len(h) > 8, 'header too short'
        result = {
            "version": h[4],
            "flags": h[5],
            "keepalive": struct.unpack("!h", h[6:8])[0]
        }

        eid_len, eid_len_size = sdnv.decode(h, 8)
        assert len(h) == 8 + eid_len_size + eid_len, "header length does not match"
        result["eid"] = h[8 + eid_len_size:].decode("ascii")
        return result

    # is basically set default route.
    # when a send is used to an id that is unknown, the message is sent to the next hop.
    # if next_hop is not set, an exception should be raised.
    def set_next_hop(self, ns):
        assert self.tcpcl_id in self.connections, "{} is not a valid id".format(ns.tcpcl_id)
        self.sock_next_hop = self.connections[ns.tcpcl_id]
        logging.info('Next hop set to {}: {}'.format(ns.tcpcl_id, self.connections[ns.tcpcl_id].getpeername()))

    # connect as client to a server. E.g: upcn
    # ignore if connection is already stablished
    # Tries to establish the connection, setting a trigger for read and write and inserting the header in the out queue
    # on write trigger, send the first queue element if the list is not empty.
    #   unsubscribe ON_WRITE
    def connect(self, ns):
        if ns.addr == 'localhost':
            ns.addr = '127.0.0.1'
        peer = (ns.addr, ns.port)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(False)
        tc = tcpcl_connection.TCPCL_Connection(s, self.selector)
        tc.register_callback(self.receive_socket_signal)
        tc.register_event(selectors.EVENT_WRITE | selectors.EVENT_READ)
        tc.enqueue(self.encode_header())
        self.unnamed_connections[peer] = tc
        print('Connecting to {}...'.format(peer))
        try:
            s.connect(peer)
        except BlockingIOError:
            logging.warning('Blocking I/O error on connecting to {}'.format(peer))

    def reconnect(self, tcpcl_id):
        pass

    # send_to is currently used for debugging, when sending from command line
    def send_to(self, ns):
        if ns.id not in self.connections:
            print('Unknown id {}'.format(ns.id))
            logging.warning('Unknown id {}'.format(ns.id))
            return
        conn = self.connections[ns.id]
        #self.send(conn, ns.message.encode())
        tcpcl_encoded = self.encode_tcpcl(ns.message.encode())
        self.send(conn, tcpcl_encoded)

    # https://tools.ietf.org/html/rfc7242#section-5.2
    # Only transmitting bundle in a sigle segment (SE == 0x3)
    # TODO organize the code
    def encode_tcpcl(self, data):
        return bytes([flags.MessageCodeType.DATA_SEGMENT << 4]) + b'\x03' \
               + sdnv.encode(len(data)) \
               + data

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
                logging.info('Got disconnected. Cleaning up...')
                try:
                    self.selector.unregister(sock)
                except (KeyError, ValueError) as msg:
                    logging.critical('Error unregistered socket: {}'.format(msg))
                    raise
                finally:
                    if connection.peer_id is None: # remove from the noname list
                        del self.unnamed_connections[connection.getpeername()]
                    else:
                        del self.connections[connection.peer_id]
            elif self.is_header(txt):
                self.receive_header(txt, connection)
            elif self.is_datasegment(txt):
                self.receive_bundle(txt, data)
            else:
                logging.critical('ERROR - Corrupted packet ignored')

        elif mask & selectors.EVENT_WRITE:
            # if connection is just established:
            data['tcpcl_conn'].send()
        else:
            logging.critical('Warning: que mascara é essa?')

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
        logging.info('Accepting connection from {}'.format(addr))

        # every connection should have its selector, since we need to
        # turn the selector on/off for write independently
        tc = tcpcl_connection.TCPCL_Connection(new_conn, self.selector)
        tc.register_callback(self.receive_socket_signal)
        tc.register_event(selectors.EVENT_READ)
        peers = tc.getpeername()
        self.unnamed_connections[peers] = tc
        # send_header
        self.send(tc, self.encode_header())


    # yet to be implemented
    def add_connection(self, sock):
        pass

    def get_unnamed_conn_index(self, peername):
        return next((idx for idx, tc_conn in enumerate(self.unnamed_connections)
                     if tc_conn.getpeername() == peername), None)

    def set_connection_id(self, tcpcl_conn):
        unknown_addr = tcpcl_conn.socket.getpeername()
        peer = tcpcl_conn.peer_id
        if unknown_addr in self.unnamed_connections:
            self.connections[peer] = self.unnamed_connections.pop(unknown_addr)
        else:
            logging.debug('{} not in unnamed conns:{}'.format(unknown_addr, self.unnamed_connections))
            self.unnamed_connections[unknown_addr] = tcpcl_conn

    def receive_header(self, txt, tcpcl_conn):
        logging.info('header received: {} : {}'.format(txt, txt.hex()))
        result = self.decode_header(txt)
        tcpcl_conn.peer_id = result['eid']
        self.set_connection_id(tcpcl_conn)

    def receive_bundle(self, txt, data):
        logging.info('bundle received: {} : {}'.format(txt, txt.hex()))

    def is_header(self, data):
        return data.startswith(b'dtn!')

    def is_datasegment(self, data):
        return not self.is_header(data)

    def decode(self, header):
        pass

    def sdnv_read(self, buffer, offset=0):
        pass

if __name__ == '__main__':
    cl = TCPCL_CL('TestingCreation')
    print("{}".format(cl.header))
    pass
