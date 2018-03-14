import matplotlib

matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import style, animation
import tkinter
from tkinter import ttk
import time
import requests
import threading
import multiprocessing
from bad_requests import requests as breqs

LARGE_FONT = ("Verdana", 12)
style.use("ggplot")

f = Figure(figsize=(5, 5), dpi=100)
a = f.add_subplot(111)

duration = 60
rate = 80
runs = 0

all_points = []
work_queue = multiprocessing.JoinableQueue()
time_queue = multiprocessing.Queue()
# url = "https://swapme.apps.monash.edu"
# url = "https://monash-swapme-dev.appspot.com"
url = "https://monplan.apps.monash.edu"
#url = "http://monplan-api-dev.appspot.com/units/FIT3047"


def animate(i):
    global all_points
    while not time_queue.empty():
        all_points.append(time_queue.get())
    # all_points = sorted(all_points, key=lambda cur: cur[0])
    xList = []
    yList = []
    y_sum = 0
    for x, y in all_points:
        xList.append(x)
        yList.append(y)
        y_sum += y
    if len(yList) > 0:
        avg_y = round(y_sum / len(yList), 3)
    else:
        avg_y = 0

    a.clear()
    # Re-draw
    a.set_ylabel("latency (s)")
    a.set_xlabel("time (s)")
    a.set_ylim([0, (max(yList) + 1) if len(yList) > 0 else 1])
    a.set_xlim([0, duration])
    a.plot(xList, yList, 'bo')
    a.plot([0, duration], [avg_y, avg_y], 'r-')


def send_over_time(per_sec, duration, w_queue, t_queue, headers=None, args=None):
    print("Running {} per second over {} seconds on {}...".format(per_sec, duration, url))
    pool = []

    def make_req(headers=None, args=None):
        while True:
            cur = w_queue.get()
            if cur is None:
                break
            s = time.time()
            try:
                #response = requests.get(url, args, headers=headers)
                response = breqs.get(url, headers=headers)
                if response.status_code != 200:
                    print("?", end='', flush=True)
            except ConnectionError:
                print("!", end='', flush=True)
            except Exception:
                print("~", end='', flush=True)
            finally:
                end_time = time.time()
                t_queue.put((round(s - start_time, 3), round(end_time - s, 3)))
                w_queue.task_done()

    for i in range(per_sec):
        t = threading.Thread(target=make_req, args=[headers, args])
        t.start()
        pool.append(t)

    start_time = time.time()
    cur = time.time()
    next_block = cur + (1 / per_sec)
    end = cur + duration
    while cur < end:
        while cur >= next_block:
            w_queue.put(1)
            next_block += (1 / per_sec)
        cur += time.time() - cur
    # Finish.
    w_queue.join()
    for i in range(per_sec):
        w_queue.put(None)
    for t in pool:
        t.join()

    # Get results.
    times = []
    while not t_queue.empty():
        occured_time, cur_time = t_queue.get()
        times.append([occured_time - start_time, cur_time])

    return times


class GraphDisplay(tkinter.Tk):
    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)

        tkinter.Tk.wm_title(self, "Results Display")

        container = tkinter.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in [GraphPanel]:
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(GraphPanel)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class GraphPanel(tkinter.Frame):
    def __init__(self, parent, controller):
        self.worker = multiprocessing.Process(target=send_over_time, args=[5, duration, work_queue, time_queue])
        tkinter.Frame.__init__(self, parent)
        label = tkinter.Label(self, text="Graph Page!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        def button_func():
            global all_points
            if not self.worker.is_alive():
                all_points = []
                # Re-create worker.
                self.worker = multiprocessing.Process(target=send_over_time,
                                                      args=[rate, duration, work_queue, time_queue])
                self.worker.start()

        button1 = ttk.Button(self, text="Run",
                             command=button_func)
        button1.pack()

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)


if __name__ == "__main__":
    app = GraphDisplay()
    ani = animation.FuncAnimation(f, animate, interval=300)
    app.mainloop()
