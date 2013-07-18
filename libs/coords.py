class CoordTree(object):
	made = {}
	def __init__(self, pos, nw=None, ne=None, se=None, sw=None):
		self.nw = nw
		self.ne = ne
		self.se = se
		self.sw = sw
		self.pos = pos
		self.made[pos] = self
		self.added = 0

	def add(self, coord):
		sx,sy = self.pos
		ox,oy = coord


		if coord == self.pos: pass
		elif ox >= sx:
			if oy >= sy:
				self.add_ne(coord)
			elif oy < sy:
				self.add_se(coord)

		elif ox < sx:
			if oy >= sy:
				self.add_nw(coord)
			elif oy < sy:
				self.add_sw(coord)
		else:
			raise

	def _add(dir):
		dist = lambda (x1,y1), (x2,y2): ( (x1-x2)**2 + (y1-y2)**2 ) ** 0.5

		def _adder(self, coord):
			self.added += 1
			cur_n = getattr(self, dir)
			if cur_n is None:
				setattr(self, dir, CoordTree(coord))
			elif dist(self.pos, cur_n.pos) >= dist(self.pos, coord):
				new = CoordTree(coord)
				setattr(new, dir, cur_n)
				setattr(self, dir, new)
			else:
				cur_n.add(coord)
		return _adder

	add_nw = _add('nw')
	add_ne = _add('ne')
	add_se = _add('se')
	add_sw = _add('sw')

	@property
	def surroundings(self):
		return self.nw, self.ne, self.se, self.sw

	def get_tree(self):
		return (self.pos, [ (None if x is None else x.get_tree()) for x in self.surroundings ])

	def print_tree(self, ind=0):
		print ' '*ind, self.pos
		for k in self.surroundings:
			nind = ind + 2
			if k is None:
				print ' '*nind, k
			else:
				k.print_tree(nind)

	def map(self, cb):
		result = []
		stack = [self]
		cur = None
		visited = set()
		while stack:
			cur = stack.pop(0)
			print cur.pos, [x.pos for x in stack], {x.pos for x in visited}
			visited.add(cur)
			stack.extend(x for x in cur.surroundings if (x is not None and x not in visited))
			result.append(cb(cur))
		print cur.pos
		return result

	def count(self):
		if all(x is None for x in self.surroundings):
			return 1
		else:
			return 1 + sum(x.count() for x in self.surroundings if x is not None)

if __name__ == '__main__':
	import random
	root = CoordTree( (5,5) )
	a = range(10)
	b = range(10)
	random.shuffle(a)
	random.shuffle(b)
	for x in a:
		for y in b:
			root.add( (x,y) )
			print root.count(), (x,y)
