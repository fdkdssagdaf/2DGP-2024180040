import math
import os
import subprocess

import cv2
import imageio_ffmpeg
import numpy as np


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WIDTH, HEIGHT = 800, 600
FPS = 30


def alpha_over(background, foreground, x, y):
    image_height, image_width = foreground.shape[:2]
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(WIDTH, x + image_width), min(HEIGHT, y + image_height)
    if x1 >= x2 or y1 >= y2:
        return

    source = foreground[y1 - y:y2 - y, x1 - x:x2 - x]
    target = background[y1:y2, x1:x2]
    if source.shape[2] == 4:
        alpha = source[:, :, 3:4].astype(np.float32) / 255
        target[:] = source[:, :, :3] * alpha + target * (1 - alpha)
    else:
        target[:] = source


def load_png(path):
    data = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_UNCHANGED)


def rectangle_position(progress):
    left, right, bottom, top = 150, 650, 100, 450
    width, height = right - left, top - bottom
    distance = progress * (width * 2 + height * 2)
    if distance < width:
        return left + distance, bottom
    if distance < width + height:
        return right, bottom + distance - width
    if distance < width * 2 + height:
        return right - (distance - width - height), top
    return left, top - (distance - width * 2 - height)


def make_frame(character, grass, x, y, title):
    frame = np.full((HEIGHT, WIDTH, 3), (235, 245, 250), dtype=np.uint8)
    alpha_over(frame, grass, 0, HEIGHT - grass.shape[0])
    character_x = int(x - character.shape[1] / 2)
    character_y = int(HEIGHT - y - character.shape[0] / 2)
    alpha_over(frame, character, character_x, character_y)
    return frame


def encode_for_discord(source_path, output_path):
    subprocess.run([
        imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-i', source_path,
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart', output_path,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    character = load_png(os.path.join(BASE_DIR, 'character.png'))
    grass = load_png(os.path.join(BASE_DIR, 'grass.png'))
    output_path = os.path.join(BASE_DIR, 'character_motion.mp4')
    source_path = os.path.join(BASE_DIR, 'character_motion_raw.mp4')
    writer = cv2.VideoWriter(source_path, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT))

    for frame_number in range(240):
        x, y = rectangle_position(frame_number / 240)
        writer.write(make_frame(character, grass, x, y, 'RECTANGULAR MOTION'))
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