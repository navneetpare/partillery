# https://stackoverflow.com/questions/12787650/finding-the-index-of-n-biggest-elements-in-python-array-list-efficiently?noredirect=1&lq=1

import math
import os
import random
import sys
from time import sleep
import pygame

from partillery.ammo.ammo import Ammo
from partillery.controls_old import ControlPanel
from partillery.player import Player
from partillery.tank import Tank
from partillery.terrain import Terrain
from partillery.explosion import Explosion


# Library Initialization
pygame.init()
clock = pygame.time.Clock()

# Game Modes

MODE_SELECTION = "Selection"
MODE_FLIGHT = "Flight"
MODE_TEST = "Test"
mode = MODE_TEST

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

display_w = 1280
display_h = 720
game_w = display_w
game_h = int(display_h * 0.8)
game_l = (display_w - game_w) / 2
game_r = game_l + game_w
# play_top = (full_h - play_h) / 2
game_t = 0
game_b = game_t + game_h
terrain_h = round(game_h * 0.2)
control_h = display_h - game_h
control_scale = 15  # for my ctrl images; set from tests
tank_h = 16
tank_w = 32
tank_x = game_l
tank_y = game_t + game_h - tank_h - terrain_h
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


# ---------------------  UTIL FUNCTIONS  --------------------- #
def get_eraser(x, y, w, h):
    area = screen.subsurface(pygame.Rect(x - game_l, y - game_t, w, h)).copy()
    return area


def scale(surface, scaling_factor):
    rect = surface.get_rect()
    new_w = round(rect.w / scaling_factor)
    new_h = round(rect.h / scaling_factor)
    return pygame.transform.scale(surface, (new_w, new_h))


def clamp(n, min_n, max_n):
    return max(min(max_n, n), min_n)


def get_slope_radians(xnew):
    # slope = (y2 - y1) / (x2 - x1)
    m = - (terr.y_coordinates[xnew + 4] - terr.y_coordinates[xnew - 4]) / 8 # ignore div by x2 - x1 which is always 1
    return math.atan(m)


def get_tank_center(x, angle):
    y = terr.y_coordinates[x - 1]
    x1 = int(tank_h / 2 * math.cos(angle + math.pi / 2) + x)
    y1 = int(-(tank_h / 2) * math.sin(angle + math.pi / 2) + y)
    return x1, y1


# ------------------------------------------------------------ #


# Initialize Display Elements

pygame.display.set_caption("Partillery")
pygame.display.set_icon(pygame.image.load("resources/images/window_icon.png"))
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100, 40)
screen = pygame.display.set_mode((display_w, display_h), pygame.RESIZABLE)
screen_rect = screen.get_rect()
screen.fill(col_screen)
play_img = pygame.image.load("resources/images/night_starry_blue.png").convert_alpha()
gamesurf = pygame.transform.scale(play_img, (game_w, game_h))
gamesurf_bk = gamesurf.copy()
gamesurf_rect = gamesurf.get_rect()
gamesurf_rect.x = game_l
gamesurf_rect.y = game_t
screen.blit(gamesurf, (game_l, game_t))

# ---------------------  Draw initial elements  --------------------- #

cpl = ControlPanel(screen, game_l, game_b, game_w, display_h - game_h, control_scale)

n1 = pygame.time.get_ticks()
terr = Terrain(screen, game_w, game_h, 'Random')
screen.blit(terr.surf, (0, 0))

tank1_x = random.randint(game_l, ((game_r - game_l) / 2) - tank_w)  # random x location
# tank1_x = 32
tank1_slope_radians = get_slope_radians(tank1_x)  # slope angle on terrain curve
tank1_center = get_tank_center(tank1_x, tank1_slope_radians)  # new center

tank2_x = random.randint(((game_r - game_l) / 2), game_r - tank_w)
tank2_slope_radians = get_slope_radians(tank2_x)
tank2_center = get_tank_center(tank2_x, tank2_slope_radians)

player1.tank = Tank(screen, gamesurf_rect, 'red', tank1_x, tank1_center, tank1_slope_radians, player1.angle)
player2.tank = Tank(screen, gamesurf_rect, "blue", tank2_x, tank2_center, tank2_slope_radians, player2.angle)

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

        screen.set_clip(screen_rect)
        player.tank.crosshair.show(screen)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.K_DOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if event.type == pygame.MOUSEMOTION:
                    # FIRE
                    if cpl.fire.collidepoint(event.pos):
                        player.tank.crosshair.hide(screen)
                        mode = MODE_FLIGHT
                        # init ammo
                        ammo_x0 = player.tank.turret_nose[0]
                        ammo_y0 = player.tank.turret_nose[1]
                        ammo = Ammo(screen, ammo_x0, ammo_y0)
                        speed_start = speed_base * player.power / 100
                        ammo_speed_x0 = speed_start * math.cos(math.radians(player.angle))
                        ammo_speed_y0 = -(speed_start * math.sin(math.radians(player.angle)))
                        # timer reset
                        t0 = pygame.time.get_ticks()

                    # ANGLE LEFT
                    if cpl.angle_inc.collidepoint(event.pos):
                        player.angle += 1
                        if player.angle == 360:
                            player.angle = 0
                        cpl.update_angle(screen, player.angle)
                        player.tank.crosshair.update(screen, gamesurf_rect, player.angle)
                        player.tank.draw_turret(screen, player.angle, False)

                    # ANGLE RIGHT
                    if cpl.angle_dec.collidepoint(event.pos):
                        player.angle -= 1
                        if player.angle < 0:
                            player.angle = 359
                        cpl.update_angle(screen, player.angle)
                        player.tank.crosshair.update(screen, gamesurf_rect, player.angle)
                        player.tank.draw_turret(screen, player.angle, False)

                    # POWER DECREMENT
                    if cpl.power_dec.collidepoint(event.pos):
                        player.power = max(player.power - 1, 0)
                        cpl.update_power(screen, player.power)

                    # POWER INCREMENT
                    if cpl.power_inc.collidepoint(event.pos):
                        player.power = min(player.power + 1, 100)
                        cpl.update_power(screen, player.power)

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
                        sleep(0.005)
                        event_list = pygame.event.get(pygame.MOUSEBUTTONUP)
                        for e in event_list:
                            if e.button == 1:
                                looping = False
                                pygame.mouse.set_visible(True)

                        pos_x = pygame.mouse.get_pos()[0]
                        val = int((clamp(pos_x, min_x, max_x) - min_x) * 100 / w)
                        player.power = val
                        cpl.update_power(screen, player.power)

                        pygame.display.update()
                        clock.tick(60)

                # ANGLE MOUSE MOVE
                if cpl.angle_viewer_rect.collidepoint(event.pos):

                    # we move the turret / angle based on mouse x movement rather than x,y movement - that's not
                    # intuitive
                    saved_pos = pygame.mouse.get_pos()
                    initial_angle = player.angle
                    pygame.mouse.set_pos(gamesurf_rect.center)
                    pos1 = saved_pos[0]
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
                    looping = True

                    while looping:
                        sleep(0.005)
                        pos2 = pygame.mouse.get_pos()[0]
                        player.angle = int((pos1 - pos2) / 2) + initial_angle

                        if player.angle < 0:
                            player.angle = 359
                        if player.angle > 359:
                            player.angle = 0

                        cpl.update_angle(screen, player.angle)
                        player.tank.draw_turret(screen, player.angle, False)
                        player.tank.crosshair.update(screen, gamesurf_rect, player.angle)

                        event_list = pygame.event.get(pygame.MOUSEBUTTONUP)
                        for e in event_list:
                            if e.button == 1:
                                looping = False
                                pygame.event.set_grab(False)
                                pygame.mouse.set_pos(saved_pos)
                                pygame.mouse.set_visible(True)

                        pygame.display.update()
                        clock.tick(60)

        pygame.display.update()
        clock.tick(60)

    while mode == MODE_FLIGHT:
        screen.set_clip(gamesurf_rect)
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
        if not (ammo.go(screen, gamesurf_bk, gamesurf_rect, game_h, terr.mask, enemy.tank, ammo_new_x,
                        ammo_new_y)):
            mode = MODE_SELECTION
            del ammo
            # change player
            if player == player1:
                player = player2
                enemy = player1
            else:
                player = player1
                enemy = player2

            cpl.update_angle(screen, player.angle)
            cpl.update_power(screen, player.power)

            break

        pygame.display.update()
        clock.tick(120)

    while mode == MODE_TEST:
        xnew = tank1_x
        # current_terr_loc = terr.points[]
        done = False
        speed = 1
        on_click = False
        while not done and xnew < game_w - 75:
            if on_click:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        #  move
                        xnew = player1.tank.proj_x + speed
                        # new_terr_loc = speed
                        angle = get_slope_radians(xnew)
                        if xnew >= game_w:  # or (angle >= math.pi / 4):
                            done = True
                            break
                        center = get_tank_center(xnew, angle)
                        player1.tank.go(screen, center, xnew, angle)
                        pygame.display.update()
                        # time.sleep(500000)'''
                        pygame.event.clear()
                        clock.tick(60)
            else:
                #  move
                xnew = player1.tank.proj_x + speed
                angle = get_slope_radians(xnew)
                if xnew >= game_w:  # or (angle >= math.pi / 4):
                    done = True
                    break
                center = get_tank_center(xnew, angle)
                player1.tank.go(screen, center, xnew, angle)
                pygame.display.update()
                # time.sleep(500000)'''
                pygame.event.clear()
                clock.tick(60)


