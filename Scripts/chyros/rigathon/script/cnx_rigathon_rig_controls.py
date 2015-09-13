from cnx_rigathon_rig_control import RigControl

class RigControls:

	def __init__(self, util, rigControlName):
		self._util = util
		self._rcName = rigControlName

		self._rig_controls = {}

		self._init_control_definitions()
		self._init_rig_controls()

	def _init_control_definitions(self):
		self._control_definitions = [
			# Name, Orientation, IK / FK, Color Scheme, Description, Index
			[self._rcName.HEAD, 'center', 'ik', 'yellow', 'Head IK', 0]
			, [self._rcName.NECK, 'center', 'fk', 'blue', 'Neck FK', 0]
			, [self._rcName.SHOULDER, 'center', 'ik', 'yellow', 'Shoulder IK', 0]
			, [self._rcName.SPINE, 'center', 'fk', 'blue', 'Spine 2 FK', 2]
			, [self._rcName.SPINE, 'center', 'fk', 'blue', 'Spine 1 FK', 1]
			, [self._rcName.HIP, 'center', 'ik', 'yellow', 'Hip IK', 0]
			, [self._rcName.BODY, 'center', '', 'red', 'Body', 0]
			, [self._rcName.ROOT, 'center', '', 'red', 'Root', 0]
			, [self._rcName.OFFSET, 'center', '', 'purple', 'Offset', 0]
			, [self._rcName.CHARACTER, 'center', '', 'red', 'Character', 0]


# LEFT ======================================================================

			, [self._rcName.SHOULDER, 'left', 'ik', 'yellow', 'Left Shoulder IK', 0]
			, [self._rcName.ELBOW, 'left', 'ik', 'yellow', 'Left Elbow IK', 0]
			, [self._rcName.WRIST, 'left', 'ik', 'yellow', 'Left Wrist IK', 0]
			, [self._rcName.KNEE, 'left', 'ik', 'yellow', 'Left Knee IK', 0]
			, [self._rcName.FOOT, 'left', 'ik', 'yellow', 'Left Foot IK', 0]
			, [self._rcName.ARM_GIMBAL, 'left', '', 'purple', 'Left Upperarm FK (Gimbal Rotation)', 0]
			, [self._rcName.UPPERARM, 'left', 'fk', 'blue', 'Left Upperarm FK', 0]
			, [self._rcName.LOWERARM, 'left', 'fk', 'blue', 'Left Lowerarm FK', 0]
			, [self._rcName.HAND, 'left', 'fk', 'blue', 'Left Hand FK', 0]
			, [self._rcName.THIGH, 'left', 'fk', 'blue', 'Left Thigh FK', 0]
			, [self._rcName.CALF, 'left', 'fk', 'blue', 'Left Calf FK', 0]
			, [self._rcName.FOOT, 'left', 'fk', 'blue', 'Left Foot FK', 0]
			, [self._rcName.BALL, 'left', 'fk', 'blue', 'Left Ball FK', 0]
			, [self._rcName.ELBOW_LOWERARM, 'left', 'fk', 'green', 'Left Elbow to Lowerarm FK', 0]
			, [self._rcName.ELBOW_HAND, 'left', 'fk', 'green', 'Left Elbow to Hand FK', 0]

			# Left Fingers
			, [self._rcName.PINKY, 'left', 'fk', 'blue', 'Left Pinky 1 FK', 1]
			, [self._rcName.PINKY, 'left', 'fk', 'blue', 'Left Pinky 2 FK', 2]
			, [self._rcName.PINKY, 'left', 'fk', 'blue', 'Left Pinky 3 FK', 3]
			, [self._rcName.RING, 'left', 'fk', 'blue', 'Left Ring 1 FK', 1]
			, [self._rcName.RING, 'left', 'fk', 'blue', 'Left Ring 2 FK', 2]
			, [self._rcName.RING, 'left', 'fk', 'blue', 'Left Ring 3 FK', 3]
			, [self._rcName.MIDDLE, 'left', 'fk', 'blue', 'Left Middle 1 FK', 1]
			, [self._rcName.MIDDLE, 'left', 'fk', 'blue', 'Left Middle 2 FK', 2]
			, [self._rcName.MIDDLE, 'left', 'fk', 'blue', 'Left Middle 3 FK', 3]
			, [self._rcName.INDEX, 'left', 'fk', 'blue', 'Left Index 1 FK', 1]
			, [self._rcName.INDEX, 'left', 'fk', 'blue', 'Left Index 2 FK', 2]
			, [self._rcName.INDEX, 'left', 'fk', 'blue', 'Left Index 3 FK', 3]
			, [self._rcName.THUMB_ORBIT, 'left', 'fk', 'purple', 'Left Thumb Orbit FK', 0]
			, [self._rcName.THUMB, 'left', 'fk', 'blue', 'Left Thumb 1 FK', 1]
			, [self._rcName.THUMB, 'left', 'fk', 'blue', 'Left Thumb 2 FK', 2]

			# Left Hand Compound Controls
			, [self._rcName.HAND, 'left', '', 'red', 'Left Hand Compound', 0]
			, [self._rcName.PINKY, 'left', '', 'red', 'Left Pinky Compound', 0]
			, [self._rcName.RING, 'left', '', 'red', 'Left Ring Compound', 0]
			, [self._rcName.MIDDLE, 'left', '', 'red', 'Left Middle Compound', 0]
			, [self._rcName.INDEX, 'left', '', 'red', 'Left Index Compound', 0]
			, [self._rcName.THUMB, 'left', '', 'red', 'Left Thumb Compound', 0]

			# Left Control Settings
			, [self._rcName.ARM_SETTINGS, 'left', '', 'purple', 'Left Arm Settings', 0]
			, [self._rcName.LEG_SETTINGS, 'left', '', 'purple', 'Left Leg Settings', 0]


# RIGHT =====================================================================

			, [self._rcName.SHOULDER, 'right', 'ik', 'yellow', 'Right Shoulder IK', 0]
			, [self._rcName.ELBOW, 'right', 'ik', 'yellow', 'Right Elbow IK', 0]
			, [self._rcName.WRIST, 'right', 'ik', 'yellow', 'Right Wrist IK', 0]
			, [self._rcName.KNEE, 'right', 'ik', 'yellow', 'Right Knee IK', 0]
			, [self._rcName.FOOT, 'right', 'ik', 'yellow', 'Right Foot IK', 0]
			, [self._rcName.ARM_GIMBAL, 'right', '', 'purple', 'Right Upperarm FK (Gimbal Rotation)', 0]
			, [self._rcName.UPPERARM, 'right', 'fk', 'blue', 'Right Upperarm FK', 0]
			, [self._rcName.LOWERARM, 'right', 'fk', 'blue', 'Right Lowerarm FK', 0]
			, [self._rcName.HAND, 'right', 'fk', 'blue', 'Right Hand FK', 0]
			, [self._rcName.THIGH, 'right', 'fk', 'blue', 'Right Thigh FK', 0]
			, [self._rcName.CALF, 'right', 'fk', 'blue', 'Right Calf FK', 0]
			, [self._rcName.FOOT, 'right', 'fk', 'blue', 'Right Foot FK', 0]
			, [self._rcName.BALL, 'right', 'fk', 'blue', 'Right Ball FK', 0]
			, [self._rcName.ELBOW_LOWERARM, 'right', 'fk', 'green', 'Right Elbow to Lowerarm FK', 0]
			, [self._rcName.ELBOW_HAND, 'right', 'fk', 'green', 'Right Elbow to Hand FK', 0]

			# Right Fingers
			, [self._rcName.PINKY, 'right', 'fk', 'blue', 'Right Pinky 1 FK', 1]
			, [self._rcName.PINKY, 'right', 'fk', 'blue', 'Right Pinky 2 FK', 2]
			, [self._rcName.PINKY, 'right', 'fk', 'blue', 'Right Pinky 3 FK', 3]
			, [self._rcName.RING, 'right', 'fk', 'blue', 'Right Ring 1 FK', 1]
			, [self._rcName.RING, 'right', 'fk', 'blue', 'Right Ring 2 FK', 2]
			, [self._rcName.RING, 'right', 'fk', 'blue', 'Right Ring 3 FK', 3]
			, [self._rcName.MIDDLE, 'right', 'fk', 'blue', 'Right Middle 1 FK', 1]
			, [self._rcName.MIDDLE, 'right', 'fk', 'blue', 'Right Middle 2 FK', 2]
			, [self._rcName.MIDDLE, 'right', 'fk', 'blue', 'Right Middle 3 FK', 3]
			, [self._rcName.INDEX, 'right', 'fk', 'blue', 'Right Index 1 FK', 1]
			, [self._rcName.INDEX, 'right', 'fk', 'blue', 'Right Index 2 FK', 2]
			, [self._rcName.INDEX, 'right', 'fk', 'blue', 'Right Index 3 FK', 3]
			, [self._rcName.THUMB_ORBIT, 'right', 'fk', 'purple', 'Right Thumb Orbit FK', 0]
			, [self._rcName.THUMB, 'right', 'fk', 'blue', 'Right Thumb 1 FK', 1]
			, [self._rcName.THUMB, 'right', 'fk', 'blue', 'Right Thumb 2 FK', 2]

			# Right Hand Compound Controls
			, [self._rcName.HAND, 'right', '', 'red', 'Right Hand Compound', 0]
			, [self._rcName.PINKY, 'right', '', 'red', 'Right Pinky Compound', 0]
			, [self._rcName.RING, 'right', '', 'red', 'Right Ring Compound', 0]
			, [self._rcName.MIDDLE, 'right', '', 'red', 'Right Middle Compound', 0]
			, [self._rcName.INDEX, 'right', '', 'red', 'Right Index Compound', 0]
			, [self._rcName.THUMB, 'right', '', 'red', 'Right Thumb Compound', 0]

			# Right Control Settings
			, [self._rcName.ARM_SETTINGS, 'right', '', 'purple', 'Right Arm Settings', 0]
			, [self._rcName.LEG_SETTINGS, 'right', '', 'purple', 'Right Leg Settings', 0]
		]

	def _init_rig_controls(self):
		for control_definition in self._control_definitions:
			part = control_definition[0]
			orientation = control_definition[1]
			type = control_definition[2]
			color = control_definition[3]
			desc = control_definition[4]
			index = control_definition[5]

			key = self._rcName.to_name(part, type, orientation, index, False)
			ctrl_name = self._rcName.to_name(part, type, orientation, index, True)
			picker_name = self._util.to_ui_name('btn_picker_' + key)

			self._rig_controls[key] = RigControl(self._util, key, ctrl_name, type, color, desc)

			# Multi-picker controls
			if key == self._rcName.OFFSET:
				self._rig_controls[key].create_picker()

	def get_rig_control(self, key):
		return self._rig_controls[key]

	def get_rig_control_keys(self):
		return self._rig_controls.keys()

	def get_rig_control_names(self, with_namespace = True):
		rig_control_names = []
		for key in self._rig_controls:
			rig_control_name = None
			if with_namespace:
				rig_control_name = self._rig_controls[key].get_ctrl_name()
			else:
				rig_control_name = self._rig_controls[key].get_ctrl_name().rpartition(':')[2]

			rig_control_names.append(rig_control_name)

		return rig_control_names

	def get_size(self):
		return len(self._rig_controls)
