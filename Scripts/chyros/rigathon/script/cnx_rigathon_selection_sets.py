import maya.cmds as cmds

from cnx_rigathon_selection_set import SelectionSet

class SelectionSets:

	def __init__(self, settings):
		self._settings = settings

		self._selection_sets = []

	def get(self, idx):
		return self._selection_sets[idx]

	def get_list(self):
		return self._selection_sets

	def get_size(self):
		return len(self._selection_sets)

	def clear(self):
		del self._selection_sets[:]

	def add(self, name, objects):
		selection_set = SelectionSet(name, objects)
		self._selection_sets.append(selection_set)

		self._update_indices()

		return selection_set

	def update(self, idx, name = None, objects = None):
		if name is not None:
			self.get(idx).set_name(name)
			self._settings.save('name', name, 'selection_set' + str(idx), 'selection_sets')

		if objects is not None:
			self.get(idx).set_objects(objects)
			self._settings.save('objects', objects, 'selection_set' + str(idx), 'selection_sets')

	def remove(self, idx):
		selection_set_names = None
		if cmds.objExists('selection_sets'):
			selection_set_names = cmds.listRelatives('selection_sets')

		if selection_set_names is not None:
			for selection_set_name in selection_set_names:
				# Delete existing anim range nodes
				self._settings.delete_node(selection_set_name, 'selection_sets')

		deleted = False
		for selection_set in self._selection_sets:
			if selection_set.get_index() == idx:
				self._selection_sets.remove(selection_set)
				deleted = True
				break

		self._update_indices()

		return deleted

	def move_up(self, idx):
		if self.get_size() < 2:
			return False

		selection_set_a = self._selection_sets[idx - 1]
		selection_set_b = self._selection_sets[idx]

		if selection_set_a is not None and selection_set_b is not None:
			self._swap(selection_set_a, selection_set_b)
			self._update_indices()
			return True

		return False

	def move_down(self, idx):
		if self.get_size() < 2:
			return False

		selection_set_a = self._selection_sets[idx]
		if self.get_size() > 1 and selection_set_a == self._selection_sets[-1]:
			# First item
			selection_set_b = self._selection_sets[0]
		else:
			# Next item
			selection_set_b = self._selection_sets[idx + 1]

		if selection_set_a is not None and selection_set_b is not None:
			self._swap(selection_set_a, selection_set_b)
			self._update_indices()
			return True

		return False

	def _update_indices(self):
		counter = 0

		for selection_set in self._selection_sets:
			selection_set.set_index(counter)

			self._settings.save('name', selection_set.get_name(), 'selection_set' + str(selection_set.get_index()), 'selection_sets')
			self._settings.save('objects', selection_set.get_objects(), 'selection_set' + str(selection_set.get_index()), 'selection_sets')

			counter += 1

	def _swap(self, selection_set_a, selection_set_b):
		tmp = SelectionSet('', [])
		tmp.set_name(selection_set_a.get_name())
		tmp.set_objects(selection_set_a.get_objects())

		selection_set_a.set_name(selection_set_b.get_name())
		selection_set_a.set_objects(selection_set_b.get_objects())

		selection_set_b.set_name(tmp.get_name())
		selection_set_b.set_objects(tmp.get_objects())
