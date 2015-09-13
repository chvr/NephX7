import maya.cmds as cmds

from cnx_rigathon_logger import Logger

class SkeletonDefinition:

	def __init__(self):
		self._logger = Logger(self.__class__.__name__)

	def to_formatted_num(self, num):
		num_length = 7

		if num == 0:
			# Remove negative sign for zero values
			num = 0

		return '{0:.2f}'.format(num).rjust(num_length)

	def to_formatted_text(self, text, text_width):
		text = text.ljust(text_width)
		text = text.replace('    ', '\t')
		if ' ' in text:
			text = text.replace(' ', '')
			text += '\t'

		return text

	def get_joint_name_width(self, skeleton_def):
		length = 0

		for joint_chain in skeleton_def:
			for joint in joint_chain:
				length = max(length, len(joint.rpartition(':')[2]))

		return length

	def get_label(self, joint_name):
		if 'root' in joint_name:
			return '\n# ROOT joint'
		elif 'pelvis' in joint_name:
			return '\n# BODY joint chain'
		elif 'thigh_lt' in joint_name:
			return '\n# Left LEG joint chain'
		elif 'clavicle' in joint_name:
			return '\n# Left ARM joint chain'
		elif any(joint for joint in ('pinky', 'ring', 'middle', 'index', 'thumb') if joint in joint_name):
			return '\n# Left {0} finger joint chain'.format(joint_name.split('_')[0].upper())

		return None

	def display_script(self, skeleton_def):
		self._logger.info('# Skeleton Definition dump:')

		joint_name_width = self.get_joint_name_width(skeleton_def)

		for joint_chain in skeleton_def:
			print(self.get_label(joint_chain[0].rpartition(':')[2]))

			for joint in joint_chain:
				parent_node = joint.rpartition(':')[0]
				child_node = joint.rpartition(':')[2]

				parent_transform = [0, 0, 0]
				child_transform = cmds.xform(child_node, query=True, worldSpace=True, translation=True)

				if cmds.objExists(parent_node):
					parent_transform = cmds.xform(parent_node, query=True, worldSpace=True, translation=True)

				x = round((child_transform[0] - parent_transform[0]), 2)
				y = round((child_transform[1] - parent_transform[1]), 2)
				z = round((child_transform[2] - parent_transform[2]), 2)

				if joint == joint_chain[0]:
					print('\tcreate_joint\t{0}\t{1}\t{2}\t{3}'.format(self.to_formatted_text(child_node, joint_name_width), self.to_formatted_num(x), self.to_formatted_num(y), self.to_formatted_num(z)))
				else:
					print('\t\t\t\t\t{0}\t{1}\t{2}\t{3}\t\tlocation_relative'.format(self.to_formatted_text(child_node, joint_name_width), self.to_formatted_num(x), self.to_formatted_num(y), self.to_formatted_num(z)))

			print('\t;')

		self._logger.info('\t* Skeleton Definition dump complete.')
		cmds.confirmDialog(title='Dump Skeleton Definition', message='Dump complete.\n\nSee Script Editor for details.       ', button='OK')

		self._logger.command_message('Dump complete. See Script Editor for details.')

	def dump(self):
		eval_joints = ['root']
		skeleton_def = []

		while len(eval_joints) > 0:
			current_node = eval_joints[0]
			eval_joints = eval_joints[1:]
			joint_def = [':{0}'.format(current_node)]

			if current_node[-3:] == '_rt':
				# Skip the right part of skeleton tree
				continue

			child_nodes = cmds.listRelatives(current_node)
			if current_node == 'root':
				# Split root from pelvis
				eval_joints += child_nodes
			else:
				while child_nodes is not None:
					joint_def.append('{0}:{1}'.format(current_node, child_nodes[0]))
					eval_joints += child_nodes[1:]

					current_node = child_nodes[0]
					child_nodes = cmds.listRelatives(current_node)

			skeleton_def.append(joint_def)

		self.display_script(skeleton_def)
