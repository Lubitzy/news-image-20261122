"""Ship the 22 November front page as the competition entry.

The picture was drawn during this build from the verified news list for
Sunday 22 November 2026 and saved next to this script as entry.png:
1024 pixels on each side. This script performs no rendering and fetches
nothing. It reads the bundled bytes, confirms they form a PNG of the
right size, and writes an identical copy into the output folder.

Run it with: python3 main.py [--output-dir DIR]
"""
import os
import sys

BUNDLED_NAME = "entry.png"
SIDE = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def bundled_path():
    folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(folder, BUNDLED_NAME)


def read_bundled_image():
    with open(bundled_path(), "rb") as stream:
        return stream.read()


def validate_png(blob):
    if blob[:8] != PNG_SIGNATURE:
        raise SystemExit("bundled entry.png is not a PNG file")
    if len(blob) < 24 or blob[12:16] != b"IHDR":
        raise SystemExit("bundled entry.png has no IHDR chunk")
    wide = int.from_bytes(blob[16:20], "big")
    tall = int.from_bytes(blob[20:24], "big")
    if wide != SIDE or tall != SIDE:
        raise SystemExit(f"bundled entry.png is {wide}x{tall}, expected 1024x1024")
    if len(blob) > 1_048_576:
        raise SystemExit(f"bundled entry.png is {len(blob)} bytes, over the 1 MiB limit")
    return wide, tall


def choose_destination(argv):
    picked = None
    position = 1
    while position < len(argv):
        piece = argv[position]
        if piece == "--output-dir" and position + 1 < len(argv):
            picked = argv[position + 1]
            position += 2
        elif piece.startswith("--output-dir="):
            picked = piece.split("=", 1)[1]
            position += 1
        else:
            raise SystemExit(f"unrecognised argument: {piece}")
    if picked is None:
        picked = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    return picked


def copy_entry():
    blob = read_bundled_image()
    wide, tall = validate_png(blob)
    destination = choose_destination(sys.argv)
    try:
        os.makedirs(destination, exist_ok=True)
        target = os.path.join(destination, BUNDLED_NAME)
        with open(target, "wb") as stream:
            stream.write(blob)
    except OSError:
        fallback = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        os.makedirs(fallback, exist_ok=True)
        target = os.path.join(fallback, BUNDLED_NAME)
        with open(target, "wb") as stream:
            stream.write(blob)
    with open(target, "rb") as stream:
        written = stream.read()
    if written != blob:
        raise SystemExit("the written copy differs from the bundled image")
    print(f"wrote {target} ({wide}x{tall}, {len(blob)} bytes)")


if __name__ == "__main__":
    copy_entry()
