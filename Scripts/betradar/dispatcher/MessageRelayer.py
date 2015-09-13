__author__ = 'Chyros'


import random
import re
import logging

from BetradarMessage import BetradarMessage


class MessageRelayer:

    # Ruby: (<status.*?name=")(?<status>[^"]+)"
    MATCHLIST_STATUS_SEARCH_PATTERN = r'(<status.*?name=")(?P<status>[^"]+)'
    MATCHLIST_STATUS_REPLACE_PATTERN = r'\g<1>{}'
    # Ruby: (<match\s.*?\smatchid=")(?<match_id>[^"]+)
    MATCHLIST_ID_SEARCH_PATTERN = r'(<match\s.*?\smatchid=")(?P<match_id>[^"]+)'
    MATCHLIST_ID_REPLACE_PATTERN = r'\g<1>{}'
    # Ruby: matchid="(?<match_id>[^"]+)"
    MATCH_ID_PATTERN = r'matchid="(?P<match_id>[^"]+)"'

    SUBSCRIPTION_MESSAGE_DELAY = 5000
    SUBSCRIPTION_START_MESSAGE = 0

    def __init__(self, src_sock, dst_sock, delimiter, name, provider_mode=False, use_booked_match_ids=False, booked_match_ids=None):
        self._src_sock = src_sock
        self._dst_sock = dst_sock
        self._data_delimiter = delimiter
        self._name = name
        self._provider_mode = provider_mode
        self._use_booked_match_ids = use_booked_match_ids
        self._booked_match_ids = booked_match_ids
        self._stop = False
        self._data_newline = BetradarMessage.NEWLINE

        logging.info('{} - MessageRelayer has started.'.format(self._name, self._src_sock.get_addr, self._dst_sock.get_addr))

    def start(self):
        try:
            data = ''
            while not self._stop:
                data = self._receive(data)
                data_chunks, data = self._parse(data)
                self._process(data_chunks)
        finally:
            logging.info('{} - MessageRelayer has stopped.'.format(self._name, self._src_sock.get_addr, self._dst_sock.get_addr))
            if self._src_sock is not None:
                self._src_sock.disconnect()
            if self._dst_sock is not None:
                self._dst_sock.disconnect()

    def stop(self):
        self._stop = True

    def _receive(self, data=''):
        try:
            data += self._src_sock.receive() or ''
        except AttributeError:
            pass
        except Exception as e:
            logging.error('{} - Unable to receive message - {}'.format(self._name, e))
            self._stop = True

        return data

    def _send(self, data):
        try:
            self._dst_sock.send(data)
        except AttributeError:
            pass
        except Exception as e:
            logging.error('{} - Unable to send message - {}'.format(self._name, e))
            self._stop = True

    def _parse(self, data):
        if self._data_delimiter not in data:
            return [], data

        data_list = data.split(self._data_delimiter)
        incomplete_data = self._data_delimiter.join(data_list[-1:])
        data_chunks = data_list[:-1]

        return data_chunks, incomplete_data

    def _process(self, data_chunks):
        for data in data_chunks:
            data += self._data_delimiter
            if self._provider_mode:
                data = self._process_provider_data(data)
            else:
                data = self._process_client_data(data)

            if data is not None:
                self._send(data)
                logging.info('{} - Relayed message: [{}].'.format(
                    self._name
                    , data.replace(self._data_newline, '^')
                ))

    def _process_provider_data(self, data):
        if '<matchlist>' in data:
            if self._use_booked_match_ids:
                data = self._update_match_ids(data)

            data = self._update_match_status(data)

        return data

    def _process_client_data(self, data):
        if '<matchlist ' in data:
            data = self._create_matchlist_request()
        elif all(xml_element in data for xml_element in ['<match ', 'feedtype']):
            data = self._create_match_subscribe_req(data)
        elif '<bookmatch ' in data and self._use_booked_match_ids:
            # Ignore match booking
            return None

        return data

    def _update_match_ids(self, data):
        regex = re.compile(self.MATCHLIST_ID_SEARCH_PATTERN)
        return regex.sub(self.MATCHLIST_ID_REPLACE_PATTERN.format(self._get_random_booked_match_id()), data)

    def _update_match_status(self, data):
        regex = re.compile(self.MATCHLIST_STATUS_SEARCH_PATTERN)
        return regex.sub(self.MATCHLIST_STATUS_REPLACE_PATTERN.format('NOT_STARTED'), data)

    def _create_matchlist_request(self):
        return '{}{}'.format(BetradarMessage().create_matchlist_request(), self._data_newline)

    def _create_match_subscribe_req(self, data):
        m = re.search(self.MATCH_ID_PATTERN, data)
        return '{}{}'.format(BetradarMessage().create_subscribe_delta_request(m.group('match_id'), self.SUBSCRIPTION_MESSAGE_DELAY, self.SUBSCRIPTION_START_MESSAGE), self._data_newline)

    def _get_random_booked_match_id(self):
        return self._booked_match_ids[int(len(self._booked_match_ids) * random.random())]
