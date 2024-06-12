import pygame as pg
from waves import ENEMY_SPAWN_DATA
import random
import constants as c

class World():
	def __init__(self, map_image):
		self.image = map_image
		self.level = 1
		self.health = c.HEALTH
		self.money = c.MONEY
		self.enemy_list = []
		self.spawned_enemies = 0
		self.killed_enemies = 0
		self.missed_enemies = 0
		self.game_speed = 1

	def process_enemies(self):
		enemies = ENEMY_SPAWN_DATA[self.level - 1]
		for enemy_type in enemies:
			enemies_to_spawn = enemies[enemy_type]
			for enemy in range(enemies_to_spawn):
				self.enemy_list.append(enemy_type)
		#now randomize enemy_list
		random.shuffle(self.enemy_list)

	def check_level_complete(self):
		if (self.killed_enemies + self.missed_enemies) == len(self.enemy_list):
			return True

	def draw(self, surface):
		surface.blit(self.image, (0, 0))
