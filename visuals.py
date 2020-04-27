#!/usr/bin/env python3


import os
import sys
import tkinter as tk
import numpy as np
import threading
import logic
import a_star


class GameCanvas:
	"""contols visuals"""
	cv_width = 896
	cv_height = 992
	width = 28
	height = 31
	px_size = 32
	update_ms = 8

	def __init__(self, master, lname):
		self.master = master
		self.lname = lname

		# start game controller
		px, py = 14, 23
		pd = (0, 0)
		self.gc = logic.GameController(px, py, pd, self.lname)

		# draw canvas
		self.canvas = tk.Canvas(self.master, width=self.cv_width, height=self.cv_height, highlightthickness=0, bg='black')
		self.canvas.pack()

		# draw background
		self.background = tk.PhotoImage(file='{}/background.png'.format(self.lname))
		self.canvas.create_image(0, 0, image=self.background, anchor='nw')

		# create and draw coins
		self.coin_image = tk.PhotoImage(file='coins/coin.png')
		self.coins = np.empty(shape=(28, 31))
		for x in range(self.width):
			for y in range(self.height):
				if self.gc.level.coins[y, x]:
					xv, yv = x*self.px_size, y*self.px_size
					self.coins[x, y] = self.canvas.create_image(xv, yv, image=self.coin_image, anchor='nw')

		# create and draw pacman
		self.pacman = Pacman(self.canvas, self.gc.pacman)

		# create and draw ghosts
		self.blinky = MovingObject(self.canvas, 32, self.gc.blinky, 'blinky.png', 1)
		self.inky = MovingObject(self.canvas, 32, self.gc.blinky, 'inky.png', 1)
		self.pinky = MovingObject(self.canvas, 32, self.gc.blinky, 'pinky.png', 1)
		self.clive = MovingObject(self.canvas, 32, self.gc.blinky, 'clive.png', 1)

		# draw score
		self.score_text = self.canvas.create_text(self.cv_width, 0, fill='white', text=str(self.gc.score), anchor='ne')

		self.running = False
		self.a_cycle = 0

	def keypress(self, event):
		"""handles keyboard commands/ controls"""
		key = event.keysym
		self.gc.keypress(key)

	def start(self):
		"""preps for main game loop"""
		self.running = True
		self.master.bind('<Key>', self.keypress)
		self.gameloop()

	def stop(self):
		"""closes main game loop"""
		self.master.unbind('<Key>')
		self.running = False

	def update_line(self, path):
		if len(path) < 2:
			return
		p_pos = (self.gc.pacman.x, self.gc.pacman.y)
		new_path = []
		for i in path:
			i = list(i)
			i[0] = (i[0]*self.px_size)+16
			i[1] = (i[1]*self.px_size)+16
			new_path.append(tuple(i))
		self.canvas.coords(self.line, list(sum(new_path, ())))

	def gameloop(self):
		"""main loop for game functions"""

		# pacman movement and update line
		if self.a_cycle % (32/self.pacman.speed) == 0:
			self.gc.gameloop()


		self.pacman.move(self.gc.pacman)
		self.blinky.move(self.gc.blinky)
		self.inky.move(self.gc.inky)
		self.pinky.move(self.gc.pinky)
		self.clive.move(self.gc.clive)

		# coins
		on_coin = self.gc.check_coin()
		if on_coin:
			self.canvas.delete(int(self.coins[tuple(self.gc.pacman.pos)]))
			self.canvas.itemconfig(self.score_text, text=str(self.gc.score))

		self.a_cycle += 1

		if not self.running:
			self.stop()
		else:
			self.master.after(self.update_ms, self.gameloop)


class MovingObject:

	def __init__(self, canvas, px_size, data, img_loc, speed):
		self.canvas = canvas
		self.px_size = px_size
		self.speed = speed

		self.image = tk.PhotoImage(file=img_loc)

		self.char = self.canvas.create_image(data.pos[0]*self.px_size, data.pos[1]*self.px_size, image=self.image, anchor='nw')

	def move(self, data):
		d = data.direction
		self.canvas.move(self.char, d[0]*self.speed, d[1]*self.speed)


class Pacman(MovingObject):
	img_loc = 'pacman/pacman.png'

	def __init__(self, canvas, data, px_size=32, speed=1):
		super().__init__(canvas, px_size, data, self.img_loc, speed)


def main():
	xc_dir, _ = os.path.split(sys.argv[0])  # get file path
	if xc_dir:
		os.chdir(xc_dir)  # set current directory

	root = tk.Tk(className='Pacman')  # sets window name
	root.resizable(False, False)

	game_canvas = GameCanvas(root, 'level1')

	root.after(0, game_canvas.start)
	root.mainloop()


if __name__ == '__main__':
	main()
