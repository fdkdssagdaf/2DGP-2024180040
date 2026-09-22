import math
import os

import cv2

from make_motion_video import FPS, HEIGHT, WIDTH, encode_for_discord, load_png, make_frame


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    character = load_png(os.path.join(BASE_DIR, 'character.png'))
    grass = load_png(os.path.join(BASE_DIR, 'grass.png'))
    output_path = os.path.join(BASE_DIR, 'circle_motion.mp4')
    source_path = os.path.join(BASE_DIR, 'circle_motion_raw.mp4')
    writer = cv2.VideoWriter(source_path, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT))

    for frame_number in range(240):
        angle = (frame_number / 240) * math.tau
        x = 400 + math.cos(angle) * 220
        y = 280 + math.sin(angle) * 170
        writer.write(make_frame(character, grass, x, y, 'CIRCULAR MOTION'))

    writer.release()
    encode_for_discord(source_path, output_path)
    os.remove(source_path)
    print(output_path)


if __name__ == '__main__':
    main()