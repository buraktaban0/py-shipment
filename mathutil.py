import math
import sys

def approx(a, b):
	return math.abs(a-b) < sys.float_info.epsilon