__author__ = 'arifal'


class Channel:

    def __init__(self, name, port):
        self._name = name
        self._port = port

    @property
    def get_name(self):
        return self._name

    @property
    def get_port(self):
        return self._port
