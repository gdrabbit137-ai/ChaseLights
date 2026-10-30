"""Build the V1-facing opportunity contract display bundle.

Owner directive 2026-10-31: V1 subjects are replaced by V2 — identity
(name_i18n), genre, conditions and rationale come from V2 canonical
contracts; V1 retains only its researched shooting-guide fields
(best_time / best_season / viewpoints). Output: apps/web-v2/opportunity-contracts.json
"""
import json
import glob
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "apps/web-v2/opportunity-contracts.json"

entries = {}
for path in sorted((ROOT / "data/v2/opportunities").glob("*.json")):
    d = json.loads(path.read_text(encoding="utf-8"))
    cc = d.get("condition_contract") or {}
    if not cc.get("genre_template"):
        continue
    conditions = []
    for c in cc.get("conditions", []):
        conditions.append({
            "id": c["id"],
            "metric": c["metric"],
            "role": c["role"],
            "condition_tier": c.get("condition_tier", "MAIN"),
            "operator": c["operator"],
            "threshold": c.get("threshold"),
            "unit": c.get("unit"),
            "rationale_i18n": c.get("rationale_i18n") or {},
        })
    entries[d["opportunity_id"]] = {
        "opportunity_id": d["opportunity_id"],
        "place_id": d["place_id"],
        "revision": d.get("revision"),
        "genre_template": cc["genre_template"],
        "contract_id": cc.get("contract_id"),
        "contract_status": cc.get("status"),
        "name_i18n": d.get("name_i18n") or {},
        "description_i18n": d.get("description_i18n") or {},
        "conditions": conditions,
    }

bundle = {
    "schema_version": "opportunity-contracts-v0.1",
    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "guidance_only": True,
    "count": len(entries),
    "opportunities": entries,
}
OUT.write_text(json.dumps(bundle, ensure_ascii=False, separators=(",", ":")) + "\n",
               encoding="utf-8")
print(json.dumps({"status": "OK", "path": str(OUT), "opportunities": len(entries),
                  "bytes": OUT.stat().st_size}))
