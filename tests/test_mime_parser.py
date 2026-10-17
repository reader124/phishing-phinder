"""Tests for the .eml MIME parser."""

import unittest
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.email.mime_parser import parse_eml  # noqa: E402


PARSER_FILE = TESTS_DIR.parent / "app" / "email" / "mime_parser.py"
EML_FIXTURE = TESTS_DIR / "Testing the phishing_phinder.eml"


class TestMimeParser(unittest.TestCase):
    def test_missing_file_raises_file_not_found_error(self) -> None:
        missing_file = TESTS_DIR / "does_not_exist.eml"

        with self.assertRaises(FileNotFoundError):
            parse_eml(missing_file)

    def test_mime_parser_py_is_rejected_as_non_eml_file(self) -> None:
        with self.assertRaises(ValueError):
            parse_eml(PARSER_FILE)

    def test_phishing_phinder_eml_returns_expected_mime_parts(self) -> None:
        parts = parse_eml(EML_FIXTURE)

        self.assertEqual(len(parts), 7)
        self.assertEqual(
            [part["content_type"] for part in parts],
            [
                "multipart/mixed",
                "multipart/alternative",
                "text/plain",
                "text/html",
                "image/png",
                "image/png",
                "text/x-python",
            ],
        )
        self.assertEqual(
            [part["filename"] for part in parts],
            [None, None, None, None, "benign_image.png", "image_with_qr_code.png", "write_my_name.py"],
        )
        self.assertIsInstance(parts[2]["payload"], str)
        self.assertIsInstance(parts[4]["payload"], bytes)


if __name__ == "__main__":
    unittest.main()
