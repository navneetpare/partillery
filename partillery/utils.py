import math
import pygame
import yaml
from yaml.loader import SafeLoader
import importlib.resources as resources
import partillery
from partillery.resources import images, audio, fonts


# Utility class to convert arbitrary dict / list into an object.
# Adopted from  : https://stackoverflow.com/a/6993694
class Struct(object):
    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return Struct(value) if isinstance(value, dict) else value


def load_image_resource(name):
    image_surface = None
    if resources.is_resource(images, name):
        with resources.path(images, name) as path:
            image_surface = pygame.image.load(path).convert_alpha()
    return image_surface


def play_background_music(name):
    if resources.is_resource(audio, name):
        with resources.path(audio, name) as path:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)  # Continuous loop


def load_font_resource(name, size):
    font = None
    if resources.is_resource(fonts, name):
        with resources.path(fonts, name) as path:
            font = pygame.font.Font(path, size)
    return font


# Returns a config object that can be read as config.a.b.c
def load_config_resource():
    name = "___game_settings.yaml"
    config_yaml = None
    config = None
    if resources.is_resource(partillery, name):
        with resources.path(partillery, name) as path:
            with open(path, 'r') as f:
                config_yaml = yaml.load(f, Loader=SafeLoader)
    config = Struct(config_yaml)
    return config


def get_control_element_names():
    config_yaml = None
    name = "___game_settings.yaml"
    if resources.is_resource(partillery, name):
        with resources.path(partillery, name) as path:
            with open(path, 'r') as f:
                config_yaml = yaml.load(f, Loader=SafeLoader)
    return config_yaml["game_control_panel"]["layout"].keys()


def get_layout_control_group_names():
    config_yaml = None
    name = "___game_settings.yaml"
    if resources.is_resource(partillery, name):
        with resources.path(partillery, name) as path:
            with open(path, 'r') as f:
                config_yaml = yaml.load(f, Loader=SafeLoader)
    return config_yaml["game_control_panel"]["layout"].keys()


def get_slope_radians(terr, x):
    # slope = (y2 - y1) / (x2 - x1)
    m = - (terr.top_layer[x + 1] - terr.top_layer[x])  # ignore div by x2 - x1 which is always 1
    return math.atan(m)


def slope(terr, rect):
    pass


def eraser(source_surf: pygame.Surface, rect: pygame.Rect):
    return source_surf.subsurface(rect).copy()


def scale(surface, scaling_factor):
    rect = surface.get_rect()
    new_w = round(rect.w / scaling_factor)
    new_h = round(rect.h / scaling_factor)
    return pygame.transform.scale(surface, (new_w, new_h))


def clamp(n, lower_bound, upper_bound):
    return max(min(upper_bound, n), lower_bound)


def bell(message: str):
    print(message)
    pass