"""Utilities for extracting MIME parts from an RFC 5322 .eml file."""

from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Any


def parse_eml(eml_path: str | Path) -> list[dict[str, Any]]:
    """Parse *eml_path* and return one dictionary for each MIME part.

    Text payloads are returned as strings and non-text payloads are returned as
    decoded bytes. Multipart container parts are included so callers can see
    the complete MIME structure.
    """

    path = Path(eml_path)
    if path.suffix.lower() != ".eml":
        raise ValueError(f"Expected a .eml file, got: {path.name}")
    if not path.is_file():
        raise FileNotFoundError(f"EML file not found: {path}")

    with path.open("rb") as eml_file:
        message = BytesParser(policy=policy.default).parse(eml_file)

    parts: list[dict[str, Any]] = []
    for part_number, part in enumerate(message.walk(), start=1):
        payload = None if part.is_multipart() else part.get_payload(decode=True)
        if payload is not None and part.get_content_maintype() == "text":
            charset = part.get_content_charset() or "utf-8"
            payload = payload.decode(charset, errors="replace")

        parts.append(
            {
                "part_number": part_number,
                "content_type": part.get_content_type(),
                "content_disposition": part.get_content_disposition(),
                "filename": part.get_filename(),
                "charset": part.get_content_charset(),
                "content_transfer_encoding": part.get("Content-Transfer-Encoding"),
                "is_multipart": part.is_multipart(),
                "payload": payload,
            }
        )

    return parts
