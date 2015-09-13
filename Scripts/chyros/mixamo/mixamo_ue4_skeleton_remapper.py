import collections

# Base Joint
base_joint = 'Hips'

# Skeleton Mapping
mixamo_to_ue4_skeleton_map = collections.OrderedDict()
mixamo_to_ue4_skeleton_map['Hips'] = 'pelvis'
mixamo_to_ue4_skeleton_map['Spine2'] = 'spine_03'
mixamo_to_ue4_skeleton_map['Spine1'] = 'spine_02'
mixamo_to_ue4_skeleton_map['Spine'] = 'spine_01'
mixamo_to_ue4_skeleton_map['Neck'] = 'neck_01'
mixamo_to_ue4_skeleton_map['HeadTop_End'] = 'head'
mixamo_to_ue4_skeleton_map['Head'] = 'neck_03'
mixamo_to_ue4_skeleton_map['Shoulder'] = 'shoulder'
mixamo_to_ue4_skeleton_map['ForeArm'] = 'lowerarm'
mixamo_to_ue4_skeleton_map['Arm'] = 'upperarm'
mixamo_to_ue4_skeleton_map['HandThumb'] = 'thumb_0'
mixamo_to_ue4_skeleton_map['HandIndex'] = 'index_0'
mixamo_to_ue4_skeleton_map['HandMiddle'] = 'middle_0'
mixamo_to_ue4_skeleton_map['HandRing'] = 'ring_0'
mixamo_to_ue4_skeleton_map['HandPinky'] = 'pinky_0'
mixamo_to_ue4_skeleton_map['Hand'] = 'hand'
mixamo_to_ue4_skeleton_map['UpLeg'] = 'thigh'
mixamo_to_ue4_skeleton_map['Leg'] = 'calf'
mixamo_to_ue4_skeleton_map['Foot'] = 'foot'
mixamo_to_ue4_skeleton_map['ToeBase'] = 'toe'
mixamo_to_ue4_skeleton_map['Toe_End'] = 'ball'

# Left / Right identifier
mixamo_left = 'Left'
mixamo_right = 'Right'
ue4_left_suffix = '_lt'
ue4_right_suffix = '_rt'

# Rename joints
joints = cmds.listRelatives(base_joint, allDescendents=True, type='joint')
if joints is not None:
	# Add base joint
	joints.insert(0, base_joint)

	for mixamo_joint in joints:
		for k, v in mixamo_to_ue4_skeleton_map.items():
			if k not in mixamo_joint:
				continue

			ue4_joint = mixamo_joint.replace(k, v)
			if mixamo_left in ue4_joint:
				ue4_joint = ue4_joint.replace(mixamo_left, '') + ue4_left_suffix
			if mixamo_right in ue4_joint:
				ue4_joint = ue4_joint.replace(mixamo_right, '') + ue4_right_suffix

			# Rename joint
			print (mixamo_joint + ' : ' + ue4_joint)
			cmds.rename(mixamo_joint, ue4_joint)

			break
