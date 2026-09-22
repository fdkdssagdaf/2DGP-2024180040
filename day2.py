from pico2d import *

open_canvas(800, 600)
character = load_image('character.png')











def move_circle():
    print('circle')

def move_rectangle():
    print('rectangle')

def move_triangle():
    print('triangle')

running = True
while running:
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False

    clear_canvas()
    move_circle()
    move_rectangle()
    move_triangle()
    character.draw(400, 300)
    update_canvas()
    delay(0.03)

close_canvas()
