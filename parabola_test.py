from matplotlib import pyplot
import numpy

start = 0
end = 15    #5 * 60  # 5 mins in seconds.
spin_up = 0.30  # Percentage.
peak = 3  # Concurrent Requests.


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
    def func(x):
        # Out of range.
        if x < start or x > start + acceleration_space + peak_duration + acceleration_space:
            return 0
        # Up tick.
        elif x < start + 0.5*acceleration_space:
            # vertex
            vertex_x = start
            vertex_y = 0
            # point
            point_x = start + (acceleration_space/2)
            point_y = max_height / 2
            return parabola_constructor(vertex_x, vertex_y, point_x, point_y)(x)
        # Curve to flat
        elif x < start + acceleration_space:
            # vertex
            vertex_x = start + acceleration_space
            vertex_y = max_height
            # point
            point_x = start + (acceleration_space / 2)
            point_y = max_height / 2
            return parabola_constructor(vertex_x, vertex_y, point_x, point_y)(x)
        # Steady peak.
        elif x < start + acceleration_space + peak_duration:
            return max_height
        # Curve down
        elif x < start + acceleration_space + peak_duration + 0.5*acceleration_space:
            # vertex
            vertex_x = start + acceleration_space + peak_duration
            vertex_y = max_height
            # point
            point_x = start + acceleration_space + peak_duration + (acceleration_space / 2)
            point_y = max_height / 2
            return parabola_constructor(vertex_x, vertex_y, point_x, point_y)(x)
        # Back to flat
        else:
            # vertex
            vertex_x = start + acceleration_space + peak_duration + acceleration_space
            vertex_y = 0
            # point
            point_x = start + acceleration_space + peak_duration + (acceleration_space / 2)
            point_y = max_height / 2
            return parabola_constructor(vertex_x, vertex_y, point_x, point_y)(x)

    return func


def parabola_constructor(peak_x, peak_y, ax, ay):
    a = (ay-peak_y)/(ax-peak_x)**2
    return lambda x: a*((x-peak_x)**2) + peak_y

"""
when x=end/2, y=peak    <- Maximum.
when x=start, y=0   <- y intercept.
when x=end, y=0     <- x intercepts.
"""

accel_time = (end-start)*spin_up
duration = end-start-2*accel_time
equation = get_built_func(start, accel_time, peak, duration)

spacer = 0.01
plot_arr = []
for j in numpy.arange(start, end, spacer):
    plot_arr.append(equation(j))

fig = pyplot.figure()
ax = fig.gca()
ax.set_xticks(numpy.arange(start, end+end/10, (end-start)/10))
ax.set_yticks(numpy.arange(0, peak+peak/10, peak/10))
pyplot.plot(list(numpy.arange(start, end, spacer)), plot_arr, "-bD",
            markevery=[0, -1, round((start+accel_time)/spacer), round((start+accel_time+duration)//spacer)])
pyplot.grid()
pyplot.show()
