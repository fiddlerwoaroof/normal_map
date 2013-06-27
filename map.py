from __future__ import division
import random
import numpy

#				5			  #
#							  #
#				|			  #
#				V			  #
#							  #
#			 3 4 6		  #
#			 7 5 5		  #
#			 1 9 5		  #
#							  #
#				|			  #
#				V			  #
#							  #
#	1 4 2  3 6 4  5 7 6 #
#	5 3 3  2 4 5  3 9 5 #
#	3 3 3  4 3 5  7 5 6 #
#							  #
#	5 9 7  . . .  . . . #
#	6 8 5  . . .  . . . #
#	9 7 7  . . .  . . . #
#							  #
#	1 1 1  . . .  . . . #
#	1 1 1  . . .  . . . #
#	1 1 1  . . .  . . . #
PGM_template = """\
P2
%(width)d %(height)d
%(maxval)d
%(data)s
"""

class Map(object):
	def __init__(self, data, depth, base=9):
		self.data = data
		self.depth = depth
		self.base = base
	@classmethod
	def rand_new(cls, depth,base=9):
		data = [numpy.random.random_integers(0,10,(1,1))]
		for x in range(1,depth+1):
			global out
			out = numpy.zeros((base**x, base**x),'int')
			for r, row in enumerate(data[-1]):
				for c, col in enumerate(row):
					new = numpy.random.normal(col,max(col/4,1),(base,base)).astype(int)
					out[r*base:r*base+base,c*base:c*base+base] = new
			data.append(out)
		return cls(data,depth)

	def to_pgm(self,level):
		level = self.data[level].copy()
		level -= min(l.min() for l in self.data)
		maxval = level.max()
		width = len(level)
		height = len(level[0])
		data = '\n'.join(' '.join(str(c) for c in row) for row in level)
		return PGM_template % dict(width=width,height=height,maxval=maxval,data=data)


