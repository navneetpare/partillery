import pygame
import math
import time

col_turret = 200, 200, 200


class Tank(pygame.sprite.Sprite):
    def __init__(self, screen, col, orientation, proj_x, center, slope_radians, turret_angle):
        super(Tank, self).__init__
        self.proj_x = proj_x
        self.surf_org = pygame.image.load("../resources/images/tank_" + col + ".png")
        self.h = self.surf_org.get_rect().h  # un-rotated height
        self.surf = None
        self.rect = None
        self.orientation = orientation
        self.eraser = None
        self.eraser_loc = None
        print('================================= Tank Init')
        print('rect = ' + str(self.rect))
        print('eraser = ' + str(self.eraser))
        print('eraser loc = ' + str(self.eraser_loc))
        print('slope = ' + str(slope_radians))
        print('center = ' + str(center))

        # screen.blit(self.surf, (self.rect.x, self.rect.y))
        # eraser for square containing tank and turret = 2x tank rect.
        # self.combo_eraser = get_eraser(screen, self.rect.x, self.rect.y - self.rect.h, self.rect.w, self.rect.h * 2)
        # self.combo_erase_loc = pygame.Rect(self.rect.x, self.rect.y - self.rect.h, self.rect.w, self.rect.h * 2)
        # self.turret = Turret(screen, self.rect.center, tank_h, turret_angle) screen.blit(self.surf, self.rect)
        # self.move_by_center(screen, play_left, play_top, center, slope_radians)
        self.move_by_center(screen, center, proj_x, slope_radians)

    def move_by_center(self, screen, center, proj_x, slope_radians):
        # print('::::: Moving Tank')
        self.surf = pygame.transform.rotate(self.surf_org, math.degrees(slope_radians))
        self.rect = self.surf.get_rect()
        if self.eraser is not None:
            print('================================= Erasing with:')
            print('eraser = ' + str(self.eraser))
            print('eraser_loc = ' + str(self.eraser_loc))
            screen.blit(self.eraser, self.eraser_loc)  # erase trail)
        self.rect.center = center  # move
        self.proj_x = proj_x
        self.eraser_loc = self.rect.x, self.rect.y  # save current loc for eraser
        self.eraser = get_eraser(screen, self.rect.x, self.rect.y, self.rect.w, self.rect.h)  # save new eraser
        screen.blit(self.surf, self.rect)  # draw to new loc
        print('================================= Moved to')
        print('rect = ' + str(self.rect))
        print('eraser = ' + str(self.eraser))
        print('eraser loc = ' + str(self.eraser_loc))
        print('slope = ' + str(slope_radians))
        print('center = ' + str(center))

    '''def move_by_midbottom(self, screen, x, y, slope_radians):
        self.surf = pygame.transform.rotate(self.surf_org, math.degrees(slope_radians))
        # self.rect = self.surf.get_rect()
        screen.blit(self.eraser, self.eraser_loc)  # erase trail
        self.rect.midbottom = x, y  # move
        self.eraser_loc = self.rect.x, self.rect.y  # save current loc for eraser
        self.eraser = get_eraser(screen, self.rect.x, self.rect.y, self.rect.w, self.rect.h)  # save new eraser
        screen.blit(self.surf, self.rect)  # draw to new loc

    def move_left_bottom(self, screen, slope_radians, bottom_left):
        print('::::: Moving Tank')
        self.surf = pygame.transform.rotate(self.surf_org, math.degrees(slope_radians))
        self.rect = self.surf.get_rect()
        print('- Erasing with:')
        print('eraser = ' + str(self.eraser))
        print('eraser_loc = ' + str(self.eraser_loc))
        screen.blit(self.eraser, self.eraser_loc)  # erase trail)
        self.rect.bottomleft = bottom_left  # move
        self.eraser_loc = self.rect.x, self.rect.y  # save current loc for eraser
        self.eraser = get_eraser(screen, self.rect.x, self.rect.y, self.rect.w, self.rect.h)  # save new eraser
        screen.blit(self.surf, self.rect)  # draw to new loc
        print('- Moved to')
        print('rect = ' + str(self.rect))
        print('eraser = ' + str(self.eraser))
        print('eraser loc = ' + str(self.eraser_loc))
        print('slope = ' + str(slope_radians))
        print('bottom_left = ' + str(bottom_left))'''


class Turret:
    def __init__(self, screen, start_pos: tuple, tank_h, angle):
        # turret length = tank height
        self.start_pos = start_pos
        x = int(start_pos[0] + tank_h * math.cos(math.radians(angle)))
        y = int(start_pos[1] - tank_h * math.sin(math.radians(angle)))
        self.rect = pygame.draw.line(screen, col_turret, start_pos, (x, y), 2)
        self.nose = x, y


def update_turret(screen: pygame.Surface, tank: Tank, angle):
    screen.blit(tank.combo_eraser, tank.combo_erase_loc)  # erase tank + turret square
    screen.blit(tank.surf, tank.rect)  # draw tank
    # compute turret location
    x = int(tank.turret.start_pos[0] + tank.rect.h * math.cos(math.radians(angle)))
    y = int(tank.turret.start_pos[1] - tank.rect.h * math.sin(math.radians(angle)))
    # draw turret
    tank.turret.rect = pygame.draw.line(screen, col_turret, tank.turret.start_pos, (x, y), 2)
    # update nose for next ammo generation
    tank.turret.nose = x, y


def get_eraser(screen, x, y, w, h):
    area = screen.subsurface(pygame.Rect(x, y, w, h)).copy()
    return area
