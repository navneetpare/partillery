# https://stackoverflow.com/questions/12787650/finding-the-index-of-n-biggest-elements-in-python-array-list-efficiently?noredirect=1&lq=1
# https://towardsdatascience.com/the-little-known-ogrid-function-in-numpy-19ead3bdae40
# https://stackoverflow.com/questions/44865023/how-can-i-create-a-circular-mask-for-a-numpy-array

import os
from time import sleep
import pygame
import math
from numpy import ogrid
from numpy import sqrt

from partillery.old.player_old import Player

# Library Initialization
pygame.init()
clock = pygame.time.Clock()

# Game Modes

MODE_SELECTION = "Selection"
MODE_FLIGHT = "Flight"
MODE_TEST = "Test"
mode = MODE_SELECTION

# Colors

col_black = 0, 0, 0
col_text = 200, 200, 200
col_screen = 10, 10, 10
col_grey = 25, 25, 25
col_night = 10, 10, 10
col_terrain = 0, 130, 50
col_day = 207, 245, 254
col_eve = 0, 30, 70

# Dimensions

full_w = 1280
full_h = 720
play_w = full_w
play_h = int(full_h * 0.8)
play_left = (full_w - play_w) / 2
play_right = play_left + play_w
# play_top = (full_h - play_h) / 2
play_top = 0
play_bottom = play_top + play_h
terrain_h = round(play_h * 0.2)
control_h = full_h - play_h
control_scale = 15  # for my ctrl images; set from tests
tank_h = 16
tank_w = 32
tank_x = play_left
tank_y = play_top + play_h - tank_h - terrain_h
ammo_h = 4

# Players

player1 = Player()
player2 = Player()
player1.angle = 60
player1.power = 50
player2.angle = 120
player2.power = 50
player = player1
enemy = player2

# Ammo physics

g = 500
speed_base = 1000

# ------------------------------------------------------------ #


# Initialize Display Elements

pygame.display.set_caption("Partillery")
# pygame.display.set_icon(pygame.image.load("resources/images/window_icon.png"))
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100, 40)
screen = pygame.display.set_mode((full_w, full_h), pygame.RESIZABLE)
screen.fill(col_screen)
play_img = pygame.image.load("../partillery/resources/images/nighthd_starry_blue.png").convert_alpha()
playsurf = pygame.transform.scale(play_img, (play_w, play_h))
playsurfbk = playsurf.copy()
playsurf_rect = playsurf.get_rect()
playsurf_rect.x = play_left
playsurf_rect.y = play_top
screen.blit(playsurf, (play_left, play_top))
pygame.draw.rect(screen, (100,100,100), (0, play_h/2, play_w, play_h/2))
pygame.display.update()

# ---------------------  ENTER GAME  --------------------- #
t = 0
t0 = pygame.time.get_ticks()
print("t0 = " + str(t0))

center = int(play_w / 2), int(play_h / 2)
exp_dia =100 # pixels

# Getting a circular mask for the explosion
exp_rect = pygame.Rect(0,0, exp_dia, exp_dia)
exp_rect.center = center
exp_bg = playsurf.subsurface(exp_rect).copy()
exp_bg_array = pygame.surfarray.pixels_alpha(exp_bg)  # use direct reference to surface pixel alphas instead of copy
x,y = ogrid[:exp_dia,:exp_dia]
c1 = exp_dia/2, exp_dia/2
d = sqrt((x - c1[0])**2 + (y-c1[1])**2)
exp_mask = d < (exp_dia / 2)
exp_bg_array[~exp_mask] = 0
del exp_bg_array
pygame.display.update()
speed = 0.5

while speed*t < exp_dia/2:  # milliseconds
    speed = 0.2 # pixels per 1000 ms

    for i in range(1, int(speed * t)):
        pygame.draw.circle(screen, (255, 150, 0, int(255 * math.pow(i % 10, 2) / 225)), center, i, 1)

    pygame.display.update()
    t = pygame.time.get_ticks() - t0
    print("t = " + str(t))

    clock.tick(60)

screen.blit(exp_bg, exp_rect)
pygame.display.update()
print("clean")
'''t0 = t
while t <= 2000:  # milliseconds
    speed = 0.2  # pixels per 1000 ms

    for i in range(1, int(speed * (t-1000))):
        pygame.draw.circle(screen, (0, 0, 0, 255), center, i, 1)

    pygame.display.update()
    t = pygame.time.get_ticks() - t0
    print("t = " + str(t))

    clock.tick(60)
'''
while True:
    sleep(5)
# this creates a fuzzy fireball that clarifies with time
# pygame.draw.circle(playsurf, (255, 150, 0, int(255 * t / 2500)), center, i, 1)

# this creates a striped growing explosion - cosine
# pygame.draw.circle(playsurf, (255, 150, 0, int(255 * (1 + math.cos(i/3)) / 2)), center, i, 1)

# weid buzzy fireball
# pygame.draw.circle(playsurf, (255, 150, 0, int(t % i)), center, i, 1)