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
                print('Could not start server on port {}: {}'.format(port, msg))
                try:
                    self.socket.shutdown(socket.SHUT_RDWR)
                    self.socket.close()
                except OSError:
                    pass
                self.socket = None
                return
            else:
                try:
                    self.selector.register(self.socket, selectors.EVENT_READ, {'func': self.callback})
                except ValueError:
                    print('Invalid event mask or file descriptor')
                    raise
                except KeyError:
                    print('Object {} is already registered'.format(self.socket))
                    raise

    def stop(self):
        if self.socket is not None:
            if self.selector is not None:
                try:
                    self.selector.unregister(self.socket)
                except KeyError:
                    print('It seems the socket was not registered (ignoring)')
                except ValueError:
                    print('Invalid selector on unregister')
                    raise
            self.socket.close()
            self.socket = None

    def is_running(self):
        is_running = self.socket is not None
        return is_running
