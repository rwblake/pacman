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
	update_ms = 6

	def __init__(self, master, lname):
		self.master = master
		self.lname = lname

		self.heart = tk.PhotoImage(file='images/heart.png')

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
		self.coin_image = tk.PhotoImage(file='images/coin.png')
		self.big_coin_image = tk.PhotoImage(file='images/big_coin.png')
		self.coins = np.empty(shape=(28, 31))
		for x in range(self.width):
			for y in range(self.height):
				if self.gc.level.coins[y, x]:
					xv, yv = x*self.px_size, y*self.px_size
					self.coins[x, y] = self.canvas.create_image(xv, yv, image=self.coin_image, anchor='nw')
				if self.gc.level.big_coins[y, x]:
					xv, yv = x*self.px_size, y*self.px_size
					self.coins[x, y] = self.canvas.create_image(xv, yv, image=self.big_coin_image, anchor='nw')

		# create and draw pacman
		self.pacman = Pacman(self.canvas, self.gc.pacman)

		# create and draw ghosts
		self.ghosts = [Ghost('blinky', self.canvas, 32, self.gc.ghosts[0], 1), Ghost('inky', self.canvas, 32, self.gc.ghosts[1], 1), Ghost('pinky', self.canvas, 32, self.gc.ghosts[2], 1), Ghost('clive', self.canvas, 32, self.gc.ghosts[3], 1)]

		# draw score
		self.score_text = self.canvas.create_text(self.cv_width, 0, fill='white', text=str(self.gc.score), anchor='ne')

		self.running = False
		self.a_cycle = 0
		self.codew = 0

	def keypress(self, event):
		"""handles keyboard commands/ controls"""
		f_str = 'felicity'
		key = event.keysym
		print(key)
		if key == f_str[self.codew]:
			self.codew += 1
			if f_str[:self.codew] == f_str:
				for coin in np.nditer(self.coins):
					if not np.isnan(coin):
						self.canvas.itemconfig(int(coin), image=self.heart)
				self.codew = 0
		else:
			self.codew = 0
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

		# logic update (runs on scaled down grid)
		if self.a_cycle % (32/self.pacman.speed) == 0:
			self.gc.gameloop()

			for ghost, gc_ghost in zip(self.ghosts, self.gc.ghosts):
				ghost.animate(gc_ghost)
				ghost.teleport(gc_ghost)

			self.pacman.teleport(self.gc.pacman)


		self.pacman.move(self.gc.pacman)
		
		for ghost, gc_ghost in zip(self.ghosts, self.gc.ghosts):
				ghost.move(gc_ghost)

		# coins
		if self.gc.on_coin:
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

	def teleport(self, data):
		vis_pos = np.array(self.canvas.coords(self.char))
		nvp = vis_pos + data.direction * np.array(self.px_size)
		nlp = data.pos * np.array(self.px_size)

		if not np.all(nvp == nlp):
			new = nlp + (np.array(data.direction) * -1 * np.array(self.px_size))
			self.canvas.coords(self.char, new[0], new[1])

	def move(self, data):
		d = data.direction
		self.canvas.move(self.char, d[0]*self.speed, d[1]*self.speed)


class Ghost:
	img_suff = ['nr1', 'nr2', 'nl1', 'nl2', 'nu1', 'nu2', 'nd1', 'nd2']

	def __init__(self, name, canvas, px_size, data, speed, anim_fr='nr1'):
		self.canvas = canvas
		self.px_size = px_size
		self.speed = speed
		self.anim_fr = anim_fr

		self.images = {}
		for suff in self.img_suff:
			self.images[suff] = tk.PhotoImage(file='images/{}-{}.png'.format(name, suff))
		for suff in ['fb1', 'fb2', 'fw1', 'fw2']:
			self.images[suff] = tk.PhotoImage(file='images/ghost-{}.png'.format(suff))

		self.char = self.canvas.create_image(data.pos[0]*self.px_size-self.px_size/2, data.pos[1]*self.px_size-self.px_size/2, image=self.images[self.anim_fr], anchor='nw')

	def animate(self, data):
		img_name = ''
		d = data.direction
		dirs = {(0, 0): 'r', (1, 0): 'r', (-1, 0): 'l', (0, 1): 'd', (0, -1): 'u'}
		state = data.state

		if state == 'chase' or state == 'scatter':
			img_name += 'n'
			img_name += dirs[tuple(d)]
			if self.anim_fr[2] == '1':
				img_name += '2'
			else:
				img_name += '1'
			self.anim_fr = img_name

		elif state == 'frightened':
			img_name += 'f'
			if self.anim_fr == 'fb1':
				self.anim_fr = 'fb2'
			elif self.anim_fr == 'fb2':
				self.anim_fr = 'fw1'
			elif self.anim_fr == 'fw1':
				self.anim_fr = 'fw2'
			else:
				self.anim_fr = 'fb1'

		self.canvas.itemconfig(self.char, image=self.images[self.anim_fr])

	def teleport(self, data):
		vis_pos = np.array(self.canvas.coords(self.char))
		nvp = vis_pos + data.direction * np.array(self.px_size)
		nlp = data.pos * np.array(self.px_size) - 16

		if not np.all(nvp == nlp):
			new = nlp + (np.array(data.direction) * -1 * np.array(self.px_size))
			self.canvas.coords(self.char, new[0], new[1])

	def move(self, data):
		d = data.direction
		self.canvas.move(self.char, d[0]*self.speed, d[1]*self.speed)


class Pacman(MovingObject):
	img_loc = 'images/pacman.png'

	def __init__(self, canvas, data, px_size=32, speed=1):
		self.canvas = canvas
		self.px_size = px_size
		self.speed = speed

		self.image = tk.PhotoImage(file=self.img_loc)

		self.char = self.canvas.create_image(data.pos[0]*self.px_size-self.px_size/2, data.pos[1]*self.px_size-self.px_size/2, image=self.image, anchor='nw')

	def teleport(self, data):
		vis_pos = np.array(self.canvas.coords(self.char))
		nvp = vis_pos + data.direction * np.array(self.px_size)
		nlp = data.pos * np.array(self.px_size) - 16

		if not np.all(nvp == nlp):
			new = nlp + (np.array(data.direction) * -1 * np.array(self.px_size))
			self.canvas.coords(self.char, new[0], new[1])

	def move(self, data):
		d = data.direction
		self.canvas.move(self.char, d[0]*self.speed, d[1]*self.speed)


def onClose():
	root.destroy()


def main():
	xc_dir, _ = os.path.split(sys.argv[0])  # get file path
	if xc_dir:
		os.chdir(xc_dir)  # set current directory

	global root
	root = tk.Tk(className='Pacman')  # sets window name
	root.resizable(False, False)

	root.protocol("WM_DELETE_WINDOW", onClose)

	game_canvas = GameCanvas(root, 'level1')

	root.after(0, game_canvas.start)
	root.mainloop()


if __name__ == '__main__':
	main()
