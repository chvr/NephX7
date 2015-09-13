import sys
import argparse
import os
import re

APP_NAME = 'Parser'

DEBUG_OUTPUT = False

LOG_INFO = 'INFO '
LOG_WARN = 'WARN '
LOG_ERROR = 'ERROR'
LOG_DEBUG = 'DEBUG'

CHAR_EMPTY = ''
CHAR_SPACE = ' '
CHAR_TAB = '\t'
CHAR_NEW_LINE = '\n'
CHAR_NOT = '!'
CHAR_QUOTE = '\"'
CHAR_DOUBLE_SPACE = CHAR_SPACE + CHAR_SPACE
CHAR_DOUBLE_QUOTE = CHAR_QUOTE + CHAR_QUOTE

SCRIPT_SYMBOL_OBJ_OPEN = '%'
SCRIPT_SYMBOL_OBJ_CLOSE = '%'
SCRIPT_SYMBOL_FORMAT_STR_OPEN = '<'
SCRIPT_SYMBOL_FORMAT_STR_CLOSE = '>'
SCRIPT_SYMBOL_ATTRIBUTE = '.'
SCRIPT_GET_ATTR_OPEN = '{'
SCRIPT_GET_ATTR_CLOSE = '}'
SCRIPT_COMMAND_DELIMITER = CHAR_NEW_LINE
SCRIPT_PARAMETER_DELIMITER = CHAR_SPACE
SCRIPT_PARAMETER_OR_DELIMITER = '|'
SCRIPT_OBJECT_DELIMITER = ','
SCRIPT_ENUM_DELIMITER = ':'

REGEX_SCRIPT = r'(?P<comment>#+[^\n]*)?\n?(?P<command>\w+[^;]*)?;?'
REGEX_SECTION_PARAM_VALUE = r'(\[(?P<section>\w+)\])?[\s]*(?P<param>[!]?\w[^=\s]+)=?(?P<value>\"[^\"]+\"?|[^\s]+)?' # param1=value1 param2="value2"
REGEX_PARAMETER_NAME = r'\$(?P<parameter_name>\w[\w|$]+)' # $param1, $param2, $param3
REGEX_PARAMETER_OBJECT_GROUP = r'(?<!\w)\[(?P<objs>.*?)\]' # [object1, object2, object3]

OBJ_REF_LIST = '_object_ref_list'
OBJ_NAME = '_object_name'
OBJ_VECTOR = '_object_vector'
LAST_OBJ_NAME = '_tmp_name'

# Global variable(s)
defaults = {}

## ==========================================================================
##	 DEFAULT CLASS
## ==========================================================================
class Default:
	pass

## ==========================================================================
##	 TO DEFAULT KEY
##		- To dictionary key
## ==========================================================================
def to_default_key(section, param):
	return section + SCRIPT_SYMBOL_ATTRIBUTE + param

## ==========================================================================
##	 QUOTE STR
## ==========================================================================
def quote_str(string):
	if string is not CHAR_EMPTY:
		return CHAR_QUOTE + string + CHAR_QUOTE

	return CHAR_EMPTY

## ==========================================================================
##	 TO OBJ
## ==========================================================================
def to_obj(name):
	return SCRIPT_SYMBOL_OBJ_OPEN + name + SCRIPT_SYMBOL_OBJ_CLOSE

## ==========================================================================
##	 TO MAYA OBJ
## ==========================================================================
def to_maya_obj(name):
	if 'getAttr' in name:
		# No change for Maya getAttribute command (i.e., 'cmds.getAttr("ik_thigh_lt.translateX")')
		pass
	elif (SCRIPT_SYMBOL_OBJ_OPEN + SCRIPT_SYMBOL_OBJ_CLOSE) == (name[0] + name[-1]):
		# Parse as object name (i.e., (name='%thigh_lt%'): output='thigh_lt')
		name = name.replace(SCRIPT_SYMBOL_OBJ_OPEN, CHAR_EMPTY) \
			.replace(SCRIPT_SYMBOL_OBJ_CLOSE, CHAR_EMPTY)
	else:
		# Parse as string literal (i.e. (name='thigh_lt'): output='"thigh_lt"')
		name = quote_str(name)

	return name

## ==========================================================================
##	 TO FORMAT STR
## ==========================================================================
def to_format_str(name, format):
	# Reformat name (i.e., (name='ik_<0>', replace_with='thigh_lt'): output='ik_thigh_lt'
	return ('$format.format($name)') \
		.replace('$format', format) \
		.replace('$name', name) \
		.replace(SCRIPT_SYMBOL_FORMAT_STR_OPEN, '{') \
		.replace(SCRIPT_SYMBOL_FORMAT_STR_CLOSE, '}')

## ==========================================================================
##	 READ FILE
## ==========================================================================
def read_file(filename):
	_file = open(filename, 'r')
	_content = _file.read()
	_file.close
	return _content

## ==========================================================================
##	 WRITE TO FILE
## ==========================================================================
def write_to_file(filename, content):
	_file = open(filename, 'w')
	_file.write(content)
	_file.close

## ==========================================================================
##	 SPLIT
##		- Helper function for splitting strings by delimiter
##		with option to omit empty lists
## ==========================================================================
def split(strings, delimiter, count = -1, omit_empty = True):
	_output = []

	_output = strings.split(delimiter)

	if omit_empty:
		# Remove empty lists
		_output = filter(None, _output)

	# Rejoin and resplit with count limit
	_output = delimiter.join(_output).split(delimiter, count)

	logDebug('split => ' + ', '.join(_output))

	return _output

## ==========================================================================
##	 EXTRACT PARAMS OBJS
##		- Helper function for extracting parameter objects from object group
## ==========================================================================
def extract_param_objs(parameters, prefix = CHAR_EMPTY):
	_output = []

	_pattern = re.compile(REGEX_PARAMETER_OBJECT_GROUP)

	# Iterate each match
	_iter = _pattern.finditer(parameters)
	for _match in _iter:
		_list = []

		_objs = _match.group('objs')

		# Iterate each by object delimiter
		for _obj in split(_objs, SCRIPT_OBJECT_DELIMITER):
			_obj = _obj.strip() # Remove trailing spaces
			_list.append(prefix + _obj)

		_output.append(_list)

	if len(_output) == 1:
		# Change type from list-of-list to list
		_output = _output[0]

	return _output

## ==========================================================================
##	 GET PARAMETER NAME
##		 - Helper function for parsing parameter names
## ==========================================================================
def get_parameter_names(parameters):
	_output = []

	_pattern = re.compile(REGEX_PARAMETER_NAME)

	# Iterate each parameter names
	_iter = _pattern.finditer(parameters)
	for _match in _iter:
		_parameter_name = _match.group('parameter_name')
		_output.append(_parameter_name)

	return _output

## ==========================================================================
##	 GET PARAMETER KEY VALUE
##		 - Helper function for parsing parameter values
##		 - Retrieve parameter value from list of parameters
##		 - Default value, if defined, will be used if parameter is not found
## ==========================================================================
def get_parameter_key_value_pair(parameters, parameter_name, value_only = False, default_section = None, is_mel_parameter = False):
	_pattern = re.compile(REGEX_SECTION_PARAM_VALUE)

	# Split by OR-switch delimiter (i.e., "parameter_name1|parameter_name2|parameter_name3")
	_parameter_names = split(parameter_name, SCRIPT_PARAMETER_OR_DELIMITER)

	# Iterate each parameters for user values
	_iter = _pattern.finditer(parameters)
	for match in _iter:
		_key = match.group('param')
		_value = match.group('value')

		# Implicitly set value to True if nothing is specified
		if _value is None:
			_value = 'True'

		# Iterate each parameter names
		for _p in _parameter_names:
			if _p == _key.replace(CHAR_NOT, CHAR_EMPTY):
				if _key[:1] == CHAR_NOT:
					# Exclude parameters with CHAR_NOT prefix
					return None

				# Parameter value found
				if value_only:
					return _value
				else:
					if is_mel_parameter:
						return _key
					else:
						return _key + '=' + _value

	# Try to search parameter from DEFAULTS
	if default_section is not None:
		for _p in _parameter_names:
			_default = defaults.get(to_default_key(default_section, _p), None)
			if _default is None:
				continue

			# Filter by section, if any
			if default_section != _default.section:
				continue

			# Default value for parameter is found
			if value_only:
				return _value
			else:
				if is_mel_parameter:
					return _key
				else:
					return _p + '=' + _default.value

	# No user or default parameter found
	return None

## ==========================================================================
##	 POPULATE COMMAND PARAMETERS
##		 - Helper function for populating command parameters
## ==========================================================================
def populate_command_parameters(command, parameters, default_section = None, is_mel_parameter = False):
	for _parameter_name in get_parameter_names(command):
		_parameter_key_value_pair = get_parameter_key_value_pair(parameters, _parameter_name, default_section = default_section, is_mel_parameter = is_mel_parameter)
		if _parameter_key_value_pair is not None:
			# Update parameter name and value
			if is_mel_parameter:
				_parameter_key_value_pair = quote_str(_parameter_key_value_pair)

			command = command.replace('$' + _parameter_name, _parameter_key_value_pair)
		else:
			# Omit non-specified parameter with no defaults
			command = command.replace(', $' + _parameter_name, CHAR_EMPTY)
			command = command.replace('$' + _parameter_name, CHAR_EMPTY) # handle first parameter

	return command

## ==========================================================================
##	 CLEAN UP SCRIPT
##		- Clean up script spacing
## ==========================================================================
def clean_up_script(script):
	# Convert tabs to spaces
	script = script.replace(CHAR_TAB, CHAR_SPACE)

	# Remove double spaces
	while CHAR_DOUBLE_SPACE in script:
		script = script.replace(CHAR_DOUBLE_SPACE, CHAR_SPACE)

	# Remove leading space
	script = script.replace(CHAR_NEW_LINE + CHAR_SPACE, CHAR_NEW_LINE)

	# Remove leading new line of SCRIPT_COMMAND_DELIMITER
	script = script.replace(CHAR_NEW_LINE + SCRIPT_COMMAND_DELIMITER, SCRIPT_COMMAND_DELIMITER)

	# Maya shortcut commands
	script = script.replace(SCRIPT_GET_ATTR_OPEN, '(cmds.getAttr(' + CHAR_QUOTE)
	script = script.replace(SCRIPT_GET_ATTR_CLOSE, CHAR_QUOTE +'))')

	return script

## ==========================================================================
##	 TRANSLATE SCRIPT
##		- Translate rigathon script to Maya python script
## ==========================================================================
def translate(script):
	_output = pre_script()

	_pattern = re.compile(REGEX_SCRIPT)

	# Iterate each script statement
	_iter = _pattern.finditer(script)
	for match in _iter:
		_comment = match.group('comment')
		_command = match.group('command')

		if _comment is not None:
			# Parse comment line
			_output += _comment + CHAR_NEW_LINE
		elif _comment is None and _command is None:
			# Parse empty line
			_output += CHAR_NEW_LINE

		if _command is not None:
			# Parse command
			if DEBUG_OUTPUT:
				logDebug('Translating \'' + _command.replace(CHAR_NEW_LINE, '\\n') + '\'...')

			# Split command from parameters
			_command_syntax = split(_command, CHAR_SPACE, 1)

			# Translate command name
			if _command_syntax[0] == 'define_defaults':						# Command: define_defaults
				script_define_defaults(_command_syntax[1])
			elif _command_syntax[0] == 'create_joint':						# Command: create_joint
				_output += script_create_joint(_command_syntax[1])
			elif _command_syntax[0] == 'insert_joint':						# Command: insert_joint
				_output += script_insert_joint(_command_syntax[1])
			elif _command_syntax[0] == 'edit_joint':						# Command: edit_joint
				_output += script_edit_joint(_command_syntax[1])
			elif _command_syntax[0] == 'mirror_joint':						# Command: mirror_joint
				_output += script_mirror_joint(_command_syntax[1])
			elif _command_syntax[0] == 'move_joint':						# Command: move_joint
				_output += script_move_joint(_command_syntax[1])
			elif _command_syntax[0] == 'parent_constraint':					# Command: parent constraint
				_output += script_parent_constraint(_command_syntax[1])
			elif _command_syntax[0] == 'point_constraint':					# Command: point constraint
				_output += script_point_constraint(_command_syntax[1])
			elif _command_syntax[0] == 'orient_constraint':					# Command: orient constraint
				_output += script_orient_constraint(_command_syntax[1])
			elif _command_syntax[0] == 'scale_constraint':					# Command: scale constraint
				_output += script_scale_constraint(_command_syntax[1])
			elif _command_syntax[0] == 'pole_constraint':					# Command: pole constraint
				_output += script_pole_constraint(_command_syntax[1])
			elif _command_syntax[0] == 'parent':							# Command: parent
				_output += script_parent(_command_syntax[1])
			elif _command_syntax[0] == 'create_group':						# Command: create_group
				_output += script_create_group(_command_syntax[1])
			elif _command_syntax[0] == 'bind_skin':							# Command: bind_skin
				_output += script_bind_skin(_command_syntax[1])
			elif _command_syntax[0] == 'skin_vertices':						# Command: skin_vertices
				_output += script_skin_vertices(_command_syntax[1])
			elif _command_syntax[0] == 'copy_skin_weights':					# Command: copy_skin_weights
				_output += script_copy_skin_weights(_command_syntax[1])
			elif _command_syntax[0] == 'wrap_deform':						# Command: wrap_deform
				_output += script_wrap_deform(_command_syntax[1])
			elif _command_syntax[0] == 'ik_handle':							# Command: ik_handle
				_output += script_ik_handle(_command_syntax[1])
			elif _command_syntax[0] == 'create_locator':					# Command: create_locator
				_output += script_create_locator(_command_syntax[1])
			elif _command_syntax[0] == 'rename':							# Command: rename
				_output += script_rename(_command_syntax[1])
			elif _command_syntax[0] == 'move':								# Command: move
				_output += script_move(_command_syntax[1])
			elif _command_syntax[0] == 'rotate':							# Command: rotate
				_output += script_rotate(_command_syntax[1])
			elif _command_syntax[0] == 'scale':								# Command: scale
				_output += script_scale(_command_syntax[1])
			elif _command_syntax[0] == 'freeze':							# Command: freeze
				_output += script_freeze(_command_syntax[1])
			elif _command_syntax[0] == 'center_pivot':						# Command: center pivot
				_output += script_center_pivot(_command_syntax[1])
			elif _command_syntax[0] == 'duplicate':							# Command: duplicate
				_output += script_duplicate(_command_syntax[1])
			elif _command_syntax[0] == 'delete':							# Command: delete
				_output += script_delete(_command_syntax[1])
			elif _command_syntax[0] == 'create_circle':						# Command: create circle
				_output += script_create_circle(_command_syntax[1])
			elif _command_syntax[0] == 'create_curve':						# Command: create curve
				_output += script_create_curve(_command_syntax[1])
			elif _command_syntax[0] == 'add_attribute':						# Command: add attribute
				_output += script_add_attribute(_command_syntax[1])
			elif _command_syntax[0] == 'set_attribute':						# Command: set attribute
				_output += script_set_attribute(_command_syntax[1])
			elif _command_syntax[0] == 'connect_attribute':					# Command: connect attribute
				_output += script_connect_attribute(_command_syntax[1])
			elif _command_syntax[0] == 'set_driven_key':					# Command: set driven key
				_output += script_set_driven_key(_command_syntax[1])
			elif _command_syntax[0] == 'create_node':						# Command: create node
				_output += script_create_node(_command_syntax[1])
			elif _command_syntax[0] == 'create_layer':						# Command: create layer
				_output += script_create_layer(_command_syntax[1])
			elif _command_syntax[0] == 'edit_layer':						# Command: edit layer
				_output += script_edit_layer(_command_syntax[1])
			elif _command_syntax[0] == 'key_tangent':						# Command: key_tangent
				_output += script_key_tangent(_command_syntax[1])
			elif _command_syntax[0] == 'set_infinity':						# Command: set_infinity
				_output += script_set_infinity(_command_syntax[1])
			elif _command_syntax[0] == 'xform_var':							# Command: xform_var
				_output += script_xform_var(_command_syntax[1])
			elif _command_syntax[0] == 'xform_ref':							# Command: xform_ref
				_output += script_xform_ref(_command_syntax[1])
			elif _command_syntax[0] == 'clear_vars':						# Command: clear_var
				_output += script_clear_vars(_command_syntax[1])
			elif _command_syntax[0] == 'create_distance':					# Command: create_distance
				_output += script_create_distance(_command_syntax[1])
			elif _command_syntax[0] == 'find_replace':						# Command: find_replace
				_output += script_find_replace(_command_syntax[1])
			elif _command_syntax[0] == 'rename_prefix':						# Command: rename_prefix
				_output += script_rename_prefix(_command_syntax[1])
			elif _command_syntax[0] == 'rename_suffix':						# Command: rename_suffix
				_output += script_rename_suffix(_command_syntax[1])
			else:															# Unsupported
				logWarn('Ignored unsupported command \'' + _command.replace(CHAR_NEW_LINE, '\\n') + '\'')

	_output += post_script()
	
	return _output

## ==========================================================================
##	 PRE SCRIPT
## ==========================================================================
def pre_script():

	_script = \
		'# Modules' + CHAR_NEW_LINE + \
		'import maya.cmds as cmds' + CHAR_NEW_LINE + \
		'# Init' + CHAR_NEW_LINE + \
		'$obj_ref_list = {}'.replace('$obj_ref_list', OBJ_REF_LIST) + CHAR_NEW_LINE + \
		CHAR_NEW_LINE

	return _script

## ==========================================================================
##	 POST SCRIPT
## ==========================================================================
def post_script():

	_script = \
		'# Clean-up script' + CHAR_NEW_LINE + \
		'$obj_ref_list = None' + CHAR_NEW_LINE + \
		'$obj_name = None' + CHAR_NEW_LINE + \
		'$obj_vector = None' + CHAR_NEW_LINE + \
		'$last_obj_name = None' + CHAR_NEW_LINE

	_script = _script \
		.replace('$obj_ref_list', OBJ_REF_LIST) \
		.replace('$obj_name', OBJ_NAME) \
		.replace('$obj_vector', OBJ_VECTOR) \
		.replace('$last_obj_name', LAST_OBJ_NAME)

	return _script

## ==========================================================================
##	 DEFINE DEFAULTS
##		 - Define default parameters which can be overridden later
## ==========================================================================
def script_define_defaults(parameters):
	_pattern = re.compile(REGEX_SECTION_PARAM_VALUE)

	# Iterate each default param/value
	_iter = _pattern.finditer(parameters)
	_header_section = None
	for match in _iter:
		_param = match.group('param')
		_value = match.group('value')
		_section = match.group('section')

		if _section is not None:
			_header_section = _section

		if _header_section is None:
			# Require header section
			continue

		# Put new default param/value into defaults dictionary
		default = Default()
		default.param = _param
		default.value = _value
		default.section = _header_section

		_key = to_default_key(_header_section, _param)
		defaults[_key] = default

## ==========================================================================
##	 (COMPOUND SCRIPT) CREATE JOINT
## ==========================================================================
def script_create_joint(statement):
	_output = CHAR_EMPTY

	# Deselect any selected objects
	_output += maya_select(clear = True) + CHAR_NEW_LINE

	_name = None
	_x = _y = _z = 0
	_value_only = True

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 4:
			continue

		_last_name = _name
		_name = _command_parameters[0]

		if 'location_relative' in _command:
			_x += float(_command_parameters[1])
			_y += float(_command_parameters[2])
			_z += float(_command_parameters[3])
		elif 'relative_to' in _command:
			_ref_name = get_parameter_key_value_pair(_command, 'relative_to', _value_only)
			_x = '($x + $ref_list["$ref_name"][0])'.replace('$x', _command_parameters[1]).replace('$ref_list', OBJ_REF_LIST).replace('$ref_name', _ref_name)
			_y = '($y + $ref_list["$ref_name"][1])'.replace('$y', _command_parameters[2]).replace('$ref_list', OBJ_REF_LIST).replace('$ref_name', _ref_name)
			_z = '($z + $ref_list["$ref_name"][2])'.replace('$z', _command_parameters[3]).replace('$ref_list', OBJ_REF_LIST).replace('$ref_name', _ref_name)
		else:
			_x = float(_command_parameters[1])
			_y = float(_command_parameters[2])
			_z = float(_command_parameters[3])

		# Create joint command
		_output += maya_joint(_name, x = _x, y = _y, z = _z)
		if _last_name is not None:
			# Edit joint command
			_output += '; ' + maya_joint(_last_name, edit = True, parameters = _command)

		_output += CHAR_NEW_LINE

	# Freeze joint orientation
	_output += maya_setAttr(_name + '.jointOrientX', 0.0, _command) + CHAR_NEW_LINE
	_output += maya_setAttr(_name + '.jointOrientY', 0.0, _command) + CHAR_NEW_LINE
	_output += maya_setAttr(_name + '.jointOrientZ', 0.0, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) INSERT JOINT
## ==========================================================================
def script_insert_joint(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 5:
			continue

		_parent = _command_parameters[0]
		_child = _command_parameters[1]
		_count = _command_parameters[2]
		_identifier = _command_parameters[3]	# i.e., _twist
		_suffix = _command_parameters[4]		# i.e., _lt

		# Variable names
		_var_parent = '_parent'
		_var_child = '_child'
		_var_delta = '_delta'
		_vars = '[' + _var_parent + ', ' + _var_child + ', ' + _var_delta + ']'

		# Get world location of parent and child joints
		_output += maya_xform(var = _var_parent, name = _parent, parameters = 'translation worldSpace') + CHAR_NEW_LINE
		_output += maya_xform(var = _var_child, name = _child, parameters = 'translation worldSpace') + CHAR_NEW_LINE
		_output += 'class $delta: pass'.replace('$delta', _var_delta) + CHAR_NEW_LINE

		# Calculate delta and divide by given count param
		_output += '$delta.x = ($child.x - $parent.x) / $count; $delta.y = ($child.y - $parent.y) / $count; $delta.z = ($child.z - $parent.z) / $count' \
			.replace('$count', str(int(_count))) \
			.replace('$delta', _var_delta) \
			.replace('$parent', _var_parent) \
			.replace('$child', _var_child) \
			+ CHAR_NEW_LINE

		# Delta XYZ values
		_delta_x = '$delta.x'.replace('$delta', _var_delta)
		_delta_y = '$delta.y'.replace('$delta', _var_delta)
		_delta_z = '$delta.z'.replace('$delta', _var_delta)

		_new_parent = _parent
		for i in range(int(_count)):
			_new_name = _identifier.join(_parent.rsplit(_suffix, 1)) \
				+ '_0$i$suffix' \
				.replace('$i', str(i + 1)) \
				.replace('$suffix', _suffix)

			# Insert joint command
			_output += maya_insertJoint(_new_parent)
			_output += '; ' + maya_joint('joint1', x = _delta_x, y = _delta_y, z = _delta_z, edit = True, new_name = _new_name, parameters = _command) + CHAR_NEW_LINE

			# Make newly created joint as the new parent
			_new_parent = _new_name

		_output += custom_script_clear_vars(_vars) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) EDIT JOINT
## ==========================================================================
def script_edit_joint(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 2:
			continue

		_name = _command_parameters[0]

		# Edit joint command
		_output += maya_joint(_name, edit = True, parameters = _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) MIRROR JOINT
## ==========================================================================
def script_mirror_joint(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 1:
			continue

		_name = _command_parameters[0]

		# Mirror joint command
		_output += maya_mirrorJoint(_name, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) MOVE JOINT
## ==========================================================================
def script_move_joint(statement):
	_output = CHAR_EMPTY

	_name = None
	_x = _y = _z = 0
	_value_only = True

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 4:
			continue

		_name = _command_parameters[0]

		if 'location_relative' in _command:
			_x += float(_command_parameters[1])
			_y += float(_command_parameters[2])
			_z += float(_command_parameters[3])
		elif 'relative_to' in _command:
			_ref_name = get_parameter_key_value_pair(_command, 'relative_to', _value_only)
			_x = '($x + $ref_list["$ref_name"][0])'.replace('$x', _command_parameters[1]).replace('$ref_list', OBJ_REF_LIST).replace('$ref_name', _ref_name)
			_y = '($y + $ref_list["$ref_name"][1])'.replace('$y', _command_parameters[2]).replace('$ref_list', OBJ_REF_LIST).replace('$ref_name', _ref_name)
			_z = '($z + $ref_list["$ref_name"][2])'.replace('$z', _command_parameters[3]).replace('$ref_list', OBJ_REF_LIST).replace('$ref_name', _ref_name)
		else:
			_x = float(_command_parameters[1])
			_y = float(_command_parameters[2])
			_z = float(_command_parameters[3])

		# Move joint command
		_output += custom_script_move_joint(_name, _x, _y, _z) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) PARENT CONSTRAINT
## ==========================================================================
def script_parent_constraint(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 2:
			continue

		_child_name = _command_parameters[0]
		_target_name = _command_parameters[1]

		if 'batch' in statement and len(_command_parameters) > 3:
			_child_name_fmt = to_obj(to_format_str(OBJ_NAME, quote_str(_command_parameters[1])))
			_target_name_fmt = to_obj(to_format_str(OBJ_NAME, quote_str(_command_parameters[2])))

			# For loop script
			_output += custom_script_foreach(maya_listRelatives(_child_name)) + CHAR_NEW_LINE

			# Parent constraint command
			_output += CHAR_TAB + maya_parentConstraint(_child_name_fmt, _command, _target_name_fmt) + CHAR_NEW_LINE

			_child_name_fmt = _child_name_fmt.replace(OBJ_NAME, quote_str(_child_name))
			_target_name_fmt = _target_name_fmt.replace(OBJ_NAME, quote_str(_child_name))

			_output += maya_parentConstraint(_child_name_fmt, _command, _target_name_fmt) + CHAR_NEW_LINE
		else:
			# Parent constraint command
			_output += maya_parentConstraint(_child_name, _command, _target_name) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) POINT CONSTRAINT
## ==========================================================================
def script_point_constraint(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 2:
			continue

		_child_name = _command_parameters[0]
		_target_name = _command_parameters[1]

		if 'batch' in statement and len(_command_parameters) > 2:
			_child_name_fmt = to_obj(to_format_str(OBJ_NAME, quote_str(_command_parameters[1])))
			_target_name_fmt = to_obj(to_format_str(OBJ_NAME, quote_str(_command_parameters[2])))

			# For loop script
			_output += custom_script_foreach(maya_listRelatives(_child_name)) + CHAR_NEW_LINE

			# Point constraint command
			_output += CHAR_TAB + maya_pointConstraint(_child_name_fmt, _command, _target_name_fmt) + CHAR_NEW_LINE

			_child_name_fmt = _child_name_fmt.replace(OBJ_NAME, quote_str(_child_name))
			_target_name_fmt = _target_name_fmt.replace(OBJ_NAME, quote_str(_child_name))

			_output += maya_pointConstraint(_child_name_fmt, _command, _target_name_fmt) + CHAR_NEW_LINE
		else:
			# Point constraint command
			_output += maya_pointConstraint(_child_name, _command, _target_name) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) ORIENT CONSTRAINT
## ==========================================================================
def script_orient_constraint(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 2:
			continue

		_child_name = _command_parameters[0]
		_target_name = _command_parameters[1]

		if 'batch' in statement and len(_command_parameters) > 2:
			_child_name_fmt = to_obj(to_format_str(OBJ_NAME, quote_str(_command_parameters[1])))
			_target_name_fmt = to_obj(to_format_str(OBJ_NAME, quote_str(_command_parameters[2])))

			# For loop script
			_output += custom_script_foreach(maya_listRelatives(_child_name)) + CHAR_NEW_LINE

			# Orient constraint command
			_output += CHAR_TAB + maya_orientConstraint(_child_name_fmt, _command, _target_name_fmt) + CHAR_NEW_LINE

			_child_name_fmt = _child_name_fmt.replace(OBJ_NAME, quote_str(_child_name))
			_target_name_fmt = _target_name_fmt.replace(OBJ_NAME, quote_str(_child_name))

			_output += maya_orientConstraint(_child_name_fmt, _command, _target_name_fmt) + CHAR_NEW_LINE
		else:
			# Orient constraint command
			_output += maya_orientConstraint(_child_name, _command, _target_name) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) SCALE CONSTRAINT
## ==========================================================================
def script_scale_constraint(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 2:
			continue

		_child_name = _command_parameters[0]
		_target_name = _command_parameters[1]

		if 'batch' in statement and len(_command_parameters) > 2:
			_child_name_fmt = to_obj(to_format_str(OBJ_NAME, quote_str(_command_parameters[1])))
			_target_name_fmt = to_obj(to_format_str(OBJ_NAME, quote_str(_command_parameters[2])))

			# For loop script
			_output += custom_script_foreach(maya_listRelatives(_child_name)) + CHAR_NEW_LINE

			# Scale constraint command
			_output += CHAR_TAB + maya_scaleConstraint(_child_name_fmt, _command, _target_name_fmt) + CHAR_NEW_LINE

			_child_name_fmt = _child_name_fmt.replace(OBJ_NAME, quote_str(_child_name))
			_target_name_fmt = _target_name_fmt.replace(OBJ_NAME, quote_str(_child_name))

			_output += maya_scaleConstraint(_child_name_fmt, _command, _target_name_fmt) + CHAR_NEW_LINE
		else:
			# Scale constraint command
			_output += maya_scaleConstraint(_child_name, _command, _target_name) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) POLE CONSTRAINT
## ==========================================================================
def script_pole_constraint(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 3:
			continue

		_name = _command_parameters[0]
		_target = _command_parameters[1]
		_handle = _command_parameters[2]

		# Pole vector constraint command
		_output += maya_poleVectorConstraint(_name, _target, _handle, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) PARENT
## ==========================================================================
def script_parent(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 2:
			continue

		_name = _command_parameters[0]

		# Parent command
		_output += maya_parent(_name, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) CREATE GROUP
## ==========================================================================
def script_create_group(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 1:
			continue

		_name = _command_parameters[0]
		_is_empty = len(_command_parameters) == 1

		# Create group command
		_output += maya_group(_name, _command, _is_empty) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) BIND SKIN
## ==========================================================================
def script_bind_skin(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 2:
			continue

		_name = _command_parameters[0]

		# Bind skin command
		_output += maya_skinCluster(_name, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) SKIN VERTICES
## ==========================================================================
def script_skin_vertices(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 3:
			continue

		_name = _command_parameters[0]
		_mesh_name = _command_parameters[1]

		# Bind skin command
		_output += maya_skinPercent(_name, _mesh_name, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) COPY SKIN WEIGHTS
## ==========================================================================
def script_copy_skin_weights(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 2:
			continue

		_source_skin = _command_parameters[0]
		_destination_skin = _command_parameters[1]

		# Create wrap command
		_output += maya_copySkinWeights(_source_skin, _destination_skin, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) WRAP DEFORM
## ==========================================================================
def script_wrap_deform(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 1:
			continue

		_deformer_obj = _command_parameters[0]

		# Create wrap command
		_output += maya_createWrap(_deformer_obj, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) IK HANDLE
## ==========================================================================
def script_ik_handle(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 3:
			continue

		_name = _command_parameters[0]
		_start_joint = _command_parameters[1]
		_end_effector = _command_parameters[2]

		_output += maya_select(clear = True) + CHAR_NEW_LINE

		# IK Handle command
		_output += maya_ikHandle(_name, _start_joint, _end_effector, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) CREATE LOCATOR
## ==========================================================================
def script_create_locator(statement):
	_output = CHAR_EMPTY

	_name = None

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)

		_name = _command_parameters[0]
		
		# Space locator command
		_output += maya_spaceLocator(_name) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) RENAME
## ==========================================================================
def script_rename(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 2:
			continue

		_name = _command_parameters[0]
		_new_name = _command_parameters[1]

		# Rename command
		_output += maya_rename(_name, _new_name) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) MOVE
## ==========================================================================
def script_move(statement):
	_output = CHAR_EMPTY

	_value_only = True
	_to_world_position = False

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 4:
			continue

		_name = _command_parameters[0]

		if 'to_world_position' in _command:
			_to_world_position = True

		if 'relative_to' in _command:
			_ref_name = get_parameter_key_value_pair(_command, 'relative_to', _value_only)
			_x = '($x + $ref_list["$ref_name"][0])'.replace('$x', _command_parameters[1]).replace('$ref_list', OBJ_REF_LIST).replace('$ref_name', _ref_name)
			_y = '($y + $ref_list["$ref_name"][1])'.replace('$y', _command_parameters[2]).replace('$ref_list', OBJ_REF_LIST).replace('$ref_name', _ref_name)
			_z = '($z + $ref_list["$ref_name"][2])'.replace('$z', _command_parameters[3]).replace('$ref_list', OBJ_REF_LIST).replace('$ref_name', _ref_name)
		else:
			_x = float(_command_parameters[1])
			_y = float(_command_parameters[2])
			_z = float(_command_parameters[3])

		# Move command
		_output += maya_move(_name, _x, _y, _z, _command, _to_world_position) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) ROTATE
## ==========================================================================
def script_rotate(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 1:
			continue

		_name = _command_parameters[0]

		_var_rotation_value = '_rotation_value'
		_value_only = True

		if 'copy_from' in _command:
			_ref_name = get_parameter_key_value_pair(_command, 'copy_from', _value_only)
			_output += maya_xform(var = _var_rotation_value, name = _ref_name, parameters = 'rotation worldSpace') + CHAR_NEW_LINE
			_x = '{0}.x'.format(_var_rotation_value)
			_y = '{0}.y'.format(_var_rotation_value)
			_z = '{0}.z'.format(_var_rotation_value)
		else:
			try:
				_x = float(_command_parameters[1])
			except ValueError:
				_x = to_maya_obj(_command_parameters[1])

			try:
				_y = float(_command_parameters[2])
			except ValueError:
				_y = to_maya_obj(_command_parameters[2])

			try:
				_z = float(_command_parameters[3])
			except ValueError:
				_z = to_maya_obj(_command_parameters[3])

		# Rotate command
		_output += maya_rotate(_name, _x, _y, _z, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) SCALE
## ==========================================================================
def script_scale(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 4:
			continue

		_name = _command_parameters[0]
		_x = float(_command_parameters[1])
		_y = float(_command_parameters[2])
		_z = float(_command_parameters[3])

		# Scale command
		_output += maya_scale(_name, _x, _y, _z, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) FREEZE
## ==========================================================================
def script_freeze(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 1:
			continue

		_name = _command_parameters[0]

		# Make identity command
		_output += maya_makeIdentity(_name, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) CENTER PIVOT
## ==========================================================================
def script_center_pivot(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 1:
			continue

		_name = _command_parameters[0]

		# Xform command
		_output += maya_xform(_name, 'centerPivots') + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) DUPLICATE
## ==========================================================================
def script_duplicate(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 2:
			continue

		_name = _command_parameters[0]
		_obj = _command_parameters[1]

		# Duplicate command
		_output += maya_duplicate(_name, _obj, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) DELETE
## ==========================================================================
def script_delete(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 1:
			continue

		_name = _command_parameters[0]

		# Delete command
		_output += maya_delete(_name, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) CREATE CIRCLE
## ==========================================================================
def script_create_circle(statement):
	_output = CHAR_EMPTY

	_x = _y = _z = 0
	_value_only = True

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 5:
			continue

		_name = _command_parameters[0]

		if 'relative_to' in _command:
			_ref_name = get_parameter_key_value_pair(_command, 'relative_to', _value_only)
			_x = '($x + $ref_list["$ref_name"][0])'.replace('$x', _command_parameters[1]).replace('$ref_list', OBJ_REF_LIST).replace('$ref_name', _ref_name)
			_y = '($y + $ref_list["$ref_name"][1])'.replace('$y', _command_parameters[2]).replace('$ref_list', OBJ_REF_LIST).replace('$ref_name', _ref_name)
			_z = '($z + $ref_list["$ref_name"][2])'.replace('$z', _command_parameters[3]).replace('$ref_list', OBJ_REF_LIST).replace('$ref_name', _ref_name)
		else:
			_x = float(_command_parameters[1])
			_y = float(_command_parameters[2])
			_z = float(_command_parameters[3])

		# Create circle command
		_output += maya_circle(_name, _x, _y, _z, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) CREATE CURVE
## ==========================================================================
def script_create_curve(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 3:
			continue

		_name = _command_parameters[0]

		# Create curve command
		_output += maya_curve(_name, _command) + CHAR_NEW_LINE

		# Rename curve
		_curve_shape_name = 'curveShape1'
		_new_curve_shape_name = to_obj(LAST_OBJ_NAME + ' + "Shape"')
		_output += maya_rename(_curve_shape_name, _new_curve_shape_name) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) ADD ATTRIBUTE
## ==========================================================================
def script_add_attribute(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 3:
			continue

		_name = _command_parameters[0]
		_long_name = _command_parameters[1]
		_attribute_type = _command_parameters[2]

		# Set attribute command
		_output += maya_addAttr(_name, _long_name, _attribute_type, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) SET ATTRIBUTE
## ==========================================================================
def script_set_attribute(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 2:
			continue

		_attribute = _command_parameters[0]
		_value = _command_parameters[1]

		# Extract and parse object names (multi-command)
		_objs = extract_param_objs(_command)
		if len(_objs) > 1:
			# Multi-command request
			for _obj in _objs:
				# Set attribute command
				_output += maya_setAttr(_attribute + SCRIPT_SYMBOL_ATTRIBUTE + _obj, _value, _command) + CHAR_NEW_LINE
		else:
			# Set attribute command
			_output += maya_setAttr(_attribute, _value, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) CONNECT ATTRIBUTE
## ==========================================================================
def script_connect_attribute(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 2:
			continue

		_param1 = _command_parameters[0]
		_param2 = _command_parameters[1]
		_param3 = None
		if len(_command_parameters) > 2:
			_param3 = _command_parameters[2]

		if 'batch' in statement and len(_command_parameters) > 4:
			# Batch command mode (iterate on object hierarchy)
			_obj_name = _param1
			_source_fmt = to_format_str(OBJ_NAME, quote_str(_param2)) + ' + '
			_dest_fmt = to_format_str(OBJ_NAME, quote_str(_param3)) + ' + '

			# For loop script
			_output += custom_script_foreach(maya_listRelatives(_obj_name)) + CHAR_NEW_LINE

			# Extract and parse attributes (multi-command)
			_attributes = extract_param_objs(_command, SCRIPT_SYMBOL_ATTRIBUTE)
			if len(_attributes) > 0:
				# Multiple attributes

				# Connect attributes for child objects
				for _attribute in _attributes:
					_source_attribute = to_obj(_source_fmt + quote_str(_attribute))
					_dest_attribute = to_obj(_dest_fmt + quote_str(_attribute))

					# Connect attribute command
					_output += CHAR_TAB + maya_connectAttr(_source_attribute, _dest_attribute, _command) + CHAR_NEW_LINE

				# Connect attributes for parent object
				for _attribute in _attributes:
					_source_attribute = to_obj(_source_fmt.replace(OBJ_NAME, quote_str(_param1)) + quote_str(_attribute))
					_dest_attribute = to_obj(_dest_fmt.replace(OBJ_NAME, quote_str(_param1)) + quote_str(_attribute))

					# Connect attribute command
					_output += maya_connectAttr(_source_attribute, _dest_attribute, _command) + CHAR_NEW_LINE
			else:
				# No attributes supplied
				pass
		else:
			# Single command mode
			_source_attribute = _param1

			# Extract and parse attributes (multi-command)
			_dest_attributes = extract_param_objs(_command)
			if len(_dest_attributes) > 0:
				# Multiple destination attributes
				for _dest_attribute in _dest_attributes:

					# Connect attribute command
					_output += maya_connectAttr(_source_attribute, _dest_attribute, _command) + CHAR_NEW_LINE
			else:
				# Single destination attribute
				_dest_attribute = _param2

				# Connect attribute command
				_output += maya_connectAttr(_source_attribute, _dest_attribute, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) SET DRIVEN KEY
## ==========================================================================
def script_set_driven_key(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 3:
			continue

		_currentDriver = _command_parameters[0]

		# Parse driver value (optional)
		_driverValue = _command_parameters[1]
		if _driverValue[-1] != '-':
			_command += ' driverValue=' + _driverValue

		# Parse driven value (optional)
		_drivenValue = _command_parameters[2]
		if _drivenValue[-1] != '-':
			if 'reference_attribute' in _command:
				_ref_attrib = get_parameter_key_value_pair(_command, 'reference_attribute', True)
				_drivenValue = 'cmds.getAttr("$ref_attrib")+'.replace('$ref_attrib', _ref_attrib) + _drivenValue

			_command += ' value=' + _drivenValue

		# Set driven keyframe command
		_output += maya_setDrivenKeyframe(_currentDriver, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) CREATE NODE
## ==========================================================================
def script_create_node(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 2:
			continue

		_name = _command_parameters[0]
		_node = _command_parameters[1]

		# Create node command
		_output += maya_createNode(_name, _node) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) CREATE LAYER
## ==========================================================================
def script_create_layer(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 1:
			continue

		_name = _command_parameters[0]

		# Create layer command
		_output += maya_createDisplayLayer(_name) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) EDIT LAYER
## ==========================================================================
def script_edit_layer(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 2:
			continue

		_node = _command_parameters[0]

		# Edit layer command
		_output += maya_editDisplayLayerMembers(_node, _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) KEY TANGENT
## ==========================================================================
def script_key_tangent(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 3:
			continue

		# Key tangent command
		_output += maya_keyTangent(_command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) SET INFINITY
## ==========================================================================
def script_set_infinity(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 3:
			continue

		# Set infinity command
		_output += maya_setInfinity(_command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) XFORM VAR
## ==========================================================================
def script_xform_var(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 3:
			continue

		_var = _command_parameters[0]
		_name = _command_parameters[1]

		# Xform command
		_output += maya_xform(var = _var, name = _name, parameters = _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) XFORM REF
## ==========================================================================
def script_xform_ref(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 2:
			continue

		_ref = _command_parameters[0]

		# Xform command
		_output += maya_xform(ref = _ref, name = _ref, parameters = _command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) CLEAR VARS
## ==========================================================================
def script_clear_vars(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 1:
			continue

		# Clear vars
		_output += custom_script_clear_vars(_command) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) CREATE DISTANCE
## ==========================================================================
def script_create_distance(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 3:
			continue

		_name = _command_parameters[0]
		_start = _command_parameters[1]
		_end = _command_parameters[2]

		# Get object position references
		_start_x = '$ref_list["$ref_name"][0]'.replace('$ref_list', OBJ_REF_LIST).replace('$ref_name', _start)
		_start_y = '$ref_list["$ref_name"][1]'.replace('$ref_list', OBJ_REF_LIST).replace('$ref_name', _start)
		_start_z = '$ref_list["$ref_name"][2]'.replace('$ref_list', OBJ_REF_LIST).replace('$ref_name', _start)
		_end_x = '$ref_list["$ref_name"][0]'.replace('$ref_list', OBJ_REF_LIST).replace('$ref_name', _end)
		_end_y = '$ref_list["$ref_name"][1]'.replace('$ref_list', OBJ_REF_LIST).replace('$ref_name', _end)
		_end_z = '$ref_list["$ref_name"][2]'.replace('$ref_list', OBJ_REF_LIST).replace('$ref_name', _end)

		# Distance dimension command
		_name_start_locator = _name + '_start_LOC'
		_name_end_locator = _name + '_end_LOC'
		_name_distance = _name + '_DIST'

		_attribute_start_locator = _name_start_locator + 'Shape.worldPosition[0]'
		_attribute_end_locator = _name_end_locator + 'Shape.worldPosition[0]'
		_attribute_distance_start_point = _name_distance + 'Shape.startPoint'
		_attribute_distance_end_point = _name_distance + 'Shape.endPoint'

		_connect_attribute_params = 'force'
		_verify_connection = True

		_output += maya_spaceLocator(_name_start_locator) + CHAR_NEW_LINE
		_output += maya_move(_name_start_locator, _start_x, _start_y, _start_z, CHAR_EMPTY) + CHAR_NEW_LINE
		_output += maya_spaceLocator(_name_end_locator) + CHAR_NEW_LINE
		_output += maya_move(_name_end_locator, _end_x, _end_y, _end_z, CHAR_EMPTY) + CHAR_NEW_LINE
		_output += maya_distanceDimension(_start_x, _start_y, _start_z, _end_x, _end_y, _end_z) + CHAR_NEW_LINE
		_output += maya_rename('distanceDimension1', _name_distance) + CHAR_NEW_LINE
		_output += maya_connectAttr(_attribute_start_locator, _attribute_distance_start_point, _connect_attribute_params, _verify_connection) + CHAR_NEW_LINE
		_output += maya_connectAttr(_attribute_end_locator, _attribute_distance_end_point, _connect_attribute_params, _verify_connection) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) FIND REPLACE
## ==========================================================================
def script_find_replace(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 3:
			continue

		_name = _command_parameters[0]
		_search = _command_parameters[1]
		_replace_with = _command_parameters[2]

		# Find replace command
		_output += custom_script_searchReplaceNames(_name, _search, _replace_with) + CHAR_NEW_LINE

	# Clear selection
	_output += maya_select(clear = True) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) RENAME PREFIX
## ==========================================================================
def script_rename_prefix(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 2:
			continue

		_name = _command_parameters[0]
		_prefix = _command_parameters[1]

		# Custom script
		_output += custom_script_rename_prefix(_name, _prefix) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (COMPOUND SCRIPT) RENAME SUFFIX
## ==========================================================================
def script_rename_suffix(statement):
	_output = CHAR_EMPTY

	# Command loop
	for _command in split(statement, SCRIPT_COMMAND_DELIMITER):
		# Split command parameters
		_command_parameters = split(_command, SCRIPT_PARAMETER_DELIMITER)
		if len(_command_parameters) < 2:
			continue

		_name = _command_parameters[0]
		_suffix = _command_parameters[1]

		# Custom script
		_output += custom_script_rename_suffix(_name, _suffix) + CHAR_NEW_LINE

	return _output

## ==========================================================================
##	 (MAYA SCRIPT) SELECT
## ==========================================================================
def maya_select(objs = None, clear = False, add = False):
	_command = None

	if clear:
		# Clear selection command
		_command = 'cmds.select(clear=True)'
	elif add:
		# Add to selection command
		_command = 'cmds.select($objs, add=True)'
	else:
		# Select command
		_command = 'cmds.select($objs)'

	if objs is not None:
		_command = _command.replace('$objs', objs)

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) JOINT
## ==========================================================================
def maya_joint(name, x = None, y = None, z = None, edit = False, new_name = None, parameters = None):
	_command = CHAR_EMPTY

	if not edit:
		# Create joint command
		_command = 'cmds.joint(name=$name, position=($X, $Y, $Z))' \
			.replace('$name', to_maya_obj(name)) \
			.replace('$X', str(x)) \
			.replace('$Y', str(y)) \
			.replace('$Z', str(z))
	else:
		if x is not None and y is not None and z is not None:
			if new_name is None:
				new_name = name

			# Edit existing joint command
			_command = 'cmds.joint($name, edit=True, relative=True, component=True, position=($X, $Y, $Z), name=$newName, $zeroScaleOrient, $orientJoint, $secondaryAxisOrient, $setPreferredAngles, $children)' \
				.replace('$name', to_maya_obj(name)) \
				.replace('$X', str(x)) \
				.replace('$Y', str(y)) \
				.replace('$Z', str(z)) \
				.replace('$newName', to_maya_obj(new_name))
		else:
			# Edit existing joint command
			_command = 'cmds.joint($name, edit=True, $zeroScaleOrient, $orientJoint, $secondaryAxisOrient, $setPreferredAngles, $children)' \
				.replace('$name', to_maya_obj(name))

		# Populate command's parameters
		_command = populate_command_parameters(_command, parameters, default_section='CREATE_JOINT')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) INSERT JOINT
## ==========================================================================
def maya_insertJoint(name):
	# Insert joint command
	return 'cmds.insertJoint($name)' \
			.replace('$name', to_maya_obj(name))

## ==========================================================================
##	 (MAYA SCRIPT) MIRROR JOINT
## ==========================================================================
def maya_mirrorJoint(name, parameters):
	# Mirror joint command
	_command = 'cmds.mirrorJoint($name, $mirrorBehavior, $mirrorXY|mirrorYZ|mirrorXZ, $searchReplace)' \
		.replace('$name', to_maya_obj(name))

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='MIRROR_JOINT')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) PARENT CONSTRAINT
## ==========================================================================
def maya_parentConstraint(child_name, parameters, target_name = CHAR_EMPTY):
	_command = CHAR_EMPTY

	# Extract and parse object names
	_targets = ', '.join(quote_str('{}').format(obj) for obj in extract_param_objs(parameters))

	if _targets is not CHAR_EMPTY:
		# Parent constraint command
		_command = 'cmds.parentConstraint($targets, $child_name, $maintainOffset, $weight)' \
			.replace('$targets', _targets) \
			.replace('$child_name', to_maya_obj(child_name))
	else:
		# Parent constraint command
		_command = 'cmds.parentConstraint($target_name, $child_name, $maintainOffset, $weight)' \
			.replace('$target_name', to_maya_obj(target_name)) \
			.replace('$child_name', to_maya_obj(child_name))

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='PARENT_CONSTRAINT')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) POINT CONSTRAINT
## ==========================================================================
def maya_pointConstraint(child_name, parameters, target_name = CHAR_EMPTY):
	_command = CHAR_EMPTY

	# Extract and parse object names
	_targets = ', '.join(quote_str('{}').format(obj) for obj in extract_param_objs(parameters))

	if _targets is not CHAR_EMPTY:
		# Point constraint command
		_command = 'cmds.pointConstraint($targets, $child_name)' \
			.replace('$targets', _targets) \
			.replace('$child_name', to_maya_obj(child_name))
	else:
		# Point constraint command
		_command = 'cmds.pointConstraint($target_name, $child_name)' \
			.replace('$target_name', to_maya_obj(target_name)) \
			.replace('$child_name', to_maya_obj(child_name))

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='POINT_CONSTRAINT')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) ORIENT CONSTRAINT
## ==========================================================================
def maya_orientConstraint(child_name, parameters, target_name = CHAR_EMPTY):
	_command = CHAR_EMPTY

	# Extract and parse object names
	_targets = ', '.join(quote_str('{}').format(obj) for obj in extract_param_objs(parameters))

	if _targets is not CHAR_EMPTY:
		# Orient constraint command
		_command = 'cmds.orientConstraint($targets, $child_name)' \
			.replace('$targets', _targets) \
			.replace('$child_name', to_maya_obj(child_name))
	else:
		# Orient constraint command
		_command = 'cmds.orientConstraint($target_name, $child_name)' \
			.replace('$target_name', to_maya_obj(target_name)) \
			.replace('$child_name', to_maya_obj(child_name))

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='ORIENT_CONSTRAINT')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) SCALE CONSTRAINT
## ==========================================================================
def maya_scaleConstraint(child_name, parameters, target_name = CHAR_EMPTY):
	_command = CHAR_EMPTY

	# Extract and parse object names
	_targets = ', '.join(quote_str('{}').format(obj) for obj in extract_param_objs(parameters))

	if _targets is not CHAR_EMPTY:
		# Scale constraint command
		_command = 'cmds.scaleConstraint($targets, $child_name, $maintainOffset, $weight)' \
			.replace('$targets', _targets) \
			.replace('$child_name', to_maya_obj(child_name))
	else:
		# Scale constraint command
		_command = 'cmds.scaleConstraint($target_name, $child_name, $maintainOffset, $weight)' \
			.replace('$target_name', to_maya_obj(target_name)) \
			.replace('$child_name', to_maya_obj(child_name))

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='SCALE_CONSTRAINT')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) POLE VECTOR CONSTRAINT
## ==========================================================================
def maya_poleVectorConstraint(name, target, handle, parameters):
	_command = CHAR_EMPTY

	# Pole vector constraint command
	_command = 'cmds.poleVectorConstraint($target, $handle, name=$name, $weight)' \
		.replace('$target', to_maya_obj(target)) \
		.replace('$handle', to_maya_obj(handle)) \
		.replace('$name', to_maya_obj(name))

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='POLE_CONSTRAINT')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) PARENT
## ==========================================================================
def maya_parent(name, parameters):
	_command = CHAR_EMPTY

	# Extract and parse object names
	_objs = ', '.join(quote_str('{}').format(obj) for obj in extract_param_objs(parameters))

	if 'world' not in parameters:
		# Parent command
		_command = 'cmds.parent($objs, $name, $relative, $shape)' \
			.replace('$objs', _objs) \
			.replace('$name', to_maya_obj(name))
	else:
		# Unparent command
		_command = 'cmds.parent($name, world=True)' \
			.replace('$name', to_maya_obj(name)) \

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='PARENT')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) GROUP
## ==========================================================================
def maya_group(name, parameters, is_empty = False):
	_command = CHAR_EMPTY

	# Extract and parse object names
	_objs = ', '.join(quote_str('{}').format(obj) for obj in extract_param_objs(parameters))

	if is_empty:
		# Parent command
		_command = 'cmds.group(name=$name, empty=True)' \
			.replace('$name', to_maya_obj(name))
	else:
		# Unparent command
		_command = 'cmds.group($objs, name=$name)' \
			.replace('$objs', _objs) \
			.replace('$name', to_maya_obj(name))

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) SKIN CLUSTER
## ==========================================================================
def maya_skinCluster(name, parameters):
	_command = CHAR_EMPTY

	_value_only = True

	# Extract and parse object names
	_objs = ', '.join(quote_str('{}').format(obj) for obj in extract_param_objs(parameters))

	if not _objs is CHAR_EMPTY:
		# Skin cluster command
		_command = 'cmds.skinCluster($objs, name=$name, $bindMethod, $heatmapFalloff, $skinMethod, $normalizeWeights, $weightDistribution, $maximumInfluences, $obeyMaxInfluences, $dropoffRate, $removeUnusedInfluence)' \
			.replace('$objs', _objs) \
			.replace('$name', to_maya_obj(name))
	else:
		# Skin cluster command
		_add_influence_object = get_parameter_key_value_pair(parameters, 'addInfluence', _value_only)
		_remove_influence_object = get_parameter_key_value_pair(parameters, 'removeInfluence', _value_only)

		if _add_influence_object is not None:
			_command = \
				'if $influence_object not in cmds.skinCluster($name, query=True, influence=True):' \
				'	cmds.skinCluster($name, edit=True, $addInfluence)' \
					.replace('$influence_object', _add_influence_object)
		elif _remove_influence_object is not None:
			_command = \
				'if $influence_object in cmds.skinCluster($name, query=True, influence=True):' \
				'	cmds.skinCluster($name, edit=True, $addInfluence, $removeInfluence)' \
				.replace('$influence_object', _remove_influence_object)

		_command = _command.replace('$name', to_maya_obj(name))

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='BIND_SKIN')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) SKIN PERCENT
## ==========================================================================
def maya_skinPercent(name, mesh_name, parameters):
	_command = CHAR_EMPTY

	# Extract and parse object names
	_objs = extract_param_objs(parameters)

	# Parse mesh parameters
	_mesh_parameters = CHAR_EMPTY
	_transform_value_list = []
	if len(_objs) == 2:
		# With vertices
		_vertex_list = _objs[0]
		_transform_value_list = _objs[1]

		_mesh_parameters = ', '.join(quote_str('$mesh_name.vtx[{0}]').format(vertex) for vertex in _vertex_list)
		_mesh_parameters = _mesh_parameters.replace('$mesh_name', mesh_name)
	elif len(_objs) == 1:
		# Without vertices
		_transform_value_list = _objs
		_mesh_parameters = quote_str(mesh_name)
	else:
		# Incorrect parameter count
		return

	# Parse transformValue parameters
	_transform_values = 'transformValue=[' + \
		', '.join(('(' + quote_str('{0}') + ', {1})') \
		.format( \
			value[:value.rfind('=')] \
			, value[value.rfind('=') + 1:] \
		) for value in _transform_value_list) \
		+ ']'

	# Skin percent command
	_command = 'cmds.skinPercent($name, $mesh_parameters, $transform_values)' \
		.replace('$name', to_maya_obj(name)) \
		.replace('$mesh_parameters', _mesh_parameters) \
		.replace('$transform_values', _transform_values)

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='SKIN_VERTICES')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) COPY SKIN WEIGHTS
## ==========================================================================
def maya_copySkinWeights(source_skin, destination_skin, parameters):
	# Copy skin weights
	_command = 'cmds.copySkinWeights(sourceSkin=$source_skin, destinationSkin=$destination_skin, $noMirror, $surfaceAssociation, $influenceAssociation)' \
		.replace('$source_skin', to_maya_obj(source_skin)) \
		.replace('$destination_skin', to_maya_obj(destination_skin)) \

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='COPY_SKIN_WEIGHTS')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) CREATE WRAP
## ==========================================================================
def maya_createWrap(deformer_obj, parameters):
	_command = CHAR_EMPTY

	# Extract and parse object names
	_influence_objs = ', '.join(quote_str('{}').format(obj) for obj in extract_param_objs(parameters))

	_command = maya_select(objs = _influence_objs) + CHAR_NEW_LINE \
		+ maya_select(objs = to_maya_obj(deformer_obj), add = True) + CHAR_NEW_LINE

	# Create wrap
	_command += 'cmds.CreateWrap()'

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) IK HANDLE
## ==========================================================================
def maya_ikHandle(name, start_joint, end_effector, parameters):
	_command = CHAR_EMPTY

	# Curve option
	if 'curve' in parameters:
		parameters += ' createCurve=False' # No auto-create curve parameter

	# IK Handle command
	_command = 'cmds.ikHandle(startJoint=$start_joint, endEffector=$end_effector, name=$name, $solver, $createCurve, $curve)' \
		.replace('$start_joint', to_maya_obj(start_joint)) \
		.replace('$end_effector', to_maya_obj(end_effector)) \
		.replace('$name', to_maya_obj(name))

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='IK_HANDLE')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) SPACE LOCATOR
## ==========================================================================
def maya_spaceLocator(name):
	# Space locator command
	return 'cmds.spaceLocator(name=$name)' \
		.replace('$name', to_maya_obj(name))

## ==========================================================================
##	 (MAYA SCRIPT) RENAME
## ==========================================================================
def maya_rename(name, new_name):
	# Rename command
	return 'cmds.rename($name, $new_name)' \
		.replace('$name', to_maya_obj(name)) \
		.replace('$new_name', to_maya_obj(new_name))

## ==========================================================================
##	 (MAYA SCRIPT) MOVE
## ==========================================================================
def maya_move(name, x, y, z, parameters, to_world_position = False):
	_command = CHAR_EMPTY

	_prefix = name + '.'

	# Extract and parse object names
	_objs = None
	_obj_list = extract_param_objs(parameters, _prefix)
	if len(_obj_list) > 1:
		# Multi-attribute object (i.e., scalePivot and rotatePivot)
		_objs = ', '.join(quote_str('{}').format(obj) for obj in extract_param_objs(parameters, _prefix))
	else:
		_objs = quote_str(name)

	# Move command
	_command = 'cmds.move($X, $Y, $Z, $objs, $relative, $rotatePivotRelative, $objectSpace, $worldSpaceDistance)'

	if to_world_position:
		_local_position_x = '-cmds.getAttr("$name.localPositionX"))'.replace('$name', name)
		_local_position_y = '-cmds.getAttr("$name.localPositionY"))'.replace('$name', name)
		_local_position_z = '-cmds.getAttr("$name.localPositionZ"))'.replace('$name', name)

		_command = _command \
			.replace('$X', '(' + str(x) + _local_position_x) \
			.replace('$Y', '(' + str(y) + _local_position_y) \
			.replace('$Z', '(' + str(z) + _local_position_z) \
			.replace('$objs', _objs)
	else:
		_command = _command \
			.replace('$X', str(x)) \
			.replace('$Y', str(y)) \
			.replace('$Z', str(z)) \
			.replace('$objs', _objs)

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='MOVE')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) ROTATE
## ==========================================================================
def maya_rotate(name, x, y, z, parameters):
	_command = CHAR_EMPTY

	# Rotate command
	_command = 'cmds.rotate($X, $Y, $Z, $name, $euler, $worldSpace, $relative)' \
		.replace('$X', str(x)) \
		.replace('$Y', str(y)) \
		.replace('$Z', str(z)) \
		.replace('$name', to_maya_obj(name)) \

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='ROTATE')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) SCALE
## ==========================================================================
def maya_scale(name, x, y, z, parameters):
	_command = CHAR_EMPTY

	# Scale command
	_command = 'cmds.scale($X, $Y, $Z, $name, $relative)' \
		.replace('$X', str(x)) \
		.replace('$Y', str(y)) \
		.replace('$Z', str(z)) \
		.replace('$name', to_maya_obj(name)) \

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='SCALE')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) MAKE IDENTITY
## ==========================================================================
def maya_makeIdentity(name, parameters):
	_command = CHAR_EMPTY

	# Make identity command
	_command = 'cmds.makeIdentity($name, $apply, $translate, $rotate, $scale, $jointOrient)' \
		.replace('$name', to_maya_obj(name)) \

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='FREEZE')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) DUPLICATE
## ==========================================================================
def maya_duplicate(name, obj, parameters):
	_command = CHAR_EMPTY

	# Duplicate command
	_command = 'cmds.duplicate($obj, name=$name, $parentOnly, $returnRootsOnly, $upstreamNodes)' \
		.replace('$obj', to_maya_obj(obj)) \
		.replace('$name', to_maya_obj(name))

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='DUPLICATE')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) DELETE
## ==========================================================================
def maya_delete(name, parameters):
	_command = CHAR_EMPTY

	# Extract and parse object names
	_objs = ', '.join(quote_str('{}').format(obj) for obj in extract_param_objs(parameters))

	# Duplicate command
	if _objs is CHAR_EMPTY:
		_command = 'cmds.delete($name)' \
			.replace('$name', to_maya_obj(name))
	else:
		_command = 'cmds.delete($objs)' \
			.replace('$objs', _objs)

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) CIRCLE
## ==========================================================================
def maya_circle(name, x, y, z, parameters):
	_command = CHAR_EMPTY

	# Create circle command
	_command = 'cmds.circle(name=$name, center=($X, $Y, $Z), $radius, $constructionHistory, $object)' \
		.replace('$name', to_maya_obj(name)) \
		.replace('$X', str(x)) \
		.replace('$Y', str(y)) \
		.replace('$Z', str(z))

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='CREATE_CIRCLE')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) CURVE
## ==========================================================================
def maya_curve(name, parameters):
	_command = CHAR_EMPTY

	# Extract and parse vectors
	_vector_list = extract_param_objs(parameters)

	# Convert vector list to point value format
	_pos = 0
	_point = 'point=[('

	for _vector in _vector_list:
		_point += _vector + ', '

		_pos += 1
		if _pos % 3 == 0:
			pos = 0
			_point = _point[:-2] + '), ('

	_point = _point[:-3] + ']'

	# Create circle command
	_command = LAST_OBJ_NAME + ' = cmds.curve(name=$name, $degree, $point)' \
		.replace('$name', to_maya_obj(name)) \
		.replace('$point', _point)

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='CREATE_CURVE')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) ADD ATTR
## ==========================================================================
def maya_addAttr(name, long_name, attribute_type, parameters):
	_command = CHAR_EMPTY

	# Extract objects as enum
	_enum_names = SCRIPT_ENUM_DELIMITER.join(extract_param_objs(parameters))

	# Add attribute command
	_command = 'cmds.addAttr($name, longName=$long_name, $niceName, attributeType=$attribute_type, $enumName, $minValue, $maxValue, $defaultValue, $keyable)' \
		.replace('$name', to_maya_obj(name)) \
		.replace('$long_name', to_maya_obj(long_name)) \
		.replace('$attribute_type', to_maya_obj(attribute_type))

	# Use enum, if specified
	if _enum_names is not CHAR_EMPTY:
		_enum_names = 'enumName=' + quote_str(_enum_names)
		_command = _command.replace('$enumName', _enum_names)

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='ADD_ATTRIBUTE')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) SET ATTR
## ==========================================================================
def maya_setAttr(attribute, value, parameters):
	_command = CHAR_EMPTY

	_optional_params = '$lock, $keyable, $channelBox'

	try:
		value = str(float(value))
	except ValueError:
		value = to_maya_obj(value)

	# Set attribute command
	_command = 'cmds.setAttr($attribute, $value, $optional_params)' \
		.replace('$attribute', to_maya_obj(attribute)) \
		.replace('$optional_params', _optional_params)

	if SCRIPT_SYMBOL_ATTRIBUTE in value:
		# No value specified
		_command = _command.replace('$value', value)

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='SET_ATTRIBUTE')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) CONNECT ATTR
## ==========================================================================
def maya_connectAttr(first_attribute, second_attribute, parameters, verify_connection = False):
	_command = CHAR_EMPTY

	if verify_connection:
		# Is connected command
		_command = 'if not cmds.isConnected($first_attribute, $second_attribute):' + CHAR_NEW_LINE + CHAR_TAB

	# Connect attribute command
	_command += 'cmds.connectAttr($first_attribute, $second_attribute, $force)'
	_command = _command \
		.replace('$first_attribute', to_maya_obj(first_attribute)) \
		.replace('$second_attribute', to_maya_obj(second_attribute))

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='CONNECT_ATTRIBUTE')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) SET DRIVEN KEYFRAME
## ==========================================================================
def maya_setDrivenKeyframe(currentDriver, parameters):
	_command = CHAR_EMPTY

	# Extract and parse object names
	_objs = extract_param_objs(parameters)
	_driven_objs = ', '.join(quote_str('{}').format(obj) for obj in _objs[0])
	_attributes = ', '.join(quote_str('{}').format(obj) for obj in _objs[1])

	# Set driven keyframe command
	_command = 'cmds.setDrivenKeyframe($driven_objs, attribute=[$attributes], currentDriver=$currentDriver, $driverValue, $value)' \
		.replace('$driven_objs', _driven_objs) \
		.replace('$attributes', _attributes) \
		.replace('$currentDriver', to_maya_obj(currentDriver)) \

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='SET_DRIVEN_KEY')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) CREATE NODE
## ==========================================================================
def maya_createNode(name, node):
	# Create node command
	return 'cmds.createNode($node, name=$name)' \
		.replace('$name', to_maya_obj(name)) \
		.replace('$node', to_maya_obj(node))

## ==========================================================================
##	 (MAYA SCRIPT) CREATE DISPLAY LAYER
## ==========================================================================
def maya_createDisplayLayer(name):
	# Create display layer command
	return 'cmds.createDisplayLayer(name=$name, number=1, empty=True)' \
		.replace('$name', to_maya_obj(name))

## ==========================================================================
##	 (MAYA SCRIPT) EDIT DISPLAY LAYER MEMBERS
## ==========================================================================
def maya_editDisplayLayerMembers(node, parameters):
	_command = CHAR_EMPTY

	# Extract and parse object names
	_objs = ', '.join(quote_str('{}').format(obj) for obj in extract_param_objs(parameters))

	# Edit display layer members command
	_command = 'cmds.editDisplayLayerMembers($node, $objs, $noRecurse)' \
		.replace('$node', to_maya_obj(node)) \
		.replace('$objs', _objs)

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='EDIT_LAYER')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) KEY TANGENT
## ==========================================================================
def maya_keyTangent(parameters):
	_command = CHAR_EMPTY

	# Extract and parse object names
	_param_objs = extract_param_objs(parameters)
	_attributes = ', '.join(quote_str('{}').format(obj) for obj in _param_objs[0])
	_objs = ', '.join(quote_str('{}').format(obj) for obj in _param_objs[1])

	# Key tangent command
	_command = 'cmds.keyTangent($objs, edit=True, attribute=[$attributes], $inTangentType, $outTangentType)' \
		.replace('$objs', _objs) \
		.replace('$attributes', _attributes)

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='KEY_TANGENT')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) SET INFINITY
## ==========================================================================
def maya_setInfinity(parameters):
	_command = CHAR_EMPTY

	# Extract and parse object names
	_param_objs = extract_param_objs(parameters)
	_attributes = ', '.join(quote_str('{}').format(obj) for obj in _param_objs[0])
	_objs = ', '.join(quote_str('{}').format(obj) for obj in _param_objs[1])

	# Set infinity command
	_command = 'cmds.setInfinity($objs, attribute=[$attributes], $preInfinite, $postInfinite)' \
		.replace('$objs', _objs) \
		.replace('$attributes', _attributes)

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='SET_INFINITY')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) XFORM
## ==========================================================================
def maya_xform(name, parameters, var = None, ref = None):
	_command = CHAR_EMPTY

	if var is not None:
		# Xform command
		_command = \
			'class $var: pass' + CHAR_NEW_LINE \
			+ '$vector = cmds.xform($name, query=True, $worldSpace, $translation|rotation)' + CHAR_NEW_LINE \
			+ '$var.x = $vector[0]' \
			+ '; $var.y = $vector[1]' \
			+ '; $var.z = $vector[2]' + CHAR_NEW_LINE \
			+ '$vector = None'

		_command = _command \
			.replace('$var', var) \
			.replace('$vector', OBJ_VECTOR) \
			.replace('$name', to_maya_obj(name))
	elif ref is not None:
		# Xform command
		_command = \
			'$vector = cmds.xform($name, query=True, $worldSpace, $translation|rotation)' + CHAR_NEW_LINE + \
			'$ref_list["$ref_name"] = $vector' + CHAR_NEW_LINE

		_command = _command \
			.replace('$ref_name', ref) \
			.replace('$ref_list', OBJ_REF_LIST) \
			.replace('$vector', OBJ_VECTOR) \
			.replace('$name', to_maya_obj(name))
	else:
		# Xform command
		_command = 'cmds.xform($name, centerPivots=True)' \
			.replace('$name', to_maya_obj(name))

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='XFORM')

	return _command

## ==========================================================================
##	 (MAYA SCRIPT) DISTANCE DIMENSION
## ==========================================================================
def maya_distanceDimension(start_x, start_y, start_z, end_x, end_y, end_z):
	# Distance dimension command
	return 'cmds.distanceDimension(startPoint=($start_x, $start_y, $start_z), endPoint=($end_x, $end_y, $end_z))' \
		.replace('$start_x', str(start_x)) \
		.replace('$start_y', str(start_y)) \
		.replace('$start_z', str(start_z)) \
		.replace('$end_x', str(end_x)) \
		.replace('$end_y', str(end_y)) \
		.replace('$end_z', str(end_z))

## ==========================================================================
##	 (MAYA SCRIPT) LIST RELATIVES
## ==========================================================================
def maya_listRelatives(obj, parameters = CHAR_EMPTY):
	_command = CHAR_EMPTY

	# List relatives
	_command = 'cmds.listRelatives($obj, allDescendents=True, path=True, $type)' \
		.replace('$obj', to_maya_obj(obj))

	# Populate command's parameters
	_command = populate_command_parameters(_command, parameters, default_section='LIST_RELATIVES')

	return _command

## ==========================================================================
##	 (CUSTOM PYTHON SCRIPT) SEARCH REPLACE NAMES
## ==========================================================================
def custom_script_move_joint(name, x, y, z):
	_script = \
		'_tmp_parent_node = cmds.listRelatives("$name", parent=True, fullPath=True)' + CHAR_NEW_LINE + \
		'if _tmp_parent_node is not None:' + CHAR_NEW_LINE + \
		'	cmds.parent("$name", world=True)' + CHAR_NEW_LINE + \
		'cmds.move($x, $y, $z, "$name")' + CHAR_NEW_LINE + \
		'if _tmp_parent_node is not None:' + CHAR_NEW_LINE + \
		'	cmds.parent("$name", _tmp_parent_node)'

	_script = _script \
		.replace('$name', name) \
		.replace('$x', str(x)) \
		.replace('$y', str(y)) \
		.replace('$z', str(z))

	return _script

## ==========================================================================
##	 (CUSTOM PYTHON SCRIPT) SEARCH REPLACE NAMES
## ==========================================================================
def custom_script_searchReplaceNames(name, search, replace_with):
	_script = \
		'$foreach' + CHAR_NEW_LINE + \
		'	_tmp_shortname = $OBJ_NAME' + CHAR_NEW_LINE + \
		'	if "|" in $OBJ_NAME:' + CHAR_NEW_LINE + \
		'		_tmp_shortname = $OBJ_NAME[$OBJ_NAME.rfind("|") + 1:]' + CHAR_NEW_LINE + \
		'	cmds.rename($OBJ_NAME, _tmp_shortname.replace($search, $replace_with))' + CHAR_NEW_LINE + \
		'cmds.rename($name, $name[$name.rfind("|") + 1:].replace($search, $replace_with))'

	_script = _script \
		.replace('$foreach', custom_script_foreach(maya_listRelatives(name))) \
		.replace('$OBJ_NAME', OBJ_NAME) \
		.replace('$name', to_maya_obj(name)) \
		.replace('$search', to_maya_obj(search)) \
		.replace('$replace_with', to_maya_obj(replace_with))

	return _script

## ==========================================================================
##	 (CUSTOM PYTHON SCRIPT) FOREACH
## ==========================================================================
def custom_script_foreach(objs):
	return 'for $OBJ_NAME in $objs:' \
		.replace('$OBJ_NAME', OBJ_NAME) \
		.replace('$objs', objs)

## ==========================================================================
##	 (CUSTOM PYTHON SCRIPT) RENAME PREFIX
## ==========================================================================
def custom_script_rename_prefix(name, prefix):
	_script = \
		'$foreach' + CHAR_NEW_LINE + \
		'	_tmp_shortname = $OBJ_NAME' + CHAR_NEW_LINE + \
		'	if "|" in $OBJ_NAME:' + CHAR_NEW_LINE + \
		'		_tmp_shortname = $OBJ_NAME[$OBJ_NAME.rfind("|") + 1:]' + CHAR_NEW_LINE + \
		'	cmds.rename($OBJ_NAME, $prefix + _tmp_shortname)' + CHAR_NEW_LINE + \
		'cmds.rename($name, $prefix + $name[$name.rfind("|") + 1:])'

	_script = _script \
		.replace('$foreach', custom_script_foreach(maya_listRelatives(name))) \
		.replace('$OBJ_NAME', OBJ_NAME) \
		.replace('$name', to_maya_obj(name)) \
		.replace('$prefix', to_maya_obj(prefix))

	return _script

## ==========================================================================
##	 (CUSTOM PYTHON SCRIPT) RENAME SUFFIX
## ==========================================================================
def custom_script_rename_suffix(name, suffix):
	_script = \
		'$foreach' + CHAR_NEW_LINE + \
		'	_tmp_shortname = $OBJ_NAME' + CHAR_NEW_LINE + \
		'	if "|" in $OBJ_NAME:' + CHAR_NEW_LINE + \
		'		_tmp_shortname = $OBJ_NAME[$OBJ_NAME.rfind("|") + 1:]' + CHAR_NEW_LINE + \
		'	cmds.rename($OBJ_NAME, _tmp_shortname + $suffix)' + CHAR_NEW_LINE + \
		'cmds.rename($name, $name[$name.rfind("|") + 1:] + $suffix)'

	_script = _script \
		.replace('$foreach', custom_script_foreach(maya_listRelatives(name))) \
		.replace('$OBJ_NAME', OBJ_NAME) \
		.replace('$name', to_maya_obj(name)) \
		.replace('$suffix', to_maya_obj(suffix))

	return _script

## ==========================================================================
##	 (CUSTOM PYTHON SCRIPT) CLEAR VARS
## ==========================================================================
def custom_script_clear_vars(_command):
	_script = CHAR_EMPTY

	_vars = extract_param_objs(_command)
	for _var in _vars:
		_script += '$var = None' \
			.replace('$var', _var) \
			+ CHAR_NEW_LINE

	return _script

## ==========================================================================
##	 Log Info
## ==========================================================================
def logInfo(message):
	_log(LOG_INFO, message)

## ==========================================================================
##	 Log Warn
## ==========================================================================
def logWarn(message):
	_log(LOG_WARN, message)

## ==========================================================================
##	 Log Error
## ==========================================================================
def logError(message):
	_log(LOG_ERROR, message)

## ==========================================================================
##	 Log Debug
## ==========================================================================
def logDebug(message):
	if DEBUG_OUTPUT:
		_log(LOG_DEBUG, message)

## ==========================================================================
##	 Log to console
## ==========================================================================
def _log(type, message):
	print('[$type] Rigathon.$name | \t$message' \
		.replace('$name', APP_NAME.ljust(10)) \
		.replace('$type', type) \
		.replace('$message', message) \
		)

## ==========================================================================
##	 MAIN
## ==========================================================================
# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--script', default='rig_script.txt', help='The RIG script file to process')
parser.add_argument('-o', '--output', default='output.py', help='Output file')
args = parser.parse_args()

# Validate script file
if not os.path.isfile(args.script):
	parser.print_help()
	sys.exit(1)

logInfo('- Reading rigathon script file \'' + args.script + '\'...')
script = read_file(args.script)

logInfo('- Translating script...')
script = clean_up_script(script)
output = translate(script)

logInfo('- Writing to output file \'' + args.output + '\'...')
write_to_file(args.output, output)

logDebug('[DEBUG] Generated output: ' + CHAR_NEW_LINE + output)

logInfo('* DONE!')
