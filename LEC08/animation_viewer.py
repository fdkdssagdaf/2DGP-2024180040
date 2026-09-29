import json
import os

from pico2d import *


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANVAS_WIDTH, CANVAS_HEIGHT = 800, 600
FPS = 24
REPEAT_COUNT = 5
PAUSE_SECONDS = 1
DISPLAY_HEIGHT = 350

SPRITE_SHEET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'character_sheet.png')
SPRITE_METADATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'character_sheet.json')
ANIMATIONS = ('idle', 'walk', 'jump', 'attack')


def initialize():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)

    grass_path = os.path.join(BASE_DIR, 'LEC05', 'grass.png')
    grass = load_image(grass_path) if os.path.isfile(grass_path) else None

    if not os.path.isfile(SPRITE_SHEET_PATH) or not os.path.isfile(SPRITE_METADATA_PATH):
        from make_sprite_sheet import build_sheet
        build_sheet()

    with open(SPRITE_METADATA_PATH, encoding='utf-8') as metadata_file:
        sprite_frames = json.load(metadata_file)['frames']
    character = load_image(SPRITE_SHEET_PATH)
    return character, grass, sprite_frames


def draw_character(character, animation, frame, sprite_frames):
    frame_data = sprite_frames[animation][frame]
    draw_width = DISPLAY_HEIGHT * frame_data['width'] / frame_data['height']
    character.clip_draw(
        frame_data['left'], frame_data['bottom'],
        frame_data['width'], frame_data['height'],
        CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2,
        draw_width, DISPLAY_HEIGHT,
    )


def draw_frame(character, grass, animation, frame, sprite_frames):
    clear_canvas()
    if grass is not None:
        grass.draw(CANVAS_WIDTH / 2, 30)

    draw_character(character, animation, frame, sprite_frames)
    update_canvas()


def is_running():
    for event in get_events():
        if event.type == SDL_QUIT:
            return False
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return False
    return True


def run():
    character, grass, sprite_frames = initialize()

    try:
        while True:
            for animation in ANIMATIONS:
                if not is_running():
                    return

                frame_count = len(sprite_frames[animation])
                for _ in range(REPEAT_COUNT):
                    for frame in range(frame_count):
                        if not is_running():
                            return
                        draw_frame(
                            character, grass, animation, frame, sprite_frames,
                        )
                        delay(1 / FPS)

                delay(PAUSE_SECONDS)
    finally:
        close_canvas()


if __name__ == '__main__':
    run()