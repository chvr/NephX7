import maya.cmds as cmds

from cnx_rigathon_selection_sets import SelectionSets

from functools import partial

class SelectionSetsUI:

	def __init__(self, settings, util):
		self._settings = settings
		self._util = util
		self._selectionSets = SelectionSets(self._settings)

	def create_panel(self, panel_width):
		cmds.frameLayout(self._util.to_ui_name('frm_selection_sets'), label='Selection Sets', borderStyle='etchedOut', collapsable=True, collapse=True, enable=False, width=panel_width)

		self._init_selection_sets_ui()

		cmds.setParent(upLevel=True)

	def init_selection_sets(self):
		selection_set_names = None
		if cmds.objExists('selection_sets'):
			selection_set_names = cmds.listRelatives('selection_sets')

		self._selectionSets.clear()
		if selection_set_names is not None:
			# Load items from settings
			for selection_set_name in selection_set_names:
				name_value = self._settings.load('name', '', selection_set_name, 'selection_sets')
				objects_value = self._settings.load('objects', '', selection_set_name, 'selection_sets', as_list = True)

				self._selectionSets.add(name_value, objects_value)

		# Update UI
		self._update_selection_sets_ui()

	def get_selection_sets(self):
		return self._selectionSets

	def add_selection_set(self, *args):
		selected_objs = cmds.ls(selection=True)
		self._util.disable_undo()
		try:
			name = 'New Set '

			selection_set = self._selectionSets.add(name, [])
			name = selection_set.get_name() + str(selection_set.get_index() + 1).zfill(02)
			self.update_selection_set(selection_set.get_index(), '', 'name', name)

			cmds.evalDeferred(self._update_selection_sets_ui)
		finally:
			self._util.select_obj(selected_objs)
			self._util.enable_undo()

	def update_selection_set(self, idx, widget_name, attribute, value, *args):
		self._util.disable_undo()
		try:
			if attribute == 'name':
				self._selectionSets.update(idx, name = value)
				if cmds.textField(widget_name, query=True, exists=True):
					cmds.textField(widget_name, edit=True, text=value, annotation=value)
		finally:
			self._util.enable_undo()

	def delete_selection_set(self, idx, *args):
		selected_objs = cmds.ls(selection=True)
		self._util.disable_undo()
		try:
			self._selectionSets.remove(idx)
			cmds.evalDeferred(self._update_selection_sets_ui)
		finally:
			self._util.select_obj(selected_objs)
			self._util.enable_undo()

	def move_selection_set_up(self, idx, *args):
		self._util.disable_undo()
		try:
			moved = self._selectionSets.move_up(idx)
			if moved:
				cmds.evalDeferred(self._update_selection_sets_ui)
		finally:
			self._util.enable_undo()

	def move_selection_set_down(self, idx, *args):
		self._util.disable_undo()
		try:
			moved = self._selectionSets.move_down(idx)
			if moved:
				cmds.evalDeferred(self._update_selection_sets_ui)
		finally:
			self._util.enable_undo()

	def add_selected_objects_to_set(self, idx, widget_name, *args):
		self._util.disable_undo()
		try:
			selected_objects = cmds.ls(selection=True)
			added = self._selectionSets.get(idx).add_objects(selected_objects)
			if added:
				objects = self._selectionSets.get(idx).get_objects()
				if objects is None:
					objects = []
				self._selectionSets.update(idx, objects = objects)

				cmds.text(widget_name, edit=True, label=str(self._selectionSets.get(idx).get_size()))
		finally:
			self._util.enable_undo()

	def remove_selected_objects_from_set(self, idx, widget_name, *args):
		self._util.disable_undo()
		try:
			selected_objects = cmds.ls(selection=True)
			removed = self._selectionSets.get(idx).remove_objects(selected_objects)
			if removed:
				objects = self._selectionSets.get(idx).get_objects()
				if objects is None:
					objects = []
				self._selectionSets.update(idx, objects = objects)

				cmds.text(widget_name, edit=True, label=str(self._selectionSets.get(idx).get_size()))
		finally:
			self._util.enable_undo()

	def empty_objects_from_set(self, idx, widget_name, *args):
		self._util.disable_undo()
		try:
			emptied = self._selectionSets.get(idx).clear_objects()
			if emptied:
				objects = self._selectionSets.get(idx).get_objects()
				if objects is None:
					objects = []
				self._selectionSets.update(idx, objects = objects)

				cmds.text(widget_name, edit=True, label=str(self._selectionSets.get(idx).get_size()))
		finally:
			self._util.enable_undo()

	def select_objects_from_set(self, idx, *args):
		selection_objects = self._selectionSets.get(idx).get_objects()
		self._util.select_obj(selection_objects)

	def _init_selection_sets_ui(self):
		cmds.columnLayout(self._util.to_ui_name('col_selection_sets'), adjustableColumn=True)
		cmds.setParent(upLevel=True)

	def _update_selection_sets_ui(self):
		col1_width = 10
		col2_width = 12
		col3_width = 18
		col6_width = 10
		col7_width = 10

		# Delete existing UI elements
		child_elements = cmds.columnLayout(self._util.to_ui_name('col_selection_sets'), query=True, childArray=True)
		if child_elements is not None:
			for element in child_elements:
				cmds.deleteUI(element)

		# Create new UI elements
		cmds.columnLayout(self._util.to_ui_name('col_selection_sets'), edit=True)

		cmds.rowLayout(parent=self._util.to_ui_name('col_selection_sets'), numberOfColumns=6, adjustableColumn=4)
		cmds.separator(style='none', width=col1_width)
		cmds.separator(style='none', width=col2_width)
		cmds.separator(style='none', width=col3_width)
		cmds.text(label='Set', font='boldLabelFont', align='left')
		cmds.text(label='', font='boldLabelFont', align='left')
		cmds.text(' Sort', font='boldLabelFont', align='left')
		cmds.setParent(upLevel=True)

		for index in range(0, self._selectionSets.get_size()):
			cmds.rowLayout(parent=self._util.to_ui_name('col_selection_sets'), numberOfColumns=7, adjustableColumn=4)
			if index == -1:
				cmds.separator(style='none', width=col1_width)
			else:
				# Close button
				cmds.iconTextButton(label='x', style='textOnly', font='boldLabelFont', command=partial(self.delete_selection_set, index), width=col1_width)

			txt_object_count_name = self._util.to_ui_name('txt_selection_set_object_count' + str(index))
			txtField_selection_set_name = self._util.to_ui_name('txtField_selection_set_name' + str(index))

			selection_set_name_value = self._selectionSets.get(index).get_name()

			cmds.text(txt_object_count_name, label=str(self._selectionSets.get(index).get_size()), annotation='Object count', width=col2_width)
			selection_set_btn = cmds.button(label='S', annotation='Selection Set Menu...', width=col3_width)
			cmds.textField(txtField_selection_set_name, text=selection_set_name_value, annotation=selection_set_name_value, changeCommand=partial(self.update_selection_set, index, txtField_selection_set_name, 'name'))
			cmds.button(label='Select', command=partial(self.select_objects_from_set, index))
			cmds.iconTextButton(label='^', style='textOnly', font='boldLabelFont', command=partial(self.move_selection_set_up, index), width=col6_width)
			cmds.iconTextButton(label='v', style='textOnly', font='boldLabelFont', command=partial(self.move_selection_set_down, index), width=col7_width)
			cmds.setParent(upLevel=True)

			# Context menu
			cmds.popupMenu(parent=selection_set_btn, button=1)
			cmds.menuItem(label='Add Selected Objects', command=partial(self.add_selected_objects_to_set, index, txt_object_count_name))
			cmds.menuItem(label='Remove Selected Objects', command=partial(self.remove_selected_objects_from_set, index, txt_object_count_name))
			cmds.menuItem(divider=True)
			cmds.menuItem(label='Empty the Set', command=partial(self.empty_objects_from_set, index, txt_object_count_name))

		cmds.rowLayout(parent=self._util.to_ui_name('col_selection_sets'), numberOfColumns=2)
		cmds.separator(style='none', width=col1_width)
		cmds.button(label=' New ', command=partial(self.add_selection_set))
		cmds.setParent(upLevel=True)
