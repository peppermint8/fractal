#!/usr/bin/env python
#! -*- coding: utf-8 -*-
"""
https://en.wikipedia.org/wiki/Gosper_curve
https://realpython.com/beginners-guide-python-turtle/
"""

import turtle

def gosper_curve(order: int, size: int, is_A: bool = True) -> None:
    """Draw the Gosper curve."""
    if order == 0:
        turtle.forward(size)
        return
    for op in "A-B--B+A++AA+B-" if is_A else "+A-BB--B-A++A+B":
        gosper_op_map[op](order - 1, size)

gosper_op_map = {
    "A": lambda o, size: gosper_curve(o, size, True),
    "B": lambda o, size: gosper_curve(o, size, False),
    "-": lambda o, size: turtle.right(60),
    "+": lambda o, size: turtle.left(60),
}

turtle.bgcolor("black")
turtle.pencolor("purple")
turtle.speed(10)

size = 10
order = 4
gosper_curve(order, size)

done = False
while not done:
    pass
