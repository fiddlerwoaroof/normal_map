import random
import numpy

def row2diterate(dct, width, height):
	for y in range(height):
		for x in range(width):
			yield dct[c,r]

class Cell(object):
	@property
	def value(self):
		return self._value
	@value.setter
	def value(self, v):
		if v >= self._value: return
		self._value = v
	def __init__(self, pos, value=0, previous={}):
		self.pos = pos
		self._value = value

		self.previous = previous
		self.previous[pos] = self

		#                 N:0   NE:1 E:2  SE:3  S:4  SW:5 W:6  NW:7
		# opposite:       S:4   SW:5 W:6  NW:7  N:0  NE:1 E:2  SE:3 
		self.neighbors = [None, None,None,None, None,None,None,None]
		neighborlen = len(self.neighbors)
		self.get_opposite = lambda idx: (idx+(neighborlen>>1)) % neighborlen

		#
		#  (-1,-1) (0,-1) (1,-1)
		#  (-1, 0) (0, 0) (1, 0)
		#  (-1, 1) (0, 1) (1, 1)
		#

		self.chg_funcs = (
			lambda (x,y): (x,y-1),
			lambda (x,y): (x+1,y-1),
			lambda (x,y): (x+1,y),
			lambda (x,y): (x+1,y+1),
			lambda (x,y): (x,y+1),
			lambda (x,y): (x-1,y+1),
			lambda (x,y): (x-1,y),
			lambda (x,y): (x-1,y-1),
		)

		self.neighbor_poses = {cfunc(self.pos):idx for idx,cfunc in enumerate(self.chg_funcs)}
		self.reconnect()

	def connect(self, other, dir):
		self.neighbors[dir] = other
		other.neighbors[self.get_opposite(dir)] = self
		self.recalc_values()

	def reconnect(self):
		for pos in self.neighbor_poses:
			val = self.previous.get(pos)
			if val is not None:
				self.connect(val,self.neighbor_poses[pos])


	def recalc_values(self):
		for k in self.neighbors:
			if k is not None:
				if self.value + 1 > k.value: # self: 9 k: 7 -> self: 8 k: 7
					self.value = k.value + 1
				elif self.value + 1 < k.value: # self 6 k: 8 -> self: 6 k: 7
					k.value = self.value + 1

	def step_all(self):
		for k in self.previous.values():
			k.step()

	def step(self):
		for pos,idx in self.neighbor_poses.items():
			if pos not in self.previous or self.neighbors[idx] is None:
				nx,ny = pos

				if pos in self.previous:
					val = self.previous[nx,ny]
				else:
					val = Cell((nx,ny), self.value+1, self.previous)

				self.neighbors[idx] = val
		self.recalc_values()

	def step_to(self, pos):
		while pos not in self.previous:
			self.step_all()

	def fill_rect(self, tl, br):
		lx,ty = tl
		rx,by = br
		self.step_to(tl)
		self.step_to(br)
		self.step_to((rx,ty))
		self.step_to((lx,by))

	def get_cells(self):
		out = []
		tl = min(self.previous)[0], min(self.previous,key=lambda x:x[1])[1]
		br = max(self.previous)[0], max(self.previous,key=lambda x:x[1])[1]
		for x in range(tl[0],br[0]+1):
			out.append([])
			for y in range(tl[1],br[1]+1):
				if (x,y) in self.previous: out[-1].append(self.previous[x,y])
				else: out[-1].append(None)
		return out




	@staticmethod
	def get_topleftmost(cell):
		return cell.neighbors[min(cell.neighbors, key=lambda (x,y): x+y)]

if __name__ == '__main__':
	import unittest
	class CellTest(unittest.TestCase):
		def new_cell(self, pos=(0,0),prev=None):
			if prev is None:
				prev = {}
			return Cell(pos, 0, prev)

		def test_step00(self):
			cell = self.new_cell()
			self.assertEqual(cell.neighbors, [None,None,None,None,None,None,None,None])
			cell.step()
			for k in cell.neighbors:
				self.assertNotEqual(k,None)
				self.assertEqual(cell.value+1, k.value)
				self.assertIn(cell, k.neighbors)
				self.assertIn(k, cell.neighbors)

		def test_step01(self):
			pattern = numpy.array([
				[2,2,2,2,2],
				[2,1,1,1,2],
				[2,1,0,1,2],
				[2,1,1,1,2],
				[2,2,2,2,2],
			])
			cell = self.new_cell((2,2))
			self.assertEqual(cell.neighbors, [None,None,None,None,None,None,None,None])
			cell.step_all()
			cell.step_all()
			dx = min(cell.previous)
			dy = min(cell.previous, key=lambda a:a[1])
			result = numpy.zeros((5,5)).astype('int')
			result[:] = 9
			for (x,y),v in cell.previous.items():
				result[x,y] = v.value
			self.assertTrue((result==pattern).all())


		def test_step02(self):
			pattern = numpy.array([
				[1,1,1,2,2],
				[1,0,1,1,2],
				[1,1,0,1,2],
				[2,1,1,1,2],
				[2,2,2,2,2],
			])
			cell = self.new_cell((2,2))
			self.assertEqual(cell.neighbors, [None,None,None,None,None,None,None,None])
			cell = self.new_cell((1,1),cell.previous)
			cell.step_all()
			cell.step_all()
			dx = min(cell.previous)
			dy = min(cell.previous, key=lambda a:a[1])
			result = numpy.zeros((5,5)).astype('int')
			result[:] = 9
			for (x,y),v in cell.previous.items():
				result[x,y] = v.value
			self.assertTrue((result==pattern).all())



		def test_getcells(self):
			cell = self.new_cell((4,4))
			self.assertEqual(len(cell.previous), 1)
			self.assertEqual(cell.get_cells(), [[cell]])



	prev = {}
	q = [Cell( (x,y), 0, prev ) for x in range(10) for y in range(10) if random.random() < 1.0/50]
	#unittest.main()

	#a = Cell( (0,0), 0, {})
	previous = {}
	for r in range(0,10,2):
		for c in range(0,10,2):
			a = Cell( (random.randrange(r*4,r*4+10),random.randrange(c*4,c*4+10)), 0, previous)
	#a.step()
	import time
	t0 = time.time()
	a.fill_rect((0,0), (40,40))
	t1 = time.time() - t0
	print int(t1*1000), 'msecs for mapgen'
	_ = a.get_cells()
	q = numpy.zeros((40,40))
	q[:] = 9
	for (x,y) in a.previous:
		if 0 < x < 40 and 0 < y < 40:
			q[x,y] = a.previous[x,y].value
	r = numpy.zeros((42,42))
	r[:] = 9
	r[1:-1,1:-1] = q

	q = (r>3).astype('int')

	for x in q:
		for y in x:
			if y == 0: print ' ',
			else: print '#',
			#if y is not None: print '%2d'% y,
			#else: print '  ',
		print
	del _
