class Character:

	def __init__(self, namespace, active):
		self._namespace = namespace
		self._active = active

		self._index = 0

	def get_namespace(self):
		return self._namespace

	def set_namespace(self, namespace):
		self._namespace = namespace

	def is_active(self):
		return self._active

	def set_active(self, active):
		self._active = active

	def get_index(self):
		return self._index

	def set_index(self, index):
		self._index = index
