import typing
from math import cos, sin, radians

from threading import Thread
import pygame
from pygame.sprite import LayeredDirty

from partillery.game.base_classes.base_element import BaseElement
from partillery.game.base_classes.explosionold import BaseExplosion
from partillery.game.tank import Tank


class WeaponFragment(BaseElement):
    # go
    #   custom motion (may not always be simple projectile)
    #   bounce off terrain
    #   roll on terrain
    #   holds explosion item
    def __init__(self, img, parent, terrain, kick, damage_score, mass, bounciness,
                 explosion_type, start_pos, start_angle, v, g, t0):
        BaseElement.__init__(self, terrain, img)
        self.explosion_type = explosion_type
        self.damage_score = damage_score
        self.start_pos = start_pos
        self.start_angle = start_angle
        self.v_x = v * cos(radians(start_angle))  # initial speed_x
        self.v_y = v * sin(radians(start_angle))  # initial speed_y
        self.g = g
        self.parent = parent
        self.mass = mass
        self.bounciness = bounciness
        self.kick = kick
        self.explosion = None
        self.alive = True
        self.last_pos = start_pos
        self.t0 = t0  # set at launch time
        self.visible = 1

    def update(self):
        self.projectile_motion()

    def launch(self):
        self.t0 = pygame.time.get_ticks()
        self.alive = True

    def projectile_motion(self):
        if self.alive:
            t = (pygame.time.get_ticks() - self.t0) / 1000
            pos_x = self.start_pos[0] + self.v_x * t  # No horizontal acceleration
            pos_y = self.start_pos[1] - (self.v_y * t + (0.5 * self.g * (t ** 2)))
            if self.move((pos_x, pos_y)):
                self.last_pos = (pos_x, pos_y)
                self.dirty = 1
            else:
                self.alive = False
                self.kill()

    def bounce_off_terrain(self):
        pass


class Weapon(LayeredDirty):
    def __init__(self, game):
        LayeredDirty.__init__(self)
        self.game = game
        self.explosions = []

    def spawn(self):
        pass

    def fire(self):
        while len(self) > 0:
            self.update()
            explosions = []
            explosion_threads = []
            explosions.extend(self.handle_tank_collisions())
            explosions.extend(self.handle_terrain_collisions())

            for location in explosions:
                explosion_threads.append(Thread(target=BaseExplosion,
                                                args=(self.game.screen, self.game.sky, self.game.terrain,
                                                      location, 30, 3500)))
            for thread in explosion_threads:
                thread.start()
            self.clear(self.game.screen, self.game.screen)
            self.game.tank_elements.clear(self.game.screen, self.game.screen)
            areas1 = self.game.tank_elements.draw(self.game.screen)
            areas2 = self.draw(self.game.screen)
            pygame.display.update(areas1)
            pygame.display.update(areas2)

        self.game.mode = self.game.MODE_CONTROL
        self.game.cpl.clear(self.game.screen, self.game.screen)
        areas = self.game.cpl.draw(self.game.screen)
        pygame.display.update(areas)

    def handle_tank_collisions(self):
        # dokill = True for weaponlet removes it from weaponlets collisions = pygame.sprite.groupcollide(self,
        # self.game.tanks, True, False, collided=pygame.sprite.collide_mask)
        collisions = pygame.sprite.groupcollide(self, self.game.tanks, True, False, pygame.sprite.collide_mask)
        explosions = []
        # TODO - handle tank kicks, damage, scoring, explosion
        for item in collisions.items():
            fragment = typing.cast(WeaponFragment, item[0])
            player_list = typing.cast(list, item[1])
            for hit_player in player_list:
                hit_player = typing.cast(Tank, hit_player)
                if hit_player == self.game.current_player:
                    self.game.current_player.score -= fragment.damage_score
                else:
                    self.game.current_player.score += fragment.damage_score
                explosions.append(fragment.rect.center)
                self.remove(fragment)
                del fragment
        return explosions

    def handle_terrain_collisions(self):
        explosions = []
        for fragment in self:
            if self.game.terrain.mask.overlap(typing.cast(WeaponFragment, fragment).mask, fragment.rect.topleft) \
                    or fragment.rect.bottom > self.game.h:
                self.remove(fragment)
                explosions.append(fragment.rect.center)
                del fragment
        return explosions

    # container for its elements
    # collects explosions and tracks them
    # when created, give it the first weaponlet
    # ask it to continuosly
    #   run it's weaponlets
    #   check for collisions with other tanks
    #   check for collisions with terrain
    #   run explosions
