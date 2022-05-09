import math

import pygame
from pygame import error
from pygame.sprite import DirtySprite
from pygame.transform import rotate

from partillery import utils
from partillery.game.terrain import Terrain


def get_slope_rads(left_point, right_point):
    m = - (right_point[1] - left_point[1]) / (right_point[0] - left_point[0])
    return math.atan(m)


class BaseElement(DirtySprite):
    def __init__(self, terrain: Terrain, img, g=0, mass=0, bounciness=0):
        DirtySprite.__init__(self)
        self.terrain = terrain
        self.image = utils.load_image_resource(img)
        self.mask = pygame.mask.from_surface(self.image, 254)
        self.image_original = self.image.copy()
        self.rect = self.image.get_rect()
        self.h = self.rect.h
        self.w = self.rect.w
        self.dirty = 1
        self.current_rotation = 0

        # For projectile motion
        self.g = g
        self.t0 = None
        self.is_projectile = False
        self.start_pos = None
        self.last_pos = None
        self.v0_x = 0  # initial speed_x
        self.v0_y = 0  # initial speed_y

        # For bouncing
        self.mass = mass
        self.bounciness = bounciness

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
        if self.rect.left < 0 or self.rect.right > self.terrain.w or self.rect.bottom >= self.terrain.game_h - 1:
            self.rect.center = prev_pos
            success = False
        return success

    def move_anyway(self, pos: tuple):
        self.rect.center = pos
        return True

    def projectile_launch(self, v, angle, t0, start_pos):
        self.t0 = t0
        self.start_pos = start_pos
        self.last_pos = start_pos
        self.v0_x = v * math.cos(math.radians(angle))  # initial speed_x
        self.v0_y = v * math.sin(math.radians(angle))  # initial speed_y
        self.is_projectile = True

    def projectile_motion(self, kill=False):
        if self.is_projectile:
            t = (pygame.time.get_ticks() - self.t0) / 1000
            pos_x = self.start_pos[0] + self.v0_x * t  # No horizontal acceleration
            pos_y = self.start_pos[1] - (self.v0_y * t + (0.5 * self.g * (t ** 2)))
            if self.move((pos_x, pos_y)):
                self.last_pos = (pos_x, pos_y)
                self.dirty = 1
            else:
                self.is_projectile = False
                if kill:
                    self.kill()

    def bounce(self, self_vector, target_vector):
        pass

    def roll_on_terrain(self, current_point_index, direction: int):
        tx = pygame.time.get_ticks()
        i = current_point_index + direction
        x0 = self.terrain.points[i][0]
        y0 = self.terrain.points[i][1]

        print('terr_point: ' + str((x0, y0)))
        # slope_angle = 0
        # point1 = self.terrain.points[i]
        # point2 = self.terrain.points[i + direction]
        # if direction > 0:
        #     slope_angle = self.get_slope_rads(point1, point2)
        #     rightx = point2[0] + (self.w / 2) * math.cos(slope_angle)
        #     righty = point2[0] - (self.w / 2) * math.sin(slope_angle)
        #     leftx = point2[0] - (self.w / 2) * math.cos(slope_angle)
        #     lefty = point2[0] + (self.w / 2) * math.sin(slope_angle)
        # else:
        #     slope_angle = self.get_slope_rads(point2, point1)
        #
        # normal = slope_angle + math.pi / 2
        #
        # # base line
        # basepoint1 =
        left_point = None
        right_point = None
        slope_angle = None

        for r in range(int(self.w/2)-1, self.w):
            for j in range(i - 2 * self.w, i):
                x = self.terrain.points[j][0]
                y = self.terrain.points[j][1]
                if int(math.sqrt(math.pow(x - x0, 2) + math.pow(y - y0, 2))) == r:
                    left_point = x, y
                    break
            for k in range(i, i + 2 * self.w):
                x = self.terrain.points[k][0]
                y = self.terrain.points[k][1]
                if int(math.sqrt(math.pow(x - x0, 2) + math.pow(y - y0, 2))) == r:
                    right_point = x, y
                    break
            if right_point is not None and left_point is not None:
                break
        print('left_point :' + str(left_point))
        print('right_point:' + str(right_point))
        if right_point is not None and left_point is not None:
            # concave or flat resting base
            if y0 > left_point[1] or y0 > right_point[1] or (y0 == left_point[1] == right_point [1]):
                # slope will be based on left and right points
                slope_angle = get_slope_rads(left_point, right_point)
                midpoint = (left_point[0] + right_point[0]) / 2, (left_point[1] + right_point[1])/ 2
                x = int(self.h / 2 * math.cos(slope_angle + math.pi / 2) + midpoint[0])
                y = int(-(self.h   / 2) * math.sin(slope_angle + math.pi / 2) + midpoint[1])

            else:  # convex resting base
                # discard left and right points and use current point and last
                if direction > 0:
                    right_point = self.terrain.points[i]
                    left_point = self.terrain.points[current_point_index]
                else:
                    right_point = self.terrain.points[current_point_index]
                    left_point = self.terrain.points[i]

                slope_angle = get_slope_rads(left_point, right_point)
                x = int(self.h / 2 * math.cos(slope_angle + math.pi / 2) + x0)
                y = int(-(self.h / 2) * math.sin(slope_angle + math.pi / 2) + y0)

            print('center: ' + str((x,y)))
            # Try moving
            prev_rotation = self.current_rotation
            self.rotate(slope_angle)
            if self.move_anyway((x, y)):
                if self.terrain.mask.overlap(self.mask, self.rect.topleft):
                    # self.rotate(prev_rotation)
                    print('overlapped')
        print('timing: ' + str(pygame.time.get_ticks() - tx))

    def roll_to(self, x):
        self.roll_on_terrain(self.terrain.get_point_index(x), 1)

    def roll_on_terrain_old(self, pos_x):
        terrain_slope = self.get_slope_rads_old(pos_x)
        pos = self.get_center_above_terrain(pos_x, terrain_slope)
        self.move(pos)
        self.rotate(terrain_slope)

    def get_center_above_terrain(self, x, angle_rads):
        y = self.terrain.y_coordinates[x]
        x1 = int(self.h / 2 * math.cos(angle_rads + math.pi / 2) + x)
        y1 = int(-(self.h / 2) * math.sin(angle_rads + math.pi / 2) + y)
        return x1, y1

    def get_slope_rads_old(self, x):
        # slope = (y2 - y1) / (x2 - x1)
        m = - (self.terrain.y_coordinates[x + 4] - self.terrain.y_coordinates[x - 4]) / 8
        # we take slope across (x + 4) px and (x - 4px) to smooth out jerky rotation
        # of the tank when going over curves and to get a more average slope across the width of the tank
        return math.atan(m)