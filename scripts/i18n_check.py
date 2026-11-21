"""Static QA for the locales/ sidecar (no weather logic, no recompute).

Checks:
  1. Every locale exposes exactly the same key set for ui.json / taxonomy.json /
     catalog.json as the zh-TW baseline (100% alignment).
  2. Long-locale title length warnings (mobile card overflow guard).
  3. Every locale file is valid JSON and every opportunity has a non-empty name.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "zh-TW"
LONG_LOCALES = {"de", "fr", "en", "ko", "es"}
TITLE_WARN = 64
FILES = ["ui", "taxonomy", "catalog"]


def flatten(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from flatten(v, f"{prefix}/{k}")
    else:
        yield prefix


def locale_dirs(root: Path):
    base = root / "locales"
    return sorted(p.name for p in base.iterdir() if p.is_dir())


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT
    langs = locale_dirs(root)
    if BASE not in langs:
        print(f"ERROR: missing base locale {BASE}", file=sys.stderr)
        return 2
    problems = []
    warnings = []

    for name in FILES:
        base_path = root / "locales" / BASE / f"{name}.json"
        if not base_path.exists():
            problems.append(f"missing {base_path}")
            continue
        base_keys = set(flatten(json.loads(base_path.read_text(encoding="utf-8"))))
        for lang in langs:
            p = root / "locales" / lang / f"{name}.json"
            if not p.exists():
                problems.append(f"missing {p}")
                continue
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                problems.append(f"invalid JSON {p}: {e}")
                continue
            keys = set(flatten(data))
            if keys != base_keys:
                problems.append(f"{lang}/{name}.json key mismatch: "
                                f"missing={len(base_keys - keys)} extra={len(keys - base_keys)}")

    # title length guard
    base_cat = json.loads((root / "locales" / BASE / "catalog.json").read_text(encoding="utf-8"))
    for lang in langs:
        if lang not in LONG_LOCALES:
            continue
        cat = json.loads((root / "locales" / lang / "catalog.json").read_text(encoding="utf-8"))
        for oid, node in cat.get("opportunities", {}).items():
            title = node.get("name") or ""
            if len(title) > TITLE_WARN:
                warnings.append(f"{lang}/{oid} title {len(title)} chars > {TITLE_WARN}")
        for pid, node in cat.get("places", {}).items():
            title = node.get("name") or ""
            if len(title) > TITLE_WARN:
                warnings.append(f"{lang}/{pid} place name {len(title)} chars > {TITLE_WARN}")

    # empty-name guard
    for lang in langs:
        cat = json.loads((root / "locales" / lang / "catalog.json").read_text(encoding="utf-8"))
        for oid, node in cat.get("opportunities", {}).items():
            if not (node.get("name") or "").strip():
                problems.append(f"{lang}/{oid} empty name")

    for w in warnings[:20]:
        print(f"WARN {w}")
    for p in problems[:20]:
        print(f"FAIL {p}")
    print(json.dumps({"locales": langs, "failures": len(problems), "warnings": len(warnings),
                      "base_opportunities": len(base_cat.get("opportunities", {}))}, ensure_ascii=False))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
