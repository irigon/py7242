import socket


class TCP_Server:
    def __init__(self, port=4556, max_conn=1, selector=None):
        self.port = port
        self.max_conn = max_conn
        self.socket = None
        self.selector = selector

    def __del__(self):
        self.stop()

    def start(self, reuse = 1, blocking = False):
        if self.socket is None:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, reuse)
                self.socket.setblocking(blocking)
                self.socket.bind(('localhost', self.port))
                self.socket.listen(self.max_conn)
            except OSError as msg:
                self.socket = None

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
        return self.socket is not None

    def register_callback(self, func):
        self.callback = func
        pass