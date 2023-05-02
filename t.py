#!/usr/bin/env python
#! -*- coding: utf-8 -*-

# SuperFastPython.com
# example of running a function in another thread
import time
from threading import Thread



# a custom function that blocks for a moment
def task(t, max_cnt):
    print("<{}> started".format(t), flush=True)
    done = False
    cnt = 0
    while not done:
        cnt += 1

        print("<{}> {}".format(t, cnt), flush=True)
        time.sleep(1)

        if cnt > max_cnt:
            done = True
 
##-----------------------

# create threads

t_list = []
for t in range(4):
    thread = Thread(target=task, args=(t,10))
    t_list.append(thread)

    # run the thread
    thread.start()

# do my own thing
task("main", 10)

# wait for the thread to finish
print('Waiting for the threads to finish ...')
for t in t_list:
    t.join()


