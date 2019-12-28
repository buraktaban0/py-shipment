
from geo import *
import rendering.graphics as graphics

import data.components.camera as camera

keys = {}

mousePosPixel = None
mousePos = None

def registerKeyDown(key):
	time = pg.time.get_ticks()
	keys[key] = {'state': 0, 'time': time}

def registerKeyUp(key):
	time = pg.time.get_ticks()
	keys[key] = {'state': 2, 'time': time}


def update():
	
	return

	time = pg.time.get_ticks()
	toBeRemoved = []
	for key in keys:
		data = keys[key]
		if data['time'] >= time:
			continue
		if data['state'] == 0:
			data['state'] = 1
		elif data['state'] == 2:
			toBeRemoved.append(key)

	for key in toBeRemoved:
		del keys[key]

		return

	global mousePosPixel
	mousePosPixel = vec3d.fromList(pg.mouse.get_pos())
	mousePosPixel.y = graphics.display_size[1] - mousePosPixel.y

	global mousePos
	mousePos = mousePosPixel.divVec(graphics.display_size)
	mousePos.y = 1.0 - mousePos.y

	mousePos = mousePos * 2 - 1
	mousePos.z = 1.0



def mouse_ray():
	return graphics.get_screen_ray(mousePosPixel)


def getKey(key):
	if not key in keys:
		return False
	return keys[key]['state'] == 1
	
def getKeyDown(key):
	if not key in keys:
		return False
	return keys[key]['state'] == 0

def getKeyUp(key):
	if not key in keys:
		return False
	return keys[key]['state'] == 2




def listAll():
	if len(keys) < 1:
		return

	s = ""
	for key in keys:
		s += str(key) + " = " + str(keys[key]['state'])

	print(s)	

