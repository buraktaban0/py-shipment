from .component import Component
from rendering.mesh import Mesh
import rendering.graphics as graphics

class Renderer(Component):

	mesh : Mesh
	shader: int

	def __init__(self, owner):
		super().__init__(owner)
		self.mesh = None
		self.shader = graphics.get_shader('simple')
		graphics.addRenderer(self)


	def update(self, dt):
		super().update(dt)
		#graphics.drawRenderer(self)

	def lateUpdate(self, dt):
		super().lateUpdate(dt)
		#graphics.drawRenderer(self)
		

	def enable(self):
		super().enable()


	def disable(self):
		super().disable()
