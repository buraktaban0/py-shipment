import enum

import rendering.graphics as graphics

from .component import Component
from rendering.mesh import Mesh

from OpenGL.GL import *

from geo import *

from PIL import *

import rendering.mesh



class UIRenderer(Component):

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



class UIElement:

	name : str

	parent = None
	children : list

	position : vec3d

	rotation : vec3d

	anchor : vec3d

	size : vec3d


	ignore_events = True


	def __init__(self, pos, size, anchor = vec3d(0, 0, 0), ignore_events = True, parent = None, children = [], name = 'Nameless UIElement'):
		self.parent = parent
		self.children = []
		self.position = pos / 2.0
		self.position.z = 0.0
		self.rotation = vec3d.zero()
		self.anchor = anchor / 2.0
		self.anchor.z = 0.0
		self.size = size
		self.size.z = 1.0
		self.ignore_events = ignore_events
		self.name = name

	def addChild(self, child):
		self.children.append(child)
		child.parent = self

	def rebuild(self):
		pass

	def draw_self(self):
		# test
		pass


	def draw(self, container_size):

		size = self.size * graphics.display_size.x 

		pos = container_size * self.position 
		anchoredPos = pos - size * self.anchor


		glPushMatrix()

		graphics.translate(anchoredPos)


		mat = glGetFloatv(GL_PROJECTION_MATRIX)

		graphics.scale(size)


		self.draw_self()

		glLoadIdentity()
		glMultMatrixf(mat)
 
		for child in self.children:
			child.draw(size)

		glPopMatrix()


_tint_loc = None

class UIImage(UIElement):

	img_path : str

	shader : int

	tex : int

	tint : list

	def __init__(self, pos, size, anchor = vec3d(0, 0, 0), ignore_events = True, 
		parent = None, children = [], img_path = 'res/white1px.png', name = 'Nameless UIImage'):
		self.parent = parent
		self.children = []
		self.position = pos / 2.0
		self.position.z = 0.0
		self.rotation = vec3d.zero()
		self.anchor = anchor / 2.0
		self.anchor.z = 0.0
		self.size = size
		self.size.z = 1.0
		self.ignore_events = ignore_events

		self.img_path = img_path

		self.tint = [1, 1, 1, 1]

		self.name = name

		self.rebuild()

		global _tint_loc


	def set_texture(self, img_path):
		self.img_path = img_path
		self.rebuild()


	def rebuild(self):
		self.shader = graphics.get_shader('ui')
		self.tex = graphics.readTexture(self.img_path)


	def draw_self(self):


		glEnable(GL_TEXTURE_2D)
		graphics.bind_texture(self.tex)
		
		graphics.bind_program(self.shader)


		_tint_loc = glGetUniformLocation(self.shader, 'tint')
		glUniform4fv(_tint_loc, 1, self.tint)

		rendering.mesh.quad_mesh.draw()	





class UIText(UIElement):
	
	font = None

	font_path = 'geonms-font.ttf'

	font_size = 20

	text_color = (255, 255, 255, 255)

	tex_text = None

	text = 'Not set'


	def set_font(self, path):
		if path == self.font_path:
			return

		self.font_path = path

		setup()


	def rebuild(self):
		super().setup()
		self.font = ImageFont.truetype(self.font_path, self.font_size)
		self.size = vec3d.fromList(font.getsize(self.text))

		if self.img_bg_path is None:
			self.img_bg = Image.new('RGBA', (w, h), (255, 255, 255, 0))
		else:
			self.img_bg = Image.open(path)

		W, H = self.img_bg.size
		draw = ImageDraw.Draw(self.img_bg, 'RGBA')	
		draw.text(((W - self.size.x) / 2, (H - self.size.y) / 2), self.text, fill = self.text_color, font = self.font)


	

