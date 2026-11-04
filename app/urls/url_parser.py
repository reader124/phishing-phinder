"""Extract URLs from HTML MIME parts."""

from collections.abc import Mapping
import re
from typing import Any


# Keep the pattern deliberately focused on web URLs.  The trailing characters
# commonly used to close a sentence or an HTML attribute are removed below.
URL_PATTERN = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
TRAILING_URL_CHARACTERS = ".,!?;:)]}"


def extract_url(mime_part: Mapping[str, Any]) -> str | None:
    """Return the first URL found in an HTML MIME part.

    ``mime_part`` is expected to be one of the dictionaries returned by
    :func:`app.email.mime_parser.parse_eml`.  Non-HTML parts and HTML parts
    without a URL return ``None``.
    """

    content_type = mime_part.get("content_type")
    if not isinstance(content_type, str) or content_type.lower() != "text/html":
        return None

    payload = mime_part.get("payload")
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8", errors="replace")
    if not isinstance(payload, str):
        return None

    match = URL_PATTERN.search(payload)
    if match is None:
        return None

    return match.group(0).rstrip(TRAILING_URL_CHARACTERS)
