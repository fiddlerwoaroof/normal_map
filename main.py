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
import colorsys
import ctypes
import libtcodpy as libtcod
import random
import time
import yaml

inst = lambda a:a()
@inst
class Settings:
	def __init__(self):
		with file('data/settings.yaml') as f:
			self.settings = yaml.safe_load(f)
	def __getattr__(self, attr):
		return self.settings[attr]

	SCREEN_WIDTH = 75
	SCREEN_HEIGHT = 20
	DISPLAY_HEIGHT = property(lambda self: self.SCREEN_HEIGHT+2)
	LIMIT_FPS = 20
	BASE = 8
	LEVELS = 3

libtcod.console_init_root(Settings.SCREEN_WIDTH, Settings.DISPLAY_HEIGHT, 'Mapping', False)
libtcod.console_set_custom_font("terminal.png",libtcod.FONT_LAYOUT_ASCII_INROW|libtcod.FONT_TYPE_GREYSCALE)
#libtcod.console_set_fullscreen(True)
con = libtcod.console_new(Settings.SCREEN_WIDTH, Settings.SCREEN_HEIGHT)
blank = libtcod.console_new(Settings.SCREEN_WIDTH, Settings.SCREEN_HEIGHT)
#for x in range(Settings.SCREEN_WIDTH):
	#for y in range(Settings.SCREEN_HEIGHT):


message_con = libtcod.console_new(Settings.SCREEN_WIDTH, 2)
libtcod.console_set_default_background(message_con,libtcod.red)
#libtcod.console_set_default_background(blank,libtcod.red)


libtcod.sys_set_fps(Settings.LIMIT_FPS)

import map
level = 1
mp = map.Map.rand_new(Settings.LEVELS, Settings.BASE) ## warning: exponential BASE ** LEVELS
mapping = {}

colors = {
	':': colorsys.rgb_to_hsv(0.0,0.0,1.0),
	chr(5): colorsys.rgb_to_hsv(0.0,0.5,0.0),
	'*': colorsys.rgb_to_hsv(1.0,1.0,0.0),
}

df = 1/40.0
for x in range(-20,20):
	char = random.choice(['.','.','.','*','*',';',':','"',"'",chr(5),'`'])
	if char in colors:
		h,s,v = colors[char]
		print s,v
		color = colorsys.hsv_to_rgb(h,s/1.75,v/2)
		bgcolor = colorsys.hsv_to_rgb(h,s/4,v/4)
	else:
		hue = x+21 * df
		color = colorsys.hsv_to_rgb(1/hue,0.5,0.5)
		bgcolor = colorsys.hsv_to_rgb(1/hue,0.25,0.25)

	color = [int(h*255) for h in color]
	bgcolor = [int(h*255) for h in bgcolor]
	mapping[x] = (libtcod.Color(*color), char, libtcod.Color(*bgcolor))

names = {
	'.': ('open',True,False),
	'*': ('meadow',True,False),
	';': ('marsh',1-0.05,False), ## Note: 1-0.05 means a 5% chance of being opaque
	':': ('pond',True,True),
	'"': ('heath',True,False),
	"'": ('marsh',1-0.15,False),
	chr(5): ('forest',False,True),
	'`': ('copse',1-0.5,False),
}

class LevelMap(object):
	def __init__(self, map):
		self.map = map
		self.fovmaps = [None]

	def get_tile_type(self, level,x,y):
		lvl = self.map.get_level(level)
		tile_val = mapping.get(lvl[y][x],(None,' '))[1]
		return names.get(tile_val,('',True,True))

	def get_fovmap(self,level):
		if level >= len(self.fovmaps):
			levelmap = mp.get_level(level)
			self.fovmaps.append(libtcod.map_new(len(levelmap), len(levelmap[0])))
			libtcod.map_clear(self.fovmaps[-1])
		return self.fovmaps[level]

	def has_level(self, level):
		return 1 <= level < len(self.fovmaps)

	def adj_map(self, level, x,y):
		fovmap = self.get_fovmap(level)
		__, trans,block = self.get_tile_type(level,x,y)
		trans = random.random() < trans
		libtcod.map_set_properties(fovmap, x,y, trans, not block)

	def comp_fov(self, level, player_x, player_y, light_radius=10):
		fovmap = self.get_fovmap(level)
		libtcod.map_compute_fov(fovmap, player_x, player_y, light_radius, False)

	def get_color(self, level,x,y, color):
		fovmap = self.get_fovmap(level)
		if libtcod.map_is_in_fov(fovmap, x,y) and libtcod.map_is_walkable(fovmap,x,y):
			#print 'cell in fov', level,x,y, libtcod.map_get_width(fovmap), libtcod.map_get_height(fovmap)
			color = [x/255 for x in color]
			h,s,v = colorsys.rgb_to_hsv(*color)
			r,g,b = [int(x*255) for x in colorsys.hsv_to_rgb(h,s, v+0.15)]
			color = libtcod.Color(r,g,b)
		return color

	def get_walkable(self, level, x,y):
		fovmap = self.get_fovmap(level)
		return libtcod.map_is_walkable(fovmap,x,y)

	def calculate_level(self, level):
		if not self.has_level(level):
			print 'calculate_level'
			lvl = mp.get_level(level)
			for y,row in enumerate(lvl):
				for x,__ in enumerate(row):
					lm.adj_map(level, x,y)



lm = LevelMap(mp)
lm.calculate_level(level)

libtcod.console_set_default_foreground(message_con, libtcod.white)
for c in [con,message_con]:
	libtcod.console_set_default_foreground(c, libtcod.white)
	libtcod.console_clear(c)

offset_x, offset_y = 0,0
levelmap = mp.get_level(level)
MAP_Y,MAP_X = len(levelmap), len(levelmap[0])
player_x, player_y = random.randrange(0,MAP_X),random.randrange(0,MAP_Y)
if not lm.get_walkable(level,player_x,player_y):
	player_x,player_y = [(x,y) for x in range(player_x-2,player_x+3) for y in range(player_y-2,player_y+3) if lm.get_walkable(level,x,y)][-1]
import time
ak=0
while not libtcod.console_is_window_closed():
	t0 = time.time()

	if player_x - offset_x >= Settings.SCREEN_WIDTH-5: offset_x += 5
	elif player_x - offset_x < 5: offset_x -= 5

	if player_y - offset_y >= Settings.SCREEN_HEIGHT-5: offset_y += 5
	elif player_y - offset_y < 5: offset_y -= 5

	offset_y = min(offset_y,MAP_Y-Settings.SCREEN_HEIGHT)
	offset_y = max(offset_y,0)

	offset_x = min(offset_x,MAP_X-Settings.SCREEN_WIDTH)
	offset_x = max(offset_x,0)

	t1 = time.time()
	lm.comp_fov(level, player_x, player_y,10)
	player_screen_pos = player_x-offset_x,player_y-offset_y
	for y,row in enumerate(levelmap[offset_y:offset_y+Settings.SCREEN_HEIGHT]):
		for x,cell in enumerate(row[offset_x:offset_x+Settings.SCREEN_WIDTH]):
			color,char,bgcolor = mapping.get(cell, (libtcod.Color(0,0,0),' ',libtcod.Color(0,0,0)))

			color = lm.get_color(level, x+offset_x, y+offset_y, color)
			bgcolor = lm.get_color(level, x+offset_x, y+offset_y, bgcolor)

			if (x,y) == player_screen_pos:
				color = libtcod.Color(128,128,100)
				char = '\x01'


			libtcod.console_set_char_foreground(con, x,y, color)
			libtcod.console_set_char_background(con, x,y, bgcolor)
			libtcod.console_set_char(con,x,y,char)

	print 'draw loop:', time.time()-t1

	libtcod.console_print(message_con, 0,1,lm.get_tile_type(level, player_x,player_y)[0])
	libtcod.console_blit(message_con, 0,0, Settings.SCREEN_WIDTH,2, 0, 0,Settings.DISPLAY_HEIGHT-2)

	blit_x,blit_y = 0,0
	blit_w,blit_h = Settings.SCREEN_WIDTH, Settings.SCREEN_HEIGHT
	if blit_x + MAP_X < Settings.SCREEN_WIDTH:
		blit_x = (Settings.SCREEN_WIDTH - (blit_x + MAP_X))/2
		blit_x = int(blit_x)
		blit_w = MAP_X
	if blit_y + MAP_Y < Settings.SCREEN_HEIGHT:
		blit_y = (Settings.SCREEN_HEIGHT - (blit_y + MAP_Y))/2
		blit_y = int(blit_y)
		blit_h = MAP_Y
	libtcod.console_blit(con, 0,0, blit_w,blit_h , 0,blit_x,blit_y)
	libtcod.console_flush()
	libtcod.console_clear(message_con)

	bk = (time.time()-t0)*1000
	print 'time to keypress:', bk
	print 'loop time:', ak+bk
	key = libtcod.Key()
	mouse = libtcod.Mouse()
	libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS, key, mouse, False)
	t0 = time.time()

	olevel = level
	diff = 1
	if key.shift:
		diff *= 10

	alt = key.lalt | key.ralt
	ox,oy = player_x,player_y
	dest_x,dest_y = player_x,player_y
	if key.vk == libtcod.KEY_DOWN and player_y < MAP_Y:
		dest_y += diff
		if alt:
			dest_x -= diff
	elif key.vk == libtcod.KEY_UP and dest_y > 0:
		dest_y -= diff
		if alt:
			dest_x += diff
	elif key.vk == libtcod.KEY_RIGHT and dest_x < MAP_X:
		dest_x += diff
		if alt:
			dest_y += diff
	elif key.vk == libtcod.KEY_LEFT and dest_x > 0:
		dest_x -= diff
		if alt:
			dest_y -= diff
	elif key.vk == libtcod.KEY_ESCAPE and any([key.lctrl,key.rctrl]): break
	elif key.c == ord('>') and level < mp.depth: level += 1
	elif key.c == ord('<') and level > 1: level -= 1

	dest_x = min(dest_x,MAP_X-1)
	dest_y = min(dest_y,MAP_Y-1)

	dest_x = max(dest_x,0)
	dest_y = max(dest_y,0)

	if olevel == level:
		libtcod.line_init(player_x,player_y, dest_x,dest_y)
		nx,ny = libtcod.line_step()
		while None not in {nx,ny}:
			if not lm.get_walkable(level,nx,ny):
				libtcod.console_print(message_con, 0,0,'You cannot walk through a %s' % lm.get_tile_type(level, nx,ny)[0])
				break
			print nx,ny
			player_x,player_y = nx,ny
			nx,ny = libtcod.line_step()

	else:
		player_prop = player_x/MAP_X, player_y/MAP_Y
		offset_prop = offset_x/MAP_X, offset_y/MAP_Y
		levelmap = mp.get_level(level)
		MAP_Y,MAP_X = len(levelmap), len(levelmap[0])
		libtcod.console_clear(0)
		libtcod.console_clear(con)

		print 'before:',offset_x, player_x, offset_x+Settings.SCREEN_WIDTH
		player_x = int(MAP_X * player_prop[0])
		player_y = int(MAP_Y * player_prop[1])

		offset_x = int(player_x - Settings.SCREEN_WIDTH / 2)
		if offset_x + Settings.SCREEN_WIDTH > MAP_X:
			offset_x -= (offset_x+Settings.SCREEN_WIDTH) - MAP_X
		offset_y = int(player_y - Settings.SCREEN_HEIGHT / 2)
		if offset_y + Settings.SCREEN_HEIGHT > MAP_Y:
			offset_y -= (offset_x+Settings.SCREEN_HEIGHT) - MAP_Y

		lm.calculate_level(level)

		if not lm.get_walkable(level,player_x,player_y):
			player_x,player_y = [(x,y) for x in range(player_x-2,player_x+3) for y in range(player_y-2,player_y+3) if lm.get_walkable(level,x,y)][-1]



	print 'time after keypress:', (time.time()-t0)*1000
