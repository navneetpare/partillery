import math
import os
import pygame
import random
import sys

from partillery.ammo import Ammo
from partillery.controls import ControlPanel
from partillery.crosshair import CrossHair
from partillery.player import Player
from partillery.tank import Tank, update_turret
from partillery.terrain import Terrain


# ---------------------  UTIL FUNCTIONS  --------------------- #
def get_eraser(x, y, w, h):
    area = playsurf.subsurface(pygame.Rect(x - play_left, y - play_top, w, h)).copy()
    return area


def scale(surface, scaling_factor):
    rect = surface.get_rect()
    new_w = round(rect.w / scaling_factor)
    new_h = round(rect.h / scaling_factor)
    return pygame.transform.scale(surface, (new_w, new_h))


def clamp(n, min_n, max_n):
    return max(min(max_n, n), min_n)


# ------------------------------------------------------------ #

# Library Initialization
pygame.init()
clock = pygame.time.Clock()

# Game Modes

MODE_SELECTION = "Selection"
MODE_FLIGHT = "Flight"
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
play_h = round(full_h * 0.8)
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
curr_player = player1
enemy = player2

# Ammo physics

g = 500
speed_base = 1000

# Initialize Display Elements

pygame.display.set_caption("Partillery")
pygame.display.set_icon(pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\partillery\\resources\\images\\window_icon.png"))
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100, 40)
screen = pygame.display.set_mode((full_w, full_h), pygame.RESIZABLE)
screen.fill(col_screen)
play_img = pygame.image.load(
    "C:\\Data\\Study\\cloud\\___python_game\\partillery\\resources\\images\\nighthd_starry.png").convert()
playsurf = pygame.transform.scale(play_img, (play_w, play_h))
playsurf_rect = playsurf.get_rect()
playsurf_rect.x = play_left
playsurf_rect.y = play_top
screen.blit(playsurf, (play_left, play_top))

#  Draw initial objects

terr = Terrain(screen, play_left, play_w, play_bottom, terrain_h)

cpl = ControlPanel(screen, play_left, play_bottom, play_w, full_h - play_h, control_scale)

player1.tank = Tank(screen, play_left, play_top, "blue",
                    random.randint(play_left, ((play_right - play_left) / 2) - tank_w),
                    (play_bottom - terrain_h - tank_h), player1.angle)

player2.tank = Tank(screen, play_left, play_top, "red",
                    random.randint(((play_right - play_left) / 2), play_right - tank_w),
                    (play_bottom - terrain_h - tank_h), player2.angle)

crosshair = CrossHair(screen, play_left, play_top, curr_player.tank.rect.midtop, curr_player.angle,
                      int(curr_player.tank.rect.w * 1.5))

pygame.display.update()

# ---------------------  ENTER GAME  --------------------- #


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.K_DOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()

    while mode == MODE_SELECTION:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.K_DOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:

                # FIRE
                if cpl.fire.collidepoint(event.pos):
                    mode = MODE_FLIGHT
                    # init ammo
                    ammo_x0 = curr_player.tank.turret.nose[0]
                    ammo_y0 = curr_player.tank.turret.nose[1]
                    ammo = Ammo(screen, play_left, play_top, ammo_x0, ammo_y0)
                    speed_start = speed_base * curr_player.power / 100
                    ammo_speed_x0 = speed_start * math.cos(math.radians(curr_player.angle))
                    ammo_speed_y0 = -(speed_start * math.sin(math.radians(curr_player.angle)))
                    # timer reset
                    t0 = pygame.time.get_ticks()

                # ANGLE LEFT
                if cpl.angle_left.collidepoint(event.pos):
                    curr_player.angle += 1
                    if curr_player.angle == 360:
                        curr_player.angle = 0
                    cpl.update_angle(screen, curr_player.angle)
                    crosshair.update(screen, playsurf_rect, play_left, play_top, curr_player.angle)
                    update_turret(screen, curr_player.tank, curr_player.angle)

                # ANGLE RIGHT
                if cpl.angle_right.collidepoint(event.pos):
                    curr_player.angle -= 1
                    if curr_player.angle < 0:
                        curr_player.angle = 359
                    cpl.update_angle(screen, curr_player.angle)
                    crosshair.update(screen, playsurf_rect, play_left, play_top, curr_player.angle)
                    update_turret(screen, curr_player.tank, curr_player.angle)

                # POWER DECREMENT
                if cpl.power_dec.collidepoint(event.pos):
                    curr_player.power = max(curr_player.power - 1, 0)
                    cpl.update_power(screen, curr_player.power)

                # POWER INCREMENT
                if cpl.power_inc.collidepoint(event.pos):
                    curr_player.power = min(curr_player.power + 1, 100)
                    cpl.update_power(screen, curr_player.power)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # POWER BAR MOUSE MOVE

                if cpl.power_bar_viewer_rect.collidepoint(event.pos):
                    min_x = cpl.power_bar_fill_area.left
                    max_x = cpl.power_bar_fill_area.right
                    w = cpl.power_bar_fill_area.w
                    pygame.mouse.set_visible(False)
                    pygame.mouse.set_pos((cpl.power_bar_fill_rect.right + 1, cpl.power_bar_fill_rect.top))
                    looping = True

                    while looping:
                        event_list = pygame.event.get(pygame.MOUSEBUTTONUP)
                        for e in event_list:
                            if e.button == 1:
                                looping = False
                                pygame.mouse.set_visible(True)

                        pos_x = pygame.mouse.get_pos()[0]
                        val = int((clamp(pos_x, min_x, max_x) - min_x) * 100 / w)
                        curr_player.power = val
                        cpl.update_power(screen, curr_player.power)

                        pygame.display.update()
                        clock.tick(60)

                # ANGLE MOUSE MOVE
                if cpl.angle_viewer_rect.collidepoint(event.pos):

                    # we move the turret / angle based on mouse x movement rather than x,y movement - that's not
                    # intuitive
                    saved_pos = pygame.mouse.get_pos()
                    initial_angle = curr_player.angle
                    pygame.mouse.set_pos(playsurf_rect.center)
                    pos1 = saved_pos[0]
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
                    looping = True

                    while looping:

                        event_list = pygame.event.get(pygame.MOUSEBUTTONUP)
                        for e in event_list:
                            if e.button == 1:
                                looping = False
                                pygame.event.set_grab(False)
                                pygame.mouse.set_pos(saved_pos)
                                pygame.mouse.set_visible(True)

                        pos2 = pygame.mouse.get_pos()[0]
                        curr_player.angle = int((pos1 - pos2) / 2) + initial_angle

                        if curr_player.angle < 0:
                            curr_player.angle = 359
                        if curr_player.angle > 359:
                            curr_player.angle = 0

                        cpl.update_angle(screen, curr_player.angle)
                        update_turret(screen, curr_player.tank, curr_player.angle)
                        crosshair.update(screen, playsurf_rect, play_left, play_top, curr_player.angle)

                        pygame.display.update()
                        clock.tick(60)

        pygame.display.update()
        clock.tick(60)

    while mode == MODE_FLIGHT:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.K_DOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()

        # compute move, s = ut + 1/2(gt^2) + x_initial
        t = (pygame.time.get_ticks() - t0) / 1000
        ammo_new_x = round((ammo_speed_x0 * t) + ammo_x0)
        ammo_new_y = round(((ammo_speed_y0 * t) + (0.5 * g * t ** 2)) + ammo_y0)

        # move and check
        if not (ammo.go(screen, playsurf_rect, play_left, play_top, terr.rect, enemy.tank.rect, ammo_new_x,
                        ammo_new_y)):
            mode = MODE_SELECTION
            ammo = None
            break

        pygame.display.update()
        clock.tick(60)
