from cnx_rigathon_widget import Widget

class Widgets:

	def __init__(self, settings, util):
		self._settings = settings
		self._util = util

		self._widgets = {}

	def create(self, key, type, attribute_name = None, attribute_type = 'attribute', value_id = None):
		widget = self.get(key)
		if widget is None:
			# Create new widget
			widget = Widget(self._util, key, type, attribute_name = attribute_name, attribute_type = attribute_type, value_id = value_id)
			if attribute_type == 'settings':
				widget.use_settings(self._settings)

			self._widgets[key] = widget

		# Generate new name
		return widget.create_new_name()

	def get(self, key):
		widget = None
		if key in self._widgets:
			# Get existing widget
			widget = self._widgets[key]

		return widget

	def clear(self):
		self._widgets.clear()
