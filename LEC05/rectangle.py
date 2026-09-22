import os

from pico2d import *


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
open_canvas(800, 600)
grass = load_image(os.path.join(BASE_DIR, 'grass.png'))
character = load_image(os.path.join(BASE_DIR, 'character.png'))

left, right = 150, 650
bottom, top = 100, 450
width, height = right - left, top - bottom

for frame in range(240):
    distance = (frame / 240) * (width * 2 + height * 2)
    if distance < width:
        x, y = left + distance, bottom
    elif distance < width + height:
        x, y = right, bottom + distance - width
    elif distance < width * 2 + height:
        x, y = right - (distance - width - height), top
    else:
        x, y = left, top - (distance - width * 2 - height)

    clear_canvas()
    grass.draw(400, 30)
    character.draw(x, y)
    update_canvas()
    delay(0.03)

close_canvas()