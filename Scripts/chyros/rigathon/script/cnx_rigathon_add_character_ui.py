import maya.cmds as cmds

from cnx_rigathon_rig_control_name import RigControlName

from functools import partial
import os
import filecmp

class AddCharacterUI:

	_MAYA_ASCII_EXT = '.ma'
	_MAYA_BINARY_EXT = '.mb'

	_MAYA_ASCII_TYPE = 'mayaAscii'
	_MAYA_BINARY_TYPE = 'mayaBinary'

	def __init__(self, settings, util, matcher, animationUI, characters_location, window_name):
		self._settings = settings
		self._util = util
		self._matcher = matcher
		self._animationUI = animationUI
		self._characters_location = characters_location
		self._window_name = window_name

		self._available_characters = {}
		self._namespace = None
		self._character_path = None

	def show_window(self, *args):
		if cmds.window(self._window_name, exists=True):
			return

		self.update_available_characters()

		namespaces = list(self._available_characters.keys())
		namespaces.sort()

		window = cmds.window(self._window_name, title='[Rig-a-thon] Add Character for Animation', sizeable=False, toolbox=True)

		cmds.columnLayout(adjustableColumn=True)
		cmds.text(label=' Select a Character:', align='left', height=20)

		# Character list selection
		scrollList_character_selection = cmds.textScrollList(self._util.to_ui_name('scrollList_character_selection'), height=264)
		for namespace in namespaces:
			cmds.textScrollList(scrollList_character_selection, edit=True, append=(namespace))

		cmds.button('Add Character', command=partial(self.create_reference), height=30)
		cmds.setParent(upLevel=True)

		cmds.showWindow(window)
		self._util.perform_maya_2015_window_resize_workaround(window)

	def update_available_characters(self):
		self._available_characters = {}

		if not os.path.isdir(self._characters_location):
			return

		for character_file in os.listdir(self._characters_location):
			character_path = os.path.join(self._characters_location, character_file)

			if not os.path.isfile(character_path):
				continue

			if not os.path.splitext(character_path)[1] in [self._MAYA_ASCII_EXT, self._MAYA_BINARY_EXT]:
				continue

			namespace = self._util.to_proper_name(os.path.splitext(character_file)[0])
			self._available_characters[namespace] = character_path

	def update_selected_character(self):
		selected_items = cmds.textScrollList(self._util.to_ui_name('scrollList_character_selection'), query=True, selectItem=True)
		if selected_items is None or len(selected_items) == 0:
			return False

		self._namespace = selected_items[0]
		self._character_path = self._available_characters[self._namespace]

		return True

	def create_reference(self, *args):
		updated = self.update_selected_character()
		if not updated:
			return

		for reference in cmds.file(query=True, reference=True):
			if filecmp.cmp(reference, self._character_path):
				# Character already exists
				err_msg = 'Add character failed.\n\nCharacter name \'$character_name\' already exists.'.replace('$character_name', self._namespace)
				self._util.message_box('Add Character', err_msg)

				return

		file_type = self._get_file_type(os.path.splitext(self._character_path)[1])
		cmds.file(self._character_path, reference=True, type=file_type, groupLocator=True, namespace=self._namespace, options='v=0;p=17;f=0', loadReferenceDepth='all')

		character = self._animationUI.add_character(self._namespace)
		self._animationUI.activate_character(character.get_index())
		self._animationUI.show_window()
		self._util.update_editor_view()
		self._matcher.init_rig_defaults(self._namespace)

		# Close window
		cmds.deleteUI(self._window_name)

	def _get_file_type(self, file_ext):
		file_type = None

		if file_ext == self._MAYA_ASCII_EXT:
			file_type = self._MAYA_ASCII_TYPE
		elif file_ext == self._MAYA_BINARY_EXT:
			file_type = self._MAYA_BINARY_TYPE

		return file_type
