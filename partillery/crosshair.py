import pygame
import math


class CrossHair(pygame.sprite.Sprite):
    def __init__(self, screen, playsurf_rect, start_pos, angle, r):
        super(CrossHair, self).__init__()
        img = pygame.image.load("../resources/images/crosshair.png")
        self.surf = scale(img, 8)
        self.rect = self.surf.get_rect()
        self.x0 = start_pos[0]
        self.y0 = start_pos[1]
        self.r = r
        x = int(self.x0 + self.r * math.cos(math.radians(angle)))
        y = int(self.y0 - self.r * math.sin(math.radians(angle)))
        self.rect.center = (x, y)
        self.eraser_loc = self.rect  # save current loc for eraser
        self.eraser = get_eraser(screen, self.rect)  # save new eraser
        # screen.blit(self.surf, self.rect)

    def update(self, screen, playsurf_rect, angle):
        screen.blit(self.eraser, self.eraser_loc)  # erase trail
        x = int(self.x0 + self.r * math.cos(math.radians(angle)))
        y = int(self.y0 - self.r * math.sin(math.radians(angle)))
        self.rect.center = (x, y)  # move
        self.rect.clamp_ip(playsurf_rect)
        self.eraser_loc = self.rect  # save current loc for eraser
        self.eraser = get_eraser(screen, self.rect)  # save new eraser
        screen.blit(self.surf, self.rect)  # draw to new loc

    def hide(self, screen):
        screen.blit(self.eraser, self.eraser_loc)

    def show(self, screen):
        screen.blit(self.surf, self.rect)


def scale(surface, scaling_factor):
    rect = surface.get_rect()
    new_w = round(rect.w / scaling_factor)
    new_h = round(rect.h / scaling_factor)
    return pygame.transform.scale(surface, (new_w, new_h))


def get_eraser(screen, rect):
    area = screen.subsurface(rect).copy()
    return area



