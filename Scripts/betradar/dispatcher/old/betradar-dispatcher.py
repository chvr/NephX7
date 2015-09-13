# Betradar Dispatcher
#
# Run using 'python3 betradar-dispatcher.py'
#
# To create server.key:
#     openssl genrsa -out server.key 4096
#
# To create server.crt:
#     openssl req -new -x509 -days 1826 -key server.key -out server.crt


# User Settings =============================================================

APP_FEEDS_PORT = 6010
APP_MATCHLIST_PORT = 6020

LOG_MATCHES_TO_FILE_INDIVIDUALLY = True  # todo: implement as needed

# End of User Settings ======================================================


import socket
import ssl
import re
import time
import threading
import traceback
import sys


PROVIDER_HOST, PROVIDER_PORT = 'scouttest.betradar.com', 2047
PROVIDER_USER, PROVIDER_PWD = 'kambiscout', 'Kambi123'
PROVIDER_KEEP_ALIVE_INTERVAL_SEC = 5
ENCODING = 'UTF-8'
READ_BUFFER_SIZE = 4096
LOG_FILE_EXT = '.log'
SPORTS = ['TENNIS']  # Values must be in UPPERCASE format
OPENSSL_CIPHERS = 'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:SRP-DSS-AES-256-CBC-SHA:SRP-RSA-AES-256-CBC-SHA:SRP-AES-256-CBC-SHA:DHE-DSS-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA256:DHE-RSA-AES256-SHA:DHE-DSS-AES256-SHA:DHE-RSA-CAMELLIA256-SHA:DHE-DSS-CAMELLIA256-SHA:AECDH-AES256-SHA:ADH-AES256-GCM-SHA384:ADH-AES256-SHA256:ADH-AES256-SHA:ADH-CAMELLIA256-SHA:ECDH-RSA-AES256-GCM-SHA384:ECDH-ECDSA-AES256-GCM-SHA384:ECDH-RSA-AES256-SHA384:ECDH-ECDSA-AES256-SHA384:ECDH-RSA-AES256-SHA:ECDH-ECDSA-AES256-SHA:AES256-GCM-SHA384:AES256-SHA256:AES256-SHA:CAMELLIA256-SHA:PSK-AES256-CBC-SHA:ECDHE-RSA-DES-CBC3-SHA:ECDHE-ECDSA-DES-CBC3-SHA:SRP-DSS-3DES-EDE-CBC-SHA:SRP-RSA-3DES-EDE-CBC-SHA:SRP-3DES-EDE-CBC-SHA:EDH-RSA-DES-CBC3-SHA:EDH-DSS-DES-CBC3-SHA:AECDH-DES-CBC3-SHA:ADH-DES-CBC3-SHA:ECDH-RSA-DES-CBC3-SHA:ECDH-ECDSA-DES-CBC3-SHA:DES-CBC3-SHA:PSK-3DES-EDE-CBC-SHA:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:SRP-DSS-AES-128-CBC-SHA:SRP-RSA-AES-128-CBC-SHA:SRP-AES-128-CBC-SHA:DHE-DSS-AES128-GCM-SHA256:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES128-SHA256:DHE-DSS-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA:DHE-RSA-SEED-SHA:DHE-DSS-SEED-SHA:DHE-RSA-CAMELLIA128-SHA:DHE-DSS-CAMELLIA128-SHA:AECDH-AES128-SHA:ADH-AES128-GCM-SHA256:ADH-AES128-SHA256:ADH-AES128-SHA:ADH-SEED-SHA:ADH-CAMELLIA128-SHA:ECDH-RSA-AES128-GCM-SHA256:ECDH-ECDSA-AES128-GCM-SHA256:ECDH-RSA-AES128-SHA256:ECDH-ECDSA-AES128-SHA256:ECDH-RSA-AES128-SHA:ECDH-ECDSA-AES128-SHA:AES128-GCM-SHA256:AES128-SHA256:AES128-SHA:SEED-SHA:CAMELLIA128-SHA:PSK-AES128-CBC-SHA:ECDHE-RSA-RC4-SHA:ECDHE-ECDSA-RC4-SHA:AECDH-RC4-SHA:ADH-RC4-MD5:ECDH-RSA-RC4-SHA:ECDH-ECDSA-RC4-SHA:RC4-SHA:RC4-MD5:PSK-RC4-SHA:EDH-RSA-DES-CBC-SHA:EDH-DSS-DES-CBC-SHA:ADH-DES-CBC-SHA:DES-CBC-SHA:EXP-EDH-RSA-DES-CBC-SHA:EXP-EDH-DSS-DES-CBC-SHA:EXP-ADH-DES-CBC-SHA:EXP-DES-CBC-SHA:EXP-RC2-CBC-MD5:EXP-ADH-RC4-MD5:EXP-RC4-MD5:ECDHE-RSA-NULL-SHA:ECDHE-ECDSA-NULL-SHA:AECDH-NULL-SHA:ECDH-RSA-NULL-SHA:ECDH-ECDSA-NULL-SHA:NULL-SHA256:NULL-SHA:NULL-MD5'

# Ruby-friendly regex pattern:
#   booked="(?<booked>[^"]+)"(\s|\S)+?matchid="(?<match_id>[^"]+)"(\s|\S)+?start="(?<match_timestamp>[^"]+)"(\s|\S)+?t1name="(?<team1>[^"]+)"(\s|\S)+?t2name="(?<team2>[^"]+)"(\s|\S)+?status.+?name="(?<status>[^"]+)"(\s|\S)+?start="(?<status_timestamp>[^"]+)"(\s|\S)+?sport.+?name="(?<sport>[^"]+)"
MATCHLIST_PATTERN = r'booked="(?P<booked>[^"]+)"(\s|\S)+?' \
                    r'matchid="(?P<match_id>[^"]+)"(\s|\S)+?' \
                    r'start="(?P<match_timestamp>[^"]+)"(\s|\S)+?' \
                    r't1name="(?P<team1>[^"]+)"(\s|\S)+?' \
                    r't2name="(?P<team2>[^"]+)"(\s|\S)+?' \
                    r'status.+?name="(?P<status>[^"]+)"(\s|\S)+?' \
                    r'start="(?P<status_timestamp>[^"]+)"(\s|\S)+?' \
                    r'sport.+?name="(?P<sport>[^"]+)"'
#   matchid[=|:]["|\s](?<match_id>[^"|^\s]+)["|\s]
MATCH_ID_PATTERN = r'matchid[=|:]["|\s](?P<match_id>[^"|^\s]+)["|\s]'


# Logger class ==============================================================

class Logger:
    def __init__(self, name):
        self._name = name

    def log(self, message):
        print('[{}] {}'.format(self._name, message))

    def log_error(self, message):
        print('ERROR: [{}] {}'.format(self._name, message))

# End of Logger class =======================================================


# BetRadarMessage class =====================================================

class BetRadarMessage:

    NEWLINE = '\r\n'
    DELIMITER = NEWLINE + NEWLINE

    LOGIN_REQ = '<login><credential><loginname value="{}"/><password value="{}"/></credential></login>'
    LOGOUT_REQ = '<logout/>'
    MATCHLIST_REQ = '<matchlist hoursback="{}" hoursforward="{}" includeavailable="{}"/>'
    SUBSCRIBE_REQ = '<match matchid="{}" feedtype="{}"/>'
    SUBSCRIBE_DELTA_REQ = '<match matchid="{}" messagedelay="{}" startmessage="{}" feedtype="delta"/>'
    UNSUBSCRIBE_REQ = '<matchstop matchid="{}"/>'
    BOOKMATCH_REQ = '<bookmatch matchid="{}"/>'
    KEEP_ALIVE_REQ = '<ct/>'

    KEEP_ALIVE_RESP = '<ct/>{0}{0}'.format(NEWLINE)

    MATCHLIST_HOURS_BACK = 48
    MATCHLIST_HOURS_FORWARD = 48
    MATCHLIST_INCLUDE_AVAILABLE = 'yes'

    SUBSCRIPTION_FEED_TYPE = 'full'
    SUBSCRIPTION_DELTA_START_MESSAGE = 0
    SUBSCRIPTION_DELTA_MESSAGE_DELAY = 1000

    def __init__(self):
        pass

    def create_login_request(self):
        return self.LOGIN_REQ.format(PROVIDER_USER, PROVIDER_PWD)

    def create_logout_request(self):
        return self.LOGOUT_REQ

    def create_matchlist_request(self, hours_back=MATCHLIST_HOURS_BACK, hours_forward=MATCHLIST_HOURS_FORWARD, include_available=MATCHLIST_INCLUDE_AVAILABLE):
        return self.MATCHLIST_REQ.format(hours_back, hours_forward, include_available)

    def create_subscribe_request(self, match_id, feed_type=SUBSCRIPTION_FEED_TYPE):
        return self.SUBSCRIBE_REQ.format(match_id, feed_type)

    def create_subscribe_delta_request(self, match_id, message_delay=SUBSCRIPTION_DELTA_MESSAGE_DELAY, start_message=SUBSCRIPTION_DELTA_START_MESSAGE):
        return self.SUBSCRIBE_DELTA_REQ.format(match_id, message_delay, start_message)

    def create_unsubscribe_request(self, match_id):
        return self.UNSUBSCRIBE_REQ.format(match_id)

    def create_bookmatch_request(self, match_id):
        return self.BOOKMATCH_REQ.format(match_id)

    def create_keep_alive_request(self):
        return self.KEEP_ALIVE_REQ

    def get_keep_alive_response(self):
        return self.KEEP_ALIVE_RESP

# End of BetRadarMessage class ==============================================


# ClientHandler class =======================================================

class ClientHandler:
    def __init__(self, name, new_line='\n'):
        self._logger = Logger(name)

        self._sock = None
        self._stop = False
        self._new_line = new_line

    def start(self, port):
        self._log('Started.')

        self._sock = socket.socket()
        self._sock.bind(('', port))
        self._sock.listen(0)

        self._log('Listening to port {}...'.format(port))

        while not self._stop:
            new_sock, addr = self._sock.accept()

            try:
                ssl_sock = ssl.wrap_socket(new_sock, server_side=True, certfile='server.crt', keyfile='server.key')
                self._log('Accepted new connection from {}'.format(addr))
                self._handle_client(ssl_sock, addr)
            except ssl.SSLEOFError:
                break

        self._log('Stopped.')

    def stop(self):
        self._log('Stopping...')
        self._stop = True

        if self._sock is not None:
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('', APP_FEEDS_PORT))
            self._sock.close()

    def is_stopped(self):
        return self._stop

    def send(self, data):
        try:
            if sys.hexversion > 0x03000000:
                # Python 3 and above
                self._sock.send(bytes(data, ENCODING))
            else:
                self._sock.send(data)

            self._log('Data sent to client: [{}]'.format(data.replace(self._new_line, '^')))
        except (OSError, TypeError) as e:
            if not self._stop:
                self._log_error('Unable to send request to client - {}'.format(e))
                traceback.print_exc()

    def _receive(self, sock):
        data = None

        try:
            if sys.hexversion > 0x03000000:
                # Python 3 and above
                data = sock.recv(READ_BUFFER_SIZE).decode(ENCODING) or ''
            else:
                data = sock.recv(READ_BUFFER_SIZE) or ''

            self._log('Data received from client: [{}]'.format(data.replace(self._new_line, '^')))
        except (OSError, TypeError) as e:
            if not self._stop:
                self._log_error('Unable to receive response from client - {}'.format(e))
                traceback.print_exc()
                self.stop()

        return data

    def _handle_client(self, sock, addr):
        provider_handler = BetradarHandler('BetradarHandler_{}'.format(addr))
        provider_handler.set_feeds_handler(provider_handler)
        #provider_handler.set_matchlist_handler(provider_handler)  # todo: fix this

        try:
            provider_handler_thread = threading.Thread(target=provider_handler.start)
            provider_handler_thread.start()

            while not provider_handler.is_connected():
                time.sleep(0.3)

            while not self._stop:
                data = self._receive(sock)
                self._process(data, provider_handler)
        finally:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            provider_handler.stop()

    def _process(self, data, provider_handler):
        provider_handler.send(data)
        self._log('Pushed data to provider: [{}]'.format(data.replace(self._new_line, '^')))

    def _log(self, message):
        self._logger.log(message)

    def _log_error(self, message):
        self._logger.log_error(message)

# End of ClientHandler class ================================================


# BetradarHandler class =====================================================

class BetradarHandler:
    def __init__(self, name, host=PROVIDER_HOST, port=PROVIDER_PORT):
        self._logger = Logger(name)
        self._host = host
        self._port = port
        self._feeds_handler = None
        self._matchlist_handler = None

        self._ssl_sock = None
        self._connected = False
        self._stop = False
        self._keep_alive_timer_thread = None
        self._betRadarMessage = BetRadarMessage()
        self._new_line = BetRadarMessage.NEWLINE
        self._data_delimiter = BetRadarMessage.DELIMITER

    def set_feeds_handler(self, feeds_handler):
        self._feeds_handler = feeds_handler

    def set_matchlist_handler(self, matchlist_handler):
        self._matchlist_handler = matchlist_handler

    def start(self):
        self._log('Started.')

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)

        self._ssl_sock = ssl.wrap_socket(sock, ciphers=OPENSSL_CIPHERS)

        self._log('Connecting to {}:{}...'.format(self._host, self._port))
        self._ssl_sock.connect((self._host, self._port))
        self._connected = True

        self._log('Starting KeepAliveTimer thread...')
        self._start_keep_alive_timer()

        data = ''
        while not self._stop:
            data = self._receive(data)
            data_chunks, data = self._parse(data)
            self._process(data_chunks)

        self._log('Stopped.')

    def stop(self):
        self._log('Stopping...')
        self._stop = True

        if self._ssl_sock is not None:
            self._ssl_sock.close()

    def is_connected(self):
        return self._connected

    def is_stopped(self):
        return self._stop

    def are_threads_alive(self):
        return self._keep_alive_timer_thread.is_alive()

    def send(self, request):
        self._log('Request: {}'.format(request.replace(self._new_line, '^')))
        try:
            data = request + BetRadarMessage.NEWLINE
            if sys.hexversion > 0x03000000:
                # Python 3 and above
                self._ssl_sock.send(bytes(data, ENCODING))
                pass
            else:
                self._ssl_sock.send(data)
                pass
        except (OSError, TypeError) as e:
            if not self._stop:
                self._log_error('Unable to send request to provider - {}'.format(e))
                traceback.print_exc()
                self.stop()

    def _receive(self, data=''):
        try:
            if sys.hexversion > 0x03000000:
                # Python 3 and above
                data += self._ssl_sock.recv(READ_BUFFER_SIZE).decode(ENCODING) or ''
            else:
                data += self._ssl_sock.recv(READ_BUFFER_SIZE) or ''

            self._log('Data received from provider: [{}]'.format(data.replace(self._new_line, '^')))
        except (OSError, TypeError) as e:
            if not self._stop:
                self._log_error('Unable to receive response from provider - {}'.format(e))
                traceback.print_exc()
                self.stop()

        return data

    def _parse(self, data):
        if self._data_delimiter not in data:
            return [], data

        data_list = data.split(self._data_delimiter)
        incomplete_data = self._data_delimiter.join(data_list[-1:])
        data_chunks = data_list[:-1]

        return data_chunks, incomplete_data

    def _process(self, data_chunks):
        for data_chunk in data_chunks:
            self._log('Processing data: [{}]'.format(data_chunk.replace(self._new_line, '^')))
            if self._feeds_handler is not None:  # todo: fix this
                self._feeds_handler.send(data_chunk)
            if self._matchlist_handler is not None:  # todo: fix this
                self._matchlist_handler.send(data_chunk)

    def _start_keep_alive_timer(self):
        if self._stop:
            self._log('KeepAliveTimer thread stopped.')
            return

        self.send(self._betRadarMessage.create_keep_alive_request())

        self._keep_alive_timer_thread = threading.Timer(PROVIDER_KEEP_ALIVE_INTERVAL_SEC, self._start_keep_alive_timer)
        self._keep_alive_timer_thread.start()

    def _login(self):
        self.send(self._betRadarMessage.create_login_request())

    def _log(self, message):
        self._logger.log(message)

    def _log_error(self, message):
        self._logger.log_error(message)

# End of BetradarHandler class ==============================================


def main():
    feeds_handler = ClientHandler('FeedsHandler', BetRadarMessage.NEWLINE)
    matchlist_handler = ClientHandler('MatchlistHandler', BetRadarMessage.NEWLINE)

    feeds_handler_thread = threading.Thread(target=feeds_handler.start, args=[APP_FEEDS_PORT])
    matchlist_handler_thread = threading.Thread(target=matchlist_handler.start, args=[APP_MATCHLIST_PORT])

    try:
        feeds_handler_thread.start()
        matchlist_handler_thread.start()

        while True:
            if feeds_handler.is_stopped():
                break

            try:
                time.sleep(0.3)
            except KeyboardInterrupt:
                break
    finally:
        feeds_handler.stop()
        matchlist_handler.stop()

    while feeds_handler_thread.is_alive() or matchlist_handler_thread.is_alive(): #todo threads dead
        time.sleep(0.3)

    print('Exited.')
    sys.exit()


main()
