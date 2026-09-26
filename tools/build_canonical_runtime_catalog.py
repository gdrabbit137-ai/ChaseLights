"""Build the one-time canonical ChaseLights R4.2 runtime catalog.

Trigger-safe migration builder for the catalog cutover.

This migration utility reconstructs the effective production catalog from the
legacy B15 compressed payload plus later batch additions through opportunities.py.
After cutover, runtime_catalog_v004_r4_2.json is the production source of truth;
the legacy fragments remain historical migration inputs only.
"""

from copy import deepcopy
import json
from pathlib import Path

import opportunities

OUTPUT = Path("runtime_catalog_v004_r4_2.json")
SOURCE_FILES = [
    "runtime_catalog_v004_r4_2_b15.compact.part1.b64",
    "runtime_catalog_v004_r4_2_b15.compact.part2.b64",
    "runtime_catalog_v004_r4_2_b15.compact.part3.b64",
    "runtime_catalog_v004_r4_2_b15.compact.part4.b64",
    "runtime_catalog_v004_r4_2_b15.compact.part5.b64",
    "runtime_catalog_v004_r4_2_b28_additions.json",
    "runtime_catalog_v004_r4_2_b32_jp_batch01.json",
    "runtime_catalog_v004_r4_2_b33_hualien_additions.json",
    "runtime_catalog_v004_r4_2_b34_liushishishan_additions.json",
    "runtime_catalog_v004_r4_2_b35_liyu_subjects.json",
]


def _counts(spots):
    return {
        "spots": len(spots),
        "opportunities": sum(len(s.get("opportunities", [])) for s in spots),
        "condition_variants": sum(
            len(o.get("condition_variants", []))
            for s in spots
            for o in s.get("opportunities", [])
        ),
        "profile_viewpoint_relations": sum(
            len(o.get("viewpoints", []))
            for s in spots
            for o in s.get("opportunities", [])
        ),
    }


def main():
    spots = deepcopy(opportunities._ACTIVE_SPOTS)
    for spot in spots:
        for opportunity in spot.get("opportunities", []):
            opportunities._apply_metadata_override(opportunity)

    counts = _counts(spots)
    if counts != opportunities.CATALOG_COUNTS:
        raise SystemExit(
            f"canonical count mismatch: computed={counts} expected={opportunities.CATALOG_COUNTS}"
        )

    payload = {
        "schema_version": "v0.04-r4.2-canonical-1",
        "catalog_role": "canonical_runtime_catalog",
        "migration_sources": SOURCE_FILES,
        "counts": counts,
        "spots": spots,
    }
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT} with {counts}")


if __name__ == "__main__":
    main()
