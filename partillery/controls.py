# References for animating buttons
# https://stackoverflow.com/questions/601776/what-do-the-blend-modes-in-pygame-mean
# https://stackoverflow.com/questions/57962130/how-can-i-change-the-brightness-of-an-image-in-pygame

import pygame
from pygame import Surface
from pygame.sprite import DirtySprite, LayeredDirty, Sprite

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
        self.elements = LayeredDirty()  # For drawing updates
        self.controls = LayeredDirty()  # Only add interactive elements

        # Create controls and other elements
        self.screen.blit(self.image, self.rect)

        # Create objects and adds them to elements list. Also adds controls as direct ControlPanel attributes
        # e.g. cpl.power_bar
        self.build(config)
        self.elements.draw(self.screen)

    # Calculate absolute center coordinates based on relative center
    # Returns a tuple to be used as rect.center
    def set_center(self, pos: tuple):
        x_offset_percent = pos[0]
        y_offset_percent = pos[1]
        x = int(x_offset_percent * self.rect.w)
        y = int(y_offset_percent * self.rect.h + self.rect.top)
        return x, y

    def add(self, control):
        self.elements.add(control)
        if control.overlay is not None:
            self.elements.add(getattr(control, 'overlay'))
        if "angle" in control.name or "power" in control.name or control.name == "ammo_list":
            self.controls.add(control)

        setattr(self, control.name, control)
        if control.title is not None:
            x = control.rect.centerx
            y = int((control.rect.top + self.rect.top) / 2)
            self.draw_title((x, y), str(control.title))
            # Draw the title once and for all. It is not a sprite and won't be updated ever.

    def draw_title(self, pos: tuple, text: str):
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_surf_rect = text_surf.get_rect()
        text_surf_rect.center = pos
        self.screen.blit(text_surf, text_surf_rect)
        pygame.display.update()

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

        # controls = (ammo_list, angle_dec, angle, angle_inc, power_dec, power, power_inc, fire, scoreboard)
        img_scale_factor = config.game_control_panel.img_scale_factor

        layout_all = config.game_control_panel.layout

        controls = utils.get_control_element_names()
        print(type(controls))
        for item in controls:
            print(item)
            print(type(item))

        for item in controls:
            name = item
            layout = getattr(layout_all, name)
            center = self.set_center(layout.pos)
            img_name = layout.img
            img_name_hover = layout.img_hover
            title = None

            if hasattr(layout, 'title'):
                title = getattr(layout, 'title')

            item = ClickableControl(self, name, img_name, img_name_hover, img_scale_factor, center, title)

            if hasattr(layout, 'overlay'):
                overlay = getattr(layout, 'overlay')

                if overlay == 'viewer':
                    overlay_w_ratio = layout.overlay_w_ratio
                    overlay_h_ratio = layout.overlay_h_ratio

                    item.overlay = ValueViewer(item.image, overlay_w_ratio, overlay_h_ratio, self.font_name,
                                               self.font_size_viewer)
            self.add(item)


# --- Base Class for a clickable item ---
# Handles drawing control background and title, animation on hover / click
# Child element can be a value viewer or a value bar with their own implementations and update mechanisms

class ClickableControl(DirtySprite):
    def __init__(self, control_panel, name, img_name, img_name_hover, img_scale_factor, center, title):
        DirtySprite.__init__(self)
        self.control_panel = control_panel  # Reference parent for updating text on viewers etc.
        self.name = name
        self.title = title
        self.overlay = None
        self.dirty = 1
        self.visible = 1
        self._layer = 0

        self.image_regular = scale(utils.load_image_resource(img_name), img_scale_factor)
        self.image_hover = scale(utils.load_image_resource(img_name_hover), img_scale_factor)
        self.image = self.image_regular

        # Brightened image to show animation on hover
        # self.image_hover = self.image.copy()
        # self.image_hover.fill((20, 20, 20), special_flags=pygame.BLEND_RGB_SUB)

        # self.surf = self.image
        self.rect = self.image.get_rect()
        self.rect.center = center

    def hover_on(self):
        self.image = self.image_hover
        self.dirty = 1

    def hover_off(self):
        self.image = self.image_regular
        self.dirty = 1

    def animate_click(self):
        self.rect.centery += 2  # animate button depression
        self.dirty = 1

    def de_animate_click(self):
        self.rect.centery -= 2  # un-animate button depression
        self.dirty = 1

    def click_down(self, current_player):
        lock_mouse_to_control = False
        if self.name in ['angle', 'power', 'power_bar', 'ammo_list']:
            lock_mouse_to_control = True
        else:
            self.animate_click()
        return lock_mouse_to_control

    def click_up(self, actuate: bool, current_player):
        if self.name in ['angle', 'power', 'power_bar', 'ammo_list']:
            pass
        elif actuate:
            self.de_animate_click()
            if self.name == 'angle_dec':
                angle = current_player.angle - 1
                if angle < 0:
                    angle = 359
                self.control_panel.angle.overlay.update(angle)
                current_player.update(angle=angle)
            elif self.name == 'angle_inc':
                angle = current_player.angle + 1
                if angle == 360:
                    angle = 0
                self.control_panel.angle.overlay.update(angle)
                current_player.update(angle=angle)
            elif self.name == 'power_dec':
                power = current_player.power - 1
                if power < 0:
                    power = 0
                self.control_panel.power.overlay.update(power)
                current_player.power = power
            elif self.name == 'power_inc':
                power = current_player.power + 1
                if power > 100:
                    power = 100
                self.control_panel.power.overlay.update(power)
                current_player.power = power
        else:
            self.de_animate_click()


class ValueViewer(DirtySprite):
    def __init__(self, parent_surface: Surface, w_ratio, h_ratio, font_name, font_size):
        DirtySprite.__init__(self)
        self.font = utils.load_font_resource(font_name, font_size)
        self.rect = parent_surface.get_rect().copy()
        w_reduction = int(self.rect.w * (w_ratio - 1))
        h_reduction = int(self.rect.h * (h_ratio - 1))
        self.rect.inflate_ip(w_reduction, h_reduction)
        self.image = parent_surface.subsurface(self.rect)
        self.update("")
        self._layer = 1
        self.dirty = 1

    def update(self, text):
        self.image.fill((0, 0, 0))
        text_surf = self.font.render(str(text), True, (255, 255, 255), (0, 0, 0))
        text_surf_rect = text_surf.get_rect()
        # We take relative center of the viewer instead of absolute position
        # Because we will blit to viewer surf instead of screen.
        text_surf_rect.center = (self.rect.w / 2, self.rect.h / 2)
        self.image.blit(text_surf, text_surf_rect)
        self.dirty = 1


class ValueBar(ClickableControl):
    def update(self, val):
        pass


class Mouse(Sprite):
    # Pseudo-sprite that is not drawn. Only to get collisions with controls.
    def __init__(self, center):
        super().__init__()
        self.image = Surface((1, 1)).convert_alpha()
        self.image.fill((255, 255, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.prev_focused_control = None  # Used for deactivating hover animation
        self.clicked_control = None
        self.locked = False
        self.saved_pos = None


def scale(surface, scaling_factor):
    rect = surface.get_rect()
    new_w = round(rect.w / scaling_factor)
    new_h = round(rect.h / scaling_factor)
    return pygame.transform.scale(surface, (new_w, new_h))
