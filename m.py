#!/usr/bin/env python
#! -*- coding: utf-8 -*-
"""
https://superfastpython.com/multiprocessing-queue-in-python/
"""

import time
import random
from multiprocessing import Process
from multiprocessing import Queue
 
# generate work
def producer(queue, p):
    print('Producer {}: Running'.format(p), flush=True)
    # generate work
    for i in range(10):
        # generate a value
        value = "{}-{}".format(p, random.randint(1,20))

        print("{}> val: {}".format(p, value))
        # block
        time.sleep(1)

        # add to the queue
        queue.put(value)
    # all done
    if p == "p3":
        queue.put(None)

    print('Producer {}: Done'.format(p), flush=True)
 
# consume work
def consumer(queue):
    print('Consumer: Running', flush=True)
    # consume work
    while True:
        # get a unit of work
        item = queue.get()
        # check for stop
        if item is None:
            break
        # report
        time.sleep(1)
        print(f'<q> value {item}', flush=True)
    # all done
    print('Consumer: Done', flush=True)
 
# entry point
if __name__ == '__main__':
    # create the shared queue
    queue = Queue()

    # start the consumer
    #consumer_process = Process(target=consumer, args=(queue,))
    #consumer_process.start()

    
    # start the producer
    p_list = []
    for i in range(4):
        pname = "p{}".format(i)
        p = Process(target=producer, args=(queue, pname))
        p.start()
        p_list.append(p)


    # wait for all processes to finish
    for p in p_list:
        p.join()

    #print("join consumer")
    #consumer_process.join()

    print("okay")
    #queue.put(None)
    #consumer(queue)

    c_list = []
    for i in range(2):
        pname = "c{}".format(i)
        p = Process(target=consumer, args=(queue,))
        p.start()
        c_list.append(p)
    for c in c_list:
        c.join()




    print("Later")
