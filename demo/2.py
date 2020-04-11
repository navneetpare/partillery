"""
Changelog
==========
v0.1
- Got the basic projectile motion figured out.
- Motion curvature is choppy.
  (Retrospectively this is due to reliance on frame refresh to do computations instead of time elapsed.)
v0.2
- Calculating position per real time, instead of moving ammo by frame rate
- Calibrated values of g and base speed
- New flat terrain surface definition
- Detect collision between ammo and terrain and edges
- Ammo and trail to be updated only on play surface
"""

import pygame, sys, math
import time

pygame.init()
clock = pygame.time.Clock()

full_w = 1024
full_h = 768
play_w = 900
play_h = 600
play_left = (full_w - play_w) / 2
play_right = play_left + play_w
play_top = (full_h - play_h) / 2
play_bottom = play_top + play_h
play_centre = (full_w - play_w) / 2, (full_h - play_h) / 2
terrain_h = 150
tank_h = 24
tank_w = 32
tank_x = play_left
tank_y = play_top + play_h - tank_h - terrain_h
ammo1_h = 4
ammo1_w = 4
ammo1_x0 = tank_x + tank_w
ammo1_y0 = tank_y - ammo1_h

# Ammo physics
angle = 85  # will be user selectable
g = 400
speed_base = 800
power = 90  # this will eventually be user selectable power percentage
speed_start = speed_base * power / 100

ammo1_speed_x0 = speed_start * math.cos(math.radians(angle))
ammo1_speed_y0 = -(speed_start * math.sin(math.radians(angle)))

# Colors
col_black = 0, 0, 0
col_night = 10, 10, 10
col_terrain = 0, 130, 50
col_day = 207, 245, 254
col_eve = 0, 30, 70


class Tank(pygame.sprite.Sprite):
    def __init__(self):
        super(Tank, self).__init__
        self.surf = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\tank_right.png")
        self.rect = self.surf.get_rect()
        self.rect.x = tank_x
        self.rect.y = tank_y


class Ammo(pygame.sprite.Sprite):
    def __init__(self):
        super(Ammo, self).__init__
        self.surf = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\ammo_4.gif")
        self.rect = self.surf.get_rect()
        self.rect.x = ammo1_x0
        self.rect.y = ammo1_y0

    def update(self):
        screen.blit(ammo1.surf, (ammo1.rect.x, ammo1.rect.y))


class Terrain(pygame.sprite.Sprite):
    def __init__(self):
        super(Terrain, self).__init__
        self.surf = pygame.Surface((play_w, terrain_h))
        self.rect = self.surf.get_rect()
        self.rect.x = play_left
        self.rect.y = play_bottom - terrain_h
        self.surf.fill(col_terrain)


def erase_trail():
    screen.blit(play_surface, ammo1_rect_old, ammo_background_rect)


tank1 = Tank()
ammo1 = Ammo()
terr = Terrain()

# set_mode(size=(0, 0), flags=0, depth=0, display=0) -> Surface
# screen=pygame.display.set_mode(size=(0,0), flags=pygame.RESIZABLE)
screen = pygame.display.set_mode((full_w, full_h))
screen.fill(col_black)

play_surface = pygame.Surface((play_w, play_h))
play_surface_rect = play_surface.get_rect()
play_surface_rect.x = play_left
play_surface_rect.y = play_top
play_surface.fill(col_night)

#  Draw initial elements
screen.blit(play_surface, play_centre)
screen.blit(terr.surf, (terr.rect.x, terr.rect.y))
screen.blit(tank1.surf, (tank_x, tank_y))
screen.blit(ammo1.surf, (ammo1_x0, ammo1_y0))

# mark a bit of the sky as reference to clear out ammo trail
ammo_background_rect = pygame.Rect(0, 0, ammo1_h, ammo1_w)
pygame.display.update()

# loop flag
running = True

# timer start
t0 = pygame.time.get_ticks()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    # get original ammo location
    ammo1_rect_old = pygame.Rect.copy(ammo1.rect)

    # move the ammo
    t = (pygame.time.get_ticks() - t0) / 1000

    # s = ut + 1/2(gt^2) + x_initial
    ammo1.rect.x = (ammo1_speed_x0 * t) + ammo1_x0
    ammo1.rect.y = ((ammo1_speed_y0 * t) + (0.5 * g * t ** 2)) + ammo1_y0

    # draw

    if not (ammo1.rect.colliderect(terr.rect)) and ((ammo1.rect.x + ammo1_w) <= play_right):
        if ammo1.rect.y > play_top:
            erase_trail()
        if ammo1.rect.y > play_top+ammo1_h:
            ammo1.update()
        pygame.display.update()
    else:
        running = False

    clock.tick(80)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
