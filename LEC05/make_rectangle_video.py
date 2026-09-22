import os

import cv2

from make_motion_video import FPS, HEIGHT, WIDTH, encode_for_discord, load_png, make_frame, rectangle_position


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    character = load_png(os.path.join(BASE_DIR, 'character.png'))
    grass = load_png(os.path.join(BASE_DIR, 'grass.png'))
    output_path = os.path.join(BASE_DIR, 'rectangle_motion.mp4')
    source_path = os.path.join(BASE_DIR, 'rectangle_motion_raw.mp4')
    writer = cv2.VideoWriter(source_path, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT))

    for frame_number in range(240):
        x, y = rectangle_position(frame_number / 240)
        writer.write(make_frame(character, grass, x, y, 'RECTANGULAR MOTION'))

    writer.release()
    encode_for_discord(source_path, output_path)
    os.remove(source_path)
    print(output_path)


if __name__ == '__main__':
    main()