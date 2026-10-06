from pico2d import *


TUK_WIDTH, TUK_HEIGHT = 1280, 1024
open_canvas(TUK_WIDTH, TUK_HEIGHT)
tuk_ground = load_image('TUK_GROUND.png')
character = load_image('animation_sheet.png')


def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                running = False
            else:
                keys_down.add(event.key)
        elif event.type == SDL_KEYUP:
            keys_down.discard(event.key)

running = True
keys_down = set()
x, y = TUK_WIDTH // 2, TUK_HEIGHT // 2
frame = 0
speed = 5

while running:
    handle_events()
    if not running:
        break

    move_x = int(SDLK_RIGHT in keys_down) - int(SDLK_LEFT in keys_down)
    move_y = int(SDLK_UP in keys_down) - int(SDLK_DOWN in keys_down)
    if move_x and move_y:
        move_x *= 0.70710678
        move_y *= 0.70710678

    next_x = max(50, min(TUK_WIDTH - 50, x + move_x * speed))
    next_y = max(50, min(TUK_HEIGHT - 50, y + move_y * speed))
    moving = next_x != x or next_y != y
    x, y = next_x, next_y

    clear_canvas()
    tuk_ground.draw(TUK_WIDTH // 2, TUK_HEIGHT // 2)
    character.clip_draw(frame * 100, 100, 100, 100, x, y)
    update_canvas()

    frame = (frame + 1) % 8
    delay(0.05)


close_canvas()
