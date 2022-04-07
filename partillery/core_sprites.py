import math
from pygame import error, Surface, draw
from pygame.sprite import DirtySprite, Group
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


class Tank(MovableAndRotatableObject):
    def __init__(self, name: str, col: str, turret_angle_degrees: int, th: int, tw: int, pos_x: int,
                 terr_y_coordinates):
        img = 'tank_' + col + '.png'
        MovableAndRotatableObject.__init__(self, img)

        self.name = name
        self.score = 0
        self.power = 50
        self.terr_y_coordinates = terr_y_coordinates
        self.h = th
        self.w = tw

        self.turret_angle = turret_angle_degrees
        self.cross_hair = None
        self.dirty = 0
        self.move_on_terrain(pos_x)

        self.turret = Turret(self.rect.center, th * 1.2, turret_angle_degrees)
        self.cross_hair = CrossHair(self.rect.center, tw * 4, turret_angle_degrees)

        # self.aim = Group(turret, cross_hair)

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

    def update(self, **kwargs):
        super().update()

        if "pos_x" in kwargs:
            self.move_on_terrain(kwargs["pos_x"])

        if "turret_angle_degrees" in kwargs:
            self.turret.set(base=self.rect.center, turret_angle_degrees=kwargs["turret_angle_degrees"])
            self.cross_hair.set(base=self.rect.center, turret_angle_degrees=kwargs["turret_angle_degrees"])

        if "crosshair_visible" in kwargs:
            self.cross_hair.set_visibility(kwargs["crosshair_visible"])


class Turret(DirtySprite):
    # Always set base = tank body center
    # turret will be drawn in a layer behind the tank
    # pass len = tank_h * 1.2

    # To keep the Turret separate from the tank, and be able to use Sprite methods, we give it a dedicated surface
    # which is a square with the diagonal length equal to turret length. (Saved as orig)
    # This will be fully transparent and copied to new every time updated. This copy is set as Sprite.image
    # The turret base will be set to one of the square corners (top left, top right, bottom left, bottom right
    # based on the angle of the turret

    def __init__(self, base, length, degrees):
        super().__init__()
        self.length = length
        diagonal = math.ceil(math.sqrt(2) * length)  # ceiling gives int >= x
        self.base_image = Surface((diagonal, diagonal)).convert_alpha()
        self.base_image.fill((255, 255, 255, 0))  # fully transparent
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        self.visible = 0  # DirtySprite attribute
        self.set(base=base, turret_angle_degrees=degrees, visible=True)

    def update_alt(self, **kwargs):
        super().update()
        nose_x = int(kwargs["base"][0] + (self.length * math.cos(kwargs["degrees"])))
        nose_y = int(kwargs["base"][1] + (self.length * math.sin(kwargs["degrees"])))
        nose = (nose_x, nose_y)
        self.image = self.base_image.copy()
        draw.aaline(self.image, (255, 255, 255), kwargs["base"], nose)
        self.rect = self.image.get_rect()

        if kwargs["degrees"] < 90:
            self.rect.bottomleft = kwargs["base"]
        elif kwargs["degrees"] < 180:
            self.rect.bottomright = kwargs["base"]
        elif kwargs["degrees"] < 270:
            self.rect.topright = kwargs["base"]
        else:
            self.rect.topleft = kwargs["base"]

        if kwargs["visible"] is not None:
            self.visible = kwargs["visible"]

        self.dirty = 1

    def set(self, base, turret_angle_degrees, visible=None):
        nose_x = int(base[0] + (self.length * math.cos(turret_angle_degrees)))
        nose_y = int(base[1] + (self.length * math.sin(turret_angle_degrees)))
        nose = (nose_x, nose_y)
        self.image = self.base_image.copy()
        draw.aaline(self.image, (255, 255, 255), base, nose)
        self.rect = self.image.get_rect()

        if turret_angle_degrees < 90:
            self.rect.bottomleft = base
        elif turret_angle_degrees < 180:
            self.rect.bottomright = base
        elif turret_angle_degrees < 270:
            self.rect.topright = base
        else:
            self.rect.topleft = base

        if visible is not None:
            self.visible = visible

        self.dirty = 1


class CrossHair(DirtySprite):
    def __init__(self, base, distance, degrees):
        super().__init__()
        self.distance = distance
        self.image = utils.load_image_resource('crosshair.png')
        self.rect = self.image.get_rect()
        self.visible = 0  # DirtySprite attribute
        self.set(base=base, turret_angle_degrees=degrees, visible=True)

    def update_alt(self, **kwargs):
        super().update()
        x = int(kwargs["base"][0] + (self.distance * math.cos(kwargs["degrees"])))
        y = int(kwargs["base"][1] + (self.distance * math.sin(kwargs["degrees"])))
        self.rect.center = (x, y)

        if kwargs["visible"] is not None:
            self.visible = kwargs["visible"]

    def set(self, base, turret_angle_degrees, visible):
        x = int(base[0] + (self.distance * math.cos(turret_angle_degrees)))
        y = int(base[1] + (self.distance * math.sin(turret_angle_degrees)))
        self.rect.center = (x, y)

        if visible is not None:
            self.visible = visible

        self.dirty = 1

    def set_visibility(self, visible):
        self.visible = visible
