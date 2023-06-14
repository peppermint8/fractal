#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""
Fractal code
- create either mandelbrot or julia set using single thread or multiprocessing & threading

Mandelbrot set:
https://en.wikipedia.org/wiki/Mandelbrot_set
fx = [-2.00 to 0.47]
fy = [-1.12, 1.12]

Julia set:
https://en.wikipedia.org/wiki/Julia_set
https://scipython.com/book/chapter-7-matplotlib/problems/p72/the-julia-set/


threads share memory, processes do not share memory
- producers cannot access shared memory
- multiprocess.queue must be used up to free multiprocess threads

numpy test
- vectorizing function doesn't help much - 17 sec vs 20 for the loop
- colors using surfarray are odd - can we define what color maps to what value?
- other numpy fractal examples use complex numbers - faster but 800k points?


r = reset to normal coordinates
s = redraw in normal mode
p = redraw in threaded/multiprocessing mode
n = use numpy

use mouse selection to select area to zoom in, then click "s" or "p"

esc to exit

Hide support msg
$ export PYGAME_HIDE_SUPPORT_PROMPT=1

julia ~ 18 sec
no fractal ~ 2 sec


"""

import sys
import math
import pygame
import time
import numpy as np
from threading import Thread
from multiprocessing import Process, Queue, cpu_count
from pygame.locals import *
import pygame.gfxdraw


MAX_CNT = 150 # how detailed the fractal will be
#MAX_CNT = 10

#FRACTAL="mandelbrot"
FRACTAL="julia"

# screen size
MAX_X = 1000
MAX_Y = 800

def julia_px(px, py, xc, yc, fx_min, fy_min):
    """julia set fractal"""

    c = complex(-0.1, 0.65)
    zmax = 10
    
    x0 = px / xc + fx_min
    y0 = py / yc + fy_min


    cnt = 0
    z = complex(x0, y0)
    while abs(z) <= zmax and cnt < MAX_CNT:
        z = z**2 + c
        cnt += 1
    
    return cnt


def mandelbrot_px(px, py, xc, yc, fx_min, fy_min):
    """
xc = constant for converting x
= 2.47 / max_x - 2 so range is -0.47 to 2
yc = constant for converting y
= 2.24 / max_y  (size of y - midpoint so y range is -1.12 to 1.12)
    """

    #x0 = px / xc - 2
    #y0 = py / yc - 1.12

    x0 = px / xc + fx_min
    y0 = py / yc + fy_min


    x = 0
    y = 0
    cnt = 0

    while x*x + y*y <= 4 and cnt < MAX_CNT:
        xtmp = x*x - y*y + x0
        y = 2*x*y + y0
        x = xtmp
        cnt += 1

    
    return cnt


def producer(thread, thread_cnt, xc, yc, fx_min, fy_min, q):

    print("<p{}> started, queue_size = {}".format(thread, q.qsize()), flush=True)
    
    """
    # striped
    for x in range(0, MAX_X):
        for y in range(0, MAX_Y):
            if x % thread_cnt == thread:
                cnt = calc_px(x, y, xc, yc)
                if cnt > 2:
                    q.put((x, y, cnt, thread))
    """

    # break into sections
    x0 = thread * MAX_X // thread_cnt
    x1 = (thread+1) * MAX_X // thread_cnt

    print("<p{}>  {} .. {}".format(thread, x0, x1))
    for x in range(x0, x1):
        for y in range(0, MAX_Y):
            if FRACTAL == "mandelbrot":
                cnt = mandelbrot_px(x, y, xc, yc, fx_min, fy_min)
            else:
                cnt = julia_px(x, y, xc, yc, fx_min, fy_min)
                
            if cnt > 2:
                q.put((x, y, cnt, thread))
    

    # thread done
    #q.put((-1, -1, -1, thread))

    print("<p{}> done, queue_size = {}".format(thread, q.qsize()), flush=True)


def consumer(q, bg, c):
    """ read from queue (q) and process data """
    
    print("<c{}> started, queue size: {}".format(c, q.qsize()))


    done = False

    while not done:
    
        # blocking
        item = q.get()

        t = item[3] # color by thread ... 
        cc = item[2]
        if cc == -1:
            continue
        
        # needed to exit properly ... close enough
        if q.qsize() < 5:
            done = True



        clr = int(cc / MAX_CNT * 255)
        
        px_color = (0,0,0)

        # color per producer
        if t % 3 == 0:
            px_color = (clr, 0, 0) # red
        elif t % 3 == 1:
            px_color = (0, clr, 0) # green
        else:
            px_color = (0, 0, clr) # blue

        # color per consumer
        """
        if c % 3 == 0:
            px_color = (clr, 0, clr)
        elif c % 3 == 1:
            px_color = (clr, clr, 0)
        elif c % 3 == 2:
            px_color = (0, clr, clr)
        """
        if clr > 1:
            bg.set_at((item[0], item[1]), px_color)
        #pygame.gfxdraw.pixel(bg, item[0], item[1], px_color)
        if q.qsize() % 100_000 == 0 or q.qsize() < 11:
            print("<c{}> queue size: {}".format(c, q.qsize()))
            screen.blit(bg, (0, 0))
            pygame.display.flip()

    
    print("<c{}> done".format(c), flush=True)



def init_screen():
    
    screen_size_px = (MAX_X, MAX_Y)

    pygame.init()

    screen = pygame.display.set_mode(screen_size_px, HWSURFACE|HWPALETTE, 8)
    pygame.display.set_caption("Mandelbrot")

    # misc useless information
    #print("SCREEN: hardware=%d, depth=%d" % (screen.get_flags()&HWSURFACE, screen.get_bitsize()))
    #print(pygame.display.Info())
    #print("display driver: {}".format(pygame.display.get_driver()))
    #pygame.mouse.set_visible(False)
    #pygame.event.set_grab(True) 
    
    return screen


def fractal(screen):
    """make a fractal"""

    clock_tick = 2
    clock = pygame.time.Clock()

    bg = pygame.Surface(screen.get_size())
    bg = bg.convert()

    background_color = (0,0,0)
    bg.fill(background_color)

    # mandelbrot fractal coordinates
    fx_min, fx_max = -2.00, 0.5
    fy_min, fy_max = -1.2, 1.2

    # julia
    if FRACTAL == "julia":
        fx_min, fx_max = -1.5, 1.5
        fy_min, fy_max = -1.5, 1.5
        

    xc = MAX_X / (fx_max - fx_min)
    yc = MAX_Y / (fy_max - fy_min)



    done = False
    loop_cnt = 0
    pal_cnt = 0

    mp_max = 8
    thread_max = 2

    redraw_flag = True # False # True # draw fractal
    mflag = False # use multiprocessing
    bg0 = None # background object
    q = Queue()

    # selection
    draw_sq_flag = False
    select_flag = False
    s0 = (0,0)
    s1 = (0,0)
    #sq_color = (255,0,255) # pink
    #sq_color2 = (0, 255, 255) # cyan
    sq_color = (255, 255, 0, 128) # yellow w/ transparency

    print("CPU cnt: {}".format(cpu_count()))

    # vectorize fractal function
    np_flag = False
    fv = None
    if FRACTAL == "mandelbrot":
        fv = np.vectorize(mandelbrot_px)
    elif FRACTAL == "julia":
        fv = np.vectorize(julia_px)

    

    while not done:

        loop_cnt += 1

        if draw_sq_flag:
            
            sx0 = min(s0[0], s1[0])
            sy0 = min(s0[1], s1[1])

            sq_width = abs(s0[0] - s1[0])
            sq_height = abs(s0[1] - s1[1])
            print("-- {} x {}".format(sq_width, sq_height))

            # set bg to copy
            bg.fill(background_color)
            if bg0:
                bg.blit(bg0, (0,0))
            
                
            pygame.draw.rect(bg, sq_color, [sx0, sy0, sq_width, sq_height], 2)
            
            # transparentcy not working, wanted a semi-transparent selection square
            #pygame.draw.rect(bg, sq_color, [sx0, sy0, sq_width, sq_height])
            
            screen.blit(bg, (0,0))
            pygame.display.flip()



        if redraw_flag:

            bg.fill(background_color)


            if mflag:
                # use multiprocessing & threads
                s = time.perf_counter()

                p_list = []
                for i in range(mp_max):
                    # producer
                    p = Process(target=producer, args=(i, mp_max, xc, yc, fx_min, fy_min, q))
                    p.start()
                    p_list.append(p)

                # must be before join of multiprocess threads

                t_list = []
                for i in range(thread_max):
                    t = Thread(target=consumer, args=(q, bg, i))
                    t_list.append(t)
                    t.start()

                for p in p_list:
                    p.join()
                
                print("producers done")

                for t in t_list:
                    t.join()
                
                print("consumers done")
                print("mp & threads done: {:.2f} sec, {:,} pixels".format(time.perf_counter() - s, MAX_X * MAX_Y))

            
            else:            
                # just normal processing

                if np_flag:
                    print("numpy start")
                    s = time.perf_counter()

                    x = np.linspace(1, MAX_X, MAX_X)
                    y = np.linspace(1, MAX_Y, MAX_Y)
                    a = fv(x[:, np.newaxis], y, xc, yc, fx_min, fy_min)
                    surf = pygame.surfarray.make_surface(a)
                    bg.blit(surf, (0,0))

                    print("numpy done: {:.2f} sec, {:,} pixels".format(time.perf_counter() - s, MAX_X * MAX_Y))


                else:
                    print("loop start")
                    s = time.perf_counter()
                    a = np.zeros((MAX_X, MAX_Y))            
                    for x in range(0, MAX_X):
                        for y in range(0, MAX_Y):
                            c = 32
                            if FRACTAL == "mandelbrot":
                                c = mandelbrot_px(x, y, xc, yc, fx_min, fy_min)
                            elif FRACTAL == "julia":
                                c = julia_px(x, y, xc, yc, fx_min, fy_min)

                            shade = c / MAX_CNT
                            #shade = 1 - math.sqrt(c / MAX_CNT)
                            #shade = math.sqrt(c / MAX_CNT)
                            cc = int(shade * 255)
                            a[x][y] = cc
                            """
                            if cc > 1:
                                #px_color = (cc, 255-cc, cc) # green bg, pink
                                px_color = (cc, cc, cc) # black & white
                                #px_color = (255-cc, 255-cc, 255-cc) # white & black

                                # set_at = 15.63 sec
                                #bg.set_at((x, y), px_color)
                                pygame.gfxdraw.pixel(bg, x, y, px_color)                    
                            """
                    
                        # refresh every stripe
                        
                        if x % 100 == 0:
                            #screen.blit(bg, (0, 0))
                            #pygame.display.flip()
                            surf = pygame.surfarray.make_surface(a)        
                            bg.blit(surf, (0,0))
                            pygame.display.flip()

                    surf = pygame.surfarray.make_surface(a)
                    bg.blit(surf, (0,0))
            

                    #screen.blit(bg, (0, 0))
                    #pygame.display.flip()                

                    print("single thread loop done: {:.2f} sec, {:,} pixels".format(time.perf_counter() - s, MAX_X * MAX_Y))


            screen.blit(bg, (0, 0))
            pygame.display.flip()
            bg0 = bg.copy()
            
            redraw_flag = False



        clock.tick(clock_tick) 

        for event in pygame.event.get():
            mm = pygame.mouse.get_pos()

            if select_flag:
                s1 = mm
                #draw_sq_flag = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    s0 = mm
                    s1 = mm
                    select_flag = True
                    draw_sq_flag = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    s1 = mm
                    select_flag = False
                    #print("selection: {}, {}".format(s0, s1))
                    
                    draw_sq_flag = False

                    # get new coordinate for fractal (f*)
                    sx0 = min(s0[0], s1[0])
                    sy0 = min(s0[1], s1[1])

                    sx1 = max(s0[0], s1[0])
                    sy1 = max(s0[1], s1[1])

                    fx_min_new = (fx_max - fx_min) * sx0 / MAX_X + fx_min
                    fy_min_new = (fy_max - fy_min) * sy0 / MAX_Y + fy_min

                    fx_max_new = (fx_max - fx_min) * sx1 / MAX_X + fx_min
                    fy_max_new = (fy_max - fy_min) * sy1 / MAX_Y + fy_min

                    if abs(fx_max_new - fx_min_new) > 0:
                        fx_min = fx_min_new
                        fx_max = fx_max_new
                    if abs(fy_max_new - fy_min_new) > 0:
                        fy_min = fy_min_new
                        fy_max = fy_max_new

                    print("fractal area: {:.6f},{:.6f} to {:.6f},{:.6f}".format(fx_min, fy_min, fx_max, fy_max))
                    
                    xc = MAX_X / (fx_max - fx_min)
                    yc = MAX_Y / (fy_max - fy_min)




            if event.type == QUIT:
                done = True
            elif event.type == KEYDOWN:

                if event.key == K_s:
                    mflag = False
                    redraw_flag = True
                if event.key == K_n:
                    # numpy
                    mflag = False
                    redraw_flag = True                    
                    np_flag = not np_flag
                if event.key == K_p:
                    mflag = True
                    redraw_flag = True

                if event.key == K_r:
                    # reset to original size

                    fx_min, fx_max = -2.00, 0.5
                    fy_min, fy_max = -1.2, 1.2 
                        
                    if FRACTAL == "julia":
                        fx_min, fx_max = -1.5, 1.5
                        fy_min, fy_max = -1.5, 1.5

                    print("reset coordinates to {},{} - {},{}".format(fx_min, fy_min, fx_max, fy_max))
                    xc = MAX_X / (fx_max - fx_min)
                    yc = MAX_Y / (fy_max - fy_min)


                if event.key == K_ESCAPE:
                    done = True


def peppermint():
    """compare loop versus numpy"""
     # julia
    fx_min, fx_max = -1.5, 1.5
    fy_min, fy_max = -1.5, 1.5
        

    xc = MAX_X / (fx_max - fx_min)
    yc = MAX_Y / (fy_max - fy_min)

    """
    s = time.perf_counter()

    

    # 15.62 sec
    a = np.zeros((MAX_X, MAX_Y))
    for x in range(0, MAX_X):
        for y in range(0, MAX_Y):
            c = 32
            if FRACTAL == "mandelbrot":
                c = mandelbrot_px(x, y, xc, yc, fx_min, fy_min)
            elif FRACTAL == "julia":
                c = julia_px(x, y, xc, yc, fx_min, fy_min)

            # set pixel x,y,c
            a[x][y] = c

    print(a)
    print(a[300][300])
    print("done: {:.2f} sec, {:,} pixels".format(time.perf_counter() - s, MAX_X * MAX_Y))
    """
    # a[300][300] = 5
    s = time.perf_counter()
    print("starting np")
    #a = np.zeros((MAX_X, MAX_Y))
    #x = np.linspace(fx_min, fx_max, MAX_X)
    #y = np.linspace(fy_min, fy_max, MAX_Y)
    x = np.linspace(1, MAX_X, MAX_X)
    y = np.linspace(1, MAX_Y, MAX_Y)

    #def julia_px(px, py, xc, yc, fx_min, fy_min):
    if FRACTAL == "mandelbrot":
        fv = np.vectorize(mandelbrot_px)
    elif FRACTAL == "julia":
        fv = np.vectorize(julia_px)

    r = fv(x[:, np.newaxis], y, xc, yc, fx_min, fy_min)
    print(r)
    print(r[300][300])
    print("done: {:.2f} sec, {:,} pixels".format(time.perf_counter() - s, MAX_X * MAX_Y))


    sys.exit(0)

if __name__ == '__main__':


    #peppermint()

    screen = init_screen()

    fractal(screen)

    pygame.quit()
    
    sys.exit(0)