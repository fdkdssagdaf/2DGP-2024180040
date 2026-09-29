import ast
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from make_sprite_sheet import PixelCanvas, build_sheet, draw_character, load_source_image


class AnimationAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.png_path = Path(cls.temp_dir.name) / 'character_sheet.png'
        cls.json_path = Path(cls.temp_dir.name) / 'character_sheet.json'
        cls.metadata = build_sheet(cls.png_path, cls.json_path)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_action_frame_counts_are_distinct(self):
        frame_counts = {
            action: len(frames)
            for action, frames in self.metadata['frames'].items()
        }
        self.assertEqual(frame_counts, {
            'idle': 6,
            'walk': 8,
            'jump': 5,
            'attack': 7,
        })

    def test_frame_rectangles_fit_the_sheet_and_vary_in_size(self):
        for frames in self.metadata['frames'].values():
            dimensions = set()
            for frame in frames:
                dimensions.add((frame['width'], frame['height']))
                self.assertGreaterEqual(frame['left'], 0)
                self.assertGreaterEqual(frame['bottom'], 0)
                self.assertLessEqual(frame['left'] + frame['width'], self.metadata['width'])
                self.assertLessEqual(frame['bottom'] + frame['height'], self.metadata['height'])
            self.assertGreater(len(dimensions), 1)

    def test_sheet_uses_the_exact_character_from_lec05(self):
        source_width, source_height, source_pixels = load_source_image()
        canvas = PixelCanvas(source_width, source_height)
        draw_character(canvas, 'idle', 0, 6)
        self.assertEqual(bytes(canvas.pixels), bytes(source_pixels))

        _, _, sheet_pixels = load_source_image(self.png_path)
        source_colors = {
            bytes(source_pixels[index:index + 4])
            for index in range(0, len(source_pixels), 4)
        }
        sheet_colors = {
            bytes(sheet_pixels[index:index + 4])
            for index in range(0, len(sheet_pixels), 4)
        }
        self.assertEqual(sheet_colors - {b'\x00\x00\x00\x00'}, source_colors)

    def test_sheet_generation_is_reproducible(self):
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first_png = Path(first_dir) / 'sheet.png'
            first_json = Path(first_dir) / 'sheet.json'
            second_png = Path(second_dir) / 'sheet.png'
            second_json = Path(second_dir) / 'sheet.json'
            build_sheet(first_png, first_json)
            build_sheet(second_png, second_json)
            self.assertEqual(first_png.read_bytes(), second_png.read_bytes())
            self.assertEqual(first_json.read_bytes(), second_json.read_bytes())

    def test_png_chunks_and_pixel_data_are_valid(self):
        data = self.png_path.read_bytes()
        self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
        position = 8
        image_data = bytearray()
        image_size = None
        while position < len(data):
            length = struct.unpack('>I', data[position:position + 4])[0]
            chunk_type = data[position + 4:position + 8]
            chunk_data = data[position + 8:position + 8 + length]
            expected_crc = struct.unpack('>I', data[position + 8 + length:position + 12 + length])[0]
            self.assertEqual(zlib.crc32(chunk_type + chunk_data) & 0xffffffff, expected_crc)
            if chunk_type == b'IHDR':
                image_size = struct.unpack('>II', chunk_data[:8])
            elif chunk_type == b'IDAT':
                image_data.extend(chunk_data)
            position += length + 12
            if chunk_type == b'IEND':
                break

        self.assertEqual(image_size, (self.metadata['width'], self.metadata['height']))
        pixels = zlib.decompress(image_data)
        row_size = self.metadata['width'] * 4
        self.assertEqual(len(pixels), (row_size + 1) * self.metadata['height'])
        self.assertTrue(all(pixels[row * (row_size + 1)] == 0 for row in range(self.metadata['height'])))
        self.assertTrue(any(pixels[offset] for offset in range(4, len(pixels), 4)))

    def test_viewer_matches_assignment_playback_requirements(self):
        viewer_path = Path(__file__).with_name('animation_viewer.py')
        tree = ast.parse(viewer_path.read_text(encoding='utf-8'))
        constants = {}
        for node in tree.body:
            if isinstance(node, ast.Assign):
                target = node.targets[0]
                if isinstance(target, ast.Name):
                    try:
                        constants[target.id] = ast.literal_eval(node.value)
                    except (ValueError, TypeError):
                        pass
                elif isinstance(target, ast.Tuple):
                    try:
                        values = ast.literal_eval(node.value)
                    except (ValueError, TypeError):
                        continue
                    for name, value in zip(target.elts, values):
                        if isinstance(name, ast.Name):
                            constants[name.id] = value

        self.assertEqual(constants['REPEAT_COUNT'], 5)
        self.assertEqual(constants['PAUSE_SECONDS'], 1)
        self.assertEqual(set(constants['ANIMATIONS']), {'idle', 'walk', 'jump', 'attack'})
        self.assertGreaterEqual(constants['DISPLAY_HEIGHT'], constants['CANVAS_HEIGHT'] / 2)

    def test_attack_draws_a_visible_slash(self):
        viewer_path = Path(__file__).with_name('animation_viewer.py')
        tree = ast.parse(viewer_path.read_text(encoding='utf-8'))
        attack_branches = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.If)
            and any(isinstance(value, ast.Name) and value.id == 'animation' for value in ast.walk(node.test))
            and any(isinstance(value, ast.Constant) and value.value == 'attack' for value in ast.walk(node.test))
        ]
        self.assertTrue(attack_branches)
        slash_calls = [
            node for branch in attack_branches for node in ast.walk(branch)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == 'draw_line'
        ]
        self.assertEqual(len(slash_calls), 5)


if __name__ == '__main__':
    unittest.main()