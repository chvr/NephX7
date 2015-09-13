import maya.cmds as cmds

from cnx_rigathon_logger import Logger
from cnx_rigathon_util import Util
from cnx_rigathon_skeleton_definition import SkeletonDefinition

from functools import partial
import os

class RigACharacterUI:

	# Base widget sizes
	_SIZE_WIDGET_WIDTH = 100
	_SIZE_WIDGET_HEIGHT = 30

	def __init__(self, util, characters_location, window_name):
		self._logger = Logger(self.__class__.__name__)
		self._util = util
		self._skeleton_definition = SkeletonDefinition()
		self._characters_location = characters_location
		self._window_name = window_name

	def show_window(self):
		if cmds.window(self._window_name, exists=True):
			return

		window = cmds.window(self._window_name, title='[Rig-a-thon] Rig a Character', iconName='Rig a Character', sizeable=False, toolbox=True)
		self._create_ui_panel()
		cmds.showWindow(window)
		self._util.perform_maya_2015_window_resize_workaround(self._window_name)

	def run_script_generate_skeleton(self, *args):
		title = 'Generate Skeleton'
		message = 'Select Skeleton Pose: T-Pose or Relaxed Pose?'
		buttons = ['T-Pose', 'Relaxed Pose', 'Cancel']

		result = self._util.custom_message_box(title, message, buttons, buttons[0], buttons[2])

		if result == 'T-Pose':
			self._util.generate_script('01_skeleton_definition_t_pose')
			self._util.exec_generated_script('01_skeleton_definition_t_pose')
		elif result == 'Relaxed Pose':
			self._util.generate_script('01_skeleton_definition_relaxed_pose')
			self._util.exec_generated_script('01_skeleton_definition_relaxed_pose')

	def run_script_add_skin_weight_influence(self, *args):
		self._util.generate_script('02_custom_add_skin_weight_influence')
		self._util.exec_generated_script('02_custom_add_skin_weight_influence')

	def run_script_add_anim_locators(self, *args):
		self._util.generate_script('03_animation_locators')
		self._util.exec_generated_script('03_animation_locators')

	def run_script_rig_it(self, *args):
		self._util.generate_script('04a_pre_rig_script')
		self._util.generate_script('04b_custom_pre_rig_script')
		self._util.generate_script('04c_rig_script')
		self._util.generate_script('04d_post_rig_script')
		self._util.generate_script('04e_custom_post_rig_script')
		self._util.exec_generated_script('04a_pre_rig_script')
		self._util.exec_generated_script('04b_custom_pre_rig_script')
		self._util.exec_generated_script('04c_rig_script')
		self._util.exec_generated_script('04d_post_rig_script')
		self._util.exec_generated_script('04e_custom_post_rig_script')

	def save_character(self, *args):
		dialog_title = 'Save Character'

		last_character_name = self._util.load_from_cache('last_character_name', '')

		character_name = self._util.dialog_box_ok_cancel(dialog_title, 'Enter a Character Name:', last_character_name)
		if character_name is None or len(character_name.strip()) == 0:
			# Save cancelled
			return

		self._util.save_to_cache('last_character_name', character_name)

		character_path = os.path.join(self._characters_location, character_name + '.mb')
		if os.path.exists(character_path):
			# Character already exists
			err_msg = 'Save failed.\n\nCharacter name \'$character_name\' already exists.'.replace('$character_name', character_name)
			self._util.message_box(dialog_title, err_msg)
			return

		if not os.path.isdir(self._characters_location):
			# Create directory
			os.makedirs(self._characters_location)

		cmds.file(rename=character_path)
		cmds.file(save=True, type='mayaBinary', force=True, prompt=True)

		if os.path.exists(character_path):
			# Save successful
			cmds.file(new=True, force=True)
			cmds.deleteUI(self._window_name)

			self._logger.command_message('Character saved as \'$character_path\'.'.replace('$character_path', character_path))
			success_msg = 'Save successful.\n\nSee Script Editor for details.'
			self._util.message_box(dialog_title, success_msg)

	def run_script_pose_arms_in_t_pose(self, *args):
		self._util.generate_script('adv_pose_arms_in_t_pose')
		self._util.exec_generated_script('adv_pose_arms_in_t_pose')

	def run_script_recreate_skeleton_and_geometry(self, *args):
		result = self._util.dialog_box_yes_no('Recreate Skeleton and Geometry', 'WARNING! This will detach the skin from the geometry. Are you sure?       ', default_button = 'No')
		if not result:
			return

		self._util.generate_script('adv_recreate_skeleton_and_geometry')
		self._util.exec_generated_script('adv_recreate_skeleton_and_geometry')

	def run_script_dump_skeleton_definition(self, *args):
		self._skeleton_definition.dump()

	def _create_ui_panel(self):
		widget_width = self._SIZE_WIDGET_WIDTH
		widget_height = self._SIZE_WIDGET_HEIGHT

		cmds.columnLayout(adjustableColumn=True)

		cmds.frameLayout(label='Rigging Scripts', borderStyle='etchedOut', collapsable=False, collapse=False, enable=True)
		cmds.rowColumnLayout(numberOfColumns=1)

		cmds.button(label='Generate Skeleton', command=partial(self.run_script_generate_skeleton), width=widget_width*2, height=widget_height)
		cmds.button(label='Add Skin Weight Influence', command=partial(self.run_script_add_skin_weight_influence), width=widget_width*2, height=widget_height)
		cmds.button(label='Add Anim Locators', command=partial(self.run_script_add_anim_locators), width=widget_width*2, height=widget_height)
		cmds.button(label='Rig It!', command=partial(self.run_script_rig_it), width=widget_width*2, height=widget_height)
		cmds.button(label='Save Character', command=partial(self.save_character), width=widget_width*2, height=widget_height)

		cmds.setParent(upLevel=True)
		cmds.setParent(upLevel=True)

		cmds.frameLayout(label='Advanced', borderStyle='etchedOut', collapsable=True, collapse=True, enable=True)
		cmds.rowColumnLayout(numberOfColumns=1)

		cmds.button(label='Pose Arms in T-Pose', command=partial(self.run_script_pose_arms_in_t_pose), width=widget_width*2, height=widget_height)
		cmds.button(label='Recreate Skeleton and Geometry', command=partial(self.run_script_recreate_skeleton_and_geometry), width=widget_width*2, height=widget_height)
		cmds.button(label='Dump Skeleton Definition', command=partial(self.run_script_dump_skeleton_definition), width=widget_width*2, height=widget_height)

		cmds.setParent(upLevel=True)
		cmds.setParent(upLevel=True)

		cmds.setParent(upLevel=True)
