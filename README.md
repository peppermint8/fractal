# Fractals and PyGame

Created code to generate the Mandelbrot set or Julia set using pygame.
Also added threading and multiprocessing to look for speed ups.
 - I think it speeds up during calculation but the pygame interface cannot be parallelized so it ends up slower

 ## Code

 `./fractal.py`
 Draw manelbrot or julia set.  Need to set variable in the code for this (FRACTAL)
  - keys to use:
    - esc = quit
    - r = reset coordinates to original
    - s = generate fractal single thread mode (simple)
    - p = generate fractal using multiprocessing and threading.  Color bands are for each mutliprocess thread (producer) used

Use the mouse to click and drag over a section, then regenerate the zoomed section with "s" or "p"

`./gosper.py` 
Found code to use "turtle" to draw.  Doing a gosper curve.

`./m.py` = multiprocessing example
`./t.py` = threading example


## To Do

Would like to learn how to color cycle the palette or do better with coloring the fractal

