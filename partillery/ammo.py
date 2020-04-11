import pygame
import numpy as np


class Ammo(pygame.sprite.Sprite):
    def __init__(self, screen, ammo_x0, ammo_y0):
        super(Ammo, self).__init__()
        self.surf = pygame.image.load("resources/images/ammo_4.gif")
        self.mask = pygame.mask.from_surface(self.surf)
        self.rect = self.surf.get_rect()
        self.rect.x = ammo_x0
        self.rect.y = ammo_y0
        self.w = self.rect.w
        self.h = self.rect.h
        self.prev_pos = ammo_x0, ammo_y0
        self.eraser = get_eraser(screen, ammo_x0, ammo_y0, self.w, self.h)
        self.mask = pygame.mask.from_surface(self.surf)
        # mask doesn't have to be recreated unless you rotate the object or change image
        # mask is cornered at top left of screen - not actual position
        self.outline = self.mask.outline()
        # this is based on above mask - assume static mask since plain ammo is spherical
        screen.blit(self.surf, self.rect)

    def go(self, screen, playsurf_rect, terr_points, enemy_tank, x, y):

        alive = True
        new_rect = pygame.Rect(x, y, self.w, self.h)
        new_rect_inside = playsurf_rect.contains(new_rect)
        old_rect_inside = playsurf_rect.contains(self.rect)
        # collides = new_rect.colliderect(terr_mask) or new_rect.colliderect(enemy_tank_mask)

        if old_rect_inside:
            screen.blit(self.eraser, (self.rect.x, self.rect.y))  # erase trail

        self.prev_pos = (self.rect.x, self.rect.y)  # save current loc
        self.rect.x = x  # move
        self.rect.y = y

        # --- COLLISION DETECTION
        # -- we'll check enemy first and if yes, we'll skip terrain check as that is expensive
        collides = False

        # colliding with enemy tank?
        if pygame.sprite.collide_mask(self, enemy_tank) is not None:
            collides = True

        else:
            # offset the mask outline by new ammo coordinates to get actual outline
            # this is done using numpy array broadcast addition ; a temp array np.array([x,y]) is created on the fly
            new_outline = self.outline + np.array([x, y])
            print(new_outline)
            print(terr_points)
            if not set(map(tuple, new_outline)).isdisjoint(set(map(tuple, terr_points))):
                collides = True

        if new_rect_inside and not collides:
            self.eraser = get_eraser(screen, x, y, self.w, self.h)  # get new eraser for the
            # next location
            screen.blit(self.surf, self.rect)  # draw self to new loc

        if (x > playsurf_rect.right) or (x + self.w < playsurf_rect.left) or collides:
            alive = False
        return alive


def get_eraser(screen, x, y, w, h):
    area = screen.subsurface(pygame.Rect(x, y, w, h)).copy()
    return area
