#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""
Barnsley Fern
- very slow to iterate through it??

"""
import sys
import os
import pygame
from pygame.locals import *
import functools
import random
import yaml
import math

def init_screen():
    """initalize screen"""
    pygame.init()

    screen_x = 1000
    screen_y = 700
        
    screen = pygame.display.set_mode((screen_x, screen_y), HWSURFACE|HWPALETTE, 8)
    
    pygame.display.set_caption("Fern Fractal")

    pygame.mouse.set_visible(False)
    
    pygame.display.set_allow_screensaver(False)

    return screen, screen_x, screen_y

@functools.cache
def barnsley_fern(x,y):
    #xn = yn = 0.0
    r = random.random()

    # Barnsley Fern
    if r < 0.01:
        xn = 0.0
        yn = 0.16 * y
    elif r < 0.86:
        xn = 0.85 * x + 0.04 * y
        yn = -0.04 * x + 0.85 * y + 1.6
    elif r < 0.93:
        xn = 0.2 * x - 0.26 * y
        yn = 0.23 * x + 0.22 * y + 1.6
    else:
        xn = -0.15 * x + 0.28 * y
        yn = 0.26 * x + 0.24 * y + 0.44
        
    return xn, yn



def fern(screen, screen_x, screen_y):
    
    background_color = (0,0,0)
    done = False

    bg = pygame.Surface(screen.get_size())
    bg = bg.convert()

    clock_tick = 90 # higher = faster
    clock = pygame.time.Clock()

    redraw_flag = True
    x = 0.0
    y = 0.0

    bg.fill(background_color)
    cnt = 0

    while not done:

        #r = random.random()
        #xn = yn = 0.0
        x, y = barnsley_fern(x,y)
        
        #print(f"{x:.2f}, {y:.2f}")
        xt = int(450 + x*50)
        yt = int(y*50 + 100)
        bg.set_at((xt, yt), (0,255,0))
        bg.set_at((xt-250,yt), (255,0,0))
        bg.set_at((xt+250,yt), (0,0,255))
        cnt += 1

        if cnt % 50 == 0:
            print(f"- iteration {cnt}")
            screen.blit(bg, (0, 0))
            pygame.display.flip()

        clock.tick(clock_tick) 

        
        

        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
            elif event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    done = True            

                if event.key == K_RETURN:
                    done = True

if __name__ == '__main__':

    print("[ Fern Fractal ]".center(60, "-"))
    # full screen option
    screen, screen_x, screen_y = init_screen()

    fern(screen, screen_x, screen_y)

    pygame.quit()
    
    sys.exit(0)