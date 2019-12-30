import math
import random
import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt

# random coefficients for the main noise generator
a = [15731, 16703, 23143, 19843, 12744, 97586, 36178, 88412, 78436, 78436, 96653, 12598, 32158, 98764, 11579, 65989,
     13647, 36987, 16467, 16798]
b = [789221, 794711, 793139, 799259, 842555, 674336, 947264, 654158, 984378, 867943, 116871, 157998, 369876, 679481,
     559852, 989797, 364984, 123654, 698749, 914672]
c = [1376328799, 1376312589, 1376324099, 1376312881, 5748234489, 3621789547, 9785412268, 1577894552, 1478965784,
     3695784298,
     1918767419, 7894976813, 1649875310, 1203401615, 9024603100, 6030149475, 6049708410, 1164973489, 6633215899,
     4424784468]

random.shuffle(a)
random.shuffle(b)
random.shuffle(c)

w = 1280
h = 720
hs = h / 8  # height segment
ws = w / 8  # width segment
terrain_type = "Cliff"  # Hill, Valley, Cliff
interpolation_type = 'linear'  # Default

# ----- Generate macro structure of the terrain type chosen ------
# Hill
if terrain_type == "Hill":
    p100 = 0, -random.randint(5 * hs, 7 * hs)  # left edge
    p200 = random.randint(2 * ws, 3 * ws), -random.randint(3 * hs, 5 * hs)  # left curve
    p300 = random.randint(3 * ws, 5 * ws), -random.randint(1 * hs, 3 * hs)  # peak
    p400 = random.randint(5 * ws, 6 * ws), -random.randint(3 * hs, 5 * hs)  # right curve
    p500 = w, -random.randint(5 * hs, 7 * hs)  # right edge
    # add centroids of right angled triangle with p1 / p2 to add to the curve
    pa = p200[0], p100[1]
    pb = p400[0], p500[1]
    p150 = (p100[0] + pa[0] + p200[0]) / 3, (p100[1] + pa[1] + p200[1]) / 3
    p450 = (p400[0] + pb[0] + p500[0]) / 3, (p400[1] + pb[1] + p500[1]) / 3

# Valley
if terrain_type == "Valley":
    p100 = 0, -random.randint(hs, 3 * hs)  # left edge
    p200 = random.randint(2 * ws, 3 * ws), -random.randint(3 * hs, 5 * hs)  # left curve
    p300 = random.randint(3 * ws, 5 * ws), -random.randint(5 * hs, 7 * hs)  # peak
    p400 = random.randint(5 * ws, 6 * ws), -random.randint(3 * hs, 5 * hs)  # right curve
    p500 = w, -random.randint(hs, 3 * hs)  # right edge
    # add centroids of right angled triangle with p1 / p2 to add to the curve
    pa = p200[0], p100[1]
    pb = p400[0], p500[1]
    p150 = (p100[0] + pa[0] + p200[0]) / 3, (p100[1] + pa[1] + p200[1]) / 3
    p450 = (p400[0] + pb[0] + p500[0]) / 3, (p400[1] + pb[1] + p500[1]) / 3

# Cliff
if terrain_type == "Cliff":
    interpolation_type = 'linear'
    ch = random.randint(1 * hs, 3 * hs)  # cliff height
    bh = random.randint(5 * hs, 7 * hs)  # base height
    if random.choice(['fall', 'rise']) == 'fall':  # slope
        p100 = 0, -ch  # left edge
        p200 = random.randint(3 * ws, 4 * ws), -ch  # plateau ends here
        p300 = w / 2, - h / 2  # centered with the screen
        p400 = random.randint(4 * ws, 5 * ws), -bh  # base starts here
        p500 = w, -bh  # right edge
        # add centroids of right angled triangle with p1 / p2 to add to the curve
        pa = p200[0], p100[1]
        pb = p400[0], p500[1]
        p150 = (p100[0] + pa[0] + p200[0]) / 3, (p100[1] + pa[1] + p200[1]) / 3
        p450 = (p400[0] + pb[0] + p500[0]) / 3, (p400[1] + pb[1] + p500[1]) / 3

    else:
        p100 = 0, -bh  # left edge
        p200 = random.randint(3 * ws, 4 * ws), -bh  # base ends here
        p300 = w / 2, -h / 2  # centered with the screen
        p400 = random.randint(4 * ws, 5 * ws), -ch  # plateau starts here
        p500 = w, -ch  # right edge
        # add centroids of right angled triangle with p1 / p2 to add to the curve
        pa = p200[0], p100[1]
        pb = p400[0], p500[1]
        p150 = (p100[0] + pa[0] + p200[0]) / 3, (p100[1] + pa[1] + p200[1]) / 3
        p450 = (p400[0] + pb[0] + p500[0]) / 3, (p400[1] + pb[1] + p500[1]) / 3

inflexion_points = [p100, p150, p200, p300, p400, p450, p500]
macro_terrain_points = np.array(inflexion_points).T
x0 = macro_terrain_points[0]
y0 = macro_terrain_points[1]
xnew = np.arange(1, 1281, 1)
fun = interpolate.interp1d(x0, y0, interpolation_type)
ynew = fun(xnew)


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


def smoothed_noise(x: float, i: int):
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
    p = 1  # persistence
    n = 16  # Number_Of_Octaves - 1

    for i in range(1, n):
        frequency = 2 * i
        amplitude = p * i
        total = total + interpolated_noise(x * frequency, i) * amplitude

    return total


perlin_vec = np.vectorize(perlin_noise)

xarr = np.arange(1, 1281, 1)
yarr = perlin_vec(xarr)
# plt.plot(xarr, yarr)  # plot the noise
# plt.plot(x0, y0, 'o', xnew, ynew, '-')  # plot the macro terrain
plt.plot(x0, y0, 'o', xnew, ynew + yarr, '-')  # final plot - terrain + noise
plt.ylim(-720, 1)
# plt.xlim(1, 72)
plt.show()
