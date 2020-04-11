"""
Changelog
==========
v0.1
- Got the basic projectile motion figured out.
- Motion curvature is choppy.
  (Retrospectively this is due to reliance on frame refresh to do computations instead of time elapsed.)
"""

import pygame, sys, math
import time

pygame.init()
clock=pygame.time.Clock()

full_width=1024
full_height=768
play_width=900
play_height=600
play_centre=(full_width-play_width)/2, (full_height-play_height)/2
terrain_initial_location=62,484
tank1_initial_location=100,(484-14)
ammo1_start_x=100+16-4
ammo1_start_y=484-32+16-8

# Colors
col_black = 0,0,0
col_gray = 10,10,10
col_terrain = 0,130,50
col_sky_blue = 207,245,254


class Terrain(pygame.sprite.Sprite):
    def __init__(self):
        super(Terrain, self).__init__
        self.surf=pygame.Surface((900,200))
        self.surf.fill(col_terrain)
        self.rect=self.surf.get_rect()

class Tank(pygame.sprite.Sprite):
    def __init__(self):
        super(Tank, self).__init__
        self.surf=pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\tank_right.png")
        self.rect=self.surf.get_rect()

class Ammo(pygame.sprite.Sprite):
    def __init__(self):
        super(Ammo, self).__init__
        self.surf=pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\ammo_8.gif")
        self.rect=self.surf.get_rect()
        self.rect.x=ammo1_start_x
        self.rect.y=ammo1_start_y

terr = Terrain()
tank1 = Tank()
ammo1 = Ammo()

#set_mode(size=(0, 0), flags=0, depth=0, display=0) -> Surface
#screen=pygame.display.set_mode(size=(0,0), flags=pygame.RESIZABLE)
screen=pygame.display.set_mode((full_width, full_height))
screen.fill(col_black)

play_surface=pygame.Surface((play_width, play_height))
play_surface.fill(col_gray)

screen.blit(play_surface, play_centre)
screen.blit(terr.surf, terrain_initial_location)
screen.blit(tank1.surf, tank1_initial_location)
screen.blit(ammo1.surf, (ammo1_start_x, ammo1_start_y))

#mark a bit of the sky as reference to clear out ammo trail
ammo_background_rect=pygame.Rect(0,0,8,8)
pygame.display.flip()

#Ammo initial speed
angle=60
speed_start=6
speed_x = speed_start * math.cos(math.radians(angle))
speed_y = speed_start * math.sin(math.radians(angle))

# timer start
t0=pygame.time.get_ticks()

#loop flag
running=True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    #get original ammo location
    ammo1_rect_old = pygame.Rect.copy(ammo1.rect)
    #move the ammo
    ammo1.rect.move_ip(speed_x,-(speed_y-(0.5*0.0098)*(pygame.time.get_ticks()-t0)))
    ammo_x = ammo1.rect.x
    ammo_y = ammo1.rect.y

    #draw
    screen.blit(ammo1.surf, (ammo_x, ammo_y))
    pygame.display.update()
    clock.tick(120)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()




