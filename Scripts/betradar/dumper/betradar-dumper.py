# How To Use:
#
# Run using 'python3 betradar-dumper.py' then watch the output file 'all-matches.txt' as it gets new feeds from
# provider. Please be noted that feeds are subject to availability.
#
# Note: currently requires Python v3

import socket
import ssl
import re
import time
import threading
import traceback
import sys

#HOST, PORT = 'localhost', 6020
HOST, PORT = 'scouttest.betradar.com', 2047
USER, PWD = 'kambiscout', 'Kambi123'

OUTPUT_FILE = 'all-matches.txt'
MATCHLIST_FILE = 'matchlist.txt'

ENCODING = 'UTF-8'
READ_BUFFER_SIZE = 4096

SPORTS = ['TENNIS']  # Values must be in UPPERCASE format
KEEP_ALIVE_INTERVAL_SEC = 5
MATCHLIST_INTERVAL_SEC = 3600 * 48
AUTO_SUBSCRIBE = False
MATCH_ID_AS_OUTPUT_FILE = True

RESPONSE_PADDING = '    '

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

OPENSSL_CIPHERS = 'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:SRP-DSS-AES-256-CBC-SHA:SRP-RSA-AES-256-CBC-SHA:SRP-AES-256-CBC-SHA:DHE-DSS-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA256:DHE-RSA-AES256-SHA:DHE-DSS-AES256-SHA:DHE-RSA-CAMELLIA256-SHA:DHE-DSS-CAMELLIA256-SHA:AECDH-AES256-SHA:ADH-AES256-GCM-SHA384:ADH-AES256-SHA256:ADH-AES256-SHA:ADH-CAMELLIA256-SHA:ECDH-RSA-AES256-GCM-SHA384:ECDH-ECDSA-AES256-GCM-SHA384:ECDH-RSA-AES256-SHA384:ECDH-ECDSA-AES256-SHA384:ECDH-RSA-AES256-SHA:ECDH-ECDSA-AES256-SHA:AES256-GCM-SHA384:AES256-SHA256:AES256-SHA:CAMELLIA256-SHA:PSK-AES256-CBC-SHA:ECDHE-RSA-DES-CBC3-SHA:ECDHE-ECDSA-DES-CBC3-SHA:SRP-DSS-3DES-EDE-CBC-SHA:SRP-RSA-3DES-EDE-CBC-SHA:SRP-3DES-EDE-CBC-SHA:EDH-RSA-DES-CBC3-SHA:EDH-DSS-DES-CBC3-SHA:AECDH-DES-CBC3-SHA:ADH-DES-CBC3-SHA:ECDH-RSA-DES-CBC3-SHA:ECDH-ECDSA-DES-CBC3-SHA:DES-CBC3-SHA:PSK-3DES-EDE-CBC-SHA:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:SRP-DSS-AES-128-CBC-SHA:SRP-RSA-AES-128-CBC-SHA:SRP-AES-128-CBC-SHA:DHE-DSS-AES128-GCM-SHA256:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES128-SHA256:DHE-DSS-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA:DHE-RSA-SEED-SHA:DHE-DSS-SEED-SHA:DHE-RSA-CAMELLIA128-SHA:DHE-DSS-CAMELLIA128-SHA:AECDH-AES128-SHA:ADH-AES128-GCM-SHA256:ADH-AES128-SHA256:ADH-AES128-SHA:ADH-SEED-SHA:ADH-CAMELLIA128-SHA:ECDH-RSA-AES128-GCM-SHA256:ECDH-ECDSA-AES128-GCM-SHA256:ECDH-RSA-AES128-SHA256:ECDH-ECDSA-AES128-SHA256:ECDH-RSA-AES128-SHA:ECDH-ECDSA-AES128-SHA:AES128-GCM-SHA256:AES128-SHA256:AES128-SHA:SEED-SHA:CAMELLIA128-SHA:PSK-AES128-CBC-SHA:ECDHE-RSA-RC4-SHA:ECDHE-ECDSA-RC4-SHA:AECDH-RC4-SHA:ADH-RC4-MD5:ECDH-RSA-RC4-SHA:ECDH-ECDSA-RC4-SHA:RC4-SHA:RC4-MD5:PSK-RC4-SHA:EDH-RSA-DES-CBC-SHA:EDH-DSS-DES-CBC-SHA:ADH-DES-CBC-SHA:DES-CBC-SHA:EXP-EDH-RSA-DES-CBC-SHA:EXP-EDH-DSS-DES-CBC-SHA:EXP-ADH-DES-CBC-SHA:EXP-DES-CBC-SHA:EXP-RC2-CBC-MD5:EXP-ADH-RC4-MD5:EXP-RC4-MD5:ECDHE-RSA-NULL-SHA:ECDHE-ECDSA-NULL-SHA:AECDH-NULL-SHA:ECDH-RSA-NULL-SHA:ECDH-ECDSA-NULL-SHA:NULL-SHA256:NULL-SHA:NULL-MD5'

# MatchEntry class ==========================================================

class MatchEntry:

    def __init__(self, match_id, match_timestamp, sport, team1, team2, status, status_timestamp, booked):
        self.match_id = match_id
        self.match_timestamp = match_timestamp
        self.sport = sport
        self.team1 = team1
        self.team2 = team2
        self.status = status
        self.status_timestamp = status_timestamp
        self.booked = (booked != '0')

    def __repr__(self):
        return self._to_string()

    def __str__(self):
        return self._to_string()

    def _to_string(self):
        return '{} [MatchID={}, MatchTimestamp={}, Sport={}, Team1={}, Team2={}, Status={}, StatusTimestamp={}, Booked={}]' \
            .format(MatchEntry.__name__, self.match_id, self.match_timestamp, self.sport, self.team1, self.team2, self.status, self.status_timestamp, self.booked)

# End of MatchEntry class ===================================================

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

    def create_login_request(self, user=USER, pwd=PWD):
        return self.LOGIN_REQ.format(user, pwd)

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


running = True
subscribed_matches = []
betRadarMessage = BetRadarMessage()
keep_alive_timer_thread = None
matchlist_timer_thread = None
ssl_socket = None

def main():
    process_responses_thread = None
    try:
        connect()
        send(betRadarMessage.create_login_request())

        start_keep_alive_timer()
        start_matchlist_timer()

        process_responses_thread = threading.Thread(target=process)
        process_responses_thread.start()

        while running:
            process_user_input()
    finally:
        if running:
            close()

        while process_responses_thread and process_responses_thread.is_alive():
            time.sleep(0.01)
            pass

        print('Exited.')
        sys.exit()


def process_user_input():
    cmd_params = None
    try:
        cmd_params = input().split()
    except KeyboardInterrupt:
        if running:
            print('Process has been interrupted!')
            close()

    if not cmd_params:
        return

    if cmd_params[0] in ['exit', 'quit', 'x', 'q']:
        close()
    elif cmd_params[0] in ['login']:
        send(betRadarMessage.create_login_request(*cmd_params[1:]))
    elif cmd_params[0] in ['logout']:
        send(betRadarMessage.create_logout_request())
    elif cmd_params[0] in ['list', 'l']:
        send(betRadarMessage.create_matchlist_request(*cmd_params[1:]))
    elif cmd_params[0] in ['subscribe', 'register', 'sub', 'reg', 's', 'r']:
        send(betRadarMessage.create_subscribe_request(*cmd_params[1:]))
    elif cmd_params[0] in ['subscribe_delta', 'register_delta', 'subd', 'regd', 'sd', 'rd']:
        send(betRadarMessage.create_subscribe_delta_request(*cmd_params[1:]))
    elif cmd_params[0] in ['unsubscribe', 'unregister', 'unsub', 'unreg', 'u']:
        send(betRadarMessage.create_unsubscribe_request(*cmd_params[1:]))
    elif cmd_params[0] in ['bookmatch', 'book', 'bm', 'b']:
        send(betRadarMessage.create_bookmatch_request(*cmd_params[1:]))
    else:
        send(' '.join(cmd_params))


def process_matchlist_response(matchlist_xml):
    matchlist_entries = []

    for m in re.finditer(MATCHLIST_PATTERN, matchlist_xml):
        entry = MatchEntry(
            m.group('match_id')
            , m.group('match_timestamp')
            , m.group('sport')
            , m.group('team1')
            , m.group('team2')
            , m.group('status')
            , m.group('status_timestamp')
            , m.group('booked')
        )
        matchlist_entries.append(entry)

    return matchlist_entries


def start_keep_alive_timer():
    global keep_alive_timer_thread

    send(betRadarMessage.create_keep_alive_request())

    keep_alive_timer_thread = threading.Timer(KEEP_ALIVE_INTERVAL_SEC, start_keep_alive_timer)
    keep_alive_timer_thread.start()


def start_matchlist_timer():
    global matchlist_timer_thread

    send(betRadarMessage.create_matchlist_request())

    matchlist_timer_thread = threading.Timer(MATCHLIST_INTERVAL_SEC, start_matchlist_timer)
    matchlist_timer_thread.start()


def connect():
    global ssl_socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    ssl_socket = ssl.wrap_socket(sock, ciphers=OPENSSL_CIPHERS)
    ssl_socket.connect((HOST, PORT))


def close():
    global running, ssl_socket

    print('Cleaning up...')

    running = False

    keep_alive_timer_thread.cancel()
    matchlist_timer_thread.cancel()

    if ssl_socket is not None:
        ssl_socket.close()


def append_to_output_file(message, output_file):
    try:
        with open(output_file, 'a') as f:
            f.write(message)
            f.flush()
    except IOError as e:
        print('ERROR: Unable to write to output file \'{}\' ({}).' % (__file__, OUTPUT_FILE, e))
        traceback.print_exc()
        close()


def send(request):
    print('Request  : {}'.format(request))
    try:
        data = request + BetRadarMessage.NEWLINE
        if sys.hexversion > 0x03000000:
            # Python 3 and above
            ssl_socket.send(bytes(data, ENCODING))
        else:
            ssl_socket.send(data)
    except (OSError, TypeError) as e:
        if running:
            print('ERROR: Unable to send request to server - {}'.format(e))
            traceback.print_exc()
            close()

def process():
    while running:
        resp = receive()
        process_response(resp)


def receive():
    resp = ''
    while running and ssl_socket and BetRadarMessage.DELIMITER not in resp:
        try:
            if sys.hexversion > 0x03000000:
                # Python 3 and above
                resp += ssl_socket.recv(READ_BUFFER_SIZE).decode(ENCODING) or ''
            else:
                resp += ssl_socket.recv(READ_BUFFER_SIZE) or ''
        except (OSError, TypeError) as e:
            if running:
                print('ERROR: Unable to receive response from server - {}'.format(e))
                traceback.print_exc()
                close()

        if betRadarMessage.get_keep_alive_response() in resp:
            # Suppress keep-alive from server from getting processed
            print('Response :\n{}{}'.format(RESPONSE_PADDING, format_response(resp)))

            resp = resp.replace(betRadarMessage.get_keep_alive_response(), '')
            continue

    if len(resp) > 0:
        print('Response :\n{}{}'.format(RESPONSE_PADDING, format_response(resp)))

    return resp


def process_response(resp):
    if 'matchlist' in resp:
        append_to_output_file(resp, MATCHLIST_FILE)

        if not AUTO_SUBSCRIBE:
            return

        matchlist_entries = process_matchlist_response(resp)
        for entry in matchlist_entries:
            if entry.match_id in subscribed_matches:
                continue

            if entry.sport.upper() not in SPORTS:
                continue

            print('Registering match: {}'.format(entry))
            if not entry.booked:
                # Book a match
                send(betRadarMessage.create_bookmatch_request(entry.match_id))

            # Subscribe a match
            send(betRadarMessage.create_subscribe_delta_request(entry.match_id))
            subscribed_matches.append(entry.match_id)
    else:
        if MATCH_ID_AS_OUTPUT_FILE:
            # Write to specific match output file
            match_id = parse_match_id(resp)
            if match_id is not None:
                append_to_output_file(resp, '{}.txt'.format(match_id))

        # Write to combined output file
        append_to_output_file(resp, OUTPUT_FILE)


def parse_match_id(resp):
    for m in re.finditer(MATCH_ID_PATTERN, resp):
        return m.group("match_id")

    return None


def format_response(resp):
    return resp.replace(betRadarMessage.DELIMITER, betRadarMessage.NEWLINE).replace(betRadarMessage.NEWLINE, '\n' + RESPONSE_PADDING)


main()
