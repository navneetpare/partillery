import random
import sys
import typing
from time import sleep

import pygame
from pygame.sprite import LayeredDirty
from partillery import utils
from partillery.controls import ControlPanel, Mouse, Control
from partillery.core_sprites import Tank
from partillery.terrain import Terrain


class Game:
    def __init__(self, screen, resolution, restore_resolution, clock, config):
        self.resolution = resolution
        self.restore_resolution = restore_resolution
        self.name = "Game"
        self.MODE_CONTROL = 0
        self.MODE_FLIGHT = 1
        self.MODE_MOVE = 2
        self.MODE_TEST = 3
        self.screen = screen
        self.clock = clock
        self.config = config
        self.mode = self.MODE_CONTROL
        self.h = int(resolution[1] * config.game.height_fraction)
        self.w = resolution[0]
        self.surf = pygame.transform.scale(
            utils.load_image_resource('night_starry_blue.png'), (self.w, self.h)).convert_alpha()
        self.rect = self.surf.get_rect()
        self.background = self.surf.copy()
        self.current_player = None
        self.player_1 = None
        self.player_2 = None
        self.cpl = None  # Control panel reference
        pygame.display.update()

    def handle_exit_key(self, event: pygame.event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.mixer.quit()
            pygame.display.set_mode(self.restore_resolution, pygame.RESIZABLE)
            pygame.display.quit()
            pygame.quit()
            sys.exit()

    def switch_player(self):
        self.current_player.crosshair.visible = 0
        if self.current_player == self.player_1:
            self.current_player = self.player_2
        else:
            self.current_player = self.player_1
        self.cpl.update_values(self.current_player)
        self.current_player.crosshair.visible = 1

    def angle_right(self):
        angle = self.current_player.angle - 1
        if angle < 0:
            angle = 359
        self.cpl.update_angle(angle)
        self.current_player.update(angle=angle)

    def angle_left(self):
        angle = self.current_player.angle + 1
        if angle == 360:
            angle = 0
        self.cpl.update_angle(angle)
        self.current_player.update(angle=angle)

    def power_dec (self):
        power = max(self.current_player.power - 1, 0)
        self.cpl.update_power(power)
        self.current_player.power = power

    def power_inc (self):
        power = min(self.current_player.power + 1, 100)
        self.cpl.update_power(power)
        self.current_player.power = power

    def move_left(self):
        if self.current_player.moves_left > 0:
            self.current_player.move_direction = -1
            self.current_player.moves_left -= 1
            self.mode = self.MODE_MOVE
            self.cpl.update_moves_left(self.current_player.moves_left)

    def move_right(self):
        if self.current_player.moves_left > 0:
            self.current_player.move_direction = 1
            self.current_player.moves_left -= 1
            self.mode = self.MODE_MOVE
            self.cpl.update_moves_left(self.current_player.moves_left)

    def fire(self):
        self.switch_player()

    def angle(self):
        pass

    def power_bar(self):
        pass

    def run(self):
        # Alias key params so I don't have to type 'self' everywhere.
        screen = self.screen
        clock = self.clock
        config = self.config
        frame_rate = config.display.frame_rate

        self.cpl = ControlPanel(screen, 0, self.h, self.w, self.resolution[1] - self.h, config)
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

        self.player_1 = Tank('Nav', 'red', 45, th, tw, p1_x, terr.y_coordinates, self.rect)
        self.player_2 = Tank('CPU', 'blue', 120, th, tw, p2_x, terr.y_coordinates, self.rect)

        objects = LayeredDirty(self.player_1.turret, self.player_1, self.player_1.crosshair,
                               self.player_2.turret, self.player_2, self.player_2.crosshair)

        mouse = Mouse(self.cpl.rect.center)
        self.current_player = self.player_1
        self.current_player.crosshair.visible = 1
        self.cpl.update_values(self.current_player)
        objects.draw(screen)
        self.cpl.elements.draw(screen)
        pygame.display.update()

        while 1:
            while self.mode == self.MODE_CONTROL:
                for event in pygame.event.get():
                    self.handle_exit_key(event)
                    pygame.event.clear()
                    if event.type == pygame.MOUSEMOTION:
                        mouse.rect.center = event.pos
                        # Because 'spritecollideany' returns Sprite object instead of Control
                        focused_control = typing.cast(Control, pygame.sprite.spritecollideany(mouse, self.cpl.controls))
                        if not mouse.locked:
                            if mouse.prev_focused_control == focused_control:
                                pass
                            else:
                                if mouse.prev_focused_control is not None:
                                    mouse.prev_focused_control.hover_off()
                                if focused_control is not None:
                                    focused_control.hover_on()
                            mouse.prev_focused_control = focused_control
                        else:
                            mouse.clicked_control.handle_mouse_move(self.current_player, event.pos)

                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # Because 'spritecollideany' returns Sprite object instead of Control
                        focused_control = typing.cast(Control, pygame.sprite.spritecollideany(mouse, self.cpl.controls))
                        mouse.clicked_control = focused_control
                        if focused_control is not None:
                            mouse.locked = focused_control.click_down(event.pos)
                            if mouse.locked:
                                mouse.saved_pos = event.pos
                                pygame.mouse.set_visible(False)

                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        if mouse.locked:
                            pygame.mouse.set_pos(mouse.saved_pos)
                        mouse.locked = False
                        pygame.mouse.set_visible(True)
                        focused_control = typing.cast(Control, pygame.sprite.spritecollideany(mouse, self.cpl.controls))
                        if mouse.clicked_control is not None:
                            # Actuate button on click up, only if the mouse has not moved away from
                            # the button that was 'clicked down'.
                            actuate = (focused_control == mouse.clicked_control)  # Boolean
                            mouse.clicked_control.click_up(actuate)
                            if actuate:
                                # Call actuation method by name
                                # E.g. if clicked_control.name = angle_inc, call method self.angle_inc()
                                getattr(self, mouse.clicked_control.name)()
                        mouse.clicked_control = None

                    sleep(0.015)
                    self.cpl.elements.clear(screen, full_bg)
                    objects.clear(screen, full_bg)
                    dirty_rect_list = self.cpl.elements.draw(screen)
                    pygame.display.update(dirty_rect_list)
                    dirty_rect_list = objects.draw(screen)
                    pygame.display.update(dirty_rect_list)
                    clock.tick(frame_rate)

            while self.mode == self.MODE_FLIGHT:
                pygame.display.update()
                clock.tick(frame_rate)

            while self.mode == self.MODE_MOVE:
                speed = self.current_player.move_direction
                t0 = pygame.time.get_ticks()  # get start time
                pos_x = self.current_player.rect.centerx
                while (pygame.time.get_ticks() - t0) < config.game.move_duration_ms:
                    pos_x += speed
                    if pos_x >= (self.w - tw) or pos_x <= tw:
                        done = True
                        pygame.event.clear()
                        break
                    objects.clear(self.screen, game_bg)
                    self.current_player.update(pos_x=pos_x)
                    objects.draw(self.screen)
                    pygame.display.update()
                    clock.tick(frame_rate)
                self.mode = self.MODE_CONTROL

            while self.mode == self.MODE_TEST:
                done = False
                speed = 1
                while not done:
                    p1_x += speed
                    p2_x -= speed
                    if p1_x >= (self.w - tw) or p2_x <= tw:
                        done = True
                        break

                    objects.clear(self.screen, game_bg)
                    self.player_1.update(pos_x=p1_x)
                    self.player_2.update(pos_x=p2_x)
                    objects.draw(self.screen)
                    pygame.display.update()
                    pygame.event.clear()
                    clock.tick(frame_rate)
                    self.handle_exit_key(event)
