class AnimSequence:

	def __init__(self, name, start, end, active):
		self._name = name
		self._start = start
		self._end = end
		self._active = active

		self._index = 0

	def get_name(self):
		return self._name

	def set_name(self, name):
		self._name = name

	def get_start(self):
		return self._start

	def set_start(self, start):
		self._start = start

	def get_end(self):
		return self._end

	def set_end(self, end):
		self._end = end

	def is_active(self):
		return self._active

	def set_active(self, active):
		self._active = active

	def get_index(self):
		return self._index

	def set_index(self, index):
		self._index = index
