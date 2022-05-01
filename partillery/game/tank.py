import math

from pygame import Surface, draw
from pygame.rect import Rect
from pygame.sprite import DirtySprite

from partillery import utils
from partillery.game.base_classes.base_element import BaseElement
from partillery.game.terrain import Terrain


class Tank(BaseElement):
    def __init__(self, name: str, col: str, angle: int, terrain: Terrain, game_rect):
        img = 'tank_' + col + '.png'
        BaseElement.__init__(self, terrain, img)
        self.w = self.rect.w
        self.h = self.rect.h
        self.moves_left = 4
        self.move_direction = 1  # -1 == left, +1 = right
        self.game_rect = game_rect
        self.top_clamp = game_rect.top
        self.name = name
        self.score = 0
        self.power = 50
        self.angle = angle
        self.dirty = 2
        self.turret = Turret(self)
        self.crosshair = CrossHair(self)
        self.selected_weapon = "Plain bomb"

    '''def get_center_above_terrain(self, x, angle_rads):
        y = self.terr_y_coordinates[x]
        x1 = int(self.h / 2 * math.cos(angle_rads + math.pi / 2) + x)
        y1 = int(-(self.h  / 2) * math.sin(angle_rads + math.pi / 2) + y)
        return x1, y1

    def get_slope_rads(self, x):
        # slope = (y2 - y1) / (x2 - x1)
        m = - (self.terr_y_coordinates[x + 4] - self.terr_y_coordinates[x - 4]) / 8
        # we take slope across (x + 4) px and (x - 4px) to smooth out jerky rotation
        # of the tank when going over curves and to get a more average slope across the width of the tank
        return math.atan(m)

    def roll_on_terrain(self, pos_x):
        terrain_slope = self.get_slope_rads(pos_x)
        pos = self.get_center_above_terrain(pos_x, terrain_slope)
        self.move(pos)
        self.rotate(terrain_slope)'''

    def update(self, **kwargs):
        super().update()

        if "pos_x" in kwargs:
            self.roll_on_terrain(kwargs["pos_x"])
            self.turret.update()
            self.crosshair.update()

        if "angle" in kwargs:
            self.angle = kwargs["angle"]
            self.turret.update()
            self.crosshair.update()


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
        self.dirty = 0
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
        self.dirty = 1


class CrossHair(DirtySprite):
    def __init__(self, tank):
        super().__init__()
        # We give it a dedicated surface w = h = tw (saved as orig)
        # This will be fully transparent and copied to new every time updated. To be centered with the tank.
        self.tank = tank  # Refer to parent for easy access
        self.distance = self.tank.w * 3
        self.image = utils.load_image_resource('crosshair.png')
        self.rect = self.image.get_rect()
        w = self.rect.w  # w = h for cross-hair, so we'll reuse it.
        # Define area where cross-hair can move. Half width to be cropped out of game area.
        self.clip_rect = Rect(self.tank.game_rect.left + w / 2, self.tank.game_rect.top + w / 2,
                              self.tank.game_rect.w - w, self.tank.game_rect.h - w)
        self.visible = 0
        self.dirty = 0

    def update(self):
        angle_radians = math.radians(self.tank.angle)
        x = self.tank.rect.centerx + (self.distance * math.cos(angle_radians))
        y = self.tank.rect.centery - (self.distance * math.sin(angle_radians))
        # x = utils.clamp(x, self.tank.game_rect.left + self.tank.w / 2, self.tank.game_rect.right - self.tank.w /2)
        # y = utils.clamp(y, self.tank.game_rect.top, self.tank.game_rect.bottom)
        clipped = self.clip_rect.clipline(self.tank.rect.center, (x, y))
        if not clipped:
            self.rect.center = x, y
        else:
            self.rect.center = clipped[1]
        self.dirty = 1
