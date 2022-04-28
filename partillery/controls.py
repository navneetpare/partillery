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
        # self.elements.draw(self.screen)

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
        if control.clickable:
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
        #   Create control items as string objects from config
        #   These will be then dynamically created as 'Control' objects in a loop by reading
        #   their names as strings from the config object using getattr
        #   Saves us writing a lot of object creation boilerplate code.
        img_scale_factor = config.game_control_panel.img_scale_factor
        layout_all = config.game_control_panel.layout
        controls = utils.get_control_element_names()

        for item in controls:
            print(item)
            print(type(item))

        for item in controls:
            name = item
            layout = getattr(layout_all, name)
            clickable = getattr(layout, 'clickable')
            can_lock_mouse = getattr(layout, 'can_lock_mouse')
            center = self.set_center(layout.pos)
            img_name = layout.img
            img_name_hover = layout.img_hover
            title = None

            if hasattr(layout, 'title'):
                title = getattr(layout, 'title')

            item = Control(self, name, clickable, can_lock_mouse, img_name,
                           img_name_hover, img_scale_factor, center, title)

            if hasattr(layout, 'overlay'):
                overlay = getattr(layout, 'overlay')

                if overlay == 'viewer':
                    overlay_w_ratio = layout.overlay_w_ratio
                    overlay_h_ratio = layout.overlay_h_ratio
                    overlay_x_offset = layout.overlay_x_offset
                    overlay_y_offset = layout.overlay_y_offset

                    item.overlay = Viewer(item.rect, overlay_w_ratio, overlay_h_ratio, self.font_name,
                                          self.font_size_viewer, overlay_x_offset, overlay_y_offset)
                elif overlay == 'value_bar':
                    overlay_w_ratio = layout.overlay_w_ratio
                    overlay_h_ratio = layout.overlay_h_ratio
                    overlay_x_offset = layout.overlay_x_offset
                    overlay_y_offset = layout.overlay_y_offset

                    item.overlay = ValueBar(item.rect, overlay_w_ratio, overlay_h_ratio, overlay_x_offset,
                                            overlay_y_offset)
            self.add(item)

    def update_power(self, val):
        getattr(self, 'viewer_power').update_value(val)
        getattr(self, 'power_bar').update_value(val)

    def update_angle(self, val):
        getattr(self, 'viewer_angle').update_value(val)

    def update_weapon(self, name):
        getattr(self, 'weapons_list').update_value("Plain bomb")


# --- Base Class for a clickable item ---
# Handles drawing control background and title, animation on hover / click
# Child element can be a value viewer or a value bar with their own implementations and update mechanisms


class Control(DirtySprite):
    def __init__(self, control_panel, name, clickable, can_lock_mouse,
                 img_name, img_name_hover, img_scale_factor, center, title):
        DirtySprite.__init__(self)
        self.control_panel = control_panel  # Reference parent for updating text on viewers etc.
        self.name = name
        self.clickable = clickable
        self.can_lock_mouse = can_lock_mouse
        self.saved_mouse_pos = None
        self.title = title
        self.overlay = None
        self.dirty = 1
        self.visible = 1
        self._layer = 0

        self.image_regular = scale(utils.load_image_resource(img_name), img_scale_factor)
        self.image_hover = scale(utils.load_image_resource(img_name_hover), img_scale_factor)
        self.image = self.image_regular

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

    def click_down(self, current_player, pos):
        lock_mouse_to_control = False
        if self.can_lock_mouse:
            lock_mouse_to_control = True
            if self.name == 'power_bar':
                self.overlay.handle_click_down()
            elif self.name == 'button_angle':
                self.saved_mouse_pos = pos
                # Temporarily set mouse (which is hidden at this point) to the center of the control panel
                # to allow flexibility to move mouse either side.
                pygame.mouse.set_pos(self.control_panel.rect.center)
        else:
            self.animate_click()
        return lock_mouse_to_control

    def click_up(self, actuate: bool, current_player):
        if (not self.can_lock_mouse) and actuate:
            self.de_animate_click()
            if self.name == 'button_angle_right':
                angle = current_player.angle - 1
                if angle < 0:
                    angle = 359
                self.control_panel.viewer_angle.overlay.update(angle)
                current_player.update(angle=angle)
            elif self.name == 'button_angle_left':
                angle = current_player.angle + 1
                if angle == 360:
                    angle = 0
                self.control_panel.viewer_angle.overlay.update(angle)
                current_player.update(angle=angle)
            elif self.name == 'button_power_dec':
                power = current_player.power - 1
                if power < 0:
                    power = 0
                self.control_panel.update_power(power)
                current_player.power = power
            elif self.name == 'button_power_inc':
                power = current_player.power + 1
                if power > 100:
                    power = 100
                self.control_panel.update_power(power)
                current_player.power = power

    def update_value(self, val):
        self.overlay.update(val)

    def handle_mouse_move(self, current_player, pos):
        if self.name == 'power_bar':
            val = int((utils.clamp(pos[0], self.overlay.rect.left,
                                   self.overlay.rect.right) - self.overlay.rect.left) * 100 / self.overlay.rect.w)
            self.control_panel.update_power(val)
            current_player.power = val
        elif self.name == 'button_angle':
            # We move the turret / angle based on mouse X-movement. The computation starts upon 'click_down' where
            # position is saved. The 'MOUSEMOVE' event pos is continuously compared to the previous saved position.
            pygame.event.set_blocked(pygame.MOUSEMOTION)

            angle = int((self.saved_mouse_pos[0] - pos[0]) / 2) + current_player.angle
            if angle > 359:
                angle -= 360
            elif angle < 0:
                angle += 360
            elif angle == 360:
                angle = 0
            self.control_panel.update_angle(angle)
            current_player.update(angle=angle)

            self.saved_mouse_pos = pos
            pygame.event.set_allowed(pygame.MOUSEMOTION)


class Viewer(DirtySprite):
    def __init__(self, parent_rect, w_ratio, h_ratio, font_name, font_size, x_offset=0, y_offset=0):
        DirtySprite.__init__(self)
        w = w_ratio * parent_rect.w
        h = h_ratio * parent_rect.h
        self.font = utils.load_font_resource(font_name, font_size)
        self.image = Surface((w, h))
        self.rect = self.image.get_rect()
        self.rect.center = parent_rect.center
        self.rect.centerx += ((x_offset / 2) * parent_rect.w)
        self.rect.centery += ((y_offset / 2) * parent_rect.h)
        self.update("")
        self._layer = 0

    def update(self, text):
        self.image.fill((0, 0, 0))
        text_surf = self.font.render(str(text), True, (255, 255, 255), (0, 0, 0))
        text_surf_rect = text_surf.get_rect()
        # We take relative center of the viewer instead of absolute position
        # Because we will blit to viewer surf instead of screen.
        text_surf_rect.center = (self.rect.w / 2, self.rect.h / 2)
        self.image.blit(text_surf, text_surf_rect)
        self.dirty = 1

    def handle_click_down(self):
        pass


class ValueBar(DirtySprite):
    def __init__(self, parent_rect, w_ratio, h_ratio, x_offset=0, y_offset=0):
        DirtySprite.__init__(self)
        w = w_ratio * parent_rect.w
        h = h_ratio * parent_rect.h
        self.image = Surface((w, h))
        self.rect = self.image.get_rect()
        self.rect.center = parent_rect.center
        self.rect.centerx += ((x_offset / 2) * parent_rect.w)
        self.rect.centery += ((y_offset / 2) * parent_rect.h)
        self.current_fill_w = 0
        self._layer = 0
        self.update(50)

    def handle_click_down(self):
        pygame.mouse.set_pos(self.rect.left + self.current_fill_w, self.rect.top)

    def update(self, val):
        self.image.fill((0, 0, 0))
        self.current_fill_w = int((self.rect.w * val) / 100)
        pygame.draw.rect(self.image, (210, 0, 40), (0, 0, self.current_fill_w, self.rect.h))
        self.dirty = 1


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
