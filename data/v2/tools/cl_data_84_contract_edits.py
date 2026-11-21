"""CL-DATA-84: contract threshold fixes (owner ticket 2026-11-22, functional batch).

Idempotent editor for the owner-listed contract gaps:
  1. jp-010-P01  + aod_550nm REQUIRED <= 0.6          (light_window already present)
  2. jp-010-P02  + visibility REQUIRED >= 15 km, + cloud_cover_low REQUIRED <= 30
  3. jp-023-P01  + visibility REQUIRED >= 15 km, + aod_550nm REQUIRED <= 0.6
                 + seasonal-calendar entries (sakura / momiji windows)
  4. jp-016-P02  + water_reflection_state REQUIRED (harbour water-light subject)
  5. every night_sky contract + precipitation REQUIRED < 0.2 mm/h
  6. jp-022-P03  + seasonal_state REQUIRED + calendar entry (Yahiko night cruise);
                 galactic_core_altitude stays QUALITY (already downgraded)
  7. sunset template: visibility REQUIRED >= 15 km where missing
  8. sunrise template: visibility REQUIRED >= 15 km where missing
  9. tw-074-P01  + landform_present REQUIRED + aod_550nm REQUIRED <= 0.4,
                 - cloud_cover_low / cloud_cover_mid_and_high (owner: misplaced)
 10. tw-074-P02  light_window already REQUIRED (no-op, verified)
 11. jp-026-P01 / tw-066-P01 reclassified geological_landform -> golden_hour
     with the golden_hour canonical condition set.

Both the legacy `conditions` list and the QUALITY-engine `conditions_v2` block
are updated so the two views never diverge. Windows metrics (light_window,
seasonal_state, *_window) live only in the legacy list — the v2 gatekeeper
reads them from `windows`.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OPP = ROOT / "data" / "v2" / "opportunities"
CAL = ROOT / "data" / "v2" / "seasonal-calendar.json"

NOTE = {
    "zh-TW": "2026-11-22 owner 票（攝影條件複核）補齊/修正；provisional，未校準。",
    "en": "Added/corrected by the 2026-11-22 owner ticket (condition re-audit); provisional, uncalibrated.",
    "ja": "2026-11-22 オーナーチケット（撮影条件再監査）による追加・修正。暫定・未校正。",
}


def load(oid):
    p = OPP / f"{oid}.json"
    return json.loads(p.read_text(encoding="utf-8")), p


def dump(doc, path):
    """Rewrite preserving the file's own formatting (the repo mixes
    CRLF/indent=1 opportunity files with LF/indent=2 calendar files)."""
    raw = path.read_bytes() if path.exists() else b""
    nl = "\r\n" if b"\r\n" in raw[:200] else "\n"
    indent = 1
    lines = raw.split(nl.encode())[:3]
    if len(lines) > 1:
        lead = len(lines[1]) - len(lines[1].lstrip(b" "))
        indent = lead if lead in (1, 2, 4) else 1
    text = json.dumps(doc, ensure_ascii=False, indent=indent)
    if raw.endswith(nl.encode()):
        text += "\n"
    path.write_bytes(text.replace("\n", nl).encode("utf-8"))


def cond(oid, doc, metric):
    for c in doc["condition_contract"]["conditions"]:
        if c.get("metric") == metric:
            return c
    return None


def v2(doc):
    return doc["condition_contract"].setdefault("conditions_v2", {"required": [], "quality": []})


def next_id(doc, suffix):
    oid = doc["opportunity_id"]
    used = {c["id"] for c in doc["condition_contract"]["conditions"]}
    used |= {c["id"] for c in v2(doc)["required"]}
    used |= {c["id"] for c in v2(doc)["quality"]}
    cand = f"C-{oid}-{suffix}"
    i = 1
    while cand in used:
        i += 1
        cand = f"C-{oid}-{suffix}{i}"
    return cand


def add_legacy(doc, donor, suffix, claim_refs, rationale):
    oid = doc["opportunity_id"]
    c = copy.deepcopy(donor)
    c["id"] = next_id(doc, suffix)
    c["claim_refs"] = claim_refs
    c["validation_status"] = "provisional"
    c["calibration_status"] = "provisional"
    c["rationale_i18n"] = rationale
    c["notes_i18n"] = dict(NOTE)
    doc["condition_contract"]["conditions"].append(c)
    return c


def add_v2(doc, metric, op, value, suffix=None, claim_id=None):
    oid = doc["opportunity_id"]
    entry = {"id": next_id(doc, suffix or "X"), "metric": metric, "op": op,
             "value": value}
    v2(doc)["required"].append(entry)
    return entry


def claims(doc):
    return [c.get("claim_id") for c in doc.get("evidence_claims", [])] or [None]


RATIONALE = {
    "visibility": {
        "zh-TW": "能見度門檻（與 sunrise 基準一致）：海霧／平流霧或沿海霾時遠景糊成一片，光有雲量與無雨仍會誤推。",
        "en": "Visibility gate aligned with the sunrise baseline: sea fog / advection fog or coastal haze blurs the far view even when cloud cover and rain look benign.",
        "ja": "視程の門檻（sunrise 基準と同一）。海霧・移流霧・沿岸の霞で遠景が潰れるため、雲量と無雨だけでは誤推になる。",
    },
    "aod": {
        "zh-TW": "氣溶膠光學厚度 ≤0.6：霾害重時空氣中的散射會吃掉遠景對比（與同地點 jp-010-P02 一致）。",
        "en": "AOD <= 0.6: heavy haze scatters away far-field contrast (matches jp-010-P02 at the same place).",
        "ja": "AOD≤0.6。強い霞は遠景のコントラストを失わせる（同一地点 jp-010-P02 と整合）。",
    },
    "cloud_low": {
        "zh-TW": "低雲量 ≤30%：低雲牆會直接遮住山體／遠景，這是「無風好天」之外的必要閘門。",
        "en": "Low cloud <= 30%: a low deck physically hides the mountain / far view — a necessary gate beyond calm winds.",
        "ja": "下層雲量≤30%。下層雲が山体・遠景を隠すため、無風好天だけでは不十分。",
    },
    "precip_night": {
        "zh-TW": "降水 <0.2 mm/h：網格低雲量再低，局地陣雨也會毀掉整段星空；星空題材一律加硬門檻。",
        "en": "Precipitation < 0.2 mm/h: even with a low grid cloud cover, a local shower ruins the whole star session.",
        "ja": "降水<0.2mm/h。グリッド雲量が低くても局地のにわか雨で星空は成立しない。",
    },
    "water_state": {
        "zh-TW": "水面狀態（鏡面／可拍／不可拍）：港口夜景靠水面倒影成景，水面被風擾亂或水質混濁時應剔除。",
        "en": "Water-surface state (mirror / shootable / unfit): the harbour night scene lives on the water reflection; a wind-ruffled or turbid surface must be excluded.",
        "ja": "水面状態（鏡面／撮影可／不可）。港湾夜景は水面反射が主役で、風波や濁りは除外すべき。",
    },
    "landform": {
        "zh-TW": "地景存在性（地形紋理可辨）：地質地景題材的核心，缺失時整段判定無意義。",
        "en": "Landform presence (readable geological texture): the core of a geological-landform subject.",
        "ja": "地形の存在（地質テクスチャの判読可否）。地質地形題材の中核。",
    },
}

# donor condition objects (cloned for schema fidelity). Donors are read from git
# HEAD so a re-run after the edits landed still finds them (idempotency).
import subprocess


def load_head(oid):
    raw = subprocess.run(["git", "show", f"HEAD:data/v2/opportunities/{oid}.json"],
                         cwd=str(ROOT), capture_output=True, check=True).stdout
    return json.loads(raw.decode("utf-8"))


D_VIS = load_head("tw-076-P01")
D_LOW = load_head("jp-010-P01")
D_WS = load_head("jp-010-P02")
D_LF = load_head("jp-026-P01")
D_GH = load_head("jp-015-P02")

DONOR = {
    "visibility": cond("tw-076-P01", D_VIS, "visibility"),
    "aod": cond("tw-076-P01", D_VIS, "aod_550nm"),
    "cloud_low": cond("jp-010-P01", D_LOW, "cloud_cover_low"),
    "precip": cond("jp-010-P01", D_LOW, "precipitation"),
    "water_state": cond("jp-010-P02", D_WS, "water_reflection_state"),
    "landform": cond("jp-026-P01", D_LF, "landform_present"),
}


def ensure_condition(oid, key, suffix):
    """Add a legacy REQUIRED condition + its v2 twin if absent."""
    doc, path = load(oid)
    metric = DONOR[key]["metric"]
    if cond(oid, doc, metric) is None:
        add_legacy(doc, DONOR[key], suffix, claims(doc), RATIONALE[key])
        op = "derived_state" if key in ("water_state", "landform") else DONOR[key]["operator"]
        val = None if op == "derived_state" else DONOR[key]["threshold"]
        add_v2(doc, metric, op, val, suffix=suffix[:2])
        dump(doc, path)
        return f"{oid}: +{metric} REQUIRED"
    # exists in legacy -> make sure v2 mirrors it
    entry = cond(oid, doc, metric)
    twin = [c for c in v2(doc)["required"] if c.get("metric") == metric]
    if not twin:
        op = "derived_state" if entry.get("operator") in ("none", None) else entry["operator"]
        val = None if op == "derived_state" else entry.get("threshold")
        v2(doc)["required"].append({"id": entry["id"], "metric": metric,
                                    "op": op, "value": val})
        dump(doc, path)
        return f"{oid}: {metric} already legacy, mirrored into conditions_v2"
    return f"{oid}: {metric} already present (no-op)"


def main():
    report = []
    # 1. jp-010-P01 aod
    report.append(ensure_condition("jp-010-P01", "aod", "A1"))
    # 2. jp-010-P02 visibility + low cloud
    report.append(ensure_condition("jp-010-P02", "visibility", "V1"))
    report.append(ensure_condition("jp-010-P02", "cloud_low", "CL1"))
    # 3. jp-023-P01 visibility + aod
    report.append(ensure_condition("jp-023-P01", "visibility", "V1"))
    report.append(ensure_condition("jp-023-P01", "aod", "A1"))
    # 4. jp-016-P02 water state
    report.append(ensure_condition("jp-016-P02", "water_state", "WS1"))

    # 5. all night_sky contracts get precipitation REQUIRED < 0.2
    for p in sorted(OPP.glob("*.json")):
        doc = json.loads(p.read_text(encoding="utf-8"))
        if doc.get("condition_contract", {}).get("genre_template") != "night_sky":
            continue
        oid = doc["opportunity_id"]
        if cond(oid, doc, "precipitation") is None:
            add_legacy(doc, DONOR["precip"], "P1", claims(doc), RATIONALE["precip_night"])
            add_v2(doc, "precipitation", "lt", 0.2, suffix="P1")
            dump(doc, p)
            report.append(f"{oid}: +precipitation REQUIRED <0.2 (night_sky)")
        else:
            report.append(f"{oid}: precipitation already present (no-op)")

    # 6. jp-022-P03 seasonal window (night cruise) + keep galactic_core QUALITY
    doc, path = load("jp-022-P03")
    cc = doc["condition_contract"]
    if cond("jp-022-P03", doc, "seasonal_state") is None:
        seasonal_donor = cond("jp-021-P02", load("jp-021-P02")[0], "seasonal_state")
        add_legacy(doc, seasonal_donor, "OP1", claims(doc), {
            "zh-TW": "夜景＆星空クルーズ限定夜間營運季節：非營運期間纜車不開，夜空再好也上不去。",
            "en": "Night-cruise operating season: outside it the ropeway does not run at night, so the best sky is unreachable.",
            "ja": "夜景＆星空クルーズの夜間運行シーズン。期間外はロープウェイが動かず、星空が良くても行けない。",
        })
        cc.setdefault("windows", {})["seasonal"] = "calendar"
        dump(doc, path)
        report.append("jp-022-P03: +seasonal_state REQUIRED (calendar) ")
    else:
        report.append("jp-022-P03: seasonal_state already present (no-op)")
    if cond("jp-022-P03", doc, "galactic_core_altitude"):
        rep = cond("jp-022-P03", doc, "galactic_core_altitude")
        report.append(f"jp-022-P03: galactic_core_altitude role={rep['role']} (owner asked remove/downgrade)")

    # 7/8. sunset + sunrise visibility alignment
    sunsets = ["jp-013-P01", "jp-019-P01", "jp-022-P02", "tw-064-P01",
               "tw-065-P01", "tw-067-P01", "tw-070-P01", "tw-071-P02"]
    sunrises = ["tw-069-P01", "tw-071-P01", "tw-073-P01", "tw-077-P01"]
    for oid in sunsets + sunrises:
        report.append(ensure_condition(oid, "visibility", "V1"))

    # 9. tw-074-P01 restore landform + aod, drop misplaced cloud gates
    doc, path = load("tw-074-P01")
    cc = doc["condition_contract"]
    before = len(cc["conditions"])
    cc["conditions"] = [c for c in cc["conditions"]
                        if c.get("metric") not in ("cloud_cover_low", "cloud_cover_mid_and_high")]
    cc["conditions_v2"]["required"] = [c for c in cc["conditions_v2"]["required"]
                                       if c.get("metric") != "cloud_cover_low"]
    cc["conditions_v2"]["quality"] = [c for c in cc["conditions_v2"]["quality"]
                                      if c.get("metric") != "cloud_cover_mid_and_high"]
    removed = before - len(cc["conditions"])
    dump(doc, path)
    report.append(f"tw-074-P01: removed {removed} misplaced cloud gate(s)")
    report.append(ensure_condition("tw-074-P01", "landform", "LF1"))
    report.append(ensure_condition("tw-074-P01", "aod", "A1"))

    # 10. tw-074-P02 light_window role check
    doc2, _ = load("tw-074-P02")
    lw = cond("tw-074-P02", doc2, "light_window")
    report.append(f"tw-074-P02: light_window role={lw['role'] if lw else 'MISSING'}")

    # 11. reclassify jp-026-P01 / tw-066-P01 -> golden_hour canonical set
    gh_src = load("jp-015-P02")[0]
    for oid in ["jp-026-P01", "tw-066-P01"]:
        doc, path = load(oid)
        cc = doc["condition_contract"]
        if cc.get("genre_template") == "golden_hour":
            report.append(f"{oid}: already golden_hour (no-op)")
            continue
        cc["genre_template"] = "golden_hour"
        cc["template_version"] = gh_src["condition_contract"].get("template_version", "golden_hour-v0.1")
        new_conditions = []
        for src in gh_src["condition_contract"]["conditions"]:
            c = copy.deepcopy(src)
            c["id"] = f"C-{oid}-GH{len(new_conditions) + 1}"
            c["claim_refs"] = claims(doc)
            c["notes_i18n"] = {
                "zh-TW": "2026-11-22 owner 裁決：人文建築（社殿／燈塔）由 geological_landform 改歸 golden_hour 光影模板，條件沿用 golden_hour 標準組。",
                "en": "Owner ruling 2026-11-22: heritage architecture (shrine hall / lighthouse) reclassified from geological_landform to the golden_hour light template, using the canonical golden_hour condition set.",
                "ja": "2026-11-22 オーナー裁定：人文建築（社殿・灯台）を geological_landform から golden_hour へ再分類し、golden_hour 標準条件を適用。",
            }
            new_conditions.append(c)
        cc["conditions"] = new_conditions
        v2src = gh_src["condition_contract"].get("conditions_v2") or {}
        cc["conditions_v2"] = {
            "required": [dict(c, id=f"C-{oid}-GHV{len(cc.get('conditions_v2', {}).get('required', [])) + i + 1}")
                         for i, c in enumerate(copy.deepcopy(v2src.get("required", [])))],
            "quality": [dict(c, id=f"C-{oid}-GHQ{i + 1}")
                        for i, c in enumerate(copy.deepcopy(v2src.get("quality", [])))],
        }
        dump(doc, path)
        report.append(f"{oid}: geological_landform -> golden_hour (canonical set)")

    # calendar entries
    cal = json.loads(CAL.read_text(encoding="utf-8"))
    entries = cal["entries"]

    def upsert(plant_id, payload):
        for i, e in enumerate(entries):
            if e.get("plant_id") == plant_id:
                entries[i] = payload
                return "updated"
        entries.append(payload)
        return "added"

    actions = []
    actions.append(("sakura_kiyomizu", upsert("sakura_kiyomizu", {
        "plant_id": "sakura_kiyomizu",
        "spots": ["jp-023-P01"],
        "name_i18n": {"zh-TW": "清水寺周邊櫻花（例年）", "en": "Cherry blossom at Kiyomizu-dera (typical)", "ja": "清水寺周辺の桜（例年）"},
        "typical_window": {"start": "03-25", "end": "04-10"},
        "sources": [{"url": "https://www.weathernews.jp/sakura/", "kind": "live_report",
                     "note_i18n": {"zh-TW": "ウェザーニュース桜開花リポート（京都例年窗）", "en": "Weathernews sakura reports (Kyoto typical window)", "ja": "ウェザーニュース桜開花リポート（京都不例年窓）"}}],
    })))
    actions.append(("momiji_kiyomizu", upsert("momiji_kiyomizu", {
        "plant_id": "momiji_kiyomizu",
        "spots": ["jp-023-P01"],
        "name_i18n": {"zh-TW": "清水寺周邊紅葉（例年）", "en": "Autumn foliage at Kiyomizu-dera (typical)", "ja": "清水寺周辺の紅葉（例年）"},
        "typical_window": {"start": "11-15", "end": "12-07"},
        "sources": [{"url": "https://www.weathernews.jp/koyo/", "kind": "live_report",
                     "note_i18n": {"zh-TW": "ウェザーニュース紅葉リポート（京都例年窗）", "en": "Weathernews koyo reports (Kyoto typical window)", "ja": "ウェザーニュース紅葉リポート（京都不例年窓）"}}],
    })))
    actions.append(("yahiko_night_cruise", upsert("yahiko_night_cruise", {
        "plant_id": "yahiko_night_cruise",
        "spots": ["jp-022-P03"],
        "name_i18n": {"zh-TW": "弥彦山夜景＆星空クルーズ（期間限定夜間運行）", "en": "Yahikosan night-view & star cruise (limited night operation)", "ja": "弥彦山夜景＆星空クルーズ（期間限定夜間運行）"},
        "typical_window": {"start": "08-11", "end": "09-23"},
        "sources": [{"url": "https://www.e-yahiko.com/2026yama/", "kind": "official",
                     "note_i18n": {"zh-TW": "弥彦観光協会 2026：8/11、12、14、15、16；9/19–23 夜間特別運行（上り 18:00–20:30／下り終発 21:00）。本窗為營運季粗窗超集。", "en": "Yahiko Tourist Association 2026: Aug 11, 12, 14, 15, 16 and Sep 19-23 special night operation (up 18:00-20:30, last down 21:00). This is the operating-season superset window.", "ja": "弥彦観光協会2026：8/11・12・14・15・16、9/19〜23 夜間特別運行（上り18:00–20:30／下り終発21:00）。本窓は運行シーズンの粗い上位集合。"}}],
    })))
    dump(cal, CAL)
    report += [f"calendar {pid}: {act}" for pid, act in actions]

    print("\n".join(report))


if __name__ == "__main__":
    main()
