import maya.cmds as cmds

from cnx_rigathon_export_layer import ExportLayer

class ExportLayers:

	def __init__(self, settings):
		self._settings = settings

		self._export_layers = []

	def get(self, idx):
		return self._export_layers[idx]

	def get_list(self):
		return self._export_layers

	def get_size(self):
		return len(self._export_layers)

	def clear(self):
		del self._export_layers[:]

	def add(self, name, objects, active):
		export_layer = ExportLayer(name, objects, active)
		self._export_layers.append(export_layer)

		self._update_indices()

		return export_layer

	def update(self, idx, name = None, objects = None, active = None):
		if name is not None:
			self.get(idx).set_name(name)
			self._settings.save('name', name, 'export_layer' + str(idx), 'export_layers')

		if objects is not None:
			self.get(idx).set_objects(objects)
			self._settings.save('objects', objects, 'export_layer' + str(idx), 'export_layers')

		if active is not None:
			self.get(idx).set_active(active)
			self._settings.save('active', active, 'export_layer' + str(idx), 'export_layers')

	def remove(self, idx):
		export_layer_names = None
		if cmds.objExists('export_layers'):
			export_layer_names = cmds.listRelatives('export_layers')

		if export_layer_names is not None:
			for export_layer_name in export_layer_names:
				# Delete existing anim range nodes
				self._settings.delete_node(export_layer_name, 'export_layers')

		deleted = False
		for export_layer in self._export_layers:
			if export_layer.get_index() == idx:
				self._export_layers.remove(export_layer)
				deleted = True
				break

		self._update_indices()

		return deleted

	def move_up(self, idx):
		if self.get_size() < 2:
			return False

		export_layer_a = self._export_layers[idx - 1]
		export_layer_b = self._export_layers[idx]

		if export_layer_a is not None and export_layer_b is not None:
			self._swap(export_layer_a, export_layer_b)
			self._update_indices()
			return True

		return False

	def move_down(self, idx):
		if self.get_size() < 2:
			return False

		export_layer_a = self._export_layers[idx]
		if self.get_size() > 1 and export_layer_a == self._export_layers[-1]:
			# First item
			export_layer_b = self._export_layers[0]
		else:
			# Next item
			export_layer_b = self._export_layers[idx + 1]

		if export_layer_a is not None and export_layer_b is not None:
			self._swap(export_layer_a, export_layer_b)
			self._update_indices()
			return True

		return False

	def _update_indices(self):
		counter = 0

		for export_layer in self._export_layers:
			export_layer.set_index(counter)

			self._settings.save('name', export_layer.get_name(), 'export_layer' + str(export_layer.get_index()), 'export_layers')
			self._settings.save('objects', export_layer.get_objects(), 'export_layer' + str(export_layer.get_index()), 'export_layers')
			self._settings.save('active', export_layer.is_active(), 'export_layer' + str(export_layer.get_index()), 'export_layers')

			counter += 1

	def _swap(self, export_layer_a, export_layer_b):
		tmp = ExportLayer('', [], True)
		tmp.set_name(export_layer_a.get_name())
		tmp.set_objects(export_layer_a.get_objects())
		tmp.set_active(export_layer_a.is_active())

		export_layer_a.set_name(export_layer_b.get_name())
		export_layer_a.set_objects(export_layer_b.get_objects())
		export_layer_a.set_active(export_layer_b.is_active())

		export_layer_b.set_name(tmp.get_name())
		export_layer_b.set_objects(tmp.get_objects())
		export_layer_b.set_active(tmp.is_active())
