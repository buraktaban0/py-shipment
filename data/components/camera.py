from .component import Component
import rendering.graphics as graphics

instance = None

class Camera(Component):


	def __init__(self, owner):
		super().__init__(owner)
		global instance
		instance = self


	def lateUpdate(self, dt):
		super().lateUpdate(dt)

		graphics.render2(self.owner.transform)

