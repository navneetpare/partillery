import random

import pygame
from pygame.sprite import LayeredDirty

from partillery import utils
from partillery.controls import ControlPanel
from partillery.core_sprites import Tank
from partillery.terrain import Terrain


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
            utils.load_image_resource('night_starry_blue.png'), (self.w, self.h)).convert_alpha()
        self.rect = self.surf.get_rect()
        self.background = self.surf.copy()
        pygame.display.update()

    def run(self):
        # Alias key params so I don't have to type 'self' everywhere.
        screen = self.screen
        clock = self.clock
        config = self.config
        frame_rate = config.display.frame_rate

        cpl = ControlPanel(screen, 0, self.h, self.w, config.display.height - self.h, config)
        tw = config.game.tank_width
        th = config.game.tank_height
        terr = Terrain(screen, self.w, self.h, 'Random')
        self.surf.blit(terr.surf, (0, 0))
        background = self.surf.copy()
        screen.blit(self.surf, (0, 0))
        pygame.display.update()

        screen.set_clip(screen.get_rect())

        p1_x = random.randint(0 + tw, int(self.w / 2 - tw))  # random loc in left half of the game area
        p2_x = random.randint(int(self.w / 2) + tw, int(self.w - tw))  # random loc in right half of the game area

        player_1 = Tank('Nav', 'red', 45, th, tw, p1_x, terr.y_coordinates, self.rect)
        player_2 = Tank('CPU', 'blue', 120, th, tw, p2_x, terr.y_coordinates, self.rect)

        objects = LayeredDirty(player_1.turret, player_1, player_1.cross_hair,
                               player_2.turret, player_2, player_2.cross_hair)

        objects.draw(screen)
        pygame.display.update()

        while True:
            while self.mode == self.MODE_CONTROL:
                pygame.display.update()
                clock.tick(frame_rate)

            while self.mode == self.MODE_FLIGHT:
                pygame.display.update()
                clock.tick(frame_rate)

            while self.mode == self.MODE_TEST:
                done = False
                speed = 10
                while not done:
                    p1_x += speed
                    p2_x -= speed
                    if p1_x >= (self.w - tw) or p2_x <= tw:
                        done = True
                        break

                    objects.clear(self.screen, background)
                    player_1.update(pos_x=p1_x)
                    player_2.update(pos_x=p2_x)
                    objects.draw(self.screen)
                    pygame.display.update()
                    pygame.event.clear()
                    clock.tick(frame_rate)
