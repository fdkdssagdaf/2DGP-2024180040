import json
import math
import os
import struct
import zlib


OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PNG = os.path.join(OUTPUT_DIR, 'character_sheet.png')
OUTPUT_JSON = os.path.join(OUTPUT_DIR, 'character_sheet.json')
GAP = 4

INK = (28, 39, 55, 255)
SKIN = (246, 183, 126, 255)
HAIR = (45, 48, 72, 255)
COAT = (40, 153, 151, 255)
COAT_LIGHT = (96, 206, 185, 255)
PANTS = (58, 81, 126, 255)
BOOT = (244, 113, 91, 255)
SWORD = (229, 250, 246, 255)
EYE = (29, 37, 49, 255)


class PixelCanvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = bytearray(width * height * 4)

    def pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            offset = (y * self.width + x) * 4
            self.pixels[offset:offset + 4] = bytes(color)

    def rectangle(self, left, top, right, bottom, color):
        for y in range(max(0, top), min(self.height, bottom)):
            for x in range(max(0, left), min(self.width, right)):
                self.pixel(x, y, color)

    def ellipse(self, center_x, center_y, radius_x, radius_y, color):
        for y in range(center_y - radius_y, center_y + radius_y + 1):
            for x in range(center_x - radius_x, center_x + radius_x + 1):
                dx = (x - center_x) / max(1, radius_x)
                dy = (y - center_y) / max(1, radius_y)
                if dx * dx + dy * dy <= 1:
                    self.pixel(x, y, color)

    def line(self, start, end, color, thickness=1):
        x1, y1 = start
        x2, y2 = end
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        step_x = 1 if x1 < x2 else -1
        step_y = 1 if y1 < y2 else -1
        error = dx - dy
        while True:
            radius = thickness // 2
            self.rectangle(x1 - radius, y1 - radius, x1 + radius + 1, y1 + radius + 1, color)
            if x1 == x2 and y1 == y2:
                break
            doubled_error = 2 * error
            if doubled_error > -dy:
                error -= dy
                x1 += step_x
            if doubled_error < dx:
                error += dx
                y1 += step_y

    def polygon(self, points, color):
        top = max(0, min(point[1] for point in points))
        bottom = min(self.height - 1, max(point[1] for point in points))
        for y in range(top, bottom + 1):
            intersections = []
            for index, (x1, y1) in enumerate(points):
                x2, y2 = points[(index + 1) % len(points)]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    intersections.append(round(x1 + (y - y1) * (x2 - x1) / (y2 - y1)))
            intersections.sort()
            for index in range(0, len(intersections) - 1, 2):
                self.rectangle(intersections[index], y, intersections[index + 1] + 1, y + 1, color)

    def save_png(self, path):
        stride = self.width * 4
        raw = b''.join(b'\x00' + self.pixels[y * stride:(y + 1) * stride] for y in range(self.height))

        def chunk(name, data):
            payload = name + data
            return struct.pack('>I', len(data)) + payload + struct.pack('>I', zlib.crc32(payload) & 0xffffffff)

        png = (
            b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', self.width, self.height, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9))
            + chunk(b'IEND', b'')
        )
        with open(path, 'wb') as image_file:
            image_file.write(png)


def draw_limb(canvas, start, end, outline, color, thickness):
    canvas.line(start, end, outline, thickness + 4)
    canvas.line(start, end, color, thickness)
    radius = thickness // 2
    canvas.ellipse(start[0], start[1], radius + 2, radius + 2, color)
    canvas.ellipse(end[0], end[1], radius + 2, radius + 2, color)


def draw_character(canvas, action, frame_index, frame_count):
    width, height = canvas.width, canvas.height
    scale = min(width / 76, height / 100)
    cx = width // 2
    ground = height - max(6, round(5 * scale))
    phase = frame_index / frame_count
    swing = round(math.sin(phase * math.tau) * 8 * scale) if action == 'walk' else 0
    bob = round(math.sin(phase * math.tau) * 2 * scale) if action == 'idle' else 0
    lunge = round(math.sin(phase * math.pi) * 7 * scale) if action == 'attack' else 0
    jump = round(math.sin(phase * math.pi) * 7 * scale) if action == 'jump' else 0
    cx += lunge
    head_radius = max(8, round(12 * scale))
    thickness = max(5, round(8 * scale))
    head_y = round(height * 0.25) + bob - jump
    shoulder_y = round(height * 0.42) + bob - jump
    hip_y = round(height * 0.66) + bob - jump
    foot_y = ground - jump

    if action == 'walk':
        left_foot = (cx - round(10 * scale) - swing, foot_y)
        right_foot = (cx + round(10 * scale) + swing, foot_y)
        left_knee = (cx - round(8 * scale) - swing // 2, round(height * 0.81) - jump)
        right_knee = (cx + round(8 * scale) + swing // 2, round(height * 0.81) - jump)
    elif action == 'jump':
        left_foot = (cx - round(15 * scale), foot_y - round(9 * scale))
        right_foot = (cx + round(15 * scale), foot_y - round(9 * scale))
        left_knee = (cx - round(12 * scale), round(height * 0.79) - jump)
        right_knee = (cx + round(12 * scale), round(height * 0.79) - jump)
    elif action == 'attack':
        left_foot = (cx - round(15 * scale), foot_y)
        right_foot = (cx + round(19 * scale), foot_y)
        left_knee = (cx - round(12 * scale), round(height * 0.81) - jump)
        right_knee = (cx + round(12 * scale), round(height * 0.79) - jump)
    else:
        left_foot = (cx - round(9 * scale), foot_y)
        right_foot = (cx + round(9 * scale), foot_y)
        left_knee = (cx - round(8 * scale), round(height * 0.81) - jump)
        right_knee = (cx + round(8 * scale), round(height * 0.81) - jump)

    hip = (cx, hip_y)
    draw_limb(canvas, hip, left_knee, INK, PANTS, thickness)
    draw_limb(canvas, left_knee, left_foot, INK, PANTS, thickness)
    draw_limb(canvas, hip, right_knee, INK, PANTS, thickness)
    draw_limb(canvas, right_knee, right_foot, INK, PANTS, thickness)
    for foot in (left_foot, right_foot):
        canvas.ellipse(foot[0], foot[1], round(8 * scale), round(4 * scale), BOOT)

    left_shoulder = (cx - round(12 * scale), shoulder_y)
    right_shoulder = (cx + round(12 * scale), shoulder_y)
    if action == 'jump':
        left_hand = (cx - round(26 * scale), shoulder_y - round(18 * scale))
        right_hand = (cx + round(26 * scale), shoulder_y - round(18 * scale))
    elif action == 'attack':
        left_hand = (cx - round(23 * scale), shoulder_y + round(17 * scale))
        right_hand = (cx + round(31 * scale), shoulder_y - round(3 * scale))
    else:
        arm_swing = swing if action == 'walk' else 0
        left_hand = (cx - round(22 * scale) - arm_swing, shoulder_y + round(22 * scale))
        right_hand = (cx + round(22 * scale) + arm_swing, shoulder_y + round(22 * scale))
    draw_limb(canvas, left_shoulder, left_hand, INK, SKIN, thickness)
    draw_limb(canvas, right_shoulder, right_hand, INK, SKIN, thickness)

    torso = [
        (cx - round(13 * scale), shoulder_y - round(3 * scale)),
        (cx + round(13 * scale), shoulder_y - round(3 * scale)),
        (cx + round(11 * scale), hip_y + round(4 * scale)),
        (cx - round(11 * scale), hip_y + round(4 * scale)),
    ]
    canvas.polygon([(x + 2, y + 3) for x, y in torso], INK)
    canvas.polygon(torso, COAT)
    canvas.line((cx, shoulder_y), (cx, hip_y), COAT_LIGHT, max(2, round(3 * scale)))

    canvas.ellipse(cx, head_y, head_radius + 2, head_radius + 2, INK)
    canvas.ellipse(cx, head_y, head_radius, head_radius, SKIN)
    canvas.ellipse(cx, head_y - round(5 * scale), head_radius + 1, round(7 * scale), HAIR)
    canvas.rectangle(cx - head_radius, head_y - round(5 * scale), cx + head_radius + 1, head_y, HAIR)
    face_direction = 1 if action == 'attack' else 0
    eye_y = head_y + round(1 * scale)
    canvas.pixel(cx + face_direction * round(4 * scale), eye_y, EYE)
    canvas.pixel(cx + face_direction * round(4 * scale) + 1, eye_y, EYE)

    if action == 'attack':
        blade_start = (right_hand[0] - round(2 * scale), right_hand[1])
        blade_end = (right_hand[0] + round(25 * scale), right_hand[1] - round(8 * scale))
        draw_limb(canvas, blade_start, blade_end, INK, SWORD, max(2, round(3 * scale)))
        canvas.line((blade_end[0] - 2, blade_end[1] + 2), (blade_end[0] + 3, blade_end[1] - 3), BOOT, 2)


def build_sheet(output_png=OUTPUT_PNG, output_json=OUTPUT_JSON):
    actions = {'idle': 6, 'walk': 8, 'jump': 5, 'attack': 7}
    sizes = {}
    for action, count in actions.items():
        sizes[action] = [
            (72 + (index % 3) * 4, 96 + ((index + 1) % 2) * 6)
            for index in range(count)
        ]

    sheet_width = max(sum(width + GAP for width, _ in frames) for frames in sizes.values())
    row_heights = [max(height for _, height in sizes[action]) for action in actions]
    sheet_height = sum(height + GAP for height in row_heights)
    sheet = PixelCanvas(sheet_width, sheet_height)
    metadata = {'width': sheet_width, 'height': sheet_height, 'frames': {}}

    row_top = 0
    for (action, frame_sizes), row_height in zip(sizes.items(), row_heights):
        metadata['frames'][action] = []
        frame_left = 0
        for frame_index, (frame_width, frame_height) in enumerate(frame_sizes):
            frame = PixelCanvas(frame_width, frame_height)
            draw_character(frame, action, frame_index, len(frame_sizes))
            top = row_top + row_height - frame_height
            for y in range(frame_height):
                source_start = y * frame_width * 4
                target_start = ((top + y) * sheet_width + frame_left) * 4
                sheet.pixels[target_start:target_start + frame_width * 4] = frame.pixels[
                    source_start:source_start + frame_width * 4
                ]
            metadata['frames'][action].append({
                'left': frame_left,
                'bottom': sheet_height - (top + frame_height),
                'width': frame_width,
                'height': frame_height,
            })
            frame_left += frame_width + GAP
        row_top += row_height + GAP

    sheet.save_png(output_png)
    with open(output_json, 'w', encoding='utf-8') as metadata_file:
        json.dump(metadata, metadata_file, indent=2)
        metadata_file.write('\n')
    return metadata


if __name__ == '__main__':
    result = build_sheet()
    print(f"Created {OUTPUT_PNG} ({result['width']}x{result['height']})")