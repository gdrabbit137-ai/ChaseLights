"""Audit the B121 WeatherGrid coverage registry against the runtime catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from weathergrid_coverage import audit_coverage_registry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", default="runtime_catalog_v004_r4_2.json")
    parser.add_argument(
        "--registry",
        default="weathergrid_coverage_registry_r4_2.json",
    )
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    registry = json.loads(Path(args.registry).read_text(encoding="utf-8"))
    audit = audit_coverage_registry(catalog, registry)

    payload = json.dumps(audit, ensure_ascii=False, indent=2)
    print(payload)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")

    # needs_research entries are expected migration work, not CI failures.
    structural_failures = [
        row
        for row in audit["results"]
        if any(
            "not found" in error
            or "invalid" in error
            or "mismatch" in error
            or "duplicate" in error
            for error in row.get("errors", [])
        )
    ]
    return 1 if structural_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
