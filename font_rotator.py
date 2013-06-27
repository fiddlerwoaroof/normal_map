#!/usr/bin/python
#
# Edward Langley (C) 2013
#
# For rotating Dwarf Fortress tilesets to workaround TCOD limitations.
# These tilesets also need to have the pink background removed. (I think)
#
import Image
import numpy
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('fro')
parser.add_argument('to')
args = parser.parse_args()

file = Image.open(args.fro)
data = numpy.asarray(file)

tiles = [numpy.split(col,16,1) for col in numpy.split(data,16)]
tiles = zip(*tiles)
tiles = [numpy.concatenate(x,1) for x in tiles]
tiles = numpy.concatenate(tiles)
Image.fromarray(tiles).save(args.to)

