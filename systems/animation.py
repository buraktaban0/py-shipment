import systems.time as time
import math

class Interpolator:

	func = None

	def __init__(self, func):
		self.func = func

	def interpolate(self, t):
		return self.func(t)



def linear():
	return Interpolator(lambda t: t);

def accelerate(f = 1.0):
	return Interpolator(lambda t: t**(2*f) )

def decelerate(f = 1.0):
	return Interpolator(lambda t: 1 - (1 - t)**(2 * f) )

def smooth():
	return Interpolator(lambda t: math.cos((t + 1) * math.pi) / 2 + 0.5 )

def anticipate(f = 1.0):
	return Interpolator(lambda t: t**3 * (f+1) - t**2 * f )

def overshoot(f = 1.0):
	return Interpolator(lambda t: (t-1)**3 * (f+1) + (t-1)**2 * f + 1)

def anticipate_overshoot(f1 = 1.0, f2 = 1.0):
	def func(t):
		if t < 0.5:
			return 0.5 * ((f1+1) * (2*t)**3 - f1 * (2 * t)**2)
		else:
			return 0.5 * ((f1 + 1) * (2 * t - 2)**3 + f1 * (2*t - 2)**2) + 1

	return Interpolator(func)		



def bounce():
	def func(t):
		b = 1.0435
		c = 0.95
		if t < 0.31489:
			b = 0
			c = 0
		elif t < 0.6599:
			b = 0.54719
			c = 0.7
		elif t < 0.85908:
			b = 0.8526
			c = 0.9

		return 8 * ((1.1226 * t - b)**2) + c	

	return Interpolator(func)

def hesitate():
	return Interpolator(lambda t: 0.5 * ((2.0*t - 1.0)**3 + 1))



anims = []


class Animation:

	obj = None
	attr = None
	v0 = None
	v1 = None

	time = None
	duration = None

	done = False

	interpolator = None

	def __init__(self, obj, attr):
		self.obj = obj
		self.attr = attr
		self.time = 0.0
		self.v0 = None
		self.v1 = None
		self.duration = 1.0
		self.done = False
		self.interpolator = linear()


	def update(self, dt):
		self.time += dt
		t = self.time / self.duration
		t = self.interpolator.interpolate(t)
		if self.time >= self.duration:
			self.done = True
			t = 1.0

		val = self.v0 + (self.v1 - self.v0) * t

		setattr(self.obj, self.attr, val)


	def fromValue(self, v):
		self.v0 = v
		return self

	def fromCurrent(self):
		self.v0 = get_dict_attr(self.obj, self.attr)
		return self


	def toValue(self, v):
		self.v1 = v
		return self


	def forDuration(self, d):
		self.duration = d
		return self

	def withInterpolator(self, interpolator = None, func = None):
		if interpolator != None:
			self.interpolator = interpolator
		elif func != None:
			self.interpolator = Interpolator(func)
		else:
			raise Exception("A valid interpolator should be provided to the animation")		
		return self	

	def start(self):
		anims.append(self)
		return self





def get_dict_attr(obj, attr):
	for obj in [obj] + obj.__class__.mro():
		if attr in obj.__dict__:
			return obj.__dict__[attr]
	raise AttributeError		
		




def animate(obj, attr):
	return Animation(obj, attr)


def update(dt = None):
	if dt is None:
		dt = time.dt 
	global anims
	for a in anims:
		a.update(dt)

	anims = [a for a in anims if not a.done]
