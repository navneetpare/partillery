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
v0.3
- Adding basic playability
    - Target tank - object only
    - Target hit detection
- Pretty background and tanks. Woooottt!!
- Trail erasure -- still patchy, erases two positions in advance. Scratching head...
  Uses subsurface based eraser. Rectangle detection at edges is also a problem and causes a crash.
  Need to fix erasure on collision. Still shows last trail.
  (edit)* this was due to error in initialising the eraser. It's location needs to be offset from play edges. Silly me.
"""

import pygame, sys, math, random
import time

pygame.init()
clock = pygame.time.Clock()

# Colors
col_black = 0, 0, 0
col_night = 10, 10, 10
col_terrain = 0, 130, 50
col_day = 207, 245, 254
col_eve = 0, 30, 70

# Vars
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

# Ammo physics
angle = 60  # will be user selectable
g = 400
speed_base = 800
power = 78  # this will eventually be user selectable power percentage
speed_start = speed_base * power / 100
ammo1_speed_x0 = speed_start * math.cos(math.radians(angle))
ammo1_speed_y0 = -(speed_start * math.sin(math.radians(angle)))

# set_mode(size=(0, 0), flags=0, depth=0, display=0) -> Surface
# screen=pygame.display.set_mode(size=(0,0), flags=pygame.RESIZABLE)
screen = pygame.display.set_mode((full_w, full_h))
screen.fill(col_black)

# play_surface = pygame.Surface((play_w, play_h))
# play_surface.fill(col_night)
playsurf = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\night_starry.png")
playsurf.set_alpha(None)
playsurf_rect = playsurf.get_rect()
playsurf_rect.x = play_left
playsurf_rect.y = play_top


def get_eraser(x, y, w, h):
    area = playsurf.subsurface(pygame.Rect(x - play_left, y - play_top, w, h)).copy()
    return area


class Tank(pygame.sprite.Sprite):
    def __init__(self, orientation, loc_x, loc_y):
        super(Tank, self).__init__
        self.surf = pygame.image.load(
            "C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\tank_" + orientation + ".png")
        self.rect = self.surf.get_rect()
        self.rect.x = loc_x
        self.rect.y = loc_y


class Ammo(pygame.sprite.Sprite):
    def __init__(self, loc_x, loc_y):
        super(Ammo, self).__init__
        self.surf = pygame.image.load(
            "C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\ammo_4.gif")
        self.surf.set_alpha(255)
        self.rect = self.surf.get_rect()
        self.rect.x = loc_x
        self.rect.y = loc_y
        self.w = self.rect.w
        self.h = self.rect.h
        self.prev_pos = loc_x, loc_y
        self.eraser = get_eraser(loc_x, loc_y, self.w, self.h)

    def go(self, x, y):

        alive = True
        new_rect = pygame.Rect(x, y, self.w, self.h)
        new_rect_inside = playsurf_rect.contains(new_rect)
        old_rect_inside = playsurf_rect.contains(self.rect)

        print("----------------------------------")
        print("cur " + str(self.rect.x) + " " + str(self.rect.y))
        print("new " + str(x) + " " + str(y))

        if (x > play_right) or (x + self.w < play_left):
            alive = False

        if old_rect_inside:
            # screen.blit(self.eraser, self.prev_pos)  # erase trail
            screen.blit(self.eraser, (self.rect.x, self.rect.y))  # erase trail
            a = 1
        self.prev_pos = (self.rect.x, self.rect.y)  # save current loc
        self.rect.x = x
        self.rect.y = y
        # print("x = " + str(self.rect.x) + "  y=" + str(self.rect.y))

        if new_rect_inside:
            self.eraser = get_eraser(x, y, self.w, self.h)  # get new eraser for the next location
            screen.blit(self.surf, self.rect)  # draw self to new loc
        return alive


class Terrain(pygame.sprite.Sprite):
    def __init__(self):
        super(Terrain, self).__init__
        # self.surf = pygame.Surface((play_w, terrain_h))
        # self.surf.fill(col_terrain)
        self.surf = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\t7.png")
        self.rect = self.surf.get_rect()
        self.rect.x = play_left
        self.rect.y = play_bottom - terrain_h


tank1 = Tank("right", random.randint(play_left, ((play_right - play_left) / 2) - tank_w),
             (play_bottom - terrain_h - tank_h))
tank2 = Tank("left", random.randint(((play_right - play_left) / 2), play_right - tank_w),
             (play_bottom - terrain_h - tank_h))
terr = Terrain()
# tank1 = Tank("right", play_left, (play_bottom - terrain_h - tank_h))
# tank2 = Tank("left", play_right - tank_w, (play_bottom - terrain_h - tank_h))

ammo1_x0 = tank1.rect.x + tank_w
ammo1_y0 = tank1.rect.y - ammo1_h
ammo1 = Ammo(ammo1_x0, ammo1_y0)


#  Draw initial elements
screen.blit(playsurf, play_centre)
screen.blit(terr.surf, terr.rect)
screen.blit(tank1.surf, tank1.rect)
screen.blit(tank2.surf, tank2.rect)
screen.blit(ammo1.surf, ammo1.rect)
pygame.display.update()

# game loop flag
volley_in_progress = True
move_count = 0

# timer start
t0 = pygame.time.get_ticks()

while volley_in_progress:

    # for event in pygame.event.get():
    #   if event.type == pygame.QUIT:
    #       sys.exit()

    if ammo1.rect.colliderect(terr.rect) or ammo1.rect.colliderect(tank2.rect):
        screen.blit(ammo1.eraser, ammo1.prev_pos)
        volley_in_progress = False
        break

    # compute move, s = ut + 1/2(gt^2) + x_initial
    t = (pygame.time.get_ticks() - t0) / 1000
    ammo1_new_x = round((ammo1_speed_x0 * t) + ammo1_x0)
    ammo1_new_y = round(((ammo1_speed_y0 * t) + (0.5 * g * t ** 2)) + ammo1_y0)

    # move and check
    volley_in_progress = ammo1.go(ammo1_new_x, ammo1_new_y)
    move_count += 1
    pygame.display.update()
    clock.tick(120)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
