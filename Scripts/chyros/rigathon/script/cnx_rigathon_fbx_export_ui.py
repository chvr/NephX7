import maya.cmds as cmds
import maya.mel as mel

from cnx_rigathon_logger import Logger
from cnx_rigathon_anim_sequences import AnimSequences
from cnx_rigathon_export_layers import ExportLayers

from functools import partial
import os

class FbxExportUI:

	def __init__(self, settings, util, export_location):
		self._logger = Logger(self.__class__.__name__)
		self._settings = settings
		self._util = util
		self._animSequences = AnimSequences(self._settings)
		self._exportLayers = ExportLayers(self._settings)
		self._export_location = export_location

	def create_panel(self, panel_width):
		cmds.frameLayout(self._util.to_ui_name('frm_fbx_export'), label='FBX Export', borderStyle='etchedOut', collapsable=True, collapse=True, enable=False, width=panel_width)

		self._init_anim_sequences_ui()
		self._init_export_layers_ui()

		cmds.setParent(upLevel=True)


# ANIM SEQUENCE ================================================== [ public ]

	def init_anim_sequences(self):
		anim_sequence_names = None
		if cmds.objExists('anim_sequences'):
			anim_sequence_names = cmds.listRelatives('anim_sequences')

		self._animSequences.clear()
		if anim_sequence_names is not None:
			# Load items from settings
			for anim_sequence_name in anim_sequence_names:
				name_value = self._settings.load('name', '', anim_sequence_name, 'anim_sequences')
				start_value = self._settings.load('start', '', anim_sequence_name, 'anim_sequences')
				end_value = self._settings.load('end', '', anim_sequence_name, 'anim_sequences')
				active_value = self._settings.load('active', True, anim_sequence_name, 'anim_sequences')

				self._animSequences.add(name_value, start_value, end_value, active_value)

		if self._animSequences.get_size() == 0:
			# Add default item
			self._animSequences.add('InitialPose', '1', '2', True)
			self._animSequences.add('AnimSeq01', 'start', 'end', True)

		# Update UI
		self._update_anim_sequences_ui()

	def get_anim_sequences(self):
		return self._animSequences

	def add_anim_sequence(self, *args):
		selected_objs = cmds.ls(selection=True)

		self._util.disable_undo()
		try:
			start = str(int(cmds.playbackOptions(query=True, min=True)))
			end = str(int(cmds.playbackOptions(query=True, max=True)))
			name = 'AnimSeq'
			active = True

			anim_sequence = self._animSequences.add(name, start, end, active)
			name = anim_sequence.get_name() + str(anim_sequence.get_index() + 1).zfill(2)
			self.update_anim_sequence(anim_sequence.get_index(), '', 'name', name)

			cmds.evalDeferred(self._update_anim_sequences_ui)
		finally:
			self._util.select_obj(selected_objs)
			self._util.enable_undo()

	def update_anim_sequence(self, idx, widget_name, attribute, value, *args):
		self._util.disable_undo()
		try:
			if attribute == 'name':
				value = self._util.to_proper_name(value)
				self._animSequences.update(idx, name = value)
				if cmds.textField(widget_name, query=True, exists=True):
					cmds.textField(widget_name, edit=True, text=value, annotation=value)
			elif attribute == 'start':
				value = self._to_range_num(value)
				self._animSequences.update(idx, start = value)
				if cmds.textField(widget_name, query=True, exists=True):
					cmds.textField(widget_name, edit=True, text=value, annotation=value)
			elif attribute == 'end':
				value = self._to_range_num(value)
				self._animSequences.update(idx, end = value)
				if cmds.textField(widget_name, query=True, exists=True):
					cmds.textField(widget_name, edit=True, text=value, annotation=value)
			elif attribute == 'active':
				self._animSequences.update(idx, active = value)
		finally:
			self._util.enable_undo()

	def delete_anim_sequence(self, idx, *args):
		selected_objs = cmds.ls(selection=True)
		self._util.disable_undo()
		try:
			self._animSequences.remove(idx)
			cmds.evalDeferred(self._update_anim_sequences_ui)
		finally:
			self._util.select_obj(selected_objs)
			self._util.enable_undo()

	def move_anim_sequence_up(self, idx, *args):
		self._util.disable_undo()
		try:
			moved = self._animSequences.move_up(idx)
			if moved:
				cmds.evalDeferred(self._update_anim_sequences_ui)
		finally:
			self._util.enable_undo()

	def move_anim_sequence_down(self, idx, *args):
		self._util.disable_undo()
		try:
			moved = self._animSequences.move_down(idx)
			if moved:
				cmds.evalDeferred(self._update_anim_sequences_ui)
		finally:
			self._util.enable_undo()


# EXPORT LAYER =================================================== [ public ]

	def init_export_layers(self):
		export_layer_names = None
		if cmds.objExists('export_layers'):
			export_layer_names = cmds.listRelatives('export_layers')

		self._exportLayers.clear()
		if export_layer_names is not None:
			# Load items from settings
			for export_layer_name in export_layer_names:
				name_value = self._settings.load('name', '', export_layer_name, 'export_layers')
				objects_value = self._settings.load('objects', '', export_layer_name, 'export_layers', as_list = True)
				active_value = self._settings.load('active', True, export_layer_name, 'export_layers')

				self._exportLayers.add(name_value, objects_value, active_value)

		# Add export objects from the scene
		fbx_export_layer = self._util.to_node_name('FBX_Export')
		character_name = self._settings.get_ref_name()
		objects = []

		if character_name == '':
			# Set default character name
			character_name = 'Character'

		# Check if it hasn't been added before
		is_new_export_layer = True
		for exportLayer in self._exportLayers.get_list():
			if character_name == exportLayer.get_name():
				is_new_export_layer = False
				break

		# Check that FBX export layer exists
		is_fbx_export_layer_exists = cmds.objExists(fbx_export_layer)

		if is_new_export_layer and is_fbx_export_layer_exists:
			# Get export objects from the scene
			export_objects = cmds.editDisplayLayerMembers(fbx_export_layer, query=True)
			if export_objects is not None and len(export_objects) > 0:
				objects = export_objects

			self._exportLayers.add(character_name, objects, True)

		# Update UI
		self._update_export_layers_ui()

	def get_export_layers(self):
		return self._exportLayers

	def add_export_layer(self, idx):
		selected_objs = cmds.ls(selection=True)
		self._util.disable_undo()
		try:
			name = 'NewLayer'
			active = True

			export_layer = self._exportLayers.add(name, [], active)
			name = export_layer.get_name() + str(export_layer.get_index()).zfill(2)
			self.update_export_layer(export_layer.get_index(), '', 'name', name)

			cmds.evalDeferred(self._update_export_layers_ui)
		finally:
			self._util.select_obj(selected_objs)
			self._util.enable_undo()

	def update_export_layer(self, idx, widget_name, attribute, value, *args):
		self._util.disable_undo()
		try:
			if attribute == 'name':
				value = self._util.to_proper_name(value)
				self._exportLayers.update(idx, name = value)
				if cmds.textField(widget_name, query=True, exists=True):
					cmds.textField(widget_name, edit=True, text=value, annotation=value)
			elif attribute == 'active':
				self._exportLayers.update(idx, active = value)
		finally:
			self._util.enable_undo()

	def delete_export_layer(self, idx, *args):
		selected_objs = cmds.ls(selection=True)
		self._util.disable_undo()
		try:
			self._exportLayers.remove(idx)
			cmds.evalDeferred(self._update_export_layers_ui)
		finally:
			self._util.select_obj(selected_objs)
			self._util.enable_undo()

	def move_export_layer_up(self, idx, *args):
		self._util.disable_undo()
		try:
			moved = self._exportLayers.move_up(idx)
			if moved:
				cmds.evalDeferred(self._update_export_layers_ui)
		finally:
			self._util.enable_undo()

	def move_export_layer_down(self, idx, *args):
		self._util.disable_undo()
		try:
			moved = self._exportLayers.move_down(idx)
			if moved:
				cmds.evalDeferred(self._update_export_layers_ui)
		finally:
			self._util.enable_undo()

	def add_selected_objects_to_layer(self, idx, widget_name, *args):
		self._util.disable_undo()
		try:
			selected_objects = cmds.ls(selection=True)
			added = self._exportLayers.get(idx).add_objects(selected_objects)
			if added:
				objects = self._exportLayers.get(idx).get_objects()
				if objects is None:
					objects = []
				self._exportLayers.update(idx, objects = objects)

				cmds.text(widget_name, edit=True, label=str(self._exportLayers.get(idx).get_size()))
		finally:
			self._util.enable_undo()

	def remove_selected_objects_from_layer(self, idx, widget_name, *args):
		self._util.disable_undo()
		try:
			selected_objects = cmds.ls(selection=True)
			removed = self._exportLayers.get(idx).remove_objects(selected_objects)
			if removed:
				objects = self._exportLayers.get(idx).get_objects()
				if objects is None:
					objects = []
				self._exportLayers.update(idx, objects = objects)

				cmds.text(widget_name, edit=True, label=str(self._exportLayers.get(idx).get_size()))
		finally:
			self._util.enable_undo()

	def empty_objects_from_layer(self, idx, widget_name, *args):
		self._util.disable_undo()
		try:
			emptied = self._exportLayers.get(idx).clear_objects()
			if emptied:
				objects = self._exportLayers.get(idx).get_objects()
				if objects is None:
					objects = []
				self._exportLayers.update(idx, objects = objects)

				cmds.text(widget_name, edit=True, label=str(self._exportLayers.get(idx).get_size()))
		finally:
			self._util.enable_undo()

	def select_objects_from_layer(self, idx, *args):
		export_objects = self._exportLayers.get(idx).get_objects()
		self._util.select_obj(export_objects)

	def fbx_export(self, idx, *args):
		dialog_title = '[Rig-a-thon] FBX Export'

		last_export_name = self._util.load_from_cache('last_export_name', '')
		export_name = self._util.dialog_box_ok_cancel(dialog_title, 'Enter export name:', last_export_name)
		if export_name is None or len(export_name.strip()) == 0:
			# Cancel export
			return

		self._util.save_to_cache('last_export_name', export_name)

		base_export_path = os.path.join(self._export_location, self._util.to_proper_name(export_name))
		if os.path.exists(base_export_path):
			# Export path already exists
			allow_overwrite = self._util.dialog_box_yes_no(dialog_title, 'Export name already exists. Do you want to overwrite existing files?       ')
			if not allow_overwrite:
				return

		# Get selected objects
		selected_objs = cmds.ls(selection=True)

		# Get initial time slider frame range
		min_frame = cmds.playbackOptions(query=True, min=True)
		max_frame = cmds.playbackOptions(query=True, max=True)

		try:
			# Get anim options
			fps = cmds.currentUnit(query=True, time=True)
			rotationInterp = 1
			for option in cmds.optionVar(list=True):
				if option == 'rotationInterpolationDefault':
					rotationInterp = cmds.optionVar(query=option)

			self._logger.info('# FBX Export started [Time Unit: $fps, RotationInterp: $rotationInterp]' \
				.replace('$fps', str(fps)) \
				.replace('$rotationInterp', str(rotationInterp))
			)

			exported_fbx_paths = []

			# Iterate thru animSequences and exportLayers
			anim_sequences = self._animSequences.get_list()
			export_layers = self._exportLayers.get_list()
			for export_layer in export_layers:
				export_all = idx == -1
				export_selected = idx == export_layer.get_index()
				export_layer_active = export_layer.is_active()

				if export_all:
					if not export_layer_active:
						# Skip inactive layers
						continue
				elif not export_selected:
					continue

				export_objects = export_layer.get_objects()
				if len(export_objects) == 0:
					# No objects to export
					self._logger.warn('# Skipping export layer \'$layer\' - no objects to export.'.replace('$layer', export_layer.get_name()))
					continue

				missing_obj = False
				for export_object in export_objects:
					if not cmds.objExists(export_object):
						# Missing export object
						missing_obj = True
						break

				if missing_obj:
					self._logger.warn('# Skipping export layer \'$layer\' - missing object \'$object\'.' \
							.replace('$layer', export_layer.get_name()) \
							.replace('$object', export_object) \
						)
					continue

				for anim_sequence in anim_sequences:
					if anim_sequence.is_active():
						export_path = self.export_anim(base_export_path, export_layer, anim_sequence, min_frame, max_frame)
						if export_path is not None:
							exported_fbx_paths.append(export_path)

			if len(exported_fbx_paths) > 0:
				self._logger.info('\t* FBX Export complete.')
				self._logger.info('# Exported FBX files:')
				for export_fbx_path in exported_fbx_paths:
					self._logger.info('\t- ' + export_fbx_path)

				cmds.confirmDialog(title=dialog_title, message='Export complete.\n\nSee Script Editor for details.       ', button='OK')
			else:
				self._logger.info('\t* FBX Export complete. No objects were exported.')
				cmds.confirmDialog(title=dialog_title, message='Export failed.\n\nSee Script Editor for details.       ', button='OK')

			self._logger.command_message('Export complete. See Script Editor for details.')
		finally:
			# Restore time slider frame range
			cmds.playbackOptions(min=min_frame, animationStartTime=min_frame)
			cmds.playbackOptions(max=max_frame, animationEndTime=max_frame)

			# Restore selections
			if len(selected_objs) > 0:
				cmds.select(selected_objs)
			else:
				cmds.select(clear=True)

	def export_anim(self, base_export_path, export_layer, anim_sequence, min_frame, max_frame):
		# Set new time slider frame range
		new_start_frame = anim_sequence.get_start()
		new_end_frame = anim_sequence.get_end()

		if new_start_frame == 'start':
			new_start_frame = str(int(min_frame))
		if new_end_frame == 'end':
			new_end_frame = str(int(max_frame))

		if int(new_start_frame) >= int(new_end_frame):
			self._logger.warn('# Skipping FBX Export on animation sequence \'$anim_sequence\' - End frame should be greater than Start frame.' \
				.replace('$anim_sequence', anim_sequence.get_name()) \
			)
			return None

		cmds.playbackOptions(min=new_start_frame, animationStartTime=new_start_frame)
		cmds.playbackOptions(max=new_end_frame, animationEndTime=new_end_frame)

		# Format export path
		export_filename = '$layer_name_$anim_sequence_$start_$end.fbx' \
			.replace('$layer_name', export_layer.get_name()) \
			.replace('$anim_sequence', anim_sequence.get_name()) \
			.replace('$start', str(new_start_frame)) \
			.replace('$end', str(new_end_frame))

		export_path = os.path.join(base_export_path, export_filename)
		self._logger.info('# Export path: ' + export_path)

		# Retrieve joint chains
		joint_chains = []
		for export_object in export_layer.get_objects():
			if cmds.nodeType(export_object) == 'joint':
				joint_chains.append(export_object)

		if len(joint_chains) == 0:
			self._logger.warn('# Skipping FBX Export on export layer \'$export_layer\' - No joints found.' \
				.replace('$export_layer', export_layer.get_name()) \
			)
			return None

		# Clear keys
		for joint_chain in joint_chains:
			cmds.cutKey(joint_chain, hierarchy='both')

		# Bake animation
		self._logger.info('\t- Baking animation...')
		cmds.select(joint_chains, hierarchy=True)
		cmds.bakeResults(simulation=True, time=(new_start_frame, new_end_frame))

		# Run an euler filter
		self._logger.info('\t- Running Euler filter...')
		cmds.select(joint_chains, hierarchy=True)
		cmds.filterCurve()

		# Set FBX properties
		mel.eval('FBXExportConstraints -v 1;')
		mel.eval('FBXExportCacheFile -v 0;')

		if not os.path.isdir(base_export_path):
			# Create directory
			os.makedirs(base_export_path)

		# Export as FBX
		self._logger.info('\t- Exporting...')
		cmds.select(export_layer.get_objects())
		cmds.file(export_path, force=True, options='v=0;', type='FBX export', preserveReferences=True, exportSelected=True)
		self._logger.info('\t* DONE!')

		# Clear keys
		for joint_chain in joint_chains:
			cmds.cutKey(joint_chain, hierarchy='both')

		return export_path


# ANIM SEQUENCE ================================================= [ private ]

	def _init_anim_sequences_ui(self):
		cmds.columnLayout(self._util.to_ui_name('col_anim_sequences'), adjustableColumn=True)
		cmds.setParent(upLevel=True)

	def _update_anim_sequences_ui(self):
		col1_width = 10
		col2_width = 34
		col3_width = 4
		col4_width = 34
		col6_width = 10
		col7_width = 12
		col8_width = 10

		# Delete existing UI elements
		child_elements = cmds.columnLayout(self._util.to_ui_name('col_anim_sequences'), query=True, childArray=True)
		if child_elements is not None:
			cmds.deleteUI(child_elements)

		# Create new UI elements
		cmds.frameLayout(parent=self._util.to_ui_name('col_anim_sequences'), label='      Animation Sequences', borderStyle='out', font='obliqueLabelFont')
		cmds.setParent(upLevel=True)

		cmds.rowLayout(parent=self._util.to_ui_name('col_anim_sequences'), numberOfColumns=7, adjustableColumn=5)
		cmds.separator(style='none', width=col1_width)
		cmds.text(' Start', font='boldLabelFont', width=col2_width, align='left')
		cmds.separator(style='none', width=col3_width)
		cmds.text(' End', font='boldLabelFont', width=col4_width, align='left')
		cmds.text(' Animation', font='boldLabelFont', align='left')
		cmds.text('', font='boldLabelFont', align='left')
		cmds.text(' Sort', font='boldLabelFont', align='left')
		cmds.setParent(upLevel=True)

		for index in range(0, self._animSequences.get_size()):
			cmds.rowLayout(parent=self._util.to_ui_name('col_anim_sequences'), numberOfColumns=8, adjustableColumn=5)
			# Close button
			cmds.iconTextButton(label='x', style='textOnly', font='boldLabelFont', command=partial(self.delete_anim_sequence, index), width=col1_width)

			txtField_start_name = self._util.to_ui_name('txtField_anim_sequence_start_name' + str(index))
			txtField_end_name = self._util.to_ui_name('txtField_anim_sequence_end_name' + str(index))
			txtField_name_name = self._util.to_ui_name('txtField_anim_sequence_name_name' + str(index))
			chk_active_name = self._util.to_ui_name('chk_anim_sequence_active_name' + str(index))

			start_value = self._animSequences.get(index).get_start()
			end_value = self._animSequences.get(index).get_end()
			name_value = self._animSequences.get(index).get_name()
			active_value = self._animSequences.get(index).is_active()

			cmds.textField(txtField_start_name, text=start_value, annotation=start_value, changeCommand=partial(self.update_anim_sequence, index, txtField_start_name, 'start'), width=col2_width)
			cmds.text('-', width=col3_width)
			cmds.textField(txtField_end_name, text=end_value, annotation=end_value, changeCommand=partial(self.update_anim_sequence, index, txtField_end_name, 'end'), width=col4_width)
			cmds.textField(txtField_name_name, text=name_value, annotation=name_value, changeCommand=partial(self.update_anim_sequence, index, txtField_name_name, 'name'))
			cmds.checkBox(chk_active_name, value=active_value, label='', changeCommand=partial(self.update_anim_sequence, index, chk_active_name, 'active'))
			cmds.iconTextButton(label='^', style='textOnly', font='boldLabelFont', command=partial(self.move_anim_sequence_up, index), width=col7_width)
			cmds.iconTextButton(label='v', style='textOnly', font='boldLabelFont', command=partial(self.move_anim_sequence_down, index), width=col8_width)
			cmds.setParent(upLevel=True)

		cmds.rowLayout(parent=self._util.to_ui_name('col_anim_sequences'), numberOfColumns=2)
		cmds.separator(style='none', width=col1_width)
		cmds.button(label=' New ', command=partial(self.add_anim_sequence))
		cmds.setParent(upLevel=True)


# EXPORT LAYER ================================================== [ private ]

	def _init_export_layers_ui(self):
		cmds.columnLayout(self._util.to_ui_name('col_export_layers'), adjustableColumn=True)
		cmds.setParent(upLevel=True)

	def _update_export_layers_ui(self):
		col1_width = 10
		col2_width = 12
		col3_width = 18
		col6_width = 12
		col7_width = 10
		col8_width = 10

		# Delete existing UI elements
		child_elements = cmds.columnLayout(self._util.to_ui_name('col_export_layers'), query=True, childArray=True)
		if child_elements is not None:
			for element in child_elements:
				cmds.deleteUI(element)

		# Create new UI elements
		cmds.columnLayout(self._util.to_ui_name('col_export_layers'), edit=True)

		cmds.frameLayout(parent=self._util.to_ui_name('col_export_layers'), label='      Export Layers', borderStyle='out', font='obliqueLabelFont')
		cmds.setParent(upLevel=True)

		cmds.rowLayout(parent=self._util.to_ui_name('col_export_layers'), numberOfColumns=7, adjustableColumn=4)
		cmds.separator(style='none', width=col1_width)
		cmds.separator(style='none', width=col2_width)
		cmds.separator(style='none', width=col3_width)
		cmds.text(label='Layer', font='boldLabelFont', align='left')
		cmds.text(label='', font='boldLabelFont', align='left')
		cmds.text(label='', font='boldLabelFont', align='left')
		cmds.text(' Sort', font='boldLabelFont', align='left')
		cmds.setParent(upLevel=True)

		for index in range(0, self._exportLayers.get_size()):
			cmds.rowLayout(parent=self._util.to_ui_name('col_export_layers'), numberOfColumns=8, adjustableColumn=4)
			# Close button
			cmds.iconTextButton(label='x', style='textOnly', font='boldLabelFont', command=partial(self.delete_export_layer, index), width=col1_width)

			txt_object_count_name = self._util.to_ui_name('txt_export_layer_object_count' + str(index))
			txtField_layer_name = self._util.to_ui_name('txtField_export_layer_layer_name' + str(index))
			chk_active_name = self._util.to_ui_name('chk_export_layer_active_name' + str(index))

			layer_value = self._exportLayers.get(index).get_name()
			active_value = self._exportLayers.get(index).is_active()

			cmds.text(txt_object_count_name, label=str(self._exportLayers.get(index).get_size()), annotation='Object count', width=col2_width)
			layer_btn = cmds.button(label='L', annotation='Layer Menu...', width=col3_width)
			cmds.textField(txtField_layer_name, text=layer_value, annotation=layer_value, changeCommand=partial(self.update_export_layer, index, txtField_layer_name, 'name'))
			cmds.button(label='Export', command=partial(self.fbx_export, index))
			cmds.checkBox(chk_active_name, value=active_value, label='', changeCommand=partial(self.update_export_layer, index, chk_active_name, 'active'))
			cmds.iconTextButton(label='^', style='textOnly', font='boldLabelFont', command=partial(self.move_export_layer_up, index), width=col7_width)
			cmds.iconTextButton(label='v', style='textOnly', font='boldLabelFont', command=partial(self.move_export_layer_down, index), width=col8_width)
			cmds.setParent(upLevel=True)

			# Context menu
			cmds.popupMenu(parent=layer_btn, button=1)
			cmds.menuItem(label='Add Selected Objects', command=partial(self.add_selected_objects_to_layer, index, txt_object_count_name))
			cmds.menuItem(label='Remove Selected Objects', command=partial(self.remove_selected_objects_from_layer, index, txt_object_count_name))
			cmds.menuItem(divider=True)
			cmds.menuItem(label='Empty the Layer', command=partial(self.empty_objects_from_layer, index, txt_object_count_name))
			cmds.menuItem(divider=True)
			cmds.menuItem(label='Select Objects', command=partial(self.select_objects_from_layer, index))

		cmds.rowLayout(parent=self._util.to_ui_name('col_export_layers'), numberOfColumns=6, adjustableColumn=3)
		cmds.separator(style='none', width=col1_width)
		cmds.button(label=' New ', command=partial(self.add_export_layer))
		cmds.separator(style='none')
		cmds.button(label=' Export All ', command=partial(self.fbx_export, -1))
		cmds.separator(style='none', width=col6_width)
		cmds.separator(style='none', width=col7_width)
		cmds.setParent(upLevel=True)

	def _to_range_num(self, num):
		# Allow 'start' and 'end' as numeric values
		num = num.strip()
		if num == 'start' or num == 'end':
			return num

		numeric_only = ''
		for c in num:
			numeric_only += c if c.isnumeric() or c == '.' else ''
		num = numeric_only

		try:
			return str(int(float(num)))
		except:
			return '0'
