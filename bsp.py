import numpy
class Space(object):
	def __init__(self, w,h):
		data = numpy.zeros((h,w))
		if w > h:
			self.data = data[...,:w/2],data[...,w/2:]
		else:
			self.data = data[:h/2], data[h/2:]

