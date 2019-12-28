from geo import vec3d
import numpy as np
import jsonpickle
import rendering.graphics as graphics

from OpenGL.GL import *



class Mesh:

	verts = []
	colors = []
	uvs = []

	tris = []

	_triCount = None

	_vao = 0

	def __init__(self, verts, tris, uvs = None):
		self.verts = verts
		self.tris = tris
		self.uvs = uvs
		col = vec3d.one()
		self.colors = [col for i in range(len(verts))]
		self._vao = 0

	

	def triCount(self):
		return len(self.tris)

	def generateUVs(self):
		xMin = min([v.x for v in self.verts])
		xMax = max([v.x for v in self.verts])
		yMin = min([v.y for v in self.verts])
		yMax = max([v.y for v in self.verts])
		
		self.uvs = [vec3d((v.x - xMin) / (xMax - xMin),(v.y - yMin) / (yMax - yMin), 0) for v in self.verts]



	def upload(self):
		if self._vao != 0:
			return

		self._triCount = len(self.tris)

		self._vao = graphics.uploadMesh(self)



	def getBuffer(self):
		buf = []
		for i in range(len(self.verts)):
			buf.extend(self.verts[i].aslist())
			buf.extend(self.colors[i].aslist())
			buf.extend(self.uvs[i].aslist2())
		return buf

			

	def draw(self):
		graphics.bind_vao(self._vao)
		glDrawElements(GL_TRIANGLES, self.triCount(), GL_UNSIGNED_INT, None)
		return
			
		glBegin(GL_TRIANGLES)
		
		for i in self.tris:
			glVertex3fv(self.verts[i].aslist())

		glEnd()	




quad_mesh = None

def init():
	global quad_mesh
	quad_mesh = quad()



def quad(size = 1):
	size *= 0.5
	verts = (np.array([
		vec3d.left() + vec3d.down(), 
		vec3d.right() + vec3d.down(), 
		vec3d.right() + vec3d.up(),
		vec3d.left() + vec3d.up()]) * size).tolist()
	tris = [0, 1, 2, 0, 2, 3]
	m = Mesh(verts, tris)
	m.generateUVs()
	m.upload()
	return m

def fromPoly(p, size = 1.0):
	verts = [vec3d.fromList(pi) * size if type(pi) != vec3d else pi * size for pi in p]
	triCount = len(verts) - 2
	tris = []
	for i in range(triCount):
		tris.append(0)
		tris.append(i+1)
		tris.append(i+2)
	m = Mesh(verts, tris)
	m.generateUVs()
	m.upload()
	return m



def deserialize(json: str):
	return jsonpickle.decode(json)

def serialize(mesh : Mesh):
	return jsonpickle.encode(mesh)



def combine(ms):
	verts = []
	colors = []
	uvs = []
	tris = []

	for m in ms:
		tris.extend((np.array(m.tris) + len(verts)).tolist())
		verts.extend(m.verts)
		colors.extend(m.colors)
		uvs.extend(m.uvs)

	m = Mesh(verts, tris)
	m.uvs = uvs
	m.colors = colors
	m.generateUVs()
	m.upload()
	return m	