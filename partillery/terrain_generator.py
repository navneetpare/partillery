import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline


def noise(x):
    x = (x << 13) ^ x
    return 2.0 - ((x * (x * x * 15731 + 789221) + 1376312589) & 2147483647) / 1073741824.0


h = 720
xarr_0 = np.arange(1, 33, 1)
xarr = np.arange(1, 1281, 40)  # X-axis, zoomed out 40x
yarr = np.empty(32) # Y-axis, empty, zoomed out 40x
for i in range(32): # Fill Y values with noise fun.
    yarr[i - 1] = int(noise(i) * h / 2)

track = np.column_stack((xarr_0, yarr))
track = track.astype('int32')

# https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.interpolate.CubicSpline.html
cs = CubicSpline(xarr, yarr)  # Cubic spline using discrete samples (xarr[i], yarr[i])
xs = np.arange(1, 1281, 1)  # X axis, full width of screen
ys = cs(xs)

track = np.column_stack((xs, ys))
track = track.astype('int32')

print(track)

plt.figure(figsize=(6.5, 4))
plt.plot(xarr, yarr, label='non-interpolated')
plt.plot(xs,ys, label="first spline")
plt.plot(xs, cs(xs, 1), label="S'")
plt.plot(xs, cs(xs, 2), label="S''")
plt.plot(xs, cs(xs, 3), label="S'''")
plt.xlim(1, 1281)
plt.legend(loc='lower left', ncol=2)
plt.show()


