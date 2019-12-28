from .component import Component
from geo import vec3d

class Transform(Component):
	position : vec3d
	rotation : vec3d
	scale : vec3d

	def __init__(self, owner):
		super().__init__(owner)
		self.position = vec3d.zero()
		self.rotation = vec3d.zero()
		self.scale = vec3d.one()

