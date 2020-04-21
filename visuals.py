#!/usr/bin/env python3


import os
import sys
import tkinter as tk
import numpy as np
import logic


class GameCanvas:
	"""contols visuals"""
	cv_width = 896
	cv_height = 992
	width = 28
	height = 31
	px_size = 32
	update_ms = 10

	def __init__(self, master, lname):
		self.master = master
		self.lname = lname

		px, py = 14, 23
		pd = (0, 0)

		self.gc = logic.GameController(px, py, pd, self.lname)

		self.canvas = tk.Canvas(self.master, width=self.cv_width, height=self.cv_height, highlightthickness=0, bg='black')
		self.canvas.pack()

		self.background = tk.PhotoImage(file='{}/background.png'.format(self.lname))
		self.canvas.create_image(0, 0, image=self.background, anchor='nw')

		self.coin_image = tk.PhotoImage(file='coins/coin.png')
		self.coins = np.empty(shape=(28, 31))
		for x in range(self.width):
			for y in range(self.height):
				if self.gc.level.coins[y, x]:
					xv, yv = x*self.px_size, y*self.px_size
					self.coins[x, y] = self.canvas.create_image(xv, yv, image=self.coin_image, anchor='nw')

		self.pacman = Pacman(self.canvas, self.px_size, self.gc.pacman)

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

	def gameloop(self):
		"""main loop for game functions"""

		# pacman movement
		if self.a_cycle % 32 == 0:
			self.gc.move_pacman()
		self.pacman.move(self.gc.pacman)

		#coins
		on_coin = self.gc.check_coin()
		if on_coin:
			x, y = self.gc.pacman.x, self.gc.pacman.y
			self.canvas.delete(int(self.coins[x, y]))
			self.canvas.itemconfig(self.score_text, text=str(self.gc.score))
		'''# pacman movement
		if self.pacman.between_square == 0:
			valid = logic.check_movement(self.pacman.data.x, self.pacman.data.y, self.pacman.next_direction, self.level.data.walls)
			if valid:
				self.pacman.data.direction = self.pacman.next_direction
		valid = logic.check_movement(self.pacman.data.x, self.pacman.data.y, self.pacman.data.direction, self.level.data.walls)
		if valid:
			x, y = self.pacman.data.direction
			self.canvas.move(self.pacman.pacman, x, y)
			if self.pacman.between_square == 0:
				self.pacman.data.move()
		self.pacman.between_square += 1
		if self.pacman.between_square == 32:
			self.pacman.between_square = 0'''

		self.a_cycle += 1

		if not self.running:
			self.stop()
		else:
			self.master.after(self.update_ms, self.gameloop)


class Pacman:

	def __init__(self, canvas, px_size, data):
		self.canvas = canvas
		self.px_size = px_size

		self.image = tk.PhotoImage(file='pacman/pacman.png')

		self.pacman = self.canvas.create_image(data.x*self.px_size, data.y*self.px_size, image=self.image, anchor='nw')

	def move(self, data):
		d = data.direction
		self.canvas.move(self.pacman, d[0], d[1])


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
