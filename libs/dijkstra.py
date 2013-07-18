try: import numpypy
except ImportError: pass
import numpy
import random
import time

import heapq
class PriorityQueue(object):
	def __init__(self):
		self.queue = []
		self.tmp = {}
	def push(self, priority, item):
		entry = [priority, item]
		self.tmp[item] = entry
		heapq.heappush(self.queue, entry)
	def pop(self):
		result = heapq.heappop(self.queue)
		while self.queue:
			if result[1] is not None: break
			result = heapq.heappop(self.queue)
		return result[1]
	def change(self, priority, item):
		newentry = [priority, item]
		if item in self.tmp:
			self.tmp[item][-1] = None
			self.tmp[item] = newentry
		heapq.heappush(self.queue, newentry)
	def __nonzero__(self):
		return bool(self.queue)

def dijkstra(graph, sources, dtype='int'):
	if not hasattr(sources[0], '__iter__'):
		sources = [sources]
	dist = numpy.zeros(graph.shape)
	w,h = graph.shape
	max = w*h+1
	dist[:] = max
	#previous = numpy.zeros(graph.shape+(2,))#.astype('int')
	#previous[:] = max

	for source in sources:
		dist[source] = 0

	width, height = graph.shape

	Q = PriorityQueue()
	for x in range(width):
		for y in range(height):
			Q.push(dist[x,y], (x,y))

	it = 0
	t0 = time.time()
	while Q:
		it += 1
		u = Q.pop()

		if u is None or dist[u] == max: break

		for v in neighbors(u):
			nx,ny = v
			if nx >= width or ny >= height: continue
			elif nx < 0 or ny < 0: continue

			alt = dist[u] + dist_between(u, v, graph)
			if alt < dist[v]:
				dist[v] = alt
				#previous[v] = u
				Q.change(alt, v)
	dt = time.time() - t0
	dt *= 1000
	print '%d iterations in %4.4f milliseconds: %4.4f iterations/millisecond' % (it, dt, it/dt)
	return dist#, previous

def dist_between(a,b, graph):
	cost = graph[b]
	return cost

def neighbors(coord):
	x,y = coord
	return (x-1, y-1), (x-1, y), (x-1, y+1), (x, y+1), (x+1, y+1), (x+1, y), (x+1, y-1), (x, y-1)


goals = []
with file('map') as f:
	map = f.read().strip()
	map = map.split('\n')
	map = [list(x) for x in map]
	map = zip(*map)
	width, height = len(map[0]), len(map)
	graph = numpy.zeros((width, height))
	for y,row in enumerate(map):
		for x,cell in enumerate(row):
			graph[x,y] = (width*height+1 if cell=='#' else 1)
			if cell == '*': goals.append((x,y))

width, height = graph.shape

import bresenham

goals = list(set(goals))
print goals

import coords
tree = coords.CoordTree(random.choice(goals))
for g in goals:
	tree.add(g)

tree.print_tree()
print tree.map(lambda x:x.pos)
print '---'

cur = tree
visited = set()
stack = [x for x in cur.surroundings if x is not None]
nexts = stack[:]

while stack:
	a = cur.pos
	visited.add(a)
	for other in nexts:
		b = other.pos
		x1,y1 = a
		x2,y2 = b
		print (x1,y1), (x2,y2)
		line = bresenham.line(x1, y1, x2, y2,2)
		line.next()
		for x,y in line:
			print x,y
			graph[x,y] = 1

	cur = stack.pop(0)
	nexts = [x for x in cur.surroundings if x is not None]
	stack.extend(x for x in nexts if x.pos not in visited)

#graph = numpy.random.standard_normal((height,width)) * 0.5
#if (graph < 0).any():
#	graph -= graph.min()
#graph = graph.astype('int')
#graph[:] = 1

#for ___ in range(20):
	#graph[random.randrange(height), random.randrange(width)] = 4000

#for x,row in enumerate(graph):
 #for y,cell in enumerate(row):
  #if (x,y) in goals: print '%1s' % '*',
  #elif cell == 4001: print '#',
  #else: print '%1d' % cell,
 #print

t1 = time.time()
rounds = 1
for ___ in range(rounds):
	d = dijkstra(graph, goals)
dt = time.time() - t1
dt *= 1000
print '%4.4f' % dt, 'milliseconds for %d rounds' % rounds, '%4.4f milliseconds per round' % (dt/rounds)



print  '---'

for x in d:
 for y in x:
  if y > width*height: print '..',
  else: print '%2d' % y,
 print

#print '---'

#for k in (d > 5).astype('int'):
 #for y in k:
  #if y: print '#',
  #else: print ' ',
 #print

