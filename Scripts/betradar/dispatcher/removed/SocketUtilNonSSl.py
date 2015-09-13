__author__ = 'Chyros'

import socket


class ServerSocketException(Exception):

    def __init__(self, message):
        super(ServerSocketException, self).__init__(message)
        self.message = message


class ServerSocket:

    def __init__(self, port=None):
        self.port = port
        self._sock = None
        self._listening = False
        self._waiting_for_connection = False
        self._closed = False

    def listen(self, port=None):
        self._listening = False

        if self._closed:
            raise ServerSocketException('Cannot listen to a port once socket has been closed')

        if port is not None:
            self.port = port

        self._close_pending_connection()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind(('', self.port))
        self._sock.listen(0)
        self._listening = True

    def accept(self):
        self._waiting_for_connection = True
        try:
            return self._sock.accept()
        except Exception as e:
            raise e
        finally:
            self._waiting_for_connection = False

    def close(self):
        self._closed = True
        self._listening = False
        self._close_pending_connection()
        self.close_socket()

    def _close_pending_connection(self):
        if not self._waiting_for_connection:
            return

        try:
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('127.0.0.1', self.port))
        except Exception:
            pass

    def _close_socket(self):
        if self._sock is not None:
            self._sock.close()
            self._sock = None

    @property
    def is_listening(self):
        return self._listening


class ClientSocket:

    READ_BUFFER_SIZE = 1024
    ENCODING = 'UTF-8'

    def __init__(self, sock=None, addr=None):
        self.read_buffer_size = self.READ_BUFFER_SIZE
        self.encoding = self.ENCODING
        self._sock = sock
        self._addr = addr
        self._connected = (sock is not None and addr is not None)

    def connect(self, host, port):
        self.disconnect()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((host, port))
        self._addr = host, port
        self._connected = True

    def disconnect(self):
        self._connected = False
        if self._sock is not None:
            self._sock.close()
            self._sock = None
            self._addr = None

    def send(self, data):
        try:
            print(self._sock)
            print(self._addr)
            self._sock.send(bytes(data, self.encoding))
        except Exception as e:
            self._connected = False
            raise e

    def receive(self):
        try:
            return self._sock.recv(self.read_buffer_size)
        except Exception as e:
            self._connected = False
            raise e

    @property
    def get_socket(self):
        return self._sock

    @property
    def get_addr(self):
        return self._addr

    @property
    def is_connected(self):
        return self._connected
