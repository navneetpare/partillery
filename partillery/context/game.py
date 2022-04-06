import math
import random
import time

import pygame
from pygame.sprite import Group

from partillery import utils
from partillery.controls import ControlPanel
from partillery.core_sprites import TankBody
from partillery.tank import Tank
from partillery.terrain import Terrain
from partillery.utils import get_slope_radians


class Game:

    def __init__(self, screen, clock, config):
        self.name = "Game"
        self.MODE_CONTROL = "Control"
        self.MODE_FLIGHT = "Flight"
        self.MODE_TEST = "Test"
        self.screen = screen
        self.clock = clock
        self.config = config
        self.mode = self.MODE_TEST
        self.h = int(config.display.height * config.game.height_fraction)
        self.w = config.display.width
        self.surf = pygame.transform.scale(
            utils.load_image_resource('night_starry_blue.png'), (self.w, self.h))
        self.background = self.surf.copy()
        pygame.display.update()

    def run(self):
        # Alias key params so I don't have to type 'self' everywhere.
        screen = self.screen
        clock = self.clock
        config = self.config
        frame_rate = config.display.frame_rate

        # Game window dims and coordinates (height, width, left edge, right edge, top edge, bottom edge)
        h = int(config.display.height * config.game.height_fraction)
        w = config.display.width

        cpl = ControlPanel(screen, 0, h, w, config.display.height - h, config)
        tw = config.game.tank_width
        th = config.game.tank_height
        terr = Terrain(screen, w, h, 'Random')
        self.surf.blit(terr.surf, (0, 0))
        background = self.surf.copy()
        screen.blit(self.surf, (0, 0))
        pygame.display.update()

        p1_x = random.randint(0 + tw, int(w / 2 - tw))  # random loc in left half of the game area
        p1_y = utils.get_slope_radians(terr, p1_x)
        p2_x = random.randint(int(w / 2) + tw, int(w - tw))  # random loc in right half of the game area
        p2_y = utils.get_slope_radians(terr, p2_x)

        # p1 = Tank(self.surf, None, 'red', p1_x, (p1_x, p1_y), 0, 90)

        p1 = TankBody('red', th, tw, p1_x, 60, 50, terr.y_coordinates)
        p2 = TankBody('blue', th, tw, p2_x, 120, 50, terr.y_coordinates)

        tanks = Group(p1, p2)

        print('tank1 rect' + str(p1.rect))
        print('tank2 rect' + str(p2.rect))

        while True:
            while self.mode == self.MODE_CONTROL:
                pygame.display.update()
                clock.tick(frame_rate)

            while self.mode == self.MODE_FLIGHT:
                pygame.display.update()
                clock.tick(frame_rate)

            while self.mode == self.MODE_TEST:
                done = False
                speed = 1
                while not done:
                    pygame.display.update()
                    clock.tick(frame_rate)
                    p1_x += speed
                    if p1_x >= (w - tw):
                        done = True
                        # break
                    p1.move_on_terrain(p1_x)
                    print(p1.rect)
                    print('tried to move')
                    updates = tanks.clear(self.screen, background)
                    updates = tanks.draw(self.screen)

                # pygame.event.clear()
                # clock.tick(60)

                # pygame.display.update()
                # clock.tick(frame_rate)
