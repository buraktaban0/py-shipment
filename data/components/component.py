

class Component:

	enabled = True
	owner = None

	def __init__(self, owner):
		self.owner = owner

	def update(self, dt):
		pass

	def lateUpdate(self, dt):
		pass

	def enable(self):
		enabled = True


	def disable(self):
		enabled = False


	def transform(self):
		return self.owner.transform