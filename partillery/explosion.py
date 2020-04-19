# https://stackoverflow.com/questions/12787650/finding-the-index-of-n-biggest-elements-in-python-array-list-efficiently?noredirect=1&lq=1
# https://towardsdatascience.com/the-little-known-ogrid-function-in-numpy-19ead3bdae40
# https://stackoverflow.com/questions/44865023/how-can-i-create-a-circular-mask-for-a-numpy-array

import pygame
import math
from numpy import ogrid
from numpy import sqrt


class Explosion():
    def __init__(self, screen, playsurfbk, terrain_mask, center, radius, ammo_type):
        t = 0
        t0 = pygame.time.get_ticks()

        # Getting a circular alpha mask for the explosion
        exp_rect = pygame.Rect(0, 0, radius * 2, radius * 2)  # create a rect the size of the exp
        exp_rect.center = center  # position the rect at the explosion location
        exp_rect = exp_rect.clip(playsurfbk.get_rect())  # clip the rect to playsurf for edge cases
        exp_bg = playsurfbk.subsurface(exp_rect).copy()  # get a backup of the background at the exp location

        # ------- Get circular background backup

        # use direct reference to surface pixel alphas instead of copy
        exp_bg_array = pygame.surfarray.pixels_alpha(exp_bg)  # create an array that references the backup pixel alphas
        # cool numpy matrix to hold the positions of the pixels (this is an extra array)
        x, y = ogrid[:exp_rect.width, :exp_rect.height]
        # find the center of the backup rect - remember this is not exp loc, but the backup which corners at (0,0)
        exp_bg_center = (radius, radius)
        # No 'for' loops. Function uses broadcasting for the formula, so 'd' will be an array too - the power of Numpy!!
        d = sqrt((x - exp_bg_center[0]) ** 2 + (y - exp_bg_center[1]) ** 2)
        exp_mask = d < (radius * 2 / 2)  # so is the mask
        exp_bg_array[~exp_mask] = 0  # this directly alters the pixel alphas due to the fast pygame method

        del exp_bg_array  # delete the pixel alpha reference array to unlock the bg surface

        # -------- Create mask to delete from terrain
        cut_surf = pygame.Surface((radius * 2, radius * 2))
        pygame.draw.circle(cut_surf, (255, 255, 255, 255), (radius, radius), radius)
        terr_cut_mask = pygame.mask.from_threshold(cut_surf, (255, 255, 255, 255))
        terr_cut_mask.invert()
        exp_speed = 0.2  # pixels per 1000 ms

        while exp_speed * t < radius:  # milliseconds
            for i in range(1, int(exp_speed * t)):
                pygame.draw.circle(screen, (255, 150, 0, int(255 * math.pow(i % 10, 2) / 225)), center, i, 1)

            pygame.display.update()
            t = pygame.time.get_ticks() - t0

        screen.blit(exp_bg, exp_rect)

        terrain_mask.erase(terr_cut_mask, (center[0] - radius, center[1] - radius))

        # this creates a fuzzy fireball that clarifies with time
        # pygame.draw.circle(playsurf, (255, 150, 0, int(255 * t / 2500)), center, i, 1)

        # this creates a striped growing explosion - cosine
        # pygame.draw.circle(playsurf, (255, 150, 0, int(255 * (1 + math.cos(i/3)) / 2)), center, i, 1)

        # weid buzzy fireball
        # pygame.draw.circle(playsurf, (255, 150, 0, int(t % i)), center, i, 1)
