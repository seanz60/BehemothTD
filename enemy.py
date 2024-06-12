import pygame as pg
from pygame.math import Vector2
import math
from waves import ENEMY_DATA
import constants as c

class Enemy(pg.sprite.Sprite):
	def __init__(self, enemy_type, waypoints, images, tier):
		pg.sprite.Sprite.__init__(self)
		self.tier = tier
		self.waypoints = waypoints
		self.pos = Vector2(self.waypoints[0])
		self.target_waypoint = 1
		self.speed = ENEMY_DATA[tier].get(enemy_type)["speed"]
		self.health = ENEMY_DATA[tier].get(enemy_type)["health"]
		self.original_image = images.get(enemy_type)
		self.angle = 0
		self.image = pg.transform.rotate(self.original_image, self.angle)
		self.rect = self.image.get_rect()
		self.rect.center = self.pos

	def update(self, world):
		self.move(world)
		self.rotate()
		self.check_alive(world)

	def move(self, world):
		#define a target waypoint
		if self.target_waypoint < len(self.waypoints):
			self.target = Vector2(self.waypoints[self.target_waypoint])
			self.movement = self.target - self.pos
		else:
			#enemy has reached the end of the path
			self.kill()
			if world.health >= self.health:
				world.health -= self.health
			else:
				world.health -= world.health
			world.missed_enemies += 1

		#calculate distance to target
		dist = self.movement.length()
		#check if remaining distance is greater than enemy speed
		if dist >= (self.speed * world.game_speed):
			self.pos += self.movement.normalize() * (self.speed * world.game_speed)
		else:
			if dist != 0 :
				self.pos += self.movement.normalize() * dist
			self.target_waypoint += 1

	def rotate(self):
		#calculate distance to next waypoint
		dist = self.target - self.pos
		#use distance to calculate angle
		self.angle = math.degrees(math.atan2(-dist[1], dist[0])) + 90
		#rotate image and update rectangle
		self.image = pg.transform.rotate(self.original_image, self.angle)
		self.rect = self.image.get_rect()
		self.rect.center = self.pos

	def check_alive(self, world):
		if self.health <= 0:
			self.kill()
			world.killed_enemies += 1
			world.money += c.KILL_REWARD