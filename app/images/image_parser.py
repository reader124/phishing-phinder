"""Extract image payloads from parsed MIME parts."""

from collections.abc import Mapping
from typing import Any


def extract_image(mime_part: Mapping[str, Any]) -> bytes | None:
    """Return the decoded image bytes from an image MIME part.

    ``mime_part`` is expected to be one of the dictionaries returned by
    :func:`app.email.mime_parser.parse_eml`.  Non-image parts and image parts
    without a decoded byte payload return ``None``.
    """

    content_type = mime_part.get("content_type")
    if not isinstance(content_type, str):
        return None

    media_type = content_type.split(";", 1)[0].strip().lower()
    if not media_type.startswith("image/"):
        return None

    payload = mime_part.get("payload")
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, bytearray):
        return bytes(payload)

    return None
