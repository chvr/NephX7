import maya.cmds as cmds

class RigControl:

	# Colors
	_YELLOW_COLOR = 'yellow'
	_BLUE_COLOR = 'blue'
	_GREEN_COLOR = 'green'
	_PURPLE_COLOR = 'purple'
	_RED_COLOR = 'red'

	# Control color definitions
	_yellow_control_unselected = [0.9, 0.9, 0.3]
	_yellow_control_selected = [1.0, 1.0, 0.8]

	_blue_control_unselected = [0.4, 0.5, 0.7]
	_blue_control_selected = [0.8, 0.8, 1.0]

	_green_control_unselected = [0.4, 0.7, 0.5]
	_green_control_selected = [0.8, 1.0, 0.8]

	_purple_control_unselected = [0.8, 0.6, 0.8]
	_purple_control_selected = [1.0, 0.8, 1.0]

	_red_control_unselected = [0.9, 0.3, 0.3]
	_red_control_selected = [1.0, 0.6, 0.6]

	def __init__(self, util, key, ctrl_name, type, color, desc):
		self._util = util
		self._key = key
		self._ctrl_name = ctrl_name
		self._type = type
		self._color = color
		self._desc = desc

		self._pickers = []
		self.create_picker()

	def get_key(self):
		return self._key

	def get_ctrl_name(self):
		return self._util.to_node_name(self._ctrl_name)

	def get_type(self):
		return self._type

	def get_desc(self):
		return self._desc

	def get_pickers(self):
		return self._pickers

	def create_picker(self):
		picker_name = self._util.to_ui_name('picker_' + self._key)

		num = 1
		while (picker_name + str(num) in self._pickers):
			num += 1

		picker_name = picker_name + str(num)
		self._pickers.append(picker_name)

		return picker_name

	def get_color(self, selected_objs = None):
		if self._color == self._YELLOW_COLOR:
			return self._yellow_control_selected if self.is_selected(selected_objs) else self._yellow_control_unselected
		elif self._color == self._BLUE_COLOR:
			return self._blue_control_selected if self.is_selected(selected_objs) else self._blue_control_unselected
		elif self._color == self._GREEN_COLOR:
			return self._green_control_selected if self.is_selected(selected_objs) else self._green_control_unselected
		elif self._color == self._PURPLE_COLOR:
			return self._purple_control_selected if self.is_selected(selected_objs) else self._purple_control_unselected
		elif self._color == self._RED_COLOR:
			return self._red_control_selected if self.is_selected(selected_objs) else self._red_control_unselected
		else:
			raise Exception('Undefined control color: ' + self._type)

	def update_color(self, selected_objs):
		for picker in self.get_pickers():
			if cmds.button(picker, exists=True):
				cmds.button(picker, edit=True, backgroundColor=self.get_color(selected_objs))

	def is_selected(self, selected_objs):
		if selected_objs is None:
			return False

		return self.get_ctrl_name() in selected_objs
