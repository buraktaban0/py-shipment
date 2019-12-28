from math import ceil, sqrt
import json
import numpy as np
from scipy import spatial
from scipy.spatial import Voronoi
from scipy.spatial import KDTree
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from bisect import bisect_left

from geo import *

class VoronoiGraph:

	points = []

	xVals = []

	cells = []

	size = 4

	tree = None

	def __init__(self, size):
		self.size = size


	def get_containing_cell(self, pos : vec3d):

		nearest = self.tree.query(pos.aslist2())

		#print("Nearest: " + str(nearest))

		return nearest[1]

		pos = vec3d.fromList(nearest)

		i  = bisect_left(self.xVals, pos.x)
		if i == 0:
			return 0 if self.points[0].sqrDistance(pos) < self.points[1].sqrDistance(pos) else 1
		if i == len(self.xVals):
			return len(self.xVals) - 1 if self.points[-1].sqrDistance(pos) < self.points[-2].sqrDistance(pos) else len(self.xVals) - 2 
		before = self.points[i-1]
		after = self.points[i]
		return i if after.sqrDistance(pos) < before.sqrDistance(pos) else (i-1)


	def generatePoints(self, size):
		nx = sqrt(size)
		cellCountX = ceil(nx * 3.0)
		cellCount = cellCountX**2
		cellSize = 1.0 / cellCountX

		av = [i for i in range(cellCount)]

		points = []
		for i in range(size):
			randi = np.random.randint(len(av))
			randc = av[randi]

			u = randc % cellCountX
			v = randc / cellCountX

			for x in range(int(max(u - 1, 0)), int(min(u+2, cellCountX))):
				for y in range(int(max(v - 1, 0)), int(min(v+2, cellCountX))):
					c = y * cellCountX + x
					if c in av : av.remove(c)

			xr = np.random.uniform(-0.4, 0.4)
			yr = np.random.uniform(-0.4, 0.4)
			x = (u + 0.5 + xr) * cellSize
			y = (v + 0.5 + yr) * cellSize
			
			point = [x, y]
			while points.count(point) > 0:
				r = np.random.uniform(-0.4, 0.4)
				x = (u + 0.5 + xr) * cellSize
				point[0] = x

			points.append([x, y])

		return points

	def voronoi_finite_polygons_2d(self, vor, radius=None):
		"""
		Reconstruct infinite voronoi regions in a 2D diagram to finite
		regions.
		Parameters
		----------
		vor : Voronoi
			Input diagram
		radius : float, optional
			Distance to 'points at infinity'.
		Returns
		-------
		regions : list of tuples
			Indices of vertices in each revised Voronoi regions.
		vertices : list of tuples
			Coordinates for revised Voronoi vertices. Same as coordinates
			of input vertices, with 'points at infinity' appended to the
			end.
		"""

		if vor.points.shape[1] != 2:
			raise ValueError("Requires 2D input")

		new_regions = []
		new_vertices = vor.vertices.tolist()

		center = vor.points.mean(axis=0)
		if radius is None:
			radius = vor.points.ptp().max()*2

		# Construct a map containing all ridges for a given point
		all_ridges = {}
		for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
			all_ridges.setdefault(p1, []).append((p2, v1, v2))
			all_ridges.setdefault(p2, []).append((p1, v1, v2))

		# Reconstruct infinite regions
		for p1, region in enumerate(vor.point_region):
			vertices = vor.regions[region]

			if all(v >= 0 for v in vertices):
				# finite region
				new_regions.append(vertices)
				continue

			# reconstruct a non-finite region
			ridges = all_ridges[p1]
			new_region = [v for v in vertices if v >= 0]

			for p2, v1, v2 in ridges:
				if v2 < 0:
					v1, v2 = v2, v1
				if v1 >= 0:
					# finite ridge: already in the region
					continue

				# Compute the missing endpoint of an infinite ridge

				t = vor.points[p2] - vor.points[p1] # tangent
				t /= np.linalg.norm(t)
				n = np.array([-t[1], t[0]])  # normal

				midpoint = vor.points[[p1, p2]].mean(axis=0)
				direction = np.sign(np.dot(midpoint - center, n)) * n
				far_point = vor.vertices[v2] + direction * radius

				new_region.append(len(new_vertices))
				new_vertices.append(far_point.tolist())

			# sort region counterclockwise
			vs = np.asarray([new_vertices[v] for v in new_region])
			c = vs.mean(axis=0)
			angles = np.arctan2(vs[:,1] - c[1], vs[:,0] - c[0])
			new_region = np.array(new_region)[np.argsort(angles)]

			# finish
			new_regions.append(new_region.tolist())

		return new_regions, np.asarray(new_vertices)


	def generate(self):

		points = self.generatePoints(self.size)

		points.sort(key = lambda p: p[0])

		points = [[p[0] - 0.5, p[1] - 0.5] for p in points]


		vor = Voronoi(points)

		#fig = voronoi_plot_2d(vor)
		#plt.show()

		regions, vertices = self.voronoi_finite_polygons_2d(vor)

		min_x = -0.5
		max_x = 0.5
		min_y = -0.5
		max_y = 0.5

		mins = np.tile((min_x, min_y), (vertices.shape[0], 1))
		bounded_vertices = np.max((vertices, mins), axis=0)
		maxs = np.tile((max_x, max_y), (vertices.shape[0], 1))
		bounded_vertices = np.min((bounded_vertices, maxs), axis=0)


		box = Polygon([[min_x, min_y], [min_x, max_y], [max_x, max_y], [max_x, min_y]])

		ridges = vor.ridge_points

		neighbors = [[] for i in range(self.size)]

		for r in ridges:
			a = r[0]
			b = r[1]
			if not b in neighbors[a]: neighbors[a].append(int(b))
			if not a in neighbors[b]: neighbors[b].append(int(a))

		data = []

		for i, region in enumerate(regions):
			polygon = vertices[region]

			poly = Polygon(polygon)
			poly = poly.intersection(box)
			
			cell = {"index": i, "center": points[i], "vertices": list(poly.exterior.coords), "neighbors": neighbors[i]}
			data.append(cell)

			polygon = Polygon([p for p in poly.exterior.coords])

			plt.plot(*polygon.exterior.xy)


		jsonText = json.dumps(data, indent=4)

		with open('vor.dat', 'w') as f:
			f.write(jsonText)


		plt.axis('equal')
		plt.xlim(0, 1)
		plt.ylim(0, 1)

		plt.savefig('vor.png')

		self.cells = data

		self.points = [vec3d.fromList(p)for p in points]

		self.xVals = [p.x for p in self.points]

		self.tree = KDTree(points)



		#plt.show()