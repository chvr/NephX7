import maya.cmds as cmds

from cnx_rigathon_character import Character

class Characters:

	def __init__(self, settings):
		self._settings = settings

		self._characters = []

	def get(self, idx):
		return self._characters[idx]

	def get_list(self):
		return self._characters

	def get_size(self):
		return len(self._characters)

	def clear(self):
		del self._characters[:]

	def add(self, namespace, active):
		character = Character(namespace, active)
		self._characters.append(character)

		self._update_indices()

		return character

	def update(self, idx, namespace = None, active = None):
		if namespace is not None:
			self.get(idx).set_namespace(namespace)
			self._settings.save('namespace', namespace, 'character' + str(idx), 'characters')

		if active is not None:
			for character in self._characters:
				is_active = False
				if character.get_index() == idx:
					is_active = active

				character.set_active(is_active)
				self._settings.save('active', is_active, 'character' + str(character.get_index()), 'characters')

	def remove(self, idx):
		namespaces = None
		if cmds.objExists('characters'):
			namespaces = cmds.listRelatives('characters')

		if namespaces is not None:
			for namespace in namespaces:
				# Delete existing anim range nodes
				self._settings.delete_node(namespace, 'characters')

		deleted = False
		for character in self._characters:
			if character.get_index() == idx:
				self._characters.remove(character)
				deleted = True
				break

		self._update_indices()

		return deleted

	def move_up(self, idx):
		if self.get_size() < 2:
			return False

		character_a = self._characters[idx - 1]
		character_b = self._characters[idx]

		if character_a is not None and character_b is not None:
			self._swap(character_a, character_b)
			self._update_indices()
			return True

		return False

	def move_down(self, idx):
		if self.get_size() < 2:
			return False

		character_a = self._characters[idx]
		if self.get_size() > 1 and character_a == self._characters[-1]:
			# First item
			character_b = self._characters[0]
		else:
			# Next item
			character_b = self._characters[idx + 1]

		if character_a is not None and character_b is not None:
			self._swap(character_a, character_b)
			self._update_indices()
			return True

		return False

	def _update_indices(self):
		counter = 0

		for character in self._characters:
			character.set_index(counter)

			self._settings.save('namespace', character.get_namespace(), 'character' + str(character.get_index()), 'characters')
			self._settings.save('active', character.is_active(), 'character' + str(character.get_index()), 'characters')

			counter += 1

	def _swap(self, character_a, character_b):
		tmp = Character('', False)
		tmp.set_namespace(character_a.get_namespace())
		tmp.set_active(character_a.is_active())

		character_a.set_namespace(character_b.get_namespace())
		character_a.set_active(character_b.is_active())

		character_b.set_namespace(tmp.get_namespace())
		character_b.set_active(tmp.is_active())
