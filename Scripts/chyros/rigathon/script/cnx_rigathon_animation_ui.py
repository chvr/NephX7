import maya.cmds as cmds

from cnx_rigathon_logger import Logger
from cnx_rigathon_settings import Settings
from cnx_rigathon_util import Util
from cnx_rigathon_characters_ui import CharactersUI
from cnx_rigathon_rig_control_name import RigControlName
from cnx_rigathon_rig_controls import RigControls
from cnx_rigathon_widgets import Widgets
from cnx_rigathon_selection_sets_ui import SelectionSetsUI
from cnx_rigathon_fbx_export_ui import FbxExportUI

from functools import partial

class AnimationUI:

	# Default options
	_DEFAULT_NUM_OF_POSES = '5'
	_NUM_OF_POSES_MIN = 5
	_NUM_OF_POSES_MAX = 200
	_DEFAULT_POSES_PER_GROUP = 'None'
	_POSES_PER_GROUP_MIN = 5
	_POSES_PER_GROUP_MAX = 200

	_ROTATION_INTERPOLATION_LABELS = ['Independent Euler', 'Synchronized Euler', 'Quaternion Slerp', 'Quaternion Cubic', 'Quaternion TD']
	_ROTATION_INTERPOLATION_ANNOTATIONS = ['Independent Euler-angle curves', 'Synchronized Euler-angle curves', 'Quaternion Slerp', 'Quaternion Cubic', 'Quaternion Tangent Dependent']
	_ROTATION_INTERPOLATION_VALUES = [1, 2, 3, 4, 5]

	# Control color definitions
	_IK_COLOR = [0.9, 0.9, 0.3]
	_FK_COLOR = [0.4, 0.5, 0.7]
	_IK_FK_COLOR = [0.4, 0.7, 0.5]

	# Layers
	_CUSTOM_CONTROLS_LAYER = 'Controls_Custom'

	# Config
	_SETTINGS_CFG = 'settings'
	_MATCH_IK_FK_CFG = 'match_ik_fk'
	_SHOW_CHANNEL_BOX_CFG = 'show_channel_box'

	# Labels
	# Left
	_LBL_SWITCH_ARM_IK_LT = 'Lt Arm IK (&W)'
	_LBL_SWITCH_ARM_FK_LT = 'Lt Arm FK (&W)'
	_LBL_SWITCH_LOWERARM_IK_LT = 'Lt Elbow IK'
	_LBL_SWITCH_LOWERARM_FK_LT = 'Lt Forearm FK'
	_LBL_SWITCH_LEG_IK_LT = 'Lt Leg IK (&S)'
	_LBL_SWITCH_LEG_FK_LT = 'Lt Leg FK (&S)'
	_LBL_SWITCH_MANUAL_KNEE_LT = 'Lt Manual Knee'
	_LBL_SWITCH_AUTO_KNEE_LT = 'Lt Auto Knee'
	# Right
	_LBL_SWITCH_ARM_IK_RT = 'Rt Arm IK (&Q)'
	_LBL_SWITCH_ARM_FK_RT = 'Rt Arm FK (&Q)'
	_LBL_SWITCH_LOWERARM_IK_RT = 'Rt Elbow IK'
	_LBL_SWITCH_LOWERARM_FK_RT = 'Rt Forearm FK'
	_LBL_SWITCH_LEG_IK_RT = 'Rt Leg IK (&A)'
	_LBL_SWITCH_LEG_FK_RT = 'Rt Leg FK (&A)'
	_LBL_SWITCH_MANUAL_KNEE_RT = 'Rt Manual Knee'
	_LBL_SWITCH_AUTO_KNEE_RT = 'Rt Auto Knee'

	# Base widget sizes
	_SIZE_FRAME_WIDTH = 206
	_SIZE_SCROLL_WIDTH = 24
	_SIZE_WIDGET_WIDTH = 100
	_SIZE_WIDGET_HEIGHT = 30

	def __init__(self, settings, util, rigControlName, matcher, export_location, app_title, window_name, docked_window_name):
		self._logger = Logger(self.__class__.__name__)
		self._settings = settings
		self._util = util
		self._rcName = rigControlName
		self._matcher = matcher
		self._rigControls = RigControls(self._util, self._rcName)
		self._export_location = export_location
		self._app_title = app_title
		self._window_name = window_name
		self._docked_window_name = docked_window_name

		# Windows and layouts
		self._LAYOUT_POSES = self._util.to_ui_name('layout_poses')

		# Widgets
		self._WIDGET_CHANNEL_BOX = self._util.to_ui_name('ctl_channel_box')
		self._WIDGET_CHK_MATCH_IK_FK = self._util.to_ui_name('chk_match_ik_fk')
		self._WIDGET_CHK_SHOW_CHANNEL_BOX = self._util.to_ui_name('chk_show_channel_box')

		self._picker_widgets = {}
		self._widget_attribs = {}

		self._num_of_poses_value = None
		self._poses_per_group_value = None

		self._init_ui()

	def _init_ui(self):
		if cmds.dockControl(self._docked_window_name, exists=True):
			cmds.deleteUI(self._docked_window_name)

		self._widgets = Widgets(self._settings, self._util)
		self._charactersUI = CharactersUI(self, self._settings, self._util)
		self._selectionSetsUI = SelectionSetsUI(self._settings, self._util)
		self._fbxExportUI = FbxExportUI(self._settings, self._util, self._export_location)

	def add_character(self, namespace):
		return self._charactersUI.add_character(namespace)

	def activate_character(self, idx):
		return self._charactersUI.activate_character(idx)

	def show_window(self):
		if cmds.dockControl(self._docked_window_name, exists=True):
			# Unhide dock control
			cmds.dockControl(self._docked_window_name, edit=True, visible=True)
		else:
			# Create/recreate UI as needed
			self._create_UI()

			# Show UI as docked control
			cmds.dockControl(self._docked_window_name, label=self._app_title, area='right', content=self._window_name, allowedArea=['left', 'right'], visible=True)

		self._setup_panels()
		self._reload_settings()
		cmds.select(clear=True)
		self._util.update_editor_view()

	def _setup_panels(self, *args):
		self._util.disable_undo()
		try:
			is_body_ctrl_picker_panel_collapsed = self._settings.load('body_ctrl_picker_panel_collapsed', False)
			is_hand_ctrl_picker_panel_collapsed = self._settings.load('hand_ctrl_picker_panel_collapsed', True)
			is_selection_sets_panel_collapsed = self._settings.load('selection_sets_panel_collapsed', True)
			is_ik_fk_switcher_panel_collapsed = self._settings.load('ik_fk_switcher_panel_collapsed', False)
			is_pose_controls_panel_collapsed = self._settings.load('pose_controls_panel_collapsed', False)
			is_fbx_export_panel_collapsed = self._settings.load('fbx_export_panel_collapsed', True)
			is_advanced_controls_collapsed = self._settings.load('advanced_controls_panel_collapsed', True)

			cmds.frameLayout(self._util.to_ui_name('frm_body_ctrl_picker'), edit=True, collapse=is_body_ctrl_picker_panel_collapsed, collapseCommand=partial(self._panel_collapsed, 'body_ctrl_picker_panel_collapsed'), expandCommand=partial(self._panel_expanded, 'body_ctrl_picker_panel_collapsed'), enable=True)
			cmds.frameLayout(self._util.to_ui_name('frm_hand_ctrl_picker'), edit=True, collapse=is_hand_ctrl_picker_panel_collapsed, collapseCommand=partial(self._panel_collapsed, 'hand_ctrl_picker_panel_collapsed'), expandCommand=partial(self._panel_expanded, 'hand_ctrl_picker_panel_collapsed'), enable=True)
			cmds.frameLayout(self._util.to_ui_name('frm_selection_sets'), edit=True, collapse=is_selection_sets_panel_collapsed, collapseCommand=partial(self._panel_collapsed, 'selection_sets_panel_collapsed'), expandCommand=partial(self._panel_expanded, 'selection_sets_panel_collapsed'), enable=True)
			cmds.frameLayout(self._util.to_ui_name('frm_ik_fk_switcher_controls'), edit=True, collapse=is_ik_fk_switcher_panel_collapsed, collapseCommand=partial(self._panel_collapsed, 'ik_fk_switcher_panel_collapsed'), expandCommand=partial(self._panel_expanded, 'ik_fk_switcher_panel_collapsed'), enable=True)
			cmds.frameLayout(self._util.to_ui_name('frm_pose_controls'), edit=True, collapse=is_pose_controls_panel_collapsed, collapseCommand=partial(self._panel_collapsed, 'pose_controls_panel_collapsed'), expandCommand=partial(self._panel_expanded, 'pose_controls_panel_collapsed'), enable=True)
			cmds.frameLayout(self._util.to_ui_name('frm_fbx_export'), edit=True, collapse=is_fbx_export_panel_collapsed, collapseCommand=partial(self._panel_collapsed, 'fbx_export_panel_collapsed'), expandCommand=partial(self._panel_expanded, 'fbx_export_panel_collapsed'), enable=True)
			cmds.frameLayout(self._util.to_ui_name('frm_advanced_controls'), edit=True, collapse=is_advanced_controls_collapsed, collapseCommand=partial(self._panel_collapsed, 'advanced_controls_panel_collapsed'), expandCommand=partial(self._panel_expanded, 'advanced_controls_panel_collapsed'), enable=True)

			self._setup_poses()
			self._charactersUI.init_characters()
			self._selectionSetsUI.init_selection_sets()
			self._fbxExportUI.init_anim_sequences()
			self._fbxExportUI.init_export_layers()
			self.refresh_widget_values()
			self.load_rotation_interpolation()
		finally:
			self._util.enable_undo()

	def _reload_settings(self):
		# Poses
		self._num_of_poses = None
		self._poses_per_group_value = None

		self.update_num_of_poses(self._get_num_of_poses(True))
		self.update_poses_per_group(self._get_poses_per_group(True))

		# Is Match IK / FK
		is_match_ik_fk = self._settings.load(self._MATCH_IK_FK_CFG, True)
		cmds.checkBox(self._WIDGET_CHK_MATCH_IK_FK, edit=True, value=is_match_ik_fk)

		# Show Channel Box
		is_show_channel_box = self._settings.load(self._SHOW_CHANNEL_BOX_CFG, False)
		cmds.checkBox(self._WIDGET_CHK_SHOW_CHANNEL_BOX, edit=True, value=is_show_channel_box)
		cmds.channelBox(self._WIDGET_CHANNEL_BOX, edit=True, visible=is_show_channel_box)

	def _setup_poses(self):
		# Save bind pose
		if not self._settings.is_pose_group_exists(self._settings.BIND_POSE_INDEX):
			self.save_ctrl_pose(self._settings.BIND_POSE_INDEX, select_all = True)

		# Save default bind pose
		if not self._settings.is_pose_group_exists(self._settings.DEFAULT_BIND_POSE_INDEX):
			self.save_ctrl_pose(self._settings.DEFAULT_BIND_POSE_INDEX, select_all = True)

	def update_rotation_space(self, key, value, *args):
		mods = cmds.getModifiers()

		ctrl_mod = False
		if (mods & 4) > 0:
			ctrl_mod = True

		if ctrl_mod:
			# Ctrl modifier = update both left and right controls
			widget = self._widgets.get(key)
			widget.set_value(value)

			if RigControlName.LEFT_CONTROL in key:
				widget = self._widgets.get(key.replace(RigControlName.LEFT_CONTROL, RigControlName.RIGHT_CONTROL))
				widget.set_value(value)
			if RigControlName.RIGHT_CONTROL in key:
				widget = self._widgets.get(key.replace(RigControlName.RIGHT_CONTROL, RigControlName.LEFT_CONTROL))
				widget.set_value(value)
		else:
			# Update single control
			widget = self._widgets.get(key)
			widget.set_value(value)

	def match_ik_fk(self, *args):
		is_match_ik_fk = cmds.checkBox(self._WIDGET_CHK_MATCH_IK_FK, query=True, value=True)
		self._settings.save(self._MATCH_IK_FK_CFG, is_match_ik_fk)

	def refresh_widget_values(self, *args):
		if not cmds.button('btn_ik_fk_switcher_arm_lt', exists=True):
			return

		self._widgets.get('ik_head_rot_space_neck').update_display_value()
		self._widgets.get('ik_head_rot_space_shoulders').update_display_value()
		self._widgets.get('ik_head_rot_space_body').update_display_value()
		self._widgets.get('ik_head_rot_space_root').update_display_value()

		self._widgets.get('ik_head_trn_space_neck').update_display_value()
		self._widgets.get('ik_head_trn_space_shoulders').update_display_value()
		self._widgets.get('ik_head_trn_space_body').update_display_value()
		self._widgets.get('ik_head_trn_space_root').update_display_value()

		# Left
		is_arm_lt_fk_mode = self._get_obj_attr(self._rcName.to_ctrl_lt(self._rcName.ARM_SETTINGS) + '.ikFkBlend', 0) >= 0.5
		is_leg_lt_fk_mode = self._get_obj_attr(self._rcName.to_ctrl_lt(self._rcName.LEG_SETTINGS) + '.ikFkBlend', 0) >= 0.5
		is_fk_elbow_mode = self._get_obj_attr(self._rcName.to_ik_ctrl_lt(self._rcName.ELBOW) + '.fkElbowBlend', 0) >= 0.5
		is_auto_knee_mode = self._get_obj_attr(self._rcName.to_ik_ctrl_lt(self._rcName.FOOT) + '.autoKneeBlend', 0) >= 0.5
		show_fk_elbow_lt = not is_arm_lt_fk_mode and is_fk_elbow_mode

		lbl_arm_lt_switch = self._LBL_SWITCH_ARM_IK_LT if is_arm_lt_fk_mode else self._LBL_SWITCH_ARM_FK_LT
		lbl_lowerarm_lt_switch = self._LBL_SWITCH_LOWERARM_IK_LT if is_fk_elbow_mode else self._LBL_SWITCH_LOWERARM_FK_LT
		lbl_leg_lt_switch = self._LBL_SWITCH_LEG_IK_LT if is_leg_lt_fk_mode else self._LBL_SWITCH_LEG_FK_LT
		lbl_knee_lt_switch = self._LBL_SWITCH_MANUAL_KNEE_LT if is_auto_knee_mode else self._LBL_SWITCH_AUTO_KNEE_LT
		color_arm_lt_switch = self._IK_COLOR if is_arm_lt_fk_mode else self._FK_COLOR
		color_lowerarm_lt_switch = self._IK_COLOR if is_fk_elbow_mode else self._IK_FK_COLOR
		color_leg_lt_switch = self._IK_COLOR if is_leg_lt_fk_mode else self._FK_COLOR
		color_knee_lt_switch = self._IK_COLOR if is_auto_knee_mode else self._FK_COLOR

		# Control Picker Buttons
		cmds.button(self._picker_widgets['fk_lowerarm_lt'], edit=True, visible=not show_fk_elbow_lt)
		cmds.button(self._picker_widgets['fk_hand_lt'], edit=True, visible=not show_fk_elbow_lt)

		# IK / FK Switcher Buttons
		cmds.button('btn_ik_fk_switcher_arm_lt', edit=True, label=lbl_arm_lt_switch)
		cmds.button('btn_ik_fk_switcher_lowerarm_lt', edit=True, label=lbl_lowerarm_lt_switch)
		cmds.button('btn_ik_fk_switcher_leg_lt', edit=True, label=lbl_leg_lt_switch)
		cmds.button('btn_ik_fk_switcher_auto_manual_knee_lt', edit=True, label=lbl_knee_lt_switch)

		# IK / FK Switcher Status
		cmds.iconTextButton('btn_ik_fk_switcher_arm_lt_status', edit=True, backgroundColor=color_arm_lt_switch)
		cmds.iconTextButton('btn_ik_fk_switcher_lowerarm_lt_status', edit=True, backgroundColor=color_lowerarm_lt_switch)
		cmds.iconTextButton('btn_ik_fk_switcher_leg_lt_status', edit=True, backgroundColor=color_leg_lt_switch)
		cmds.iconTextButton('btn_ik_fk_switcher_auto_manual_knee_lt_status', edit=True, backgroundColor=self._IK_COLOR)

		self._widgets.get('fk_arm_rot_space_shoulder_lt').update_display_value()
		self._widgets.get('fk_arm_rot_space_body_lt').update_display_value()
		self._widgets.get('fk_arm_rot_space_root_lt').update_display_value()

		self._widgets.get('fk_leg_rot_space_hip_lt').update_display_value()
		self._widgets.get('fk_leg_rot_space_body_lt').update_display_value()
		self._widgets.get('fk_leg_rot_space_root_lt').update_display_value()

		# Right
		is_arm_rt_fk_mode = self._get_obj_attr(self._rcName.to_ctrl_rt(self._rcName.ARM_SETTINGS) + '.ikFkBlend', 0) >= 0.5
		is_leg_rt_fk_mode = self._get_obj_attr(self._rcName.to_ctrl_rt(self._rcName.LEG_SETTINGS) + '.ikFkBlend', 0) >= 0.5
		is_fk_elbow_mode = self._get_obj_attr(self._rcName.to_ik_ctrl_rt(self._rcName.ELBOW) + '.fkElbowBlend', 0) >= 0.5
		is_auto_knee_mode = self._get_obj_attr(self._rcName.to_ik_ctrl_rt(self._rcName.FOOT) + '.autoKneeBlend', 0) >= 0.5
		show_fk_elbow_rt = not is_arm_rt_fk_mode and is_fk_elbow_mode

		lbl_arm_rt_switch = self._LBL_SWITCH_ARM_IK_RT if is_arm_rt_fk_mode else self._LBL_SWITCH_ARM_FK_RT
		lbl_lowerarm_rt_switch = self._LBL_SWITCH_LOWERARM_IK_RT if is_fk_elbow_mode else self._LBL_SWITCH_LOWERARM_FK_RT
		lbl_leg_rt_switch = self._LBL_SWITCH_LEG_IK_RT if is_leg_rt_fk_mode else self._LBL_SWITCH_LEG_FK_RT
		lbl_knee_rt_switch = self._LBL_SWITCH_MANUAL_KNEE_RT if is_auto_knee_mode else self._LBL_SWITCH_AUTO_KNEE_RT
		color_arm_rt_switch = self._IK_COLOR if is_arm_rt_fk_mode else self._FK_COLOR
		color_lowerarm_rt_switch = self._IK_COLOR if is_fk_elbow_mode else self._IK_FK_COLOR
		color_leg_rt_switch = self._IK_COLOR if is_leg_rt_fk_mode else self._FK_COLOR
		color_knee_rt_switch = self._IK_COLOR if is_auto_knee_mode else self._FK_COLOR

		# Control Picker Buttons
		cmds.button(self._picker_widgets['fk_lowerarm_rt'], edit=True, visible=not show_fk_elbow_rt)
		cmds.button(self._picker_widgets['fk_hand_rt'], edit=True, visible=not show_fk_elbow_rt)

		# IK / FK Switcher Buttons
		cmds.button('btn_ik_fk_switcher_arm_rt', edit=True, label=lbl_arm_rt_switch)
		cmds.button('btn_ik_fk_switcher_lowerarm_rt', edit=True, label=lbl_lowerarm_rt_switch)
		cmds.button('btn_ik_fk_switcher_leg_rt', edit=True, label=lbl_leg_rt_switch)
		cmds.button('btn_ik_fk_switcher_auto_manual_knee_rt', edit=True, label=lbl_knee_rt_switch)

		# IK / FK Switcher Status
		cmds.iconTextButton('btn_ik_fk_switcher_arm_rt_status', edit=True, backgroundColor=color_arm_rt_switch)
		cmds.iconTextButton('btn_ik_fk_switcher_lowerarm_rt_status', edit=True, backgroundColor=color_lowerarm_rt_switch)
		cmds.iconTextButton('btn_ik_fk_switcher_leg_rt_status', edit=True, backgroundColor=color_leg_rt_switch)
		cmds.iconTextButton('btn_ik_fk_switcher_auto_manual_knee_rt_status', edit=True, backgroundColor=self._IK_COLOR)

		self._widgets.get('fk_arm_rot_space_shoulder_rt').update_display_value()
		self._widgets.get('fk_arm_rot_space_body_rt').update_display_value()
		self._widgets.get('fk_arm_rot_space_root_rt').update_display_value()

		self._widgets.get('fk_leg_rot_space_hip_rt').update_display_value()
		self._widgets.get('fk_leg_rot_space_body_rt').update_display_value()
		self._widgets.get('fk_leg_rot_space_root_rt').update_display_value()

	def save_ctrl_pose(self, index, select_all = False, verbose = False, *args):
		selected_objs = cmds.ls(selection=True, long=True)
		selected_ctrls = self._get_selected_ctrls(select_all)

		if verbose:
			self._logger.info('# Saving pose for $selection_type controls:' \
				.replace('$selection_type', 'all' if len(selected_ctrls) == self._rigControls.get_size() else 'selected') \
				)

		self._util.disable_undo()
		try:
			count = 0
			for ctrl_name in selected_ctrls:
				saved = self._settings.save_pose(index, ctrl_name)
				if saved:
					count += 1
					if verbose:
						self._logger.info('\t- ' + ctrl_name)
		finally:
			self._util.select_obj(selected_objs)
			self._util.enable_undo()

		if verbose:
			if count > 0:
				self._logger.info('\t* Saved pose for $count controls.'.replace('$count', str(count)))
			else:
				self._logger.info('\t* No selected rig controls to save pose.')

		if index > -1:
			if count > 0:
				pose_name = self._settings.load_pose_name(index)
				self._logger.command_message('Save Pose: $pose_name ($count)' \
					.replace('$pose_name', pose_name) \
					.replace('$count', str(count)) \
				)
			else:
				if verbose:
					self._logger.command_message('No selected rig controls to save pose from.')

	def load_ctrl_pose(self, index, select_all = False, verbose = False, *args):
		selected_ctrls = self._get_selected_ctrls(select_all)

		if verbose:
			self._logger.info('# Loading pose for $selection_type controls:' \
				.replace('$selection_type', 'all' if len(selected_ctrls) == self._rigControls.get_size() else 'selected') \
				)

		count = 0
		for ctrl_name in selected_ctrls:
			loaded = self._settings.load_pose(index, ctrl_name)
			if loaded:
				count += 1
				if verbose:
					self._logger.info('\t- ' + ctrl_name)

		if verbose:
			if count > 0:
				self._logger.info('\t* Loaded pose for $count controls.'.replace('$count', str(count)))
			else:
				self._logger.info('\t* No pose loaded for selected rig controls.')

		if index > -1:
			if count > 0:
				pose_name = self._settings.load_pose_name(index)
				self._logger.command_message('Load Pose: $pose_name ($count)' \
					.replace('$pose_name', pose_name) \
					.replace('$count', str(count)) \
				)
			else:
				self._logger.command_message('No pose loaded for selected rig controls.')

	def delete_ctrl_pose(self, index, select_all = False, verbose = False, *args):
		selected_ctrls = self._get_selected_ctrls(select_all)

		if verbose:
			self._logger.info('# Deleting pose for $selection_type controls:' \
				.replace('$selection_type', 'all' if len(selected_ctrls) == self._rigControls.get_size() else 'selected') \
				)

		self._util.disable_undo()
		try:
			count = 0
			for ctrl_name in selected_ctrls:
				deleted = self._settings.delete_pose(index, ctrl_name)
				if deleted:
					count += 1
					if verbose:
						self._logger.info('\t- ' + ctrl_name)
		finally:
			self._util.enable_undo()

		if verbose:
			if count > 0:
				self._logger.info('\t* Deleted pose for $count controls.'.replace('$count', str(count)))
			else:
				self._logger.info('\t* No pose deleted for selected rig controls.')

	def rename_pose_name(self, index, *args):
		selected_objs = cmds.ls(selection=True, long=True)

		pose_name = self._settings.load_pose_name(index)
		lbl_message = 'Enter new pose name:'
		dlg_rename = cmds.promptDialog(title='Rename', message=lbl_message, text=pose_name, button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
		if dlg_rename == 'OK':
			new_pose_name = cmds.promptDialog(query=True, text=True)

			self._util.disable_undo()
			try:
				if len(new_pose_name.strip()) > 0:
					self._settings.save_pose_name(index, new_pose_name)
				else:
					self._settings.delete_pose_name(index)
			finally:
				self._util.select_obj(selected_objs)
				self._util.enable_undo()

			self._save_load_poses_update_pose_names(index)

	def rename_pose_group(self, start, end, *args):
		selected_objs = cmds.ls(selection=True, long=True)

		pose_group = self._settings.load_pose_group_name(start, end)
		lbl_message = 'Enter new pose group name:'
		dlg_rename = cmds.promptDialog(title='Rename', message=lbl_message, text=pose_group, button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
		if dlg_rename == 'OK':
			new_pose_group = cmds.promptDialog(query=True, text=True)

			self._util.disable_undo()
			try:
				if len(new_pose_group.strip()) > 0:
					self._settings.save_pose_group_name(start, end, new_pose_group)
				else:
					self._settings.delete_pose_group_name(start, end)
			finally:
				self._util.select_obj(selected_objs)
				self._util.enable_undo()

			self._save_load_poses_update_pose_group_names(start, end)

	def reset_to_bind_pose(self, *args):
		self.load_ctrl_pose(self._settings.BIND_POSE_INDEX, select_all = True)
		self._logger.command_message('Bind pose loaded.')

	def set_new_bind_pose(self, *args):
		self.save_ctrl_pose(self._settings.BIND_POSE_INDEX, select_all = True)
		self._logger.command_message('Bind pose updated.')

	def reset_bind_pose_to_default(self, *args):
		self.load_ctrl_pose(self._settings.DEFAULT_BIND_POSE_INDEX, select_all = True)
		self.save_ctrl_pose(self._settings.BIND_POSE_INDEX, select_all = True)
		self._logger.command_message('Bind pose reset to default.')

	def euler_filter(self, selection, *args):
		selected_objs = cmds.ls(selection=True, long=True)

		if selection == 'all':
			# Select all rig controls
			self._ctrl_picker_select('all')
		elif len(selected_objs) == 0:
			self._logger.command_message('No control(s) selected.')
			return

		filtered = cmds.filterCurve()

		self._logger.command_message('Filter Curves: Euler Filter ($filtered)'.replace('$filtered', str(filtered)))
		self._util.select_obj(selected_objs)

	def load_rotation_interpolation(self):
		rotation_interpolation_value = cmds.optionVar(query='rotationInterpolationDefault')
		for label, value in zip(self._ROTATION_INTERPOLATION_LABELS, self._ROTATION_INTERPOLATION_VALUES):
			if rotation_interpolation_value == value:
				cmds.optionMenu(self._util.to_ui_name('opt_rotation_interp'), edit=True, value=label)
				break

	def update_rotation_interpolation(self, rotation_interpolation_label, *args):
		for label, value in zip(self._ROTATION_INTERPOLATION_LABELS, self._ROTATION_INTERPOLATION_VALUES):
			if rotation_interpolation_label == label:
				cmds.optionVar(intValue=('rotationInterpolationDefault',value))
				self._logger.command_message('Rotation Interpolation is set to \'$rotation_interpolation\'.'.replace('$rotation_interpolation', rotation_interpolation_label))
				break

	def set_fps(self, time_unit, *args):
		cmds.currentUnit(time=time_unit)
		self._logger.command_message('Time Unit is set to \'$time_unit\'.'.replace('$time_unit', time_unit))

	def y_up_axis(self, *args):
		cmds.upAxis(axis='Y', rotateView=False)

	def z_up_axis(self, *args):
		cmds.upAxis(axis='Z', rotateView=False)

	def control_scale(self, rate, *args):
		selected_objs = cmds.ls(selection=True)
		if len(selected_objs) == 0:
			self._logger.command_message('No control(s) selected.')
			return

		scaled = False
		for obj in selected_objs:
			if obj.rpartition(':')[2] not in self._rigControls.get_rig_control_names(False):
				continue

			# Select curves
			cmds.select(clear=True)
			cmds.select(obj + '.cv[*]', add=True)

			if len(cmds.ls(selection=True, long=True)) > 0:
				cmds.scale(rate, rate, rate, relative=True, centerPivot=True)
				scaled = True

		if not scaled:
			self._logger.command_message('No control(s) selected.')

		self._util.select_obj(selected_objs)

	def layer_ctrl_add(self, *args):
		self._util.disable_undo()
		try:
			err_msg = self._validate_display_layer_name(self._get_custom_layer())
			if err_msg is not None:
				self._logger.warn('Unable to add selected objects to custom controls layer: ' + err_msg)
				self._logger.command_message('Warn: Failed to add selected objects to custom layer. See Script Editor for details.')
				return False

			selected_objs = cmds.ls(selection=True, long=True)
			if len(selected_objs) == 0:
				self._logger.info('No selected objects to add onto custom controls layer.')
				self._logger.command_message('No object(s) selected.')
				return False

			obj_count = cmds.editDisplayLayerMembers(self._get_custom_layer(), selected_objs, noRecurse=True)
			self._logger.info('Selected objects added to custom controls layer.')
			self._logger.command_result(obj_count)

			return True
		finally:
			self._util.enable_undo()

	def layer_ctrl_remove(self, *args):
		self._util.disable_undo()
		try:
			err_msg = self._validate_display_layer_name(self._get_custom_layer())
			if err_msg is not None:
				self._logger.warn('Unable to remove selected objects to custom controls layer: ' + err_msg)
				self._logger.command_message('Warn: Failed to remove selected objects to custom layer. See Script Editor for details.')
				return False

			selected_objs = cmds.ls(selection=True, long=True)
			if len(selected_objs) == 0:
				self._logger.info('No selected objects to remove from custom controls layer.')
				self._logger.command_message('No object(s) selected.')
				return False

			obj_count = 0
			layer_objs = cmds.editDisplayLayerMembers(self._get_custom_layer(), query=True)
			if layer_objs is not None:
				for layer_obj in layer_objs:
					if layer_obj in selected_objs:
						obj_count += cmds.editDisplayLayerMembers('defaultLayer', layer_obj, noRecurse=True)

			self._logger.info('Selected objects removed from custom controls layer.')
			self._logger.command_result(obj_count)

			return True
		finally:
			self._util.enable_undo()

	def layer_ctrl_select(self, *args):
		err_msg = self._validate_display_layer_name(self._get_custom_layer())
		if err_msg is not None:
			self._logger.warn('Unable to select objects from custom controls layer: ' + err_msg)
			self._logger.command_message('Warn: Failed to select objects from custom layer. See Script Editor for details.')
			return False

		layer_objs = cmds.editDisplayLayerMembers(self._get_custom_layer(), query=True)
		cmds.select(layer_objs)

		return True

	def update_num_of_poses(self, num_of_poses, *args):
		self._util.disable_undo()
		try:
			self._widgets.get('num_of_poses').set_value(num_of_poses)
			self._num_of_poses_value = num_of_poses

			self._update_poses_per_group_items(num_of_poses)
			self._create_save_load_poses_content()
		finally:
			self._util.enable_undo()

	def update_poses_per_group(self, poses_per_group, *args):
		self._util.disable_undo()
		try:
			self._widgets.get('poses_per_group').set_value(poses_per_group)
			self._poses_per_group_value = poses_per_group

			self._create_save_load_poses_content()
		finally:
			self._util.enable_undo()

	def show_hide_channel_box(self, show_channel_box, *args):
		self._settings.save(self._SHOW_CHANNEL_BOX_CFG, show_channel_box)
		cmds.channelBox(self._WIDGET_CHANNEL_BOX, edit=True, visible=show_channel_box)

	def update_rig_matcher_defaults(self, *args):
		ref_name = self._settings.get_ref_name()
		self._matcher.init_rig_defaults(ref_name)

	def _create_UI(self):
		frame_width = self._SIZE_FRAME_WIDTH
		scroll_width = self._SIZE_SCROLL_WIDTH

		if cmds.window(self._window_name, exists=True):
			cmds.deleteUI(self._window_name)

		cmds.window(self._window_name, title=self._app_title, resizeToFitChildren=True, toolbox=True, retain=True)

		# Main layout
		cmds.paneLayout(configuration='vertical2')

		# Rigathon panel
		cmds.scrollLayout(childResizable=True, width=frame_width+scroll_width)
		self._create_characters_panel()
		self._create_body_ctrl_picker_panel()
		self._create_hand_ctrl_picker_panel()
		self._ctrl_picker_context_menus()
		self._create_selection_sets_panel()
		self._create_ik_fk_switcher_panel()
		self._create_save_load_poses_panel()
		self._create_fbx_export_panel()
		self._create_advanced_panel()
		cmds.setParent(upLevel=True)

		# ChannelBox panel
		cmds.channelBox(self._WIDGET_CHANNEL_BOX, width=self._SIZE_FRAME_WIDTH)

	def _create_characters_panel(self):
		self._charactersUI.create_panel(self._SIZE_FRAME_WIDTH)

	def _create_body_ctrl_picker_panel(self):
		frame_width = self._SIZE_FRAME_WIDTH
		widget_width = 29
		widget_height = 29

		cmds.frameLayout(self._util.to_ui_name('frm_body_ctrl_picker'), label='[Body] Rig Control Picker', borderStyle='etchedOut', collapsable=True, collapse=True, enable=False, width=frame_width)
		cmds.columnLayout(adjustableColumn=True)

		# Row 01: HEAD (IK)
		cmds.rowColumnLayout(numberOfColumns=2)
		cmds.separator(style='none', width=widget_width*3)
		# -- IK Head
		self._picker_widgets['ik_head'] = self._ctrl_picker_create_button('ik_head', widget_width)
		cmds.setParent(upLevel=True)

		# Row 02: NECK (FK), SHOULDER (IK)
		cmds.rowColumnLayout(numberOfColumns=4)
		cmds.separator(style='none', width=widget_width*2)
		# -- IK Shoulder RT
		cmds.rowColumnLayout(numberOfColumns=1, width=widget_width)
		self._picker_widgets['ik_shoulder_rt'] = self._ctrl_picker_create_button('ik_shoulder_rt', widget_width/1.5, widget_height/1.5)
		cmds.setParent(upLevel=True)
		# -- FK Neck
		self._picker_widgets['fk_neck'] = self._ctrl_picker_create_button('fk_neck', widget_width)
		# -- IK Shoulder LT
		cmds.rowColumnLayout(numberOfColumns=2, width=widget_width)
		cmds.separator(style='none', width=widget_width/3.5)
		self._picker_widgets['ik_shoulder_lt'] = self._ctrl_picker_create_button('ik_shoulder_lt', widget_width/1.5, widget_height/1.5)
		cmds.setParent(upLevel=True)
		cmds.setParent(upLevel=True)

		# Row 03: UPPERARM (FK), SHOULDER (IK)
		cmds.rowColumnLayout(numberOfColumns=6)
		cmds.separator(style='none', width=widget_width)
		self._picker_widgets['fk_upperarm_rt'] = self._ctrl_picker_create_button('fk_upperarm_rt', widget_width)
		self._picker_widgets['arm_gimbal_rt'] = self._ctrl_picker_create_button('arm_gimbal_rt', widget_width/2)
		self._picker_widgets['ik_shoulder'] = self._ctrl_picker_create_button('ik_shoulder', widget_width*2)
		self._picker_widgets['arm_gimbal_lt'] = self._ctrl_picker_create_button('arm_gimbal_lt', widget_width/2)
		self._picker_widgets['fk_upperarm_lt'] = self._ctrl_picker_create_button('fk_upperarm_lt', widget_width)
		cmds.setParent(upLevel=True)

		# Row 04: ELBOW (IK), LOWERARM (FK), SPINE 02 (FK)
		cmds.rowColumnLayout(numberOfColumns=7)
		# -- IK Elbow RT
		cmds.rowColumnLayout(numberOfColumns=1, width=widget_width)
		self._picker_widgets['ik_elbow_rt'] = self._ctrl_picker_create_button('ik_elbow_rt', widget_width/1.5, widget_height/1.5)
		cmds.setParent(upLevel=True)
		# -- FK Lowerarm RT
		cmds.flowLayout(width=widget_width, columnSpacing=0)
		self._picker_widgets['fk_lowerarm_rt'] = self._ctrl_picker_create_button('fk_lowerarm_rt', widget_width)
		self._picker_widgets['fk_elbow_lowerarm_rt'] = self._ctrl_picker_create_button('fk_elbow_lowerarm_rt', widget_width)
		cmds.setParent(upLevel=True)
		cmds.separator(style='none', width=widget_width/2)
		# -- FK Spine 02
		self._picker_widgets['fk_spine_02'] = self._ctrl_picker_create_button('fk_spine_02', widget_width*2)
		cmds.separator(style='none', width=widget_width/2)
		# -- FK Lowerarm LT
		cmds.flowLayout(width=widget_width, columnSpacing=0)
		self._picker_widgets['fk_lowerarm_lt'] = self._ctrl_picker_create_button('fk_lowerarm_lt', widget_width)
		self._picker_widgets['fk_elbow_lowerarm_lt'] = self._ctrl_picker_create_button('fk_elbow_lowerarm_lt', widget_width)
		cmds.setParent(upLevel=True)
		# -- IK Elbow LT
		cmds.rowColumnLayout(numberOfColumns=2, width=widget_width)
		cmds.separator(style='none', width=widget_width/3.5)
		self._picker_widgets['ik_elbow_lt'] = self._ctrl_picker_create_button('ik_elbow_lt', widget_width/1.5, widget_height/1.5)
		cmds.setParent(upLevel=True)
		cmds.setParent(upLevel=True)

		# Row 05: HAND (FK), SPINE_01 (FK)
		cmds.rowColumnLayout(numberOfColumns=6)
		cmds.separator(style='none', width=widget_width)
		# -- FK Hand RT
		cmds.flowLayout(width=widget_width, columnSpacing=0)
		self._picker_widgets['fk_hand_rt'] = self._ctrl_picker_create_button('fk_hand_rt', widget_width)
		self._picker_widgets['fk_elbow_hand_rt'] = self._ctrl_picker_create_button('fk_elbow_hand_rt', widget_width)
		cmds.setParent(upLevel=True)
		cmds.separator(style='none', width=widget_width/2)
		# -- FK Spine 01
		self._picker_widgets['fk_spine_01'] = self._ctrl_picker_create_button('fk_spine_01', widget_width*2)
		cmds.separator(style='none', width=widget_width/2)
		# -- FK Hand LT
		cmds.flowLayout(width=widget_width, columnSpacing=0)
		self._picker_widgets['fk_hand_lt'] = self._ctrl_picker_create_button('fk_hand_lt', widget_width)
		self._picker_widgets['fk_elbow_hand_lt'] = self._ctrl_picker_create_button('fk_elbow_hand_lt', widget_width)
		cmds.setParent(upLevel=True)
		cmds.setParent(upLevel=True)

		# Row 06: HAND (IK), HIP (IK)
		cmds.rowColumnLayout(numberOfColumns=7)
		# -- Arm Settings RT
		cmds.rowColumnLayout(numberOfColumns=1, width=widget_width)
		self._picker_widgets['arm_settings_rt'] = self._ctrl_picker_create_button('arm_settings_rt', widget_width/1.5, widget_height/1.5)
		cmds.setParent(upLevel=True)
		# -- IK Hand RT
		self._picker_widgets['ik_wrist_rt'] = self._ctrl_picker_create_button('ik_wrist_rt', widget_width)
		cmds.separator(style='none', width=widget_width/2)
		# -- IK Hip
		self._picker_widgets['ik_hip'] = self._ctrl_picker_create_button('ik_hip', widget_width*2)
		cmds.separator(style='none', width=widget_width/2)
		# -- IK Hand LT
		self._picker_widgets['ik_wrist_lt'] = self._ctrl_picker_create_button('ik_wrist_lt', widget_width)
		# -- Arm Settings LT
		cmds.rowColumnLayout(numberOfColumns=2, width=widget_width)
		cmds.separator(style='none', width=widget_width/3.5)
		self._picker_widgets['arm_settings_lt'] = self._ctrl_picker_create_button('arm_settings_lt', widget_width/1.5, widget_height/1.5)
		cmds.setParent(upLevel=True)
		cmds.setParent(upLevel=True)

		# Row 07: THIGH (FK), BODY
		cmds.rowColumnLayout(numberOfColumns=4)
		cmds.separator(style='none', width=widget_width*2)
		# -- FK Thigh RT
		self._picker_widgets['fk_thigh_rt'] = self._ctrl_picker_create_button('fk_thigh_rt', widget_width)
		# -- BODY
		self._picker_widgets['body'] = self._ctrl_picker_create_button('body', widget_width)
		# -- FK Thigh LT
		self._picker_widgets['fk_thigh_lt'] = self._ctrl_picker_create_button('fk_thigh_lt', widget_width)
		cmds.setParent(upLevel=True)

		# Row 08: KNEE (IK), CALF (FK)
		cmds.rowColumnLayout(numberOfColumns=6)
		cmds.separator(style='none', width=widget_width)
		# -- IK Knee RT
		cmds.rowColumnLayout(numberOfColumns=1, width=widget_width)
		self._picker_widgets['ik_knee_rt'] = self._ctrl_picker_create_button('ik_knee_rt', widget_width/1.5, widget_height/1.5)
		cmds.setParent(upLevel=True)
		# -- FK Calf RT
		self._picker_widgets['fk_calf_rt'] = self._ctrl_picker_create_button('fk_calf_rt', widget_width)
		cmds.separator(style='none', width=widget_width)
		# -- FK Calf LT
		self._picker_widgets['fk_calf_lt'] = self._ctrl_picker_create_button('fk_calf_lt', widget_width)
		# -- IK Knee LT
		cmds.rowColumnLayout(numberOfColumns=2, width=widget_width)
		cmds.separator(style='none', width=widget_width/3.5)
		self._picker_widgets['ik_knee_lt'] = self._ctrl_picker_create_button('ik_knee_lt', widget_width/1.5, widget_height/1.5)
		cmds.setParent(upLevel=True)
		cmds.setParent(upLevel=True)

		# Row 09: FOOT (FK)
		cmds.rowColumnLayout(numberOfColumns=4)
		cmds.separator(style='none', width=widget_width*2)
		# -- FK Foot RT
		self._picker_widgets['fk_foot_rt'] = self._ctrl_picker_create_button('fk_foot_rt', widget_width)
		cmds.separator(style='none', width=widget_width)
		# -- FK Foot LT
		self._picker_widgets['fk_foot_lt'] = self._ctrl_picker_create_button('fk_foot_lt', widget_width)
		cmds.setParent(upLevel=True)

		# Row 10: FOOT (IK), BALL (FK)
		cmds.rowColumnLayout(numberOfColumns=7)
		# -- IK Elbow RT
		cmds.rowColumnLayout(numberOfColumns=1, width=widget_width)
		self._picker_widgets['leg_settings_rt'] = self._ctrl_picker_create_button('leg_settings_rt', widget_width/1.5, widget_height/1.5)
		cmds.setParent(upLevel=True)
		# -- FK Ball RT
		self._picker_widgets['fk_ball_rt'] = self._ctrl_picker_create_button('fk_ball_rt', widget_width)
		# -- IK Foot RT
		self._picker_widgets['ik_foot_rt'] = self._ctrl_picker_create_button('ik_foot_rt', widget_width)
		cmds.separator(style='none', width=widget_width)
		# -- IK Foot LT
		self._picker_widgets['ik_foot_lt'] = self._ctrl_picker_create_button('ik_foot_lt', widget_width)
		# -- FK Ball LT
		self._picker_widgets['fk_ball_lt'] = self._ctrl_picker_create_button('fk_ball_lt', widget_width)
		# -- Leg Settins LT
		cmds.rowColumnLayout(numberOfColumns=2, width=widget_width)
		cmds.separator(style='none', width=widget_width/3.5)
		self._picker_widgets['leg_settings_lt'] = self._ctrl_picker_create_button('leg_settings_lt', widget_width/1.5, widget_height/1.5)
		cmds.setParent(upLevel=True)
		cmds.setParent(upLevel=True)

		# Row 11: OFFSET, ROOT
		cmds.rowColumnLayout(numberOfColumns=4, height=widget_height/2)
		cmds.separator(style='none', width=widget_width)
		# -- Offset
		self._picker_widgets['offset1'] = self._ctrl_picker_create_button('offset', widget_width*2)
		# -- Root
		self._picker_widgets['root'] = self._ctrl_picker_create_button('root', widget_width)
		# -- Offset
		self._picker_widgets['offset2'] = self._ctrl_picker_create_button('offset', widget_width*2)
		cmds.setParent(upLevel=True)

		# Row 12: CHARACTER
		cmds.rowColumnLayout(numberOfColumns=2, height=widget_height/2)
		cmds.separator(style='none', width=widget_width)
		# -- Character
		self._picker_widgets['character'] = self._ctrl_picker_create_button('character', widget_width*5)
		cmds.setParent(upLevel=True)

		cmds.setParent(upLevel=True)
		cmds.setParent(upLevel=True)

	def _create_hand_ctrl_picker_panel(self):
		frame_width = self._SIZE_FRAME_WIDTH
		widget_width = 28 / 1.42
		widget_height = 28 / 2
		gap_width = widget_width * 1.4

		cmds.frameLayout(self._util.to_ui_name('frm_hand_ctrl_picker'), label='[Hand] Rig Control Picker', borderStyle='etchedOut', collapsable=True, collapse=True, enable=False, width=frame_width)
		cmds.rowColumnLayout(numberOfColumns=11, width=widget_width, columnAttach=[1, 'left', 1])

		# Column 01: Right Finger 03
		cmds.columnLayout(width=widget_width)
		self._picker_widgets['fk_pinky_03_rt'] = self._ctrl_picker_create_button('fk_pinky_03_rt', widget_width, widget_height)
		self._picker_widgets['fk_ring_03_rt'] = self._ctrl_picker_create_button('fk_ring_03_rt', widget_width, widget_height)
		self._picker_widgets['fk_middle_03_rt'] = self._ctrl_picker_create_button('fk_middle_03_rt', widget_width, widget_height)
		self._picker_widgets['fk_index_03_rt'] = self._ctrl_picker_create_button('fk_index_03_rt', widget_width, widget_height)
		cmds.setParent(upLevel=True)

		# Column 02: Right Finger 02
		cmds.columnLayout(width=widget_width)
		self._picker_widgets['fk_pinky_02_rt'] = self._ctrl_picker_create_button('fk_pinky_02_rt', widget_width, widget_height)
		self._picker_widgets['fk_ring_02_rt'] = self._ctrl_picker_create_button('fk_ring_02_rt', widget_width, widget_height)
		self._picker_widgets['fk_middle_02_rt'] = self._ctrl_picker_create_button('fk_middle_02_rt', widget_width, widget_height)
		self._picker_widgets['fk_index_02_rt'] = self._ctrl_picker_create_button('fk_index_02_rt', widget_width, widget_height)
		cmds.separator(style='none', height=widget_height)
		self._picker_widgets['fk_thumb_02_rt'] = self._ctrl_picker_create_button('fk_thumb_02_rt', widget_width, widget_height)
		cmds.setParent(upLevel=True)

		# Column 03: Right Finger 01
		cmds.columnLayout(width=widget_width)
		self._picker_widgets['fk_pinky_01_rt'] = self._ctrl_picker_create_button('fk_pinky_01_rt', widget_width, widget_height)
		self._picker_widgets['fk_ring_01_rt'] = self._ctrl_picker_create_button('fk_ring_01_rt', widget_width, widget_height)
		self._picker_widgets['fk_middle_01_rt'] = self._ctrl_picker_create_button('fk_middle_01_rt', widget_width, widget_height)
		self._picker_widgets['fk_index_01_rt'] = self._ctrl_picker_create_button('fk_index_01_rt', widget_width, widget_height)
		self._picker_widgets['fk_thumb_orbit_rt'] = self._ctrl_picker_create_button('fk_thumb_orbit_rt', widget_width, widget_height)
		self._picker_widgets['fk_thumb_01_rt'] = self._ctrl_picker_create_button('fk_thumb_01_rt', widget_width, widget_height)
		cmds.setParent(upLevel=True)

		# Column 04: Right Fingers Compound controls
		cmds.columnLayout(width=widget_width/1.3)
		self._picker_widgets['pinky_rt'] = self._ctrl_picker_create_button('pinky_rt', widget_width/1.3, widget_height)
		self._picker_widgets['ring_rt'] = self._ctrl_picker_create_button('ring_rt', widget_width/1.3, widget_height)
		self._picker_widgets['middle_rt'] = self._ctrl_picker_create_button('middle_rt', widget_width/1.3, widget_height)
		self._picker_widgets['index_rt'] = self._ctrl_picker_create_button('index_rt', widget_width/1.3, widget_height)
		self._picker_widgets['thumb_rt'] = self._ctrl_picker_create_button('thumb_rt', widget_width/1.3, widget_height)
		cmds.setParent(upLevel=True)

		# Column 05: Right Hand Compound Control
		cmds.columnLayout(width=widget_width/1.3)
		cmds.separator(style='none', height=widget_height)
		self._picker_widgets['hand_rt'] = self._ctrl_picker_create_button('hand_rt', widget_width/1.3, widget_height*3)
		cmds.setParent(upLevel=True)

		# Column 06: Separator
		cmds.columnLayout(width=gap_width)
		cmds.separator(style='none')
		cmds.setParent(upLevel=True)

		# Column 07: Right Hand Compound Control
		cmds.columnLayout(width=widget_width/1.3)
		cmds.separator(style='none', height=widget_height)
		self._picker_widgets['hand_lt'] = self._ctrl_picker_create_button('hand_lt', widget_width/1.3, widget_height*3)
		cmds.setParent(upLevel=True)

		# Column 08: Right Finger Compound Controls
		cmds.columnLayout(width=widget_width/1.3)
		self._picker_widgets['pinky_lt'] = self._ctrl_picker_create_button('pinky_lt', widget_width/1.3, widget_height)
		self._picker_widgets['ring_lt'] = self._ctrl_picker_create_button('ring_lt', widget_width/1.3, widget_height)
		self._picker_widgets['middle_lt'] = self._ctrl_picker_create_button('middle_lt', widget_width/1.3, widget_height)
		self._picker_widgets['index_lt'] = self._ctrl_picker_create_button('index_lt', widget_width/1.3, widget_height)
		self._picker_widgets['thumb_lt'] = self._ctrl_picker_create_button('thumb_lt', widget_width/1.3, widget_height)
		cmds.setParent(upLevel=True)

		# Column 09: Right Finger 01
		cmds.columnLayout(width=widget_width)
		self._picker_widgets['fk_pinky_01_lt'] = self._ctrl_picker_create_button('fk_pinky_01_lt', widget_width, widget_height)
		self._picker_widgets['fk_ring_01_lt'] = self._ctrl_picker_create_button('fk_ring_01_lt', widget_width, widget_height)
		self._picker_widgets['fk_middle_01_lt'] = self._ctrl_picker_create_button('fk_middle_01_lt', widget_width, widget_height)
		self._picker_widgets['fk_index_01_lt'] = self._ctrl_picker_create_button('fk_index_01_lt', widget_width, widget_height)
		cmds.separator(style='none')
		self._picker_widgets['fk_thumb_orbit_lt'] = self._ctrl_picker_create_button('fk_thumb_orbit_lt', widget_width, widget_height)
		self._picker_widgets['fk_thumb_01_lt'] = self._ctrl_picker_create_button('fk_thumb_01_lt', widget_width, widget_height)
		cmds.setParent(upLevel=True)

		# Column 10: Right Finger 02
		cmds.columnLayout(width=widget_width)
		self._picker_widgets['fk_pinky_02_lt'] = self._ctrl_picker_create_button('fk_pinky_02_lt', widget_width, widget_height)
		self._picker_widgets['fk_ring_02_lt'] = self._ctrl_picker_create_button('fk_ring_02_lt', widget_width, widget_height)
		self._picker_widgets['fk_middle_02_lt'] = self._ctrl_picker_create_button('fk_middle_02_lt', widget_width, widget_height)
		self._picker_widgets['fk_index_02_lt'] = self._ctrl_picker_create_button('fk_index_02_lt', widget_width, widget_height)
		cmds.separator(style='none', height=widget_height)
		self._picker_widgets['fk_thumb_02_lt'] = self._ctrl_picker_create_button('fk_thumb_02_lt', widget_width, widget_height)
		cmds.setParent(upLevel=True)

		# Column 11: Right Finger 03
		cmds.columnLayout(width=widget_width)
		self._picker_widgets['fk_pinky_03_lt'] = self._ctrl_picker_create_button('fk_pinky_03_lt', widget_width, widget_height)
		self._picker_widgets['fk_ring_03_lt'] = self._ctrl_picker_create_button('fk_ring_03_lt', widget_width, widget_height)
		self._picker_widgets['fk_middle_03_lt'] = self._ctrl_picker_create_button('fk_middle_03_lt', widget_width, widget_height)
		self._picker_widgets['fk_index_03_lt'] = self._ctrl_picker_create_button('fk_index_03_lt', widget_width, widget_height)
		cmds.setParent(upLevel=True)

		cmds.setParent(upLevel=True)
		cmds.setParent(upLevel=True)

	def _ctrl_picker_context_menus(self):
		for widget in self._picker_widgets:
			widget_menu = cmds.popupMenu(parent=self._picker_widgets[widget], button=3)
			cmds.menuItem(parent=widget_menu, label='Select &All', command=partial(self._ctrl_picker_select, 'all'))
			cmds.menuItem(parent=widget_menu, label='Select All (with Key&s only)', command=partial(self._ctrl_picker_select, 'keyed'))

			if widget == 'ik_head':
				control_label = 'HEAD IK'

				attribute_name = self._rcName.to_name(self._rcName.HEAD, self._rcName.IK, self._rcName.CENTER, 0, True) + '.rotationSpace'
				ihrs_neck_widget_name = self._widgets.create('ik_head_rot_space_neck', 'menuItem_radioButton', attribute_name, value_id = 0)
				ihrs_shoulders_widget_name = self._widgets.create('ik_head_rot_space_shoulders', 'menuItem_radioButton', attribute_name, value_id = 1)
				ihrs_body_widget_name = self._widgets.create('ik_head_rot_space_body', 'menuItem_radioButton', attribute_name, value_id = 2)
				ihrs_root_widget_name = self._widgets.create('ik_head_rot_space_root', 'menuItem_radioButton', attribute_name, value_id = 3)

				attribute_name = self._rcName.to_name(self._rcName.HEAD, self._rcName.IK, self._rcName.CENTER, 0, True) + '.translationSpace'
				ihts_neck_widget_name = self._widgets.create('ik_head_trn_space_neck', 'menuItem_radioButton', attribute_name, value_id = 0)
				ihts_shoulders_widget_name = self._widgets.create('ik_head_trn_space_shoulders', 'menuItem_radioButton', attribute_name, value_id = 1)
				ihts_body_widget_name = self._widgets.create('ik_head_trn_space_body', 'menuItem_radioButton', attribute_name, value_id = 2)
				ihts_root_widget_name = self._widgets.create('ik_head_trn_space_root', 'menuItem_radioButton', attribute_name, value_id = 3)

				cmds.menuItem(divider=True)
				cmds.menuItem(parent=widget_menu, label='Rotation Space - $control_label'.replace('$control_label', control_label), boldFont=True)
				cmds.radioMenuItemCollection()
				cmds.menuItem(ihrs_neck_widget_name, label='Neck', command=partial(self.update_rotation_space, 'ik_head_rot_space_neck', 0), radioButton=False)
				cmds.menuItem(ihrs_shoulders_widget_name, label='Shoulders', command=partial(self.update_rotation_space, 'ik_head_rot_space_shoulders', 1), radioButton=False)
				cmds.menuItem(ihrs_body_widget_name, label='Body', command=partial(self.update_rotation_space, 'ik_head_rot_space_body', 2), radioButton=False)
				cmds.menuItem(ihrs_root_widget_name, label='Root', command=partial(self.update_rotation_space, 'ik_head_rot_space_root', 3), radioButton=False)

				cmds.menuItem(divider=True)
				cmds.menuItem(parent=widget_menu, label='Translation Space - $control_label'.replace('$control_label', control_label), boldFont=True)
				cmds.radioMenuItemCollection()
				cmds.menuItem(ihts_neck_widget_name, label='Neck', command=partial(self.update_rotation_space, 'ik_head_trn_space_neck', 0), radioButton=False)
				cmds.menuItem(ihts_shoulders_widget_name, label='Shoulders', command=partial(self.update_rotation_space, 'ik_head_trn_space_shoulders', 1), radioButton=False)
				cmds.menuItem(ihts_body_widget_name, label='Body', command=partial(self.update_rotation_space, 'ik_head_trn_space_body', 2), radioButton=False)
				cmds.menuItem(ihts_root_widget_name, label='Root', command=partial(self.update_rotation_space, 'ik_head_trn_space_root', 3), radioButton=False)

			if widget in ['ik_wrist_lt', 'fk_upperarm_lt', 'fk_lowerarm_lt', 'fk_hand_lt', 'fk_elbow_lowerarm_lt', 'fk_elbow_hand_lt', 'ik_wrist_rt', 'fk_upperarm_rt', 'fk_lowerarm_rt', 'fk_hand_rt', 'fk_elbow_lowerarm_rt', 'fk_elbow_hand_rt']:
				position = ''
				control_label = ''
				attribute_name = ''
				if widget in ['ik_wrist_lt', 'fk_upperarm_lt', 'fk_lowerarm_lt', 'fk_hand_lt', 'fk_elbow_lowerarm_lt', 'fk_elbow_hand_lt']:
					position = '_' + RigControlName.LEFT_CONTROL
					control_label = 'LEFT ARM FK'
					attribute_name = self._rcName.to_name(self._rcName.ARM_SETTINGS, '', self._rcName.LEFT, 0, True) + '.rotationSpace'
				elif widget in ['ik_wrist_rt', 'fk_upperarm_rt', 'fk_lowerarm_rt', 'fk_hand_rt', 'fk_elbow_lowerarm_rt', 'fk_elbow_hand_rt']:
					position = '_' + RigControlName.RIGHT_CONTROL
					control_label = 'RIGHT ARM FK'
					attribute_name = self._rcName.to_name(self._rcName.ARM_SETTINGS, '', self._rcName.RIGHT, 0, True) + '.rotationSpace'

				fars_shoulder_widget_name = self._widgets.create('fk_arm_rot_space_shoulder' + position, 'menuItem_radioButton', attribute_name, value_id = 0)
				fars_body_widget_name = self._widgets.create('fk_arm_rot_space_body' + position, 'menuItem_radioButton', attribute_name, value_id = 1)
				fars_root_widget_name = self._widgets.create('fk_arm_rot_space_root' + position, 'menuItem_radioButton', attribute_name, value_id = 2)

				cmds.menuItem(divider=True)
				cmds.menuItem(parent=widget_menu, label='Rotation Space - $control_label'.replace('$control_label', control_label), boldFont=True)
				cmds.radioMenuItemCollection()
				cmds.menuItem(fars_shoulder_widget_name, label='Shoulder', command=partial(self.update_rotation_space, 'fk_arm_rot_space_shoulder' + position, 0), radioButton=False)
				cmds.menuItem(fars_body_widget_name, label='Body', command=partial(self.update_rotation_space, 'fk_arm_rot_space_body' + position, 1), radioButton=False)
				cmds.menuItem(fars_root_widget_name, label='Root', command=partial(self.update_rotation_space, 'fk_arm_rot_space_root' + position, 2), radioButton=False)

			if widget in ['ik_foot_lt', 'fk_thigh_lt', 'fk_calf_lt', 'fk_foot_lt', 'fk_ball_lt', 'ik_foot_rt', 'fk_thigh_rt', 'fk_calf_rt', 'fk_foot_rt', 'fk_ball_rt']:
				position = ''
				control_label = ''
				attribute_name = ''
				if widget in ['ik_foot_lt', 'fk_thigh_lt', 'fk_calf_lt', 'fk_foot_lt', 'fk_ball_lt']:
					position = '_' + RigControlName.LEFT_CONTROL
					control_label = 'LEFT LEG FK'
					attribute_name = self._rcName.to_name(self._rcName.LEG_SETTINGS, '', self._rcName.LEFT, 0, True) + '.rotationSpace'
				elif widget in ['ik_foot_rt', 'fk_thigh_rt', 'fk_calf_rt', 'fk_foot_rt', 'fk_ball_rt']:
					position = '_' + RigControlName.RIGHT_CONTROL
					control_label = 'RIGHT LEG FK'
					attribute_name = self._rcName.to_name(self._rcName.LEG_SETTINGS, '', self._rcName.RIGHT, 0, True) + '.rotationSpace'

				fars_hip_widget_name = self._widgets.create('fk_leg_rot_space_hip' + position, 'menuItem_radioButton', attribute_name, value_id = 0)
				fars_body_widget_name = self._widgets.create('fk_leg_rot_space_body' + position, 'menuItem_radioButton', attribute_name, value_id = 1)
				fars_root_widget_name = self._widgets.create('fk_leg_rot_space_root' + position, 'menuItem_radioButton', attribute_name, value_id = 2)

				cmds.menuItem(divider=True)
				cmds.menuItem(parent=widget_menu, label='Rotation Space - $control_label'.replace('$control_label', control_label), boldFont=True)
				cmds.radioMenuItemCollection()
				cmds.menuItem(fars_hip_widget_name, label='Hip', command=partial(self.update_rotation_space, 'fk_leg_rot_space_hip' + position, 0), radioButton=False)
				cmds.menuItem(fars_body_widget_name, label='Body', command=partial(self.update_rotation_space, 'fk_leg_rot_space_body' + position, 1), radioButton=False)
				cmds.menuItem(fars_root_widget_name, label='Root', command=partial(self.update_rotation_space, 'fk_leg_rot_space_root' + position, 2), radioButton=False)

	def _create_selection_sets_panel(self):
		self._selectionSetsUI.create_panel(self._SIZE_FRAME_WIDTH)

	def _create_ik_fk_switcher_panel(self):
		frame_width = self._SIZE_FRAME_WIDTH
		widget_width = self._SIZE_WIDGET_WIDTH
		widget_height = self._SIZE_WIDGET_HEIGHT

		cmds.frameLayout(self._util.to_ui_name('frm_ik_fk_switcher_controls'), label='IK / FK Switcher', borderStyle='etchedOut', collapsable=True, collapse=True, enable=False, width=frame_width)
		cmds.columnLayout(adjustableColumn=True)

		cmds.rowColumnLayout(numberOfColumns=3)
		offset = 5
		cmds.separator(style='none', width=offset, height=widget_height/2)
		cmds.checkBox(self._WIDGET_CHK_MATCH_IK_FK, label=' Match IK / FK', changeCommand=partial(self.match_ik_fk), width=widget_width*1.5-offset, value=True)
		cmds.button('btn_ik_fk_switcher_refresh', label='Refresh', command=partial(self.refresh_widget_values), width=widget_width/2, height=widget_height/1.5)
		cmds.setParent(upLevel=True)

		cmds.rowColumnLayout(numberOfColumns=4)
		status_width = 15
		cmds.rowLayout(width=status_width)
		cmds.iconTextButton('btn_ik_fk_switcher_arm_rt_status', style='textOnly', label='>', font='boldLabelFont', width=status_width-2, height=widget_height-2, enable=False)
		cmds.setParent(upLevel=True)
		cmds.button('btn_ik_fk_switcher_arm_rt', label='Loading...', command=partial(self.ik_fk_switcher_arm_rt), width=widget_width-status_width, height=widget_height)
		cmds.rowLayout(width=status_width)
		cmds.iconTextButton('btn_ik_fk_switcher_arm_lt_status', style='textOnly', label='>', font='boldLabelFont', width=status_width-2, height=widget_height-2, enable=False)
		cmds.setParent(upLevel=True)
		cmds.button('btn_ik_fk_switcher_arm_lt', label='Loading...', command=partial(self.ik_fk_switcher_arm_lt), width=widget_width-status_width, height=widget_height)
		cmds.rowLayout(width=status_width)
		cmds.iconTextButton('btn_ik_fk_switcher_lowerarm_rt_status', style='textOnly', label='>', font='boldLabelFont', width=status_width-2, height=widget_height-2, enable=False)
		cmds.setParent(upLevel=True)
		cmds.button('btn_ik_fk_switcher_lowerarm_rt', label='Loading...', command=partial(self.ik_fk_switcher_lowerarm_rt), width=widget_width-status_width, height=widget_height)
		cmds.rowLayout(width=status_width)
		cmds.iconTextButton('btn_ik_fk_switcher_lowerarm_lt_status', style='textOnly', label='>', font='boldLabelFont', width=status_width-2, height=widget_height-2, enable=False)
		cmds.setParent(upLevel=True)
		cmds.button('btn_ik_fk_switcher_lowerarm_lt', label='Loading...', command=partial(self.ik_fk_switcher_lowerarm_lt), width=widget_width-status_width, height=widget_height)
		cmds.rowLayout(width=status_width)
		cmds.iconTextButton('btn_ik_fk_switcher_leg_rt_status', style='textOnly', label='>', font='boldLabelFont', width=status_width-2, height=widget_height-2, enable=False)
		cmds.setParent(upLevel=True)
		cmds.button('btn_ik_fk_switcher_leg_rt', label='Loading...', command=partial(self.ik_fk_switcher_leg_rt), width=widget_width-status_width, height=widget_height)
		cmds.rowLayout(width=status_width)
		cmds.iconTextButton('btn_ik_fk_switcher_leg_lt_status', style='textOnly', label='>', font='boldLabelFont', width=status_width-2, height=widget_height-2, enable=False)
		cmds.setParent(upLevel=True)
		cmds.button('btn_ik_fk_switcher_leg_lt', label='Loading...', command=partial(self.ik_fk_switcher_leg_lt), width=widget_width-status_width, height=widget_height)
		cmds.rowLayout(width=status_width)
		cmds.iconTextButton('btn_ik_fk_switcher_auto_manual_knee_rt_status', style='textOnly', label='>', font='boldLabelFont', width=status_width-2, height=widget_height-2, enable=False)
		cmds.setParent(upLevel=True)
		cmds.button('btn_ik_fk_switcher_auto_manual_knee_rt', label='Loading...', command=partial(self.ik_fk_switcher_auto_manual_knee_rt), width=widget_width-status_width, height=widget_height)
		cmds.rowLayout(width=status_width)
		cmds.iconTextButton('btn_ik_fk_switcher_auto_manual_knee_lt_status', style='textOnly', label='>', font='boldLabelFont', width=status_width-2, height=widget_height-2, enable=False)
		cmds.setParent(upLevel=True)
		cmds.button('btn_ik_fk_switcher_auto_manual_knee_lt', label='Loading...', command=partial(self.ik_fk_switcher_auto_manual_knee_lt), width=widget_width-status_width, height=widget_height)
		cmds.setParent(upLevel=True)

		cmds.setParent(upLevel=True)
		cmds.setParent(upLevel=True)

	def _create_save_load_poses_panel(self):
		frame_width = self._SIZE_FRAME_WIDTH
		widget_width = self._SIZE_WIDGET_WIDTH
		widget_height = self._SIZE_WIDGET_HEIGHT

		cmds.frameLayout(self._util.to_ui_name('frm_pose_controls'), label='Save / Load Poses', borderStyle='etchedOut', collapsable=True, collapse=True, enable=False, width=frame_width)

		cmds.columnLayout(self._LAYOUT_POSES, width=widget_width*2)
		cmds.setParent(upLevel=True)

		cmds.setParent(upLevel=True)

	def _create_save_load_poses_content(self, *args):
		parent_widget = self._LAYOUT_POSES
		frame_width = self._SIZE_FRAME_WIDTH
		widget_width = self._SIZE_WIDGET_WIDTH
		widget_height = self._SIZE_WIDGET_HEIGHT

		# Delete any existing UI content
		child_controls = cmds.columnLayout(parent_widget, query=True, childArray=True)
		if child_controls is not None:
			cmds.deleteUI(child_controls)

		num_of_poses = int(self._get_num_of_poses())
		poses_per_group = self._get_poses_per_group()
		num_of_groups = 0

		if poses_per_group != 'None':
			poses_per_group = int(poses_per_group)
			num_of_groups = num_of_poses / poses_per_group

		if num_of_groups > 1:
			# Groups
			for group_idx in range(0, num_of_groups):
				pose_idx_start = group_idx * poses_per_group + 1
				pose_idx_end = group_idx * poses_per_group + poses_per_group

				# Group name
				group_name = 'Poses #$start - $end' \
					.replace('$start', str(pose_idx_start)) \
					.replace('$end', str(pose_idx_end))

				# Widget names
				pose_group_id = '$start_$end'.replace('$start', str(pose_idx_start)).replace('$end', str(pose_idx_end))
				frm_pose_group_rename = 'frm_pose_group_rename' + pose_group_id
				mnu_pose_group_rename = self._save_load_poses_get_menu_name('pose_group', 'rename', pose_group_id)

				# Frame and frame context menu widget
				cmds.frameLayout(frm_pose_group_rename, parent=parent_widget, label=group_name, borderStyle='etchedOut', collapsable=True, collapse=True, width=frame_width-3)
				frm_menu_rename = cmds.popupMenu(parent=frm_pose_group_rename, button=3)
				cmds.menuItem(mnu_pose_group_rename, parent=frm_menu_rename, label='Loading...', command=partial(self.rename_pose_group, pose_idx_start, pose_idx_end))

				# Save / Rename / Load buttons
				cmds.rowColumnLayout(numberOfColumns=3)
				cmds.evalDeferred(partial(self._save_load_poses_update_pose_group_names, pose_idx_start, pose_idx_end))

				for pose_idx in range(pose_idx_start, pose_idx_end + 1):
					self._create_save_load_poses_buttons(pose_idx)
					cmds.evalDeferred(partial(self._save_load_poses_update_pose_names, pose_idx))

				cmds.setParent(upLevel=True)
				cmds.setParent(upLevel=True)
		else:
			# Save / Rename / Load buttons
			cmds.rowColumnLayout(parent=parent_widget)
			cmds.rowColumnLayout(numberOfColumns=3)

			for pose_idx in range(1, num_of_poses + 1):
				self._create_save_load_poses_buttons(pose_idx)
				cmds.evalDeferred(partial(self._save_load_poses_update_pose_names, pose_idx))

			cmds.setParent(upLevel=True)
			cmds.setParent(upLevel=True)

		# Reset To Bind Pose
		cmds.rowColumnLayout()
		cmds.rowColumnLayout(numberOfColumns=1)
		btn_reset_to_bind_pose = cmds.button('btn_reset_to_bind_pose', label='&Reset to Bind Pose', command=partial(self.reset_to_bind_pose), width=widget_width*2-1, height=widget_height)
		cmds.setParent(upLevel=True)
		cmds.setParent(upLevel=True)

		# Button context menu
		btn_menu_reset_to_bind_pose = cmds.popupMenu(parent=btn_reset_to_bind_pose, button=3)
		cmds.menuItem(parent=btn_menu_reset_to_bind_pose, label='Set as &new Bind Pose', command=partial(self.set_new_bind_pose))
		cmds.menuItem(parent=btn_menu_reset_to_bind_pose, divider=True)
		cmds.menuItem(parent=btn_menu_reset_to_bind_pose, label='Reset to &default', command=partial(self.reset_bind_pose_to_default))

	def _create_save_load_poses_buttons(self, pose_idx):
		widget_width = self._SIZE_WIDGET_WIDTH
		widget_height = self._SIZE_WIDGET_HEIGHT

		# Widget names
		btn_pose_save = 'btn_pose_save' + str(pose_idx)
		btn_pose_rename = 'btn_pose_rename' + str(pose_idx)
		btn_pose_load = 'btn_pose_load' + str(pose_idx)
		mnu_pose_save_rename = self._save_load_poses_get_menu_name('save', 'rename', pose_idx)
		mnu_pose_rename_rename = self._save_load_poses_get_menu_name('rename', 'rename', pose_idx)
		mnu_pose_load_rename = self._save_load_poses_get_menu_name('load', 'rename', pose_idx)
		mnu_pose_save_delete = self._save_load_poses_get_menu_name('save', 'delete', pose_idx)
		mnu_pose_rename_delete = self._save_load_poses_get_menu_name('rename', 'delete', pose_idx)
		mnu_pose_load_delete = self._save_load_poses_get_menu_name('load', 'delete', pose_idx)

		# Button widgets
		cmds.button(btn_pose_save, label='Save', command=partial(self.save_ctrl_pose, pose_idx, verbose = True), width=widget_width/2.5, height=widget_height)
		cmds.button(btn_pose_rename, label='Loading...', command=partial(self.rename_pose_name, pose_idx), width=widget_width*1.19, height=widget_height)
		cmds.button(btn_pose_load, label='Load', command=partial(self.load_ctrl_pose, pose_idx, verbose = True), width=widget_width/2.5, height=widget_height)

		# Button context menu widgets
		btn_menu_save = cmds.popupMenu(parent=btn_pose_save, button=3)
		cmds.menuItem(mnu_pose_save_rename, parent=btn_menu_save, label='Loading...', command=partial(self.rename_pose_name, pose_idx))
		cmds.menuItem(parent=btn_menu_save, divider=True)
		cmds.menuItem(mnu_pose_save_delete, parent=btn_menu_save, label='Loading...', command=partial(self.delete_ctrl_pose, pose_idx))

		btn_menu_rename = cmds.popupMenu(parent=btn_pose_rename, button=3)
		cmds.menuItem(mnu_pose_rename_rename, parent=btn_menu_rename, label='Loading...', command=partial(self.rename_pose_name, pose_idx))
		cmds.menuItem(parent=btn_menu_rename, divider=True)
		cmds.menuItem(mnu_pose_rename_delete, parent=btn_menu_rename, label='Loading...', command=partial(self.delete_ctrl_pose, pose_idx))

		btn_menu_load = cmds.popupMenu(parent=btn_pose_load, button=3)
		cmds.menuItem(mnu_pose_load_rename, parent=btn_menu_load, label='Loading...', command=partial(self.rename_pose_name, pose_idx))
		cmds.menuItem(parent=btn_menu_load, divider=True)
		cmds.menuItem(mnu_pose_load_delete, parent=btn_menu_load, label='Loading...', command=partial(self.delete_ctrl_pose, pose_idx))

	def _create_fbx_export_panel(self):
		self._fbxExportUI.create_panel(self._SIZE_FRAME_WIDTH)

	def _create_advanced_panel(self):
		frame_width = self._SIZE_FRAME_WIDTH
		widget_width = self._SIZE_WIDGET_WIDTH / 1.66
		widget_height = self._SIZE_WIDGET_HEIGHT / 1.33
		label_width = self._SIZE_WIDGET_WIDTH * 0.80

		cmds.frameLayout(self._util.to_ui_name('frm_advanced_controls'), label='Advanced', borderStyle='etchedOut', collapsable=True, collapse=True, enable=False, width=frame_width)
		cmds.columnLayout()

		cmds.rowColumnLayout(numberOfColumns=3, rowSpacing=[1, 2])
		# Euler Filter
		cmds.text(label='Run Euler Filter ', align='right', width=label_width, height=widget_height)
		cmds.button(label='Selected', command=partial(self.euler_filter, 'selected'), width=widget_width)
		cmds.button(label='All', command=partial(self.euler_filter, 'all'), width=widget_width)
		cmds.setParent(upLevel=True)

		cmds.rowColumnLayout(numberOfColumns=2, rowSpacing=[1, 2])
		# Rotation Interpolation
		cmds.text(label='Rotation Interp ', align='right', width=label_width, height=widget_height)
		cmds.optionMenu(self._util.to_ui_name('opt_rotation_interp'), label='', changeCommand=partial(self.update_rotation_interpolation), width=widget_width*2)
		for label, annotation in zip(self._ROTATION_INTERPOLATION_LABELS, self._ROTATION_INTERPOLATION_ANNOTATIONS):
			cmds.menuItem(label=label, annotation=annotation)
		cmds.setParent(upLevel=True)

		cmds.rowColumnLayout(numberOfColumns=4)
		# FPS
		cmds.text(label='FPS ', align='right', width=label_width, height=widget_height)
		cmds.button(label='30', command=partial(self.set_fps, 'ntsc'), width=widget_width*2/3)
		cmds.button(label='60', command=partial(self.set_fps, 'ntscf'), width=widget_width*2/3)
		cmds.button(label='120', command=partial(self.set_fps, '120fps'), width=widget_width*2/3)
		cmds.setParent(upLevel=True)

		cmds.rowColumnLayout(numberOfColumns=3, rowSpacing=[1, 2])
		# Up Axis
		cmds.text(label='Up Axis ', align='right', width=label_width, height=widget_height)
		cmds.button(label='Y-Up', command=partial(self.y_up_axis), width=widget_width)
		cmds.button(label='Z-Up', command=partial(self.z_up_axis), width=widget_width)

		# Controls Scaling
		cmds.text(label='Control Scale ', align='right', width=label_width, height=widget_height)
		custom_layer_widgets = []
		cmds.button(label='+', command=partial(self.control_scale, 1.1), width=widget_width)
		cmds.button(label='-', command=partial(self.control_scale, 0.9), width=widget_width)

		# Controls Layer
		cmds.text(label='Controls Layer ', align='right', width=label_width, height=widget_height)
		custom_layer_widgets = []
		custom_layer_widgets.append(cmds.button(label='Add', command=partial(self.layer_ctrl_add), width=widget_width))
		custom_layer_widgets.append(cmds.button(label='Remove', command=partial(self.layer_ctrl_remove), width=widget_width))

		# Custom Layer widgets' context menu
		for widget in custom_layer_widgets:
			widget_menu = cmds.popupMenu(parent=widget, button=3)
			cmds.menuItem(parent=widget_menu, label='Select Objects', command=partial(self.layer_ctrl_select))
		cmds.setParent(upLevel=True)

		cmds.rowColumnLayout(numberOfColumns=2, rowSpacing=[1, 2])
		# Save / Load Poses Parameters
		# Num of Poses
		cmds.text(label='Poses ', align='right', width=label_width, height=widget_height)
		opt_num_of_poses_name = self._widgets.create('num_of_poses', 'optionMenu', 'num_of_poses', self._SETTINGS_CFG)
		cmds.optionMenu(opt_num_of_poses_name, label='', changeCommand=partial(self.update_num_of_poses), width=widget_width*2)
		cmds.menuItem(parent=opt_num_of_poses_name, label='5')
		step = 10
		for num_of_poses in range(step, self._NUM_OF_POSES_MAX + step, step):
			if num_of_poses > 100 and num_of_poses < 200:
				continue

			cmds.menuItem(parent=opt_num_of_poses_name, label=str(num_of_poses))

		# Poses per Group
		cmds.text(label='Poses / Group ', align='right', width=label_width, height=widget_height)
		opt_poses_per_group_name = self._widgets.create('poses_per_group', 'optionMenu', 'poses_per_group', self._SETTINGS_CFG)
		opt_poses_per_group = cmds.optionMenu(opt_poses_per_group_name, label='', changeCommand=partial(self.update_poses_per_group), width=widget_width*2)
		cmds.setParent(upLevel=True)

		cmds.rowColumnLayout(numberOfColumns=2)
		# Channel Box
		cmds.text(label='Channel Box ', align='right', width=label_width, height=widget_height)
		is_show_channel_box = self._settings.load(self._SHOW_CHANNEL_BOX_CFG, False)
		cmds.checkBox(self._WIDGET_CHK_SHOW_CHANNEL_BOX, label='', changeCommand=partial(self.show_hide_channel_box), value=is_show_channel_box)
		cmds.setParent(upLevel=True)

		cmds.rowColumnLayout(numberOfColumns=2)
		# Update Rig Matcher
		cmds.text(label='Rig Matcher ', align='right', width=label_width, height=widget_height)
		cmds.button(label='Update Defaults', command=partial(self.update_rig_matcher_defaults), width=widget_width*2)
		cmds.setParent(upLevel=True)

		cmds.setParent(upLevel=True)
		cmds.setParent(upLevel=True)

	def _ctrl_picker_create_button(self, rig_ctrl_key, btn_width = None, btn_height = None):
		widget = None

		rig_ctrl = self._rigControls.get_rig_control(rig_ctrl_key)
		ctrl_desc = rig_ctrl.get_desc()
		ctrl_color = rig_ctrl.get_color()
		ctrl_cmd = partial(self._ctrl_picker_select, rig_ctrl_key)

		for picker_name in rig_ctrl.get_pickers():
			if not cmds.button(picker_name, query=True, exists=True):
				if btn_width is not None and btn_height is not None:
					widget = cmds.button(picker_name, label='', annotation=ctrl_desc, command=ctrl_cmd, width=btn_width, height=btn_height, backgroundColor=ctrl_color)
				elif btn_width is not None:
					widget = cmds.button(picker_name, label='', annotation=ctrl_desc, command=ctrl_cmd, width=btn_width, backgroundColor=ctrl_color)
				elif btn_height is not None:
					widget = cmds.button(picker_name, label='', annotation=ctrl_desc, command=ctrl_cmd, height=btn_height, backgroundColor=ctrl_color)
				else:
					widget = cmds.button(picker_name, label='', annotation=ctrl_desc, command=ctrl_cmd, backgroundColor=ctrl_color)

				break

		return widget

	def _ctrl_picker_select(self, rig_ctrl_key, *args):
		if rig_ctrl_key == 'keyed':
			# Keyed controls only
			keyed_controls = []
			for rig_control_name in self._rigControls.get_rig_control_names():
				missing = False
				if not cmds.objExists(rig_control_name):
					# Skip rig controls that doesn't exist
					self._logger.warn('Rig control \'$rig_control\' not found.'.replace('$rig_control', rig_control_name))
					missing = True
					continue

				currentTime = cmds.currentTime(query=True)
				keyframeCount = cmds.keyframe(rig_control_name, time=(currentTime, currentTime), query=True, keyframeCount=True)

				if keyframeCount > 0:
					keyed_controls.append(rig_control_name)

			if missing:
				self._logger.command_message('Warn: Some rig controls were not found. See Script Editor for details.')

			if len(keyed_controls) > 0:
				cmds.select(keyed_controls, replace=True)
			else:
				cmds.select(clear=True)

			return
		elif rig_ctrl_key == 'all':
			# Select all controls
			self._util.select_obj(self._rigControls.get_rig_control_names(), replace = True)

			return

		mods = cmds.getModifiers()
		shift_mod = False
		ctrl_mod = False

		if (mods & 1) > 0:
			shift_mod = True
		if (mods & 4) > 0:
			ctrl_mod = True

		if not shift_mod:
			cmds.select(clear=True)

		ctrl_name = self._rigControls.get_rig_control(rig_ctrl_key).get_ctrl_name()
		if ctrl_mod:
			# Ctrl modifier = select both left and right controls (in correct order)
			ctrl_selection = []
			if RigControlName.LEFT_CONTROL in ctrl_name:
				ctrl_selection.append(ctrl_name.replace(RigControlName.LEFT_CONTROL, RigControlName.RIGHT_CONTROL))
			elif RigControlName.RIGHT_CONTROL in ctrl_name:
				ctrl_selection.append(ctrl_name.replace(RigControlName.RIGHT_CONTROL, RigControlName.LEFT_CONTROL))
			ctrl_selection.append(ctrl_name)
			cmds.select(ctrl_selection, add=True)
		else:
			# Toggle selection
			self._util.select_obj(ctrl_name, toggle = True)

	def _ctrl_picker_highlight_selection(self, *args):
		selected_objs = cmds.ls(selection=True)

		for key in self._rigControls.get_rig_control_keys():
			rig_ctrl = self._rigControls.get_rig_control(key)
			rig_ctrl.update_color(selected_objs)

	def _panel_collapsed(self, settings_name, *args):
		self._settings.save(settings_name, True)

	def _panel_expanded(self, settings_name, *args):
		self._settings.save(settings_name, False)

	def _save_load_poses_update_pose_names(self, index = None, *args):
		num_of_poses = int(self._get_num_of_poses())

		# Save / Rename / Load Buttons
		for pose_idx in range(1, num_of_poses + 1):
			if index != None and index != pose_idx:
				continue

			# Pose names
			pose_name = self._settings.load_pose_name(pose_idx)
			label_rename = 'Rename ' + pose_name
			label_delete = 'Delete ' + pose_name

			# Widget names
			btn_pose_rename = 'btn_pose_rename' + str(pose_idx)
			mnu_pose_save_rename = self._save_load_poses_get_menu_name('save', 'rename', pose_idx)
			mnu_pose_rename_rename = self._save_load_poses_get_menu_name('rename', 'rename', pose_idx)
			mnu_pose_load_rename = self._save_load_poses_get_menu_name('load', 'rename', pose_idx)
			mnu_pose_save_delete = self._save_load_poses_get_menu_name('save', 'delete', pose_idx)
			mnu_pose_rename_delete = self._save_load_poses_get_menu_name('rename', 'delete', pose_idx)
			mnu_pose_load_delete = self._save_load_poses_get_menu_name('load', 'delete', pose_idx)

			# Button and button context menu widgets
			cmds.button(btn_pose_rename, edit=True, label=pose_name, annotation=pose_name)
			cmds.menuItem(mnu_pose_save_rename, edit=True, label=label_rename)
			cmds.menuItem(mnu_pose_rename_rename, edit=True, label=label_rename)
			cmds.menuItem(mnu_pose_load_rename, edit=True, label=label_rename)
			cmds.menuItem(mnu_pose_save_delete, edit=True, label=label_delete)
			cmds.menuItem(mnu_pose_rename_delete, edit=True, label=label_delete)
			cmds.menuItem(mnu_pose_load_delete, edit=True, label=label_delete)

	def _save_load_poses_update_pose_group_names(self, start = None, end = None, *args):
		num_of_poses = int(self._get_num_of_poses())
		poses_per_group = self._get_poses_per_group()
		num_of_groups = 0

		if poses_per_group != 'None':
			poses_per_group = int(poses_per_group)
			num_of_groups = num_of_poses / poses_per_group

		if num_of_groups > 1:
			# Groups
			for group_idx in range(0, num_of_groups):
				pose_idx_start = group_idx * poses_per_group + 1
				pose_idx_end = group_idx * poses_per_group + poses_per_group

				if start != None and end != None:
					if start != pose_idx_start or end != pose_idx_end:
						continue

				# Group name
				group_name = self._settings.load_pose_group_name(pose_idx_start, pose_idx_end) \
					.replace('$start', str(pose_idx_start)) \
					.replace('$end', str(pose_idx_end))

				# Widget names
				pose_group_id = '$start_$end'.replace('$start', str(pose_idx_start)).replace('$end', str(pose_idx_end))
				frm_pose_group_rename = 'frm_pose_group_rename' + pose_group_id
				mnu_pose_group_rename = self._save_load_poses_get_menu_name('pose_group', 'rename', pose_group_id)

				# Frame and frame context menu widget
				cmds.frameLayout(frm_pose_group_rename, edit=True, label=group_name, annotation=group_name)
				cmds.menuItem(mnu_pose_group_rename, edit=True, label='Rename ' + group_name)

	def _save_load_poses_get_menu_name(self, type, command, id):
		return 'mnu_$type_ctrl_pose_$command_$id' \
			.replace('$type', type) \
			.replace('$command', command) \
			.replace('$id', str(id))

	def _update_poses_per_group_items(self, num_of_poses_value):
		opt_poses_per_group_name = self._widgets.get('poses_per_group').get_names()[0]

		# Delete existing menu items
		menu_items = cmds.optionMenu(opt_poses_per_group_name, query=True, itemListLong=True)
		if menu_items:
			cmds.deleteUI(menu_items)

		# Add valid menu items
		opt_poses_per_group = cmds.optionMenu(opt_poses_per_group_name, edit=True)
		cmds.menuItem(parent=opt_poses_per_group, label='None')

		step = 5
		old_value = self._get_poses_per_group(True)
		old_value_exists = False

		for poses_per_group in range(step, self._POSES_PER_GROUP_MAX + step, step):
			if int(num_of_poses_value) % poses_per_group == 0 and int(num_of_poses_value) != poses_per_group:
				cmds.menuItem(parent=opt_poses_per_group, label=str(poses_per_group))
				if old_value == str(poses_per_group):
					old_value_exists = True

		# Try to re-select old selected value
		new_value = None
		if not old_value_exists:
			new_value = cmds.optionMenu(opt_poses_per_group_name, query=True, value=True)
		else:
			new_value = old_value

		self.update_poses_per_group(new_value)

	def _get_selected_ctrls(self, select_all = False):
		selected_ctrls = []

		custom_ctrls = self._get_custom_ctrls()

		if select_all:
			# All controls selected
			selected_ctrls = list(self._rigControls.get_rig_control_names())

			# Add custom controls to selection
			if custom_ctrls is not None:
				for custom_ctrl in custom_ctrls:
					selected_ctrls.append(custom_ctrl)
		else:
			# Get selected controls
			for selected_ctrl in cmds.ls(selection=True):
				if selected_ctrl in self._rigControls.get_rig_control_names():
					selected_ctrls.append(selected_ctrl)
				elif custom_ctrls is not None and selected_ctrl in custom_ctrls:
					selected_ctrls.append(selected_ctrl)

			# Select all when no controls are selected
			if len(selected_ctrls) == 0:
				selected_ctrls = list(self._rigControls.get_rig_control_names())

				# Add custom controls to selection
				if custom_ctrls is not None:
					for custom_ctrl in custom_ctrls:
						selected_ctrls.append(custom_ctrl)

		return selected_ctrls

	def _get_custom_layer(self):
		return self._util.to_node_name(self._CUSTOM_CONTROLS_LAYER)

	def _get_custom_ctrls(self):
		if self._validate_display_layer_name(self._get_custom_layer()) is not None:
			return None

		return cmds.editDisplayLayerMembers(self._get_custom_layer(), query=True)

	def _validate_display_layer_name(self, name):
		if not cmds.objExists(name):
			return 'Layer $name not found'.replace('$name', name)

		if not cmds.objectType(name, isType='displayLayer'):
			return 'Invalid layer $name'.replace('$name', name)

		return None

	def _get_num_of_poses(self, load_from_settings = False):
		if load_from_settings or self._num_of_poses_value is None:
			self._num_of_poses_value = self._widgets.get('num_of_poses').get_value(self._DEFAULT_NUM_OF_POSES)

		try:
			# Retrieve value from settings then convert to int
			value = int(self._num_of_poses_value)
		except ValueError:
			pass

		# Clamp value
		if value < self._NUM_OF_POSES_MIN:
			value = self._NUM_OF_POSES_MIN
		if value > self._NUM_OF_POSES_MAX:
			value = self._NUM_OF_POSES_MAX

		# Return as string
		return str(value)

	def _get_poses_per_group(self, load_from_settings = False):
		if load_from_settings or self._poses_per_group_value is None:
			self._poses_per_group_value = self._widgets.get('poses_per_group').get_value(self._DEFAULT_POSES_PER_GROUP)

		try:
			# Retrieve value from settings
			value = self._poses_per_group_value

			# Value should be either 'None' or a number in string
			if value is not 'None':
				# Conver to int
				value = int(value)
		except ValueError:
			# Set value to default
			value = self._DEFAULT_POSES_PER_GROUP

		# Clamp numeric value
		if type(value) in [int, long]:
			if value < self._POSES_PER_GROUP_MIN:
				value = self._POSES_PER_GROUP_MIN
			if value > self._POSES_PER_GROUP_MAX:
				value = self._POSES_PER_GROUP_MAX

		# Return value
		return str(value)

	def _get_obj_attr(self, attr_name, default_value = None):
		value = default_value

		obj_name = attr_name.rpartition('.')[0]
		if cmds.objExists(obj_name):
			value = cmds.getAttr(attr_name)

		return value


# LEFT ======================================================================

	def ik_fk_switcher_arm_lt(self, *args):
		is_match_ik_fk = cmds.checkBox(self._WIDGET_CHK_MATCH_IK_FK, query=True, value=True)

		if self._get_obj_attr(self._rcName.to_ctrl_lt(self._rcName.ARM_SETTINGS) + '.ikFkBlend', 0) == 0:
			if self._matcher.ik_fk_switcher_to_fk_arm_lt(match = is_match_ik_fk):
				self._logger.command_message('Left Arm FK mode')
		else:
			if self._matcher.ik_fk_switcher_to_ik_arm_lt(match = is_match_ik_fk):
				if self._get_obj_attr(self._rcName.to_ik_ctrl_lt(self._rcName.ELBOW) + '.fkElbowBlend', 0) == 0:
					self._logger.command_message('Left Arm IK mode (Elbow IK)')
				else:
					self._logger.command_message('Left Arm IK mode (Forearm FK)')

		self.refresh_widget_values()

	def ik_fk_switcher_lowerarm_lt(self, *args):
		is_match_ik_fk = cmds.checkBox(self._WIDGET_CHK_MATCH_IK_FK, query=True, value=True)

		if self._get_obj_attr(self._rcName.to_ik_ctrl_lt(self._rcName.ELBOW) + '.fkElbowBlend', 0) == 0:
			if self._matcher.ik_fk_switcher_to_fk_lowerarm_lt(match = is_match_ik_fk):
				self._logger.command_message('Left Arm IK mode (Forearm FK)')
		else:
			if self._matcher.ik_fk_switcher_to_ik_lowerarm_lt(match = is_match_ik_fk):
				self._logger.command_message('Left Arm IK mode (Elbow IK)')

		self.refresh_widget_values()

	def ik_fk_switcher_leg_lt(self, *args):
		is_match_ik_fk = cmds.checkBox(self._WIDGET_CHK_MATCH_IK_FK, query=True, value=True)

		if self._get_obj_attr(self._rcName.to_ctrl_lt(self._rcName.LEG_SETTINGS) + '.ikFkBlend', 0) == 0:
			if self._matcher.ik_fk_switcher_to_fk_leg_lt(match = is_match_ik_fk):
				self._logger.command_message('Left Leg FK mode')
		else:
			autoKnee = (self._get_obj_attr(self._rcName.to_ik_ctrl_lt(self._rcName.FOOT) + '.autoKneeBlend', 0) != 0)
			if self._matcher.ik_fk_switcher_to_ik_leg_lt(autoKnee, match = is_match_ik_fk):
				if autoKnee:
					self._logger.command_message('Left Leg IK mode (Auto Knee)')
				else:
					self._logger.command_message('Left Leg IK mode (Manual Knee)')

		self.refresh_widget_values()

	def ik_fk_switcher_auto_manual_knee_lt(self, *args):
		is_match_ik_fk = cmds.checkBox(self._WIDGET_CHK_MATCH_IK_FK, query=True, value=True)

		if self._get_obj_attr(self._rcName.to_ik_ctrl_lt(self._rcName.FOOT) + '.autoKneeBlend', 0) == 0:
			if self._matcher.ik_fk_switcher_to_auto_knee_lt(match = is_match_ik_fk):
				self._logger.command_message('Left Leg IK mode (Auto Knee)')
		else:
			if self._matcher.ik_fk_switcher_to_manual_knee_lt(match = is_match_ik_fk):
				self._logger.command_message('Left Leg IK mode (Manual Knee)')

		self.refresh_widget_values()


# RIGHT =====================================================================

	def ik_fk_switcher_arm_rt(self, *args):
		is_match_ik_fk = cmds.checkBox(self._WIDGET_CHK_MATCH_IK_FK, query=True, value=True)

		if self._get_obj_attr(self._rcName.to_ctrl_rt(self._rcName.ARM_SETTINGS) + '.ikFkBlend', 0) == 0:
			if self._matcher.ik_fk_switcher_to_fk_arm_rt(match = is_match_ik_fk):
				self._logger.command_message('Right Arm FK mode')
		else:
			if self._matcher.ik_fk_switcher_to_ik_arm_rt(match = is_match_ik_fk):
				if self._get_obj_attr(self._rcName.to_ik_ctrl_rt(self._rcName.ELBOW) + '.fkElbowBlend', 0) == 0:
					self._logger.command_message('Right Arm IK mode (Elbow IK)')
				else:
					self._logger.command_message('Right Arm IK mode (Forearm FK)')

		self.refresh_widget_values()

	def ik_fk_switcher_lowerarm_rt(self, *args):
		is_match_ik_fk = cmds.checkBox(self._WIDGET_CHK_MATCH_IK_FK, query=True, value=True)

		if self._get_obj_attr(self._rcName.to_ik_ctrl_rt(self._rcName.ELBOW) + '.fkElbowBlend', 0) == 0:
			if self._matcher.ik_fk_switcher_to_fk_lowerarm_rt(match = is_match_ik_fk):
				self._logger.command_message('Right Arm IK mode (Forearm FK)')
		else:
			if self._matcher.ik_fk_switcher_to_ik_lowerarm_rt(match = is_match_ik_fk):
				self._logger.command_message('Right Arm IK mode (Elbow IK)')

		self.refresh_widget_values()

	def ik_fk_switcher_leg_rt(self, *args):
		is_match_ik_fk = cmds.checkBox(self._WIDGET_CHK_MATCH_IK_FK, query=True, value=True)

		if self._get_obj_attr(self._rcName.to_ctrl_rt(self._rcName.LEG_SETTINGS) + '.ikFkBlend', 0) == 0:
			if self._matcher.ik_fk_switcher_to_fk_leg_rt(match = is_match_ik_fk):
				self._logger.command_message('Right Leg FK mode')
		else:
			autoKnee = (self._get_obj_attr(self._rcName.to_ik_ctrl_rt(self._rcName.FOOT) + '.autoKneeBlend', 0) != 0)
			if self._matcher.ik_fk_switcher_to_ik_leg_rt(autoKnee, match = is_match_ik_fk):
				if autoKnee:
					self._logger.command_message('Right Leg IK mode (Auto Knee)')
				else:
					self._logger.command_message('Right Leg IK mode (Manual Knee)')

		self.refresh_widget_values()

	def ik_fk_switcher_auto_manual_knee_rt(self, *args):
		is_match_ik_fk = cmds.checkBox(self._WIDGET_CHK_MATCH_IK_FK, query=True, value=True)

		if self._get_obj_attr(self._rcName.to_ik_ctrl_rt(self._rcName.FOOT) + '.autoKneeBlend', 0) == 0:
			if self._matcher.ik_fk_switcher_to_auto_knee_rt(match = is_match_ik_fk):
				self._logger.command_message('Right Leg IK mode (Auto Knee)')
		else:
			if self._matcher.ik_fk_switcher_to_manual_knee_rt(match = is_match_ik_fk):
				self._logger.command_message('Right Leg IK mode (Manual Knee)')

		self.refresh_widget_values()
