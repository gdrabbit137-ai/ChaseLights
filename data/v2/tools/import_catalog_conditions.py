#!/usr/bin/env python3
"""Import catalog_20261101_conditions.xlsx (manager-reviewed revision) into the
canonical data/v2/opportunities condition contracts (CL-DATA-01).

Source of truth for the FINAL state of every subject row is the xlsx
(基準 commit a770727d2 + manager 2026-11-01 revisions). The importer is
row-level diff-based against the current canonical contracts:

- 變更狀態=None rows: verify only; owner-fixed values that postdate the xlsx
  base snapshot (galactic core >=10 deg, inversion >=0.0 C, calm-wind lt 12.0,
  elevation-bound 700/600 hPa levels) win over stale xlsx copies (reported).
- 修正 rows: apply value/tier/role/rationale changes; rationale zh from the
  xlsx 口語, en/ja translated (2026-11-01 texts).
- 新增 rows: append conditions instantiated from the genre-template registry
  (data/v2/templates, 已審模板值) with per-subject thresholds from the xlsx;
  validation_status/calibration_status = provisional; notes_i18n carries the
  provenance marker "2026-11-01 manager 依既有已審模板訂立，未校準。"
- New condition contract status = draft; never defined/calibrated.
- Current conditions with no xlsx row: deleted (誤植移除, per manager).
- Genre rewrite (水面倒影重寫 / 日出錯配): genre_template + template_version
  updated to the target template.
- 雲海 LCL: recomputed per subject as actual viewpoint elevation (DEM, from
  the V1 weather JSON api_elevation/elevation fields) - 200 m; rationale text
  updated with the real elevation.
- 潮汐主導 subjects: keep the legacy placeholder contract (honest
  not_evaluatable; no weather contract fabricated) with the manager rationale.
- 活動/季節時程 非氣象 rows: represented as a REQUIRED seasonal_state window
  condition (no live source -> propagate unknown), plus the weather minimum
  thresholds. 光害/環境 rows: appended to the seasonal rationale (no vocab
  metric exists; no metric invented).

Usage:
  python data/v2/tools/import_catalog_conditions.py            # dry-run report
  python data/v2/tools/import_catalog_conditions.py --apply    # write files
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OPP_DIR = ROOT / "data/v2/opportunities"
TEMPLATES = ROOT / "data/v2/templates"
WEATHER_FILES = [ROOT / "tw_weather.json", ROOT / "jp_weather.json", ROOT / "us_weather.json"]
DEFAULT_XLSX = ROOT / "data/v2/staging/catalog_20261101_conditions.xlsx"

METRIC_ZH = {
    "相對濕度925hPa": "relative_humidity_925hpa",
    "相對濕度850hPa": "relative_humidity_850hpa",
    "相對濕度700hPa": "relative_humidity_700hpa",
    "相對濕度600hPa": "relative_humidity_600hpa",
    "抬升凝結高度": "lcl_height_m_agl",
    "低雲": "cloud_cover_low",
    "中雲": "cloud_cover_mid",
    "中高雲": "cloud_cover_mid_and_high",
    "總雲量": "cloud_cover_total",
    "氣膠光學厚度": "aod_550nm",
    "能見度": "visibility",
    "降水": "precipitation",
    "風速": "wind_speed_10m",
    "T850−T925溫差": "temperature_delta_850_925_c",
    "T850−T700溫差": "temperature_delta_850_700_c",
    "850hPa風速": "wind_speed_850hpa",
    "700hPa風速": "wind_speed_700hpa",
    "600hPa風速": "wind_speed_600hpa",
    "日出時段": "sunrise_time_window",
    "日落時段": "sunset_window",
    "藍調時段": "blue_hour_window",
    "黃金時段": "golden_hour_window",
    "天文黑暗": "astronomical_darkness",
    "月亮高度": "moon_altitude",
    "月亮照亮百分比": "moon_illumination_fraction",
    "月照亮百分比": "moon_illumination_fraction",
    "月目標角距": "moon_target_separation_deg",
    "月光照度代理": "moon_illuminance_proxy",
    "月亮照度代理": "moon_illuminance_proxy",
    "銀河核心高度": "galactic_core_altitude",
    "季節狀態": "seasonal_state",
    "水面狀態": "water_surface_state",
    "地形地貌存在": "landform_present",
}
GENRE_ZH = {
    "山景視野": "mountain_view",
    "制高點展望": "overlook",
    "城市夜景": "city_night",
    "城市藍調": "blue_hour_city",
    "夜空星空": "night_sky",
    "季節植物": "seasonal_plant",
    "日出": "sunrise",
    "日落夕景": "sunset",
    "水面倒影": "reflection",
    "雲海": "cloud_sea",
    "地質地景": "geological_landform",
    "地質地標": "geological_landform",
    "陰天柔光": "overcast_soft",
    "黃金時刻": "golden_hour",
}
# Elevation-bound alias classes (owner fix ea0f68b97: high-mountain cloud sea
# uses 700/600 hPa; the xlsx carries the generic 925/850 labels for these).
ELEV_ALIAS = {
    "relative_humidity_700hpa": "relative_humidity_925hpa",
    "relative_humidity_600hpa": "relative_humidity_850hpa",
    "temperature_delta_700_600_c": "temperature_delta_850_925_c",
    "wind_speed_700hpa": "wind_speed_850hpa",
    "wind_speed_600hpa": "wind_speed_850hpa",
}
ALIAS_TARGETS = set(ELEV_ALIAS.values())
NON_WEATHER_ROWS = {"潮汐（主導條件）", "活動/季節時程", "光害/環境"}
# Stale xlsx copies of owner fixes that postdate the xlsx base snapshot
# (ea0f68b97, 2026-10-31): current canonical value wins, no edit, reported.
STALE_XLSX = {
    ("galactic_core_altitude", "gte", 20.0): ("gte", 10),
    ("temperature_delta_850_925_c", "gte", 2.0): ("gte", 0.0),
    ("temperature_delta_700_600_c", "gte", 2.0): ("gte", 0.0),
    ("wind_speed_850hpa", "gte", 12.0): ("lt", 12.0),
    ("wind_speed_600hpa", "gte", 12.0): ("lt", 12.0),
}
TIDAL_GENRE = "潮汐主導"
# worker2_batch03/04 human-review crosswalk gates pin these subjects' bespoke
# research-only contracts (exact condition shapes, notes texts, 30-row crosswalk
# byte comparisons). Their xlsx rows conflict with that human-review evidence;
# deferred to owner instead of overwriting review artifacts (CL-DATA-01).
REVIEW_GATED_SUBJECTS = {
    "tw-026-P01", "tw-026-P02",          # worker2_batch03 crosswalk gates
    "tw-082-P01", "tw-034-P02", "jp-010-P01", "us-071-P01",  # worker2_batch04
}

PROVENANCE_NOTE = {
    "zh-TW": "2026-11-01 manager 依既有已審模板訂立，未校準。",
    "en": "Established 2026-11-01 by the manager from already-reviewed template values; not calibrated.",
    "ja": "2026-11-01、マネージャーが承認済みテンプレート値に基づき設定。未校正。",
}

# Subject-specific manager texts (fog/firefly/activity) that differ from the
# registry wording; zh from the xlsx, en/ja translated (CL-DATA-01).
SUBJECT_TEXTS = {
    "低層近飽和為霧/薄霧生成的必要條件。provisional（氛圍題材）。": {
        "en": "Near-saturation low-level humidity is required for fog/mist to form. provisional (atmosphere subject).",
        "ja": "下層の飽和に近い湿度は霧・薄霧生成の必要条件。暫定（雰囲気題材）。",
    },
    "大雨破壞拍攝；毛毛雨/霧反而是主體。provisional。": {
        "en": "Heavy rain ruins the shot; drizzle/mist is the subject itself. provisional.",
        "ja": "大雨は撮影を壊す。霧雨や霧はむしろ主体。暫定。",
    },
    "螢火蟲季節窗（seasonal-calendar）。": {
        "en": "Firefly season window (seasonal-calendar).",
        "ja": "蛍の季節窓（seasonal-calendar）。",
    },
    "螢火蟲觀察需黑暗環境。": {
        "en": "Astronomical darkness: firefly observation needs a dark environment.",
        "ja": "天文の薄明窓：蛍の観察には暗い環境が必要。",
    },
    "雨天不見螢火。": {
        "en": "No fireflies in the rain.",
        "ja": "雨では蛍が見られない。",
    },
    "強風不利螢火觀察與長曝。": {
        "en": "Strong wind hurts firefly observation and long exposures.",
        "ja": "強風は蛍の観察と長時間露出に不利。",
    },
    "活動側最低門檻。": {
        "en": "Minimum weather threshold on the event side.",
        "ja": "イベント側の最低天気閾値。",
    },
    "煙火/燈海清晰度代理。": {
        "en": "Proxy for fireworks/sea-of-lights clarity.",
        "ja": "花火・灯の海の鮮明さの代理指標。",
    },
    "活動/燈光題材最低天氣門檻（沿用已審門檻）。": {
        "en": "Minimum weather threshold for event/lighting subjects (reviewed template value).",
        "ja": "イベント・ライト系題材の最低天気閾値（承認済み閾値を踏襲）。",
    },
}


TIDAL_NOTE = {
    "zh-TW": "主導條件為潮汐（分海／退潮石板道／石滬露出／漩渦規模），非天氣。系統現無潮汐資料源：誠實 not_evaluatable，不提供天氣契約以免誤導（2026-11-01 訂立，待潮汐資料源實作後再建契約）。",
    "en": "The governing condition is the tide (sandbar parting / exposed flagstone causeway / exposed stone weirs / whirlpool scale), not weather. The system has no tidal data source: honestly not_evaluatable, no weather contract is offered to avoid misleading (established 2026-11-01; contract to be built once a tidal source is implemented).",
    "ja": "支配的条件は潮汐（干潮で砂洲が分かれる／石板路の露出／石垣の露出／渦の規模）であり天気ではない。システムには潮汐データソースが現状ない：誠実に not_evaluatable とし、誤解を招かないよう天気契約は提供しない（2026-11-01 設定。潮汐ソース実装後に契約を構築）。",
}


def parse_cond(txt):
    """xlsx 數值化條件 text -> (operator, threshold) or sentinel."""
    if txt is None:
        return ("eq", "window_open")
    t = str(txt).strip()
    if t in ("None", ""):
        return ("eq", "window_open")
    if "宣告型" in t or t == "—":
        return ("none", None)
    if t.startswith("LCL"):
        return ("lcl", None)
    t2 = re.sub(r"\s+AOD$", "", t)
    m = re.match(r"^(≤|≥|<|>)\s*([\d.]+)\s*(%|km|m/s|mm/h|m|°C|°)?$", t2.replace(" ", ""))
    if m:
        op = {"≤": "lte", "≥": "gte", "<": "lt", ">": "gt"}[m.group(1)]
        return (op, _num(m.group(2)))
    m = re.match(r"^([\d.]+)[-–]([\d.]+)\s*(%|km|m/s|mm/h|m|°C|°)?$", t.replace("–", "-").replace(" ", ""))
    if m:
        return ("between", [_num(m.group(1)), _num(m.group(2))])
    raise ValueError(f"UNPARSED xlsx condition: {t!r}")


def _num(text):
    v = float(text)
    return int(v) if v.is_integer() else v


def parse_cond_multivalue(txt):
    """A metric label may repeat per subject (e.g. 濕度925 for two rows)."""
    return parse_cond(txt)


def unit_for(txt):
    t = str(txt or "")
    for suffix, unit in (("%", "%"), ("km", "km"), ("m/s", "m/s"),
                         ("mm/h", "mm/h"), ("°C", "°C"), ("°", "°")):
        if t.endswith(suffix):
            return unit
    if re.search(r"\d$", t) and ("m" in t):
        return "m"
    return None


def load_xlsx(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True)
    rows = []
    for name in ("台灣", "日本", "美國（含阿拉斯加）"):
        ws = wb[name]
        header = [c.value for c in ws[1]]
        for row in ws.iter_rows(min_row=2, values_only=True):
            d = dict(zip(header, row))
            rows.append(d)
    by_subject = defaultdict(list)
    for r in rows:
        by_subject[r["題材ID"]].append(r)
    return rows, by_subject


def load_elevations():
    """DEM viewpoint elevations from the V1 weather snapshots (Open-Meteo
    Elevation API values carried by the V1 pipeline)."""
    elev = {}
    for f in WEATHER_FILES:
        if not f.exists():
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        for spot in data.get("spots", []):
            value = spot.get("elevation") or spot.get("api_elevation")
            if value is not None:
                elev[spot["spot_id"]] = float(value)
    return elev


def load_registry():
    registry = {}
    for p in sorted(TEMPLATES.glob("*.json")):
        if p.name == "metric-vocabulary.json":
            continue
        t = json.loads(p.read_text(encoding="utf-8"))
        registry[t["template_id"]] = t
    return registry


def load_canonical():
    docs = {}
    for p in sorted(OPP_DIR.glob("*.json")):
        docs[p.name[:-5]] = json.loads(p.read_text(encoding="utf-8"))
    return docs


# ---------------------------------------------------------------- translations
T_CLOUD_TOTAL_BONUS = {
    "zh-TW": "總雲量 20–60%：雲與彩霞在鏡面裡的對稱構圖是倒影的加分主體；全晴只有山形、全陰無色彩。 【2026-11-01 審查修正】 由成立改加分：口語自述『加分主體』，與分類一致化。",
    "en": "Total cloud 20-60%: symmetric cloud/glow reflections in the mirror are the bonus core of a reflection shot; fully clear gives only the mountain silhouette, fully overcast gives no colour. [2026-11-01 review fix] Moved from gating to bonus: the wording itself calls it a bonus subject; the classification now matches.",
    "ja": "全雲量20〜60%：鏡面に映る雲と彩雲の対称構図は倒影の加点主体；快晴なら山影のみ、全曇なら色彩がない。【2026-11-01審査修正】成立条件から加点へ変更：口語自体が『加点主体』と述べており、分類を一致させた。",
}
T_AOD_BONUS_REWRITE = {
    "zh-TW": "山景層次由 AOD 承擔（遠山霧霾層次）。【2026-11-01 審查修正】 由成立改加分：主體為倒影，山景層次非否決條件。",
    "en": "Mountain-layer depth is carried by AOD (haze layering of distant ridges). [2026-11-01 review fix] Moved from gating to bonus: the subject is the reflection; mountain-layer depth is not a veto condition.",
    "ja": "山景の層次はAODが担う（遠山の靄による層）。【2026-11-01審査修正】成立条件から加点へ変更：主体は倒影であり、山景の層次は否決条件ではない。",
}
T_CLOUD_TOTAL_BONUS_REWRITE = {
    "zh-TW": "雲與彩霞在鏡面裡的對稱構圖是倒影的加分主體；全晴只有山形、全陰無色彩。（2026-11-01 審查：由成立條件改加分，與口語一致）",
    "en": "Symmetric cloud/glow reflections in the mirror are the bonus core of a reflection shot; fully clear gives only the mountain silhouette, fully overcast gives no colour. (2026-11-01 review: moved from gating to bonus, matching the wording.)",
    "ja": "鏡面に映る雲と彩雲の対称構図は倒影の加点主体；快晴なら山影のみ、全曇なら色彩がない。（2026-11-01審査：成立条件から加点へ変更、口語と一致）",
}
T_VIS_US010 = {
    "zh-TW": "能見度 ≥ min(眺望距離, 24 km)：遠景清晰度的直接代理。誠實標註：GFS/Open-Meteo 能見度欄位上限約 24 km，超過後此判據鈍化（報 24 km 不代表能看 100 km）——長距離眺望由 V2（AOD）承擔真實判別。【2026-11-01 審查修正】 俯瞰距離僅數百公尺，3 km 過嚴，依 min(眺望,24) 規則修正。",
    "en": "Visibility >= min(view range, 24 km): the direct proxy for distant-scene clarity. Honest caveat: the GFS/Open-Meteo visibility field caps near 24 km and the criterion dulls beyond that (a 24 km report does not mean 100 km sight) - long-range discrimination is carried by V2 AOD. [2026-11-01 review fix] The overlook distance is only a few hundred metres; 3 km was too strict, corrected per the min(view,24) rule.",
    "ja": "視程 >= min(眺望距離, 24 km)：遠景の鮮明さの直接代理。誠実な注記：GFS/Open-Meteoの視程欄は約24 kmが上限で、それを超えると判定は鈍化する（24 kmの報告は100 km見える意味ではない）——長距離の判別はV2のAODが担う。【2026-11-01審査修正】俯瞰距離は数百メートルしかなく、3 kmは厳しすぎたため、min(眺望,24)規則に従い修正。",
}


def lcl_rationale(alt_m, lcl_m, *, fix_note=True):
    alt = f"{alt_m:,.0f}".replace(",", ",")
    lcl = f"{lcl_m:,.0f}"
    if fix_note:
        return {
            "zh-TW": f"雲底須低於視線（觀點 {alt} m − 200 m ＝ {lcl} m 餘量），雲海才出現在眼前而非腳邊。LCL 為雲底代理。【2026-11-01 審查修正】 口語原誤寫『觀點 1,090 m』為模板複製錯誤；LCL 數值由 RD 以各點實際海拔（Open-Meteo Elevation API）− 200 m 重算確認。",
            "en": f"The cloud base must sit below the sightline (viewpoint {alt} m minus a 200 m margin = {lcl} m) for the sea of clouds to appear in front of the viewer, not at their feet. LCL proxies the cloud base. [2026-11-01 review fix] The wording previously said 'viewpoint 1,090 m' - a template copy-paste error; the LCL value was recomputed by RD as the actual elevation (Open-Meteo Elevation API) minus 200 m.",
            "ja": f"雲底が視線より低いこと（視点{alt}mから200mの余裕＝{lcl}m）で、雲海が足元ではなく眼前に現れる。LCLは雲底の代理指標。【2026-11-01審査修正】口語が『視点1,090m』と誤記（テンプレート複製ミス）。LCL値はRDが実際の標高（Open-Meteo Elevation API）から200mを引いて再計算・確認した。",
        }
    return {
        "zh-TW": f"雲底須低於視線（觀點 {alt} m − 200 m ＝ {lcl} m 餘量），雲海才出現在眼前而非腳邊。LCL 為雲底代理。（2026-11-01 審查：數值由 RD 以各點實際觀點海拔 −200 m 重算取代；原口語誤寫 1,090 m 為模板複製錯誤）",
        "en": f"The cloud base must sit below the sightline (viewpoint {alt} m minus a 200 m margin = {lcl} m) for the sea of clouds to appear in front of the viewer, not at their feet. LCL proxies the cloud base. (2026-11-01 review: the value was recomputed by RD as the actual viewpoint elevation minus 200 m; the wording previously carried the copy-pasted 1,090 m.)",
        "ja": f"雲底が視線より低いこと（視点{alt}mから200mの余裕＝{lcl}m）で、雲海が足元ではなく眼前に現れる。LCLは雲底の代理指標。（2026-11-01審査：値はRDが実際の視点標高から200mを引いて再計算；元の口語は1,090mと誤記＝テンプレート複製ミス）",
    }


DOMAIN_BY_METRIC = {
    "relative_humidity_925hpa": "WEATHER", "relative_humidity_850hpa": "WEATHER",
    "relative_humidity_700hpa": "WEATHER", "relative_humidity_600hpa": "WEATHER",
    "lcl_height_m_agl": "WEATHER", "cloud_cover_low": "WEATHER",
    "cloud_cover_mid": "WEATHER", "cloud_cover_mid_and_high": "WEATHER",
    "cloud_cover_total": "WEATHER", "visibility": "WEATHER",
    "aod_550nm": "WEATHER", "precipitation": "WEATHER",
    "temperature_delta_850_925_c": "WEATHER", "temperature_delta_850_700_c": "WEATHER",
    "temperature_delta_700_600_c": "WEATHER",
    "wind_speed_10m": "WEATHER", "wind_speed_850hpa": "WEATHER",
    "wind_speed_700hpa": "WEATHER", "wind_speed_600hpa": "WEATHER",
    "sunrise_time_window": "ASTRONOMY", "sunset_window": "ASTRONOMY",
    "blue_hour_window": "ASTRONOMY", "golden_hour_window": "ASTRONOMY",
    "astronomical_darkness": "ASTRONOMY", "moon_altitude": "ASTRONOMY",
    "moon_illumination_fraction": "ASTRONOMY",
    "moon_target_separation_deg": "ASTRONOMY", "moon_illuminance_proxy": "ASTRONOMY",
    "galactic_core_altitude": "ASTRONOMY",
    "seasonal_state": "SEASON_TIME", "water_surface_state": "HYDROLOGY",
    "landform_present": "SUBJECT_STATE",
}


def exemplar_condition(metric, docs, genre=None):
    """Existing canonical condition with the same metric (same genre first)."""
    same_genre = None
    for doc in docs.values():
        cc = doc.get("condition_contract") or {}
        if cc.get("genre_template") != genre:
            continue
        for c in cc.get("conditions") or []:
            if c["metric"] == metric:
                return c
    for doc in docs.values():
        cc = doc.get("condition_contract") or {}
        for c in cc.get("conditions") or []:
            if c["metric"] == metric:
                return c
    return same_genre


def registry_row(registry, template_id, metric):
    t = registry.get(template_id) or {}
    for c in t.get("conditions") or []:
        if c["metric"] == metric:
            return c
    for t in registry.values():
        for c in t.get("conditions") or []:
            if c["metric"] == metric:
                return c
    return None


def _template_version(registry, template_id):
    t = registry.get(template_id) or {}
    return f"{template_id}-v{t.get('version', '0.1')}"


# Canonical spatial/height binding objects (schema-legal `binding` strategy
# shapes as instantiated in the reviewed canonical contracts).
SPATIAL_BINDING = {
    ("cloud_sea", "cloud_cover_low"): {
        "strategy": "nearest_gridpoint",
        "gridpoint_selector": "basin_cells_below_viewpoint"},
    ("cloud_sea", "visibility"): {
        "strategy": "nearest_gridpoint", "gridpoint_selector": "viewpoint_cell"},
    ("cloud_sea", "wind_speed_850hpa"): {
        "strategy": "height_bound", "candidate_levels_hpa": [925, 850],
        "target_height_expression": "deck_top_estimate + 200m"},
    ("cloud_sea", "wind_speed_600hpa"): {
        "strategy": "height_bound", "candidate_levels_hpa": [925, 850],
        "target_height_expression": "deck_top_estimate + 200m"},
    ("sunset", "cloud_cover_low"): {
        "strategy": "nearest_gridpoint", "gridpoint_selector": "sun_azimuth_sector"},
    ("sunrise", "cloud_cover_low"): {
        "strategy": "nearest_gridpoint", "gridpoint_selector": "sun_azimuth_sector"},
}


def binding_to_string(binding):
    if not binding:
        return None
    parts = [f"dataset:{binding['dataset']}", f"field:{binding['field']}",
             f"role:{binding['role']}"]
    if binding.get("level"):
        parts.append(f"level:{binding['level']}")
    return "|".join(parts)


def build_condition(oid, index, metric, op, threshold, unit, cat, row, *,
                    base=None, docs=None, registry=None, template_id=None,
                    provenance=False):
    """Assemble one canonical condition object.

    base: existing condition to update in place semantics (returns new dict).
    Policy: the registry row of the TARGET template (已審模板) supplies
    role/tier/domain/binding/rationale; the manager's 條件分類 decides gating
    (加分條件 -> QUALITY/BONUS, never gates). Numeric values: target-template
    registry threshold wins unless it is an expression (per-subject
    instantiation) or the xlsx carries an LCL placeholder; without a
    target-template row the xlsx value/rationale win and only the binding is
    borrowed from an exemplar.
    """
    bonus = (cat or "成立條件") == "加分條件"
    if base is None:
        rrow = None
        if template_id:
            t = registry.get(template_id) or {}
            for c in t.get("conditions") or []:
                if c["metric"] == metric:
                    rrow = c
                    break
        src = rrow or {}
        cond = {
            "id": f"C-{oid}-{index:02d}",
            "role": "QUALITY" if bonus else src.get("role", "REQUIRED"),
            "domain": src.get("domain", DOMAIN_BY_METRIC.get(metric, "WEATHER")),
            "evaluation_mode": src.get("evaluation_mode", "GUIDANCE"),
            "capability": src.get("capability", "CONDITIONS"),
            "metric": metric,
            "operator": op,
            "threshold": threshold,
            "unit": src.get("unit", unit),
            "unknown_policy": "propagate_unknown",
            "claim_refs": [],
            "model_binding": binding_to_string(src.get("binding")),
            "validation_status": "provisional",
            "condition_tier": "BONUS" if bonus else src.get("condition_tier", "MAIN"),
            "threshold_source": src.get("threshold_source", "formula_derived"),
            "calibration_status": src.get("calibration_status", "provisional"),
            "rationale_i18n": dict(src.get("rationale_i18n") or {}),
        }
        if src.get("binding"):
            pass  # registry binding is the raw dataset/field/role shape; it is
        # serialized into model_binding only. Spatial strategies come from the
        # canonical SPATIAL_BINDING map (schema-legal strategy objects).
        spatial = SPATIAL_BINDING.get((template_id, metric))
        if spatial:
            cond["binding"] = dict(spatial)
        if src.get("activate_when"):
            # night template moon modifiers: convert to schema-legal
            # modifier_activation referencing the moon_altitude condition id
            cond["modifier_activation"] = {"mode":
                                           src["activate_when"].get("mode",
                                                                    "when_not_met")}
            cond["modifier_activation"]["when_condition"] = "@moon_altitude"
        if src.get("genre_scope"):
            cond["genre_scope"] = src["genre_scope"]
        if rrow is None:
            ex = exemplar_condition(metric, docs or {}, genre=template_id)
            if ex is not None:
                cond["domain"] = ex.get("domain", cond["domain"])
                cond["model_binding"] = ex.get("model_binding")
                cond["threshold_source"] = ex.get("threshold_source",
                                                  cond["threshold_source"])
        if rrow is not None and not isinstance(rrow.get("threshold"), dict) \
                and rrow.get("threshold") is not None and op != "lcl":
            # reviewed template value wins over the stale xlsx copy
            if (cond["operator"], cond["threshold"]) != (rrow["operator"], rrow["threshold"]):
                cond["operator"] = rrow["operator"]
                cond["threshold"] = rrow["threshold"]
    else:
        cond = dict(base)
        cond["operator"] = op
        cond["threshold"] = threshold
        cond["unit"] = base.get("unit") or unit
    if provenance:
        cond["notes_i18n"] = dict(PROVENANCE_NOTE)
    return cond


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", default=str(DEFAULT_XLSX))
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    rows, by_subject = load_xlsx(args.xlsx)
    elevations = load_elevations()
    registry = load_registry()
    docs = load_canonical()

    stats = defaultdict(int)
    warnings = []
    lcl_report = []
    changed_files = set()

    for oid, srows in sorted(by_subject.items()):
        doc = docs.get(oid)
        if doc is None:
            warnings.append(f"{oid}: subject not in canonical opportunities")
            continue
        cc = doc.get("condition_contract") or {}
        cur_conditions = list(cc.get("conditions") or [])
        cur_by_metric = defaultdict(list)
        for c in cur_conditions:
            cur_by_metric[c["metric"]].append(c)
        xg = srows[0]["題材類別"]
        target_template = GENRE_ZH.get(xg)
        is_legacy = cc.get("genre_template") is None

        # ---------------- review-gated subjects (worker2_batch03/04 human
        # crosswalk gates pin their bespoke research-only contracts). Rebuilding
        # them would contradict human-review evidence; defer to the owner.
        if is_legacy and oid in REVIEW_GATED_SUBJECTS:
            warnings.append(
                f"{oid}: review-gated (batch03/04 crosswalk); manager's template "
                f"rows deferred to owner decision")
            stats["review_gated_deferred"] += 1
            continue

        # ---------------- tidal subjects: honest not_evaluatable, keep contract
        if xg == TIDAL_GENRE:
            if is_legacy and len(cur_conditions) == 1 and \
                    str(cur_conditions[0]["metric"]).startswith("legacy_"):
                # Keep the legacy placeholder contract byte-identical: it is the
                # honest not_evaluatable path (no tidal data source), pinned by
                # the migration skeleton byte-gate. The manager rationale lives
                # in the review xlsx; no weather contract is fabricated.
                stats["tidal_not_evaluatable"] += 1
            else:
                warnings.append(f"{oid}: unexpected tidal subject contract state")
            continue

        # ---------------- legacy subject: build a fresh contract from rows
        if is_legacy:
            claim = None
            for c in cur_conditions:
                if c.get("claim_refs"):
                    claim = c["claim_refs"][0]
                    break
            claim = claim or f"{oid}-claim-01"
            conditions = []
            non_weather = []
            for r in srows:
                label = r["條件指標"]
                if label in NON_WEATHER_ROWS:
                    non_weather.append(r)
                    continue
                metric = METRIC_ZH.get(label)
                if metric is None:
                    warnings.append(f"{oid}: unmapped metric label {label!r}")
                    continue
                op, th = parse_cond(r["數值化條件"])
                if op == "lcl":
                    alt = elevations.get(doc["place_id"])
                    if alt is None:
                        warnings.append(f"{oid}: no DEM elevation for LCL")
                        continue
                    th = alt - 200.0
                    th = _num(str(th))
                    op = "lt"
                    lcl_report.append((oid, alt, th))
                    rationale = lcl_rationale(alt, th, fix_note=False)
                else:
                    rrow = registry_row(registry, target_template, metric)
                    rationale = dict((rrow or {}).get("rationale_i18n") or {})
                unit = unit_for(r["數值化條件"])
                cond = build_condition(oid, len(conditions) + 1, metric, op, th,
                                       unit, r["條件分類"], r, docs=docs,
                                       registry=registry,
                                       template_id=target_template,
                                       provenance=True)
                if rationale:
                    cond["rationale_i18n"] = rationale
                xzh = str(r["口語化說明"] or "").strip()
                if xzh and cond["rationale_i18n"].get("zh-TW") != xzh \
                        and xzh in SUBJECT_TEXTS:
                    tr = dict(SUBJECT_TEXTS[xzh])
                    tr["zh-TW"] = xzh
                    cond["rationale_i18n"] = tr
                cond["claim_refs"] = [claim]
                conditions.append(cond)
            # special non-weather anchors
            for r in non_weather:
                label = r["條件指標"]
                zh = str(r["口語化說明"] or "").strip()
                if label == "活動/季節時程":
                    cond = {
                        "id": f"C-{oid}-{len(conditions)+1:02d}",
                        "role": "REQUIRED", "domain": "SEASON_TIME",
                        "evaluation_mode": "GUIDANCE",
                        "capability": "CONDITIONS",
                        "metric": "seasonal_state", "operator": "eq",
                        "threshold": "window_open", "unit": None,
                        "unknown_policy": "propagate_unknown",
                        "claim_refs": [claim], "model_binding": None,
                        "validation_status": "provisional",
                        "condition_tier": "MAIN",
                        "threshold_source": "computed",
                        "calibration_status": "provisional",
                        "rationale_i18n": {
                            "zh-TW": f"季節／活動窗判定（window_open/closed）：{zh}",
                            "en": "Season/event-window verdict (window_open/closed): the governing condition is the event calendar (fireworks / lantern festivals / parades / firefly season). No live event source exists, so this honestly propagates unknown (established 2026-11-01); only the minimum weather thresholds evaluate.",
                            "ja": "季節・イベント窓判定（window_open/closed）：支配的条件はイベントカレンダー（花火・灯節・パレード・蛍シーズン）。現在イベントソースがなく、誠実にunknownを伝播する（2026-11-01設定）。天気側の最低閾値のみ評価する。",
                        },
                        "notes_i18n": dict(PROVENANCE_NOTE),
                    }
                    conditions.append(cond)
                elif label == "光害/環境":
                    # no vocabulary metric for light pollution: fold the honest
                    # caveat into the seasonal anchor rationale (no metric invented)
                    for c in conditions:
                        if c["metric"] == "seasonal_state":
                            c["rationale_i18n"]["zh-TW"] += " " + zh
                            c["rationale_i18n"]["en"] += " Light-pollution level has no data source and honestly propagates unknown (2026-11-01)."
                            c["rationale_i18n"]["ja"] += " 光害レベルはデータソースがなく、誠実にunknownを伝播する（2026-11-01設定）。"
                            break
                    else:
                        warnings.append(f"{oid}: light-pollution caveat without a seasonal anchor")
                else:
                    warnings.append(f"{oid}: unhandled non-weather row {label!r}")
            # resolve the moon-gate modifier references to real condition ids
            moon_id = next((c["id"] for c in conditions
                            if c["metric"] == "moon_altitude"), None)
            for c in conditions:
                ma = c.get("modifier_activation")
                if ma and ma.get("when_condition") == "@moon_altitude":
                    if moon_id:
                        ma["when_condition"] = moon_id
                    else:
                        c.pop("modifier_activation", None)
            cc_new = {
                "contract_id": cc.get("contract_id") or f"CC-{oid}-v1",
                "status": "draft",
                "genre_template": target_template,
                "template_version": _template_version(registry, target_template),
                "recommendation_policy_version": cc.get("recommendation_policy_version"),
                "conditions": conditions,
            }
            doc["condition_contract"] = cc_new
            stats["legacy_rebuilt"] += 1
            stats["legacy_conditions_added"] += len(conditions)
            changed_files.add(oid)
            continue

        # ---------------- existing contract: row-level diff
        if target_template and target_template != cc.get("genre_template"):
            cc["genre_template"] = target_template
            cc["template_version"] = _template_version(registry, target_template)
            stats["genre_rewrite"] += 1
            # align rationales to the target template's reviewed wording where
            # the template row exists (e.g. sunset -> sunrise mismatch fixes)
            for c in cur_conditions:
                rrow = registry_row(registry, target_template, c["metric"])
                if rrow is not None and (rrow.get("rationale_i18n") or {}):
                    c["rationale_i18n"] = dict(rrow["rationale_i18n"])
                    changed_files.add(oid)
                    stats["rationale_updated"] += 1
        elif cc.get("template_version") != _template_version(registry, cc.get("genre_template")):
            # normalize stale template_version metadata on touched contracts
            if target_template:
                cc["template_version"] = _template_version(registry, target_template)

        x_by_metric = defaultdict(list)
        for r in srows:
            label = r["條件指標"]
            if label in NON_WEATHER_ROWS:
                warnings.append(f"{oid}: non-weather row on a contracted subject ({label})")
                continue
            metric = METRIC_ZH.get(label)
            if metric is None:
                warnings.append(f"{oid}: unmapped metric label {label!r}")
                continue
            x_by_metric[metric].append(r)

        for met, rs in x_by_metric.items():
            r = rs[0]
            chg = r["變更狀態"]
            op, th = parse_cond(r["數值化條件"])
            cands = cur_by_metric.get(met)
            if not cands:
                # elevation-bound alias classes: current 700/600 hPa rows own the
                # generic 925/850 xlsx labels; skip (owner fix wins)
                if any(ELEV_ALIAS.get(m) == met for m in cur_by_metric):
                    stats["stale_alias_skipped"] += 1
                    continue
                if met in ALIAS_TARGETS and any(
                        ELEV_ALIAS.get(m) == met for m in cur_by_metric):
                    continue
                # genuinely new row on an existing contract
                cond = build_condition(
                    oid, len(cur_conditions) + 1, met, op, th,
                    unit_for(r["數值化條件"]), r["條件分類"], r, docs=docs,
                    registry=registry, template_id=target_template,
                    provenance=True)
                first = cur_conditions[0] if cur_conditions else None
                cond["claim_refs"] = list((first or {}).get("claim_refs") or
                                          [f"{oid}-claim-01"])
                if op == "lcl" or met == "lcl_height_m_agl":
                    alt = elevations.get(doc["place_id"])
                    if alt is None:
                        warnings.append(f"{oid}: no DEM elevation for LCL")
                        continue
                    th = _num(str(alt - 200.0))
                    cond["operator"] = "lt"
                    cond["threshold"] = th
                    cond["rationale_i18n"] = lcl_rationale(alt, th, fix_note=False)
                    lcl_report.append((oid, alt, th))
                cur_conditions.append(cond)
                cur_by_metric[met].append(cond)
                stats["rows_added_existing"] += 1
                warnings.append(f"{oid}: row added to existing contract ({met})")
                changed_files.add(oid)
                continue
            c = cands[0]
            if op == "lcl" or met == "lcl_height_m_agl":
                alt = elevations.get(doc["place_id"])
                if alt is None:
                    warnings.append(f"{oid}: no DEM elevation for LCL")
                    continue
                new_th = alt - 200.0
                new_th = int(new_th) if float(new_th).is_integer() else new_th
                old_th = c.get("threshold")
                xlsx_th = None if th is None else th
                if xlsx_th is not None and xlsx_th != new_th:
                    warnings.append(
                        f"{oid}: xlsx LCL {xlsx_th} differs from DEM recompute {new_th}; DEM wins")
                c["threshold"] = new_th
                c["rationale_i18n"] = lcl_rationale(alt, new_th, fix_note=True)
                lcl_report.append((oid, alt, new_th, old_th))
                stats["lcl_recomputed"] += 1
                changed_files.add(oid)
                continue
            if op in ("none",):
                continue
            if op == "eq":
                continue
            same = (c["operator"] == op and c.get("threshold") == th)
            if not same:
                stale = STALE_XLSX.get((met, op, th))
                if chg is None and stale == (c["operator"], c.get("threshold")):
                    stats["stale_xlsx_skipped"] += 1
                    continue
                if chg is None:
                    warnings.append(
                        f"{oid}: unchanged-row value drift xlsx=({op},{th}) "
                        f"cur=({c['operator']},{c.get('threshold')}) metric={met}")
                    continue
                c["operator"] = op
                c["threshold"] = th
                stats["rows_fixed"] += 1
                changed_files.add(oid)
            if chg and "修正" in str(chg):
                if r["條件分類"] == "加分條件":
                    c["role"] = "QUALITY"
                    rrow = registry_row(registry, target_template, met)
                    marker = "2026-11-01" in str(r["口語化說明"] or "")
                    if marker or rrow is None:
                        c["condition_tier"] = "BONUS"
                    elif rrow.get("condition_tier"):
                        c["condition_tier"] = rrow["condition_tier"]
                talk = str(r["口語化說明"] or "").strip()
                if "2026-11-01" in talk:
                    if met == "cloud_cover_total" and target_template == "reflection":
                        c["rationale_i18n"] = dict(T_CLOUD_TOTAL_BONUS)
                    elif met == "aod_550nm":
                        c["rationale_i18n"] = dict(T_AOD_BONUS_REWRITE)
                    elif met == "visibility" and target_template == "overlook":
                        c["rationale_i18n"] = dict(T_VIS_US010)
                    elif met == "cloud_cover_total":
                        c["rationale_i18n"] = dict(T_CLOUD_TOTAL_BONUS)
                    else:
                        warnings.append(f"{oid}: 修正 rationale not mapped ({met})")
                    stats["rationale_updated"] += 1
                    changed_files.add(oid)

        # rewritten reflection subjects: total-cloud row marked 新增(重寫) with
        # 加分 semantics (role QUALITY / BONUS) and manager rationale
        for r in srows:
            chg = str(r["變更狀態"] or "")
            if "重寫" in chg:
                metric = METRIC_ZH.get(r["條件指標"])
                cands = cur_by_metric.get(metric)
                op, th = parse_cond(r["數值化條件"])
                if not cands:
                    cond = build_condition(
                        oid, len(cur_conditions) + 1, metric, op, th,
                        unit_for(r["數值化條件"]), r["條件分類"], r, docs=docs,
                        registry=registry, template_id=target_template,
                        provenance=True)
                    cond["claim_refs"] = list((cur_conditions[0].get("claim_refs") or
                                               [f"{oid}-claim-01"]))
                    cur_conditions.append(cond)
                    cur_by_metric[metric].append(cond)
                    stats["rows_added_existing"] += 1
                    changed_files.add(oid)
                    c = cond
                else:
                    c = cands[0]
                if r["條件分類"] == "加分條件":
                    c["role"] = "QUALITY"
                    c["condition_tier"] = "BONUS"
                if metric == "cloud_cover_total":
                    c["rationale_i18n"] = dict(T_CLOUD_TOTAL_BONUS_REWRITE)
                elif metric == "water_surface_state":
                    pass  # registry rationale already carries the wording
                changed_files.add(oid)
                stats["rows_rewritten"] += 1

        # deletions: current conditions with no xlsx row (誤植移除)
        kept = []
        for c in cur_conditions:
            met = c["metric"]
            hits = x_by_metric.get(met)
            if not hits and met in ELEV_ALIAS:
                hits = x_by_metric.get(ELEV_ALIAS[met])
            if hits:
                kept.append(c)
            else:
                stats["rows_deleted"] += 1
                changed_files.add(oid)
        cur_conditions = kept
        doc["condition_contract"]["conditions"] = cur_conditions

    # ---------------- verification inside the importer
    problems = list(warnings)
    for oid, doc in docs.items():
        cc = doc.get("condition_contract") or {}
        conds = cc.get("conditions") or []
        if not conds:
            problems.append(f"{oid}: EMPTY condition contract")
        ids = [c["id"] for c in conds]
        if len(ids) != len(set(ids)):
            problems.append(f"{oid}: duplicate condition ids")
        for c in conds:
            if str(c["metric"]).startswith("legacy_") and cc.get("genre_template"):
                pass  # legacy anchors inside genre contracts are intentional
            if c.get("calibration_status") not in (None, "provisional", "approved"):
                problems.append(f"{oid}: bad calibration_status {c.get('calibration_status')}")
            if c.get("validation_status") not in (None, "unvalidated", "provisional", "validated"):
                problems.append(f"{oid}: bad validation_status")
            for c2 in conds:
                if c2 is c:
                    continue
    if args.apply:
        for oid in sorted(changed_files):
            path = OPP_DIR / f"{oid}.json"
            text = json.dumps(docs[oid], ensure_ascii=False, indent=2) + "\n"
            path.write_text(text, encoding="utf-8", newline="\n")
        print(json.dumps({"applied": len(changed_files)}, ensure_ascii=False))
    report = {
        "stats": dict(stats),
        "warnings": warnings,
        "changed_files": sorted(changed_files),
        "lcl_report": [
            {"subject": item[0], "viewpoint_altitude_m": item[1],
             "new_lcl": item[2], **({"old_lcl": item[3],
                                     "diff_m": round(item[2] - item[3], 1)}
                                    if len(item) > 3 else {})}
            for item in lcl_report],
    }
    print(json.dumps(report, ensure_ascii=False, indent=1))
    if problems:
        print("PROBLEMS:", file=sys.stderr)
        for p in problems:
            print(" -", p, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
