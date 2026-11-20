"""Extract URLs from QR codes in image bytes using OpenCV."""

from urllib.parse import urlparse

import cv2
import numpy as np


def qr_to_url(image: bytes | bytearray) -> str | None:
    """Return the HTTP(S) URL encoded in an image's QR code.

    ``image`` should be the decoded byte payload returned by
    :func:`app.images.image_parser.extract_image`.  Images without a QR code,
    or QR codes containing non-URL data, return ``None``.

    Raises:
        ValueError: If *image* is empty, not bytes, or is not a valid image.
    """

    if not isinstance(image, (bytes, bytearray)) or not image:
        raise ValueError("Input must contain a non-empty image payload.")

    image_array = np.frombuffer(image, dtype=np.uint8)
    decoded_image = cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)
    if decoded_image is None:
        raise ValueError("Input does not contain a valid image.")

    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(decoded_image)
    if not data:
        return None

    url = data.strip()
    parsed_url = urlparse(url)
    if parsed_url.scheme.lower() not in {"http", "https"} or not parsed_url.netloc:
        return None

    return url
