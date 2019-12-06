import pygame

col_screen = 10, 10, 10
col_text = 200, 200, 200
col_fire = 200, 100, 40
col_power = 200, 20, 40
default_angle_val = 60
default_power_val = 50


class ControlPanel:
    def __init__(self, screen: pygame.Surface, cpl_x, cpl_y, cpl_w, cpl_h, control_scale):
        control_img = pygame.image.load(
            "C:\\Data\\Study\\cloud\\___python_game\\partillery\\resources\\images\\control_panel.png").convert()
        self.surf = pygame.transform.scale(control_img, (cpl_w, cpl_h))
        self.rect = self.surf.get_rect()
        self.rect.x = cpl_x
        self.rect.y = cpl_y
        screen.blit(self.surf, (cpl_x, cpl_y))

        # add and draw control elements
        sec_w = cpl_w / 5
        wp_x = sec_w
        angle_x = sec_w * 2
        power_x = sec_w * 3
        fire_x = sec_w * 4
        text_y = self.rect.y + self.rect.h * 0.25
        control_baseline_y = self.rect.y + self.rect.h * 0.4  # setting up a y-axis center line for controls

        # load images
        wp_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\partillery\\resources\\images\\wp_list.png")
        angle_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\partillery\\resources\\images\\param_window.png")
        angle_right_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\partillery\\resources\\images\\inc_button.png")
        angle_left_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\partillery\\resources\\images\\dec_button.png")
        power_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\partillery\\resources\\images\\param_window.png")
        power_bar_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\partillery\\resources\\images\\power_bar.png")
        power_inc_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\partillery\\resources\\images\\inc_button.png")
        power_dec_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\partillery\\resources\\images\\dec_button.png")
        fire_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\partillery\\resources\\images\\param_window.png")
        fire_text_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\partillery\\resources\\images\\fire_text.png")

        # scale images
        wp_surf = scale(wp_img, control_scale)
        angle_left_surf = scale(angle_left_img, control_scale)
        angle_surf = scale(angle_img, control_scale)
        angle_right_surf = scale(angle_right_img, control_scale)
        power_dec_surf = scale(power_dec_img, control_scale)
        power_surf = scale(power_img, control_scale)
        power_inc_surf = scale(power_inc_img, control_scale)
        power_bar_surf = scale(power_bar_img, control_scale)
        fire_surf = scale(fire_img, control_scale)
        fire_text_surf = scale(fire_text_img, control_scale / 1.2)

        # get rects with simple names
        self.wp = wp_surf.get_rect()
        self.angle_left = angle_left_surf.get_rect()
        self.angle_sel = angle_surf.get_rect()
        self.angle_right = angle_right_surf.get_rect()
        self.power_dec = power_dec_surf.get_rect()
        self.power = power_surf.get_rect()
        self.power_inc = power_inc_surf.get_rect()
        self.power_bar = power_bar_surf.get_rect()
        self.fire = fire_surf.get_rect()
        self.fire_text = fire_text_surf.get_rect()

        # set positions
        self.wp.center = (wp_x + angle_x) / 2, control_baseline_y
        self.angle_sel.center = (angle_x + power_x) / 2, control_baseline_y
        self.power.center = (power_x + fire_x) / 2, control_baseline_y
        self.power_bar.center = (power_x + fire_x) / 2, (control_baseline_y + self.rect.bottom) / 2
        self.fire.center = (fire_x + self.rect.right) / 2, (self.rect.y + self.rect.h / 2)
        self.angle_left.center = ((
                                          angle_x + power_x) / 2) - self.angle_left.w / 2 - self.angle_sel.w / 2, control_baseline_y
        self.angle_right.center = ((
                                           angle_x + power_x) / 2) + self.angle_right.w / 2 + self.angle_sel.w / 2, control_baseline_y
        self.power_dec.center = ((power_x + fire_x) / 2) - self.power_dec.w / 2 - self.power.w / 2, control_baseline_y
        self.power_inc.center = ((power_x + fire_x) / 2) + self.power_inc.w / 2 + self.power.w / 2, control_baseline_y

        # control windows

        self.wp_viewer = pygame.Surface((int(self.wp.w * 0.7), int(self.wp.h * 0.5)))
        self.wp_viewer_rect = self.wp_viewer.get_rect()
        self.wp_viewer.fill(col_screen)
        self.wp_viewer_rect.center = self.wp.center

        self.angle_viewer = pygame.Surface((int(self.angle_sel.w * 0.7), int(self.angle_sel.h * 0.5)))
        self.angle_viewer_rect = self.angle_viewer.get_rect()
        self.angle_viewer.fill(col_screen)
        self.angle_viewer_rect.center = self.angle_sel.center

        self.power_viewer = pygame.Surface((int(self.power.w * 0.7), int(self.power.h * 0.5)))
        self.power_viewer_rect = self.power_viewer.get_rect()
        self.power_viewer.fill(col_screen)
        self.power_viewer_rect.center = self.power.center

        self.power_bar_viewer = pygame.Surface((int(self.power_bar.w * 0.8), int(self.power_bar.h * 0.5)))
        self.power_bar_viewer_rect = self.power_bar_viewer.get_rect()
        self.power_bar_viewer_rect.center = self.power_bar.center
        self.power_bar_viewer.fill(col_screen)  # background fill

        # fill area max size and loc
        self.fill_w = int(self.power_bar.w * 0.78)
        self.fill_h = int(self.power_bar.h * 0.44)
        self.fill_x = int(self.power_bar_viewer_rect.x + (self.power_bar_viewer_rect.w - self.fill_w) / 2)
        self.fill_y = int(self.power_bar_viewer_rect.y + (self.power_bar_viewer_rect.h - self.fill_h) / 2)
        self.power_bar_fill_area = pygame.Rect(self.fill_x, self.fill_y, self.fill_w, self.fill_h)  # max area

        # display text
        # font = pygame.font.Font("C:\\WINDOWS\\Fonts\\ARIALN.ttf", 32)
        self.font = pygame.font.SysFont("segoeui", 13, True)

        self.angle_text = self.font.render(str(default_angle_val), True, col_text, col_screen)
        self.angle_text_rect = self.angle_text.get_rect()
        self.angle_text_rect.center = self.angle_viewer_rect.center

        self.power_text = self.font.render(str(default_power_val), True, col_text, col_screen)
        self.power_text_rect = self.power_text.get_rect()
        self.power_text_rect.center = self.power_viewer_rect.center

        self.wp_text = self.font.render("Plain ammo", True, col_text, col_screen)
        self.wp_text_rect = self.wp_text.get_rect()
        self.wp_text_rect.center = self.wp_viewer_rect.center

        '''self.fire_text = self.font.render("Fire", True, col_fire)
        self.fire_text_rect = self.fire_text.get_rect()
        self.fire_text_rect.center = self.fire.center'''
        self.fire_text.center = self.fire.center

        # power_bar_fill_rect = power_bar
        # power_viewer_rect.w = power_viewer_rect.w * 10 / 100
        # power_bar_viewer.fill(col_day)

        # draw control elements
        screen.blits(((wp_surf, self.wp), (angle_surf, self.angle_sel), (power_surf, self.power),
                      (power_bar_surf, self.power_bar),
                      (fire_surf, self.fire),
                      (angle_right_surf, self.angle_right),
                      (angle_left_surf, self.angle_left),
                      (power_inc_surf, self.power_inc),
                      (power_dec_surf, self.power_dec),
                      (self.wp_viewer, self.wp_viewer_rect),
                      (self.angle_viewer, self.angle_viewer_rect),
                      (self.power_viewer, self.power_viewer_rect),
                      (self.power_bar_viewer, self.power_bar_viewer_rect),
                      # (self.power_bar_fill, self.power_bar_fill_rect),
                      (self.angle_text, self.angle_text_rect),
                      (self.power_text, self.power_text_rect),
                      (self.wp_text, self.wp_text_rect),
                      # (self.fire_text, self.fire_text_rect)
                      (fire_text_surf, self.fire_text)
                      ), 0)

        # fill bar at the end
        self.power_bar_fill_rect = pygame.draw.rect(screen, col_power,
                                                    (self.fill_x, self.fill_y,
                                                     int(self.fill_w * (default_power_val / 100)),
                                                     self.fill_h))

    def update_angle(self, screen: pygame.Surface, val):
        self.angle_viewer.fill(col_screen)
        self.angle_text = self.font.render(str(val), True, col_text, col_screen)
        screen.blits(((self.angle_viewer, self.angle_viewer_rect), (self.angle_text, self.angle_text_rect)), 0)

    def update_power(self, screen: pygame.Surface, val):
        self.power_viewer.fill(col_screen)
        self.power_text = self.font.render(str(val), True, col_text, col_screen)
        screen.blits(((self.power_viewer, self.power_viewer_rect), (self.power_text, self.power_text_rect)), 0)
        # redraw power bar fill
        pygame.draw.rect(screen, col_screen, (self.fill_x, self.fill_y, self.fill_w, self.fill_h))
        self.power_bar_fill_rect = pygame.draw.rect(screen, col_power, (self.fill_x, self.fill_y, self.fill_w * (val / 100), self.fill_h))


def scale(surface, scaling_factor):
    rect = surface.get_rect()
    new_w = round(rect.w / scaling_factor)
    new_h = round(rect.h / scaling_factor)
    return pygame.transform.scale(surface, (new_w, new_h))
