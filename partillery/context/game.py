import random
import sys
from time import sleep

import pygame
from pygame.sprite import LayeredDirty, DirtySprite, Sprite

from partillery import utils
from partillery.controls import ControlPanel, Mouse
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
        self.mode = self.MODE_CONTROL
        self.h = int(config.display.height * config.game.height_fraction)
        self.w = config.display.width
        self.surf = pygame.transform.scale(
            utils.load_image_resource('night_starry_blue.png'), (self.w, self.h)).convert_alpha()
        self.rect = self.surf.get_rect()
        self.background = self.surf.copy()
        pygame.display.update()

    def handle_events(self):
        pass

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
        screen.blit(self.surf, (0, 0))
        game_bg = self.surf.copy()
        pygame.display.update()
        full_bg = screen.copy()

        screen.set_clip(screen.get_rect())

        p1_x = random.randint(0 + tw, int(self.w / 2 - tw))  # random loc in left half of the game area
        p2_x = random.randint(int(self.w / 2) + tw, int(self.w - tw))  # random loc in right half of the game area

        player_1 = Tank('Nav', 'red', 45, th, tw, p1_x, terr.y_coordinates, self.rect)
        player_2 = Tank('CPU', 'blue', 120, th, tw, p2_x, terr.y_coordinates, self.rect)

        objects = LayeredDirty(player_1.turret, player_1, player_1.cross_hair,
                               player_2.turret, player_2, player_2.cross_hair)

        objects.draw(screen)
        pygame.display.update()

        mouse = Mouse(cpl.rect.center)
        current_player = player_1

        while 1:
            while self.mode == self.MODE_CONTROL:

                for event in pygame.event.get():
                    pygame.event.clear()
                    if event.type == pygame.MOUSEMOTION:
                        mouse.rect.center = event.pos
                        focused_control = pygame.sprite.spritecollideany(mouse, cpl.controls)
                        if not mouse.locked:
                            if mouse.prev_focused_control == focused_control:
                                pass
                            else:
                                if mouse.prev_focused_control is not None:
                                    getattr(mouse.prev_focused_control, 'hover_off')()
                                if focused_control is not None:
                                    getattr(focused_control, 'hover_on')()
                            mouse.prev_focused_control = focused_control

                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        focused_control = pygame.sprite.spritecollideany(mouse, cpl.controls)
                        mouse.clicked_control = focused_control
                        if focused_control is not None:
                            mouse.locked = getattr(focused_control, 'click_down')(current_player)
                            if mouse.locked:
                                mouse.saved_pos = event.pos
                                pygame.mouse.set_visible(False)

                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        if mouse.locked:
                            pygame.mouse.set_pos(mouse.saved_pos)
                        mouse.locked = False
                        pygame.mouse.set_visible(True)
                        focused_control = pygame.sprite.spritecollideany(mouse, cpl.controls)
                        if mouse.clicked_control is not None:
                            if focused_control == mouse.clicked_control:
                                getattr(mouse.clicked_control, 'click_up')(True, current_player)
                            else:
                                getattr(mouse.clicked_control, 'click_up')(False, current_player)
                        mouse.clicked_control = None

                    sleep(0.015)
                    cpl.elements.clear(screen, full_bg)
                    dirty_rect_list = cpl.elements.draw(screen)
                    pygame.display.update(dirty_rect_list)
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

                    objects.clear(self.screen, game_bg)
                    player_1.update(pos_x=p1_x)
                    player_2.update(pos_x=p2_x)
                    objects.draw(self.screen)
                    pygame.display.update()
                    pygame.event.clear()
                    clock.tick(frame_rate)
