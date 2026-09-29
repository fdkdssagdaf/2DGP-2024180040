import json
import math
import os
import struct
import zlib


OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PNG = os.path.join(OUTPUT_DIR, 'character_sheet.png')
OUTPUT_JSON = os.path.join(OUTPUT_DIR, 'character_sheet.json')
SOURCE_PNG = os.path.join(OUTPUT_DIR, 'character.png')
GAP = 4
SOURCE_IMAGE = None


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


def load_source_image(path=SOURCE_PNG):
    with open(path, 'rb') as image_file:
        data = image_file.read()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Character source must be a PNG image')

    position = 8
    image_data = bytearray()
    while position < len(data):
        length = struct.unpack('>I', data[position:position + 4])[0]
        chunk_type = data[position + 4:position + 8]
        chunk_data = data[position + 8:position + 8 + length]
        position += length + 12
        if chunk_type == b'IHDR':
            width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(
                '>IIBBBBB', chunk_data,
            )
            if (bit_depth, color_type, interlace) != (8, 6, 0):
                raise ValueError('Character PNG must be non-interlaced 8-bit RGBA')
        elif chunk_type == b'IDAT':
            image_data.extend(chunk_data)
        elif chunk_type == b'IEND':
            break

    stride = width * 4
    filtered = zlib.decompress(image_data)
    pixels = bytearray(height * stride)

    def paeth(left, above, upper_left):
        estimate = left + above - upper_left
        distances = (abs(estimate - left), abs(estimate - above), abs(estimate - upper_left))
        return (left, above, upper_left)[distances.index(min(distances))]

    source_position = 0
    for y in range(height):
        filter_type = filtered[source_position]
        source_position += 1
        row_start = y * stride
        for x in range(stride):
            raw = filtered[source_position]
            source_position += 1
            left = pixels[row_start + x - 4] if x >= 4 else 0
            above = pixels[row_start + x - stride] if y else 0
            upper_left = pixels[row_start + x - stride - 4] if y and x >= 4 else 0
            if filter_type == 1:
                raw += left
            elif filter_type == 2:
                raw += above
            elif filter_type == 3:
                raw += (left + above) // 2
            elif filter_type == 4:
                raw += paeth(left, above, upper_left)
            elif filter_type != 0:
                raise ValueError(f'Unsupported PNG filter: {filter_type}')
            pixels[row_start + x] = raw & 255

    return width, height, pixels


def draw_character(canvas, action, frame_index, frame_count):
    global SOURCE_IMAGE
    if SOURCE_IMAGE is None:
        SOURCE_IMAGE = load_source_image()
    source_width, source_height, source_pixels = SOURCE_IMAGE

    for y in range(canvas.height):
        source_y = min(source_height - 1, y * source_height // canvas.height)
        for x in range(canvas.width):
            source_x = min(source_width - 1, x * source_width // canvas.width)
            source_start = (source_y * source_width + source_x) * 4
            target_start = (y * canvas.width + x) * 4
            canvas.pixels[target_start:target_start + 4] = source_pixels[source_start:source_start + 4]


def build_sheet(output_png=OUTPUT_PNG, output_json=OUTPUT_JSON):
    actions = {'idle': 6, 'walk': 8, 'jump': 5, 'attack': 7}
    sizes = {}
    source_width, source_height, _ = load_source_image()
    for action, count in actions.items():
        scales = [1.0, 1.08, 0.96, 1.04, 0.92, 1.12, 0.98, 1.06]
        sizes[action] = [
            (round(source_width * scales[index]), round(source_height * scales[index]))
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