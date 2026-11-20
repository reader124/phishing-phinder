"""Identify QR codes in image bytes using OpenCV."""

import cv2
import numpy as np


def identify_qr_code(image: bytes | bytearray) -> bool:
    """Return whether *image* contains a detectable QR code.

    ``image`` should be the decoded byte payload returned by
    :func:`app.images.image_parser.extract_image`.  Detection does not
    require the QR code contents to be successfully decoded.
    """

    if not isinstance(image, (bytes, bytearray)) or not image:
        raise ValueError("Input must contain a non-empty image payload.")

    image_array = np.frombuffer(image, dtype=np.uint8)
    decoded_image = cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)
    if decoded_image is None:
        raise ValueError("Input does not contain a valid image.")

    detector = cv2.QRCodeDetector()
    _, points = detector.detect(decoded_image)
    return points is not None and len(points) > 0
