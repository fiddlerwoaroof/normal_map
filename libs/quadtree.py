from __future__ import print_function
import collections

#
#  (0,0)  (1,0) | (2,0) (3,0)
#  (0,1)  (1,1) | (2,1) (3,1)
#  -------------+------------
#  (0,2)  (1,2) | (2,2) (3,2)
#  (0,3)  (1,3) | (2,3) (3,3)
#

class Rect(object):
	@property
	def width(self): return self.size[0]
	@property
	def height(self): return self.size[1]

	@property
	def x(self): return self.pos[0]
	@property
	def y(self): return self.pos[1]

	@classmethod
	def random_rect(cls, xrange, yrange, dimrange):
		x = random.randrange(*xrange)
		y = random.randrange(*yrange)
		size = map(lambda x: random.randrange(*x), dimrange)
		return cls(x,y, *size)

	def __repr__(self):
		return 'Rect(%d, %d, %d, %d)' % (self.pos + self.size)

	def fill(self, array, value):
		x,y = self.pos
		w,h = self.size
		array[x:x+w,y:y+h] = value

	def __init__(self, x,y, w,h):
		self.pos = (x,y)
		self.size = (w,h)

class QuadTree(object):
	MAX_OBJECTS = 10
	MAX_LEVELS = 8

	def __init__(self, pLevel, pBounds):
		self.level = pLevel
		self.objects = []
		self.bounds = pBounds
		self.nodes = [None, None, None, None]

	def clear(self):
		del self.objects[:]
		for idx,node in enumerate(self.nodes):
			if node is not None:
				node.clear()
				self.nodes[idx] = None

	def split(self):
		subWidth = self.bounds.size[0] / 2
		subHeight = self.bounds.size[1] / 2
		x, y = self.bounds.pos

		self.nodes[0] = QuadTree(self.level+1, Rect(x+subWidth, y, subWidth, subHeight))
		self.nodes[1] = QuadTree(self.level+1, Rect(x, y, subWidth, subHeight))
		self.nodes[2] = QuadTree(self.level+1, Rect(x, y + subHeight, subWidth, subHeight))
		self.nodes[3] = QuadTree(self.level+1, Rect(x + subWidth, y + subHeight, subWidth, subHeight))

	def getIndex(self, rect):
		index = -1
		verticalMidpoint = self.bounds.x + self.bounds.width/2
		horizontalMidpoint = self.bounds.y + self.bounds.width/2
		topquad = rect.y < horizontalMidpoint and rect.y + rect.height < horizontalMidpoint
		bottomquad = rect.y > horizontalMidpoint

		if rect.x < verticalMidpoint and rect.x + rect.width < verticalMidpoint:
			if topquad:
				index = 1
			elif bottomquad:
				index = 2
		elif rect.x > verticalMidpoint:
			if topquad:
				index = 0
			elif bottomquad:
				index = 3

		return index

	def insert(self, rect):
		if self.nodes[0] is not None:
			index = self.getIndex(rect)
			if index != -1:
				self.nodes[index].insert(rect)
				return

		self.objects.append(rect)

		if len(self.objects) > self.MAX_OBJECTS and self.level < self.MAX_LEVELS:
			if self.nodes[0] is None:
				self.split()

			i = 0
			while i < len(self.objects):
				index = self.getIndex(self.objects[i])
				if index != -1:
					self.nodes[index].insert(self.objects.pop(i))
				else:
					i += 1

	def retrieve(self, rect):
		result = []
		index = self.getIndex(rect)
		if index != -1 and self.nodes[0] is not None:
			result.extend(self.nodes[index].retrieve(rect))

		result.extend(self.objects)
		return result

	def locate_rect(self, rect):
		cur = self
		index = cur.getIndex(rect)

		while index != -1:
			yield index
			cur = self.nodes[index]




import random

objects = {Rect.random_rect( (1,37), (1,200), ( (2,10), (2,10) ) ) for ___ in range(50)}
quad = QuadTree(0, Rect(0,0, 48,211))
quad.clear()
for obj in objects:
	quad.insert(obj)

collided = set()
oot = set()

for obj in objects:
	out = quad.retrieve(obj)

	if obj in collided: continue
	oot.add(obj)

	for col in out:
		collided.add(col)
		print(obj, 'collides with', col)
	else:
		print('---')


import numpy
field = numpy.zeros( (48,211) )
for obj in objects:
	obj.fill(field, 2)
for obj in oot:
	obj.fill(field, 1)

for row in field:
	for cell in row:
		print('%d' % cell, end='')
	print()
