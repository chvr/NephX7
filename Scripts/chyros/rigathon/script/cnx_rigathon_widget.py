import maya.cmds as cmds

from cnx_rigathon_logger import Logger

class Widget:

	def __init__(self, util, key, type, attribute_name, attribute_type, value_id):
		self._logger = Logger(self.__class__.__name__)
		self._util = util
		self._key = key
		self._type = type
		self._attribute_name = attribute_name
		self._attribute_type = attribute_type
		self._value_id = value_id

		self._names = []

	def create_new_name(self):
		# Create widget name
		name = self._create_widget_name()
		index = 0
		while name in self._names:
			index += 1
			name = self._create_widget_name() + str(index)

		self._names.append(name)

		return name

	def use_settings(self, settings):
		self._settings = settings

	def get_key(self):
		return self._key

	def get_type(self):
		return self._type

	def get_attribute_name(self):
		return self.attribute_name

	def get_attribute_type(self):
		return self.attribute_type

	def get_names(self):
		return self._names

	def get_value(self, default_value = None):
		value = default_value

		# Retrieve control's value
		if self._attribute_type == 'attribute':
			object_name = self._util.to_node_name(self._attribute_name.rpartition('.')[0])
			if cmds.objExists(object_name):
				attribute_name = self._util.to_node_name(self._attribute_name)
				value = cmds.getAttr(attribute_name)
		elif self._attribute_type == 'settings':
			value = self._settings.load(self._attribute_name, default_value)
		else:
			raise Exception('Unknown attribute type ' + str(self._attribute_type))

		return value

	def set_value(self, value):
		# Update control's value
		if self._attribute_type == 'attribute':
			attr_name = self._util.to_node_name(self._attribute_name)
			obj_name = attr_name.rpartition('.')[0]
			if not cmds.objExists(obj_name):
				self._logger.warn('Rig control \'$rig_control\' not found.'.replace('$rig_control', obj_name))
				self._logger.command_message('Warn: Rig control not found. See Script Editor for details.')
				return False

			cmds.setAttr(self._util.to_node_name(self._attribute_name), value)
		elif self._attribute_type == 'settings':
			self._settings.save(self._attribute_name, value)
		else:
			raise Exception('Unknown attribute type ' + str(self._attribute_type))

		# Update display control's value
		self.update_display_value()

		return True

	def update_display_value(self, default_value = None):
		value = self.get_value(default_value)

		for name in self._names:
			# Update display control's value
			if self._type == 'menuItem_radioButton':
				cmds.menuItem(name, edit=True, radioButton=(self._value_id == value))
			elif self._type == 'optionMenu':
				# Verify if the value exists in the options
				options = []
				for menu_item_name in cmds.optionMenu(name, query=True, itemListLong=True):
					options.append(cmds.menuItem(menu_item_name, query=True, label=True))

				if value not in options:
					if default_value in options:
						value = default_value
					else:
						return

				cmds.optionMenu(name, edit=True, value=value)
			else:
				raise Exception('Unknown widget type ' + self._type)

	def _create_widget_name(self):
		return self._util.to_ui_name('$type_$key' \
			.replace('$type', self._type) \
			.replace('$key', self._key) \
			)
