# Terrain layer thickness needs to be pixel based.
# Drawing vertical segments does not account for slope.
# http://geomalgorithms.com/a13-_intersect-4.html

# 11/04/2020 - Divide the terrain vertically into slats. Each will have its own mask.

import pygame
import math
import random
import numpy as np
from scipy import interpolate

# import matplotlib.pyplot as plt

# Colours

g1 = 0, 180, 0, 255  # green opaque
g2 = 0, 150, 0, 255  # green opaque
g3 = 0, 120, 0, 255  # green opaque
g4 = 0, 90, 0, 255  # green opaque
g5 = 0, 60, 0, 255  # green opaque

# --- awesome palette
teal = 56, 104, 80
b1 = 240, 192, 160
b2 = 152, 112, 80
b3 = 112, 80, 48
b4 = 56, 16, 0

d1_for_purple = 21,21,21

# Coefficients for the main noise generator
a = [15731, 16703, 23143, 19843, 12744, 97586, 36178, 88412, 78436, 78436, 96653, 12598, 32158, 98764, 11579, 65989,
     13647, 36987, 16467, 16798]
b = [789221, 794711, 793139, 799259, 842555, 674336, 947264, 654158, 984378, 867943, 116871, 157998, 369876, 679481,
     559852, 989797, 364984, 123654, 698749, 914672]
c = [1376328799, 1376312589, 1376324099, 1376312881, 5748234489, 3621789547, 9785412268, 1577894552, 1478965784,
     3695784298,
     1918767419, 7894976813, 1649875310, 1203401615, 9024603100, 6030149475, 6049708410, 1164973489, 6633215899,
     4424784468]


# ------ Maths functions --------
def noise(x: int, i: int):
    x = (x << 13) ^ x
    return 1.0 - ((x * (x * x * a[i] + b[i]) + c[i]) & 2147483647) / 1073741824.0


def cubic_interpolation(v0, v1, v2, v3, x):
    p = (v3 - v2) - (v0 - v1)
    q = (v0 - v1) - p
    r = v2 - v0
    s = v1
    return p * (x ** 3) + q * (x ** 2) + r * x + s


def cosine_interpolation(a, b, x):
    ft = x * 3.1415927
    f = (1 - math.cos(ft)) * .5
    return a * (1 - f) + b * f


def smoothed_noise(x, i):
    return noise(x, i) / 2 + noise(x - 1, i) / 4 + noise(x + 1, i) / 4


def interpolated_noise(x: float, i: int):
    x *= 0.001
    integer_x = int(x)
    fractional_x = x - integer_x

    v1 = smoothed_noise(integer_x, i)
    v2 = smoothed_noise(integer_x + 1, i)

    return cosine_interpolation(v1, v2, fractional_x)


def perlin_noise(x: float):
    total = 0
    p = 1.5  # persistence
    n = 14  # Number_Of_Octaves - 1
    for i in range(1, n):
        frequency = 2 * i
        amplitude = p * i
        total = total + interpolated_noise(x * frequency, i) * amplitude
    return total


def generate(w, h, terrain_type):
    # ----- Generate macro structure of the terrain type chosen ------
    random.shuffle(a)
    random.shuffle(b)
    random.shuffle(c)
    hs = h / 8  # height segment
    ws = w / 8  # width segment
    inflexion_points = None
    y_arr = None

    if terrain_type == "Random":
        terrain_type = random.choice(['Valley', 'Hill', 'Cliff'])
        interpolation_type = 'linear'  # Default
        # Hill
        if terrain_type == "Hill":
            p100 = 0, random.randint(5.5 * hs, 7.5 * hs)  # left edge
            p200 = random.randint(2 * ws, 3.5 * ws), random.randint(3 * hs, 5 * hs)  # left curve
            p300 = random.randint(3.5 * ws, 4.5 * ws), random.randint(2 * hs, 3 * hs)  # peak1
            # p350 = random.randint(4 * ws, 5 * ws), random.randint(2 * hs, 3 * hs)  # peak2
            p400 = random.randint(4.5 * ws, 6 * ws), random.randint(3 * hs, 5 * hs)  # right curve
            p500 = w, random.randint(5.5 * hs, 7.5 * hs)  # right edge
            # add centroids of right angled triangle with p1 / p2 to add to the curve
            pa = p200[0], p100[1]
            pb = p400[0], p500[1]
            p150 = (p100[0] + pa[0] + p200[0]) / 3, (p100[1] + pa[1] + p200[1]) / 3
            p450 = (p400[0] + pb[0] + p500[0]) / 3, (p400[1] + pb[1] + p500[1]) / 3
            inflexion_points = [p100, p150, p200, p300, p400, p450, p500]

        # Valley
        elif terrain_type == "Valley":
            p100 = 0, random.randint(1 * hs, 2.5 * hs)  # left edge
            p200 = random.randint(2.5 * ws, 3.5 * ws), random.randint(3 * hs, 5 * hs)  # left curve
            p300 = random.randint(3.5 * ws, 4.5 * ws), random.randint(6 * hs, 7 * hs)  # trough
            p400 = random.randint(4.5 * ws, 5.5 * ws), random.randint(3 * hs, 5 * hs)  # right curve
            p500 = w, random.randint(1 * hs, 2.5 * hs)  # right edge
            # add centroids of right angled triangle with p1 / p2 to add to the curve
            pa = p200[0], p100[1]
            pb = p400[0], p500[1]
            p150 = (p100[0] + pa[0] + p200[0]) / 3, (p100[1] + pa[1] + p200[1]) / 3
            p450 = (p400[0] + pb[0] + p500[0]) / 3, (p400[1] + pb[1] + p500[1]) / 3
            inflexion_points = [p100, p150, p200, p300, p400, p450, p500]

        # Cliff
        elif terrain_type == "Cliff":
            interpolation_type = 'linear'
            ch = random.randint(2 * hs, 3.5 * hs)  # cliff height
            bh = random.randint(5.5 * hs, 7.5 * hs)  # base height
            if random.choice(['fall', 'rise']) == 'fall':  # slope
                p100 = 0, ch  # left edge
                p200 = random.randint(2 * ws, 3.5 * ws), ch  # plateau ends here
                p300 = w / 2, h / 2  # centered with the screen
                p400 = random.randint(4.5 * ws, 6 * ws), bh  # base starts here
                p500 = w, bh  # right edge
                # add centroids of right angled triangle with p1 / p2 to add to the curve
                pa = p200[0], p100[1]
                pb = p400[0], p500[1]
                p150 = (p100[0] + pa[0] + p200[0]) / 3, (p100[1] + pa[1] + p200[1]) / 3
                p450 = (p400[0] + pb[0] + p500[0]) / 3, (p400[1] + pb[1] + p500[1]) / 3
                inflexion_points = [p100, p150, p200, p300, p400, p450, p500]

            else:
                p100 = 0, bh  # left edge
                p200 = random.randint(2 * ws, 3 * ws), bh  # base ends here
                p300 = w / 2, h / 2  # centered with the screen
                p400 = random.randint(5 * ws, 6 * ws), ch  # plateau starts here
                p500 = w, ch  # right edge
                # add centroids of right angled triangle with p1 / p2 to add to the curve
                pa = p200[0], p100[1]
                pb = p400[0], p500[1]
                p150 = (p100[0] + pa[0] + p200[0]) / 3, (p100[1] + pa[1] + p200[1]) / 3
                p450 = (p400[0] + pb[0] + p500[0]) / 3, (p400[1] + pb[1] + p500[1]) / 3
                inflexion_points = [p100, p150, p200, p300, p400, p450, p500]

        macro_terrain_points = np.array(inflexion_points).T
        x0 = macro_terrain_points[0]
        y0 = macro_terrain_points[1]

        x_arr = np.arange(1, w + 1, 1)
        fun = interpolate.interp1d(x0, y0, interpolation_type)
        y_base = fun(x_arr)
        perlin_vec = np.vectorize(perlin_noise)
        y_perlin = perlin_vec(x_arr)
        y_arr = y_base + y_perlin
        y_arr = y_arr.astype(int, 'K', 'unsafe', True, True)

    elif terrain_type == 'Flat':
        y_arr = np.ones(w)*400

    return y_arr  # only need the y coords; x is implicit as array index - 1

    # Debug only
    # plt.plot(x0, y0, 'o', x_arr, y_arr, '-')
    # plt.ylim(-720, 1)
    # plt.xlim(1, 72)
    # plt.show()


class Terrain:
    def __init__(self, game_w, game_h, terrain_type):
        # Create a layer for terrain, with per-pixel alpha allowed
        self.w = game_w
        self.image = pygame.Surface((game_w, game_h), pygame.SRCALPHA)
        self.y_coordinates = generate(game_w, game_h, terrain_type)  # only y coords
        x = np.arange(1, game_w + 1, 1)  # just temp
        self.points = np.column_stack((x, self.y_coordinates))

        # temp y array which will be moved downwards for painting layers of terrain
        y = np.array(self.y_coordinates)  # for fast numpy methods

        green_val = 255
        # Top crust
        for i in range(1, 3):
            m = np.column_stack((x, y))
            # pygame.draw.lines(self.surf, b1, False, m)
            pygame.draw.aalines(self.image, (170, 170, 170), False, m)
            y += 1
            y.clip(0, game_h)
        '''for i in range(21, 40):
            m = np.column_stack((x, y))
            pygame.draw.lines(self.surf, b2, False, m)
            y += 1
            y.clip(0, play_h)
        for i in range(41, 60):
            m = np.column_stack((x, y))
            pygame.draw.lines(self.surf, b3, False, m)
            y += 1
            y.clip(0, play_h)'''
        # Body gradient
        for i in range(4, game_h):
            m = np.column_stack((x, y))
            # pygame.draw.lines(self.surf, b4, False, m)
            pygame.draw.lines(self.image, (150, 150, 150, 255), False, m)
            # pygame.draw.lines(self.surf, b4, False, m)
            green_val -= 0.3
            y += 1
            y.clip(0, game_h)

        # get mask after drawing complete
        self.mask = pygame.mask.from_surface(self.image, 254)

