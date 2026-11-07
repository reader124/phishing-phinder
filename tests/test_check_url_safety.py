"""Integration tests for the Google Safe Browsing v5 URL lookup."""

import sys
import os
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.urls.check_url_safety import _decode_search_urls_response, check_url_safety


class TestCheckUrlSafety(unittest.TestCase):
    def test_decodes_safe_protobuf_response(self) -> None:
        # Field 2 contains a Duration message with 258 seconds.
        result = _decode_search_urls_response(b"\x12\x03\x08\x82\x02")

        self.assertEqual(result, {"threats": [], "cacheDuration": "258s"})

    def test_decodes_unsafe_protobuf_response(self) -> None:
        # ThreatUrl: url="http://malware.test", threatTypes=[MALWARE].
        url = b"http://malware.test"
        threat_url = b"\x0a" + bytes([len(url)]) + url + b"\x10\x01"
        response = b"\x0a" + bytes([len(threat_url)]) + threat_url

        result = _decode_search_urls_response(response)

        self.assertEqual(result["threats"][0]["url"], "http://malware.test")
        self.assertEqual(result["threats"][0]["threatTypes"], ["MALWARE"])

    @unittest.skipUnless(
        os.getenv("GOOGLE_SAFE_BROWSING_API_KEY"),
        "GOOGLE_SAFE_BROWSING_API_KEY is not set",
    )
    def test_google_com_is_safe(self) -> None:
        result = check_url_safety(["https://google.com"])

        self.assertIsInstance(result, dict)
        self.assertTrue(result, "Safe Browsing request returned no response")
        self.assertFalse(result.get("threats", []), result)

    @unittest.skipUnless(
        os.getenv("GOOGLE_SAFE_BROWSING_API_KEY"),
        "GOOGLE_SAFE_BROWSING_API_KEY is not set",
    )
    def test_safe_browsing_malware_url_is_unsafe(self) -> None:
        result = check_url_safety(
            ["http://testsafebrowsing.appspot.com/s/malware.html"]
        )

        self.assertIsInstance(result, dict)
        self.assertTrue(result, "Safe Browsing request returned no response")
        self.assertTrue(result.get("threats"), result)


if __name__ == "__main__":
    unittest.main()
