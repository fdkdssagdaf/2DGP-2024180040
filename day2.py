from pico2d import *

open_canvas(800, 600)
character = load_image('character.png')











def move_circle():
    print('circle')

def move_rectangle():
    print('rectangle')

def move_triangle():
    print('triangle')

while True:
    clear_canvas()
    move_circle()
    move_rectangle()
    move_triangle()
    character.draw(400, 300)
    update_canvas()
    delay(0.03)

close_canvas()
