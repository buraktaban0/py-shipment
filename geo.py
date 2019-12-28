import math
import numpy as np
from mathutil import approx

class vec3d:

	x = 0.0
	y = 0.0
	z = 0.0


	def __init__(self, x = 0.0, y = 0.0, z = 0.0):
		self.x = x
		self.y = y
		self.z = z


	def __repr__(self):
		return "(%.3f, %.3f, %.3f)" % (self.x, self.y, self.z)
	
	def __str__(self):
		return "(%.3f, %.3f, %.3f)" % (self.x, self.y, self.z)

	def __getitem__(self, key):
		if key == 0: return self.x
		elif key == 1 : return self.y
		else: return self.z


	def __add__(self, o):
		return vec3d(self.x + o.x, self.y + o.y, self.z + o.z) if type(o) is vec3d else vec3d(self.x + o, self.y + o, self.z + o)

	def __sub__(self, o):
		return vec3d(self.x - o.x, self.y - o.y, self.z - o.z) if type(o) is vec3d else vec3d(self.x - o, self.y - o, self.z - o)

	def __mul__(self, o):
		return vec3d(self.x * o.x, self.y * o.y, self.z * o.z) if type(o) is vec3d else vec3d(self.x * o ,self.y * o, self.z * o)

	def __truediv__(self, o):
		return vec3d(self.x / o.x, self.y / o.y, self.z / o.z) if o is vec3d else vec3d(self.x / o ,self.y / o, self.z / o)

	def __eq__(self, o):
		return approx(self.x, o.x) and approx(self.y, o.y) and approx(self.z, o.z)

	def __ne__(self, o):
		return not __eq__(self, o)	

	def __neg__(self):
		return vec3d(-self.x, -self.y, -self.z)


	def divVec(self, o):
		return vec3d(self.x / o.x if o.x else 0, self.y / o.y if o.y else 0, self.z / o.z if o.z else 0)

	def sqrLength(self):
		return self.x**2 + self.y**2 + self.z**2

	def length(self):
		return math.sqrt(self.sqrLength())

	def sqrDistance(self, o):
		return (self - o).sqrLength()

	def distance(self, o):
		return Math.sqrt(self.sqrDistance(o))

	def normalize(self):
		_len = self.length()
		self.x /= _len;
		self.y /= _len;
		self.z /= _len;

	def normalized(self):
		a = self.copy()
		a.normalize()
		return a	


	def astuple(self):
		return (self.x, self.y, self.z)

	def aslist(self):
		return [self.x, self.y, self.z]	

	def astuple2(self):
		return (self.x, self.y)

	def aslist2(self):
		return [self.x, self.y]

	def copy(self):
		return vec3d(self.x, self.y, self.z)


	def zero():
		return vec3d(0, 0, 0)

	def one():
		return vec3d(1, 1, 1)

	def right():
		return vec3d(1, 0, 0)

	def left():
		return vec3d(-1, 0, 0)

	def up():
		return vec3d(0, 1, 0)
	
	def down():
		return vec3d(0, -1, 0)	

	def forward():
		return vec3d(0, 0, 1)

	def back():
		return vec3d(0, 0, -1)

	def rand():
		x = np.random.uniform(0, 1)
		y = np.random.uniform(0, 1)
		z = np.random.uniform(0, 1)
		return vec3d(x, y, z)

	def fromList(l):
		return vec3d(l[0], l[1], l[2] if len(l) > 2 else 0.0)


	def dot(a, b):
		return a.x * b.x + a.y * b.y + a.z * b.z
