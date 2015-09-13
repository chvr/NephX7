import maya.cmds as cmds

from cnx_rigathon_logger import Logger

import threading
import os
import subprocess
import imp
import traceback

class Util:

	_CHAR_INDENT = '\t'

	_lock = threading.RLock()

	def __init__(self, settings, data_location, script_location, generated_script_location):
		self._logger = Logger(self.__class__.__name__)
		self._settings = settings
		self._data_location = data_location
		self._script_location = script_location
		self._generated_script_location = generated_script_location

		self._disable_undo_counter = 0

	def generate_script(self, filename):
		parser_path = os.path.join(self._script_location, 'cnx_rigathon_parser.py')
		data_path = os.path.join(self._data_location, filename + '.txt')
		generated_script_path = os.path.join(self._generated_script_location, filename + '.py')

		command = '$PARSER_PATH -s $DATA_PATH -o $GENERATED_SCRIPT_PATH' \
			.replace('$PARSER_PATH', parser_path) \
			.replace('$DATA_PATH', data_path) \
			.replace('$GENERATED_SCRIPT_PATH', generated_script_path)

		self._logger.info('# Generate rigathon script file: ' + generated_script_path + ' ...')
		try:
			self.disable_undo()

			if not os.path.isdir(self._generated_script_location):
				# Create directory
				os.makedirs(self._generated_script_location)

			stdout = subprocess.check_output('mayapy ' + command, shell=True)
			self._logger.log(stdout)
		except:
			self._logger.error(self._CHAR_INDENT + '* Failed generating rigathon script.')

			# Format exception
			lines = traceback.format_exc().splitlines()
			for line in lines:
				self._logger.error(self._CHAR_INDENT + self._CHAR_INDENT + '# ' + line)
		finally:
			self.enable_undo()

	def exec_generated_script(self, script_name):
		script_path = os.path.join(self._generated_script_location, script_name + '.py')

		self._logger.info('# Executing rigathon script file: ' + script_path + ' ...')
		try:
			self.disable_undo()

			imp.load_source('rigathon_script', script_path)
			self._logger.info(self._CHAR_INDENT + '* DONE!')
		except:
			self._logger.error(self._CHAR_INDENT + '* Failed executing rigathon script.')

			# Format exception
			lines = traceback.format_exc().splitlines()
			for line in lines:
				self._logger.error(self._CHAR_INDENT + self._CHAR_INDENT + '# ' + line)
		finally:
			self.enable_undo()

	def disable_undo(self):
		with self._lock:
			self._disable_undo_counter += 1
			cmds.undoInfo(stateWithoutFlush=False)

	def enable_undo(self):
		with self._lock:
			self._disable_undo_counter -= 1
			if self._disable_undo_counter == 0:
				cmds.undoInfo(stateWithoutFlush=True)

	def select_obj(self, objs, toggle = False, replace = False):
		if type(objs) is list:
			found_objs = []
			missing = False

			for obj in objs:
				if cmds.objExists(obj):
					found_objs.append(obj)
				else:
					self._logger.warn('Rig control \'$rig_control\' not found.'.replace('$rig_control', obj))
					missing = True

			if len(found_objs) > 0:
				if found_objs != cmds.ls(selection=True):
					cmds.select(found_objs, toggle=toggle, replace=replace)
			else:
				cmds.select(clear=True)

			if missing:
				self._logger.command_message('Warn: Some rig controls were not found. See Script Editor for details.')
		else:
			if cmds.objExists(objs):
				cmds.select(objs, toggle=toggle, replace=replace)
			else:
				self._logger.warn('Rig control \'$rig_control\' not found.'.replace('$rig_control', objs))
				self._logger.command_message('Warn: Rig control not found. See Script Editor for details.')

	def message_box(self, title, message, *args):
		message = (''.ljust(7) + '\n').join(message.split('\n')) + ''.ljust(7)
		cmds.confirmDialog(title=title, message=message, button='OK')

	def custom_message_box(self, title, message, buttons, default_button, cancel_button):
		message = (''.ljust(7) + '\n').join(message.split('\n')) + ''.ljust(7)
		return cmds.confirmDialog(title=title, message=message, button=buttons, defaultButton=default_button, cancelButton=cancel_button, dismissString=cancel_button)

	def dialog_box_ok_cancel(self, title, message, value = '', *args):
		dlg_result = cmds.promptDialog(title=title, message=message, text=value, button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
		if dlg_result == 'OK':
			return cmds.promptDialog(query=True, text=True)
		else:
			return None

	def dialog_box_yes_no(self, title, message, text = '', default_button = 'Yes', *args):
		dlg_result = cmds.confirmDialog(title=title, message=message, button=['Yes', 'No'], defaultButton=default_button, cancelButton='No', dismissString='No')
		return dlg_result == 'Yes'

	def save_to_cache(self, name, value):
		self.disable_undo()
		try:
			section = 'cache'
			self._settings.save(name, value, section = section)
		finally:
			self.enable_undo()

	def load_from_cache(self, name, default_value = None):
		self.disable_undo()
		try:
			section = 'cache'
			return self._settings.load(name, default_value, section = section)
		finally:
			self.enable_undo()

	def to_matcher_category(self):
		return 'matchers'

	def to_matcher_name(self, character_name):
		return 'matcher_' + character_name

	def to_ui_name(self, name):
		return 'cnx_' + name

	def to_node_name(self, name):
		ref_name = self._settings.get_ref_name()
		if len(ref_name) > 0:
			ref_name += ':'

		return ref_name + name

	def to_proper_name(self, name):
		proper_name = ''

		for c in name:
			proper_name += c if c.isalnum() else '_'

		return proper_name

	def update_editor_view(self):
		cmds.viewFit()

		panels = cmds.getPanel(type='modelPanel')
		for panel in panels:
			modelEditor = cmds.modelPanel(panel, query=True, modelEditor=True)
			cmds.modelEditor(modelEditor, edit=True, displayAppearance='smoothShaded', displayTextures=True, textures=True, joints=False)

	def perform_maya_2015_window_resize_workaround(self, window_name):
		cmds.window(window_name, edit=True, resizeToFitChildren=True, widthHeight=(1, 1))
