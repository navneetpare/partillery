# References for animating buttons
# https://stackoverflow.com/questions/601776/what-do-the-blend-modes-in-pygame-mean
# https://stackoverflow.com/questions/57962130/how-can-i-change-the-brightness-of-an-image-in-pygame

import pygame
from pygame.sprite import Sprite as DirtySprite, Group as Group

import partillery.utils as utils


class ControlPanel:
    def __init__(self, screen, x, y, w, h, config):
        img_name = config.game_control_panel.background_img
        image = utils.load_image_resource(img_name)
        self.font_name = config.game_control_panel.font_name
        self.font_size_title = config.game_control_panel.font_size_title
        self.font_size_viewer = config.game_control_panel.font_size_viewer
        self.font = utils.load_font_resource(self.font_name, self.font_size_title)
        self.screen = screen
        self.image = pygame.transform.scale(image, (w, h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.controls = Group()

        # Create controls and other elements
        self.build(config)
        self.controls.draw(self.image)
        self.screen.blit(self.image, self.rect)

    # Calculate absolute center coordinates based on relative center
    # Returns a tuple to be used as rect.center
    def set_center(self, pos: tuple):
        x_offset_percent = pos[0]
        y_offset_percent = pos[1]
        x = int(x_offset_percent * self.rect.w)
        y = int(y_offset_percent * self.rect.h)
        return x, y

    def add(self, control):
        self.controls.add(control)
        if control.title is not None:
            x = control.rect.centerx
            y = int(control.rect.top / 2)
            self.draw_title((x, y), str(control.title))
            # Draw the title once and for all. It is not a sprite and won't be updated ever.

    def draw_title(self, pos: tuple, text: str):
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_surf_rect = text_surf.get_rect()
        text_surf_rect.center = pos
        self.image.blit(text_surf, text_surf_rect)
        # print(str(self.surf))

    def build(self, config):
        # Create control items as string objects.
        #   These will be then dynamically created as ClickableControl objects in a loop by reading
        #   their names as strings from the config object using getattr
        #   Saves us writing a lot of object creation boilerplate code.

        ammo_list = 'ammo_list'
        angle_dec = 'angle_dec'
        angle = 'angle'
        angle_inc = 'angle_inc'
        power_dec = 'power_dec'
        power = 'power'
        power_inc = 'power_inc'
        fire = 'fire'
        scoreboard = 'scoreboard'

        controls = (ammo_list, angle_dec, angle, angle_inc, power_dec, power, power_inc, fire, scoreboard)
        img_scale_factor = config.game_control_panel.img_scale_factor

        layout_all = config.game_control_panel.layout

        for item in controls:
            name = item
            layout = getattr(layout_all, name)
            center = self.set_center(layout.pos)
            img_name = layout.img
            title = None

            if hasattr(layout, 'title'):
                title = getattr(layout, 'title')

            item = ClickableControl(name, img_name, img_scale_factor, center, title)

            if hasattr(layout, 'overlay'):
                overlay = getattr(layout, 'overlay')

                if overlay == 'viewer':
                    overlay_w_ratio = layout.overlay_w_ratio
                    overlay_h_ratio = layout.overlay_h_ratio

                    item.overlay = ValueViewer(item.image, overlay_w_ratio, overlay_h_ratio, self.font_name,
                                               self.font_size_viewer, 'Init')
            self.add(item)


# --- Base Class for a clickable item ---
# Handles drawing control background and title, animation on hover / click
# Child element can be a value viewer or a value bar with their own implementations and update mechanisms

class ClickableControl(DirtySprite):
    def __init__(self, name, img_name, img_scale_factor, center, title):
        DirtySprite.__init__(self)
        self.name = name
        self.title = title
        self.overlay = None
        self.clicked = False
        self.hover = False

        self.image = scale(utils.load_image_resource(img_name), img_scale_factor)

        # Brightened image to show animation on hover
        self.image_animate = self.image.copy()
        self.image_animate.fill((10, 10, 10), special_flags=pygame.BLEND_RGB_SUB)

        # self.surf = self.image
        self.rect = self.image.get_rect()
        self.rect.center = center

    def animate(self):
        pass

    def update(self, *args):
        self.animate()
        if self.overlay is not None:
            self.overlay.update()


class ValueViewer:
    def __init__(self, parent_surface: pygame.Surface, w_ratio, h_ratio, font_name, font_size, text):
        super().__init__()
        self.font = utils.load_font_resource(font_name, font_size)
        self.rect = parent_surface.get_rect().copy()
        w_reduction = int(self.rect.w * (w_ratio - 1))
        h_reduction = int(self.rect.h * (h_ratio - 1))
        self.rect.inflate_ip(w_reduction, h_reduction)
        self.surf = parent_surface.subsurface(self.rect)
        # print('viewer center ' + str(self.rect.center))
        self.update(text)

    def update(self, text):
        self.surf.fill((0, 0, 0))
        text_surf = self.font.render(text, True, (255, 255, 255), (0, 0, 0))
        text_surf_rect = text_surf.get_rect()
        # We take relative center of the viewer instead of absolute position
        # Because we will blit to viewer surf instead of screen.
        text_surf_rect.center = (self.rect.w / 2, self.rect.h / 2)
        self.surf.blit(text_surf, text_surf_rect)


class ValueBar(ClickableControl):
    def update(self, val):
        pass


def scale(surface, scaling_factor):
    rect = surface.get_rect()
    new_w = round(rect.w / scaling_factor)
    new_h = round(rect.h / scaling_factor)
    return pygame.transform.scale(surface, (new_w, new_h))
