from __future__ import print_function, division

# from: http://roguebasin.roguelikedevelopment.org/index.php?title=Bresenham's_Line_Algorithm#Python

def line(x0, y0, x1, y1, wd):
	dx = abs(x1-x0); sx = 1 if x0 < x1 else -1
	dy = abs(y1-y0); sy = 1 if y0 < y1 else -1
	err = dx-dy
	ed = 1 if dx + dy == 0 else (dx*dx + dy*dy)**0.5

	e2 = x2 = y2 = 0

	wd = (wd + 1) / 2.0
	while True:
		yield (x0,y0)
		e2 = err; x2 = x0
		if 2*e2 >= -dx:
			e2 += dx
			y2 = y0
			while e2 < ed*wd and (y1 != y2 or dx > dy):
				yield (x0, y2)
				y2 += sy
				e2 += dx
			if x0 == x1: break
			e2 = err
			err -= dy
			x0 += sx
		if 2*e2 <= dy:
			e2 = dx-e2
			while e2 < ed*wd and (x1 != x2 or dx < dy):
				yield (x2, y0)
				x2 += sx
				e2 += dy
			if y0 == y1: break
			err += dx
			y0 += sy
