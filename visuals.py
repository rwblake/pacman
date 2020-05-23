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
	update_ms = 4  # 4 is best

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
		p = self.gc.pacman
		self.pacman = Pacman(self.canvas, p.pos*self.px_size, p.direction)

		# create and draw ghosts
		self.ghosts = []
		for g, name in zip(self.gc.ghosts, ['blinky', 'inky', 'pinky', 'clive']):
			self.ghosts.append(Ghost(self.canvas, g.pos*self.px_size, g.direction, g.state, name))

		# draw score
		self.score_text = self.canvas.create_text(self.cv_width, 0, fill='white', text=str(self.gc.score), anchor='ne')

		self.pop_up_img = tk.PhotoImage('/images/200.png')

		self.running = False
		self.a_cycle = 0
		self.codew = 0
		self.paused = False

	def keypress(self, event):
		"""handles keyboard commands/ controls"""

		f_str = 'felicity'
		key = event.keysym
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
		self.paused = False
		self.master.bind('<Key>', self.keypress)
		self.gameloop()

	def stop(self):
		"""closes main game loop"""

		self.master.unbind('<Key>')
		self.running = False

	def gameloop(self):
		"""main loop for game functions"""

		# logic update (runs on scaled down grid)
		if self.a_cycle % self.px_size == 0:
			self.gc.gameloop()

			self.pacman.next_pos = self.gc.pacman.pos * self.px_size
			self.pacman.logic_direction = self.gc.pacman.direction
			self.pacman.animate()

			for ghost, gc_ghost in zip(self.ghosts, self.gc.ghosts):
				ghost.state = gc_ghost.state
				ghost.speed = gc_ghost.speed
				ghost.logic_direction = gc_ghost.direction
				ghost.next_pos = gc_ghost.pos * self.px_size
				ghost.animate()
		
		# move entitites
		self.pacman.move()
		for ghost in self.ghosts:
			ghost.move()

		# coins
		if self.gc.on_coin:
			self.canvas.delete(int(self.coins[tuple(self.gc.pacman.pos)]))

		# update score text
		self.canvas.itemconfig(self.score_text, text=str(self.gc.score))

		# increment game clock
		self.a_cycle += 1

		if self.paused:
			pass
		elif not self.running:
			self.stop()
		else:
			self.master.after(self.update_ms, self.gameloop)


class Entity:
	"""class for pictures on screen"""

	def __init__(self, canvas, pos, image, offset=np.array([0, 0])):
		"""initiates variables"""

		self.canvas = canvas
		self.offset = offset

		self.char = self.canvas.create_image(pos[0]+self.offset[0], pos[1]+self.offset[1], image=image, anchor='nw')

		self.pos = pos
		self.image = image

	@property
	def pos(self):
		return np.array(self.canvas.coords(self.char)) - self.offset

	@pos.setter
	def pos(self, pos):
		pos = pos + self.offset
		self.canvas.coords(self.char, pos[0], pos[1])

	@property
	def image(self):
		return self.__image

	@image.setter
	def image(self, image):
		self.canvas.itemconfig(self.char, image=image)
		self.__image = image


class MovingEntity(Entity):
	"""class for moving pictures on screen"""

	def __init__(self, canvas, pos, image, l_d,speed=1, offset=np.array([0, 0]), next_pos=None):
		"""initiates variables"""

		super().__init__(canvas, pos, image, offset)
		self.speed = speed
		self.direction = l_d
		self.next_pos = next_pos
		self.logic_direction = l_d

	def move(self):
		"""move object slowly towards target position"""

		target_v = self.next_pos - self.pos
		for c, v in enumerate(target_v):
			if abs(v) > 32:
				self.teleport()
				return
			if v == 0:
				target_v[c] = 0
			elif v < 0:
				target_v[c] = -1
			else:
				target_v[c] = 1
		self.direction = target_v
		self.canvas.move(self.char, self.direction[0]*self.speed, self.direction[1]*self.speed)

	def teleport(self):
		"""move object to new position far away"""

		self.pos = self.next_pos - self.logic_direction * np.array([32])


class Ghost(MovingEntity):
	"""ghost entity class from movingentity"""

	offset = np.array([-16, -16])

	def __init__(self, canvas, pos, l_d, state, name, speed=1, anim_fr='nr1'):
		"""initiate variables and images"""

		self.state = state
		self.name = name
		self.anim_fr = anim_fr

		self.images = {}
		for suff in ['nr1', 'nr2', 'nl1', 'nl2', 'nu1', 'nu2', 'nd1', 'nd2']:
			self.images[suff] = tk.PhotoImage(file='images/{}-{}.png'.format(name, suff))
		for suff in ['fb1', 'fb2', 'fw1', 'fw2', 'er', 'el', 'eu', 'ed']:
			self.images[suff] = tk.PhotoImage(file='images/ghost-{}.png'.format(suff))

		super().__init__(canvas, pos, self.images[anim_fr], l_d, speed=speed, offset=self.offset)

	def animate(self):
		"""change image"""

		img_name = ''

		if self.state == 'chase' or self.state == 'scatter':
			dirs = {(0, 0): 'r', (1, 0): 'r', (-1, 0): 'l', (0, 1): 'd', (0, -1): 'u'}
			img_name += 'n'
			img_name += dirs[tuple(self.logic_direction)]
			if len(self.anim_fr) > 2 and self.anim_fr[2] == '1':
				img_name += '2'
			else:
				img_name += '1'

		elif self.state == 'frightened':
			suffs = {'fb1': 'fb2', 'fb2': 'fw1', 'fw1': 'fw2'}
			if self.anim_fr in suffs:
				img_name = suffs[self.anim_fr]
			else:
				img_name = 'fb1'

		elif self.state == 'eaten':
			dirs = {(0, 0): 'r', (1, 0): 'r', (-1, 0): 'l', (0, 1): 'd', (0, -1): 'u'}
			img_name += 'e'
			img_name += dirs[tuple(self.logic_direction)]

		self.anim_fr = img_name
		self.image = self.images[self.anim_fr]


class Pacman(MovingEntity):
	"""pacman entity class from movingentity"""

	offset = np.array([-16, -16])

	def __init__(self, canvas, pos, l_d, speed=1, anim_fr='00'):
		"""initiate variables and images"""

		self.anim_fr = anim_fr
		self.images = {}
		for suff in ['r1', 'r2', 'l1', 'l2', 'u1', 'u2', 'd1', 'd2']:
			self.images[suff] = tk.PhotoImage(file='images/pacman-{}.png'.format(suff))
			self.images['00'] = tk.PhotoImage(file='images/pacman.png')
		image = self.images[self.anim_fr]
		super().__init__(canvas, pos, image, l_d, speed=speed, offset=self.offset)

	def animate(self):
		"""update image"""

		if np.all(self.logic_direction == np.array([0, 0])):
			return
		img_name = ''
		dirs = {(0, 0): 'r', (1, 0): 'r', (-1, 0): 'l', (0, 1): 'd', (0, -1): 'u'}
		img_name += dirs[tuple(self.logic_direction)]
		if self.anim_fr[1] == '1':
			img_name += '2'
		else:
			img_name += '1'
		self.anim_fr = img_name
		self.image = self.images[self.anim_fr]


def onClose():
	"""kills mainloop on window close"""

	root.destroy()


def main():
	"""creates pacman game instance"""

	xc_dir, _ = os.path.split(sys.argv[0])  # get file path
	if xc_dir:
		os.chdir(xc_dir)  # set current directory

	global root
	root = tk.Tk(className='Pacman')  # sets window name
	root.resizable(False, False)  # unresizable

	root.protocol("WM_DELETE_WINDOW", onClose)  # close mainloop at end

	game_canvas = GameCanvas(root, 'level1')  # create gamecanvas

	# start
	root.after(0, game_canvas.start)
	root.mainloop()


if __name__ == '__main__':
	main()
