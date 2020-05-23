import numpy as np
import random


class Ghost:

	def __init__(self, pos, scatter_goal, target=np.empty([2,1], dtype=int), state='scatter', eaten_goal=np.array([13, 11]), speed=1):
		self.pos = pos  # position vector
		self.scatter_goal = scatter_goal  # goal in scatter mode
		self.target = target  # goal to move towards
		self.state = state  # chase, scatter, frightened, eaten
		self.direction = np.array([0, 0])  # direction vector
		self.new_direction = np.zeros([2,1], dtype=int)
		self.eaten_goal = eaten_goal
		self.speed = speed

	def flip_dir(self):
		self.new_direction = self.direction * -1

	def chase(self, pac_pos, pac_dir, bli_pos):
		return pac_pos

	def update_target(self, pac_pos, pac_dir, bli_pos):
		if self.state == 'chase':
			self.target = self.chase(pac_pos, pac_dir, bli_pos)
		elif self.state == 'scatter':
			self.target = self.scatter_goal
		elif self.state == 'eaten':
			self.target = self.eaten_goal

	def move(self, walls, portals):
		if np.any(self.new_direction):
			self.direction = self.new_direction
			self.new_direction = np.zeros([2,1], dtype=int)
		cost = []

		for direction in [[0, -1], [-1, 0], [0, 1], [1, 0]]:
			direction = np.array(direction)

			# check for backward direction
			if np.all(direction == self.direction*-1):
				continue

			# check for wall
			tmp = tuple(direction + self.pos)
			try:
				if walls[tmp]:
					continue
			except:
				pass

			new_pos = self.pos + direction
			delta = self.target - new_pos
			new_cost = delta[0]**2 + delta[1]**2
			cost.append([new_cost, direction])

		if self.state == 'frightened':
			new = random.choice(cost)[1]
		else:
			cost.sort(key=lambda x: x[0])
			new = cost[0][1]

		self.direction = new
		self.pos += new

		if self.state == 'eaten' and np.array_equal(self.pos, self.target):
			self.state = 'scatter'

		# portal teleporting
		p = tuple(self.pos)
		if p in portals:
			new_pos = portals[p]
			self.pos = np.array(new_pos)

	def update(self, pac_pos, pac_dir, bli_pos, walls, portals):
		self.update_target(pac_pos, pac_dir, bli_pos)
		self.move(walls, portals)

	def new_state(self, new_state):
		if new_state == 'frightened' or new_state == 'chase':
			self.flip_dir()
		elif new_state == 'scatter' and self.state == 'chase':
			self.flip_dir()
		self.state = new_state


class Blinky(Ghost):
	scatter_goal = np.array([27, 0])

	def __init__(self, pos):
		super().__init__(pos, self.scatter_goal)


class Pinky(Ghost):
	scatter_goal = np.array([0, 0])

	def __init__(self, pos):
		super().__init__(pos, self.scatter_goal)

	def chase(self, pac_pos, pac_dir, bli_pos):
		if np.all(pac_dir == [0, -1]):
			t = np.array(pac_pos[0]-3, pac_pos[1]-4)
		else:
			t = pac_pos + pac_dir*4

		return t


class Inky(Ghost):
	scatter_goal = np.array([27, 30])

	def __init__(self, pos):
		super().__init__(pos, self.scatter_goal)

	def chase(self, pac_pos, pac_dir, bli_pos):
		if np.all(pac_dir == [0, -1]):
			pac_t = np.array(pac_pos[0]-2, pac_pos[1]-2)
		else:
			pac_t = pac_pos + pac_dir*2

		b_v = bli_pos - pac_t
		i_v = pac_t + b_v*-1

		return i_v


class Clive(Ghost):
	scatter_goal = np.array([0, 30])

	def __init__(self, pos):
		super().__init__(pos, self.scatter_goal)

	def chase(self, pac_pos, pac_dir, bli_pos):
		delta = pac_pos - self.pos
		distsq = delta[0]**2 + delta[1]**2
		if distsq < 64:
			t = self.scatter_goal
		else:
			t = pac_pos

		return t
