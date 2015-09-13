__author__ = 'arifal'


class BetradarMessage:

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

    # Ruby-friendly regex pattern:
    #   <match\smatchid="(?<match_id>[^"]+)"
    SUBSCRIBE_REQ_PATTERN = r'<match\smatchid="(?<match_id>[^"]+)"'

    MATCHLIST_HOURS_BACK = 12
    MATCHLIST_HOURS_FORWARD = 12
    MATCHLIST_INCLUDE_AVAILABLE = 'yes'

    SUBSCRIPTION_FEED_TYPE = 'full'
    SUBSCRIPTION_DELTA_START_MESSAGE = 0
    SUBSCRIPTION_DELTA_MESSAGE_DELAY = 5000

    def __init__(self):
        pass

    def create_login_request(self, host, password):
        return self.LOGIN_REQ.format(host, password)

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
