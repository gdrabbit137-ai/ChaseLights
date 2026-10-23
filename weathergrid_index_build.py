"""Build the WeatherGrid cache index.

Scans the published weathergrid/ JSON bundles, hashes each file and writes
weathergrid/index.json. The browser cache layer (assets/weather-map.js) uses
the index to fetch every bundle through an immutable, content-addressed URL
(?v=<sha12>) backed by the Cache API, so repeat visitors never re-download
bundles that have not changed since their last visit.

Run AFTER all bundle copies/removals in a publish step, so the index always
describes exactly the files present in the same commit.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

INDEX_VERSION = 1
SUFFIXES = ("_browser.json", "_qc.json")


def build_index(root: Path) -> dict:
    files: dict[str, dict] = {}
    for path in sorted(root.iterdir()):
        if not path.is_file() or path.name == "index.json":
            continue
        if not path.name.endswith(SUFFIXES):
            continue
        data = path.read_bytes()
        files[path.name] = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
        }
    return {
        "index_version": INDEX_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "files": files,
    }


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path("weathergrid")
    if not root.is_dir():
        print(f"weathergrid directory not found: {root}", file=sys.stderr)
        return 1
    index = build_index(root)
    (root / "index.json").write_text(
        json.dumps(index, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"index written: {len(index['files'])} files, "
          f"{sum(v['bytes'] for v in index['files'].values())} bytes hashed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
