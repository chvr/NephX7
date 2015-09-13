class SelectionSet:

	def __init__(self, name, objects):
		self._name = name
		self._objects = objects

		self._index = 0

	def get_name(self):
		return self._name

	def set_name(self, name):
		self._name = name

	def get_objects(self):
		return self._objects

	def set_objects(self, objects):
		self._objects = objects

	def add_objects(self, objects):
		added = False
		for obj in objects:
			if obj not in self._objects:
				self._objects.append(obj)
				added = True

		return added

	def remove_objects(self, objects):
		removed = False
		for obj in objects:
			if obj in self._objects:
				self._objects.remove(obj)
				removed = True

		return removed

	def clear_objects(self):
		if self.get_size() > 0:
			del self._objects[:]
			return True

		return False

	def get_size(self):
		return len(self._objects)

	def get_index(self):
		return self._index

	def set_index(self, index):
		self._index = index
