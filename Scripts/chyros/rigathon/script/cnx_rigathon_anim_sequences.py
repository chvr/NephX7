import maya.cmds as cmds

from cnx_rigathon_anim_sequence import AnimSequence

class AnimSequences:

	def __init__(self, settings):
		self._settings = settings

		self._anim_sequences = []

	def get(self, idx):
		return self._anim_sequences[idx]

	def get_list(self):
		return self._anim_sequences

	def get_size(self):
		return len(self._anim_sequences)

	def clear(self):
		del self._anim_sequences[:]

	def add(self, name, start, end, active):
		anim_sequence = AnimSequence(name, start, end, active)
		self._anim_sequences.append(anim_sequence)

		self._update_indices()

		return anim_sequence

	def update(self, idx, name = None, start = None, end = None, active = None):
		if name is not None:
			self.get(idx).set_name(name)
			self._settings.save('name', name, 'anim_sequence' + str(idx), 'anim_sequences')

		if start is not None:
			self.get(idx).set_start(start)
			self._settings.save('start', start, 'anim_sequence' + str(idx), 'anim_sequences')

		if end is not None:
			self.get(idx).set_end(end)
			self._settings.save('end', end, 'anim_sequence' + str(idx), 'anim_sequences')

		if active is not None:
			self.get(idx).set_active(active)
			self._settings.save('active', active, 'anim_sequence' + str(idx), 'anim_sequences')

	def remove(self, idx):
		anim_sequence_names = None
		if cmds.objExists('anim_sequences'):
			anim_sequence_names = cmds.listRelatives('anim_sequences')

		if anim_sequence_names is not None:
			for anim_sequence_name in anim_sequence_names:
				# Delete existing anim sequence nodes
				self._settings.delete_node(anim_sequence_name, 'anim_sequences')

		deleted = False
		for anim_sequence in self._anim_sequences:
			if anim_sequence.get_index() == idx:
				self._anim_sequences.remove(anim_sequence)
				deleted = True
				break

		self._update_indices()

		return deleted

	def move_up(self, idx):
		if self.get_size() < 2:
			return False

		anim_sequence_a = self._anim_sequences[idx - 1]
		anim_sequence_b = self._anim_sequences[idx]

		if anim_sequence_a is not None and anim_sequence_b is not None:
			self._swap(anim_sequence_a, anim_sequence_b)
			self._update_indices()
			return True

		return False

	def move_down(self, idx):
		if self.get_size() < 2:
			return False

		anim_sequence_a = self._anim_sequences[idx]
		if self.get_size() > 1 and anim_sequence_a == self._anim_sequences[-1]:
			# First item
			anim_sequence_b = self._anim_sequences[0]
		else:
			# Next item
			anim_sequence_b = self._anim_sequences[idx + 1]

		if anim_sequence_a is not None and anim_sequence_b is not None:
			self._swap(anim_sequence_a, anim_sequence_b)
			self._update_indices()
			return True

		return False

	def _update_indices(self):
		counter = 0

		for anim_sequence in self._anim_sequences:
			anim_sequence.set_index(counter)

			self._settings.save('name', anim_sequence.get_name(), 'anim_sequence' + str(anim_sequence.get_index()), 'anim_sequences')
			self._settings.save('start', anim_sequence.get_start(), 'anim_sequence' + str(anim_sequence.get_index()), 'anim_sequences')
			self._settings.save('end', anim_sequence.get_end(), 'anim_sequence' + str(anim_sequence.get_index()), 'anim_sequences')
			self._settings.save('active', anim_sequence.is_active(), 'anim_sequence' + str(anim_sequence.get_index()), 'anim_sequences')

			counter += 1

	def _swap(self, anim_sequence_a, anim_sequence_b):
		tmp = AnimSequence('', '', '', False)
		tmp.set_name(anim_sequence_a.get_name())
		tmp.set_start(anim_sequence_a.get_start())
		tmp.set_end(anim_sequence_a.get_end())
		tmp.set_active(anim_sequence_a.is_active())

		anim_sequence_a.set_name(anim_sequence_b.get_name())
		anim_sequence_a.set_start(anim_sequence_b.get_start())
		anim_sequence_a.set_end(anim_sequence_b.get_end())
		anim_sequence_a.set_active(anim_sequence_b.is_active())

		anim_sequence_b.set_name(tmp.get_name())
		anim_sequence_b.set_start(tmp.get_start())
		anim_sequence_b.set_end(tmp.get_end())
		anim_sequence_b.set_active(tmp.is_active())
