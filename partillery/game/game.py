import random
import sys
import threading
import time
import typing

import pygame
from pygame.sprite import LayeredDirty

from partillery import utils
from partillery.game.base_classes.weapon import Weapon, WeaponFragment
from partillery.game.control_panel import ControlPanel, Mouse, Control
from partillery.game.tank import Tank
from partillery.game.terrain import Terrain


class Game:
    def __init__(self, screen, resolution, restore_resolution, clock, config):
        self.fire_count = 0
        self.resolution = resolution
        self.restore_resolution = restore_resolution
        self.name = "Game"
        self.MODE_FIRE_CONTROL = 0
        self.MODE_FIRE = 1
        self.MODE_MOVE = 2
        self.MODE_TEST = 3
        self.screen = screen
        self.clock = clock
        self.config = config
        self.mode = self.MODE_FIRE_CONTROL
        self.h = int(resolution[1] * config.game.height_fraction)
        self.w = resolution[0]

        # Choose a random scene
        chosen_scene = random.choice(self.config.game.scenes)
        # Used for drawing the sky and as a background when clearing explosion areas
        self.sky = pygame.transform.scale(utils.load_image_resource(chosen_scene.background),
                                          (self.w, self.h)).convert_alpha()

        # Used as a background for turret, crosshair and tank moves. Explosions cut this surface
        # The terrain will be drawn on this.
        self.scene = self.sky.copy()
        # Rects for limiting display updates, e.g. explosions overlapping control panel.
        self.scene_rect = self.sky.get_rect()
        # self.scene.set_clip(self.scene_rect)

        # Used as a full screen background for control panel once all intial elements are drawn
        self.full_bg = None

        self.rect = pygame.Rect((0, 0), self.resolution)  # For screen clipping
        self.current_player = None
        self.player_1 = None
        self.player_2 = None
        self.tank_elements = None  # Sprite group for drawing
        self.tanks = None  # Sprite group for tank collisions
        self.cpl = None  # Control panel reference
        self.move_start_time = None
        self.pos_x = None  # Util var to track tank moves
        self.weapon = None  # The actual weapon object
        self.weapon_choice = None  # The weapon selected from the object

        # ------ Create the terrain
        self.terrain_falling = False  # To track terrain fall after explosions.
        self.terrain = Terrain(self, self.w, self.h, 'Random', chosen_scene.terrain_layers)

        # ------ Create the control panel and controls
        self.cpl = ControlPanel(0, self.h, self.w, self.resolution[1] - self.h, self.config)

    def handle_escape_key(self, event: pygame.event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.mixer.quit()
            pygame.display.set_mode(self.restore_resolution, pygame.RESIZABLE)
            pygame.display.quit()
            pygame.quit()
            sys.exit()

    def redraw(self, weapon=False, tanks=False, controls=False):
        all_rects = []
        if weapon is True:
            self.weapon.clear(self.screen, self.scene)
            all_rects.extend(self.weapon.draw(self.screen))
            # pygame.display.update(rects)
        if tanks is True:
            self.tank_elements.clear(self.screen, self.scene)
            all_rects.extend(self.tank_elements.draw(self.screen))
            # pygame.display.update(rects)
        if controls is True:
            self.cpl.clear(self.screen, self.full_bg)
            all_rects.extend(self.cpl.draw(self.screen))

        pygame.display.update(all_rects)

    def undraw(self, weapon=False, tanks=False, controls=False):
        if weapon is True:
            self.weapon.clear(self.screen, self.scene)
        if tanks is True:
            self.tank_elements.clear(self.screen, self.scene)
        if controls is True:
            self.cpl.clear(self.screen, self.full_bg)

    def draw(self, weapon=False, tanks=False, controls=False):
        if weapon is True and weapon:
            rects = self.weapon.draw(self.screen)
            pygame.display.update(rects)
        if tanks is True:
            rects = self.tank_elements.draw(self.screen)
            pygame.display.update(rects)
        if controls is True:
            rects = self.cpl.draw(self.screen)
            pygame.display.update(rects)

    def update_scoreboard(self):
        self.cpl.scoreboard.overlay.update(str(self.player_1.name) + " : " + str(self.player_1.score) + "    " +
                                           str(self.player_2.name) + " : " + str(self.player_2.score))
        # print("scoreboard: " + str(self.player_1.score) + " / " + str(self.player_2.score))
        pygame.display.update()

    # Button Actions
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

    def power_dec(self):
        power = max(self.current_player.power - 1, 0)
        self.cpl.update_power(power)
        self.current_player.power = power

    def power_inc(self):
        power = min(self.current_player.power + 1, 100)
        self.cpl.update_power(power)
        self.current_player.power = power

    def move_left(self):
        if self.current_player.moves_left > 0:
            self.current_player.move_direction = -1
            self.current_player.moves_left -= 1
            self.mode = self.MODE_MOVE
            # self.pos_x = self.current_player.rect.centerx
            self.move_start_time = pygame.time.get_ticks()
            self.cpl.update_moves_left(self.current_player.moves_left)

    def move_right(self):
        if self.current_player.moves_left > 0:
            self.current_player.move_direction = 1
            self.current_player.moves_left -= 1
            self.cpl.update_moves_left(self.current_player.moves_left)
            self.mode = self.MODE_MOVE

    def fire(self):
        self.fire_count += 1
        self.mode = self.MODE_FIRE

    def angle(self):
        pass

    def power_bar(self):
        pass

    # Game Method
    def run(self):
        # ------ Alias key params, so I don't have to type 'self' everywhere.
        # screen = self.screen
        # clock = self.clock
        # config = self.config
        g = self.config.physics.gravity

        # ------ Create tank objects, move them and draw onto screen
        self.player_1 = Tank(self, 'Rick', 'red', 45, self.terrain, g / 10)
        self.player_2 = Tank(self, 'Morty', 'blue', 120, self.terrain, g / 10)
        tw = self.player_1.rect.w
        p1_x = random.randint(0 + tw, int(self.w / 2 - tw))  # random loc in left half of the game area
        p2_x = random.randint(int(self.w / 2) + tw, int(self.w - tw))  # random loc in right half of the game area
        # print('Roll initial start ' + str(pygame.time.get_ticks()))
        self.player_1.update(roll_to=p1_x)
        # print('Roll initial end ' + str(pygame.time.get_ticks()))
        self.player_2.update(roll_to=p2_x)
        # print('Roll initial end 2 ' + str(pygame.time.get_ticks()))
        self.tank_elements = LayeredDirty(self.player_1.turret, self.player_1, self.player_1.crosshair,
                                          self.player_2.turret, self.player_2, self.player_2.crosshair)
        self.tanks = LayeredDirty(self.player_1, self.player_2)

        mouse = Mouse(self.cpl.rect.center)
        self.current_player = self.player_1
        self.current_player.crosshair.visible = 1
        self.cpl.update_values(self.current_player)

        # ------ Draw stuff on to the screen
        self.scene.blit(self.terrain.image, (0, 0))  # The scene already has the sky before this from init.
        self.screen.blit(self.scene, (0, 0))
        self.screen.blit(self.cpl.image, self.cpl.rect)
        self.full_bg = self.screen.copy()  # Capture the screen to be used as bg for controls
        self.update_scoreboard()
        # print('Tanks redraw start ' + str(pygame.time.get_ticks()))
        self.redraw(tanks=True, controls=True)

        # print('Tanks redraw end ' + str(pygame.time.get_ticks()))

        # Game modes
        def fire_control_mode():
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

            self.redraw(tanks=True, controls=True)

        def fire_mode():
            # self.screen.set_clip(self.rect)
            self.weapon = Weapon(self)
            t0 = pygame.time.get_ticks()
            start_pos = self.current_player.turret.get_absolute_nose()
            v = self.current_player.power * 1000 / 100
            # g = config.physics.gravity
            weaponFragment1 = WeaponFragment('ammo_4.gif', self.weapon, self.terrain, start_pos,
                                             self.current_player.angle, t0=t0, v=v, g=g, explosion_radius=60)

            weaponFragment2 = WeaponFragment('ammo_4.gif', self.weapon, self.terrain, start_pos,
                                             self.current_player.angle + 1, t0, v=v, g=g, explosion_radius=60)

            weaponFragment3 = WeaponFragment('ammo_4.gif', self.weapon, self.terrain, start_pos,
                                             self.current_player.angle + 2, t0, v=v, g=g, explosion_radius=60)

            weaponFragment4 = WeaponFragment('ammo_4.gif', self.weapon, self.terrain, start_pos,
                                             self.current_player.angle - 1, t0, v=v, g=g, explosion_radius=60)

            weaponFragment5 = WeaponFragment('ammo_4.gif', self.weapon, self.terrain, start_pos,
                                             self.current_player.angle - 2, t0, v=v, g=g, explosion_radius=60)

            self.weapon.add(weaponFragment1)
            # self.weapon.add(weaponFragment2)
            # self.weapon.add(weaponFragment3)
            # self.weapon.add(weaponFragment4)
            # self.weapon.add(weaponFragment5)
            explosions_area = self.weapon.fire()
            self.redraw(tanks=True, controls=True)
            # self.terrain.fall(explosions_area)
            # self.tanks.update(terrain_changed=True)
            terrain_fall_thread = threading.Thread(target=self.terrain.fall, args=[explosions_area])
            tank_fall_thread = threading.Thread(target=self.tanks.update, kwargs={'terrain_changed': True})
            terrain_fall_thread.start()
            # time.sleep(0.75)
            tank_fall_thread.start()
            terrain_fall_thread.join()
            tank_fall_thread.join()
            self.screen.set_clip(self.rect)
            self.update_scoreboard()
            self.redraw(tanks=True, controls=True)
            self.mode = self.MODE_FIRE_CONTROL
            self.switch_player()
            # self.players.clear(self.screen, self.scene)
            # tank_rects = self.players.draw(self.screen)
            # pygame.display.update()
            # pygame.display.update(tank_rects)
            # self.switch_player()

        def move_mode():
            self.move_start_time = pygame.time.get_ticks()
            while (pygame.time.get_ticks() - self.move_start_time) < self.config.game.move_duration_ms:
                self.current_player.update(roll_on_terrain=True)
                self.redraw(tanks=True)
                time.sleep(0.015)
            self.mode = self.MODE_FIRE_CONTROL

        # Game loop
        while 1:
            event = None
            for retrieved_event in pygame.event.get([pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN,
                                                     pygame.MOUSEMOTION, pygame.MOUSEWHEEL, pygame.KEYDOWN]):
                event = retrieved_event
                self.handle_escape_key(event)

            if self.mode == self.MODE_FIRE_CONTROL and event is not None:
                fire_control_mode()

            elif self.mode == self.MODE_FIRE:
                fire_mode()

            elif self.mode == self.MODE_MOVE:
                move_mode()

            self.clock.tick(self.config.display.frame_rate)
