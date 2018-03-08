import time
from matplotlib import pyplot
from numpy import arange
from math import pi, e, sqrt

start = 0
end = 15#5 * 60  # 5 mins in seconds.
peak = 10  # Per second.


def get_parab(x, y, xint1, xint2):
    return lambda real_x: (y / ((x - xint1) * (x - xint2))) * (real_x - xint1) * (real_x - xint2)

def get_gauss(a, b, c):
    return lambda x: a*e**-(((x-b)**2)/2*c**2)

def get_dist_gauss(expected_val, variance):
    """
    Distribution style gauss function.
    :param expected_val: the "u" in the formula's.
    :param variance: the "o" in the formula's.
    :return: Function.
    """
    return lambda x: (1/(variance*sqrt(2*pi))) * e ** (-(1/2)*((x-expected_val)/variance)**2)


def get_built_func(start, acceleration_space, max_height, peak_duration):
    """
    Creates an odd semi-gaussian curve with a flat top.
        __
       /  \
    __/    \__
    :param start: Initial point.
    :param acceleration_space: Space to get to peak.
    :param max_height: Peak
    :param peak_duration: Time at peak.
    :return: Function that given an x, returns what height it should be at.
    """
    # TODO: Make acceleration/deceleration smoother.
    def func(x):
        # Out of range.
        if x < start or x > acceleration_space + peak_duration + acceleration_space:
            return 0
        # Up tick.
        elif x < start + 0.5*(2*start + acceleration_space):
            return (x-start)**2
        # Curve to flat
        elif x < start + acceleration_space:
            return -(x-(start + acceleration_space))**2 + max_height
        # Steady peak.
        elif x < start + acceleration_space + peak_duration:
            return max_height
        # Curve down
        elif x < start + acceleration_space + peak_duration + 0.5*(2*start + acceleration_space):
            return -(x-(start + acceleration_space + peak_duration))**2 + max_height
        # Back to flat
        else:
            return (x-(start + acceleration_space + peak_duration + acceleration_space))**2

    return func


"""
when x=end/2, y=peak    <- Maximum.
when x=start, y=0   <- y intercept.
when x=end, y=0     <- x intercepts.
"""

#equation = get_parab((end - start) / 2, peak, start, end)
#equation = get_gauss(peak, (start + end)/2, 0.1)
#equation = get_dist_gauss(0, i)
equation = get_built_func(0, 2, 4, 6)

plot_arr = []
for j in arange(start, end, 0.1):
    plot_arr.append(equation(j))

pyplot.plot(list(arange(start, end, 0.1)), plot_arr)
pyplot.show()
