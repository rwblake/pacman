import numpy as np
import ghosts


class GameController:
	coin_value = 1

	def __init__(self, px, py, pd, lname):
		self.pacman = Pacman(px, py, pd)
		self.level = Level(lname)
		self.blinky = ghosts.Blinky(np.array([1, 1]))
		self.inky = ghosts.Inky(np.array([1, 1]))
		self.pinky = ghosts.Pinky(np.array([1, 1]))
		self.clive = ghosts.Clive(np.array([1, 1]))

		self.score = 0
		self.chase = True

	def gameloop(self):
		self.move_pacman()

		graph = np.swapaxes(self.level.walls, 0, 1)
		pac_pos = self.pacman.pos
		pac_dir = np.array(self.pacman.direction)
		bli_pos = self.blinky.pos
		self.blinky.update(pac_pos, pac_dir, bli_pos, graph)
		self.inky.update(pac_pos, pac_dir, bli_pos, graph)
		self.pinky.update(pac_pos, pac_dir, bli_pos, graph)
		self.clive.update(pac_pos, pac_dir, bli_pos, graph)

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
		elif key == 'space':  # swap
			self.chase = not self.chase
			print(self.chase)
			if self.chase:
				self.blinky.new_state('scatter')
				self.inky.new_state('scatter')
				self.pinky.new_state('scatter')
				self.clive.new_state('scatter')
			else:
				self.blinky.new_state('chase')
				self.inky.new_state('chase')
				self.pinky.new_state('chase')
				self.clive.new_state('chase')

	def move_pacman(self):
		nd = self.check_movement(self.pacman.pos[0], self.pacman.pos[1], self.pacman.new_direction)
		if nd:
			self.pacman.direction = self.pacman.new_direction
		d = self.check_movement(self.pacman.pos[0], self.pacman.pos[1], self.pacman.direction)
		if d:
			self.pacman.move()
		else:
			self.pacman.direction = (0, 0)

	def check_coin(self):
		x = self.pacman.pos[0]
		y = self.pacman.pos[1]
		coin_bool = self.level.coins[y, x]

		if coin_bool:
			self.level.coins[y, x] = False
			self.score += self.coin_value

		return coin_bool


class Pacman:

	def __init__(self, x, y, direction, speed=1):
		self.pos = np.array([x, y])
		self.direction = direction
		self.speed = speed

		self.new_direction = (0, 0)

	def move(self):
		self.pos[0] += self.direction[0]*self.speed
		self.pos[1] += self.direction[1]*self.speed


class Level:
	"""contains level data"""

	def __init__(self, name):
		self.walls = np.load('{}/walls.npy'.format(name))
		self.coins = np.load('{}/coins.npy'.format(name))
		self.big_coins = np.load('{}/big_coins.npy'.format(name))
