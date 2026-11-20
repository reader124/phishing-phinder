# Phishing Phinder Main
# Sean Reading

import sys
import tkinter as tk
from tkinter import filedialog
from pathlib import Path


# Support both ``python -m app.main`` from the project root and
# ``python app/main.py``.
try:
    from app.email.mime_parser import parse_eml
    from app.images.identify_qr_code import identify_qr_code
    from app.images.image_parser import extract_image
    from app.urls.check_url_safety import check_url_safety
    from app.urls.url_parser import extract_url
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from app.email.mime_parser import parse_eml
    from app.images.identify_qr_code import identify_qr_code
    from app.images.image_parser import extract_image
    from app.urls.check_url_safety import check_url_safety
    from app.urls.url_parser import extract_url


def select_eml_file() -> Path | None:
    """Open a file picker and return the selected .eml path, if any."""

    root = tk.Tk()
    root.withdraw()
    try:
        selected_file = filedialog.askopenfilename(
            title="Select an email file",
            filetypes=[("Email files", "*.eml"), ("All files", "*.*")],
        )
    finally:
        root.destroy()

    return Path(selected_file) if selected_file else None


def main() -> None:
    eml_path = select_eml_file()
    if eml_path is None:
        print("No .eml file selected.")
        return

    try:
        mime_parts = parse_eml(eml_path)
    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"Could not parse {eml_path}: {error}")
        return

    # print(f"MIME parts: {len(mime_parts)}")

    urls: list[str] = []
    for part in mime_parts:
        # print(part["content_type"])

        if part["content_type"].lower() == "text/html":
            url = extract_url(part)
            if url is not None:
                urls.append(url)

        elif part["content_type"].lower().startswith("image/"):
            image = extract_image(part)
            if image is not None:
                is_qr_code = identify_qr_code(image)
                image_name = part.get("filename") or "Image"
                print(f"{image_name} is a QR code: {is_qr_code}")

    # print(urls)

    # url_check_result = check_url_safety(urls)
    
    # print(url_check_result)


if __name__ == "__main__":
    main()
