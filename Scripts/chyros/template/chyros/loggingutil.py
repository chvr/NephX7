import logging
import sys

__author__ = 'ChyrosNX'


def create(log_file=None, log_level=logging.INFO, log_format=None):
    if log_format is None:
        log_format = '%(asctime)s - %(levelname)s | %(message)s'

    root = logging.getLogger()
    root.setLevel(log_level)

    if log_file is not None:
        logging.basicConfig(filename=log_file, level=log_level, format=log_format)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(log_format))
        root.addHandler(console_handler)
    else:
        logging.basicConfig(level=log_level, format=log_format)
