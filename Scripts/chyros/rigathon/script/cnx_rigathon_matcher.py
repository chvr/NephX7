import maya.cmds as cmds

from cnx_rigathon_logger import Logger

class Matcher:

	_ITERATION_LIMIT = 10000
	_INITIAL_KNEE_TWIST_INTERVAL = 90.0

	def __init__(self, settings, util, rigControlName):
		self._logger = Logger(self.__class__.__name__)
		self._settings = settings
		self._util = util
		self._rcName = rigControlName

	def init_rig_defaults(self, character_name):
		self._util.disable_undo()
		try:
			section = self._util.to_matcher_category()
			sub_section = self._util.to_matcher_name(character_name)

			# Left
			self._settings.save('upperarm_lt_length', cmds.getAttr(self._rcName.to_result_name_lt(self._rcName.LOWERARM) + '.translateX'), section = section, sub_section = sub_section)
			self._settings.save('lowerarm_lt_length', cmds.getAttr(self._rcName.to_result_name_lt(self._rcName.HAND) + '.translateX'), section = section, sub_section = sub_section)
			self._settings.save('thigh_lt_length', cmds.getAttr(self._rcName.to_result_name_lt(self._rcName.CALF) + '.translateX'), section = section, sub_section = sub_section)
			self._settings.save('calf_lt_length', cmds.getAttr(self._rcName.to_result_name_lt(self._rcName.FOOT) + '.translateX'), section = section, sub_section = sub_section)

			# Right
			self._settings.save('upperarm_rt_length', cmds.getAttr(self._rcName.to_result_name_rt(self._rcName.LOWERARM) + '.translateX'), section = section, sub_section = sub_section)
			self._settings.save('lowerarm_rt_length', cmds.getAttr(self._rcName.to_result_name_rt(self._rcName.HAND) + '.translateX'), section = section, sub_section = sub_section)
			self._settings.save('thigh_rt_length', cmds.getAttr(self._rcName.to_result_name_rt(self._rcName.CALF) + '.translateX'), section = section, sub_section = sub_section)
			self._settings.save('calf_rt_length', cmds.getAttr(self._rcName.to_result_name_rt(self._rcName.FOOT) + '.translateX'), section = section, sub_section = sub_section)
		finally:
			self._util.enable_undo()

	def _angle_to_value(self, source_node, target_angle, attribute, delta_value, center_vector, zero_vector):
		count = 0
		value = delta_value

		while count < self._ITERATION_LIMIT:
			count += 1

			# Update attribute with new value
			cmds.setAttr(attribute, value)

			# Check if target angle of the source node has been met
			current_vector = cmds.xform(source_node, query=True, worldSpace=True, translation=True)
			center_to_current_vector = [current_vector[0] - center_vector[0], current_vector[1] - center_vector[1], current_vector[2] - center_vector[2]]

			# Get new angle result
			current_angle = cmds.angleBetween(vector1=[center_to_current_vector[0], center_to_current_vector[1], center_to_current_vector[2]], vector2=[zero_vector[0], zero_vector[1], zero_vector[2]])

			tolerance = 0.01
			if abs(current_angle[3] - target_angle) < tolerance:
				self._logger.debug('Match found. Iterations: ' + str(count))
				return value
			else:
				delta_value = delta_value / 2
				# Change value (bifurcation)
				if current_angle[3] > target_angle:
					value = value - delta_value
				else:
					value = value + delta_value

		self._logger.debug('Match not found. Iterations: ' + str(count))
		return value


# LEFT ======================================================================

	def _get_upperarm_lt_length(self):
		length = self._settings.load('upperarm_lt_length', None, section = self._util.to_matcher_category(), sub_section = self._util.to_matcher_name(self._settings.get_ref_name()))
		if length is None:
			length = cmds.getAttr(self._rcName.to_result_name_lt(self._rcName.LOWERARM) + '.translateX')
			self._logger.warn('No matcher settings found - matcher may fail.')

		return length

	def _get_lowerarm_lt_length(self):
		length = self._settings.load('lowerarm_lt_length', None, section = self._util.to_matcher_category(), sub_section = self._util.to_matcher_name(self._settings.get_ref_name()))
		if length is None:
			length = cmds.getAttr(self._rcName.to_result_name_lt(self._rcName.HAND) + '.translateX')
			self._logger.warn('No matcher settings found - matcher may fail.')

		return length

	def _get_thigh_lt_length(self):
		length = self._settings.load('thigh_lt_length', None, section = self._util.to_matcher_category(), sub_section = self._util.to_matcher_name(self._settings.get_ref_name()))
		if length is None:
			length = cmds.getAttr(self._rcName.to_result_name_lt(self._rcName.CALF) + '.translateX')
			self._logger.warn('No matcher settings found - matcher may fail.')

		return length

	def _get_calf_lt_length(self):
		length = self._settings.load('calf_lt_length', None, section = self._util.to_matcher_category(), sub_section = self._util.to_matcher_name(self._settings.get_ref_name()))
		if length is None:
			length = cmds.getAttr(self._rcName.to_result_name_lt(self._rcName.FOOT) + '.translateX')
			self._logger.warn('No matcher settings found - matcher may fail.')

		return length


# RIGHT =====================================================================

	def _get_upperarm_rt_length(self):
		length = self._settings.load('upperarm_rt_length', None, section = self._util.to_matcher_category(), sub_section = self._util.to_matcher_name(self._settings.get_ref_name()))
		if length is None:
			length = cmds.getAttr(self._rcName.to_result_name_rt(self._rcName.LOWERARM) + '.translateX')
			self._logger.warn('No matcher settings found - matcher may fail.')

		return length

	def _get_lowerarm_rt_length(self):
		length = self._settings.load('lowerarm_rt_length', None, section = self._util.to_matcher_category(), sub_section = self._util.to_matcher_name(self._settings.get_ref_name()))
		if length is None:
			length = cmds.getAttr(self._rcName.to_result_name_rt(self._rcName.HAND) + '.translateX')
			self._logger.warn('No matcher settings found - matcher may fail.')

		return length

	def _get_thigh_rt_length(self):
		length = self._settings.load('thigh_rt_length', None, section = self._util.to_matcher_category(), sub_section = self._util.to_matcher_name(self._settings.get_ref_name()))
		if length is None:
			length = cmds.getAttr(self._rcName.to_result_name_rt(self._rcName.CALF) + '.translateX')
			self._logger.warn('No matcher settings found - matcher may fail.')

		return length

	def _get_calf_rt_length(self):
		length = self._settings.load('calf_rt_length', None, section = self._util.to_matcher_category(), sub_section = self._util.to_matcher_name(self._settings.get_ref_name()))
		if length is None:
			length = cmds.getAttr(self._rcName.to_result_name_rt(self._rcName.FOOT) + '.translateX')
			self._logger.warn('No matcher settings found - matcher may fail.')

		return length


# LEFT ======================================================================

	def ik_fk_switcher_to_ik_arm_lt(self, match = True, fk_elbow_mode = None):
		try:
			if not match:
				# Don't match IK / FK
				cmds.setAttr(self._rcName.to_ctrl_lt(self._rcName.ARM_SETTINGS) + '.ikFkBlend', 0)

				if fk_elbow_mode is not None:
					# Set FK Elbow Mode value
					fk_elbow_value = 0
					if fk_elbow_mode:
						fk_elbow_value = 1
					cmds.setAttr(self._rcName.to_ik_ctrl_lt(self._rcName.ELBOW) + '.fkElbowBlend', fk_elbow_value)

				return True

			if fk_elbow_mode is None:
				# Get FK Elbow Mode value
				fk_elbow_blend = cmds.getAttr(self._rcName.to_ik_ctrl_lt(self._rcName.ELBOW) + '.fkElbowBlend')
				fk_elbow_mode = (fk_elbow_blend >= 0.5)

			# Get arm lengths
			current_upperarm_length = cmds.getAttr(self._rcName.to_result_name_lt(self._rcName.LOWERARM) + '.translateX')
			current_lowerarm_length = cmds.getAttr(self._rcName.to_result_name_lt(self._rcName.HAND) + '.translateX')

			tolerance = 0.001
			if abs(current_upperarm_length - self._get_upperarm_lt_length()) > tolerance or \
				abs(current_lowerarm_length - self._get_lowerarm_lt_length()) > tolerance:
					# Enable IK Arm Stretch
					cmds.setAttr(self._rcName.to_ik_ctrl_lt(self._rcName.WRIST) + '.stretch', 1)
					if not fk_elbow_mode:
						# Enable Elbow Snap
						cmds.setAttr(self._rcName.to_ik_ctrl_lt(self._rcName.ELBOW) + '.elbowSnap', 1)

			if not fk_elbow_mode:
				# IK Wrist transforms / rotations
				t_ik_wrist = cmds.xform(self._rcName.to_ik_ctrl_lt(self._rcName.WRIST), query=True, worldSpace=True, translation=True)
				t_result_hand = cmds.xform(self._rcName.to_result_name_lt(self._rcName.HAND), query=True, worldSpace=True, translation=True)
				t_ik_wrist_wrp = cmds.xform(self._rcName.to_ik_ctrl_lt(self._rcName.WRIST), query=True, worldSpace=True, rotatePivot=True)
				t_ik_wrist[0] = t_ik_wrist[0] + t_result_hand[0] - t_ik_wrist_wrp[0]
				t_ik_wrist[1] = t_ik_wrist[1] + t_result_hand[1] - t_ik_wrist_wrp[1]
				t_ik_wrist[2] = t_ik_wrist[2] + t_result_hand[2] - t_ik_wrist_wrp[2]
				r_ik_wrist = cmds.xform(self._rcName.to_ik_snap_grp_lt(self._rcName.WRIST), query=True, worldSpace=True, rotation=True)

				# IK Elbow transforms
				t_ik_elbow = cmds.xform(self._rcName.to_ik_ctrl_lt(self._rcName.ELBOW), query=True, worldSpace=True, translation=True)
				t_result_lowerarm = cmds.xform(self._rcName.to_result_name_lt(self._rcName.LOWERARM), query=True, worldSpace=True, translation=True)
				t_ik_elbow_wrp = cmds.xform(self._rcName.to_ik_ctrl_lt(self._rcName.ELBOW), query=True, worldSpace=True, rotatePivot=True)
				t_ik_elbow[0] = t_ik_elbow[0] + t_result_lowerarm[0] - t_ik_elbow_wrp[0]
				t_ik_elbow[1] = t_ik_elbow[1] + t_result_lowerarm[1] - t_ik_elbow_wrp[1]
				t_ik_elbow[2] = t_ik_elbow[2] + t_result_lowerarm[2] - t_ik_elbow_wrp[2]

				# Update IK arm settings, transforms, and rotations
				cmds.setAttr(self._rcName.to_ik_ctrl_lt(self._rcName.ELBOW) + '.fkElbowBlend', 0)

				cmds.xform(self._rcName.to_ik_ctrl_lt(self._rcName.WRIST), worldSpace=True, rotation=[r_ik_wrist[0], r_ik_wrist[1], r_ik_wrist[2]])
				cmds.xform(self._rcName.to_ik_ctrl_lt(self._rcName.WRIST), worldSpace=True, translation=[t_ik_wrist[0], t_ik_wrist[1], t_ik_wrist[2]])
				cmds.xform(self._rcName.to_ik_ctrl_lt(self._rcName.ELBOW), worldSpace=True, translation=[t_ik_elbow[0], t_ik_elbow[1], t_ik_elbow[2]])
			else:
				# IK Elbow transforms
				t_ik_elbow = cmds.xform(self._rcName.to_ik_ctrl_lt(self._rcName.ELBOW), query=True, worldSpace=True, translation=True)
				t_result_lowerarm = cmds.xform(self._rcName.to_result_name_lt(self._rcName.LOWERARM), query=True, worldSpace=True, translation=True)
				t_ik_elbow_wrp = cmds.xform(self._rcName.to_ik_ctrl_lt(self._rcName.ELBOW), query=True, worldSpace=True, rotatePivot=True)
				t_ik_elbow[0] = t_ik_elbow[0] + t_result_lowerarm[0] - t_ik_elbow_wrp[0]
				t_ik_elbow[1] = t_ik_elbow[1] + t_result_lowerarm[1] - t_ik_elbow_wrp[1]
				t_ik_elbow[2] = t_ik_elbow[2] + t_result_lowerarm[2] - t_ik_elbow_wrp[2]

				# FK arm rotations
				r_fk_elbow_lowerarm = cmds.xform(self._rcName.to_fk_snap_name_lt(self._rcName.LOWERARM), query=True, worldSpace=True, rotation=True)
				r_fk_elbow_hand = cmds.xform(self._rcName.to_fk_snap_name_lt(self._rcName.HAND), query=True, worldSpace=True, rotation=True)

				# Calculate arm lengths
				lowerarm_length_factor = abs(current_lowerarm_length / self._get_lowerarm_lt_length())

				# Update IK/FK arm settings, length, transforms, and rotations
				cmds.setAttr(self._rcName.to_ik_ctrl_lt(self._rcName.ELBOW) + '.elbowSnap', 1)
				cmds.setAttr(self._rcName.to_ik_ctrl_lt(self._rcName.ELBOW) + '.fkElbowBlend', 1)

				cmds.xform(self._rcName.to_ik_ctrl_lt(self._rcName.ELBOW), worldSpace=True, translation=[t_ik_elbow[0], t_ik_elbow[1], t_ik_elbow[2]])
				cmds.xform(self._rcName.to_fk_ctrl_lt(self._rcName.ELBOW_LOWERARM), worldSpace=True, rotation=[r_fk_elbow_lowerarm[0], r_fk_elbow_lowerarm[1], r_fk_elbow_lowerarm[2]])
				cmds.xform(self._rcName.to_fk_ctrl_lt(self._rcName.ELBOW_HAND), worldSpace=True, rotation=[r_fk_elbow_hand[0], r_fk_elbow_hand[1], r_fk_elbow_hand[2]])

				cmds.setAttr(self._rcName.to_fk_ctrl_lt(self._rcName.ELBOW_LOWERARM) + '.length', lowerarm_length_factor)

			cmds.setAttr(self._rcName.to_ctrl_lt(self._rcName.ARM_SETTINGS) + '.ikFkBlend', 0)

			return True
		except (ValueError, RuntimeError) as e:
			self._logger.error('Failed to switch IK / FK: ' + str(e))
			self._logger.command_message('Warn: Failed to switch IK / FK. See Script Editor for details.')

			return False

	def ik_fk_switcher_to_fk_arm_lt(self, match = True):
		try:
			if not match:
				# Don't match IK / FK
				cmds.setAttr(self._rcName.to_ctrl_lt(self._rcName.ARM_SETTINGS) + '.ikFkBlend', 1)
				return True

			# Calculate arm lengths
			current_upperarm_length = cmds.getAttr(self._rcName.to_result_name_lt(self._rcName.LOWERARM) + '.translateX')
			current_lowerarm_length = cmds.getAttr(self._rcName.to_result_name_lt(self._rcName.HAND) + '.translateX')
			upperarm_length_factor = abs(current_upperarm_length / self._get_upperarm_lt_length())
			lowerarm_length_factor = abs(current_lowerarm_length / self._get_lowerarm_lt_length())

			# Get FK arm rotations
			r_fk_upperarm = cmds.xform(self._rcName.to_fk_snap_name_lt(self._rcName.UPPERARM), query=True, worldSpace=True, rotation=True)
			r_fk_lowerarm = cmds.xform(self._rcName.to_fk_snap_name_lt(self._rcName.LOWERARM), query=True, worldSpace=True, rotation=True)
			r_fk_hand = cmds.xform(self._rcName.to_fk_snap_name_lt(self._rcName.HAND), query=True, worldSpace=True, rotation=True)

			# Update IK arm settings, length, and rotations
			cmds.setAttr(self._rcName.to_fk_ctrl_lt(self._rcName.UPPERARM) + '.length', upperarm_length_factor)
			cmds.setAttr(self._rcName.to_fk_ctrl_lt(self._rcName.LOWERARM) + '.length', lowerarm_length_factor)

			cmds.setAttr(self._rcName.to_ctrl_lt(self._rcName.ARM_GIMBAL) + '.rotate', 0.0, 0.0, 0.0)
			cmds.xform(self._rcName.to_fk_ctrl_lt(self._rcName.UPPERARM), worldSpace=True, rotation=[r_fk_upperarm[0], r_fk_upperarm[1], r_fk_upperarm[2]])
			cmds.xform(self._rcName.to_fk_ctrl_lt(self._rcName.LOWERARM), worldSpace=True, rotation=[r_fk_lowerarm[0], r_fk_lowerarm[1], r_fk_lowerarm[2]])
			cmds.xform(self._rcName.to_fk_ctrl_lt(self._rcName.HAND), worldSpace=True, rotation=[r_fk_hand[0], r_fk_hand[1], r_fk_hand[2]])

			cmds.setAttr(self._rcName.to_ctrl_lt(self._rcName.ARM_SETTINGS) + '.ikFkBlend', 1)

			return True
		except (ValueError, RuntimeError) as e:
			self._logger.error('Failed to switch IK / FK: ' + str(e))
			self._logger.command_message('Warn: Failed to switch IK / FK. See Script Editor for details.')

			return False

	def ik_fk_switcher_to_ik_lowerarm_lt(self, match = True):
		return self.ik_fk_switcher_to_ik_arm_lt(match = match, fk_elbow_mode = False)

	def ik_fk_switcher_to_fk_lowerarm_lt(self, match = True):
		return self.ik_fk_switcher_to_ik_arm_lt(match = match, fk_elbow_mode = True)

	def ik_fk_switcher_to_ik_leg_lt(self, auto_knee_mode = None, match = True):
		try:
			if not match:
				# Don't match IK / FK
				cmds.setAttr(self._rcName.to_ctrl_lt(self._rcName.LEG_SETTINGS) + '.ikFkBlend', 0)

				if auto_knee_mode is not None:
					# Set Auto Knee Mode value
					auto_knee_value = 0
					if auto_knee_mode:
						auto_knee_value = 1
					cmds.setAttr(self._rcName.to_ik_ctrl_lt(self._rcName.FOOT) + '.autoKneeBlend', auto_knee_value)

				return True

			if auto_knee_mode is None:
				# Get Auto Knee Mode value
				auto_knee_blend = cmds.getAttr(self._rcName.to_ik_ctrl_lt(self._rcName.FOOT) + '.autoKneeBlend')
				auto_knee_mode = (auto_knee_blend >= 0.5)

			# Get leg lengths
			current_thigh_length = cmds.getAttr(self._rcName.to_result_name_lt(self._rcName.CALF) + '.translateX')
			current_calf_length = cmds.getAttr(self._rcName.to_result_name_lt(self._rcName.FOOT) + '.translateX')

			tolerance = 0.001
			if abs(current_thigh_length - self._get_thigh_lt_length()) > tolerance or \
				abs(current_calf_length - self._get_calf_lt_length()) > tolerance:
					cmds.setAttr(self._rcName.to_ik_ctrl_lt(self._rcName.KNEE) + '.kneeSnap', 1)
					cmds.setAttr(self._rcName.to_ik_ctrl_lt(self._rcName.FOOT) + '.stretch', 1)

			# IK Foot transforms / rotations
			t_ik_foot = cmds.xform(self._rcName.to_ik_ctrl_lt(self._rcName.FOOT), query=True, worldSpace=True, translation=True)
			t_result_foot = cmds.xform(self._rcName.to_result_name_lt(self._rcName.FOOT), query=True, worldSpace=True, translation=True)
			t_ik_foot_wrp = cmds.xform(self._rcName.to_ik_ctrl_lt(self._rcName.FOOT), query=True, worldSpace=True, rotatePivot=True)
			t_ik_foot[0] = t_ik_foot[0] + t_result_foot[0] - t_ik_foot_wrp[0]
			t_ik_foot[1] = t_ik_foot[1] + t_result_foot[1] - t_ik_foot_wrp[1]
			t_ik_foot[2] = t_ik_foot[2] + t_result_foot[2] - t_ik_foot_wrp[2]
			r_ik_foot = cmds.xform(self._rcName.to_ik_snap_grp_lt(self._rcName.FOOT), query=True, worldSpace=True, rotation=True)

			# Result Ball orientation
			orient_result_ball = cmds.getAttr(self._rcName.to_result_name_lt(self._rcName.BALL) + '.rotateZ')

			# Update IK leg settings, transforms, and rotations
			cmds.xform(self._rcName.to_ik_ctrl_lt(self._rcName.FOOT), worldSpace=True, rotation=[r_ik_foot[0], r_ik_foot[1], r_ik_foot[2]])
			cmds.xform(self._rcName.to_ik_ctrl_lt(self._rcName.FOOT), worldSpace=True, translation=[t_ik_foot[0], t_ik_foot[1], t_ik_foot[2]])

			cmds.setAttr(self._rcName.to_ik_ctrl_lt(self._rcName.FOOT) + '.toeWiggle', orient_result_ball)

			if not auto_knee_mode:
				# Manual Knee

				# IK knee transforms / rotations
				t_ik_knee = cmds.xform(self._rcName.to_ik_ctrl_lt(self._rcName.KNEE), query=True, worldSpace=True, translation=True)
				t_result_knee = cmds.xform(self._rcName.to_result_name_lt(self._rcName.CALF), query=True, worldSpace=True, translation=True)
				t_ik_knee_wrp = cmds.xform(self._rcName.to_ik_ctrl_lt(self._rcName.KNEE), query=True, worldSpace=True, rotatePivot=True)
				t_ik_knee[0] = t_ik_knee[0] + t_result_knee[0] - t_ik_knee_wrp[0]
				t_ik_knee[1] = t_ik_knee[1] + t_result_knee[1] - t_ik_knee_wrp[1]
				t_ik_knee[2] = t_ik_knee[2] + t_result_knee[2] - t_ik_knee_wrp[2]

				cmds.xform(self._rcName.to_ik_ctrl_lt(self._rcName.KNEE), worldSpace=True, translation=[t_ik_knee[0], t_ik_knee[1], t_ik_knee[2]])

				cmds.setAttr(self._rcName.to_ik_ctrl_lt(self._rcName.FOOT) + '.autoKneeBlend', 0)
			else:
				# Auto Knee

				# Calculate leg lengths
				leg_length_factor = cmds.getAttr(self._rcName.to_ik_nf_name_lt(self._rcName.CALF) + '_translateX.output') / self._get_thigh_lt_length()
				thigh_length_factor = current_thigh_length / (self._get_thigh_lt_length() * leg_length_factor)
				calf_length_factor = current_calf_length / (self._get_calf_lt_length() * leg_length_factor)

				cmds.setAttr(self._rcName.to_ik_ctrl_lt(self._rcName.FOOT) + '.autoKneeThighLength', thigh_length_factor)
				cmds.setAttr(self._rcName.to_ik_ctrl_lt(self._rcName.FOOT) + '.autoKneeCalfLength', calf_length_factor)

				# Knee Twist
				cmds.setAttr(self._rcName.to_ik_ctrl_lt(self._rcName.FOOT) + '.kneeTwist' , 0)

				vertex_a = cmds.xform(self._rcName.to_ik_nf_name_lt(self._rcName.CALF), query=True, worldSpace=True, translation=True)
				vertex_b = cmds.xform(self._rcName.to_result_name_lt(self._rcName.CALF), query=True, worldSpace=True, translation=True)
				origin = cmds.xform(self._rcName.to_ik_nf_name_lt(self._rcName.FOOT), query=True, worldSpace=True, translation=True)

				origin_to_vertex_a = [vertex_a[0] - origin[0], vertex_a[1] - origin[1], vertex_a[2] - origin[2]]
				origin_to_vertex_b = [vertex_b[0] - origin[0], vertex_b[1] - origin[1], vertex_b[2] - origin[2]]

				angle = cmds.angleBetween(vector1=[origin_to_vertex_a[0], origin_to_vertex_a[1], origin_to_vertex_a[2]], vector2=[origin_to_vertex_b[0], origin_to_vertex_b[1], origin_to_vertex_b[2]])

				knee_twist = self._angle_to_value(self._rcName.to_ik_nf_name_lt(self._rcName.CALF), angle[3], self._rcName.to_ik_ctrl_lt(self._rcName.FOOT) + '.kneeTwist', self._INITIAL_KNEE_TWIST_INTERVAL, origin, origin_to_vertex_a)
				vertex_a = cmds.xform(self._rcName.to_ik_nf_name_lt(self._rcName.CALF), query=True, worldSpace=True, translation=True)

				tolerance = 0.01
				if abs(vertex_a[0] - vertex_b[0]) > tolerance or \
					abs(vertex_a[1] - vertex_b[1]) > tolerance or \
					abs(vertex_a[2] - vertex_b[2]) > tolerance:
					cmds.setAttr(self._rcName.to_ik_ctrl_lt(self._rcName.FOOT) + '.kneeTwist', -1 * knee_twist)

				cmds.setAttr(self._rcName.to_ik_ctrl_lt(self._rcName.FOOT) + '.autoKneeBlend', 1)

			cmds.setAttr(self._rcName.to_ctrl_lt(self._rcName.LEG_SETTINGS) + '.ikFkBlend', 0)

			return True
		except (ValueError, RuntimeError) as e:
			self._logger.error('Failed to switch IK / FK: ' + str(e))
			self._logger.command_message('Warn: Failed to switch IK / FK. See Script Editor for details.')

			return False

	def ik_fk_switcher_to_fk_leg_lt(self, match = True):
		try:
			if not match:
				# Don't match IK / FK
				cmds.setAttr(self._rcName.to_ctrl_lt(self._rcName.LEG_SETTINGS) + '.ikFkBlend', 1)
				return False

			# Calculate leg length
			current_thigh_length = cmds.getAttr(self._rcName.to_result_name_lt(self._rcName.CALF) + '.translateX')
			current_calf_length = cmds.getAttr(self._rcName.to_result_name_lt(self._rcName.FOOT) + '.translateX')
			thigh_length_factor = abs(current_thigh_length / self._get_thigh_lt_length())
			calf_length_factor = abs(current_calf_length / self._get_calf_lt_length())

			# Get FK leg rotations
			r_fk_thigh = cmds.xform(self._rcName.to_fk_snap_name_lt(self._rcName.THIGH), query=True, worldSpace=True, rotation=True)
			r_fk_calf = cmds.xform(self._rcName.to_fk_snap_name_lt(self._rcName.CALF), query=True, worldSpace=True, rotation=True)
			r_fk_foot = cmds.xform(self._rcName.to_fk_snap_name_lt(self._rcName.FOOT), query=True, worldSpace=True, rotation=True)
			r_fk_ball = cmds.xform(self._rcName.to_fk_snap_name_lt(self._rcName.BALL), query=True, worldSpace=True, rotation=True)

			# Update FK leg settings, length, and rotations
			cmds.setAttr(self._rcName.to_fk_ctrl_lt(self._rcName.THIGH) + '.length', thigh_length_factor)
			cmds.setAttr(self._rcName.to_fk_ctrl_lt(self._rcName.CALF) + '.length', calf_length_factor)

			cmds.xform(self._rcName.to_fk_ctrl_lt(self._rcName.THIGH), worldSpace=True, rotation=[r_fk_thigh[0], r_fk_thigh[1], r_fk_thigh[2]])
			cmds.xform(self._rcName.to_fk_ctrl_lt(self._rcName.CALF), worldSpace=True, rotation=[r_fk_calf[0], r_fk_calf[1], r_fk_calf[2]])
			cmds.xform(self._rcName.to_fk_ctrl_lt(self._rcName.FOOT), worldSpace=True, rotation=[r_fk_foot[0], r_fk_foot[1], r_fk_foot[2]])
			cmds.xform(self._rcName.to_fk_ctrl_lt(self._rcName.BALL), worldSpace=True, rotation=[r_fk_ball[0], r_fk_ball[1], r_fk_ball[2]])

			cmds.setAttr(self._rcName.to_ctrl_lt(self._rcName.LEG_SETTINGS) + '.ikFkBlend', 1)

			return True
		except (ValueError, RuntimeError) as e:
			self._logger.error('Failed to switch IK / FK: ' + str(e))
			self._logger.command_message('Warn: Failed to switch IK / FK. See Script Editor for details.')

			return False

	def ik_fk_switcher_to_auto_knee_lt(self, match = True):
		return self.ik_fk_switcher_to_ik_leg_lt(auto_knee_mode = True, match = match)

	def ik_fk_switcher_to_manual_knee_lt(self, match = True):
		return self.ik_fk_switcher_to_ik_leg_lt(auto_knee_mode = False, match = match)


# RIGHT =====================================================================

	def ik_fk_switcher_to_ik_arm_rt(self, match = True, fk_elbow_mode = None):
		try:
			if not match:
				# Don't match IK / FK
				cmds.setAttr(self._rcName.to_ctrl_rt(self._rcName.ARM_SETTINGS) + '.ikFkBlend', 0)

				if fk_elbow_mode is not None:
					# Set FK Elbow Mode value
					fk_elbow_value = 0
					if fk_elbow_mode:
						fk_elbow_value = 1
					cmds.setAttr(self._rcName.to_ik_ctrl_rt(self._rcName.ELBOW) + '.fkElbowBlend', fk_elbow_value)

				return True

			if fk_elbow_mode is None:
				# Get FK Elbow Mode value
				fk_elbow_blend = cmds.getAttr(self._rcName.to_ik_ctrl_rt(self._rcName.ELBOW) + '.fkElbowBlend')
				fk_elbow_mode = (fk_elbow_blend >= 0.5)

			# Get arm lengths
			current_upperarm_length = cmds.getAttr(self._rcName.to_result_name_rt(self._rcName.LOWERARM) + '.translateX')
			current_lowerarm_length = cmds.getAttr(self._rcName.to_result_name_rt(self._rcName.HAND) + '.translateX')

			tolerance = 0.001
			if abs(current_upperarm_length - self._get_upperarm_rt_length()) > tolerance or \
				abs(current_lowerarm_length - self._get_lowerarm_rt_length()) > tolerance:
					# Enable IK Arm Stretch
					cmds.setAttr(self._rcName.to_ik_ctrl_rt(self._rcName.WRIST) + '.stretch', 1)
					if not fk_elbow_mode:
						# Enable Elbow Snap
						cmds.setAttr(self._rcName.to_ik_ctrl_rt(self._rcName.ELBOW) + '.elbowSnap', 1)

			if not fk_elbow_mode:
				# IK Wrist transforms / rotations
				t_ik_wrist = cmds.xform(self._rcName.to_ik_ctrl_rt(self._rcName.WRIST), query=True, worldSpace=True, translation=True)
				t_result_hand = cmds.xform(self._rcName.to_result_name_rt(self._rcName.HAND), query=True, worldSpace=True, translation=True)
				t_ik_wrist_wrp = cmds.xform(self._rcName.to_ik_ctrl_rt(self._rcName.WRIST), query=True, worldSpace=True, rotatePivot=True)
				t_ik_wrist[0] = t_ik_wrist[0] + t_result_hand[0] - t_ik_wrist_wrp[0]
				t_ik_wrist[1] = t_ik_wrist[1] + t_result_hand[1] - t_ik_wrist_wrp[1]
				t_ik_wrist[2] = t_ik_wrist[2] + t_result_hand[2] - t_ik_wrist_wrp[2]
				r_ik_wrist = cmds.xform(self._rcName.to_ik_snap_grp_rt(self._rcName.WRIST), query=True, worldSpace=True, rotation=True)

				# IK Elbow transforms
				t_ik_elbow = cmds.xform(self._rcName.to_ik_ctrl_rt(self._rcName.ELBOW), query=True, worldSpace=True, translation=True)
				t_result_lowerarm = cmds.xform(self._rcName.to_result_name_rt(self._rcName.LOWERARM), query=True, worldSpace=True, translation=True)
				t_ik_elbow_wrp = cmds.xform(self._rcName.to_ik_ctrl_rt(self._rcName.ELBOW), query=True, worldSpace=True, rotatePivot=True)
				t_ik_elbow[0] = t_ik_elbow[0] + t_result_lowerarm[0] - t_ik_elbow_wrp[0]
				t_ik_elbow[1] = t_ik_elbow[1] + t_result_lowerarm[1] - t_ik_elbow_wrp[1]
				t_ik_elbow[2] = t_ik_elbow[2] + t_result_lowerarm[2] - t_ik_elbow_wrp[2]

				# Update IK arm settings, transforms, and rotations
				cmds.setAttr(self._rcName.to_ik_ctrl_rt(self._rcName.ELBOW) + '.fkElbowBlend', 0)

				cmds.xform(self._rcName.to_ik_ctrl_rt(self._rcName.WRIST), worldSpace=True, rotation=[r_ik_wrist[0], r_ik_wrist[1], r_ik_wrist[2]])
				cmds.xform(self._rcName.to_ik_ctrl_rt(self._rcName.WRIST), worldSpace=True, translation=[t_ik_wrist[0], t_ik_wrist[1], t_ik_wrist[2]])
				cmds.xform(self._rcName.to_ik_ctrl_rt(self._rcName.ELBOW), worldSpace=True, translation=[t_ik_elbow[0], t_ik_elbow[1], t_ik_elbow[2]])
			else:
				# IK Elbow transforms
				t_ik_elbow = cmds.xform(self._rcName.to_ik_ctrl_rt(self._rcName.ELBOW), query=True, worldSpace=True, translation=True)
				t_result_lowerarm = cmds.xform(self._rcName.to_result_name_rt(self._rcName.LOWERARM), query=True, worldSpace=True, translation=True)
				t_ik_elbow_wrp = cmds.xform(self._rcName.to_ik_ctrl_rt(self._rcName.ELBOW), query=True, worldSpace=True, rotatePivot=True)
				t_ik_elbow[0] = t_ik_elbow[0] + t_result_lowerarm[0] - t_ik_elbow_wrp[0]
				t_ik_elbow[1] = t_ik_elbow[1] + t_result_lowerarm[1] - t_ik_elbow_wrp[1]
				t_ik_elbow[2] = t_ik_elbow[2] + t_result_lowerarm[2] - t_ik_elbow_wrp[2]

				# FK arm rotations
				r_fk_elbow_lowerarm = cmds.xform(self._rcName.to_fk_snap_name_rt(self._rcName.LOWERARM), query=True, worldSpace=True, rotation=True)
				r_fk_elbow_hand = cmds.xform(self._rcName.to_fk_snap_name_rt(self._rcName.HAND), query=True, worldSpace=True, rotation=True)

				# Calculate arm lengths
				lowerarm_length_factor = abs(current_lowerarm_length / self._get_lowerarm_rt_length())

				# Update IK/FK arm settings, length, transforms, and rotations
				cmds.setAttr(self._rcName.to_ik_ctrl_rt(self._rcName.ELBOW) + '.elbowSnap', 1)
				cmds.setAttr(self._rcName.to_ik_ctrl_rt(self._rcName.ELBOW) + '.fkElbowBlend', 1)

				cmds.xform(self._rcName.to_ik_ctrl_rt(self._rcName.ELBOW), worldSpace=True, translation=[t_ik_elbow[0], t_ik_elbow[1], t_ik_elbow[2]])
				cmds.xform(self._rcName.to_fk_ctrl_rt(self._rcName.ELBOW_LOWERARM), worldSpace=True, rotation=[r_fk_elbow_lowerarm[0], r_fk_elbow_lowerarm[1], r_fk_elbow_lowerarm[2]])
				cmds.xform(self._rcName.to_fk_ctrl_rt(self._rcName.ELBOW_HAND), worldSpace=True, rotation=[r_fk_elbow_hand[0], r_fk_elbow_hand[1], r_fk_elbow_hand[2]])

				cmds.setAttr(self._rcName.to_fk_ctrl_rt(self._rcName.ELBOW_LOWERARM) + '.length', lowerarm_length_factor)

			cmds.setAttr(self._rcName.to_ctrl_rt(self._rcName.ARM_SETTINGS) + '.ikFkBlend', 0)

			return True
		except (ValueError, RuntimeError) as e:
			self._logger.error('Failed to switch IK / FK: ' + str(e))
			self._logger.command_message('Warn: Failed to switch IK / FK. See Script Editor for details.')

			return False

	def ik_fk_switcher_to_fk_arm_rt(self, match = True):
		try:
			if not match:
				# Don't match IK / FK
				cmds.setAttr(self._rcName.to_ctrl_rt(self._rcName.ARM_SETTINGS) + '.ikFkBlend', 1)
				return True

			# Calculate arm lengths
			current_upperarm_length = cmds.getAttr(self._rcName.to_result_name_rt(self._rcName.LOWERARM) + '.translateX')
			current_lowerarm_length = cmds.getAttr(self._rcName.to_result_name_rt(self._rcName.HAND) + '.translateX')
			upperarm_length_factor = abs(current_upperarm_length / self._get_upperarm_rt_length())
			lowerarm_length_factor = abs(current_lowerarm_length / self._get_lowerarm_rt_length())

			# Get FK arm rotations
			r_fk_upperarm = cmds.xform(self._rcName.to_fk_snap_name_rt(self._rcName.UPPERARM), query=True, worldSpace=True, rotation=True)
			r_fk_lowerarm = cmds.xform(self._rcName.to_fk_snap_name_rt(self._rcName.LOWERARM), query=True, worldSpace=True, rotation=True)
			r_fk_hand = cmds.xform(self._rcName.to_fk_snap_name_rt(self._rcName.HAND), query=True, worldSpace=True, rotation=True)

			# Update IK arm settings, length, and rotations
			cmds.setAttr(self._rcName.to_fk_ctrl_rt(self._rcName.UPPERARM) + '.length', upperarm_length_factor)
			cmds.setAttr(self._rcName.to_fk_ctrl_rt(self._rcName.LOWERARM) + '.length', lowerarm_length_factor)

			cmds.setAttr(self._rcName.to_ctrl_rt(self._rcName.ARM_GIMBAL) + '.rotate', 0.0, 0.0, 0.0)
			cmds.xform(self._rcName.to_fk_ctrl_rt(self._rcName.UPPERARM), worldSpace=True, rotation=[r_fk_upperarm[0], r_fk_upperarm[1], r_fk_upperarm[2]])
			cmds.xform(self._rcName.to_fk_ctrl_rt(self._rcName.LOWERARM), worldSpace=True, rotation=[r_fk_lowerarm[0], r_fk_lowerarm[1], r_fk_lowerarm[2]])
			cmds.xform(self._rcName.to_fk_ctrl_rt(self._rcName.HAND), worldSpace=True, rotation=[r_fk_hand[0], r_fk_hand[1], r_fk_hand[2]])

			cmds.setAttr(self._rcName.to_ctrl_rt(self._rcName.ARM_SETTINGS) + '.ikFkBlend', 1)

			return True
		except (ValueError, RuntimeError) as e:
			self._logger.error('Failed to switch IK / FK: ' + str(e))
			self._logger.command_message('Warn: Failed to switch IK / FK. See Script Editor for details.')

			return False

	def ik_fk_switcher_to_ik_lowerarm_rt(self, match = True):
		return self.ik_fk_switcher_to_ik_arm_rt(match = match, fk_elbow_mode = False)

	def ik_fk_switcher_to_fk_lowerarm_rt(self, match = True):
		return self.ik_fk_switcher_to_ik_arm_rt(match = match, fk_elbow_mode = True)

	def ik_fk_switcher_to_ik_leg_rt(self, auto_knee_mode = None, match = True):
		try:
			if not match:
				# Don't match IK / FK
				cmds.setAttr(self._rcName.to_ctrl_rt(self._rcName.LEG_SETTINGS) + '.ikFkBlend', 0)

				if auto_knee_mode is not None:
					# Set Auto Knee Mode value
					auto_knee_value = 0
					if auto_knee_mode:
						auto_knee_value = 1
					cmds.setAttr(self._rcName.to_ik_ctrl_rt(self._rcName.FOOT) + '.autoKneeBlend', auto_knee_value)

				return True

			if auto_knee_mode is None:
				# Get Auto Knee Mode value
				auto_knee_blend = cmds.getAttr(self._rcName.to_ik_ctrl_rt(self._rcName.FOOT) + '.autoKneeBlend')
				auto_knee_mode = (auto_knee_blend >= 0.5)

			# Get leg lengths
			current_thigh_length = cmds.getAttr(self._rcName.to_result_name_rt(self._rcName.CALF) + '.translateX')
			current_calf_length = cmds.getAttr(self._rcName.to_result_name_rt(self._rcName.FOOT) + '.translateX')

			tolerance = 0.001
			if abs(current_thigh_length - self._get_thigh_rt_length()) > tolerance or \
				abs(current_calf_length - self._get_calf_rt_length()) > tolerance:
					cmds.setAttr(self._rcName.to_ik_ctrl_rt(self._rcName.KNEE) + '.kneeSnap', 1)
					cmds.setAttr(self._rcName.to_ik_ctrl_rt(self._rcName.FOOT) + '.stretch', 1)

			# IK Foot transforms / rotations
			t_ik_foot = cmds.xform(self._rcName.to_ik_ctrl_rt(self._rcName.FOOT), query=True, worldSpace=True, translation=True)
			t_result_foot = cmds.xform(self._rcName.to_result_name_rt(self._rcName.FOOT), query=True, worldSpace=True, translation=True)
			t_ik_foot_wrp = cmds.xform(self._rcName.to_ik_ctrl_rt(self._rcName.FOOT), query=True, worldSpace=True, rotatePivot=True)
			t_ik_foot[0] = t_ik_foot[0] + t_result_foot[0] - t_ik_foot_wrp[0]
			t_ik_foot[1] = t_ik_foot[1] + t_result_foot[1] - t_ik_foot_wrp[1]
			t_ik_foot[2] = t_ik_foot[2] + t_result_foot[2] - t_ik_foot_wrp[2]
			r_ik_foot = cmds.xform(self._rcName.to_ik_snap_grp_rt(self._rcName.FOOT), query=True, worldSpace=True, rotation=True)

			# Result Ball orientation
			orient_result_ball = cmds.getAttr(self._rcName.to_result_name_rt(self._rcName.BALL) + '.rotateZ')

			# Update IK leg settings, transforms, and rotations
			cmds.xform(self._rcName.to_ik_ctrl_rt(self._rcName.FOOT), worldSpace=True, rotation=[r_ik_foot[0], r_ik_foot[1], r_ik_foot[2]])
			cmds.xform(self._rcName.to_ik_ctrl_rt(self._rcName.FOOT), worldSpace=True, translation=[t_ik_foot[0], t_ik_foot[1], t_ik_foot[2]])

			cmds.setAttr(self._rcName.to_ik_ctrl_rt(self._rcName.FOOT) + '.toeWiggle', orient_result_ball)

			if not auto_knee_mode:
				# Manual Knee

				# IK knee transforms / rotations
				t_ik_knee = cmds.xform(self._rcName.to_ik_ctrl_rt(self._rcName.KNEE), query=True, worldSpace=True, translation=True)
				t_result_knee = cmds.xform(self._rcName.to_result_name_rt(self._rcName.CALF), query=True, worldSpace=True, translation=True)
				t_ik_knee_wrp = cmds.xform(self._rcName.to_ik_ctrl_rt(self._rcName.KNEE), query=True, worldSpace=True, rotatePivot=True)
				t_ik_knee[0] = t_ik_knee[0] + t_result_knee[0] - t_ik_knee_wrp[0]
				t_ik_knee[1] = t_ik_knee[1] + t_result_knee[1] - t_ik_knee_wrp[1]
				t_ik_knee[2] = t_ik_knee[2] + t_result_knee[2] - t_ik_knee_wrp[2]

				cmds.xform(self._rcName.to_ik_ctrl_rt(self._rcName.KNEE), worldSpace=True, translation=[t_ik_knee[0], t_ik_knee[1], t_ik_knee[2]])

				cmds.setAttr(self._rcName.to_ik_ctrl_rt(self._rcName.FOOT) + '.autoKneeBlend', 0)
			else:
				# Auto Knee

				# Calculate leg lengths
				leg_length_factor = cmds.getAttr(self._rcName.to_ik_nf_name_rt(self._rcName.CALF) + '_translateX.output') / self._get_thigh_rt_length()
				thigh_length_factor = current_thigh_length / (self._get_thigh_rt_length() * leg_length_factor)
				calf_length_factor = current_calf_length / (self._get_calf_rt_length() * leg_length_factor)

				cmds.setAttr(self._rcName.to_ik_ctrl_rt(self._rcName.FOOT) + '.autoKneeThighLength', thigh_length_factor)
				cmds.setAttr(self._rcName.to_ik_ctrl_rt(self._rcName.FOOT) + '.autoKneeCalfLength', calf_length_factor)

				# Knee Twist
				cmds.setAttr(self._rcName.to_ik_ctrl_rt(self._rcName.FOOT) + '.kneeTwist' , 0)

				vertex_a = cmds.xform(self._rcName.to_ik_nf_name_rt(self._rcName.CALF), query=True, worldSpace=True, translation=True)
				vertex_b = cmds.xform(self._rcName.to_result_name_rt(self._rcName.CALF), query=True, worldSpace=True, translation=True)
				origin = cmds.xform(self._rcName.to_ik_nf_name_rt(self._rcName.FOOT), query=True, worldSpace=True, translation=True)

				origin_to_vertex_a = [vertex_a[0] - origin[0], vertex_a[1] - origin[1], vertex_a[2] - origin[2]]
				origin_to_vertex_b = [vertex_b[0] - origin[0], vertex_b[1] - origin[1], vertex_b[2] - origin[2]]

				angle = cmds.angleBetween(vector1=[origin_to_vertex_a[0], origin_to_vertex_a[1], origin_to_vertex_a[2]], vector2=[origin_to_vertex_b[0], origin_to_vertex_b[1], origin_to_vertex_b[2]])

				knee_twist = self._angle_to_value(self._rcName.to_ik_nf_name_rt(self._rcName.CALF), angle[3], self._rcName.to_ik_ctrl_rt(self._rcName.FOOT) + '.kneeTwist', self._INITIAL_KNEE_TWIST_INTERVAL, origin, origin_to_vertex_a)
				vertex_a = cmds.xform(self._rcName.to_ik_nf_name_rt(self._rcName.CALF), query=True, worldSpace=True, translation=True)

				tolerance = 0.01
				if abs(vertex_a[0] - vertex_b[0]) > tolerance or \
					abs(vertex_a[1] - vertex_b[1]) > tolerance or \
					abs(vertex_a[2] - vertex_b[2]) > tolerance:
					cmds.setAttr(self._rcName.to_ik_ctrl_rt(self._rcName.FOOT) + '.kneeTwist', -1 * knee_twist)

				cmds.setAttr(self._rcName.to_ik_ctrl_rt(self._rcName.FOOT) + '.autoKneeBlend', 1)

			cmds.setAttr(self._rcName.to_ctrl_rt(self._rcName.LEG_SETTINGS) + '.ikFkBlend', 0)

			return True
		except (ValueError, RuntimeError) as e:
			self._logger.error('Failed to switch IK / FK: ' + str(e))
			self._logger.command_message('Warn: Failed to switch IK / FK. See Script Editor for details.')

			return False

	def ik_fk_switcher_to_fk_leg_rt(self, match = True):
		try:
			if not match:
				# Don't match IK / FK
				cmds.setAttr(self._rcName.to_ctrl_rt(self._rcName.LEG_SETTINGS) + '.ikFkBlend', 1)
				return False

			# Calculate leg length
			current_thigh_length = cmds.getAttr(self._rcName.to_result_name_rt(self._rcName.CALF) + '.translateX')
			current_calf_length = cmds.getAttr(self._rcName.to_result_name_rt(self._rcName.FOOT) + '.translateX')
			thigh_length_factor = abs(current_thigh_length / self._get_thigh_rt_length())
			calf_length_factor = abs(current_calf_length / self._get_calf_rt_length())

			# Get FK leg rotations
			r_fk_thigh = cmds.xform(self._rcName.to_fk_snap_name_rt(self._rcName.THIGH), query=True, worldSpace=True, rotation=True)
			r_fk_calf = cmds.xform(self._rcName.to_fk_snap_name_rt(self._rcName.CALF), query=True, worldSpace=True, rotation=True)
			r_fk_foot = cmds.xform(self._rcName.to_fk_snap_name_rt(self._rcName.FOOT), query=True, worldSpace=True, rotation=True)
			r_fk_ball = cmds.xform(self._rcName.to_fk_snap_name_rt(self._rcName.BALL), query=True, worldSpace=True, rotation=True)

			# Update FK leg settings, length, and rotations
			cmds.setAttr(self._rcName.to_fk_ctrl_rt(self._rcName.THIGH) + '.length', thigh_length_factor)
			cmds.setAttr(self._rcName.to_fk_ctrl_rt(self._rcName.CALF) + '.length', calf_length_factor)

			cmds.xform(self._rcName.to_fk_ctrl_rt(self._rcName.THIGH), worldSpace=True, rotation=[r_fk_thigh[0], r_fk_thigh[1], r_fk_thigh[2]])
			cmds.xform(self._rcName.to_fk_ctrl_rt(self._rcName.CALF), worldSpace=True, rotation=[r_fk_calf[0], r_fk_calf[1], r_fk_calf[2]])
			cmds.xform(self._rcName.to_fk_ctrl_rt(self._rcName.FOOT), worldSpace=True, rotation=[r_fk_foot[0], r_fk_foot[1], r_fk_foot[2]])
			cmds.xform(self._rcName.to_fk_ctrl_rt(self._rcName.BALL), worldSpace=True, rotation=[r_fk_ball[0], r_fk_ball[1], r_fk_ball[2]])

			cmds.setAttr(self._rcName.to_ctrl_rt(self._rcName.LEG_SETTINGS) + '.ikFkBlend', 1)

			return True
		except (ValueError, RuntimeError) as e:
			self._logger.error('Failed to switch IK / FK: ' + str(e))
			self._logger.command_message('Warn: Failed to switch IK / FK. See Script Editor for details.')

			return False

	def ik_fk_switcher_to_auto_knee_rt(self, match = True):
		return self.ik_fk_switcher_to_ik_leg_rt(auto_knee_mode = True, match = match)

	def ik_fk_switcher_to_manual_knee_rt(self, match = True):
		return self.ik_fk_switcher_to_ik_leg_rt(auto_knee_mode = False, match = match)
