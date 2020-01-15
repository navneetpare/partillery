import pygame
import math
from partillery.crosshair import CrossHair

col_turret = 200, 200, 200


class Tank(pygame.sprite.Sprite):
    def __init__(self, screen, playsurf_rect, col, proj_x, center, slope_radians, turret_angle):
        super(Tank, self).__init__()
        self.surf_org = pygame.image.load("resources/images/tank_" + col + ".png")
        self.h_orig = self.surf_org.get_rect().h  # un-rotated height
        self.w_orig = self.surf_org.get_rect().h  # un-rotated width
        self.surf = pygame.transform.rotate(self.surf_org, math.degrees(slope_radians))
        self.mask = pygame.mask.from_surface(self.surf)
        self.rect = self.surf.get_rect()
        self.rect.center = center  # set initial location
        self.proj_x = proj_x
        self.eraser_loc = self.rect  # save current loc for eraser
        self.eraser = get_eraser(screen, self.rect)  # save new eraser
        self.turret_nose = None
        self.crosshair = CrossHair(screen, playsurf_rect, center, turret_angle, self.w_orig * 4)
        screen.blit(self.surf, self.rect)  # initial tank draw
        # --- eraser for rect containing tank and turret = 2x tank rect.
        # --- maximum width and maximum height of bounding rect lies along the diagonals
        self.combo_erase_loc = self.rect.inflate(2 * self.w_orig, 2 * self.w_orig)  # creates a copy
        self.combo_erase_loc.center = self.rect.center  # recenter the inflated one - pygame is imperfect
        self.combo_eraser = get_eraser(screen, self.combo_erase_loc)
        self.update_turret(screen, turret_angle, True)  # initial turret draw

    def go(self, screen, center, proj_x, slope_radians):
        # print('::::: Moving Tank')
        self.surf = pygame.transform.rotate(self.surf_org, math.degrees(slope_radians))
        self.mask = pygame.mask.from_surface(self.surf)
        self.rect = self.surf.get_rect()
        screen.blit(self.eraser, self.eraser_loc)  # erase trail
        self.rect.center = center  # move
        self.proj_x = proj_x
        self.eraser_loc = self.rect  # save current loc for eraser
        self.eraser = get_eraser(screen, self.rect)  # save new eraser
        screen.blit(self.surf, self.rect)  # draw to new loc

    def update_turret(self, screen, angle, initial=False):
        if not initial:
            screen.blit(self.combo_eraser, self.combo_erase_loc)  # erase tank + turret square
        self.combo_erase_loc = self.rect.inflate(2 * self.w_orig, 2 * self.w_orig)  # creates a copy
        self.combo_erase_loc.center = self.rect.center  # recenter the inflated one - pygame is imperfect
        self.combo_eraser = get_eraser(screen, self.combo_erase_loc)
        # compute turret nose
        x = int(self.rect.centerx + self.h_orig * 1.2 * math.cos(math.radians(angle)))
        y = int(self.rect.centery - self.h_orig * 1.2 * math.sin(math.radians(angle)))
        # draw turret
        pygame.draw.line(screen, col_turret, self.rect.center, (x, y), 2)
        # update nose for next ammo generation
        self.turret_nose = x, y


def get_eraser(screen, rect):
    area = screen.subsurface(rect).copy()
    return area
