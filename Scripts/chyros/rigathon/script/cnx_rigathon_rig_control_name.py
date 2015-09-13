class RigControlName:

	# Control parts
	HEAD = 'head'
	NECK = 'neck'
	SHOULDER = 'shoulder'
	SPINE = 'spine'
	HIP = 'hip'
	BODY = 'body'
	ROOT = 'root'
	OFFSET = 'offset'
	CHARACTER = 'character'
	ARM_GIMBAL = 'arm_gimbal'
	UPPERARM = 'upperarm'
	LOWERARM = 'lowerarm'
	ELBOW_LOWERARM = 'elbow_lowerarm'
	ELBOW = 'elbow'
	HAND = 'hand'
	ELBOW_HAND = 'elbow_hand'
	WRIST = 'wrist'
	PINKY = 'pinky'
	RING = 'ring'
	MIDDLE = 'middle'
	INDEX = 'index'
	THUMB_ORBIT = 'thumb_orbit'
	THUMB = 'thumb'
	THIGH = 'thigh'
	CALF = 'calf'
	KNEE = 'knee'
	FOOT = 'foot'
	BALL = 'ball'
	ARM_SETTINGS = 'arm_settings'
	LEG_SETTINGS = 'leg_settings'

	# Type
	IK = 'ik'
	FK = 'fk'
	RESULT = 'result'
	IK_SNAP = 'ik_snap'
	FK_SNAP = 'fk_snap'
	IK_SNAP_REF = 'ik_snapRef'
	FK_SNAP_REF = 'fk_snapRef'
	IK_NF = 'ik_nf'

	# Orientation
	CENTER = ''
	LEFT = 'left'
	RIGHT = 'right'

	LEFT_CONTROL = 'lt'
	RIGHT_CONTROL = 'rt'
	CONTROL_NAME = 'CTRL'
	GROUP_NAME = 'GRP'

	def __init__(self, util):
		self._util = util

	def to_name(self, part, type, orientation, index, is_control, is_group = False):
		prefix = ''
		suffix = ''

		# Control type
		if len(type) > 0:
			prefix = type + '_'

		# Control index
		if index > 0:
			suffix += '_' + str(index).zfill(2)

		# Control orientation (left, right, center)
		if orientation == self.LEFT:
			suffix += '_' + self.LEFT_CONTROL
		elif orientation == self.RIGHT:
			suffix += '_' + self.RIGHT_CONTROL

		# Control name suffix
		if is_control:
			suffix += '_' + self.CONTROL_NAME

		# Group name suffix
		if is_group:
			suffix += '_' + self.GROUP_NAME

		return prefix + part + suffix

# Controls ==================================================================

	def to_ctrl(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, '', self.CENTER, index, True))

	def to_ctrl_lt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, '', self.LEFT, index, True))

	def to_ctrl_rt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, '', self.RIGHT, index, True))


# IK Controls ===============================================================

	def to_ik_ctrl(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.IK, self.CENTER, index, True))

	def to_ik_ctrl_lt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.IK, self.LEFT, index, True))

	def to_ik_ctrl_rt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.IK, self.RIGHT, index, True))


# IK Controls ===============================================================

	def to_ik_ctrl(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.IK, self.CENTER, index, True))

	def to_ik_ctrl_lt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.IK, self.LEFT, index, True))

	def to_ik_ctrl_rt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.IK, self.RIGHT, index, True))


# FK Controls ===============================================================

	def to_fk_ctrl(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.FK, self.CENTER, index, True))

	def to_fk_ctrl_lt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.FK, self.LEFT, index, True))

	def to_fk_ctrl_rt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.FK, self.RIGHT, index, True))


# RESULT Controls ===========================================================

	def to_result_ctrl(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.RESULT, self.CENTER, index, True))

	def to_result_ctrl_lt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.RESULT, self.LEFT, index, True))

	def to_result_ctrl_rt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.RESULT, self.RIGHT, index, True))


# IK Name ===================================================================

	def to_ik_name(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.IK, self.CENTER, index, False))

	def to_ik_name_lt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.IK, self.LEFT, index, False))

	def to_ik_name_rt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.IK, self.RIGHT, index, False))


# FK Name ===================================================================

	def to_fk_name(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.FK, self.CENTER, index, False))

	def to_fk_name_lt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.FK, self.LEFT, index, False))

	def to_fk_name_rt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.FK, self.RIGHT, index, False))


# RESULT Name ===============================================================

	def to_result_name(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.RESULT, self.CENTER, index, False))

	def to_result_name_lt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.RESULT, self.LEFT, index, False))

	def to_result_name_rt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.RESULT, self.RIGHT, index, False))


# IK NF Group ===============================================================

	def to_ik_nf_name_lt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.IK_NF, self.LEFT, index, False))

	def to_ik_nf_name_rt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.IK_NF, self.RIGHT, index, False))


# IK Snap Group =============================================================

	def to_ik_snap_grp_lt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.IK_SNAP, self.LEFT, index, False, True))

	def to_ik_snap_grp_rt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.IK_SNAP, self.RIGHT, index, False, True))


# IK Snap Ref Group =========================================================

	def to_ik_snap_ref_grp_lt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.IK_SNAP_REF, self.LEFT, index, False, True))

	def to_ik_snap_ref_grp_rt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.IK_SNAP_REF, self.RIGHT, index, False, True))


# FK Snap Name ==============================================================

	def to_fk_snap_name_lt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.FK_SNAP, self.LEFT, index, False))

	def to_fk_snap_name_rt(self, part, index = 0):
		return self._util.to_node_name(self.to_name(part, self.FK_SNAP, self.RIGHT, index, False))
