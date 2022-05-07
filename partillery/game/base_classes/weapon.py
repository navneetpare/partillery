import typing
from math import cos, sin, radians

from threading import Thread
import pygame
from pygame.sprite import LayeredDirty

from partillery.game.base_classes.base_element import BaseElement
from partillery.game.base_classes.explosion import BaseExplosion
from partillery.game.tank import Tank


class WeaponFragment(BaseElement):
    def __init__(self, img, parent, terrain, start_pos, start_angle, t0, v=0, g=0,
                 explosion_radius=60, kick=0, damage_score=1, mass=0, bounciness=0,
                 explosion_type=BaseExplosion):
        BaseElement.__init__(self, terrain, img)
        self.explosion_type = explosion_type
        self.explosion_radius = explosion_radius
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

    def explode(self):
        return self.rect.center, self.explosion_radius, self.explosion_type

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
        explosions_alive = False
        explosions = []
        explosion_threads = []

        while len(self) > 0:
            self.update()

            new_explosion_threads = []
            new_explosions = self.handle_tank_collisions()
            new_explosions.extend(self.handle_terrain_collisions())
            explosions.extend(new_explosions)

            for explosion in new_explosions:
                # 'explosions' is a tuple (center, explosion_radius, explosion_type)
                # Thread target takes a function.
                # Here we pass the Explosion class name, which will invoke its constructor
                new_explosion_threads.append(Thread(target=explosion[2],
                                                    args=(self.game, explosion[0], explosion[1], 500)))
                explosion_threads.extend(new_explosion_threads)

            for thread in new_explosion_threads:
                thread.start()

            self.game.redraw(weapon=True, tanks=True)

            # if len(explosion_threads) > 0:
            #     for thread in explosion_threads:
            #         this_thread_alive = thread.is_alive()
            #         explosions_alive = explosions_alive or this_thread_alive
            #         if not this_thread_alive:
            #             explosion_threads.remove(thread)

        for thread in explosion_threads:
            thread.join()

        explosions_area = get_explosions_bounding_area(explosions, self.game.scene_rect)
        return explosions_area

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
                explosions.append(fragment.explode())
                self.remove(fragment)
        return explosions

    def handle_terrain_collisions(self):
        explosions = []
        for fragment in self:
            fragment = typing.cast(WeaponFragment, fragment)
            if self.game.terrain.mask.overlap(fragment.mask, fragment.rect.topleft) \
                    or fragment.rect.bottom > self.game.h:
                self.remove(fragment)
                explosions.append(fragment.explode())
        return explosions


def get_explosions_bounding_area(explosions, scene_rect):
    # 'explosions' is a list of tuples (center, explosion_radius, explosion_type)
    rect = None
    for i in range(len(explosions)):
        explosion = explosions[i]
        item_rect = pygame.Rect(0, 0, explosion[1] * 2, explosion[1] * 2)
        item_rect.center = explosion[0]
        if i == 0:
            rect = item_rect
        else:
            rect = rect.union(item_rect)
    bottom = scene_rect.bottom - 1
    rect = rect.clip(scene_rect.x, scene_rect.y, scene_rect.w, bottom)
    print('Explosions area = ' + str(rect))
    return rect