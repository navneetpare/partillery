import pygame


class BaseExplosion:
    def __init__(self, game, pos: tuple, radius: int, lifespan: int):
        # print('explosion top: ' + str((pos[0], pos[1] + radius)))
        # print('explosion center: ' + str(pos))
        # print('explosion bottom: ' + str((pos[0], pos[1] - radius)))

        self.exp_rect = None
        self.cut_out = None
        self.done = False
        self.clipped_rect = None
        exp_speed = radius / lifespan  # pixels per 1000 ms
        t0 = pygame.time.get_ticks()
        colour = (255, 170, 0, 255)

        while not self.done:
            t = pygame.time.get_ticks() - t0
            r = int(exp_speed * t)  # milliseconds
            if r <= radius:
                if r > 0:
                    # ---- Create a square transparent explosion surface, side = diameter.
                    exp_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)  # square the size of current diameter
                    self.exp_rect = exp_surf.get_rect()
                    self.exp_rect.center = pos

                    # ---- Draw opaque explosion on temp surf
                    pygame.draw.circle(exp_surf, colour, (self.exp_rect.w / 2, self.exp_rect.h / 2), r)

                    # TODO Desciption of the clipping and cropping code.
                    self.clipped_rect = self.exp_rect.clip(game.scene_rect)

                    if self.exp_rect.left < 0:
                        left = -self.exp_rect.left
                    else:
                        left = 0

                    if self.exp_rect.top < 0:
                        top = -self.exp_rect.top
                    else:
                        top = 0

                    exp_crop_rect = (left, top, self.clipped_rect.w, self.clipped_rect.h)

                    # r1 = pygame.Rect(1200, 550, 100, 100)
                    # r2 = r1.clip(game.scene_rect)
                    # print(r1)
                    # print(r2)
                    cropped_exp_surf = exp_surf.subsurface(exp_crop_rect)

                    # ---- Get mask of the square where the explosion is drawn.
                    # Setting the threshold selects only the circular area
                    exp_mask = pygame.mask.from_surface(cropped_exp_surf, 254)

                    # ---- Cut out the circular area from  the terrain mask. This is only for collisions
                    game.terrain.mask.erase(exp_mask, self.clipped_rect.topleft)

                    # ---- Draw the sky at the circular area.
                    # Get sky pixels at the mask set bits. Unset bits not drawn.
                    # The subsurface is clipped to scene rect to avoid Surface outside display error.
                    # self.exp_rect = self.exp_rect.clip(game.scene_rect)
                    try:
                        self.cut_out = exp_mask.to_surface(setsurface=game.sky.subsurface(self.clipped_rect),
                                                           unsetcolor=None)
                    except ValueError:
                        done = True
                        break

                    game.scene.blit(self.cut_out, self.clipped_rect)  # Erase terrain cutout from scene backup
                    game.screen.blit(self.cut_out, self.clipped_rect)  # Erase terrain from screen
                    game.screen.blit(cropped_exp_surf, self.clipped_rect)  # Draw explosion to screen
                    pygame.display.update(self.clipped_rect)

            else:
                self.done = True

        try:
            pass
            game.screen.blit(self.cut_out, self.clipped_rect)
        except TypeError:
            pass
        pygame.display.update(self.clipped_rect)
