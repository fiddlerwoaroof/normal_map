
# Copyright (c) 2013 Edward Langley
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# Neither the name of the project's author nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import division
import collections
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

class MapData(collections.MutableMapping):
	def __init__(self, data, base=9):
		self.data = data
		self.base = base
		self.below = [[None for __ in range(base)] for ___ in range(base)]

	@classmethod
	def rand_new(cls, mean, base=9):
		data = numpy.random.normal(mean, max(mean/4,1), (base,base)).astype(int)
		return cls(data,base)

	def get_cell(self, x,y, depth=1):
		cur = self
		if depth > 1:
			below = self.get_below(x,y)
			depth -= 1
			while depth > 1:
				below = below.get_below(0,0)
				depth -= 1
			cur = below
		return cur.data[y,x]

	def get_below(self, x,y):
		below = self.below[y][x]
		if below is None:
			mean = self.get_cell(x,y)
			below = self.below[y][x] = self.rand_new(mean,self.base)
		return below

	def get_all_below(self):
		for y, lis in enumerate(self.below):
			for x, val in enumerate(lis):
				if val is not None: continue
				self.get_below(x,y)
		return numpy.concatenate([numpy.concatenate([x.data for x in l],1) for l in self.below])

	def get_rect_below(self, x,y, w,h):
		tw = w/self.base
		tw = int(numpy.ceil(tw))
		th = h/self.base
		th = int(numpy.ceil(th))
		out = []
		for ny  in range(y,min(len(self.data),y+th)):
			out.append([])
			for nx in range(x,min(len(self.data[0]),x+tw)):
				out[-1].append(self.get_below(nx,ny))

		return numpy.concatenate([numpy.concatenate([x.data for x in l],1) for l in out])[:h,:w]

	def __getitem__(self, key):
		return self.data.__getitem__(key)
	def __delitem__(self, key):
		self.data.__setitem__(key, 0.0)
	def __len__(self):
		return len(self.data)
	def __setitem__(self, key, value):
		self.data.__setitem__(key, value)
	def __iter__(self):
		return iter(self.data)


class Map(object):
	def __init__(self, data, depth, base=9):
		self.data = data
		self.depth = depth
		self.base = base

	@classmethod
	def rand_new(cls, depth,base=9):
		data = MapData.rand_new(numpy.random.randint(0,10),base)
		return cls(data,depth)

	def get_level(self, level):
		cur = self.data
		for idx in range(1, level):
			cur = cur.get_below(0,0)
		return cur.get_rect_below(0,0, self.base**level, self.base**level)

	def to_pgm(self,level):
		level = self.data[level].copy()
		level -= min(l.min() for l in self.data)
		maxval = level.max()
		width = len(level)
		height = len(level[0])
		data = '\n'.join(' '.join(str(c) for c in row) for row in level)
		return PGM_template % dict(width=width,height=height,maxval=maxval,data=data)


