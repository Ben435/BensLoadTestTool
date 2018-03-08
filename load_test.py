import requests
import time
import multiprocessing.pool
import threading
import queue

# SSO Server.
# url = 'https://swapme-sso.appspot.com/proxy/?sso'

# Backend Server.
# url = 'https://swapme-backend-dev.appspot.com/emails/api/put_email'

# Frontend Server.
# url = 'https://monash-swapme-dev.appspot.com/'

# MIX
# url = 'https://mix.monash.edu/v1/id-xref/id'
# url = 'https://mix-qat.monash.edu/v1/id-xref/id'

# Incapsula URL
url = "https://swapme.apps.monash.edu"


def single():
    print("Running GET single on {}...".format(url))
    max_time = 0
    hits = 0
    while True:
        try:
            init_time = time.time()
            response = requests.get(url)
            end_time = time.time() - init_time
            if max_time < end_time:
                max_time = end_time
            if response.status_code != 200:
                print("Error...")
            hits += 1
            print(".", end='', flush=True)
        except KeyboardInterrupt:
            break
    print("\nMax Response Time: {}ms\nHits: {}".format(max_time / 1000, hits))


def multi(senders, reqs_per_sender=100):
    print("Running GET multi on {}...".format(url))
    pool = multiprocessing.pool.ThreadPool(senders)
    run = True
    time_queue = queue.PriorityQueue()

    def todo(calls):
        max_time = 0
        while run and calls > 0:
            init_time = time.time()
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    print("?", end='', flush=True)
                    print(response.status_code)
            except ConnectionError:
                print("!", end='', flush=True)
            finally:
                end_time = time.time() - init_time
                if end_time > max_time:
                    max_time = end_time
                if calls % 10 == 0:
                    print(".", end='', flush=True)
                calls -= 1
        print("#", end='', flush=True)
        time_queue.put((-max_time, max_time))

    pool.map(todo, [reqs_per_sender] * senders)
    print("\nMax Time: {}ms".format(round(time_queue.get()[1] * 1000)))


def post_multi(senders, reqs_per_sender=100):
    print("Running POST multi on {}...".format(url))
    test_form = {
        'id': '12345678',
        'name': 'Tester Testman',
        'to_address': 'test@test',

        'email_type': 'submitted',
        'from_class': '01',
        'to_class': '02',

        'unit': 'TST1234',
        'class_type': 'Laboratory',

    }
    pool = multiprocessing.pool.ThreadPool(senders)
    run = True
    time_queue = queue.PriorityQueue()

    def todo(calls):
        max_time = 0
        while run and calls > 0:
            init_time = time.time()
            try:
                response = requests.post(url, test_form)
                if response.status_code != 200:
                    print("?", end='', flush=True)
                elif calls % 10 == 0:
                    print(".", end='', flush=True)
            except ConnectionError:
                print("!", end='', flush=True)
            finally:
                end_time = time.time() - init_time
                if end_time > max_time:
                    max_time = end_time
                calls -= 1
        print("#", end='', flush=True)
        time_queue.put((-max_time, max_time))

    pool.map(todo, [reqs_per_sender] * senders)
    print("\nMax Time: {}ms".format(round(time_queue.get()[1] * 1000)))


def mix_multi(senders, reqs_per_sender=100):
    print("Running MIX QA on {}...".format(url))
    pool = multiprocessing.pool.ThreadPool(senders)
    run = True
    time_queue = queue.PriorityQueue()
    avg_queue = queue.Queue()

    def todo(calls):
        max_time = 0
        while run and calls > 0:
            init_time = time.time()
            try:
                response = requests.get(url, args, headers=headers)
                if response.status_code != 200:
                    print(response.json())
                    print("?", end='', flush=True)
                elif calls % 10 == 0:
                    print(".", end='', flush=True)
            except ConnectionError:
                print("!", end='', flush=True)
            finally:
                end_time = time.time() - init_time
                if end_time > max_time:
                    max_time = end_time
                calls -= 1
                avg_queue.put(end_time)
        print("#", end='', flush=True)
        time_queue.put((-max_time, max_time))

    pool.map(todo, [reqs_per_sender] * senders)
    avg_sum = 0
    avg_len = avg_queue.qsize()
    while not avg_queue.empty():
        avg_sum += avg_queue.get()
    print("\nMax Time: {}ms\nAvg Time: {}ms".format(round(time_queue.get()[1] * 1000), round((avg_sum / avg_len) * 1000)))


def pre_scale(senders, reqs_per_sender=100):
    print("Running pre-scale on {}...".format(url))
    landing_js = "/static/js/landing/main.a3ef395c.js"
    landing_css = "/static/css/landing/main.04a5dc04.css"
    student_js = "/static/js/student/main.e9800e02.js"
    student_css = "/static/css/student/main.d34f0cb0.css"
    all_urls = [landing_js, landing_css, student_js, student_css]

    pool = multiprocessing.pool.ThreadPool(senders)
    run = True
    time_queue = queue.PriorityQueue()
    avg_queue = queue.Queue()

    def todo(details):
        max_time = 0
        calls = details[0]
        path = details[1]
        while run and calls > 0:
            init_time = time.time()
            try:
                response = requests.get(url + path)
                if response.status_code != 200:
                    print("?", end='', flush=True)
                elif calls % 10 == 0:
                    print(".", end='', flush=True)
            except ConnectionError:
                print("!", end='', flush=True)
            finally:
                end_time = time.time() - init_time
                if end_time > max_time:
                    max_time = end_time
                calls -= 1
                avg_queue.put(end_time)
        print("#", end='', flush=True)
        time_queue.put((-max_time, max_time))

    final = ((reqs_per_sender, all_urls[i % len(all_urls)]) for i in range(senders))
    pool.map(todo, final)
    avg_sum = 0
    avg_len = avg_queue.qsize()
    while not avg_queue.empty():
        avg_sum += avg_queue.get()
    print(
        "\nMax Time: {}ms\nAvg Time: {}ms".format(round(time_queue.get()[1] * 1000), round((avg_sum / avg_len) * 1000)))


def send_over_time(per_sec, duration):
    print("Running {} per second over {} seconds on {}...".format(per_sec, duration, url))
    pool = []

    def make_req(headers=None, args=None):
        while True:
            cur = work_queue.get()
            if cur is None:
                break
            # print("↑", end='', flush=True)
            s = time.time()
            # print("{} started at {}...".format(threading.current_thread().name, s))
            try:
                response = requests.get(url, args, headers=headers)
                if response.status_code != 200:
                    print("?", end='', flush=True)
                else:
                    # print("↓", end='', flush=True)
                    pass
            except ConnectionError:
                print("!", end='', flush=True)
            except Exception:
                print("~", end='', flush=True)
            finally:
                end_time = time.time()
                time_queue.put((s, end_time - s))
                work_queue.task_done()

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
            work_queue.put(1)
            next_block += (1 / per_sec)
        cur += time.time() - cur
    # Finish.
    work_queue.join()
    for i in range(per_sec):
        work_queue.put(None)
    for t in pool:
        t.join()

    # Get results.
    sum_times = 0
    max_time = 0
    len_times = 0
    times = []
    while not time_queue.empty():
        occured_time, cur_time = time_queue.get()
        if cur_time > max_time:
            max_time = cur_time
        sum_times += cur_time
        len_times += 1
        times.append([occured_time - start_time, cur_time])
    print("\nMax Time: {}ms\nAvg Time: {}ms".format(round(max_time * 1000),
                                                    round((sum_times / len_times) * 1000)))

    return times


# multi(300, 100)
# multi(10, 10)
# post_multi(10, 10)
# mix_multi(100, 100)
# pre_scale(50, 50)

work_queue = queue.Queue()
time_queue = queue.Queue()

duration = 30
times = send_over_time(5, duration)
times = sorted(times, key=lambda a: a[0])

# from matplotlib import pyplot
#
# x = []
# y = []
# for i in range(len(times)):
# 	x.append(times[i][0])
# 	y.append(times[i][1])
# mid_y = sum(y)/len(y)
#
# pyplot.plot(x, y, 'bo')
# pyplot.plot(list(range(0, round(max(x)))), [mid_y]*round(max(x)), 'r-')
# pyplot.ylabel('latency (s)')
# pyplot.xlabel('time (s)')
# pyplot.xlim((0, duration))
# pyplot.grid(True)
#
# pyplot.tight_layout(1)
# pyplot.show()
