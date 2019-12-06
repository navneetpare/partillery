import pygame
import math

col_turret = 200, 200, 200


class Tank(pygame.sprite.Sprite):
    def __init__(self, screen, play_left, play_top, col, loc_x, loc_y, angle):
        super(Tank, self).__init__
        self.surf = pygame.image.load("../resources/images/tank_" + col + ".png")
        self.rect = self.surf.get_rect()
        self.rect.x = loc_x
        self.rect.y = loc_y
        # eraser for square containing tank and turret = 2x tank rect.
        # this eraser should not change unless the tank moves
        self.combo_eraser = get_eraser(screen, play_left, play_top, loc_x, loc_y - self.rect.h, self.rect.w,
                                       self.rect.h * 2)
        self.erase_loc = pygame.Rect(loc_x, loc_y - self.rect.h, self.rect.w, self.rect.h * 2)
        self.turret = Turret(screen, self.rect.midtop, self.rect.h, angle)
        screen.blit(self.surf, self.rect)


class Turret:
    def __init__(self, screen, start_pos: tuple, tank_h, angle):
        # turret length = tank height
        self.start_pos = start_pos
        x = int(start_pos[0] + tank_h * math.cos(math.radians(angle)))
        y = int(start_pos[1] - tank_h * math.sin(math.radians(angle)))
        self.rect = pygame.draw.line(screen, col_turret, start_pos, (x, y), 2)
        self.nose = x, y


def update_turret(screen: pygame.Surface, tank: Tank, angle):
    screen.blit(tank.combo_eraser, tank.erase_loc)  # erase tank + turret square
    screen.blit(tank.surf, tank.rect)  # draw tank
    # compute turret location
    x = int(tank.turret.start_pos[0] + tank.rect.h * math.cos(math.radians(angle)))
    y = int(tank.turret.start_pos[1] - tank.rect.h * math.sin(math.radians(angle)))
    # draw turret
    tank.turret.rect = pygame.draw.line(screen, col_turret, tank.turret.start_pos, (x, y), 2)
    # update nose for next ammo generation
    tank.turret.nose = x, y


def get_eraser(screen, play_left, play_top, x, y, w, h):
    area = screen.subsurface(pygame.Rect(x - play_left, y - play_top, w, h)).copy()
    return area
