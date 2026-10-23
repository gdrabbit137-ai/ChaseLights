"""Deterministic W4 solar pilot artifact builder (research-only, RAW_ONLY).

Generates the immutable sidecar artifact consumed by apps/web-v2
solar-pilot: a fixed window of daily solar WINDOW results for the tw-036
representative place sample, each result individually validated against
the pinned W1 solar-window-result-v0.1 schema. Pure computation: no
network access, no photography score, no verdict, no directions.

The committed artifact records the actual generation instant and the
generator version; regenerating with the same --start-date/--days and a
fixed --computed-at reproduces identical bytes (proven by test).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages/models-v2"))

from solar_window import (  # noqa: E402
    ALGORITHM_VERSION, MODEL_ID, RESULT_SCHEMA, compute_solar_window)

PLACE_ID = "tw-036"
PILOT_ID = "tw-036-solar-window-v0.1"
GENERATOR_VERSION = "0.1.0"
TZ_NAME = "Asia/Taipei"
# Representative place sample: the same tw-036 request point as the hourly
# weather pilot; explicitly NOT a surveyed tripod GPS (coordinate_role keeps
# that distinction inside every per-day result).
OBSERVER = {
    "coordinate_role": "representative_place_sample",
    "lat": 24.0314,
    "lon": 121.6272,
    "coordinate_source": "representative place sample (tw-036 weather pilot request point)",
    "uncertainty_m": None,
    "altitude_m": 6,
}
MODEL = {
    "model_id": MODEL_ID,
    "algorithm_version": ALGORITHM_VERSION,
    "horizon_assumption": "ideal_unobstructed",
    "sun_altitude_crossing_deg": -0.833,
}
LIMITATIONS_I18N = {
    "zh-TW": ("理想無遮蔽地平線的區域性日出日落估算（代表性地點樣本，非實測機位座標）；"
              "未驗證實際地形地平線、大氣折射、雲況或攝影適合度，不構成拍攝建議。"),
    "en": ("Regional sunrise/sunset at an ideal unobstructed horizon from a "
           "representative place sample (not a surveyed camera point); actual "
           "terrain horizon, refraction, clouds and photographic suitability "
           "are unverified. Not a shooting recommendation."),
    "ja": ("代表地点サンプル（実測の撮影座標ではない）に基づく、遮蔽のない理想水平線での"
           "日の出・日の入り推定。実際の地形・屈折・雲・撮影適性は未確認で、撮影提案ではありません。"),
}
ATTRIBUTION_I18N = {
    "zh-TW": "演算法：NOAA 太陽計算法（時間方程／赤緯）與 Jean Meeus《Astronomical Algorithms》；以 -0.833° 視高度近似。",
    "en": "Algorithms: NOAA Solar Calculation Details (equation of time / declination) and Jean Meeus, Astronomical Algorithms; -0.833 deg apparent-altitude approximation.",
    "ja": "アルゴリズム：NOAA 太陽計算法（均時差・赤緯）および Jean Meeus『Astronomical Algorithms』。-0.833 度近似。",
}


def build(start_date: str, days: int, computed_at: datetime, tzdb_version: str | None) -> dict:
    from solar_window import _schema_validate  # reuse the pinned validator

    results = []
    for offset in range(days):
        local_date = (datetime.fromisoformat(start_date) + timedelta(days=offset)).date().isoformat()
        request_id = f"{PILOT_ID}:{local_date}"
        result = compute_solar_window({
            "schema_version": "0.1.0",
            "request_id": request_id,
            "local_date": local_date,
            "time_zone": TZ_NAME,
            "observer": dict(OBSERVER),
            "model": dict(MODEL),
        }, computed_at=computed_at)
        _schema_validate(result, RESULT_SCHEMA)
        if result["capability"] != "WINDOW" or result["recommendation_eligible"] is not False \
                or result["photography_verdict"] != "NOT_EVALUABLE":
            raise ValueError("solar WINDOW result left the frozen research-only contract")
        if result["request_id"] != request_id or result["local_date"] != local_date:
            raise ValueError("solar WINDOW result identity mismatch")
        results.append(result)
    return {
        "pilot_id": PILOT_ID,
        "place_id": PLACE_ID,
        "schema_version": "0.1.0",
        "time_zone": TZ_NAME,
        "window_days": [r["local_date"] for r in results],
        "observer": OBSERVER,
        "model": MODEL,
        "results": results,
        "generation": {
            "generated_at_utc": computed_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
            "generator_version": GENERATOR_VERSION,
            "tzdb_version": tzdb_version,
            "source": "deterministic local computation (no network, no provider data)",
        },
        "data_state": "RAW_ONLY",
        "calibration_status": "UNVALIDATED",
        "availability": "COMPLETE",
        "recommendation_eligible": False,
        "photography_verdict": "NOT_EVALUABLE",
        "limitations_i18n": LIMITATIONS_I18N,
        "attribution_i18n": ATTRIBUTION_I18N,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-date", required=True, help="first local_date (YYYY-MM-DD)")
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--computed-at", help="UTC instant recorded as computed_at_utc (default: now)")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    computed_at = (datetime.fromisoformat(args.computed_at) if args.computed_at
                   else datetime.now(timezone.utc))
    try:
        import importlib.metadata
        tzdb = importlib.metadata.version("tzdata")
    except Exception:
        tzdb = None
    artifact = build(args.start_date, args.days, computed_at, tzdb)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out} ({len(artifact['results'])} days)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
