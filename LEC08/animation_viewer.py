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
                    x = 120 + progress * 560
                    y += math.sin(progress * math.tau) * 22
                elif animation == 'jump':
                    x += math.sin(progress * math.tau) * 24
                    y = 180 + math.sin(progress * math.pi) * 250
                elif animation == 'attack':
                    if progress < 0.25:
                        x = 400 - math.sin(progress / 0.25 * math.pi / 2) * 100
                    elif progress < 0.65:
                        x = 300 + (progress - 0.25) / 0.4 * 250
                    else:
                        x = 550 - (progress - 0.65) / 0.35 * 150
                else:
                    x += math.sin(progress * math.tau) * 4
                    y += math.cos(progress * math.tau) * 5

                draw_line(40, 92, 760, 92, 66, 82, 98)
                if animation == 'walk':
                    draw_circle(x - 28, 105, 6, 110, 205, 185, filled=True)
                    draw_circle(x + 24, 105, 6, 110, 205, 185, filled=True)
                elif animation == 'jump':
                    shadow_size = max(10, 38 - int((y - 180) / 9))
                    draw_circle(400, 105, shadow_size, 95, 110, 125, filled=True)

                draw_width = DISPLAY_HEIGHT * frame['width'] / frame['height']
                character.clip_draw(
                    frame['left'], frame['bottom'], frame['width'], frame['height'],
                    x, y, draw_width, DISPLAY_HEIGHT,
                )
                if animation == 'jump' and 0.15 <= progress <= 0.85:
                    for streak in range(3):
                        streak_x = x - 85 + streak * 20
                        draw_line(streak_x, y - 125, streak_x - 14, y - 80, 150, 225, 255)
                elif animation == 'attack' and 0.1 <= progress <= 0.9:
                    swing = (progress - 0.1) / 0.8
                    slash_y = y + 35 + math.sin(swing * math.pi) * 35
                    impact_x, impact_y = x + 175, slash_y + 130
                    draw_line(x + 20, slash_y, impact_x, impact_y, 255, 236, 110)
                    draw_line(x + 28, slash_y - 8, impact_x + 8, impact_y - 8, 255, 255, 240)
                    draw_line(x + 12, slash_y - 16, impact_x - 8, impact_y - 16, 90, 220, 255)
                    draw_line(impact_x - 24, impact_y, impact_x + 24, impact_y, 255, 185, 80)
                    draw_line(impact_x, impact_y - 24, impact_x, impact_y + 24, 255, 185, 80)
                update_canvas()
                delay(1 / FPS)

            if not running:
                break
        if not running:
            break
        delay(PAUSE_SECONDS)

close_canvas()