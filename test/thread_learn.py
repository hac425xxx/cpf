from queue import Queue
from time import sleep
from threading import Thread
import time

q = Queue(maxsize=20)


def use():
    while True:
        i = q.get()
        print i


def give():
    while True:
        sleep(3)
        q.put(time.time())


if __name__ == '__main__':
    u = Thread(target=use)
    g = Thread(target=give)
    g.start()
    u.start()

    sleep(30)
