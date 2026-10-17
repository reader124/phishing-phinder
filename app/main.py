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
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from app.email.mime_parser import parse_eml


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

    # Test that mime_parser works by printing out the result.
    print(mime_parts)


if __name__ == "__main__":
    main()
