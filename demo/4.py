"""
Changelog
==========
v0.1
- Got the basic projectile motion figured out.
- Motion curvature is choppy.
  (Retrospectively this is due to reliance on frame refresh to do computations instead of time elapsed.)
v0.2
- Calculating position per real time, instead of moving ammo by frame rate
- Calibrated values of g and base speed
- New flat terrain surface definition
- Detect collision between ammo and terrain and edges
- Ammo and trail to be updated only on play surface
v0.3
- Adding more elements
    - Target tank - object only
    - Target hit detection
    - Pretty background and tanks.
- Trail erasure -- still patchy, erases two positions in advance. Scratching head...
  Uses subsurface based eraser. Rectangle detection at edges is also a problem and causes a crash.
  Need to fix erasure on collision. Still shows last trail.
  (edit)* this was due to error in initialising the eraser. It's location needs to be offset from play edges. Silly me!
v0.4
 - Objectives:
   - Add mouse input to click and fire.
   - A lot more parameterized.
   - Drawn control panel (non-functional yet)

"""

import pygame, sys, math, random, os

pygame.init()
clock = pygame.time.Clock()

# Colors
col_black = 0, 0, 0
col_text = 200, 200, 200
col_screen = 10, 10, 10
col_grey = 25, 25, 25
col_night = 10, 10, 10
col_terrain = 0, 130, 50
col_day = 207, 245, 254
col_eve = 0, 30, 70

# Vars
full_w = 1280
full_h = 720
play_w = full_w
play_h = round(full_h * 0.8)
play_left = (full_w - play_w) / 2
play_right = play_left + play_w
# play_top = (full_h - play_h) / 2
play_top = 0  # moved the play area to the top of the screen
play_bottom = play_top + play_h
# play_centre = (full_w - play_w) / 2, (full_h - play_h) / 2
terrain_h = round(play_h * 0.2)
control_h = full_h - play_h
control_scale = 15  # scaling factor for my ctrl images; set from tests
tank_h = 24
tank_w = 32
tank_x = play_left
tank_y = play_top + play_h - tank_h - terrain_h
ammo1_h = 4

# Ammo physics
angle_val = 60  # will be user selectable
g = 500
speed_base = 1000
power_val = 78  # this will eventually be user selectable power percentage
speed_start = speed_base * power_val / 100
ammo1_speed_x0 = speed_start * math.cos(math.radians(angle_val))
ammo1_speed_y0 = -(speed_start * math.sin(math.radians(angle_val)))

# set_mode(size=(0, 0), flags=0, depth=0, display=0) -> Surface
# screen=pygame.display.set_mode(size=(0,0), flags=pygame.RESIZABLE)
pygame.display.set_caption("Tanks")
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100, 40)
screen = pygame.display.set_mode((full_w, full_h), pygame.RESIZABLE)
screen.fill(col_screen)

playimg = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\nighthd_starry.png").convert()
playsurf = pygame.transform.scale(playimg, (play_w, play_h))
playsurf_rect = playsurf.get_rect()
playsurf_rect.x = play_left
playsurf_rect.y = play_top


def get_eraser(x, y, w, h):
    area = playsurf.subsurface(pygame.Rect(x - play_left, y - play_top, w, h)).copy()
    return area


def scale(surface, scaling_factor):
    rect = surface.get_rect()
    new_w = round(rect.w / scaling_factor)
    new_h = round(rect.h / scaling_factor)
    return pygame.transform.scale(surface, (new_w, new_h))


class Tank(pygame.sprite.Sprite):
    def __init__(self, orientation, loc_x, loc_y):
        super(Tank, self).__init__
        self.surf = pygame.image.load(
            "C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\tank_" + orientation + ".png")
        self.rect = self.surf.get_rect()
        self.rect.x = loc_x
        self.rect.y = loc_y
        screen.blit(self.surf, self.rect)


class Ammo(pygame.sprite.Sprite):
    def __init__(self, loc_x, loc_y):
        super(Ammo, self).__init__
        self.surf = pygame.image.load(
            "C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\ammo_4.gif")
        self.surf.set_alpha(255)
        self.rect = self.surf.get_rect()
        self.rect.x = loc_x
        self.rect.y = loc_y
        self.w = self.rect.w
        self.h = self.rect.h
        self.prev_pos = loc_x, loc_y
        self.eraser = get_eraser(loc_x, loc_y, self.w, self.h)
        screen.blit(self.surf, self.rect)

    def go(self, x, y):

        alive = True
        new_rect = pygame.Rect(x, y, self.w, self.h)
        new_rect_inside = playsurf_rect.contains(new_rect)
        old_rect_inside = playsurf_rect.contains(self.rect)

        if (x > play_right) or (x + self.w < play_left):
            alive = False

        if old_rect_inside:
            screen.blit(self.eraser, (self.rect.x, self.rect.y))  # erase trail
            a = 1
        self.prev_pos = (self.rect.x, self.rect.y)  # save current loc
        self.rect.x = x  # move
        self.rect.y = y

        if new_rect_inside:
            self.eraser = get_eraser(x, y, self.w, self.h)  # get new eraser for the next location
            screen.blit(self.surf, self.rect)  # draw self to new loc
        return alive


class Terrain(pygame.sprite.Sprite):
    def __init__(self):
        super(Terrain, self).__init__
        self.surf = pygame.transform.scale(
            pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\terrain.png"),
            (play_w, terrain_h))
        self.rect = self.surf.get_rect()
        self.rect.x = play_left
        self.rect.y = play_bottom - terrain_h
        screen.blit(self.surf, self.rect)


class ControlPanel():
    def __init__(self):
        controlimg = pygame.image.load(
            "C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\control_panel.png").convert()
        self.surf = pygame.transform.scale(controlimg, (play_w, full_h - play_h))
        self.rect = self.surf.get_rect()
        self.rect.x = play_left
        self.rect.y = play_top + play_h
        screen.blit(self.surf, (play_left, play_bottom))

        # add and draw control elements
        sec_w = full_w / 5
        wp_x = sec_w
        angle_x = sec_w * 2
        power_x = sec_w * 3
        fire_x = sec_w * 4
        text_y = self.rect.y + self.rect.h * 0.25
        control_baseline_y = self.rect.y + self.rect.h * 0.4  # setting up a y-axis center line for controls

        # load images
        wp_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\wp_list.png")
        angle_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\param_window.png")
        angle_add_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\add_button.png")
        angle_sub_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\sub_button.png")
        power_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\param_window.png")
        power_bar_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\power_bar.png")
        power_add_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\add_button.png")
        power_sub_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\sub_button.png")
        fire_img = pygame.image.load("C:\\Data\\Study\\cloud\\___python_game\\resources\\images\\fire.png")

        # scale images
        wp_surf = scale(wp_img, control_scale)
        angle_sub_surf = scale(angle_sub_img, control_scale)
        angle_surf = scale(angle_img, control_scale)
        angle_add_surf = scale(angle_add_img, control_scale)
        power_sub_surf = scale(power_sub_img, control_scale)
        power_surf = scale(power_img, control_scale)
        power_add_surf = scale(power_add_img, control_scale)
        power_bar_surf = scale(power_bar_img, control_scale)
        fire_surf = scale(fire_img, control_scale)

        # get rects with simple names
        wp = wp_surf.get_rect()
        angle_sub = angle_sub_surf.get_rect()
        angle_sel = angle_surf.get_rect()
        angle_add = angle_add_surf.get_rect()
        power_sub = power_sub_surf.get_rect()
        power = power_surf.get_rect()
        power_add = power_add_surf.get_rect()
        power_bar = power_bar_surf.get_rect()
        fire = fire_surf.get_rect()

        # set positions
        wp.center = (wp_x + angle_x) / 2, control_baseline_y
        angle_sel.center = (angle_x + power_x) / 2, control_baseline_y
        power.center = (power_x + fire_x) / 2, control_baseline_y
        power_bar.center = (power_x + fire_x) / 2, (control_baseline_y + full_h) / 2
        fire.center = (fire_x + play_right) / 2, (self.rect.y + self.rect.h / 2)
        angle_sub.center = ((angle_x + power_x) / 2) - angle_sub.w / 2 - angle_sel.w / 2, control_baseline_y
        angle_add.center = ((angle_x + power_x) / 2) + angle_add.w / 2 + angle_sel.w / 2, control_baseline_y
        power_sub.center = ((power_x + fire_x) / 2) - power_sub.w / 2 - power.w / 2, control_baseline_y
        power_add.center = ((power_x + fire_x) / 2) + power_add.w / 2 + power.w / 2, control_baseline_y

        # control windows

        wp_viewer = pygame.Surface((int(wp.w * 0.7), int(wp.h * 0.5)))
        wp_viewer_rect = wp_viewer.get_rect()
        wp_viewer.fill(col_screen)
        wp_viewer_rect.center = wp.center

        angle_viewer = pygame.Surface((int(angle_sel.w * 0.7), int(angle_sel.h * 0.5)))
        angle_viewer_rect = angle_viewer.get_rect()
        angle_viewer.fill(col_screen)
        angle_viewer_rect.center = angle_sel.center

        power_viewer = pygame.Surface((int(power.w * 0.7), int(power.h * 0.5)))
        power_viewer_rect = power_viewer.get_rect()
        power_viewer.fill(col_screen)
        power_viewer_rect.center = power.center

        power_bar_viewer = pygame.Surface((int(power_bar.w * 0.7), int(power_bar.h * 0.5)))
        power_bar_viewer_rect = power_bar_viewer.get_rect()
        power_bar_viewer.fill(col_screen)
        power_bar_viewer_rect.center = power_bar.center

        # display text
        # font = pygame.font.Font("C:\\WINDOWS\\Fonts\\ARIALN.ttf", 32)
        font = pygame.font.SysFont("segoeui", 15, True)

        angle_text = font.render(str(angle_val), True, col_text, col_screen)
        angle_text_rect = angle_text.get_rect()
        angle_text_rect.center = angle_viewer_rect.center

        power_text = font.render(str(power_val), True, col_text, col_screen)
        power_text_rect = power_text.get_rect()
        power_text_rect.center = power_viewer_rect.center

        wp_text = font.render("Plain ammo", True, col_text, col_screen)
        wp_text_rect = wp_text.get_rect()
        wp_text_rect.center = wp_viewer_rect.center

        # power_bar_fill_rect = power_bar
        # power_viewer_rect.w = power_viewer_rect.w * 10 / 100
        # power_bar_viewer.fill(col_day)

        # draw control elements
        screen.blits(((wp_surf, wp), (angle_surf, angle_sel), (power_surf, power), (power_bar_surf, power_bar),
                      (fire_surf, fire), (angle_add_surf, angle_add), (angle_sub_surf, angle_sub),
                      (power_add_surf, power_add), (power_sub_surf, power_sub), (wp_viewer, wp_viewer_rect),
                      (angle_viewer, angle_viewer_rect), (power_viewer, power_viewer_rect),
                      (power_bar_viewer, power_bar_viewer_rect), (angle_text, angle_text_rect),
                      (power_text, power_text_rect), (wp_text, wp_text_rect)), 0)


#  Create and draw initial elements
screen.blit(playsurf, (play_left, play_top))

terr = Terrain()
ctl = ControlPanel()

tank1 = Tank("right", random.randint(play_left, ((play_right - play_left) / 2) - tank_w),
             (play_bottom - terrain_h - tank_h))
tank2 = Tank("left", random.randint(((play_right - play_left) / 2), play_right - tank_w),
             (play_bottom - terrain_h - tank_h))
# tank1 = Tank("right", play_left, (play_bottom - terrain_h - tank_h))
# tank2 = Tank("left", play_right - tank_w, (play_bottom - terrain_h - tank_h))

ammo1_x0 = tank1.rect.x + tank_w
ammo1_y0 = tank1.rect.y - ammo1_h
ammo1 = Ammo(ammo1_x0, ammo1_y0)
pygame.display.update()

# game loop flag
volley_in_progress = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.K_DOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            volley_in_progress = True
            # timer start
            t0 = pygame.time.get_ticks()

    while volley_in_progress:
        if ammo1.rect.colliderect(terr.rect) or ammo1.rect.colliderect(tank2.rect):
            screen.blit(ammo1.eraser, ammo1.prev_pos)
            volley_in_progress = False
            break

        # compute move, s = ut + 1/2(gt^2) + x_initial
        t = (pygame.time.get_ticks() - t0) / 1000
        ammo1_new_x = round((ammo1_speed_x0 * t) + ammo1_x0)
        ammo1_new_y = round(((ammo1_speed_y0 * t) + (0.5 * g * t ** 2)) + ammo1_y0)

        # move and check
        volley_in_progress = ammo1.go(ammo1_new_x, ammo1_new_y)
        pygame.display.update()
        clock.tick(60)
