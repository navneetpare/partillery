import math

import pygame
from pygame import error
from pygame.sprite import DirtySprite
from pygame.transform import rotate

from partillery import utils
from partillery.game.terrain import Terrain


class BaseElement(DirtySprite):
    def __init__(self, terrain: Terrain, img):
        DirtySprite.__init__(self)
        self.terrain = terrain
        self.image = utils.load_image_resource(img)
        self.mask = pygame.mask.from_surface(self.image, 254)
        self.image_original = self.image.copy()
        self.rect = self.image.get_rect()
        self.h = self.rect.h
        self.w = self.rect.w
        self.dirty = 1

    # In-place rotation
    def rotate(self, rads):
        # self.erase()
        try:
            # The rotation is absolute, not relative, so we use the stored original image
            # Also the original image is located at (0, 0) so it must be moved back to loc.
            center = self.rect.center
            self.image = rotate(self.image_original, math.degrees(rads))
            self.mask = pygame.mask.from_surface(self.image, 254)
            self.rect = self.image.get_rect()
            self.rect.center = center
        except error:
            utils.bell('Cannot rotate')
            pass

    def move(self, pos: tuple):
        success = True
        prev_pos = self.rect.center
        self.rect.center = pos
        if self.rect.left < 0 or self.rect.right > self.terrain.w:
            self.rect.center = prev_pos
            success = False
        return success


    def bounce(self, self_vector, target_vector):
        pass

    def roll_on_terrain(self, pos_x):
        terrain_slope = self.get_slope_rads(pos_x)
        pos = self.get_center_above_terrain(pos_x, terrain_slope)
        self.move(pos)
        self.rotate(terrain_slope)

    def get_center_above_terrain(self, x, angle_rads):
        y = self.terrain.y_coordinates[x]
        x1 = int(self.h / 2 * math.cos(angle_rads + math.pi / 2) + x)
        y1 = int(-(self.h  / 2) * math.sin(angle_rads + math.pi / 2) + y)
        return x1, y1

    def get_slope_rads(self, x):
        # slope = (y2 - y1) / (x2 - x1)
        m = - (self.terrain.y_coordinates[x + 4] - self.terrain.y_coordinates[x - 4]) / 8
        # we take slope across (x + 4) px and (x - 4px) to smooth out jerky rotation
        # of the tank when going over curves and to get a more average slope across the width of the tank
        return math.atan(m)
