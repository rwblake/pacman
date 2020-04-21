#!/usr/bin/env python3


import sys
import os
import tkinter as tk
import numpy as np


class GameCanvas:
	"""controls main game screen etc"""

	def __init__(self, master, width=480, height=480, level='level1'):
		self.master = master
		self.width = width
		self.height = height
		self.level = level

		self.update_ms = 20

		self.canvas = tk.Canvas(self.master, width=width, height=height, highlightthickness=0, bg='black')
		self.canvas.pack()

		self.running = False
		self.levelnum = 1

		self.levels = {1: Level('level1')}
		self.canvas.create_image(0, 0, image=self.levels[self.levelnum].background, anchor='nw')  # add background image

		self.pacman = PacMan(self.canvas, 0, 8)

	def keypress(self, event):
		"""handles keyboard commands/ controls"""
		key = event.keysym

		if key == 'w' or key == 'Up':  # up
			self.pacman.next_direction = 0
		elif key == 'a' or key == 'Left':  # left
			self.pacman.next_direction = 3
		elif key == 's' or key == 'Down':  # down
			self.pacman.next_direction = 2
		elif key == 'd' or key == 'Right':  # right
			self.pacman.next_direction = 1

		if key == 'q':  # quit
			self.stop()

	def start(self):
		"""preps for main game loop"""
		self.running = True
		self.master.bind('<Key>', self.keypress)
		self.gameloop()

	def stop(self):
		"""closes main game loop"""
		self.master.unbind('<Key>')
		self.running = False

	def gameloop(self):
		"""self called loop for main functions"""

		#pacman movement
		wm = self.levels[self.levelnum].walls
		ndb = self.pacman.next_overlaps_box(self.pacman.next_direction)
		n_wm = wm[ndb[1]:ndb[3], ndb[0]:ndb[2]]
		if not np.any(n_wm):
			self.pacman.direction = self.pacman.next_direction
		cdb = self.pacman.next_overlaps_box(self.pacman.direction)
		n_wm = wm[cdb[1]:cdb[3], cdb[0]:cdb[2]]
		if not np.any(n_wm):
			self.pacman.update()
		else:
			self.pacman.direction = None

		if not self.running:
			self.stop()
		else:
			self.master.after(self.update_ms, self.gameloop)


class PacMan:
	"""controls pacman characters"""
	size = 24  # px width and height

	def __init__(self, canvas, xcoord, ycoord, vel=1, direction=None):
		self.canvas = canvas
		self.xcoord = xcoord
		self.ycoord = ycoord
		self.vel = vel
		self.direction = direction  # 0-3 where 0 is N, 1 is E etc OR None

		self.next_direction = None

		self.dir_vals = {None: (0, 0), 0: (0, -1), 1: (1, 0), 2: (0, 1), 3: (-1, 0)}

		self.images = {'0': tk.PhotoImage(file='pacman/0.png'),
		               '1r': tk.PhotoImage(file='pacman/1r.png'),
		               '1d': tk.PhotoImage(file='pacman/1d.png'),
		               '1l': tk.PhotoImage(file='pacman/1l.png'),
		               '1u': tk.PhotoImage(file='pacman/1u.png'),
		               '2r': tk.PhotoImage(file='pacman/2r.png'),
		               '2d': tk.PhotoImage(file='pacman/2d.png'),
		               '2l': tk.PhotoImage(file='pacman/2l.png'),
		               '2u': tk.PhotoImage(file='pacman/2u.png')}

		self.pacman = self.canvas.create_image(self.xcoord, self.ycoord, image=self.images['0'], anchor='nw')

		self.moving = False
		self.counter = 0
		self.animation_frame = 0

	def next_overlaps_box(self, direction):
		"""the area where pacman would move in next refresh"""
		x, y = map(lambda x: x*self.vel, self.dir_vals[direction])
		a = self.xcoord+x
		b = self.ycoord+y
		c = self.xcoord+x+self.size
		d = self.ycoord+y+self.size
		return (a, b, c, d)

	def update_image(self):
		if self.moving:
			if self.animation_frame == 3:
					self.animation_frame = 1
			else:
				self.animation_frame += 1
		else:
			self.animation_frame = 0

		i = ''

		if self.animation_frame == 0:
			i = '0'
		else:
			k = {1: '1', 2: '2', 3: '1'}
			i += k[self.animation_frame]
			k = {0: 'u', 1: 'r', 2: 'd', 3: 'l'}
			i += k[self.direction]

		self.canvas.itemconfig(self.pacman, image=self.images[i])

	def update(self):
		"""moves pacman in direction by velocity"""
		xvel = self.dir_vals[self.direction][0]*self.vel
		yvel = self.dir_vals[self.direction][1]*self.vel

		if xvel != 0 or yvel != 0:
			self.moving = True
		else:
			self.moving = False

		self.counter += 1

		self.xcoord += xvel
		self.ycoord += yvel
		self.canvas.move(self.pacman, xvel, yvel)

		if not self.moving:
			self.update_image()
		elif self.counter % 3 == 0:
			self.update_image()


class Level:
	"""holds all level data"""

	def __init__(self, name):
		self.background = tk.PhotoImage(file='{}/background.png'.format(name))  # level background image
		self.walls = np.load('level1/walls.npy')  # 2d boolean np array of wall/ no wall


def main():
	xc_dir, _ = os.path.split(sys.argv[0])  # get file path
	if xc_dir:
		os.chdir(xc_dir)  # set current directory

	root = tk.Tk(className='Pacman')  # sets window name
	root.resizable(False, False)
	root.call('wm', 'iconphoto', root, tk.PhotoImage(file='pacman/1r.png'))

	canvas = GameCanvas(root)

	root.after(0, canvas.start)
	root.mainloop()


if __name__ == '__main__':
	main()
