import math
import time

import pygame.time
from pygame import Surface, draw
from pygame.rect import Rect
from pygame.sprite import DirtySprite

from partillery import utils
from partillery.game.base_classes.base_element import BaseElement
from partillery.game.terrain import Terrain


class Tank(BaseElement):
    def __init__(self, game, name: str, col: str, angle: int, terrain: Terrain, g):
        img = 'tank_' + col + '.png'
        BaseElement.__init__(self, terrain, img, g=g)
        self.game = game
        self.w = self.rect.w
        self.h = self.rect.h
        self.moves_left = 10
        self.move_direction = 1  # -1 == left, +1 = right
        # self.game_rect = game_rect
        # self.top_clamp = game_rect.top
        self.name = name
        self.score = 0
        self.power = 50
        self.angle = angle
        self.dirty = 2
        self.turret = Turret(self)
        self.crosshair = CrossHair(self)
        self.selected_weapon = "Plain bomb"
        self.resting = False

    def update(self, **kwargs):
        super().update()

        if "terrain_changed" in kwargs:
            try:
                self.current_terrain_point_index = self.terrain.points.index(self.current_terrain_point)
            except ValueError:
                self.fall()

        if "roll_on_terrain" in kwargs:
            self.roll_on_terrain(direction=self.move_direction)
            self.turret.update()
            self.crosshair.update()

        if "roll_to" in kwargs:
            self.roll_to(kwargs["roll_to"])
            self.turret.update()
            self.crosshair.update()

        if "angle" in kwargs:
            self.angle = kwargs["angle"]
            self.turret.update()
            self.crosshair.update()

        if "fall" in kwargs:
            self.fall()

    def fall(self):
        self.projectile_launch(0, 0, pygame.time.get_ticks(), self.rect.center)
        while self.terrain.is_falling or self.is_projectile:
            if not self.on_terrain():
                # print('not on terrain')
                self.projectile_motion()
                self.turret.update()
                self.crosshair.update()
                self.game.redraw(tanks=True)
                if self.on_terrain():
                    self.update(roll_to=self.rect.centerx)
                    print('rolled')
                    self.is_projectile = False
            else:
                self.is_projectile = False

    def handle_terrain_collisions(self):
        if self.on_terrain():
            self.is_projectile = False
            self.update(roll_to=self.rect.centerx)

    def on_terrain(self):
        return self.game.terrain.mask.overlap(self.mask, self.rect.topleft) or self.rect.bottom >= self.game.h
        # return self.current_terrain_point in self.terrain.points


class Turret(DirtySprite):
    def __init__(self, tank):
        super().__init__()
        # We give it a dedicated surface w = h = tw (saved as orig)
        # This will be fully transparent and copied to new every time updated. To be centered with the tank.
        self.tank = tank  # Refer to parent for easy access
        self.len = self.tank.w * 1.2
        self.bg = Surface((self.len, self.len)).convert_alpha()
        self.bg.fill((255, 255, 255, 0))  # fully transparent
        self.image = None
        self.rect = None
        self.nose = None
        self.visible = 1
        self.dirty = 2
        self.update()

    def get_relative_nose(self):
        # This nose is relative to turret img only
        angle_radians = math.radians(self.tank.angle)
        x = (self.rect.w / 2) + (self.len * math.cos(angle_radians))
        y = (self.rect.h / 2) - (self.len * math.sin(angle_radians))
        return x, y

    def get_absolute_nose(self):
        angle_radians = math.radians(self.tank.angle)
        x = self.tank.rect.centerx + (self.len * math.cos(angle_radians))
        y = self.tank.rect.centery + - (self.len * math.sin(angle_radians))
        return x, y

    def update(self):
        # Not to be called before tank.update
        self.image = self.bg.copy()
        self.rect = self.image.get_rect()
        self.rect.center = self.tank.rect.center
        self.nose = self.get_relative_nose()
        draw.line(self.image, (255, 255, 255, 255), (self.rect.w / 2, self.rect.h / 2), self.nose, 2)


class CrossHair(DirtySprite):
    def __init__(self, tank: Tank):
        super().__init__()
        # We give it a dedicated surface w = h = tw (saved as orig)
        # This will be fully transparent and copied to new every time updated. To be centered with the tank.
        self.tank = tank  # Refer to parent for easy access
        self.distance = self.tank.w * 3
        self.image = utils.load_image_resource('crosshair.png')
        self.rect = self.image.get_rect()
        w = self.rect.w  # w = h for cross-hair, so we'll reuse it.
        # Define area where cross-hair can move. Half width to be cropped out of game area.
        self.clip_rect = Rect(self.tank.game.scene_rect.left + w / 2, self.tank.game.scene_rect.top + w / 2,
                              self.tank.game.scene_rect.w - w, self.tank.game.scene_rect.h - w)
        self.visible = 0
        self.dirty = 0

    def update(self):
        angle_radians = math.radians(self.tank.angle)
        x = self.tank.rect.centerx + (self.distance * math.cos(angle_radians))
        y = self.tank.rect.centery - (self.distance * math.sin(angle_radians))
        clipped = self.clip_rect.clipline(self.tank.rect.center, (x, y))
        if not clipped:
            self.rect.center = x, y
        else:
            self.rect.center = clipped[1]
        self.dirty = 1
