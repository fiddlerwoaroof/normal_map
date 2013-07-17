from __future__ import print_function
import collections

#
#  (0,0)  (1,0) | (2,0) (3,0)
#  (0,1)  (1,1) | (2,1) (3,1)
#  -------------+------------
#  (0,2)  (1,2) | (2,2) (3,2)
#  (0,3)  (1,3) | (2,3) (3,3)
#

class XY(collections.namedtuple('XY', 'x y')):
	def __add__(self, other):
		dx, dy = other
		return XY(self.x+dx, self.y+dy)
	def __sub__(self, other):
		dx, dy = other
		return XY(self.x-dx, self.y-dy)
	def __div__(self, n):
		return XY(self.x/n, self.y/n)
	def __mul__(self, n):
		return XY(self.x*n, self.y*n)
	def __abs__(self):
		return XY(abs(self.x), abs(self.y))

class AABB(collections.namedtuple('AABB', 'center halfDimension')):
	@property
	def tl(self):
		return self.center - self.halfDimension
	@property
	def br(self):
		return self.center + self.halfDimension
	@property
	def tr(self):
		return XY(self.br[0], self.tl[1])
	@property
	def bl(self):
		return XY(self.tl[0], self.br[1])
	def containsPoint(self, p):
		tl = self.center - self.halfDimension
		br = (self.center + self.halfDimension) - (1,1)
		return all(x >= 0 for x in p - tl) and all(x > 0 for x in br - p)

	def intersectsAABB(self, other):
		tl = self.center - self.halfDimension
		br = self.center + self.halfDimension
		tr = XY(br[0], tl[1])
		bl = XY(tl[0], br[1])
		return other.containsPoint(tl) or other.containsPoint(br) or other.containsPoint(tr) or other.containsPoint(bl)


	def subdivide(self):
		tl = self.center - self.halfDimension
		br = self.center + self.halfDimension
		tr = XY(br[0], tl[1])
		bl = XY(tl[0], br[1])

		center = self.center
		ne = AABB( (tl+center)/2, self.halfDimension/2 )
		nw = AABB( (tr+center)/2, self.halfDimension/2 )
		se = AABB( (br+center)/2, self.halfDimension/2 )
		sw = AABB( (bl+center)/2, self.halfDimension/2 )
		return nw, ne, se, sw

class QuadTree(object):
	QT_NODE_CAPACITY = 4

	def __init__(self, boundary):
		self.boundary = boundary
		self.nw = None
		self.ne = None
		self.se = None
		self.sw = None
		self.points = []

	def insert(self, p):
		if not self.boundary.containsPoint(p): return False

		if len(self.points) < self.QT_NODE_CAPACITY:
			self.points.append(p)
			return True

		if self.nw is None:
			self.nw, self.ne, self.se, self.sw = map(self.__class__, self.boundary.subdivide())
			while self.points:
				point = self.points.pop()
				if self.nw.insert(point): pass
				elif self.ne.insert(point): pass
				elif self.se.insert(point): pass
				elif self.sw.insert(point): pass

		elif self.nw.insert(p): return True
		elif self.ne.insert(p): return True
		elif self.se.insert(p): return True
		elif self.sw.insert(p): return True

		return False

	def query(self, range):
		pointsInRange = []

		if not self.boundary.intersectsAABB(range):
			return pointsInRange

		for p in self.points:
			if range.containsPoint(p):
				pointsInRange.append(p)

		if self.nw is None: return pointsInRange

		pointsInRange.extend(self.nw.query(range))
		pointsInRange.extend(self.ne.query(range))
		pointsInRange.extend(self.se.query(range))
		pointsInRange.extend(self.sw.query(range))

		return pointsInRange

	def visualize(self):
		points = self.query(self.boundary)
		import numpy
		out = numpy.zeros(self.boundary.halfDimension * 2).astype('int')
		for p in points:
			out[p] = 1

		for row in out:
			for cell in row:
				if cell == 1: print('#',end='')
				elif cell == 0: print(' ',end='')
			print()

a = QuadTree(AABB(XY(128,128), XY(128,128)))
import random
for x in range(128):
	for y in range(128):
		if not a.insert(XY(x,y)):
			pass #print (x,y)
#points = {XY(random.randrange(128),random.randrange(128)) for ___ in range(300)}
#for p in points:
	#a.insert(p)
#a.visualize()
