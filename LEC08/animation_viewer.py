import math
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
            frames = sprite_frames[animation]
            for frame_index, frame in enumerate(frames):
                for event in get_events():
                    if event.type == SDL_QUIT or (event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE):
                        running = False
                        break
                if not running:
                    break

                clear_canvas()
                progress = frame_index / len(frames)
                x, y = CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2
                if animation == 'walk':
                    x = 270 + progress * 260
                    y += math.sin(progress * math.tau) * 8
                elif animation == 'jump':
                    y = 210 + math.sin(progress * math.pi) * 170
                elif animation == 'attack':
                    x = 320 + math.sin(progress * math.pi) * 160
                else:
                    x += math.sin(progress * math.tau) * 8
                    y += math.cos(progress * math.tau) * 6

                draw_width = DISPLAY_HEIGHT * frame['width'] / frame['height']
                character.clip_draw(
                    frame['left'], frame['bottom'], frame['width'], frame['height'],
                    x, y, draw_width, DISPLAY_HEIGHT,
                )
                if animation == 'attack' and 0.15 <= progress <= 0.85:
                    swing = (progress - 0.15) / 0.7
                    slash_y = y + 20 + math.sin(swing * math.pi) * 45
                    draw_line(x + 30, slash_y, x + 115, slash_y + 95, 255, 245, 160)
                    draw_line(x + 45, slash_y - 12, x + 125, slash_y + 75, 130, 235, 255)
                update_canvas()
                delay(1 / FPS)

            if not running:
                break
        if not running:
            break
        delay(PAUSE_SECONDS)

close_canvas()