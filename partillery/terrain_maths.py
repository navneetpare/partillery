import math
import random
import numpy as np
from scipy.interpolate import CubicSpline
from scipy import interpolate
import matplotlib.pyplot as plt

a = [15731, 16703, 23143, 19843, 12744, 97586, 36178, 88412, 78436, 78436, 96653, 12598, 32158, 98764, 11579, 65989,
     13647, 36987, 16467, 16798]
b = [789221, 794711, 793139, 799259, 842555, 674336, 947264, 654158, 984378, 867943, 116871, 157998, 369876, 679481,
     559852, 989797, 364984, 123654, 698749, 914672]
c = [1376328799, 1376312589, 1376324099, 1376312881, 5748234489, 3621789547, 9785412268, 1577894552, 1478965784,
     3695784298,
     1918767419, 7894976813, 1649875310, 1203401615, 9024603100, 6030149475, 6049708410, 1164973489, 6633215899,
     4424784468]

'''print(a)
print(b)
print(c)'''

random.shuffle(a)
random.shuffle(b)
random.shuffle(c)

''' print(a)
print(b)
print(c) '''

w = 1280
h = 720
hs = h / 8  # height segment
ws = w / 8  # width segment
terrain_type = "Hill"  # Hill, Valley, Cliff

# Hill
if terrain_type == "Hill":
    p1 = 0, -random.randint(5 * hs, 7 * hs)  # left edge
    p2 = random.randint(ws, 3 * ws), -random.randint(3 * hs, 5 * hs)  # left curve
    p3 = random.randint(3 * ws, 5 * ws), -random.randint(1 * hs, 3 * hs)  # peak
    p4 = random.randint(5 * ws, 7 * ws), -random.randint(3 * hs, 5 * hs)  # right curve
    p5 = w, -random.randint(5 * hs, 7 * hs)  # right edge

# Valley
if terrain_type == "Valley":
    p1 = 0, -random.randint(hs, 3 * hs)  # left edge
    p2 = random.randint(ws, 3 * ws), -random.randint(3 * hs, 5 * hs)  # left curve
    p3 = random.randint(3 * ws, 5 * ws), -random.randint(5 * hs, 7 * hs)  # peak
    p4 = random.randint(5 * ws, 7 * ws), -random.randint(3 * hs, 5 * hs)  # right curve
    p5 = w, -random.randint(hs, 3 * hs)  # right edge

# Cliff
if terrain_type == "Cliff":
    ch = random.randint(1 * hs, 3 * hs)  # cliff height
    bh = random.randint(5 * hs, 7 * hs)  # base height
    if random.choice(['fall', 'rise']) == 'fall': # slope
        p1 = 0, -ch  # left edge
        p2 = random.randint(3 * ws, 4 * ws), -ch  # plateau ends here
        p3 = w / 2, - h / 2  # centered with the screen
        p4 = random.randint(4 * ws, 5 * ws), -bh  # base starts here
        p5 = w, -bh  # right edge
    else:
        p1 = 0, -bh  # left edge
        p2 = random.randint(3 * ws, 4 * ws), -bh  # base ends here
        p3 = w / 2, -h / 2  # centered with the screen
        p4 = random.randint(4 * ws, 5 * ws), -ch  # plateau starts here
        p5 = w, -ch  # right edge


inflexion_points = [p1, p2, p3, p4, p5]
print(inflexion_points)
macro_terrain_points = np.array(inflexion_points).T
x0 = macro_terrain_points[0]
y0 = macro_terrain_points[1]
xnew = np.arange(1, 1281, 1)
cs = CubicSpline(x0, y0)
fun = interpolate.interp1d(x0, y0, 'linear')
ynew = fun(xnew)

# def macro_terrain(x: int):
xs = np.arange(1, 1281, 1)  # X axis, full width of screen
ys = cs(xs)


def cubic_interpolation(v0, v1, v2, v3, x):
    P = (v3 - v2) - (v0 - v1)
    Q = (v0 - v1) - P
    R = v2 - v0
    S = v1
    return P * (x ** 3) + Q * (x ** 2) + R * x + S


def cosine_interpolation(a, b, x):
    ft = x * 3.1415927
    f = (1 - math.cos(ft)) * .5
    return a * (1 - f) + b * f


def noise(x: int, i: int):
    x = (x << 13) ^ x
    return ((x * (x * x * a[i] + b[i]) + c[i]) & 2147483647) / 1073741824.0


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
    p = 0.5  # persistence
    n = 14 # Number_Of_Octaves - 1

    for i in range(1, n):
        frequency = 2 * i
        amplitude = (p * i)
        total = total + interpolated_noise(x * frequency, i) * amplitude

    return total * 5


perlin_vec = np.vectorize(perlin_noise)

xarr = np.arange(1, 1281, 1)
yarr = perlin_vec(xarr)
# plt.plot(xarr, yarr)
# plt.plot(*zip(*inflexion_points), label='macro terrain discrete')
# plt.plot(xs, ys, label='macro terrain cubic spline')
# plt.plot(x0, y0, 'o', xnew, ynew, '-')
plt.plot(x0, y0, 'o', xnew, ynew + yarr - 100, '-')

plt.ylim(-720, 0)
# plt.xlim(1, 72)
plt.show()
