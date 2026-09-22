import math
import os

from pico2d import *


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
open_canvas(800, 600)
grass = load_image(os.path.join(BASE_DIR, 'grass.png'))
character = load_image(os.path.join(BASE_DIR, 'character.png'))

for frame in range(240):
    angle = (frame / 240) * math.tau
    x = 400 + math.cos(angle) * 220
    y = 280 + math.sin(angle) * 170

    clear_canvas()
    grass.draw(400, 30)
    character.draw(x, y)
    update_canvas()
    delay(0.03)

close_canvas()