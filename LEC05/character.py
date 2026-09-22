import math
import os

from pico2d import *


open_canvas(800, 600)

base_dir = os.path.dirname(os.path.abspath(__file__))
grass = load_image(os.path.join(base_dir, 'grass.png'))
character = load_image(os.path.join(base_dir, 'character.png'))

def draw_scene(x, y):
	clear_canvas()
	grass.draw(400, 30)
	character.draw(x, y)
	update_canvas()


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
	draw_scene(x, y)
	delay(0.03)

for frame in range(240):
	angle = (frame / 240) * math.tau
	x = 400 + math.cos(angle) * 220
	y = 280 + math.sin(angle) * 170
	draw_scene(x, y)
	delay(0.03)

close_canvas()