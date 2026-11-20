"""Tests for identifying QR codes in image files."""

import unittest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.images.identify_qr_code import identify_qr_code


TESTS_DIR = Path(__file__).resolve().parent


class TestIdentifyQrCode(unittest.TestCase):
    def test_benign_jpg_is_not_a_qr_code(self) -> None:
        image = (TESTS_DIR / "testimage_jpg_benign.jpg").read_bytes()

        self.assertFalse(identify_qr_code(image))

    def test_benign_png_is_not_a_qr_code(self) -> None:
        image = (TESTS_DIR / "testimage_png_benign.png").read_bytes()

        self.assertFalse(identify_qr_code(image))

    def test_jpg_with_qr_code_is_identified(self) -> None:
        image = (TESTS_DIR / "testimage_jpg_with_qr.jpg").read_bytes()

        self.assertTrue(identify_qr_code(image))

    def test_png_with_qr_code_is_identified(self) -> None:
        image = (TESTS_DIR / "testimage_png_with_qr.png").read_bytes()

        self.assertTrue(identify_qr_code(image))

    def test_non_image_input_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            identify_qr_code(b"This is not an image.")


if __name__ == "__main__":
    unittest.main()
