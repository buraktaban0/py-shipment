import systems.input
from pygame.locals import *

timescale = 1.0
dt = 0.1

def unscaledDt():
	return dt / timescale


def update():
	global timescale
	if systems.input.getKeyDown(K_KP_PLUS):
		timescale *= 2.0
		print("Timescale: %f" % timescale)
	elif systems.input.getKeyDown(K_KP_MINUS):
		timescale *= 0.5
		print("Timescale: %f" % timescale)