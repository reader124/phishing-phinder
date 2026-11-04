"""Tests for extracting URLs from HTML MIME parts."""

import unittest
import sys
from pathlib import Path

# Allow this test to be run directly as ``python tests/test_url_parser.py``.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.urls.url_parser import extract_url


class TestUrlParser(unittest.TestCase):
    def test_extracts_url_from_html_attribute(self) -> None:
        mime_part = {
            "content_type": "text/html",
            "payload": '<a href="https://example.com/login">Sign in</a>',
        }

        self.assertEqual(extract_url(mime_part), "https://example.com/login")

    def test_extracts_url_from_html_text_and_removes_sentence_punctuation(self) -> None:
        mime_part = {
            "content_type": "text/html",
            "payload": "Visit https://example.com/account.",
        }

        self.assertEqual(extract_url(mime_part), "https://example.com/account")

    def test_returns_none_for_non_html_part(self) -> None:
        mime_part = {
            "content_type": "text/plain",
            "payload": "Visit https://example.com",
        }

        self.assertIsNone(extract_url(mime_part))

    def test_returns_none_when_html_has_no_url(self) -> None:
        mime_part = {"content_type": "text/html", "payload": "Nothing to see here."}

        self.assertIsNone(extract_url(mime_part))


if __name__ == "__main__":
    unittest.main()
