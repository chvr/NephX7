__author__ = 'arifal'


import socket
import ssl
import sys


OPENSSL_CIPHERS = r'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:SRP-DSS-AES-256-CBC-SHA:SRP-RSA-AES-256-CBC-SHA:SRP-AES-256-CBC-SHA:DHE-DSS-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA256:DHE-RSA-AES256-SHA:DHE-DSS-AES256-SHA:DHE-RSA-CAMELLIA256-SHA:DHE-DSS-CAMELLIA256-SHA:AECDH-AES256-SHA:ADH-AES256-GCM-SHA384:ADH-AES256-SHA256:ADH-AES256-SHA:ADH-CAMELLIA256-SHA:ECDH-RSA-AES256-GCM-SHA384:ECDH-ECDSA-AES256-GCM-SHA384:ECDH-RSA-AES256-SHA384:ECDH-ECDSA-AES256-SHA384:ECDH-RSA-AES256-SHA:ECDH-ECDSA-AES256-SHA:AES256-GCM-SHA384:AES256-SHA256:AES256-SHA:CAMELLIA256-SHA:PSK-AES256-CBC-SHA:ECDHE-RSA-DES-CBC3-SHA:ECDHE-ECDSA-DES-CBC3-SHA:SRP-DSS-3DES-EDE-CBC-SHA:SRP-RSA-3DES-EDE-CBC-SHA:SRP-3DES-EDE-CBC-SHA:EDH-RSA-DES-CBC3-SHA:EDH-DSS-DES-CBC3-SHA:AECDH-DES-CBC3-SHA:ADH-DES-CBC3-SHA:ECDH-RSA-DES-CBC3-SHA:ECDH-ECDSA-DES-CBC3-SHA:DES-CBC3-SHA:PSK-3DES-EDE-CBC-SHA:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:SRP-DSS-AES-128-CBC-SHA:SRP-RSA-AES-128-CBC-SHA:SRP-AES-128-CBC-SHA:DHE-DSS-AES128-GCM-SHA256:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES128-SHA256:DHE-DSS-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA:DHE-RSA-SEED-SHA:DHE-DSS-SEED-SHA:DHE-RSA-CAMELLIA128-SHA:DHE-DSS-CAMELLIA128-SHA:AECDH-AES128-SHA:ADH-AES128-GCM-SHA256:ADH-AES128-SHA256:ADH-AES128-SHA:ADH-SEED-SHA:ADH-CAMELLIA128-SHA:ECDH-RSA-AES128-GCM-SHA256:ECDH-ECDSA-AES128-GCM-SHA256:ECDH-RSA-AES128-SHA256:ECDH-ECDSA-AES128-SHA256:ECDH-RSA-AES128-SHA:ECDH-ECDSA-AES128-SHA:AES128-GCM-SHA256:AES128-SHA256:AES128-SHA:SEED-SHA:CAMELLIA128-SHA:PSK-AES128-CBC-SHA:ECDHE-RSA-RC4-SHA:ECDHE-ECDSA-RC4-SHA:AECDH-RC4-SHA:ADH-RC4-MD5:ECDH-RSA-RC4-SHA:ECDH-ECDSA-RC4-SHA:RC4-SHA:RC4-MD5:PSK-RC4-SHA:EDH-RSA-DES-CBC-SHA:EDH-DSS-DES-CBC-SHA:ADH-DES-CBC-SHA:DES-CBC-SHA:EXP-EDH-RSA-DES-CBC-SHA:EXP-EDH-DSS-DES-CBC-SHA:EXP-ADH-DES-CBC-SHA:EXP-DES-CBC-SHA:EXP-RC2-CBC-MD5:EXP-ADH-RC4-MD5:EXP-RC4-MD5:ECDHE-RSA-NULL-SHA:ECDHE-ECDSA-NULL-SHA:AECDH-NULL-SHA:ECDH-RSA-NULL-SHA:ECDH-ECDSA-NULL-SHA:NULL-SHA256:NULL-SHA:NULL-MD5'


class ServerSocketException(Exception):

    def __init__(self, message):
        super(ServerSocketException, self).__init__(message)
        self.message = message


class ServerSocket:

    def __init__(self, port=None, ssl_mode=False):
        self.port = port
        self._ssl_mode = ssl_mode
        self._sock = None
        self._listening = False
        self._waiting_for_connection = False
        self._closed = False

        self._init_ssl_context()

    def listen(self, port=None, ssl_mode=None):
        self._listening = False

        if self._closed:
            raise ServerSocketException('Cannot listen to a port once socket has been closed')

        if port is not None:
            self.port = port
        if ssl_mode is not None:
            self._ssl_mode = ssl_mode

        self._close_pending_connection()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind(('', self.port))
        self._sock.listen(0)
        self._listening = True

    def accept(self):
        self._waiting_for_connection = True
        try:
            sock, addr = self._sock.accept()
            if self._ssl_mode:
                ssl_sock = self._ssl_context.wrap_socket(sock, server_side=True)
                return ClientSocket(ssl_sock, addr)
            else:
                return ClientSocket(sock, addr)
        except Exception as e:
            raise e
        finally:
            self._waiting_for_connection = False

    def close(self):
        self._closed = True
        self._listening = False
        self._close_pending_connection()
        self._close_socket()

    def _init_ssl_context(self):
        self._ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self._ssl_context.set_ciphers(OPENSSL_CIPHERS)

    def _close_pending_connection(self):
        if not self._waiting_for_connection:
            return

        try:
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('127.0.0.1', self.port))
        except Exception:
            pass

    def _close_socket(self):
        if self._sock is None:
            return

        self._sock.close()
        self._sock = None

    @property
    def get_ssl_mode(self):
        return self._ssl_mode

    @property
    def is_listening(self):
        return self._listening


class ClientSocket:

    READ_BUFFER_SIZE = 1024
    ENCODING = 'UTF-8'

    def __init__(self, sock=None, addr=None, host=None, port=None, ssl_mode=False, ssl_ciphers=OPENSSL_CIPHERS):
        self.read_buffer_size = self.READ_BUFFER_SIZE
        self.encoding = self.ENCODING
        self._sock = sock
        self._addr = addr
        self._host = host
        self._port = port
        self._ssl_mode = ssl_mode
        self._ssl_ciphers = ssl_ciphers
        self._connected = (sock is not None and addr is not None)

    def connect(self, host=None, port=None, ssl_mode=None, ssl_ciphers=None):
        self.disconnect()

        if host is not None:
            self._host = host
        if port is not None:
            self._port = port
        if ssl_mode is not None:
            self._ssl_mode = ssl_mode
        if ssl_ciphers is not None:
            self._ssl_ciphers = ssl_ciphers

        if self._ssl_mode:
            self._sock = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), ciphers=self._ssl_ciphers)
        else:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._sock.connect((self._host, self._port))
        self._addr = self._host, self._port
        self._connected = True

    def disconnect(self):
        self._connected = False
        if self._sock is not None:
            self._sock.close()
            self._sock = None
            self._addr = None

    def send(self, data):
        try:
            if sys.hexversion > 0x03000000:
                # Python v3 and above
                self._sock.send(bytes(data, self.encoding))
            else:
                self._sock.send(data)
        except Exception as e:
            self._connected = False
            raise e

    def receive(self):
        try:
            if sys.hexversion > 0x03000000:
                # Python 3 and above
                return self._sock.recv(self.read_buffer_size).decode(self.encoding)
            else:
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
    def get_ssl_mode(self):
        return self._ssl_mode

    @property
    def is_connected(self):
        return self._connected
