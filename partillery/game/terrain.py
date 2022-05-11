# Terrain layer thickness needs to be pixel based.
# Drawing vertical segments does not account for slope.
# http://geomalgorithms.com/a13-_intersect-4.html

# 11/04/2020 - Divide the terrain vertically into slats. Each will have its own mask.
import time
import timeit
from collections import OrderedDict

import pygame
from pygame import Rect
import math
import random
import numpy as np
from scipy import interpolate

# import matplotlib.pyplot as plt

# Colours

snow = 150, 150, 150
g1 = 0, 180, 0  # green opaque
g2 = 0, 150, 0  # green opaque
g3 = 0, 120, 0  # green opaque
g4 = 0, 90, 0  # green opaque
g5 = 0, 60, 0  # green opaque

# --- awesome palette
teal = 56, 104, 80
b1 = 240, 192, 160
b2 = 152, 112, 80
b3 = 112, 80, 48
b4 = 56, 16, 0

d1_for_purple = 21, 21, 21

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
    interpolation_type = 'linear'  # Default

    if terrain_type == "Random":
        terrain_type = random.choice(['Valley', 'Hill', 'Cliff'])
        # terrain_type = 'Hill'
        # interpolation_type = 'linear'  # Default
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
            # interpolation_type = 'linear'
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
        y_arr = np.ones(w) * 550

    return y_arr  # only need the y coords; x is implicit as array index - 1

    # Debug only
    # plt.plot(x0, y0, 'o', x_arr, y_arr, '-')
    # plt.ylim(-720, 1)
    # plt.xlim(1, 72)
    # plt.show()


def get_display_update_area(area):
    return Rect(area.left, 0, area.w, area.bottom)


def get_optimal_display_update_areas(columns: OrderedDict):
    contiguous_columns = []
    rect_list = []
    if len(columns) > 0:
        cols = columns.items()
        done = False
        x_start = next(iter(cols))[0]  # first x in cols
        x_prev = x_start
        x_end = next(reversed(cols))[0]
        cols = columns.items()
        for x, (bottom, top) in cols:
            if x == x_start:
                pass
            elif x == x_end:
                contiguous_columns.append((x_start, x))
            else:
                if x - x_prev == 1:
                    x_prev = x
                else:
                    contiguous_columns.append((x_start, x_prev))
                    x_start = x
                    x_prev = x

        if len(contiguous_columns) > 0:
            for i in range(len(contiguous_columns)):
                current_tuple = contiguous_columns[i]

                x = current_tuple[0]  # left edge
                w = current_tuple[1] - current_tuple[0]

                # find highest y in contiguous column
                top = None
                bottom = None
                for j in range(current_tuple[0], current_tuple[1] + 1):  # +1 to include rightmost column too
                    current_bottom = columns[current_tuple[0]][0]
                    current_top = columns[current_tuple[0]][1]
                    if j == current_tuple[0]:
                        top = current_top
                        bottom = current_bottom
                    else:
                        if current_bottom > bottom:  # check bottoms
                            bottom = current_bottom
                        if current_top < top:
                            top = current_top

                y = top
                h = bottom - top
                rect = Rect(x, y, w, h)
                rect_list.append(rect)
                print(rect)
                print(top)
                print(bottom)

    print(contiguous_columns)
    return rect_list


class Terrain:
    def __init__(self, game, game_w, game_h, terrain_type):
        # Create a layer for terrain, with per-pixel alpha allowed
        # print('Terr gen start ' + str(pygame.time.get_ticks()))
        self.is_falling = False
        self.game = game
        self.w = game_w
        self.game_h = game_h
        self.image = pygame.Surface((game_w, game_h), pygame.SRCALPHA)
        # print('Generate method start ' + str(pygame.time.get_ticks()))
        self.y_coordinates = generate(game_w, game_h, terrain_type)  # only y coords
        # print('Generate method end ' + str(pygame.time.get_ticks()))
        x = np.arange(1, game_w + 1, 1)  # just temp
        # self.points = np.array((x, self.y_coordinates)).T
        self.points = None

        # temp y array which will be moved downwards for painting layers of terrain
        y = np.array(self.y_coordinates)  # for fast numpy methods

        green_val = 255
        # Top crust
        for i in range(1, 20):
            m = np.column_stack((x, y))
            # pygame.draw.lines(self.surf, b1, False, m)
            pygame.draw.lines(self.image, snow, False, m)
            y += 1
            y.clip(0, game_h)
        for i in range(20, 60):
            m = np.column_stack((x, y))
            pygame.draw.lines(self.image, teal, False, m)
            y += 1
            y.clip(0, game_h)
        for i in range(60, 100):
            m = np.column_stack((x, y))
            pygame.draw.lines(self.image, teal, False, m)
            y += 1
            y.clip(0, game_h)
        # Body gradient
        for i in range(100, game_h):
            m = np.column_stack((x, y))
            # pygame.draw.lines(self.surf, b4, False, m)
            pygame.draw.lines(self.image, teal, False, m)
            # pygame.draw.lines(self.surf, b4, False, m)
            green_val -= 0.3
            y += 1
            y.clip(0, game_h)

        # get mask after drawing complete
        self.mask = pygame.mask.from_surface(self.image, 254)
        # print('Compute initial start ' + str(pygame.time.get_ticks()))
        self.compute_terrain_points()
        # print('Compute initial end ' + str(pygame.time.get_ticks()))

    def compute_terrain_points(self):
        # find first pixel in each continuous terrain area
        floor_y = self.game_h - 1
        tracking = self.mask.get_at((1, floor_y))
        start_points = [((1, floor_y), tracking)]
        for i in range(2, self.w):
            mask = self.mask.get_at((i, floor_y))
            if mask == tracking:
                pass
            else:
                tracking = mask
                start_points.append(((i, floor_y), tracking))

        print('--- start points ---')
        print(start_points)

        # last_mask = self.mask.get_at(self.w-1, bottom)
        # if last_mask != tracking:
        #     start_points.append(self.w-1, bottom)
        masks = []
        outlines = []
        trimmed_outlines = []
        final_terrain_points = []
        for start_point in start_points:
            if start_point[1] == 1:  # i.e. terrain is filled from this point
                masks.append(self.mask.connected_component(start_point[0]))
        print('--- masks ---')
        print(masks)
        for mask in masks:
            outlines.append(mask.outline())
        print('--- raw outlines ---')
        print(outlines)
        for outline in outlines:
            trimmed_outlines.append(self.trim_outline(outline))
        print('--- trimmed outlines ---')
        print(trimmed_outlines)
        for i in range(len(trimmed_outlines)):
            if len(final_terrain_points) == 0:
                if trimmed_outlines[i][0][0] > 1:
                    final_terrain_points.extend(self.filler(-1, trimmed_outlines[i][0][0]))
                final_terrain_points.extend(trimmed_outlines[i])
            else:
                # fill the gap between last outline and this outline as terrain floor
                last_x_of_prev_list = final_terrain_points[-1][0]
                first_x_of_current_list = trimmed_outlines[i][0][0]
                final_terrain_points.extend(self.filler(last_x_of_prev_list, first_x_of_current_list))
                final_terrain_points.extend(trimmed_outlines[i])

        if final_terrain_points[-1][0] < self.w - 1:
            final_terrain_points.extend(self.filler(final_terrain_points[-1][0], self.w))

        self.points = final_terrain_points
        print('--- final points ---')
        print(self.points)

    def filler(self, left_x, right_x):
        # generates filler 'between' two points, exlusive of both
        floor_y = self.game_h - 1
        x_array = np.arange(left_x + 1, right_x, dtype=int)
        y_array = np.ones(right_x - left_x - 1) * floor_y
        arr = np.column_stack((x_array, y_array)).tolist()
        return arr

    def trim_outline(self, outline: list) -> list:
        # https://stackoverflow.com/questions/25823608/find-matching-rows-in-2-dimensional-numpy-array
        floor_y = self.game_h - 1
        outline_arr = np.array(outline, dtype=int)
        print(outline_arr)
        outline_floor = outline_arr[(outline_arr[:, 1] == floor_y)]
        outline_floor_index_of_left = np.argmin(outline_floor, axis=0)[0]
        outline_floor_index_of_right = np.argmax(outline_floor, axis=0)[0]
        outline_floor_left_x = outline_floor[outline_floor_index_of_left][0]
        outline_floor_right_x = outline_floor[outline_floor_index_of_right][0]
        outline_index_of_left = np.where((outline_arr[:, 0] == outline_floor_left_x) & (outline_arr[:, 1] == floor_y))[0]
        outline_index_of_right = np.where((outline_arr[:, 0] == outline_floor_right_x) & (outline_arr[:, 1] == floor_y))[0]
        outline_arr_slice_1 = outline_arr[int(outline_index_of_left):, :]
        outline_arr_slice_2 = outline_arr[:int(outline_index_of_right) + 1, :]
        points_arr = np.vstack((outline_arr_slice_1, outline_arr_slice_2))

        # handle screen left and right edges
        if tuple(points_arr[0]) == (1, floor_y):
            top_index_of_left_screen_edge = np.where(points_arr[:, 0] == 1)[0][-1]
            points_arr = points_arr[top_index_of_left_screen_edge:]
            # print(points_arr)

        if tuple(points_arr[-1]) == (self.w - 1, floor_y):
            top_index_of_right_screen_edge = np.where(points_arr[:, 0] == self.w - 1)[0][0]
            points_arr = points_arr[: top_index_of_right_screen_edge + 1]
            # print(points_arr)

        points = points_arr.tolist()
        return points

    def get_point(self, x):
        for point in self.points:
            if point[0] == x:
                return point

    def get_point_index(self, x):
        for i in range(len(self.points)):
            if self.points[i][0] == x:
                return i

    def fall(self, area: pygame.Rect):
        if area is not None:
            self.is_falling = True
            print('game_h:' + str(self.game_h))
            columns = self.get_columns_with_holes(area)
            update_area = get_display_update_area(area)

            deleted_columns = []
            while len(columns) > 0:
                for x in deleted_columns:
                    del columns[x]  # Remove columns queued for removal
                deleted_columns.clear()  # empty the list to prevent re-deletion error
                for x, (bottom, top) in columns.items():  # For each column
                    i = 0

                    bottom_new = min(bottom, self.game_h - 2)  # exlude pixels which touch game bottom
                    for y in range(bottom_new, top - 2, -1):  # shift down all pixels in the column
                        i += self.fall_pixel((x, y))

                    if i == 0:  # if nothing moved in the column:
                        deleted_columns.append(x)  # queue the column for removal

                    else:
                        columns[x] = (bottom, top + 1)
                        self.y_coordinates[x] += 1

                pygame.display.update(update_area)

            self.is_falling = False

    def get_columns_with_holes(self, area: pygame.Rect):
        columns = OrderedDict()
        # Find list of x where terrain has holes
        for x in range(area.left, area.right):
            has_terrain = False
            has_hole = False
            top = None
            bottom = None
            for y in range(0, area.bottom):
                if self.mask.get_at((x, y)) == 1:
                    has_terrain = True
                    top = y
                    break
            if top is not None:
                for y in range(top, area.bottom):
                    if self.mask.get_at((x, y)) == 0:
                        has_hole = True
                        break
                for y in range(area.bottom, top, -1):
                    if self.mask.get_at((x, y)) == 0:
                        bottom = y
                        break
            if has_terrain and has_hole:
                columns.update({x: (bottom, top)})
        return columns

    def fall_pixel(self, pixel):
        # print('pixel: ' + str(pixel))
        pixel_below = pixel[0], pixel[1] + 1
        mask_pixel = self.mask.get_at(pixel)
        mask_below = self.mask.get_at(pixel_below)
        if mask_below == 0:  # If no terrain below
            self.mask.set_at(pixel_below, mask_pixel)  # shift terrain pixel mask
            self.mask.set_at(pixel, 0)  # Leave transparency behind for the next pixel to fall
            if mask_pixel == 0:
                col = self.game.sky.get_at(pixel)
            else:
                col = self.game.screen.get_at(pixel)
            self.game.screen.set_at(pixel_below, col)
            self.game.scene.set_at(pixel_below, col)
            return 1
        else:
            return 0
