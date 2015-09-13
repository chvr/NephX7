import maya.mel as mel

class Logger:

	_INFO = 'INFO '
	_WARN = 'WARN '
	_ERROR = 'ERROR'
	_DEBUG = 'DEBUG'

	def __init__(self, name):
		self._name = name

	def command_message(self, message):
		message = message.replace('\\', '\\\\')
		mel.eval('print "$message\\n"'.replace('$message', str(message)))

	def command_result(self, message):
		message = str(message).replace('\\', '\\\\')
		mel.eval('print "// Result: $message\\n"'.replace('$message', str(message)))

	def info(self, message):
		self._log(self._INFO, message)

	def warn(self, message):
		self._log(self._WARN, message)

	def error(self, message):
		self._log(self._ERROR, message)

	def debug(self, message):
		self._log(self._DEBUG, message)

	def log(self, message):
		print(message),

	def _log(self, type, message):
		print('[$type] Rigathon.$name | $message') \
			.replace('$name', self._name.ljust(10)) \
			.replace('$type', type) \
			.replace('$message', message)
