import maya.cmds as cmds

from cnx_rigathon_characters import Characters

from functools import partial

class CharactersUI:

	def __init__(self, parent_ui, settings, util):
		self._parent_ui = parent_ui
		self._settings = settings
		self._util = util
		self._characters = Characters(self._settings)

	def create_panel(self, panel_width):
		cmds.frameLayout(self._util.to_ui_name('frm_characters'), label='Characters', borderStyle='etchedOut', collapsable=True, collapse=True, collapseCommand=partial(self._panel_collapsed), expandCommand=partial(self._panel_expanded), enable=True, width=panel_width)

		self._init_characters_ui()

		cmds.setParent(upLevel=True)

	def init_characters(self):
		character_namespaces = None
		if cmds.objExists('characters'):
			character_namespaces = cmds.listRelatives('characters')

		self._characters.clear()
		if character_namespaces is not None:
			# Load items from settings
			for character_namespace in character_namespaces:
				namespace_value = self._settings.load('namespace', '', character_namespace, 'characters')
				objects_value = self._settings.load('objects', '', character_namespace, 'characters', as_list = True)
				active_value = self._settings.load('active', True, character_namespace, 'characters')

				self._characters.add(namespace_value, active_value)

		# Apply selected reference
		self.apply_selected_ref_name()

		# Update UI
		self._update_characters_ui()

		# Update panel view
		is_panel_collapsed = self._settings.load('characters_panel_collapsed', True)
		cmds.frameLayout(self._util.to_ui_name('frm_characters'), edit=True, collapse=is_panel_collapsed, collapseCommand=partial(self._panel_collapsed), expandCommand=partial(self._panel_expanded), enable=True)

	def get_characters(self):
		return self._characters

	def add_character(self, namespace, *args):
		selected_objs = cmds.ls(selection=True)
		self._util.disable_undo()
		try:
			active = False
			character = self._characters.add(namespace, active)

			cmds.evalDeferred(self._update_characters_ui)

			return character
		finally:
			self._util.select_obj(selected_objs)
			self._util.enable_undo()

	def update_character(self, idx, widget_name, attribute, value, *args):
		self._util.disable_undo()
		try:
			reapply_ref_name = False

			if attribute == 'namespace':
				value = self._util.to_proper_name(value)
				self._characters.update(idx, namespace = value)
				if cmds.textField(widget_name, query=True, exists=True):
					cmds.textField(widget_name, edit=True, text=value, annotation=value)

				if self._characters.get(idx).is_active():
					reapply_ref_name = True

			elif attribute == 'active':
				# Only check single checkbox. Uncheck the reest.
				for row_layout in cmds.columnLayout(self._util.to_ui_name('col_characters'), query=True, childArray=True):
					for child_obj in cmds.rowLayout(row_layout, query=True, childArray=True):
						if not cmds.checkBox(child_obj, query=True, exists=True):
							continue

						is_active = False
						if widget_name == child_obj:
							is_active = value

						cmds.checkBox(child_obj, edit=True, value=is_active)

				self._characters.update(idx, active = value)

				reapply_ref_name = True

			if reapply_ref_name:
				# Re-apply ref name
				self.apply_selected_ref_name()

		finally:
			self._util.enable_undo()

	def delete_character(self, idx, *args):
		selected_objs = cmds.ls(selection=True)
		self._util.disable_undo()
		try:
			reapply_ref_name = False
			if self._characters.get(idx).is_active():
				reapply_ref_name = True

			self._characters.remove(idx)
			cmds.evalDeferred(self._update_characters_ui)

			if reapply_ref_name:
				# Re-apply ref name
				self.apply_selected_ref_name()
		finally:
			self._util.select_obj(selected_objs)
			self._util.enable_undo()

	def move_character_up(self, idx, *args):
		self._util.disable_undo()
		try:
			moved = self._characters.move_up(idx)
			if moved:
				cmds.evalDeferred(self._update_characters_ui)
		finally:
			self._util.enable_undo()

	def move_character_down(self, idx, *args):
		self._util.disable_undo()
		try:
			moved = self._characters.move_down(idx)
			if moved:
				cmds.evalDeferred(self._update_characters_ui)
		finally:
			self._util.enable_undo()

	def activate_character(self, idx):
		self._util.disable_undo()
		try:
			self._characters.update(idx, active = True)
			self.apply_selected_ref_name()
		finally:
			self._util.enable_undo()

	def apply_selected_ref_name(self):
		self._util.disable_undo()
		try:
			# Reset ref name
			self._settings.reset_ref_name()

			for character in self._characters.get_list():
				if character.is_active():
					self._settings.set_ref_name(character.get_namespace())
					break

			# Refresh UI widgets
			self._parent_ui.refresh_widget_values()

			# Refresh selection
			selected_objs = cmds.ls(selection=True)

			# Switch character selection
			new_selection = []
			for obj in selected_objs:
				new_obj = self._util.to_node_name(obj.rpartition(':')[2])
				if cmds.objExists(new_obj):
					new_selection.append(new_obj)
				else:
					new_selection.append(obj)

			if len(new_selection) > 0:
				cmds.select(new_selection)
		finally:
			self._util.enable_undo()

	def _init_characters_ui(self):
		cmds.columnLayout(self._util.to_ui_name('col_characters'), adjustableColumn=True)
		cmds.setParent(upLevel=True)

	def _update_characters_ui(self):
		col1_width = 10
		col3_width = 12
		col4_width = 10
		col5_width = 10

		# Delete existing UI elements
		child_elements = cmds.columnLayout(self._util.to_ui_name('col_characters'), query=True, childArray=True)
		if child_elements is not None:
			for element in child_elements:
				cmds.deleteUI(element)

		# Create new UI elements
		cmds.columnLayout(self._util.to_ui_name('col_characters'), edit=True)

		cmds.rowLayout(parent=self._util.to_ui_name('col_characters'), numberOfColumns=4, adjustableColumn=2)
		cmds.separator(style='none', width=col1_width)
		cmds.text(label='Namespace', font='boldLabelFont', align='left')
		cmds.text(label='', font='boldLabelFont', align='left')
		cmds.text(label=' Sort', font='boldLabelFont', align='left')
		cmds.setParent(upLevel=True)

		for index in range(0, self._characters.get_size()):
			cmds.rowLayout(parent=self._util.to_ui_name('col_characters'), numberOfColumns=5, adjustableColumn=2)
			# Close button
			cmds.iconTextButton(label='x', style='textOnly', font='boldLabelFont', command=partial(self.delete_character, index), width=col1_width)

			txtField_namespace_name = self._util.to_ui_name('txtField_character_namespace_name' + str(index))
			chk_active_name = self._util.to_ui_name('chk_character_active_name' + str(index))

			namespace_value = self._characters.get(index).get_namespace()
			active_value = self._characters.get(index).is_active()

			cmds.textField(txtField_namespace_name, text=namespace_value, annotation=namespace_value, changeCommand=partial(self.update_character, index, txtField_namespace_name, 'namespace'))
			cmds.checkBox(chk_active_name, value=active_value, label='', changeCommand=partial(self.update_character, index, chk_active_name, 'active'))
			cmds.iconTextButton(label='^', style='textOnly', font='boldLabelFont', command=partial(self.move_character_up, index), width=col4_width)
			cmds.iconTextButton(label='v', style='textOnly', font='boldLabelFont', command=partial(self.move_character_down, index), width=col5_width)
			cmds.setParent(upLevel=True)

		cmds.rowLayout(parent=self._util.to_ui_name('col_characters'), numberOfColumns=2, adjustableColumn=3)
		cmds.separator(style='none', width=col1_width)
		cmds.button(label=' New ', command=partial(self.add_character, ''))
		cmds.setParent(upLevel=True)

	def _panel_collapsed(self, *args):
		self._settings.save('characters_panel_collapsed', True)

	def _panel_expanded(self, *args):
		self._settings.save('characters_panel_collapsed', False)
