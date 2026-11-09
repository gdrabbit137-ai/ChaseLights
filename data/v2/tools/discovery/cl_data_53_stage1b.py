#!/usr/bin/env python3
"""CL-DATA-53 stage 1b: backfill the 22 missing legacy runtime spots (us-097..118,
CL-DATA-42/43 admissions that never reached runtime_catalog_v004_r4_2.json) and add
curation names/classifications for the 40 new places (us-119..us-158)."""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location(
    'cl53b', str(ROOT / 'data/v2/tools/discovery/cl_data_53_build.py'))
m53 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m53)
cl = m53.cl
m52 = m53.m52
wb = m53.wb
TICKET = "CL-DATA-53"

def main():
    import types as _types
    _stub = _types.ModuleType("opportunities_stub")
    _stub.get_opportunities = lambda *a, **k: []
    _stub.merge_legacy_themes = lambda *a, **k: []
    sys.modules.setdefault("opportunities", _stub)
    import regions as R
    # 1) legacy place dicts for us-097..118 from regions.py + V2 contracts
    spots = R.get_spots("us")
    by_id = {s["spot_id"]: s for s in spots}
    legacy_theme_reverse = {}
    for k, (legacy, _status) in cl.LEGACY_MAP.items():
        legacy_theme_reverse.setdefault(legacy, k)
    cat_path = ROOT / "runtime_catalog_v004_r4_2.json"
    cat = json.loads(cat_path.read_bytes().decode("utf-8"))
    have_ids = {s["spot_id"] for s in cat["spots"]}
    max_var = 0
    for s in cat["spots"]:
        for o in s["opportunities"]:
            for v in o.get("condition_variants", []):
                max_var = max(max_var, int(str(v["variant_id"]).split("-")[1]))
    var_id = max_var + 1
    built = {}
    for n in range(97, 119):
        pid = f"us-{n:03d}"
        if pid in have_ids:
            continue
        s = by_id[pid]
        opps = sorted((ROOT / "data/v2/opportunities").glob(f"{pid}-P*.json"))
        assert opps, f"{pid}: no V2 contracts found"
        subjects = []
        for cpath in opps:
            c = json.loads(cpath.read_bytes().decode("utf-8"))
            tpl = c["condition_contract"]["genre_template"]
            if tpl == "sunrise_marine":
                tpl = "sunrise"
            ni = c["name_i18n"]; di = c["description_i18n"]
            subjects.append(dict(suffix=c["opportunity_id"].split("-P")[1],
                                 template=tpl, seasonal=None,
                                 zh=ni["zh-TW"], en=ni["en"], ja=ni["ja"],
                                 desc_zh=di["zh-TW"], desc_en=di["en"], desc_ja=di["ja"]))
        p = dict(place_id=pid, region="us",
                 slug=f"legacy-{pid}",
                 names={"zh-TW": s["name_i18n"]["zh-TW"], "en": s["name_i18n"]["en"],
                        "ja": s["name_i18n"]["ja"], "local": s["name_i18n"]["local"] if "local" in s["name_i18n"] else s["name_i18n"]["en"]},
                 lat=s["lat"], lon=s["lon"], elev_m=None, coord_conf="high",
                 coord_source=f"regions.py spot tuple ({pid})", coord_sources=["https://github.com/"],
                 admin="", category=s["category"], tags=s["tags"], subjects=subjects)
        spot, _ = cl.build_legacy_spot(p, var_id)
        var_id += len(spot["opportunities"])
        built[pid] = spot
    for p in m53.PLACES:
        if p["place_id"] in have_ids:
            continue
        spot, _ = cl.build_legacy_spot(p, var_id)
        var_id += len(spot["opportunities"])
        built[p["place_id"]] = spot
    # insert maintaining us id order
    us_new = sorted(built.keys())
    for pid in us_new:
        cat["spots"].append(built[pid])
    cat["spots"].sort(key=lambda s: (s["spot_id"].split("-")[0], int(s["spot_id"].split("-")[1])))
    cat["counts"] = {
        "spots": len({s["spot_id"] for s in cat["spots"]}),
        "opportunities": sum(len(s["opportunities"]) for s in cat["spots"]),
        "condition_variants": sum(sum(len(o.get("condition_variants", [])) for o in s["opportunities"]) for s in cat["spots"]),
        "profile_viewpoint_relations": sum(sum(len(o.get("viewpoints", [])) for o in s["opportunities"]) for s in cat["spots"]),
    }
    wb(cat_path, cl.jdump(cat))
    print("runtime catalog counts:", cat["counts"])

    # 2) manifest recompute (us end stays 158)
    mf_path = ROOT / "runtime_catalog_manifest_r4_2.json"
    mf = json.loads(mf_path.read_bytes().decode("utf-8"))
    us_spots = [s for s in cat["spots"] if s["spot_id"].startswith("us-")]
    us_opps = [o for s in us_spots for o in s["opportunities"]]
    mf["regions"]["us"]["numeric_id_end"] = 158
    mf["regions"]["us"]["counts"] = {
        "spots": len(us_spots), "opportunities": len(us_opps),
        "condition_variants": sum(len(o.get("condition_variants", [])) for o in us_opps),
        "profile_viewpoint_relations": sum(len(o.get("viewpoints", [])) for o in us_opps)}
    mf["totals"] = dict(cat["counts"])
    wb(mf_path, cl.jdump(mf))  # write totals FIRST so the adapter import validates
    sys.modules.pop("opportunities", None)
    import opportunities as _O
    from collections import Counter as _C
    pol = _C()
    for s in cat["spots"]:
        for o in s["opportunities"]:
            pol[_O.runtime_policy(o)] += 1
    mf = json.loads(mf_path.read_bytes().decode("utf-8"))
    mf["runtime_policy_counts"] = dict(pol)
    wb(mf_path, cl.jdump(mf))
    print("manifest us counts:", mf["regions"]["us"]["counts"])

    # 3) curation.json: names + classifications for us-119..us-158
    cur_path = ROOT / "data/v2/indexes/research/curation.json"
    cur = json.loads(cur_path.read_bytes().decode("utf-8"))
    PLACES = m53.PLACES
    topic_for = {"mountain_view": "topic:mountain-landscape", "overlook": "topic:mountain-landscape",
                 "sunrise": "topic:sunrise", "sunset": "topic:sunset", "reflection": "topic:reflection"}
    added_names = added_cls = 0
    for p in PLACES:
        pid = p["place_id"]
        if pid not in cur["names"]:
            first_opp = f"{pid}-{p['subjects'][0]['suffix']}"
            cur["names"][pid] = {
                lang: {"direct_source": True, "source_path": "us_weather.json",
                       "spot_id": pid, "pointer": f"/name_i18n/{lang}"}
                for lang in ("zh-TW", "en", "ja")}
            added_names += 1
        for subj in p["subjects"]:
            oid = f"{pid}-{subj['suffix']}"
            if oid in cur["classifications"]:
                continue
            legacy_theme = cl.LEGACY_MAP[subj["template"]][0]
            cur["classifications"][oid] = {
                "topic_ids": ([topic_for[subj["template"]]] if subj["template"] in topic_for else []),
                "canonical_pointers": ["/targets/0/name_i18n", "/description_i18n"],
                "evidence_claim_id": f"{oid}-claim-01",
                "evidence_refs": [f"e-d53-web-{p['slug']}"],
                "classification_basis": f"legacy_theme={legacy_theme} ({TICKET} admission)"}
            added_cls += 1
    wb(cur_path, cl.jdump(cur))
    print("curation names +%d, classifications +%d (totals %d/%d)" % (
        added_names, added_cls, len(cur["names"]), len(cur["classifications"])))

if __name__ == "__main__":
    main()
