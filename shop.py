import pygame as pg
import constants as c

class Shop():
	def __init__(self, image):
		self.image = image

	def draw(self, surface):
		surface.blit(self.image, (c.SCREEN_WIDTH, 0))

class Outcome():
	def __init__(self, image):
		self.image = image

	def draw(self, surface):
		surface.blit(self.image, (250, 150))
