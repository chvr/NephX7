__author__ = 'arifal'


import logging

from datetime import datetime


class Logger:

    def __init__(self, name):
        self._name = name

    def info(self, message):
        formatted_msg = self._format(message)
        print(message)
        logging.info(message)

    def warn(self, message):
        formatted_msg = self._format(message)
        print(message)
        logging.warning(message)

    def error(self, message):
        formatted_msg = self._format(message)
        print(message)
        logging.error(message)

    def _format(self, msg_type, msg):
        return '{} [{}] {} | {}'.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], self._name, msg)

    def _write_to_file(self, msg):
        with open('{}.log'.format(__file__), 'a') as f:
            f.write(msg)
            f.flush()
