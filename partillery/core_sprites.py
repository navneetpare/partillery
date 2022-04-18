import math

from pygame import error, Surface, draw
from pygame.rect import Rect
from pygame.sprite import DirtySprite
from pygame.transform import rotate

from partillery import utils


# The background will be used for eraser.
# The background will comprise of the sky + the terrain. It may be updated by explosions and other events
# so we don't copy it but refer to it here. Python passes vars by ref.
# The logic to update the background will be in the main game context.

class MovableAndRotatableObject(DirtySprite):
    def __init__(self, img):
        DirtySprite.__init__(self)
        self.image = utils.load_image_resource(img)
        self.image_original = self.image.copy()
        self.rect = self.image.get_rect()
        self.dirty = 0

    # In-place rotation
    def rotate_ip(self, rads):
        # self.erase()
        try:
            # The rotation is absolute, not relative, so we use the stored original image
            # Also the original image is located at (0, 0) so it must be moved back to loc.
            center = self.rect.center
            self.image = rotate(self.image_original, math.degrees(rads))
            self.rect = self.image.get_rect()
            self.rect.center = center
        except error:
            utils.bell('Cannot rotate')
            pass

    def move(self, pos: tuple):
        try:
            self.rect.center = pos
        except error:
            utils.bell('Cannot move')

    def bounce(self, self_vector, target_vector):
        pass


class Tank(MovableAndRotatableObject):
    def __init__(self, name: str, col: str, turret_angle_degrees: int, th: int, tw: int, pos_x: int,
                 terr_y_coordinates, game_rect):
        img = 'tank_' + col + '.png'
        MovableAndRotatableObject.__init__(self, img)
        self.game_rect = game_rect
        self.top_clamp = game_rect.top
        self.name = name
        self.score = 0
        self.power = 0
        self.turret_angle = math.radians(turret_angle_degrees)
        print('Angle : ' + str(turret_angle_degrees) + ' ' + str(self.turret_angle))
        self.terr_y_coordinates = terr_y_coordinates
        self.h = th
        self.w = tw
        self.dirty = 2
        self.turret = Turret(self)
        self.cross_hair = CrossHair(self)
        # Set initial position
        self.update(pos_x=pos_x)

    def get_center_above_terrain(self, x, angle_rads):
        y = self.terr_y_coordinates[x]
        x1 = int(self.h / 2 * math.cos(angle_rads + math.pi / 2) + x)
        y1 = int(-(self.h / 2) * math.sin(angle_rads + math.pi / 2) + y)
        return x1, y1

    def get_slope_rads(self, x):
        # slope = (y2 - y1) / (x2 - x1)
        m = - (self.terr_y_coordinates[x + 4] - self.terr_y_coordinates[x - 4]) / 8
        # we take slope across (x + 4) px and (x - 4px) to smooth out jerky rotation
        # of the tank when going over curves and to get a more average slope across the width of the tank
        return math.atan(m)

    def move_on_terrain(self, pos_x):
        terrain_slope = self.get_slope_rads(pos_x)
        pos = self.get_center_above_terrain(pos_x, terrain_slope)
        self.move(pos)
        self.rotate_ip(terrain_slope)
        self.turret.update()
        self.cross_hair.update()

    def update_angle(self, turret_angle):
        self.turret_angle = math.radians(turret_angle)

    def update(self, **kwargs):
        super().update()

        if "pos_x" in kwargs:
            self.move_on_terrain(kwargs["pos_x"])

        if "turret_angle_degrees" in kwargs:
            self.update_angle(kwargs["turret_angle_degrees"])


class Turret(DirtySprite):
    def __init__(self, tank):
        super().__init__()
        # We give it a dedicated surface w = h = tw (saved as orig)
        # This will be fully transparent and copied to new every time updated. To be centered with the tank.
        self.tank = tank  # Refer to parent for easy access
        self.len = self.tank.w
        self.bg = Surface((self.len, self.len)).convert_alpha()
        self.bg.fill((255, 255, 255, 0))  # fully transparent
        self.image = None
        self.rect = None
        self.nose = None
        self.visible = 1
        self.dirty = 2
        self.update()

    def get_nose(self):
        x = (self.rect.w / 2) + (self.len * math.cos(self.tank.turret_angle))
        y = (self.rect.h / 2) - (self.len * math.sin(self.tank.turret_angle))
        return x, y

    def update(self):
        # Not to be called before tank.update
        self.image = self.bg.copy()
        self.rect = self.image.get_rect()
        self.rect.center = self.tank.rect.center
        self.nose = self.get_nose()
        draw.line(self.image, (255, 255, 255, 255), (self.rect.w / 2, self.rect.h / 2), self.nose, 2)


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
        self.visible = 1
        self.dirty = 2

    def update(self):

        x = self.tank.rect.centerx + (self.distance * math.cos(self.tank.turret_angle))
        y = self.tank.rect.centery - (self.distance * math.sin(self.tank.turret_angle))
        # x = utils.clamp(x, self.tank.game_rect.left + self.tank.w / 2, self.tank.game_rect.right - self.tank.w /2)
        # y = utils.clamp(y, self.tank.game_rect.top, self.tank.game_rect.bottom)
        clipped = self.clip_rect.clipline(self.tank.rect.center, (x, y))
        if not clipped:
            self.rect.center = x, y
        else:
            self.rect.center = clipped[1]
