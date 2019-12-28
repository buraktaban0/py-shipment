import pyglet
from pyglet import clock
import time

import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *

import rendering.graphics as graphics

import systems.input
import systems.time
import systems.animation

from geo import *
from voronoi import VoronoiGraph

from data.entity import Entity

import rendering.mesh as mesh

import data.components.camera as camera

import pygame_gui


win = None

label = pyglet.text.Label('Hello, world',
                          font_name='Agency FB',
                          font_size=12,
                          x=0, y=0,
                          anchor_x='left', anchor_y='bottom')


fullScreen = False 


_systems = [systems.input, systems.time, systems.animation]

entities = []


def createEntity(comps = [], name = "Auto %i" % len(entities)):
	e = Entity(name)
	for c in comps:
		e.addComp(c)

	entities.append(e)
	return e	

def update_systems():
	for s in _systems:
		s.update()


def update_entities(dt):
	for e in entities:
		e.update(dt)

	for e in entities:
		e.lateUpdate(dt)	


def main():

	framerate = 5000
	frametime = 1.0 / framerate
	

	camEntity = createEntity(['data.components.camera.Camera'], 'Camera')
	camEntity.transform.position = vec3d.forward() * 10
	cam = camEntity.getComp('data.components.camera.Camera')


	global win

	win = graphics.init(camEntity.transform)

	mesh.init()

	_time = time.time()

	dt = 0.1

	
	m = mesh.fromPoly([vec3d(0, 0, 0), vec3d(1, 0, 0), vec3d(1, 1, 0)], 3)
	e = createEntity();
	e.transform.position = vec3d.back() * 5 
	r = e.addComp('data.components.renderer.Renderer')
	r.mesh = m

	'''
	anim = systems.animation.animate(graphics.label, 'x').fromCurrent().toValue(graphics.label.x + 100).forDuration(3)
	anim.start()
	'''

	run = True
	while run:
		
		if win.has_exit:
			win.close()
			break

		win.dispatch_events()


		update_systems()

		update_entities(dt)


		new_time = time.time()
		dt = new_time - _time
		wait_seconds = max(0, frametime - dt)
		time.sleep(wait_seconds)

		_time = new_time + wait_seconds
		dt += wait_seconds

		systems.time.dt = dt




main()
	

'''
clock.schedule(update)

pyglet.app.run()
'''

