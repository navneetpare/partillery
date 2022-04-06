import math

# from pygame import Vector2
from pygame.sprite import DirtySprite
from pygame.transform import rotate
from pygame import error
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
    def rotate_ip(self, radians):
        # self.erase()
        try:
            # The rotation is absolute, not relative, so we use the stored original image
            # Also the original image is located at (0, 0) so it must be moved back to loc.
            center = self.rect.center
            self.image = rotate(self.image_original, math.degrees(radians))
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


class TankBody(MovableAndRotatableObject):
    def __init__(self, col, th, tw, pos_x, turret_angle, power, terr_y_coordinates):
        img = 'tank_' + col + '.png'
        MovableAndRotatableObject.__init__(self, img)

        self.terr_y_coordinates = terr_y_coordinates
        self.h = th
        self.w = tw
        self.power = power
        self.turret = None
        self.turret_angle = turret_angle
        self.cross_hair = None
        self.dirty = 0

        self.move_on_terrain(pos_x)
        print('Tank Created')
        print(self.rect)

    def get_center(self, x, angle_radians):
        y = self.terr_y_coordinates[x]
        x1 = int(self.h / 2 * math.cos(angle_radians + math.pi / 2) + x)
        y1 = int(-(self.h / 2) * math.sin(angle_radians + math.pi / 2) + y)
        return x1, y1

    def get_slope_radians(self, x):
        # slope = (y2 - y1) / (x2 - x1)
        m = - (self.terr_y_coordinates[x + 4] - self.terr_y_coordinates[x - 4]) / 8
        # we take slope across (x + 4) px and (x - 4px) to smooth out jerky rotation
        # of the tank when going over curves and to get a more average slope across the width of the tank
        return math.atan(m)

    def move_on_terrain(self, pos_x):
        slope = self.get_slope_radians(pos_x)
        pos = self.get_center(pos_x, slope)
        self.move(pos)
        self.rotate_ip(slope)
        self.dirty = 1
        print('Debug - Move on Terrain')
        print('--------------------------')
        print('pos_x: ' + str(pos_x))
        print('slope: ' + str(slope))
        print('slope_deg: ' + str(math.degrees(slope)))
        print('target_center: ' + str(pos))
        print('actual_center: ' + str(self.rect.center))
