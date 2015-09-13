import maya.cmds as cmds
import maya.mel as mel

from functools import partial
import os
import sys

class Rigathon:

	_APP_TITLE = 'ChyrosNX\'s Rig-a-thon'
	_APP_VERSION = 'Version 1.0 (Build 302)'

	def __init__(self, rigathon_path = None):
		self._init_path_locations(rigathon_path)
		self._init_modules()
		self._init_menu()
		self._init_UI()
		self._init_script_jobs()

	def _init_path_locations(self, rigathon_path):
		self._rigathon_path = rigathon_path

		main_dir = rigathon_path if not rigathon_path is None else 'C:/$_Chyros/GameDev/Workspace/Python/rigathon' # [DEBUG] developer's default path
		main_dir = os.path.normpath(main_dir)

		has_data_location = os.path.isdir(os.path.join(main_dir, 'data'))
		has_script_location = os.path.isdir(os.path.join(main_dir, 'script'))

		if has_data_location and has_script_location:
			self._data_location = os.path.join(main_dir, 'data')
			self._script_location = os.path.join(main_dir, 'script')
			self._generated_script_location = os.path.join(main_dir, 'generated')
			self._project_location = os.path.join(main_dir, 'project')
			self._characters_location = os.path.join(self._project_location, 'characters')
			self._export_location = os.path.join(self._project_location, 'export')

			# Add scripts
			if self._script_location not in sys.path:
				sys.path.append(self._script_location)
			if self._generated_script_location not in sys.path:
				sys.path.append(self._generated_script_location)
		else:
			err_msg_prefix = '$name - [ERROR] '.replace('$name', self.__class__.__name__)
			if rigathon_path is None:
				print (err_msg_prefix + 'No rigathon script path specified')
			else:
				print (err_msg_prefix + 'Incorrect rigathon script path specified - ' + rigathon_path)

			sys.exit()

	def _init_modules(self):
		from cnx_rigathon_settings import Settings
		from cnx_rigathon_util import Util
		from cnx_rigathon_rig_control_name import RigControlName
		from cnx_rigathon_matcher import Matcher

		self._settings = Settings()
		self._util = Util(self._settings, self._data_location, self._script_location, self._generated_script_location)
		self._rcName = RigControlName(self._util)
		self._matcher = Matcher(self._settings, self._util, self._rcName)

	def _init_menu(self):
		# Get Maya's main window
		maya_main_window = mel.eval('$tmpVar = $gMainWindow')

		# Delete previously created Rigathon menu, if exists
		menus = cmds.window(maya_main_window, query=True, menuArray=True)
		for menu in menus:
			label = cmds.menu(menu, query=True, label=True)
			if label == 'Rigathon':
				cmds.deleteUI(menu)
				break

		# Create Rigathon menu
		rigathon_menu = cmds.menu(parent=maya_main_window, label='Rigathon')
		cmds.menuItem(parent=rigathon_menu, label='Rig a Character', command=partial(self.show_rig_a_character_window))
		cmds.menuItem(parent=rigathon_menu, label='Add Character for Animation', command=partial(self.add_character_for_animation))
		cmds.menuItem(parent=rigathon_menu, divider=True)
		cmds.menuItem(parent=rigathon_menu, label='Show Animation UI', command=partial(self.show_animation_ui_window))
		cmds.menuItem(parent=rigathon_menu, divider=True)
		menuAdvanced = cmds.menuItem(parent=rigathon_menu, label='Ad&vanced', subMenu=True)
		cmds.menuItem(parent=menuAdvanced, label='(&1) Reload modules', command=partial(self.reload_modules))
		cmds.menuItem(parent=rigathon_menu, divider=True)
		cmds.menuItem(parent=rigathon_menu, label='&About...', command=partial(self.show_about_window))

	def _init_UI(self):
		self._about_window = self._util.to_ui_name('wnd_about')
		self._rig_a_character_window = self._util.to_ui_name('wnd_rig_a_character')
		self._animation_window = self._util.to_ui_name('wnd_animation_window')
		self._animation_dockControl = self._util.to_ui_name('wnd_animation_dockControl')
		self._add_character_for_animation_window = self._util.to_ui_name('wnd_add_character_for_animation')

		from cnx_rigathon_rig_a_character_ui import RigACharacterUI
		from cnx_rigathon_animation_ui import AnimationUI
		from cnx_rigathon_add_character_ui import AddCharacterUI

		self._rigACharacterUI = RigACharacterUI(self._util, self._characters_location, self._rig_a_character_window)
		self._animationUI = AnimationUI(self._settings, self._util, self._rcName, self._matcher, self._export_location, self._APP_TITLE, self._animation_window, self._animation_dockControl)
		self._addCharacterUI = AddCharacterUI(self._settings, self._util, self._matcher, self._animationUI, self._characters_location, self._add_character_for_animation_window)

	def _init_script_jobs(self):
		self._util.disable_undo()
		try:
			# NewSceneOpened script job
			self._script_job_new_scene_opened = cmds.scriptJob(event=['NewSceneOpened', partial(self.reset)])

			# SceneOpened script job
			self._script_job_scene_opened = cmds.scriptJob(event=['SceneOpened', partial(self.reset)])

			# SelectionChanged script job
			self._script_job_selection_changed = cmds.scriptJob(event=['SelectionChanged', partial(self._animationUI._ctrl_picker_highlight_selection)])

			# timeChanged script job
			self._script_job_time_changed = cmds.scriptJob(event=['timeChanged', partial(self._animationUI.refresh_widget_values)])

			# Redo script job
			self._script_job_redo = cmds.scriptJob(event=['Redo', partial(self._animationUI.refresh_widget_values)])

			# Undo script job
			self._script_job_undo = cmds.scriptJob(event=['Undo', partial(self._animationUI.refresh_widget_values)])
		finally:
			self._util.enable_undo()

	def _clean_up_windows(self):
		for window in [self._about_window, self._rig_a_character_window, self._animation_window, self._add_character_for_animation_window]:
			if cmds.window(window, exists=True):
				cmds.deleteUI(window)

		if cmds.dockControl(self._animation_dockControl, exists=True):
			cmds.deleteUI(self._animation_dockControl)

	def _clean_up_script_jobs(self):
		self._util.disable_undo()
		try:
			for script_job in [self._script_job_new_scene_opened, self._script_job_scene_opened, self._script_job_selection_changed, self._script_job_time_changed, self._script_job_redo, self._script_job_undo]:
				if script_job is not None:
					# Delete old script job, if any
					cmds.scriptJob(kill=script_job)
					script_job = None
		except Exception as e:
			print ('WARN: Unable to clean up script jobs for Rig-a-thon - ' + str(e))
		finally:
			self._util.enable_undo()

	def reset(self, *args):
		if cmds.dockControl(self._animation_dockControl, exists=True):
			cmds.dockControl(self._animation_dockControl, edit=True, visible=False)

	def show_rig_a_character_window(self, *args):
		self._rigACharacterUI.show_window()

	def add_character_for_animation(self, *args):
		self._addCharacterUI.show_window()

	def show_animation_ui_window(self, *args):
		self._animationUI.show_window()

	def show_about_window(self, *args):
		widget_width = 20
		widget_height = 15
		widget_margin_side = 20
		widget_margin_bottom = 5

		label_size = 200

		button_padding_right = 160
		button_size = 100

		if cmds.window(self._about_window, exists=True):
			return

		window = cmds.window(self._about_window, title='About Rigathon', sizeable=False, minimizeButton=False, maximizeButton=False)

		cmds.columnLayout(adjustableColumn=True)

		cmds.rowColumnLayout(numberOfColumns=5)
		cmds.separator(style='none', width=widget_margin_side, height=widget_height)
		cmds.separator(style='none', width=widget_width)
		cmds.separator(style='none', width=label_size)
		cmds.separator(style='none', width=widget_width)
		cmds.separator(style='none', width=widget_margin_side)

		cmds.separator(style='none', height=widget_height)
		cmds.separator(style='none')
		cmds.text(label='Rig-a-Thon', font='boldLabelFont', align='left')
		cmds.separator(style='none')
		cmds.separator(style='none')

		cmds.separator(style='none', height=widget_height)
		cmds.separator()
		cmds.separator()
		cmds.separator()
		cmds.separator(style='none')

		cmds.separator(style='none', height=widget_height)
		cmds.separator(style='none')
		cmds.text(label='Created by ChyrosNX', align='left')
		cmds.separator(style='none')
		cmds.separator(style='none')

		cmds.separator(style='none', height=widget_height)
		cmds.separator(style='none')
		cmds.text(label=self._APP_VERSION, align='left')
		cmds.separator(style='none')
		cmds.separator(style='none')

		cmds.separator(style='none', height=widget_height)
		cmds.separator(style='none')
		cmds.text(label='Copyleft 2014-2015 Codeswitch', align='left')
		cmds.separator(style='none')
		cmds.separator(style='none')

		cmds.separator(style='none', height=widget_height)
		cmds.separator(style='none')
		cmds.separator(style='none')
		cmds.separator(style='none')
		cmds.separator(style='none')

		cmds.separator(style='none', height=widget_height)
		cmds.separator(style='none')
		cmds.text(label='Contact Information', font='boldLabelFont', align='left')
		cmds.separator(style='none')
		cmds.separator(style='none')

		cmds.separator(style='none', height=widget_height)
		cmds.separator(style='none')
		cmds.text(label='Ariel \'ChyrosNX\' Falgui', align='right')
		cmds.separator(style='none')
		cmds.separator(style='none')

		cmds.separator(style='none', height=widget_height)
		cmds.separator(style='none')
		cmds.text(label='chykun@gmail.com', align='right')
		cmds.separator(style='none')
		cmds.separator(style='none')

		cmds.separator(style='none', height=widget_height)
		cmds.separator(style='none')
		cmds.separator(style='none')
		cmds.separator(style='none')
		cmds.separator(style='none')

		cmds.separator(style='none', height=widget_height)
		cmds.separator()
		cmds.separator()
		cmds.separator()
		cmds.separator(style='none')
		cmds.setParent(upLevel=True)

		cmds.rowColumnLayout(numberOfColumns=2)

		cmds.separator(style='none', width=button_padding_right, height=widget_height)
		cmds.button(label='OK', command=('cmds.deleteUI(\'' + window + '\', window=True)'), width=button_size)

		cmds.separator(style='none', height=widget_margin_bottom)

		cmds.showWindow(window)
		self._util.perform_maya_2015_window_resize_workaround(self._about_window)

	def reload_modules(self, *args):
		self._clean_up_script_jobs()
		self._clean_up_windows()

		import cnx_rigathon_logger
		import cnx_rigathon_settings
		import cnx_rigathon_util
		import cnx_rigathon_character
		import cnx_rigathon_characters
		import cnx_rigathon_characters_ui
		import cnx_rigathon_rig_control_name
		import cnx_rigathon_rig_control
		import cnx_rigathon_rig_controls
		import cnx_rigathon_widget
		import cnx_rigathon_widgets
		import cnx_rigathon_selection_set
		import cnx_rigathon_selection_sets
		import cnx_rigathon_selection_sets_ui
		import cnx_rigathon_matcher
		import cnx_rigathon_anim_sequence
		import cnx_rigathon_anim_sequences
		import cnx_rigathon_export_layer
		import cnx_rigathon_export_layers
		import cnx_rigathon_fbx_export_ui
		import cnx_rigathon_animation_ui
		import cnx_rigathon_add_character_ui
		import cnx_rigathon_rig_a_character_ui
		import cnx_rigathon_skeleton_definition
		import cnx_rigathon

		reload(cnx_rigathon_logger)
		reload(cnx_rigathon_settings)
		reload(cnx_rigathon_util)
		reload(cnx_rigathon_character)
		reload(cnx_rigathon_characters)
		reload(cnx_rigathon_characters_ui)
		reload(cnx_rigathon_rig_control_name)
		reload(cnx_rigathon_rig_control)
		reload(cnx_rigathon_rig_controls)
		reload(cnx_rigathon_widget)
		reload(cnx_rigathon_widgets)
		reload(cnx_rigathon_selection_set)
		reload(cnx_rigathon_selection_sets)
		reload(cnx_rigathon_selection_sets_ui)
		reload(cnx_rigathon_matcher)
		reload(cnx_rigathon_anim_sequence)
		reload(cnx_rigathon_anim_sequences)
		reload(cnx_rigathon_export_layer)
		reload(cnx_rigathon_export_layers)
		reload(cnx_rigathon_fbx_export_ui)
		reload(cnx_rigathon_animation_ui)
		reload(cnx_rigathon_add_character_ui)
		reload(cnx_rigathon_rig_a_character_ui)
		reload(cnx_rigathon_skeleton_definition)
		reload(cnx_rigathon)

		from cnx_rigathon import Rigathon
		Rigathon(self._rigathon_path)
