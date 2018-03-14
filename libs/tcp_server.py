import socket
import selectors


class TCP_Server:
    def __init__(self, max_conn, callback, selector):
        self.max_conn = max_conn
        self.socket = None
        self.callback = callback
        self.selector = selector

    def __del__(self):
        self.stop()

    def start(self, port, reuse = 1, blocking = False):
        if self.socket is None:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, reuse)
                self.socket.setblocking(blocking)
                self.socket.bind(('localhost', port))
                self.socket.listen(self.max_conn)
            except OSError as msg:
                print('Error starting server on port {}. Is the port already being used?'.format(port))
                self.socket = None
                return
            self.selector.register(self.socket, selectors.EVENT_READ, {'func': self.callback})

    def stop(self):
        if self.socket is not None:
            if self.selector is not None:
                try:
                    self.selector.unregister(self.socket)
                except KeyError:
                    print('It seems the socket was not registered')
                except ValueError:
                    print('Invalid selector on unregister')
            self.socket.close()
            self.socket = None

    def is_running(self):
        is_running = self.socket is not None
        return is_running
