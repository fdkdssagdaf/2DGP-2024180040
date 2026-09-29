import json
import os

from pico2d import *


LEC08_DIR = os.path.dirname(os.path.abspath(__file__))
CANVAS_WIDTH, CANVAS_HEIGHT = 800, 600
FPS = 24
REPEAT_COUNT = 5
PAUSE_SECONDS = 1
DISPLAY_HEIGHT = 350
ANIMATIONS = ('idle', 'walk', 'jump', 'attack')


open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
character = load_image(os.path.join(LEC08_DIR, 'character_sheet.png'))

with open(os.path.join(LEC08_DIR, 'character_sheet.json'), encoding='utf-8') as metadata_file:
    sprite_frames = json.load(metadata_file)['frames']

running = True
while running:
    for animation in ANIMATIONS:
        for repeat in range(REPEAT_COUNT):
            for frame in sprite_frames[animation]:
                for event in get_events():
                    if event.type == SDL_QUIT or (event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE):
                        running = False
                        break
                if not running:
                    break

                clear_canvas()
                draw_width = DISPLAY_HEIGHT * frame['width'] / frame['height']
                character.clip_draw(
                    frame['left'], frame['bottom'], frame['width'], frame['height'],
                    CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2, draw_width, DISPLAY_HEIGHT,
                )
                update_canvas()
                delay(1 / FPS)

            if not running:
                break
        if not running:
            break
        delay(PAUSE_SECONDS)

close_canvas()