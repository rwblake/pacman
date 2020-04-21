import numpy as np


class GameController:

	def __init__(self, px, py, pd, lname):
		self.pacman = Pacman(px, py, pd)
		self.level = Level(lname)

		self.score = 0

	def check_movement(self, x, y, direction):
		"""find if wall is in way of path or not"""
		new_x = x + direction[0]
		new_y = y + direction[1]

		wall_present = self.level.walls[new_y, new_x]
		return not wall_present

	def keypress(self, key):
		if key == 'w' or key == 'Up':  # up
			self.pacman.new_direction = (0, -1)
		elif key == 'a' or key == 'Left':  # left
			self.pacman.new_direction = (-1, 0)
		elif key == 's' or key == 'Down':  # down
			self.pacman.new_direction = (0, 1)
		elif key == 'd' or key == 'Right':  # right
			self.pacman.new_direction = (1, 0)

	def move_pacman(self):
		nd = self.check_movement(self.pacman.x, self.pacman.y, self.pacman.new_direction)
		if nd:
			self.pacman.direction = self.pacman.new_direction
		d = self.check_movement(self.pacman.x, self.pacman.y, self.pacman.direction)
		if d:
			self.pacman.move()
		else:
			self.pacman.direction = (0, 0)


class Pacman:

	def __init__(self, x, y, direction):
		self.x = x
		self.y = y
		self.direction = direction

		self.new_direction = (0, 0)

	def move(self):
		self.x += self.direction[0]
		self.y += self.direction[1]


class Level:
	"""contains level data"""

	def __init__(self, name):
		self.walls = np.load('{}/walls.npy'.format(name))
		self.coins = np.load('{}/coins.npy'.format(name))
		self.big_coins = np.load('{}/big_coins.npy'.format(name))
