__author__ = 'arifal'


import logging


class UserCommand:

    _DELIMITER = '\n'

    def __init__(self, owner, sock):
        self._owner = owner
        self._sock = sock
        self._stop = False

    def start(self):
        command_buffer = ''
        while not self._stop:
            command_buffer += self._sock.receive() or ''
            commands, command_buffer = self._parse(command_buffer)

            self._process(commands)

    def stop(self):
        self._stop = True
        if self._sock is not None:
            self._sock.disconnect()

    def _parse(self, command_buffer):
        if self._DELIMITER not in command_buffer:
            return [], command_buffer

        command_list = command_buffer.replace('\r', '').split(self._DELIMITER)
        incomplete_command = self._DELIMITER.join(command_list[-1:])
        commands = command_list[:-1]

        return commands, incomplete_command

    def _process(self, commands):
        for command in commands:
            if command.lower() in ['exit', 'quit', 'logout', 'e', 'x', 'q']:
                logging.info('# Exit command received from user.')
                self._owner.stop()
                return
            elif command.lower() in ['help', 'h', '?']:
                logging.info('# Type \'exit\' to stop.')
            else:
                logging.info('# Unknown command \'{}\' received from user.'.format(command))
