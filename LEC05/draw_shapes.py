import math
import os

from pico2d import *


grass = None
character = None


def initialize():
    global grass, character
    base_dir = os.path.dirname(os.path.abspath(__file__))
    open_canvas(800, 600)
    grass = load_image(os.path.join(base_dir, 'grass.png'))
    character = load_image(os.path.join(base_dir, 'character.png'))


def draw_circle(frame):
    x, y = get_circle_position(frame)
    character.draw(x, y)


def get_circle_position(frame):
    angle = frame * math.tau / 240
    x = 200 + math.cos(angle) * 120
    y = 330 + math.sin(angle) * 120
    return x, y


def draw_rectangle(frame):
    width, height = 240, 150
    perimeter = 2 * (width + height)
    distance = (frame * 4) % perimeter
    if distance < width:
        draw_top(distance, width)
    elif distance < width + height:
        draw_right(distance - width, width, height)
    elif distance < width * 2 + height:
        draw_bottom(distance - width - height, width, height)
    else:
        draw_left(distance - width * 2 - height, height)


def draw_top(distance, width):
    x = 400 - width / 2 + distance
    character.draw(x, 180)


def draw_right(distance, width, height):
    character.draw(400 + width / 2, 180 + distance)


def draw_bottom(distance, width, height):
    x = 400 + width / 2 - distance
    character.draw(x, 180 + height)


def draw_left(distance, height):
    y = 180 + height - distance
    character.draw(400 - 120, y)


def draw_triangle(frame):
    points = [(650, 180), (750, 180), (700, 330)]
    side = (frame // 80) % 3
    ratio = (frame % 80) / 80
    x, y = get_point_between(points[side], points[(side + 1) % 3], ratio)
    character.draw(x, y)


def get_point_between(start, end, ratio):
    x = start[0] + (end[0] - start[0]) * ratio
    y = start[1] + (end[1] - start[1]) * ratio
    return x, y


def draw_frame(frame):
    clear_canvas()
    grass.draw(400, 30)
    draw_circle(frame)
    draw_rectangle(frame)
    draw_triangle(frame)
    update_canvas()


def run():
    for frame in range(240):
        draw_frame(frame)
        delay(0.03)


def main():
    initialize()
    run()
    close_canvas()


if __name__ == '__main__':
    main()