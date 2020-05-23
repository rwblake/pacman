import numpy as np
import random
import ghosts


class GameController:
	coin_value = 10
	big_coin_value = 100

	def __init__(self, px, py, pd, lname):
		self.pacman = Pacman(px, py, pd)
		self.level = Level(lname)

		self.ghosts = [ghosts.Blinky(np.array([1, 1])), ghosts.Inky(np.array([1, 1])), ghosts.Pinky(np.array([1, 1])), ghosts.Clive(np.array([1, 1]))]

		self.portals = {(28, 14): (0, 14), (-1, 14): (27, 14)}

		self.score = 0
		self.chase = True
		self.on_coin = False  # either false or 1 or 2: small/ big coin
		self.state_swap = False  # counts down

		self.clock = 0

	def gameloop(self):
		self.state_swap -= 1
		if self.state_swap == 0:
			self.state_swap = False
			for ghost in self.ghosts:
				if ghost.state != 'eaten':
					ghost.speed = 1
					ghost.new_state('scatter')

		a = random.randint(0, 90)
		if not a:
			for ghost in self.ghosts:
				if ghost.state == 'scatter':
					ghost.new_state('chase')
				elif ghost.state == 'chase':
					ghost.new_state('scatter')

		self.move_pacman(self.level.portals)

		graph = np.swapaxes(self.level.walls, 0, 1)
		pac_pos = self.pacman.pos
		pac_dir = np.array(self.pacman.direction)
		bli_pos = self.ghosts[0].pos

		for ghost in self.ghosts:
			if self.clock % (1/ghost.speed) == 0:
				ghost.update(pac_pos, pac_dir, bli_pos, graph, self.level.portals)

		self.collision()

		self.check_coin()

		self.clock += 1

	def check_movement(self, x, y, direction):
		"""find if wall is in way of path or not"""
		new_x = x + direction[0]
		new_y = y + direction[1]

		try:
			wall_present = self.level.walls[new_y, new_x]
		except:
			return True
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
			if self.chase:
				for ghost in self.ghosts:
					ghost.new_state('scatter')
			else:
				for ghost in self.ghosts:
					ghost.new_state('chase')

	def move_pacman(self, portals):
		nd = self.check_movement(self.pacman.pos[0], self.pacman.pos[1], self.pacman.new_direction)
		if nd:
			self.pacman.direction = self.pacman.new_direction
		d = self.check_movement(self.pacman.pos[0], self.pacman.pos[1], self.pacman.direction)
		if d:
			self.pacman.move()
		else:
			self.pacman.direction = (0, 0)

		# portal teleporting
		p = tuple(self.pacman.pos)
		if p in portals:
			new_pos = portals[p]
			self.pacman.pos = np.array(new_pos)

	def check_coin(self):
		x = self.pacman.pos[0]
		y = self.pacman.pos[1]

		if self.level.coins[y, x]:
			self.level.coins[y, x] = False
			self.score += self.coin_value
			self.on_coin = 1
		elif self.level.big_coins[y, x]:
			self.level.big_coins[y, x] = False
			self.score += self.big_coin_value
			self.on_coin = 2
			for ghost in self.ghosts:
				ghost.new_state('frightened')
				ghost.speed = 0.5
			self.state_swap = 40
		else:
			self.on_coin = False

	def collision(self):
		prev_pp = self.pacman.pos - self.pacman.direction
		for ghost in self.ghosts:
			prev_gp = ghost.pos - ghost.direction
			if np.array_equal(ghost.pos, self.pacman.pos) or np.array_equal(ghost.pos, prev_pp) or np.array_equal(prev_gp, self.pacman.pos):
				if ghost.state == 'frightened':
					ghost.state = 'eaten'
					ghost.speed = 1
					self.score += 200
				elif ghost.state != 'eaten':
					# kill pacman
					pass


class Pacman:

	def __init__(self, x, y, direction, speed=1):
		self.pos = np.array([x, y])
		self.direction = direction
		self.speed = speed

		self.new_direction = (0, 0)

	def move(self):
		self.pos[0] += self.direction[0]
		self.pos[1] += self.direction[1]


class Level:
	"""contains level data"""

	def __init__(self, name):
		self.walls = np.load('{}/walls.npy'.format(name))
		self.coins = np.load('{}/coins.npy'.format(name))
		self.big_coins = np.load('{}/big_coins.npy'.format(name))
		self.portals = {(27, 14): (0, 14), (0, 14): (27, 14)}
