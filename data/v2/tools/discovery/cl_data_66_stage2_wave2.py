#!/usr/bin/env python3
"""CL-DATA-66 wave-2 stage 2: curation names/classifications for the 15 new
places + 22 contracts. SCORELESS (owner ruling 2026-11-11): AGLI dual-board
block deliberately NOT executed — agli-final.json untouched."""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location(
    'cl66w2', str(ROOT / 'data/v2/tools/discovery/cl_data_66_build_wave2.py'))
m2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m2)
TICKET = "CL-DATA-66"
PLACES = m2.PLACES
cl = m2.cl

TOPIC_FOR = {
    "cloud_sea": "topic:mountain-landscape", "sunrise": "topic:sunrise", "sunset": "topic:sunset",
    "city_night": "topic:cityscape", "night_sky": "topic:cityscape",
    "geological_landform": "topic:mountain-landscape", "mountain_view": "topic:mountain-landscape",
    "overlook": "topic:mountain-landscape", "seasonal_plant": "topic:flowers",
    "reflection": "topic:reflection", "waterfall": "topic:mountain-landscape",
}


def wcur(p, obj):
    (ROOT / p).write_bytes((json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def main():
    import json
    cur_path = ROOT / "data/v2/indexes/research/curation.json"
    cur = json.loads(cur_path.read_bytes().decode("utf-8"))
    added_names = added_cls = 0
    for p in PLACES:
        pid = p["place_id"]
        if pid not in cur["names"]:
            cur["names"][pid] = {
                lang: {"direct_source": True, "source_path": "tw_weather.json",
                       "spot_id": pid, "pointer": f"/name_i18n/{lang}"}
                for lang in ("zh-TW", "en", "ja")}
            added_names += 1
        for subj in p["subjects"]:
            oid = f"{pid}-{subj['suffix']}"
            if oid in cur["classifications"]:
                continue
            legacy_theme = cl.LEGACY_MAP[subj["template"]][0]
            cur["classifications"][oid] = {
                "topic_ids": ([t] if (t := TOPIC_FOR.get(subj["template"])) else []),
                "canonical_pointers": ["/targets/0/name_i18n", "/description_i18n"],
                "evidence_claim_id": f"{oid}-claim-01",
                "evidence_refs": [f"e-d66-web-{p['slug']}"],
                "classification_basis": f"legacy_theme={legacy_theme} ({TICKET} wave-2 scoreless admission)"}
            added_cls += 1
    wcur("data/v2/indexes/research/curation.json", cur)
    print("curation names +%d, classifications +%d (totals %d/%d)" % (
        added_names, added_cls, len(cur["names"]), len(cur["classifications"])))


if __name__ == "__main__":
    main()
