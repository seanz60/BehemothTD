import pygame as pg
from enemy import Enemy
from world import World
import constants as c
from behemoth import Turret
from button import Button
from shop import Shop
from shop import Outcome
from turret_data import GUN_DATA
from turret_data import CLAW_DATA
from turret_data import CASH_DATA

#initialize pygame
pg.init()

#create clock
clock = pg.time.Clock()

#create game window
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defence")

#game variables
speed_last_activated = pg.time.get_ticks()
level_started = False
placing_gun = False
placing_claw = False
placing_cash = False
selected_turret = None
game_over = False
speed_activated = False
tier = 0
game_outcome = 0 #-1 is loss and 1 and win
last_enemy_spawn = pg.time.get_ticks()

#load images
#enemies
enemy_images = {
	"weak": pg.transform.scale(pg.image.load('assets/images/enemies/enemy_1.png').convert_alpha(), (c.TILE_SIZE, c.TILE_SIZE)),
	"medium": pg.transform.scale(pg.image.load('assets/images/enemies/enemy_2.png').convert_alpha(), (c.TILE_SIZE, c.TILE_SIZE)),
	"strong": pg.transform.scale(pg.image.load('assets/images/enemies/enemy_3.png').convert_alpha(), (c.TILE_SIZE, c.TILE_SIZE)),
	"elite": pg.transform.scale(pg.image.load('assets/images/enemies/enemy_4.png').convert_alpha(), (c.TILE_SIZE, c.TILE_SIZE))
}
#map
map_image = pg.image.load('levels/level.png').convert_alpha()
map_image = pg.transform.scale(map_image, (c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
#individual turret for mouse cursor
cursor_turret = pg.image.load('assets/images/turrets/behemoth_gun.png').convert_alpha()
cursor_turret = pg.transform.scale(cursor_turret, (c.TILE_SIZE, c.TILE_SIZE))
claw_cursor_turret = pg.image.load('assets/images/turrets/behemoth_claw.png').convert_alpha()
claw_cursor_turret = pg.transform.scale(claw_cursor_turret, (c.TILE_SIZE, c.TILE_SIZE))
cash_cursor_turret = pg.image.load('assets/images/turrets/behemoth_cash.png').convert_alpha()
cash_cursor_turret = pg.transform.scale(cash_cursor_turret, (c.TILE_SIZE, c.TILE_SIZE))
#turret spritesheets
turret_sheet = pg.image.load('assets/images/turrets/behemoth_gun_sheet.png').convert_alpha()
chandelier_sheet = pg.image.load('assets/images/turrets/behemoth_gun_chandelier_spritesheet.png').convert_alpha()
claw_sheet = pg.image.load('assets/images/turrets/behemoth_claw_sheet.png').convert_alpha()
cash_sheet1 = pg.image.load('assets/images/turrets/behemoth_cash_1_sheet.png').convert_alpha()
cash_sheet2 = pg.image.load('assets/images/turrets/behemoth_cash_2_sheet.png').convert_alpha()
cash_sheet3 = pg.image.load('assets/images/turrets/behemoth_cash_3_sheet.png').convert_alpha()
cash_sheet4 = pg.image.load('assets/images/turrets/behemoth_cash_4_sheet.png').convert_alpha()
gun_sheets = []
gun_sheets.append(turret_sheet)
gun_sheets.append(turret_sheet)
gun_sheets.append(turret_sheet)
gun_sheets.append(chandelier_sheet)
claw_sheets = []
claw_sheets.append(claw_sheet)
claw_sheets.append(claw_sheet)
claw_sheets.append(claw_sheet)
claw_sheets.append(claw_sheet)
cash_sheets = []
cash_sheets.append(cash_sheet1)
cash_sheets.append(cash_sheet2)
cash_sheets.append(cash_sheet3)
cash_sheets.append(cash_sheet4)
#menu
shop_menu = pg.image.load('assets/images/gui/shop_menu.png').convert_alpha()
#buttons
buy_gun_image = pg.image.load('assets/images/buttons/buy_gun.png').convert_alpha()
buy_claw_image = pg.image.load('assets/images/buttons/buy_claw.png').convert_alpha()
buy_cash_image = pg.image.load('assets/images/buttons/buy_cash.png').convert_alpha()
cancel_image = pg.image.load('assets/images/buttons/cancel.png').convert_alpha()
upgrade_image = pg.image.load('assets/images/buttons/upgrade.png').convert_alpha()
begin_image = pg.image.load('assets/images/buttons/start.png').convert_alpha()
lost_image = pg.image.load('assets/images/gui/lost.png').convert_alpha()
win_image = pg.image.load('assets/images/gui/win.png').convert_alpha()
restart_image = pg.image.load('assets/images/buttons/restart.png').convert_alpha()
fast_forward_unpressed_image = pg.image.load('assets/images/buttons/fast_forward_unpressed.png').convert_alpha()
fast_forward_pressed_image = pg.image.load('assets/images/buttons/fast_forward_pressed.png').convert_alpha()

#load fonts for displaying text
text_font = pg.font.SysFont("Consolas", 24, bold = True)
large_font = pg.font.SysFont("Consolas", 36)

#function for outputting text on screen
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def create_turret(mouse_pos):
	mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
	mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
	#check if there isn't already a turret there
	space_is_free = True
	for turret in turret_group:
		if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
			space_is_free = False
	#if it is a free space then create turret
	if space_is_free == True:
		if placing_gun == True:
			new_turret = Turret(gun_sheets, mouse_tile_x, mouse_tile_y, GUN_DATA)
		elif placing_claw == True:
			new_turret = Turret(claw_sheets, mouse_tile_x, mouse_tile_y, CLAW_DATA)
		elif placing_cash == True:
			new_turret = Turret(cash_sheets, mouse_tile_x, mouse_tile_y, CASH_DATA)
		turret_group.add(new_turret)
		#deduct cost
		if placing_gun == True:
			world.money -= c.BUY_GUN_COST
		elif placing_claw == True:
			world.money -= c.BUY_CLAW_COST
		elif placing_cash == True:
			world.money -= c.BUY_CASH_COST

def select_turret(mouse_pos):
	mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
	mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
	for turret in turret_group:
		if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
			return turret

def clear_selection():
	for turret in turret_group:
		turret.selected = False

def reset_level():
		for turret in turret_group:
			world.money += turret.cash
		#reset enemy vars
		world.enemy_list = []
		world.spawned_enemies = 0
		world.killed_enemies = 0
		world.missed_enemies = 0

#create World
world = World(map_image)
world.process_enemies()

#create shop menu
shop = Shop(shop_menu)

#create outcome image
lost = Outcome(lost_image)
win = Outcome(win_image)

#create groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()

waypoints = [
(405 * c.SCREEN_WIDTH // 500, 0 * c.SCREEN_HEIGHT // 500),
(405 * c.SCREEN_WIDTH // 500, 80 * c.SCREEN_HEIGHT // 500),
(190 * c.SCREEN_WIDTH // 500, 80 * c.SCREEN_HEIGHT // 500),
(190 * c.SCREEN_WIDTH // 500, 175 * c.SCREEN_HEIGHT // 500),
(402 * c.SCREEN_WIDTH // 500, 175 * c.SCREEN_HEIGHT // 500),
(402 * c.SCREEN_WIDTH // 500, 268 * c.SCREEN_HEIGHT // 500),
(190 * c.SCREEN_WIDTH // 500, 268 * c.SCREEN_HEIGHT // 500),
(190 * c.SCREEN_WIDTH // 500, 362 * c.SCREEN_HEIGHT // 500),
(427 * c.SCREEN_WIDTH // 500, 362 * c.SCREEN_HEIGHT // 500),
(427 * c.SCREEN_WIDTH // 500, 457 * c.SCREEN_HEIGHT // 500),
(85 * c.SCREEN_WIDTH // 500, 457 * c.SCREEN_HEIGHT // 500),
(85 * c.SCREEN_WIDTH // 500, 0 * c.SCREEN_HEIGHT // 500)]

#create buttons
turret_button = Button(c.SCREEN_WIDTH + 30, 120, buy_gun_image, True)
claw_button = Button(c.SCREEN_WIDTH + 250, 120, buy_claw_image, True)
cash_button = Button(c.SCREEN_WIDTH + 140, 300, buy_cash_image, True)
cancel_button = Button(c.SCREEN_WIDTH + 30, 580, cancel_image, True)
upgrade_button = Button(c.SCREEN_WIDTH + 55, 480, upgrade_image, True)
begin_button = Button(c.SCREEN_WIDTH - 213, 20, begin_image, True)
restart_button = Button(250, 300, restart_image, True)
fast_forward_button = Button(c.SCREEN_WIDTH - 90, 660, fast_forward_unpressed_image, True)

#game loop
run = True
while run:

	clock.tick(c.FPS)
	#################################################
	# UPDATING SECT
	#################################################

	if game_over == False:
		#check if player has lost
		if world.health <= 0:
			game_over = True
			game_outcome = -1
		#check if player has won
		if world.level > c.TOTAL_LEVELS:
			game_over = True
			game_outcome = 1
		#update groups
		enemy_group.update(world)
		turret_group.update(enemy_group, world)

		#highlight selected turret
		if selected_turret:
			selected_turret.selected = True

	#################################################
	# DRAWING SECT
	#################################################
	screen.fill("grey10")

	#draw level
	world.draw(screen)

	#draw groups
	enemy_group.draw(screen)
	for turret in turret_group:
		turret.draw(screen)

	#draw shop menu
	shop.draw(screen)

	draw_text("HEALTH: " + str(world.health), text_font, "grey100", 15, 15)
	draw_text("MONEY: " + str(world.money), text_font, "grey100", 15, 45)
	draw_text("LEVEL: " + str(world.level), text_font, "grey100", 15, 75)

	if game_over == False:
		draw_text("COST: " + str(c.BUY_GUN_COST), text_font, "grey100", c.SCREEN_WIDTH + 30, 90)
		draw_text("COST: " + str(c.BUY_CLAW_COST), text_font, "grey100", c.SCREEN_WIDTH + 250, 90)
		draw_text("COST: " + str(c.BUY_CASH_COST), text_font, "grey100", c.SCREEN_WIDTH + 140, 270)
		#check if level has started
		if level_started == False:
			if begin_button.draw(screen):
				level_started = True
		else:
			#fast forward option
			if fast_forward_button.draw(screen):
				if speed_activated and pg.time.get_ticks() - speed_last_activated > 30:
					world.game_speed = 1
					fast_forward_button =  Button(c.SCREEN_WIDTH - 90, 660, fast_forward_unpressed_image, True)
					speed_activated = False
					speed_last_activated = pg.time.get_ticks()
					
				elif speed_activated == False and pg.time.get_ticks() - speed_last_activated > 30:
					world.game_speed = 2
					fast_forward_button =  Button(c.SCREEN_WIDTH - 90, 660, fast_forward_pressed_image, True)
					speed_activated = True
					speed_last_activated = pg.time.get_ticks()
			
			#check waves for difficulty progression
			if world.level == 50:
				tier = 10
			elif world.level >= 45:
				tier = 9
			elif world.level >= 40:
				tier = 8
			elif world.level >= 35:
				tier = 7
			elif world.level >= 30:
				tier = 6
			elif world.level >= 25:
				tier = 5
			elif world.level >= 20:
				tier = 4
			elif world.level >= 15:
				tier = 3
			elif world.level >= 10:
				tier = 2
			elif world.level >= 5:
				tier = 1
			else:
				tier = 0
			#spawn enemies
			if pg.time.get_ticks() - last_enemy_spawn > (c.SPAWN_COOLDOWN / world.game_speed):
				if world.spawned_enemies < len(world.enemy_list):
					enemy_type = world.enemy_list[world.spawned_enemies]
					world.spawned_enemies += 1
					enemy = Enemy(enemy_type, waypoints, enemy_images, tier)
					enemy_group.add(enemy)
					last_enemy_spawn = pg.time.get_ticks()

		#check if wave is finished
		if world.check_level_complete():
			world.money += c.LEVEL_COMPLETE_REWARD
			level_started = False
			world.level += 1
			last_enemy_spawn = pg.time.get_ticks()
			reset_level()
			world.process_enemies()

		#draw buttons
		#buttons for placing turrets
		if turret_button.draw(screen):
			placing_gun = True
		elif claw_button.draw(screen):
			placing_claw = True
		elif cash_button.draw(screen):
			placing_cash = True

		if placing_gun == True:
			cursor_rect = cursor_turret.get_rect()
			cursor_pos = pg.mouse.get_pos()
			cursor_rect.center = cursor_pos
			if cursor_pos[0] <= c.SCREEN_WIDTH:
				screen.blit(cursor_turret, cursor_rect)
			if cancel_button.draw(screen):
				placing_gun = False
				placing_claw = False
				placing_cash = False

		if placing_claw == True:
			cursor_rect = claw_cursor_turret.get_rect()
			cursor_pos = pg.mouse.get_pos()
			cursor_rect.center = cursor_pos
			if cursor_pos[0] <= c.SCREEN_WIDTH:
				screen.blit(claw_cursor_turret, cursor_rect)
			if cancel_button.draw(screen):
				placing_gun = False
				placing_claw = False
				placing_cash = False

		if placing_cash == True:
			cursor_rect = cash_cursor_turret.get_rect()
			cursor_pos = pg.mouse.get_pos()
			cursor_rect.center = cursor_pos
			if cursor_pos[0] <= c.SCREEN_WIDTH:
				screen.blit(cash_cursor_turret, cursor_rect)
			if cancel_button.draw(screen):
				placing_gun = False
				placing_claw = False
				placing_cash = False

		#show upgrade button if turret is selected
		if selected_turret:
			if selected_turret.upgrade_level < c.TURRET_LEVELS:
				draw_text("COST: " + str(selected_turret.turret_type[selected_turret.upgrade_level].get("upgrade")), text_font, "grey100", c.SCREEN_WIDTH + 55, 450)
			if selected_turret.upgrade_level < c.TURRET_LEVELS:
				if upgrade_button.draw(screen):
					if world.money >= selected_turret.turret_type[selected_turret.upgrade_level].get("upgrade"):
						selected_turret.upgrade()
						world.money -= selected_turret.upgrade_cost
	else:
		world.money = 0
		if game_outcome == -1:
			lost.draw(screen)
		elif game_outcome == 1:
			win.draw(screen)
		#restart level
		if restart_button.draw(screen):
			game_over = False
			level_started = False
			placing_turrets = False
			selected_turret = None
			speed_activated = False
			fast_forward_button =  Button(c.SCREEN_WIDTH - 90, 660, fast_forward_unpressed_image, True)
			speed_last_activated = pg.time.get_ticks()
			last_enemy_spawn = pg.time.get_ticks()
			world = World(map_image)
			world.process_enemies()
			world.game_speed = 1
			tier = 0
			#empty groups
			enemy_group.empty()
			turret_group.empty()

	#event handler
	for event in pg.event.get():
		#quit program
		if event.type == pg.QUIT:
			run = False
		#mouse click
		if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
			mouse_pos = pg.mouse.get_pos()
			#check if mouse is on the game area
			if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT and not(mouse_pos[0] > 151 and mouse_pos[0] < 201 and not(mouse_pos[1] > 701)) and not(mouse_pos[1] > 651 and mouse_pos[1] < 701 and not(mouse_pos[0] < 151 or mouse_pos[0] > 900)) and not(mouse_pos[0] > 801 and mouse_pos[0] < 901 and not(mouse_pos[1] > 701 or mouse_pos[1] < 501)) and not(mouse_pos[1] > 501 and mouse_pos[1] < 551 and not(mouse_pos[0] > 851 or mouse_pos[0] < 401)) and not(mouse_pos[0] > 351 and mouse_pos[0] < 401 and not(mouse_pos[1] > 551 or mouse_pos[1] < 351)) and not(mouse_pos[1] > 351 and mouse_pos[1] < 401 and not(mouse_pos[0] > 851 or mouse_pos[0] < 351)) and not(mouse_pos[0] > 751 and mouse_pos[0] < 851 and not(mouse_pos[1] > 401 or mouse_pos[1] < 251)) and not(mouse_pos[1] > 201 and mouse_pos[1] < 301 and not(mouse_pos[0] > 851 or mouse_pos[0] < 401)) and not(mouse_pos[1] < 151 and mouse_pos[1] > 101 and not(mouse_pos[0] > 851 or mouse_pos[0] < 351)) and not(mouse_pos[1] > 101 and mouse_pos[1] < 151 and not(mouse_pos[0] > 401 or mouse_pos[0] < 351)) and not(mouse_pos[0] > 351 and mouse_pos[0] < 401 and not(mouse_pos[1] < 101 or mouse_pos[1] > 301)) and not(mouse_pos[0] < 851 and mouse_pos[0] > 751 and not(mouse_pos[1] > 151)):
				#clear selected turrets
				selected_Turret = None
				clear_selection()
				if placing_gun == True:
					#check if enough money
					if world.money >= c.BUY_GUN_COST:
						create_turret(mouse_pos)
						selected_turret = None
				if placing_claw == True:
					if world.money >= c.BUY_CLAW_COST:
						create_turret(mouse_pos)
						selected_turret = None
				if placing_cash == True:
					if world.money >= c.BUY_CASH_COST:
						create_turret(mouse_pos)
						selected_turret = None
				else:
					selected_turret = select_turret(mouse_pos)
	#update display
	pg.display.flip()

pg.quit()