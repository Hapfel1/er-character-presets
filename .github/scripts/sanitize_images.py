"""Re-encode submitted preset images into a preset folder.

Usage: sanitize_images.py <source_dir> <preset_dir>

face/body/preview images (png/jpg/jpeg, any case) are decoded and saved as
PNG, which rejects files that are not images and drops EXIF and other
embedded metadata. preview.png falls back to face, then body, as before.
"""

import sys
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = 40_000_000

MAX_BYTES = 15 * 1024 * 1024
MAX_EDGE = 2560
EXTS = {".png", ".jpg", ".jpeg"}


def find(src: Path, stem: str) -> Path | None:
    for path in sorted(src.iterdir()):
        if (
            path.is_file()
            and not path.is_symlink()
            and path.stem.lower() == stem
            and path.suffix.lower() in EXTS
        ):
            return path
    return None


def reencode(path: Path, dest: Path) -> None:
    if path.stat().st_size > MAX_BYTES:
        raise ValueError(f"{path.name} is larger than {MAX_BYTES} bytes")
    with Image.open(path) as probe:
        probe.verify()
    with Image.open(path) as img:
        img.load()
        img = img.convert("RGB")
        img.thumbnail((MAX_EDGE, MAX_EDGE))
        img.save(dest, "PNG", optimize=True)


def main() -> int:
    src, dest = Path(sys.argv[1]), Path(sys.argv[2])
    if not src.is_dir():
        print("No images extracted")
        return 0
    dest.mkdir(parents=True, exist_ok=True)
    found = {}
    for kind in ("face", "body", "preview"):
        path = find(src, kind)
        if path is not None:
            reencode(path, dest / f"{kind}.png")
            found[kind] = True
            print(f"{kind}: re-encoded from {path.name}")
    if "preview" not in found:
        for kind in ("face", "body"):
            if kind in found:
                (dest / "preview.png").write_bytes((dest / f"{kind}.png").read_bytes())
                print(f"preview: copied from {kind}")
                break
    return 0


if __name__ == "__main__":
    sys.exit(main())
