"""Tests for extracting URLs from QR codes in image files."""

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.images.qr_to_url import qr_to_url  # noqa: E402


TESTS_DIR = Path(__file__).resolve().parent
EXPECTED_URL = "https://readingreality.itch.io/origami-fish-to-dragon"


class TestQrToUrl(unittest.TestCase):
    def test_extracts_url_from_jpg_qr_code(self) -> None:
        image = (TESTS_DIR / "testimage_jpg_with_qr.jpg").read_bytes()

        self.assertEqual(qr_to_url(image), EXPECTED_URL)

    def test_extracts_url_from_png_qr_code(self) -> None:
        image = (TESTS_DIR / "testimage_png_with_qr.png").read_bytes()

        self.assertEqual(qr_to_url(image), EXPECTED_URL)

    def test_returns_none_for_benign_png(self) -> None:
        image = (TESTS_DIR / "testimage_png_benign.png").read_bytes()

        self.assertIsNone(qr_to_url(image))


if __name__ == "__main__":
    unittest.main()
