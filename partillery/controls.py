import pygame
from pygame.sprite import Sprite as Sprite, Group as Group
import partillery.utils as utils


class ControlPanel:
    def __init__(self, screen, x, y, w, h, background_img):
        image = utils.load_image_resource(background_img).convert()
        self.screen = screen
        self.image = pygame.transform.scale(image, (w, h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.build()

    def add(self, control):
        self.screen.blit(control.image, control.rect)

    def build(self):
        power_window = ValueWindow('param_window.png', 15, 100, 50, 0.8, 0.6, 'expressway.ttf', 13)
        power_button = Button('inc_button.png', 15, 200, 50)
        # power = ControlSet(50, power_window, power_button)
        self.add(power_window)
        self.add(power_button)


class ControlSet(Group):
    def __init__(self, value, window=None, buttons=None, bar=None):
        Group.__init__(self)
        self.value = value
        self.window = window
        self.buttons = buttons
        self.bar = bar


class ClickableControl(Sprite):

    def __init__(self, img_name, scaling_factor, x, y):
        Sprite.__init__(self)
        image = utils.load_image_resource(img_name).convert()
        self.image = scale(image, scaling_factor)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, *args):
        pass


class Button(ClickableControl):
    type = None

    def update(self, screen):
        # TODO - Animate on hover / click
        pass


class ValueWindow(ClickableControl):
    def __init__(self, img_name, scaling_factor, x, y, viewer_w_ratio, viewer_h_ratio,
                 font_name, font_size_viewer):
        super().__init__(img_name, scaling_factor, x, y)
        self.rect = self.image.get_rect()
        self.font = utils.load_font_resource(font_name, font_size_viewer)
        self.viewer_w = int(viewer_w_ratio * self.rect.w)
        self.viewer_h = int(viewer_h_ratio * self.rect.h)
        self.viewer = pygame.Surface((self.viewer_w, self.viewer_h))
        self.viewer_rect = self.viewer.get_rect()
        self.viewer_rect.center = self.rect.center

    def draw_viewer(self, val):
        self.viewer.fill(color='0,0,0')
        self.image.blit(self.viewer)
        text = self.font.render(val, True, '255,255,255', '0,0,0')
        text.get_rect().center = self.viewer_rect.center
        self.viewer.blit(text, text.get_rect())

    def update(self, screen, val):
        pass


class ValueBar(ClickableControl):
    def update(self, val):
        pass


def scale(surface, scaling_factor):
    rect = surface.get_rect()
    new_w = round(rect.w / scaling_factor)
    new_h = round(rect.h / scaling_factor)
    return pygame.transform.scale(surface, (new_w, new_h))
