import time
from matplotlib import pyplot

start = 0
end = 5 * 60        # 5 mins in seconds.
peak = 10           # Per second.


def get_eq(x, y, xint1, xint2):
	return lambda real_x: (y/((x-xint1)*(x-xint2))) * (real_x-xint1)*(real_x-xint2)

"""
when x=end/2, y=peak    <- Maximum.
when x=start, y=0   <- y intercept.
when x=end, y=0     <- x intercepts.
"""

equation = get_eq((end-start)/2, peak, start, end)
plot_arr = []
for i in range(start, end):
	plot_arr.append(equation(i))

pyplot.plot(list(range(start, end)), plot_arr)
pyplot.show()




