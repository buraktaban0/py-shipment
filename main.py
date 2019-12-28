import pygame as pg
from pygame.locals import *
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



vor = VoronoiGraph(6)

vor.generate()

polygons = [c["vertices"] for c in vor.cells]

entities = []

def handleEvents():
	for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
				quit()
			elif event.type == pg.KEYDOWN:
				systems.input.registerKeyDown(event.key)
			elif event.type == pg.KEYUP:
				systems.input.registerKeyUp(event.key)

def updateSystems():
	systems.input.update()
	systems.time.update()
	systems.animation.update()


def updateEntities(dt):
	#for e in entities:
	#		e.update(dt);

	for e in entities:
			e.lateUpdate(dt);


def main():


	pg.init()

	camEntity = Entity("Camera")
	camEntity.addComp("data.components.camera.Camera")
	camEntity.transform.position = vec3d.forward() * 3

	entities.append(camEntity)

	graphics.init(camEntity.transform)


	lastTime = pg.time.get_ticks()

	frameRate = 144
	frameMs = int(1000.0 / 500)

	dt = 0.1

	pos = vec3d.zero()

	meshes = []
	for i, p in enumerate(polygons):
		m = mesh.fromPoly(p, 1.0)
		meshes.append(m)
	
	combinedMesh = mesh.combine(meshes)

	e = Entity("Combined polygons")
	r = e.addComp('data.components.renderer.Renderer')
	r.mesh = combinedMesh

	entities.append(e)


	'''
	a = systems.animation.animate(e.transform, 'rotation') \
		.fromCurrent() \
		.toValue(vec3d(0, 0, 30)) \
		.forDuration(2.0) \
		.withInterpolator(systems.animation.bounce())
	a.start()
	'''

	while True:
		
		handleEvents()

		updateSystems()

		updateEntities(dt)


		o, d = systems.input.mouse_ray()
		t = -camera.instance.transform().position.z / d.z
		wpos = camera.instance.transform().position + d * t

		cell = vor.get_containing_cell(wpos)


		#print(wpos)
		#print(vor.points[cell])

		#glRotatef(1, 3, 1, 1)

		#graphics.drawPoly([vec3d(0, 0), vec3d(1, 1), vec3d(0, 1), vec3d(-0.5, 0.75), vec3d(-0.95, 0.4)])
		
		#camEntity.transform.position += vec3d.right() * dt * 0.1
		#camEntity.transform.rotation += vec3d.forward() * dt * 10
		
		#e.transform.position += vec3d.left() * dt * 0.1
		
		#e.transform.rotation += vec3d.forward() * dt * 10

		currentTime = pg.time.get_ticks()
		dt = (currentTime - lastTime)
		lastTime = currentTime

		wait = max(0, frameMs - dt)
		pg.time.wait(wait)

		dt *= 0.001 * systems.time.timescale
		systems.time.dt = dt



main()	