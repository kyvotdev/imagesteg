import tempfile
import unittest
from pathlib import Path

from PIL import Image
from imagesteg import encode_text_to_image, decode_text_from_image


class SteganographyTests(unittest.TestCase):
    def test_round_trip_and_alpha(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.png'
            result = Path(directory) / 'result.png'
            Image.new('RGBA', (32, 32), (124, 32, 78, 91)).save(source)
            for message in ('Привет, секрет! 🕵', ''):
                encode_text_to_image(source, result, message)
                self.assertEqual(decode_text_from_image(result), message)
                with Image.open(result) as image:
                    self.assertEqual(set(image.getchannel('A').tobytes()), {91})

    def test_invalid_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.png'
            result = Path(directory) / 'result.png'
            Image.new('RGB', (2, 2), (255, 255, 255)).save(source)
            for output, message in ((result, 'too long'), (result, 'a\0b'),
                                    (Path(directory) / 'result.jpg', 'a')):
                with self.assertRaises(ValueError):
                    encode_text_to_image(source, output, message)
            with self.assertRaisesRegex(ValueError, 'Конец сообщения'):
                decode_text_from_image(source)

    def test_grayscale_decode(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'gray.png'
            Image.new('L', (8, 8), 255).save(source)
            with self.assertRaises(ValueError):
                decode_text_from_image(source)


if __name__ == '__main__':
    unittest.main()
