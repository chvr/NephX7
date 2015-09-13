import maya.cmds as cmds

from cnx_rigathon_logger import Logger

class Settings:

	# Bind Pose Indices
	BIND_POSE_INDEX = -1
	DEFAULT_BIND_POSE_INDEX = -2

	_NODE_SETTINGS = 'rigathon_settings'
	_NODE_POSES = 'poses'

	# Bind Pose Nodes
	_BIND_POSE_NODE = 'bind_pose'
	_DEFAULT_BIND_POSE_NODE = 'default_bind_pose'

	# Pose Node and Attribute
	_POSE_NODE = 'pose_$index'
	_POSE_ATTRIB = 'name'

	# Pose Group Node and Attribute
	_POSE_GROUP_NODE = 'pose_group'
	_POSE_GROUP_ATTRIBUTE = 'name_$start_to_$end'

	_CTRL_POSE_NODE_SUFFIX = '_POSE'

	_LIST_SEP = r'\,' # Make this separator as unique as possible
	_DECIMAL_PT = '.'

	def __init__(self, ref_name = ''):
		self._logger = Logger(self.__class__.__name__)
		self._ref_name = ref_name

	def get_ref_name(self):
		return self._ref_name

	def set_ref_name(self, ref_name):
		self._ref_name = ref_name

	def reset_ref_name(self):
		self._ref_name = ''

	def is_pose_group_exists(self, index):
		return cmds.objExists(self._get_pose_node(index))

	def save(self, key, value, node_name = None, section = None, sub_section = None):
		node_path = self._create_node(node_name, section, sub_section)

		if not cmds.objExists(self._to_maya_attr(key, node_path)):
			# Create new key
			if type(value) is bool:
				cmds.addAttr(node_path, longName=key, attributeType='bool')
			elif type(value) is int:
				cmds.addAttr(node_path, longName=key, attributeType='long')
			elif type(value) is float:
				cmds.addAttr(node_path, longName=key, attributeType='float')
			elif type(value) in (unicode, str, list):
				cmds.addAttr(node_path, longName=key, dataType='string')
			else:
				self._logger.warn('Unable to save key \'$key\' - unsupported type \'$type\'' \
					.replace('$key', key) \
					.replace('$type', type(value).__name__) \
					)
				return False

			cmds.setAttr(self._to_maya_attr(key, node_path), channelBox=True)

		# Update key with new value
		if type(value) is list:
			cmds.setAttr(self._to_maya_attr(key, node_path), self._LIST_SEP.join(str(item) for item in value), type='string')
		elif type(value) in [unicode, str]:
			cmds.setAttr(self._to_maya_attr(key, node_path), value, type='string')
		else:
			cmds.setAttr(self._to_maya_attr(key, node_path), value)

		return True

	def load(self, key, default_value = None, node_name = None, section = None, sub_section = None, as_list = False):
		node_path = self._to_node_path(node_name, section, sub_section)

		if not cmds.objExists(self._to_maya_attr(key, node_path)):
			return default_value

		value = cmds.getAttr(self._to_maya_attr(key, node_path))
		if type(value) is unicode and self._LIST_SEP in value:
			value_list = []
			for item in value.split(self._LIST_SEP):
				if len(value.strip()) == 0:
					continue

				if self._DECIMAL_PT in item:
					try:
						value_list.append(float(item))
					except ValueError:
						value_list.append(item)
				else:
					try:
						value_list.append(int(item))
					except ValueError:
						value_list.append(item)

			return value_list
		else:
			if as_list:
				if len(value.strip()) == 0:
					return []
				else:
					return [value]
			else:
				return value

	def delete_node(self, node_name = None, section = None, sub_section = None):
		node_path = self._create_node(node_name, section, sub_section)

		if cmds.objExists(node_path):
			cmds.delete(node_path)

	def save_pose(self, index, ctrl_name):
		# Duplicate custom attributes
		if not cmds.objExists(ctrl_name):
			return False

		# Pose node
		ctrl_pose_node_path = self._create_node(self._get_ctrl_pose_node(index, ctrl_name, False), self._NODE_POSES, self._get_pose_node(index), True)

		src_attr_list = cmds.listAttr(ctrl_name, keyable=True)
		dest_attr_list = cmds.listAttr(ctrl_pose_node_path, keyable=True)

		for attr in src_attr_list:
			if ctrl_name.rpartition(':')[2] == 'character_CTRL':
				if attr in ['translateX', 'translateY', 'translateZ']:
					# Skip translation attributes
					continue

			if dest_attr_list is None or attr not in dest_attr_list:
				if attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ', 'visibility']:
					# Unhide default attribute
					cmds.setAttr(ctrl_pose_node_path + '.' + attr, lock=False, keyable=True, channelBox=True)
				else:
					cmds.addAttr(ctrl_pose_node_path, longName=attr, dataType='string', keyable=True)

		# Copy attribute values
		cmds.copyAttr(ctrl_name, ctrl_pose_node_path, values=True, attribute=src_attr_list)

		return True

	def load_pose(self, index, ctrl_name):
		ctrl_pose_node = self._get_ctrl_pose_node(index, ctrl_name, True)

		# Copy posed control attributes to the specified control
		if cmds.objExists(ctrl_pose_node):
			src_attr_list = cmds.listAttr(ctrl_pose_node, channelBox=True)
			cmds.copyAttr(ctrl_pose_node, ctrl_name, values=True, attribute=src_attr_list)
			return True

		return False

	def delete_pose(self, index, ctrl_name):
		ctrl_pose_node = self._get_ctrl_pose_node(index, ctrl_name, True)

		# Delete posed control
		if cmds.objExists(ctrl_pose_node):
			cmds.delete(ctrl_pose_node)
			return True

		return False

	def save_pose_name(self, index, new_pose_name):
		return self.save(self._POSE_ATTRIB, new_pose_name, self._get_pose_node(index), self._NODE_POSES)

	def load_pose_name(self, index):
		pose_name = self.load(self._POSE_ATTRIB, None, self._get_pose_node(index), self._NODE_POSES)
		if pose_name is None:
			pose_name = 'Pose #' + str(index)

		return pose_name

	def delete_pose_name(self, index):
		pose_node_path = self._create_node(self._get_pose_node(index), self._NODE_POSES)
		node_attrib = '.'.join([pose_node_path, self._POSE_ATTRIB])

		if cmds.objExists(node_attrib):
			cmds.deleteAttr(node_attrib)

	def save_pose_group_name(self, start, end, new_pose_group_name):
		return self.save(self._get_pose_group_attrib(start, end), new_pose_group_name, self._get_pose_group_node(), self._NODE_POSES)

	def load_pose_group_name(self, start, end):
		pose_group_name = self.load(self._get_pose_group_attrib(start, end), None, self._get_pose_group_node(), self._NODE_POSES)
		if pose_group_name is None:
			pose_group_name = 'Poses #$start - $end'

		return pose_group_name

	def delete_pose_group_name(self, start, end):
		pose_group_node = self._get_pose_group_node()
		node_attrib = '.'.join([pose_group_node, self._get_pose_group_attrib(start, end)])

		if cmds.objExists(node_attrib):
			cmds.deleteAttr(node_attrib)

	def _create_node(self, node_name, section = None, sub_section = None, hide_default_attr = True):
		node_path = self._to_node_path(node_name, section, sub_section)
		self._create_node_path(node_path, hide_default_attr)

		return node_path

	def _get_pose_node(self, index):
		if index == self.BIND_POSE_INDEX:
			return self._BIND_POSE_NODE
		elif index == self.DEFAULT_BIND_POSE_INDEX:
			return self._DEFAULT_BIND_POSE_NODE
		else:
			return self._POSE_NODE \
				.replace('$index', '{0:03d}'.format(index))

	def _get_ctrl_pose_node(self, index, ctrl_name, full_path = False):
		ctrl_name = ctrl_name.rpartition(':')[2]
		ctrl_pose_node = None

		if full_path:
			ctrl_pose_node = '$config_node|$poses_node|$pose_node|$ctrl_name$suffix'
		else:
			ctrl_pose_node = '$ctrl_name$suffix'

		return ctrl_pose_node \
			.replace('$config_node', self._NODE_SETTINGS) \
			.replace('$poses_node', self._NODE_POSES) \
			.replace('$pose_node', self._get_pose_node(index)) \
			.replace('$ctrl_name', ctrl_name.lower()) \
			.replace('$suffix', self._CTRL_POSE_NODE_SUFFIX)

	def _get_pose_group_node(self):
		return self._POSE_GROUP_NODE

	def _get_pose_group_attrib(self, start, end):
		return self._POSE_GROUP_ATTRIBUTE \
			.replace('$start', str(start)) \
			.replace('$end', str(end))

	def _to_node_path(self, node_name, section = None, sub_section = None):
		node_path = '|' + self._NODE_SETTINGS

		if section is not None:
			node_path = '|'.join([node_path, section])

		if sub_section is not None:
			node_path = '|'.join([node_path, sub_section])

		if node_name is not None:
			node_path = '|'.join([node_path, node_name])

		return node_path

	def _create_node_path(self, node_path, hide_default_attr = True):
		if cmds.objExists(node_path):
			# Node path already exists
			return False

		parent_node_path = ''
		for node in node_path.split('|'):
			if node == '':
				# Skip empty node name
				continue

			node = '|' + node
			if not cmds.objExists(parent_node_path + node):
				# Create new node
				cmds.group(empty=True, name=node)
				if hide_default_attr:
					# Hide initial attributes
					self._hide_default_attr(node)

			if parent_node_path == '':
				# Set current node as parent
				parent_node_path = node
			else:
				if not cmds.objExists(parent_node_path + node):
					# Move newly created node child of the current parent
					cmds.parent(node, parent_node_path)

				# Set parent node path
				parent_node_path = parent_node_path + node

		return True

	def _hide_default_attr(self, node_path):
		cmds.setAttr(node_path + '.visibility', False)
		for attr in ['.tx', '.ty', '.tz', '.rx', '.ry', '.rz', '.sx', '.sy', '.sz', '.v']:
			cmds.setAttr(node_path + attr, lock=True, keyable=False, channelBox=False)

	def _to_maya_attr(self, key, section):
		if section is None:
			section = self._NODE_SETTINGS

		return '.'.join([section, key])
