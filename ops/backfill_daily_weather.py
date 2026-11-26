"""CL-CI-44: backfill ``daily[].weather`` into the published regional summaries.

``analyze_weather.py`` now emits a per-day weather block (WMO code, temperature
range, visibility) so the card face and the forecast modal can render the SAME
weather for a day. Re-running the full Open-Meteo pipeline just to add those
fields would re-fetch every Place and re-pin the whole bundle, so this script
re-derives the block from the already-published ``weather_details/`` shards —
the exact hourly rows the daily summaries were built from.

Run: python ops/backfill_daily_weather.py [region ...]
Default regions: tw jp us. Idempotent: it replaces ``daily[].weather``.
"""

import json
import sys
from pathlib import Path

# The repo root is one level up from ops/; analyze_weather.py lives there.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analyze_weather import _day_weather_block  # noqa: E402

REGIONS = ("tw", "jp", "us")


def backfill(region):
    summary_path = Path(f"{region}_weather.json")
    shard_dir = Path("weather_details") / region
    if not summary_path.exists() or not shard_dir.is_dir():
        print(f"skip {region}: missing summary or shard dir")
        return 0
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    touched = 0
    for spot in summary.get("spots", []):
        spot_id = spot.get("spot_id")
        if not spot_id:
            continue
        shard = shard_dir / f"{spot_id}.json"
        if not shard.exists():
            continue
        hourly = json.loads(shard.read_text(encoding="utf-8")).get("spot", {}).get("hourly_forecast") or []
        by_date = {}
        for row in hourly:
            if not isinstance(row, dict):
                continue
            date = row.get("local_date")
            if date:
                by_date.setdefault(date, []).append(row)
        for day in spot.get("daily", []):
            rows = by_date.get(day.get("date"))
            if not rows:
                continue
            winner = day.get("all") if isinstance(day.get("all"), dict) else None
            day["weather"] = _day_weather_block(rows, winner)
            touched += 1
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"{region}: {touched} day rows backfilled in {summary_path}")
    return touched


def main():
    regions = sys.argv[1:] or list(REGIONS)
    total = 0
    for region in regions:
        total += backfill(region)
    print(f"total day rows: {total}")


if __name__ == "__main__":
    main()
