import OpenGL
import math
import numpy as np
import pyglet
import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from pyglet import clock
#from OpenGLContext.arrays import * 
from OpenGL.GL import shaders
from OpenGL.WGL import *
from OpenGL.arrays import vbo

from PIL import Image
from PIL import ImageDraw
from PIL import ImageEnhance
from PIL import ImageFont

import array as arr

from rendering.mesh import Mesh


from data.components.renderer import Renderer

from geo import *

from os import listdir
from os.path import isfile
from os.path import join



window = None

fov = 60

display_size = None

renderers = []

meshes = []

lines = []
triangles = []
quads = []
polygons = []


textureIds = {}

compiled_shaders = {}

deg2rad = math.pi / 180.0

tex = 0


_bound_texture = None
_bound_program = None
_bound_vao = None

def bind_texture(texture):
	global _bound_texture
	if _bound_texture == texture:
		return

	glBindTexture(GL_TEXTURE_2D, texture)
	_bound_texture = texture	


def bind_program(prog):
	global _bound_program
	if _bound_program == prog:
		return

	shaders.glUseProgram(prog)
	_bound_program = prog	

def bind_vao(vao):
	global _bound_vao
	if _bound_vao == vao:
		return

	glBindVertexArray(vao)
	_bound_vao = vao	




def mv_matrix():
	mv = (GLdouble * 16)()
	glGetDoublev(GL_MODELVIEW_MATRIX, mv)
	return mv

def p_matrix():
	p = (GLdouble * 16)()
	glGetDoublev(GL_PROJECTION_MATRIX, p)
	return p

def v_rect():
	v = (GLint * 4)()
	glGetIntegerv(GL_VIEWPORT, v)
	return v

def get_screen_ray(pos : vec3d):
	p0 = vec3d(pos.x, pos.y, 0)
	p1 = vec3d(pos.x, pos.y, 1)

	ray_near = [GLdouble() for _ in range(3)]
	ray_far = [GLdouble() for _ in range(3)]

	mv = mv_matrix()
	p = p_matrix()
	v = v_rect()

	ray_near = gluUnProject(pos.x, pos.y, 0, mv, p, v)
	ray_far = gluUnProject(pos.x, pos.y, 1, mv, p, v)

	ray_near = vec3d.fromList(ray_near)
	ray_far = vec3d.fromList(ray_far)

	return (ray_near, (ray_far - ray_near).normalized())

def uploadMesh(m : Mesh):
	buf = m.getBuffer()
	elements = m.tris
	vertexElementSize = 8

	vao = glGenVertexArrays(1)
	#glBindVertexArray(vao)
	bind_vao(vao)

	bufs = glGenBuffers(2)
	glBindBuffer(GL_ARRAY_BUFFER, bufs[0])
	glBufferData(GL_ARRAY_BUFFER, sizeof(ctypes.c_float) * len(buf), (ctypes.c_float * len(buf))(*buf), GL_STATIC_DRAW)

	glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, bufs[1])
	glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(ctypes.c_uint) * len(elements), (ctypes.c_uint * len(elements))(*elements), GL_STATIC_DRAW)

	glEnableVertexAttribArray(0)
	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(ctypes.c_float) * vertexElementSize, None)

	glEnableVertexAttribArray(3)
	glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, sizeof(ctypes.c_float) * vertexElementSize, ctypes.c_void_p(3*sizeof(ctypes.c_float)))

	glEnableVertexAttribArray(4)
	glVertexAttribPointer(4, 2, GL_FLOAT, GL_FALSE, sizeof(ctypes.c_float) * vertexElementSize, ctypes.c_void_p(6*sizeof(ctypes.c_float)))

	#glBindVertexArray(0)
	bind_vao(0)

	return vao

def get_texture(path):
	if not path in textureIds:
		raise Exception("No texture exist with path: %s" % path)

	return textureIds[path]


def update_texture(path, data):
	
	id = None
	if not path in textureIds:
		id = glGenTexture(1)
		textureIds[path] = id

		#glBindTexture(GL_TEXTURE_2D, id)
		bind_texture(id)

		glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

	id = textureIds[path]

	#glBindTexture(GL_TEXTURE_2D, id)
	bind_texture(id)

	getTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, data.shape[0], data.shape[1], 0, GL_RGB, GL_UNSIGNED_BYTE, data)

	bind_texture(0)


def readTexture(path: str):
	if path in textureIds:
		return textureIds[path]

	img = Image.open(path)
	img_data = np.array(list(img.getdata()), np.int8)
	texture_id = glGenTextures(1)
	
	#glBindTexture(GL_TEXTURE_2D, texture_id)
	bind_texture(texture_id)

	#glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_NEAREST)
	
	#glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
	#glTexParameterf(GL_TEXTURE_2D, 0x84FE, 8.0)

	#glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

	format = GL_RGB if img.mode == "RGB" else GL_RGBA
	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0, format, GL_UNSIGNED_BYTE, img_data)
	glGenerateMipmap(GL_TEXTURE_2D)

	textureIds[path] = texture_id

	bind_texture(0)

	return texture_id



def get_shader(name):
	if not name in compiled_shaders:
		raise Exception('Shader "%s" is not compiled' % name)

	return compiled_shaders[name]



def compile_shaders():
	path = 'shaders'
	frag = 'fragment'
	vert = 'vertex'
	ext = '.shader'
	vertExt = '_%s%s' % (vert, ext)
	fragExt = '_%s%s' % (frag, ext)

	fileNames = [join(path, f) for f in listdir(path) if isfile(join(path, f))]

	shaderNames = set([f.replace(vertExt, '').replace(fragExt, '').replace('%s\\' % path, '') for f in fileNames])

	def compile(name):
		vertPath = '%s\\%s%s' % (path, name, vertExt)
		fragPath = '%s\\%s%s' % (path, name, fragExt)

		vertexContent = ""
		with open(vertPath, 'r') as f:
			vertexContent = f.read()

		fragContent = ""
		with open(fragPath, 'r') as f:
			fragContent = f.read()

		vertShader = shaders.compileShader(vertexContent, GL_VERTEX_SHADER)
		fragShader = shaders.compileShader(fragContent, GL_FRAGMENT_SHADER)

		shader = shaders.compileProgram(vertShader, fragShader)

		compiled_shaders[name] = shader


	for sName in shaderNames:
		compile(sName)
		



def init(camTransform):
		
	global display_size
	global window

	fullscreen = False

	display_size = (1920, 1080) if fullscreen else (1024, 768)

	config = pyglet.gl.Config(sample_buffers = 1, 
		samples = 16, double_buffer=True,
		depth_size = 24, stencil_size = 0)
	window = pyglet.window.Window(width = display_size[0], height= display_size[1], vsync = False, config = config)

	display_size = vec3d.fromList(display_size)
	display_size.z = 1.0

	glViewport(0, 0, display_size[0], display_size[1])


	aspectRatio = display_size[0] / display_size[1]


	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(fov, aspectRatio, 0.1, 50.0)

	
	glMatrixMode(GL_MODELVIEW)
	gluLookAt(
		camTransform.position.x, 
		camTransform.position.y,
		camTransform.position.z,
		0, 0, 0,
		0, 1, 0)

	glLoadIdentity()
	

	glEnable(GL_TEXTURE_2D)
	
	global tex
	tex = readTexture('res/rock.png')

	#glBindTexture(GL_TEXTURE_2D, tex)
	bind_texture(tex)

	compile_shaders()

	
	return window





def addRenderer(r : Renderer):
	if not r in renderers: renderers.append(r)

def removeRenderer(r: Renderer):
	if r in renderers: renderers.remover(r)

def drawRenderer(r : Renderer):
	renderers.append(r)

def drawMesh(m):
	meshes.append(m)


def drawLine(a: vec3d, b: vec3d):
	lines.append(a)
	lines.append(b)

def drawTriangle(a: vec3d, b: vec3d, c: vec3d):
	triangles.append(a)
	triangles.append(b)
	triangles.append(c)

def drawQuad(a: vec3d, b: vec3d, c: vec3d, d: vec3d):
	quads.append(a)
	quads.append(b)
	quads.append(c)
	quads.append(d)

def drawPoly(vertices):
	polygons.append(vertices)


def translate(v):
	#v = -v
	glTranslatef(v.x, v.y, v.z)

def rotate(v):
	#v = -v
	glRotatef(v.x, 1, 0, 0)
	glRotatef(v.y, 0, 1, 0)
	glRotatef(v.z, 0, 0, 1)

def scale(v):
	glScalef(v.x, v.y, v.z)


from data.components.ui import *

el = None
el2 = None

def render2(cam):

	global el
	global el2
	if el is None:

		el = UIImage(vec3d.one() * 0.2, vec3d.one() * 0.1, anchor = vec3d.zero(), img_path = 'res/bricks.jpg')

		#el2 = UIImage(vec3d.one() * -1, vec3d.one()* 0.1, anchor = vec3d(1, 1, 0))

		#el.addChild(el2)

	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()


	gluPerspective(fov, display_size[0] / display_size[1], 0.1, 50.0)
	
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()


	glPushMatrix()

	'''
	sx = math.sin(deg2rad * cam.rotation.x)
	cx = math.cos(deg2rad * cam.rotation.x)
	sy = math.sin(deg2rad * cam.rotation.y)
	cy = math.cos(deg2rad * cam.rotation.y)

	forward = vec3d(sy*cx, -sx, cy*cx)
	'''

	target = cam.position.copy()
	target.z = -10

	sz = math.sin(deg2rad * cam.rotation.z)
	cz = math.cos(deg2rad * cam.rotation.z)

	up = vec3d(-sz, cz, 0)
	#up = vec3d.up()


	gluLookAt(
		cam.position.x, 
		cam.position.y,
		cam.position.z,
		target.x,
		target.y,
		target.z,
		up.x,
		up.y,
		up.z)
	

	viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)

	glPopMatrix()

	glMultMatrixf(viewMatrix)

	window.clear()

	#glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)


	for r in renderers:
		glPushMatrix()

		tr = r.transform()
		translate(tr.position)
		rotate(tr.rotation)
		
		glEnable(GL_TEXTURE_2D)
		#glBindTexture(GL_TEXTURE_2D, tex)
		bind_texture(tex)

		#shaders.glUseProgram(r.shader)
		bind_program(r.shader)

		#glBindVertexArray(r.mesh._vao)
		bind_vao(r.mesh._vao)

		glDrawElements(GL_TRIANGLES, r.mesh.triCount(), GL_UNSIGNED_INT, None)

		glPopMatrix()


	#glBindVertexArray(0)
	bind_vao(0)

	#glBindTexture(GL_TEXTURE_2D, 0)
	bind_texture(0)

	#shaders.glUseProgram(0)
	bind_program(0)

	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
	glEnable(GL_BLEND)

	glLoadIdentity()

	glMatrixMode(GL_PROJECTION)

	glLoadIdentity()
	glViewport(0, 0, display_size[0], display_size[1])
	glOrtho(0.0, display_size[0], 0.0, display_size[1], -1.0, 1.0)

	
	#print(glGetFloatv(GL_PROJECTION_MATRIX))

	#(ctypes.c_uint * len(elements))(*elements)
	
	mat = [
	[1.0, 0, 0, 0],
	[0, 1.0, 0, 0],
	[0, 0, -1, 0],
	[-1, -1, 0, 1]
	]


	#glMultMatrixf(mat)

	glPushMatrix()

	'''
	glBegin(GL_LINES)

	glVertex3f(0, 0, 0)
	glVertex3f(500, 380, 0)

	glEnd()
	'''

	el.draw(display_size)

	'''
	label.draw()
	label2.draw()

	font = ImageFont.truetype('geonms-font.ttf', 30 * 2)
	w, h = font.getsize('Heyoo Burak yeah !!')


	img = Image.new('RGBA', (w, h), (1, 1, 1, 255))
	draw = ImageDraw.Draw(img, 'RGBA')
	draw.text((0, 0), 'Heyoo Burak yeah !!', fill=(255, 255, 255, 255), font = font)
	resized = img.resize((int(w/2.0), int(h/2.0)), Image.ANTIALIAS)
	resized.save('test3.png')
	'''

	glPopMatrix()

	#glBindTexture(GL_TEXTURE_2D, 0)
	bind_texture(0)	

	window.flip()