import pygame


class Terrain(pygame.sprite.Sprite):
    def __init__(self, screen, play_left, play_w, play_bottom, terrain_h):
        super(Terrain, self).__init__
        self.surf = pygame.transform.scale(
            pygame.image.load("../resources/images/terrain.png"),
            (play_w, terrain_h))
        self.rect = self.surf.get_rect()
        self.rect.x = play_left
        self.rect.y = play_bottom - terrain_h
        screen.blit(self.surf, self.rect)
