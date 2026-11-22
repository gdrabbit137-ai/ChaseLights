#!/usr/bin/env python3
"""CL-DATA-85: align the derived `conditions_v2` view with the legacy contracts.

Scope (owner ruling 2026-11-22, ticket CL-DATA-85 — pure structural alignment):

  * `tw-001-P04` is the only canonical contract still on schema 2.1.0 with no
    `windows` / `conditions_v2` derived view. It is migrated with the same
    deterministic migrator CL-DATA-80 used.
  * 48 further contracts carry a `conditions_v2.required` list that no longer
    matches the legacy `conditions` (their REQUIRED entries were added or
    re-idded by later hand edits). Only `required` is rebuilt; `quality` is
    never touched.
  * `jp-026-P01` / `tw-066-P01` additionally store the quality entry under the
    id `...-GHQ1` while their legacy condition (and therefore the migrator) uses
    `...-GH1`. The ids are aligned. This is scoring-neutral: the quality engine
    reads `entry["id"]` only for `kind == "binary"` entries, and this entry is a
    numeric trapezoid that is scored by `metric`.

Hard boundaries: no threshold changes, no weight/quad changes, no evaluation run,
no weather recompute, no re-pin. The script is idempotent: a second run reports
zero changes.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OPP_DIR = ROOT / "data/v2/opportunities"
MIGRATOR = ROOT / "data/v2/migration/contract_v2_migrate.py"
ID_ALIGNMENT = {"jp-026-P01": ("C-jp-026-P01-GHQ1", "C-jp-026-P01-GH1"),
                "tw-066-P01": ("C-tw-066-P01-GHQ1", "C-tw-066-P01-GH1")}


def load_migrator():
    spec = importlib.util.spec_from_file_location("contract_v2_migrate", MIGRATOR)
    assert spec and spec.loader, "migrator module cannot be loaded"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def empty_report() -> dict:
    return {"contracts": 0, "changed": 0, "seasonal_contracts": 0,
            "required_entries": 0, "quality_entries": 0,
            "provisional_quality": 0, "time_of_day_names": set(),
            "unmapped_templates": set()}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="report what would change without writing")
    args = parser.parse_args(argv)
    mig = load_migrator()

    migrated, synced, renamed = [], [], []
    for path in sorted(OPP_DIR.glob("*.json")):
        raw = path.read_bytes()
        # Preserve the record's own line ending: most canonical files are CRLF,
        # and a silent whole-file conversion would bury the real one-line edit.
        newline = "\r\n" if b"\r\n" in raw else "\n"
        # Preserve the file's own indent width as well; canonical records are
        # mixed (indent 1 and 2), and re-indenting buries a one-line change in a
        # 400-line diff.
        indent = 2 if raw.startswith(b'{\n  "') else 1
        doc = json.loads(raw.decode("utf-8"))
        cc = doc.get("condition_contract") or {}
        oid = doc.get("opportunity_id")
        before = copy.deepcopy(doc)
        cc2 = doc.get("condition_contract") or {}

        if not isinstance(cc2.get("conditions_v2"), dict):
            # Whole-contract migration (tw-001-P04): no derived view exists yet,
            # so nothing hand-authored can be overwritten.
            mig.migrate_doc(doc, empty_report())
            migrated.append(oid)
        else:
            derived = copy.deepcopy(doc)
            mig.migrate_doc(derived, empty_report())
            want = derived["condition_contract"]["conditions_v2"]
            v2 = cc2["conditions_v2"]
            if v2.get("required") != want["required"]:
                v2["required"] = want["required"]
                synced.append(oid)
            if oid in ID_ALIGNMENT:
                old_id, new_id = ID_ALIGNMENT[oid]
                for entry in v2.get("quality") or []:
                    if entry.get("id") == old_id:
                        entry["id"] = new_id
                        renamed.append(oid)

        if doc != before:
            if not args.check:
                path.write_text(json.dumps(doc, ensure_ascii=False, indent=indent) + "\n",
                                encoding="utf-8", newline=newline)

    print(json.dumps({"status": "OK", "check": args.check,
                      "migrated": migrated,
                      "required_synced": len(synced),
                      "id_aligned": renamed}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
