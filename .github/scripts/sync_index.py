"""Bring index.json in line with the preset folders under presets/.

Existing entries keep their position and fields. Folders without an entry
are appended in ID order, built from their data.json. Entries whose folder
is gone are dropped. last_updated changes only when the preset list does.
"""

import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "index.json"
PRESETS = ROOT / "presets"
FOLDER_RE = re.compile(r"^preset_(\d+)$")


def build_entry(preset_id: str) -> dict:
    folder = PRESETS / preset_id
    data = json.loads((folder / "data.json").read_text(encoding="utf-8"))
    base = f"presets/{preset_id}/"
    entry = {
        "id": preset_id,
        "name": data.get("name", ""),
        "author": data.get("author", ""),
        "tags": data.get("tags", []),
        "description": data.get("description", ""),
        "created": data.get("created", ""),
        "data_url": base + "data.json",
        "screenshot_url": base + "preview.png",
    }
    if (folder / "face.png").exists():
        entry["face_url"] = base + "face.png"
    if (folder / "body.png").exists():
        entry["body_url"] = base + "body.png"
    return entry


def main() -> int:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    folders = sorted(
        (
            p.name
            for p in PRESETS.iterdir()
            if FOLDER_RE.match(p.name) and (p / "data.json").is_file()
        ),
        key=lambda name: int(FOLDER_RE.match(name).group(1)),
    )
    present = set(folders)

    presets = [p for p in index["presets"] if p.get("id") in present]
    listed = {p["id"] for p in presets}
    presets += [build_entry(f) for f in folders if f not in listed]

    if presets == index["presets"]:
        print("index.json is up to date")
        return 0

    added = [p["id"] for p in presets if p["id"] not in {e.get("id") for e in index["presets"]}]
    removed = [p.get("id") for p in index["presets"] if p.get("id") not in present]
    print(f"added: {added or 'none'}, removed: {removed or 'none'}")

    index["presets"] = presets
    index["last_updated"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
