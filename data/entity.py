from data.components.transform import Transform
from data.components.component import Component
from pydoc import locate

class Entity:

	name : str
	transform = None
	components = []

	enabled = True

	def __init__(self, name : str = None):
		self.name = name
		self.transform = Transform(self)
		self.components = [self.transform]

	def __str__(self):
		return "Entity: %s" % (self.name)

	def addComp(self, type : str):
		t = locate(type)
		comp  = t(self)
		self.components.append(comp)
		return comp

	def getComp(self, typeName : str):
		t = locate(typeName)
		comps = [c for c in self.components if type(c) == t]
		if len(comps) < 1:
			raise Exception("Trying to get a component which does not exist on entity '%s'" % self.name)
			return
		return comps[0]


	def addComps(self, types : list):
		for t in types: self.addComp(t)


	def update(self, dt):
		if not self.enabled:
			return

		for comp in self.components:
			comp.update(dt)

	def lateUpdate(self, dt):
		if not self.enabled:
			return

		for comp in self.components:
			comp.lateUpdate(dt)

	def enable(self):
		self.enabled = True

	def disable(self):
		self.enabled = False


	def listComps(self):

		s = ""
		for comp in self.components:
			s += str(type(comp)) + "\r\n"
		print(s)