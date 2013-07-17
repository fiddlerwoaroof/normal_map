def row2diterate(dct, width, height):
	for y in range(height):
		for x in range(width):
			yield dct[c,r]

class Cell(object):
	def __init__(self, pos, value=0, neighbors = None, previous = None):
		self.pos = pos
		self.value = value

		if previous is None: previous = {}
		self.previous = previous
		self.previous[pos] = self

		if neighbors is None: neighbors = [None,None,None,None]
		chg_funcs = [
			lambda (x,y): (x,y-1),
			lambda (x,y): (x+1,y),
			lambda (x,y): (x,y+1),
			lambda (x,y): (x-1,y),
		]
		for idx,val in enumerate(neighbors):
			val = neighbors[idx] = previous.get(chg_funcs[idx](pos))
			if val is not None: val.reconnect()
		self.neighbors = neighbors


	def reconnect(self):
		chg_funcs = [
			lambda (x,y): (x,y-1),
			lambda (x,y): (x+1,y),
			lambda (x,y): (x,y+1),
			lambda (x,y): (x-1,y),
		]
		for idx,val in enumerate(self.neighbors):
			if val is None: continue
			self.neighbors[idx] = self.previous.get(chg_funcs[idx](self.pos))

	def expand(self, tl=(0,0),br=(None,None), recurse=0):
		chg_funcs = [
			lambda (x,y): (x,y-1),
			lambda (x,y): (x+1,y),
			lambda (x,y): (x,y+1),
			lambda (x,y): (x-1,y),
		]


		for idx, (cfunc,val) in enumerate(zip(chg_funcs,self.neighbors)):
			if val is None:
				nx,ny = cfunc(self.pos)
				if any(a<b for (a,b) in zip((nx,ny), tl)): continue
				elif br[0] is not None and any(a>b for (a,b) in zip((nx,ny), br)): continue

				if (nx,ny) in self.previous:
					val = self.previous[nx,ny]
					if val.value + 1 < self.value:
						self.value = val.value + 1
				else:
					val = Cell((nx,ny), self.value+1, None, self.previous)

				self.neighbors[idx] = val
				if self not in val.neighbors or val.value > self.value + 1:
					val.expand(tl,br)




	@staticmethod
	def get_topleftmost(cell):
		return cell.neighbors[min(cell.neighbors, key=lambda (x,y): x+y)]

