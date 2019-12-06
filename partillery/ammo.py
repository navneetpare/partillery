import pygame


class Ammo(pygame.sprite.Sprite):
    def __init__(self, screen, play_left, play_top, ammo_x0, ammo_y0):
        super(Ammo, self).__init__
        self.surf = pygame.image.load("../resources/images/ammo_4.gif")
        self.surf.set_alpha(255)
        self.rect = self.surf.get_rect()
        self.rect.x = ammo_x0
        self.rect.y = ammo_y0
        self.w = self.rect.w
        self.h = self.rect.h
        self.prev_pos = ammo_x0, ammo_y0
        self.eraser = get_eraser(screen, play_left, play_top, ammo_x0, ammo_y0, self.w, self.h)
        screen.blit(self.surf, self.rect)

    def go(self, screen, playsurf_rect, play_left, play_top, terr_rect, tank2_rect, x, y):

        alive = True
        new_rect = pygame.Rect(x, y, self.w, self.h)
        new_rect_inside = playsurf_rect.contains(new_rect)
        old_rect_inside = playsurf_rect.contains(self.rect)
        collides = new_rect.colliderect(terr_rect) or new_rect.colliderect(tank2_rect)

        if (x > playsurf_rect.right) or (x + self.w < playsurf_rect.left) or collides:
            alive = False

        if old_rect_inside:
            screen.blit(self.eraser, (self.rect.x, self.rect.y))  # erase trail

        self.prev_pos = (self.rect.x, self.rect.y)  # save current loc
        self.rect.x = x  # move
        self.rect.y = y

        if new_rect_inside and not collides:
            self.eraser = get_eraser(screen, play_left, play_top, x, y, self.w, self.h)  # get new eraser for the
            # next location
            screen.blit(self.surf, self.rect)  # draw self to new loc
        return alive


def get_eraser(screen, play_left, play_top, x, y, w, h):
    area = screen.subsurface(pygame.Rect(x - play_left, y - play_top, w, h)).copy()
    return area
