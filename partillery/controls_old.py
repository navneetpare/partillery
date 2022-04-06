import pygame

col_screen = 10, 10, 10
col_text_white = 230, 230, 230
# col_text_yellow = 210, 196, 62
# col_text_yellow = 255, 255, 128
col_heading = 255, 210, 150
col_fire = 200, 100, 40
col_power = 200, 20, 40
default_angle_val = 60
default_power_val = 50


class ControlPanel:
    def __init__(self, screen: pygame.Surface, cpl_x, cpl_y, cpl_w, cpl_h, control_scale):

        control_img = pygame.image.load("resources/images/control_panel.png").convert()
        self.surf = pygame.transform.scale(control_img, (cpl_w, cpl_h))
        self.rect = self.surf.get_rect()
        self.rect.x = cpl_x
        self.rect.y = cpl_y
        screen.blit(self.surf, (cpl_x, cpl_y))

        # add and draw control elements


        '''sec_w = cpl_w / 5
        wp_x = sec_w
        angle_x = sec_w * 2
        power_x = sec_w * 3
        fire_x = sec_w * 4 '''

        w1 = cpl_w / 5
        rw = cpl_w - w1
        sec_w = rw / 5
        wp_x = w1
        angle_x = w1 + sec_w
        power_x = w1 + sec_w * 2
        fire_x = w1 + sec_w * 3

        control_baseline_y = self.rect.y + self.rect.h * 0.45  # setting up a y-axis center line for controls

        # create surfaces

        wp_img = pygame.image.load("resources/images/ammo_list.png")
        angle_img = pygame.image.load("resources/images/param_window.png")
        angle_dec_img = pygame.image.load("resources/images/button_inc.png")
        angle_inc_img = pygame.image.load("resources/images/button_dec.png")
        power_img = pygame.image.load("resources/images/param_window.png")
        power_bar_img = pygame.image.load("resources/images/power_bar.png")
        power_inc_img = pygame.image.load("resources/images/button_inc.png")
        power_dec_img = pygame.image.load("resources/images/button_dec.png")
        fire_img = pygame.image.load("resources/images/param_window.png")
        fire_text_img = pygame.image.load("resources/images/fire_text.png")
        scoreboard_frame = pygame.image.load("resources/images/scoreboard_frame.png")

        # scale surfaces

        wp_surf = scale(wp_img, control_scale)
        angle_inc_surf = scale(angle_inc_img, control_scale)
        angle_surf = scale(angle_img, control_scale)
        angle_dec_surf = scale(angle_dec_img, control_scale)
        power_dec_surf = scale(power_dec_img, control_scale)
        power_surf = scale(power_img, control_scale)
        power_inc_surf = scale(power_inc_img, control_scale)
        power_bar_surf = scale(power_bar_img, control_scale)
        fire_surf = scale(fire_img, control_scale)
        fire_text_surf = scale(fire_text_img, control_scale / 1.2)
        scoreboard_frame_surf = scale(scoreboard_frame, control_scale)

        # get rects with simple names

        self.wp = wp_surf.get_rect()
        self.angle_inc = angle_inc_surf.get_rect()
        self.angle_sel = angle_surf.get_rect()
        self.angle_dec = angle_dec_surf.get_rect()
        self.power_dec = power_dec_surf.get_rect()
        self.power = power_surf.get_rect()
        self.power_inc = power_inc_surf.get_rect()
        self.power_bar = power_bar_surf.get_rect()
        self.fire = fire_surf.get_rect()
        self.fire_text = fire_text_surf.get_rect()
        self.scoreboard = scoreboard_frame_surf.get_rect()

        # set positions

        self.wp.center = (wp_x + angle_x) / 2, control_baseline_y
        self.angle_sel.center = (angle_x + power_x) / 2, control_baseline_y
        self.power.center = (power_x + fire_x) / 2, control_baseline_y
        # self.power_bar.center = (power_x + fire_x) / 2, (control_baseline_y + self.rect.bottom) / 2
        # The 0.995 to place bar is irritating; need to fix
        self.power_bar.center = (power_x + fire_x) / 2, 0.995*(self.power.bottom + self.rect.bottom) / 2
        self.angle_inc.center = ((angle_x + power_x) / 2) - self.angle_inc.w / 4 - self.angle_sel.w / 2, control_baseline_y
        self.angle_dec.center = ((angle_x + power_x) / 2) + self.angle_dec.w / 4 + self.angle_sel.w / 2, control_baseline_y
        self.power_dec.center = ((power_x + fire_x) / 2) - self.power_dec.w / 4 - self.power.w / 2, control_baseline_y
        self.power_inc.center = ((power_x + fire_x) / 2) + self.power_inc.w / 4 + self.power.w / 2, control_baseline_y
        self.fire.center = (fire_x + (fire_x + sec_w)) / 2, (self.rect.y + self.rect.h / 2)
        self.fire_text.center = self.fire.center
        self.scoreboard.center = (self.fire.centerx + sec_w, self.rect.centery)

        # control windows

        self.wp_viewer = pygame.Surface((int(self.wp.w * 0.8), int(self.wp.h * 0.6)))
        self.wp_viewer_rect = self.wp_viewer.get_rect()
        self.wp_viewer.fill(col_screen)
        self.wp_viewer_rect.center = self.wp.center

        self.angle_viewer = pygame.Surface((int(self.angle_sel.w * 0.65), int(self.angle_sel.h * 0.6)))
        self.angle_viewer_rect = self.angle_viewer.get_rect()
        self.angle_viewer.fill(col_screen)
        self.angle_viewer_rect.center = self.angle_sel.center

        self.power_viewer = pygame.Surface((int(self.power.w * 0.65), int(self.power.h * 0.6)))
        self.power_viewer_rect = self.power_viewer.get_rect()
        self.power_viewer.fill(col_screen)
        self.power_viewer_rect.center = self.power.center

        self.power_bar_viewer = pygame.Surface((int(self.power_bar.w * 0.8), int(self.power_bar.h * 0.6)))
        self.power_bar_viewer_rect = self.power_bar_viewer.get_rect()
        self.power_bar_viewer_rect.center = self.power_bar.center
        self.power_bar_viewer.fill(col_screen)

        self.score_viewer = pygame.Surface((int(self.scoreboard.w * 0.8), int(self.scoreboard.h * 0.76)))
        self.score_viewer_rect = self.score_viewer.get_rect()
        self.score_viewer_rect.center = (self.scoreboard.centerx + 1, self.scoreboard.centery + 1)
        self.score_viewer.fill(col_screen)

        # scoreboard_surf.fill(col_screen)

        # fill area max size and loc

        self.fill_w = int(self.power_bar.w * 0.78)
        self.fill_h = int(self.power_bar.h * 0.44)
        self.fill_x = int(self.power_bar_viewer_rect.x + (self.power_bar_viewer_rect.w - self.fill_w) / 2)
        self.fill_y = int(self.power_bar_viewer_rect.y + (self.power_bar_viewer_rect.h - self.fill_h) / 2)
        self.power_bar_fill_area = pygame.Rect(self.fill_x, self.fill_y, self.fill_w, self.fill_h)  # max area

        # display text
        # self.font_param = pygame.font.SysFont("segoeui", 13, True)
        self.font_param = pygame.font.Font("resources/fonts/expressway.ttf", 13)
        # self.font_heading = pygame.font.SysFont("comicsansms", 16, True)
        self.font_heading = pygame.font.Font("resources/fonts/expressway.ttf", 15)

        self.angle_text = self.font_param.render(str(default_angle_val), True, col_text_white, col_screen)
        self.angle_text_rect = self.angle_text.get_rect()
        self.angle_text_rect.center = self.angle_viewer_rect.center

        self.angle_heading = self.font_heading.render("Angle", True, col_text_white)
        self.angle_heading_rect = self.angle_heading.get_rect()
        self.angle_heading_rect.center = (self.angle_viewer_rect.centerx, (self.angle_viewer_rect.top + self.rect.top) / 2)

        self.power_text = self.font_param.render(str(default_power_val), True, col_text_white, col_screen)
        self.power_text_rect = self.power_text.get_rect()
        self.power_text_rect.center = self.power_viewer_rect.center

        self.power_heading = self.font_heading.render("Power", True, col_text_white)
        self.power_heading_rect = self.power_heading.get_rect()
        self.power_heading_rect.center = (self.power_viewer_rect.centerx, (self.power_viewer_rect.top + self.rect.top) / 2)

        self.wp_text = self.font_param.render("Plain ammo", True, col_text_white, col_screen)
        self.wp_text_rect = self.wp_text.get_rect()
        self.wp_text_rect.center = self.wp_viewer_rect.center

        self.wp_heading = self.font_heading.render("Weapon", True, col_text_white)
        self.wp_heading_rect = self.wp_heading.get_rect()
        self.wp_heading_rect.center = (self.wp_viewer_rect.centerx, (self.wp_viewer_rect.top + self.rect.top) / 2)

        self.scoreboard_heading = self.font_param.render("Scoreboard", True, col_text_white)
        self.scoreboard_heading_rect = self.scoreboard_heading.get_rect()
        self.scoreboard_heading_rect.center = (self.score_viewer_rect.centerx, self.score_viewer_rect.top + self.score_viewer_rect.h / 9)

        '''self.fire_text = self.font.render("Fire", True, col_fire)
        self.fire_text_rect = self.fire_text.get_rect()
        self.fire_text_rect.center = self.fire.center'''


        # draw control elements

        screen.blits(((wp_surf, self.wp), (angle_surf, self.angle_sel), (power_surf, self.power),
                      (power_bar_surf, self.power_bar),
                      (fire_surf, self.fire),
                      (angle_dec_surf, self.angle_dec),
                      (angle_inc_surf, self.angle_inc),
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
                      (self.angle_heading, self.angle_heading_rect),
                      (self.power_heading, self.power_heading_rect),
                      (self.wp_heading, self.wp_heading_rect),
                      (fire_text_surf, self.fire_text),
                      (scoreboard_frame_surf, self.scoreboard),
                      (self.score_viewer, self.score_viewer_rect),
                      (self.scoreboard_heading, self.scoreboard_heading_rect)
                      ), 0)

        # fill bar at the end
        self.power_bar_fill_rect = pygame.draw.rect(screen, col_power,
                                                    (self.fill_x, self.fill_y,
                                                     int(self.fill_w * (default_power_val / 100)),
                                                     self.fill_h))

    def update_angle(self, screen: pygame.Surface, val):
        self.angle_viewer.fill(col_screen)
        self.angle_text = self.font_param.render(str(val), True, col_text_white, col_screen)
        screen.blits(((self.angle_viewer, self.angle_viewer_rect), (self.angle_text, self.angle_text_rect)), 0)

    def update_power(self, screen: pygame.Surface, val):
        self.power_viewer.fill(col_screen)
        self.power_text = self.font_param.render(str(val), True, col_text_white, col_screen)
        screen.blits(((self.power_viewer, self.power_viewer_rect), (self.power_text, self.power_text_rect)), 0)
        # redraw power bar fill
        pygame.draw.rect(screen, col_screen, (self.fill_x, self.fill_y, self.fill_w, self.fill_h))
        self.power_bar_fill_rect = pygame.draw.rect(screen, col_power, (self.fill_x, self.fill_y, self.fill_w * (val / 100), self.fill_h))


def scale(surface, scaling_factor):
    rect = surface.get_rect()
    new_w = round(rect.w / scaling_factor)
    new_h = round(rect.h / scaling_factor)
    return pygame.transform.scale(surface, (new_w, new_h))
