#!/usr/bin/env python3
"""CL-DATA-34: build V2 opportunity contracts for the 7 jp legacy spots that had
NO V2 contract (jp-001, jp-012, jp-014, jp-015, jp-017, jp-018, jp-024).
Method mirrors CL-DATA-20 (Taiwan legacy contract build): AI web verification
(owner ruling 2026-11-06: AI-sourced URL+date suffices), trilingual copy,
provenance URL+date on every checkable fact. Excludes jp-037..049 and any
CL-DATA-32 additions (not on the base yet)."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if (Path(__file__).resolve().parent.name == 'tools') else Path.cwd()
if not (ROOT / 'data/v2/opportunities').is_dir():
    ROOT = Path('D:/tmp/cl-data-34-wt')
OPS = ROOT / 'data/v2/opportunities'
AS_OF = '2026-11-08'

# ---------------------------------------------------------------- evidence
EVIDENCE = {
    "audit_version": "cl-data-34-web-verification-v1",
    "as_of": AS_OF,
    "method": "AI web verification (owner ruling 2026-11-06: AI-sourced URL+date suffices for entry; human-review gate retired). Coordinates, elevation, opening/illumination windows and seasonal windows verified per spot before contract authoring.",
    "scope": "CL-DATA-34: seven no-V2-contract jp legacy spots (jp-001, jp-012, jp-014, jp-015, jp-017, jp-018, jp-024). jp-037..049 and CL-DATA-32 additions (jp-051..064) excluded by ticket scope.",
    "evidence": [
        {"id": "e-d34-a", "grade": "A", "kind": "encyclopedic_text", "url": "https://ja.wikipedia.org/wiki/%E9%9D%92%E3%81%84%E6%B1%A0",
         "supports": "Blue Pond coordinates 43.493583N 142.614028E (V1 point within ~15 m) and elevation ~500 m on the left bank of the Biei River; artificial pond of the 1989 Tokachidake lahar-control dams, drowned larches (karamatsu).",
         "retrieved_at": AS_OF, "limitation": "Community encyclopedia; coordinates cross-checked against V1 POI"},
        {"id": "e-d34-b", "grade": "A", "kind": "official_text", "url": "https://www.biei-hokkaido.jp/ja/facility/shirogane-blue-pond",
         "supports": "Biei Tourism Association (official): pond water from the aluminum-bearing Shirahige Falls / Biei River mix turns cobalt blue, drowned larches over a mirror surface; seasonal expressions.",
         "retrieved_at": AS_OF, "limitation": "Tourism copy"},
        {"id": "e-d34-c", "grade": "A", "kind": "official_text", "url": "https://www.visit-hokkaido.jp/spot/detail_10511.html",
         "supports": "HOKKAIDO LOVE! (official): autumn foliage contrasts with the blue water; calm-water reflections of the standing dead larches; bridge overlook.",
         "retrieved_at": AS_OF, "limitation": "No foliage dates given; window is climatological"},
        {"id": "e-d34-d", "grade": "A", "kind": "official_text", "url": "https://www.pref.kanagawa.jp/osirase/0602/feelshonan/sightseeing/1066/index.html",
         "supports": "Kanagawa Prefecture official: Kotoku-in (Kamakura Daibutsu) hours 8:00-17:30 (Apr-Sep), 8:00-17:00 (Oct-Mar), open year-round.",
         "retrieved_at": AS_OF, "limitation": "None for hours"},
        {"id": "e-d34-e", "grade": "B", "kind": "travel_text", "url": "https://www.enjoytokyo.jp/article/205020/",
         "supports": "Kotoku-in autumn foliage: ginkgo and maple peak 11-late to 12-early (info confirmed by the Kotoku-in temple office); maple trees behind the Great Buddha are the representative vantage; no illumination.",
         "retrieved_at": AS_OF, "limitation": "Commercial guide, but temple-office confirmed; window climatological"},
        {"id": "e-d34-f", "grade": "B", "kind": "travel_text", "url": "https://www.trip-kamakura.com/facility/detail.php?id=23",
         "supports": "Kotoku-in hours detail 8:00-17:30 (Apr-Sep) / 8:00-17:00 (Oct-Mar), last entry 15 min before closing, year-round.",
         "retrieved_at": AS_OF, "limitation": "Secondary source cross-checked against the Kanagawa Prefecture official page (e-d34-d)"},
        {"id": "e-d34-g", "grade": "A", "kind": "official_text", "url": "https://www.city.setagaya.lg.jp/02075/9082.html",
         "supports": "Setagaya City (official): Todoroki Valley Park, ~1 km gorge carved by Yazawa River into the Musashino terrace, the only gorge in Tokyo 23 wards, designated scenic spot.",
         "retrieved_at": AS_OF, "limitation": "No elevation published; camera altitude left unknown"},
        {"id": "e-d34-h", "grade": "B", "kind": "travel_text", "url": "https://www.nikotama-kun.jp/spot/season/momizi/",
         "supports": "Todoroki Valley autumn: both banks of the ~600 m boardwalk turn red, stream with falling leaves; local tourism portal.",
         "retrieved_at": AS_OF, "limitation": "No dates; Tokyo foliage window climatological"},
        {"id": "e-d34-i", "grade": "B", "kind": "travel_text", "url": "https://j-eps.net/spot/zh-hant-%E7%9A%87%E5%B1%85%E5%A4%96%E8%8B%91/",
         "supports": "Kokyo Gaien (Imperial Palace outer garden, Environment Ministry managed): plaza area open at all times, free, no regular holidays; classic Nijubashi photo point is the Seimon Stone Bridge view across the moat (stone bridge + iron bridge + Fushimi-yagura).",
         "retrieved_at": AS_OF, "limitation": "Special events/closures possible; hours guidance only"},
        {"id": "e-d34-j", "grade": "B", "kind": "travel_text", "url": "https://watabi.org/articles/kenrokuen-winter-illumination-2027",
         "supports": "Kenrokuen winter hours 10-16..2-end 8:00-17:00 (last entry 16:30); yukitsuri (snow-hanging rope work) starts 11-01, whole garden hung by mid-December; winter illumination 'Fuyu no Dan' 18:00-21:00 on ~8 February nights only (free, no reservations); yukitsuri reflected in Kasumiga-ike.",
         "retrieved_at": AS_OF, "limitation": "Secondary source quoting Ishikawa Prefecture official pages"},
        {"id": "e-d34-k", "grade": "B", "kind": "travel_text", "url": "https://log.tripuuu.com/zh-hant/snow-scenery/chubu/kenrokuen-yukitsuri",
         "supports": "Kenrokuen yukitsuri typical viewing mid-December to late February; snow scene requires snowfall; Kenrokuen Park winter illumination event window.",
         "retrieved_at": AS_OF, "limitation": "Secondary source"},
        {"id": "e-d34-l", "grade": "A", "kind": "official_text", "url": "https://www.nagoyajo.city.nagoya.jp/info/faq/",
         "supports": "Nagoya Castle official FAQ: the castle keep exterior is illuminated EVERY DAY from sunset until 23:00 (21:30 on the 8th of each month / green campaign nights may switch off earlier).",
         "retrieved_at": AS_OF, "limitation": "Illumination of the exterior; castle grounds close 16:30 so the night view is from the surrounding area"},
        {"id": "e-d34-m", "grade": "A", "kind": "official_text", "url": "https://www.nagoya-info.jp/event/detail/65/",
         "supports": "Nagoya City official tourism: Nagoya Castle grounds 9:00-16:30, closed 17:00 (longer hours only during festival periods).",
         "retrieved_at": AS_OF, "limitation": "None for regular hours"},
        {"id": "e-d34-n", "grade": "A", "kind": "official_text", "url": "https://www.osakacastle.net/question/",
         "supports": "Osaka Castle official FAQ: keep illumination runs every day from sunset until 24:30, ramping up over ~1 h after sunset; only the one annual inspection day is dark.",
         "retrieved_at": AS_OF, "limitation": "None for illumination"},
        {"id": "e-d34-o", "grade": "B", "kind": "travel_text", "url": "https://j-eps.net/spot/osaka-castle-park/",
         "supports": "Osaka Castle Park is free and the park itself is open 24 h (paid facilities have their own hours); the illuminated keep is viewed from around Gokuraku-bashi and the inner moat.",
         "retrieved_at": AS_OF, "limitation": "Secondary source; visit routes follow on-site notices"},
    ],
}

LW = {
    "zh-TW": "必要光線窗：全日可見光題材只在民用光（太陽仰角 > −6°）內成立（CL-DATA-11 同源定義；夜間一律不符合）。場區營業時間另見存取資訊。",
    "en": "Required light window: an all-day visible-light subject only qualifies in civil light (sun elevation > -6 deg; CL-DATA-11 same-source definition; night hours never qualify). Site opening hours are noted in the access notes.",
    "ja": "必要な光の窓：全日型の可視光題材は市民光（太陽高度 > -6°）の時間帯でのみ成立（CL-DATA-11 同源定義、夜間は一律不成立）。施設の開場時間はアクセス情報を参照。",
}


def cond(oid, n, role, metric, operator, threshold, unit, binding, tier, src, rat):
    return {"id": f"C-{oid}-{n}", "role": role, "domain": "WEATHER" if binding or metric in (
        'precipitation', 'visibility', 'cloud_cover_total', 'cloud_cover_mid', 'cloud_cover_low',
        'aod_550nm', 'wind_speed_10m') else ("ASTRONOMY" if metric in ('light_window', 'sunset_window', 'sunrise_time_window', 'golden_hour_window', 'city_night_window') else "SEASON_TIME"),
        "evaluation_mode": "GUIDANCE", "capability": "CONDITIONS", "metric": metric, "operator": operator,
        "threshold": threshold, "unit": unit, "unknown_policy": "propagate_unknown",
        "claim_refs": [f"{oid}-claim-01"], "model_binding": binding, "validation_status": "provisional",
        "condition_tier": tier, "threshold_source": src, "calibration_status": "provisional", "rationale_i18n": rat}


def light_window(oid):
    return {"id": f"C-{oid}-LW1", "role": "REQUIRED", "domain": "ASTRONOMY", "evaluation_mode": "GUIDANCE",
            "capability": "CONDITIONS", "metric": "light_window", "operator": "none", "threshold": None, "unit": None,
            "unknown_policy": "propagate_unknown", "claim_refs": [f"{oid}-claim-01"], "model_binding": None,
            "validation_status": "provisional", "condition_tier": "MAIN", "threshold_source": "computed",
            "calibration_status": "provisional", "rationale_i18n": LW}


def gfs(field, role):
    return f"dataset:gfs_0p25|field:{field}|role:{role}"


def make_contract(oid, place, names, desc, cam_geo, geo_status, geo_deriv, access, safety,
                  genre, tv, conditions, altitude, nav_label, claim_note, nav_status="needs_review",
                  nav_conf="low"):
    point = {"type": "Point", "coordinates": [cam_geo[1], cam_geo[0]]}
    return {
        "schema_version": "2.1.0", "opportunity_id": oid, "place_id": place, "revision": 1,
        "lifecycle_status": "draft", "name_i18n": names, "description_i18n": desc,
        "camera_contexts": [{
            "id": f"CZ-{oid}-01", "kind": "area",
            "geometry": {"kind": "point", "status": geo_status, "geojson": point, "uncertainty_m": None,
                          "derivation_method": geo_deriv, "source_geometry_revision": None,
                          "reason_if_absent": None},
            "verification_status": geo_status, "evidence_refs": [],
            "access_notes_i18n": access, "safety_notes_i18n": safety, "altitude_m": altitude}],
        "targets": [{
            "id": f"SG-{oid}-01", "kind": "multi_component", "name_i18n": names,
            "geometry": {"kind": "point", "status": "provisional", "geojson": point, "uncertainty_m": None,
                          "derivation_method": "imported_from_v1_viewpoint_reference; terrain/shooting-point facts web-verified (see camera derivation_method)",
                          "source_geometry_revision": None, "reason_if_absent": None},
            "phenomenon_model_id": None, "evidence_refs": [], "components": []}],
        "observation_relations": [{
            "id": f"VR-{oid}-01", "camera_context_id": f"CZ-{oid}-01", "target_id": f"SG-{oid}-01",
            "type": "foreground_background", "geometry_mode": "unknown", "azimuth_deg": None,
            "elevation_deg": None, "distance_m": None, "evidence_refs": [], "derivation_method": None,
            "uncertainty_note": "Imported V1 reference; angles and distance unknown."}],
        "navigation_targets": [{
            "id": f"NAV-{oid}-01", "status": nav_status, "target_type": "other",
            "lat": cam_geo[0], "lon": cam_geo[1], "label_i18n": nav_label, "evidence_refs": [],
            "confidence": nav_conf}],
        "condition_contract": {
            "contract_id": f"CC-{oid}-v1", "status": "draft", "genre_template": genre,
            "template_version": tv, "recommendation_policy_version": None, "conditions": conditions},
        "evidence_claims": [{
            "claim_id": f"{oid}-claim-01", "claim_type": "existence", "evidence_refs": EVID_REFS.get(oid, []),
            "audit_status": "UNKNOWN",
            "scope_note": claim_note}],
        "readiness": {"research_level": "R1", "gaps": ["RESEARCH_GAP"]},
        "provenance": {"source_catalog": "runtime_catalog_v004_r4_2.json", "source_revision": f"v1-spot-{place}",
                        "imported_at": "2026-11-08T00:00:00Z", "review_status": "pending", "reviewed_by": None},
    }


REFLECTION_RAT = {
    "wind": {"zh-TW": "倒影題材的命門是風：水面風速 >2 m/s 就起漣漪，立枯的鏡像破碎；2 m/s 以下才能拿到乾淨的鏡面反射。", "en": "Wind is the make-or-break for reflections: above 2 m/s the water ripples and the mirror of the drowned larches breaks; only under 2 m/s gives a clean mirror.", "ja": "反射撮影の要は風：水面風速2m/sを超えると漣が立ち、枯れ木の鏡像が崩れる。2m/s未満で初めて鏡面が得られる。"},
    "wsurface": {"zh-TW": "水面狀態（結冰/水位）無即時觀測源，誠實回報 UNKNOWN，不猜測：冬期結冰時倒影不成立，請依現場狀況判斷。", "en": "Water-surface state (ice/level) has no live observation source - honestly UNKNOWN, never guessed: in winter freeze the reflection fails, judge on site.", "ja": "水面状態（結氷・水位）は即時観測源がなく、誠実にUNKNOWNを返す（推測しない）。冬季の凍結時は反射が成立しない。現地で判断すること。"},
    "prec": {"zh-TW": "雨點直接打在水面就沒有鏡面，降水 >0.2 mm/h 否決。", "en": "Raindrops breaking the water surface kill the mirror; reject above 0.2 mm/h.", "ja": "雨粒が水面を叩くと鏡面は成立しない。降水0.2mm/h超は否決。"},
    "cloud": {"zh-TW": "帶點雲的藍天（總雲量 20–60%）讓倒影有色階而不是一片死藍；純藍天太單調，全陰太暗。", "en": "Broken blue sky (total cloud 20-60%) gives the reflection tonal bands instead of a flat blue; pure blue is monotonous, full overcast too dark.", "ja": "適度な雲（全雲量20〜60%）があると反射に階調が出る。快晴だと単調、全曇では暗すぎる。"},
}
SEASON_RAT = {
    "season": None,  # filled per spot below
    "prec": {"zh-TW": "降水 >0.2 mm/h 時葉面打濕、色彩變鈍，否決。", "en": "Above 0.2 mm/h the wet foliage dulls and colors wash out; reject.", "ja": "降水0.2mm/h超では葉が濡れて色彩が鈍るため否決。"},
    "wind": {"zh-TW": "風速 >5 m/s 吹動枝葉、長曝糊掉，否決。", "en": "Wind above 5 m/s shakes the branches and smears long exposures; reject.", "ja": "風速5m/s超では枝葉が揺れて長時間露出がぼやけるため否決。"},
}
NIGHT_RAT = {
    "cloud": {"zh-TW": "夜間點燈主體是建物照明，但天空乾淨（總雲量 ≤30%）才有星空層次與清晰的燈光邊緣。", "en": "The subject is the illuminated building, but a clean sky (total cloud ≤30%) keeps the light edges crisp and leaves room for stars.", "ja": "主題は夜間照明の建物だが、空が澄んでいる（全雲量30%以下）と光の縁がくっきりし星空も残る。"},
    "vis": {"zh-TW": "能見度 ≥10 km 才能把燈光顏色拍準；霧霾會把照明染成土黃。", "en": "Visibility ≥10 km keeps the lighting colors true; haze stains the illumination muddy.", "ja": "視程10km以上で照明の色が正確に写る。ヘイズでは照明明色が濁る。"},
    "prec": {"zh-TW": "降水 >0.2 mm/h 鏡頭進水、燈光暈開，否決。", "en": "Above 0.2 mm/h water hits the lens and the lights smear; reject.", "ja": "降水0.2mm/h超ではレンズに水滴が付き灯光がにじむため否決。"},
    "aod": {"zh-TW": "AOD >0.5 的霧霾夜會把整座照明糊成一團光暈，否決；乾淨夜空才見得到金鯱的輪廓。", "en": "On hazy nights (AOD >0.5) the whole illumination smears into a halo blob; reject - a clean night sky is what keeps the golden details readable.", "ja": "AOD0.5超のヘイズの夜は照明全体が光暈に溶けるため否決。澄んだ夜空でこそ金の細部が読める。"},
    "window": None,  # filled per spot
}
GOLD_RAT = {
    "vis": {"zh-TW": "能見度 ≥8 km（市區空氣常帶霾，設 10 km 太苛）：遠景與主體輪廓都要看得清楚。", "en": "Visibility ≥8 km (city air carries haze; 10 km would be too strict): both the subject and the background need readable edges.", "ja": "視程8km以上（都市の空気はヘイズを帯びるため10kmは過酷）：対象と背景の輪郭がはっきり読める必要がある。"},
    "aod": {"zh-TW": "AOD >0.5 霧霾會讓主體輪廓發灰，否決。", "en": "AOD >0.5 haze greys out the subject's edges; reject.", "ja": "AOD0.5超のヘイズは対象の輪郭を灰色にするため否決。"},
    "prec": {"zh-TW": "降水 >0.2 mm/h 時拍攝與器材都受影響，否決。", "en": "Above 0.2 mm/h shooting and gear suffer; reject.", "ja": "降水0.2mm/h超は撮影も機材も難航するため否決。"},
    "gold": {"zh-TW": "低角度金光作為加分項：斜光把青銅面/石垣的立體感拍出來；白天平光仍可拍，只是較平。", "en": "Low-angle golden light is a bonus: raking light brings out the relief of bronze surfaces and stonework; flat midday light still shoots, just flatter.", "ja": "低角度のゴールデン光は加点：斜光が青銅面や石垣の立体感を引き出す。昼間の平光でも撮れるが、平坦になる。"},
}
PAN_RAT = {
    "cloud": {"zh-TW": "全景層次來自天空結構：總雲量 30–60% 的碎雲帶讓廣場/城郭全景有明暗節奏；藍底白雲最理想。", "en": "Panorama depth comes from sky structure: broken cloud at 30-60% total gives the plaza/castle vista a brightness rhythm; blue sky with fair-weather cloud is ideal.", "ja": "全景の層次は空の構造が作る：全雲量30〜60%の断片雲帯が広場・城郭の景色に明暗のリズムを与える。晴天空雲が理想。"},
    "vis": {"zh-TW": "能見度 ≥10 km：全景價值就在看得遠，霧霾直接否決。", "en": "Visibility ≥10 km: the whole point of a vista is distance; haze vetoes it.", "ja": "視程10km以上：眺望の価値は遠くまで見えることにあり、ヘイズは直接否決。"},
    "aod": {"zh-TW": "AOD >0.6 才否決（中等霧霾仍留層次感）。", "en": "Veto only above AOD 0.6 (moderate haze still leaves some layering).", "ja": "AOD0.6超のみ否決（中程度のヘイズは依然層を残す）。"},
    "sunrise": {"zh-TW": "晨昏低角度光是廣場全景最上相的窗口（順光點亮主體、逆光剪影），作為加分項。", "en": "Low-angle dawn/dusk light is the vista's best window (front light warms the subject, backlight silhouettes it) - a bonus, not a gate.", "ja": "朝夕の低角度光が眺望の最良窓（順光で対象を暖め、逆光でシルエットにする）。門檻ではなく加点。"},
}

SPOTS = {
    "jp-001": {"lat": 43.493611, "lon": 142.614167,
                "zh": "美瑛青池", "en": "Shirogane Blue Pond", "ja": "美瑛青い池"},
    "jp-012": {"lat": 35.31685, "lon": 139.53572,
                "zh": "鎌倉大佛", "en": "Kamakura Great Buddha", "ja": "鎌倉大仏"},
    "jp-014": {"lat": 35.607857, "lon": 139.646545,
                "zh": "等等力溪谷", "en": "Todoroki Valley", "ja": "等々力渓谷"},
    "jp-015": {"lat": 35.678475, "lon": 139.754897,
                "zh": "皇居外苑二重橋", "en": "Nijubashi, Imperial Palace Outer Garden", "ja": "皇居外苑・二重橋"},
    "jp-017": {"lat": 36.563367, "lon": 136.662817,
                "zh": "金澤兼六園", "en": "Kenrokuen Garden", "ja": "兼六園"},
    "jp-018": {"lat": 35.185181, "lon": 136.89865,
                "zh": "名古屋城", "en": "Nagoya Castle", "ja": "名古屋城"},
    "jp-024": {"lat": 34.6892, "lon": 135.52675,
                "zh": "大阪城公園", "en": "Osaka Castle Park", "ja": "大阪城公園"},
}

SP3 = {pid: {"zh-TW": v["zh"], "en": v["en"], "ja": v["ja"]} for pid, v in SPOTS.items()}

CONTRACTS = []  # filled by build functions below
EVID_REFS = {'jp-001-P01': ['e-d34-a','e-d34-b'], 'jp-001-P02': ['e-d34-c'], 'jp-012-P01': ['e-d34-d','e-d34-f'], 'jp-012-P02': ['e-d34-e'], 'jp-014-P01': ['e-d34-g'], 'jp-014-P02': ['e-d34-g','e-d34-h'], 'jp-015-P01': ['e-d34-i'], 'jp-015-P02': ['e-d34-i'], 'jp-017-P01': ['e-d34-j','e-d34-k'], 'jp-017-P02': ['e-d34-j'], 'jp-018-P01': ['e-d34-m'], 'jp-018-P02': ['e-d34-l'], 'jp-024-P01': ['e-d34-n','e-d34-o'], 'jp-024-P02': ['e-d34-o']}


def a_(d):
    return " biei-hokkaido" if False else d


# ---------------- jp-001 ----------------
oid = "jp-001-P01"
CONTRACTS.append(make_contract(
    oid, "jp-001",
    {"zh-TW": "青池立枯倒影", "en": "Blue Pond drowned-larch reflection", "ja": "青い池の立ち枯れと水面反射"},
    {"zh-TW": "在池畔步道與橋上拍立枯落羽松與青色水面的鏡像：風靜水貼如鏡時，白樺與枯木完整倒映；晨間水氣未起前最穩。",
     "en": "Shoot the drowned larches mirroring in the cobalt water from the pond boardwalk and the bridge: on calm mornings before the wind picks up, the dead trees and birches reflect whole.",
     "ja": "池畔の遊歩道と橋から、立ち枯れのカラマツと青い水面の鏡像を撮る。風の朝早い時間帯、水面が鏡のようになったとき枯れ木が完全に映り込む。"},
    (43.493611, 142.614167), "verified",
    "imported_from_v1_viewpoint_reference; CL-DATA-34 AI web verification 2026-11-08: ja.wikipedia 青い池 coordinates 43.493583N 142.614028E match V1 point within ~15 m and elevation 約500 m (https://ja.wikipedia.org/wiki/青い池); subject facts per 美瑛町観光協会 (https://www.biei-hokkaido.jp/ja/facility/shirogane-blue-pond)",
    {"zh-TW": "池畔步道與ブルーリバー橋全日開放，冬季積雪期間步道可能封閉，請依現場公告。", "en": "The pond boardwalk and Blue River Bridge are open all day; in winter the path may close after snowfall - follow on-site notices.", "ja": "池畔の遊歩道とブルーリバー橋は終日開放。冬の積雪期は通行止めになる場合があり現地の告知に従うこと。"},
    {"zh-TW": "池岸濕滑，晨間結霜時務必注意腳下；步道外不得進入池畔。", "en": "The banks are slippery - mind frost in the early morning; do not leave the boardwalk.", "ja": "池畔は滑りやすい。朝の霜に注意し、遊歩道外へ入らないこと。"},
    "reflection", "reflection-v0.1",
    [cond(oid, "01", "REQUIRED", "wind_speed_10m", "lte", 2.0, "m/s", gfs("wind_speed_10m_m_s", "MID"), "MAIN", "formula_derived", REFLECTION_RAT["wind"]),
     cond(oid, "02", "REQUIRED", "water_surface_state", "none", None, None, None, "MAIN", "computed", REFLECTION_RAT["wsurface"]),
     cond(oid, "03", "REQUIRED", "precipitation", "lt", 0.2, "mm", gfs("precipitation_rate_mm_h", "MID"), "MAIN", "formula_derived", REFLECTION_RAT["prec"]),
     cond(oid, "04", "QUALITY", "cloud_cover_total", "between", [20, 60], "%", gfs("cloud_cover_total_percent", "MID"), "MODIFIER", "formula_derived", REFLECTION_RAT["cloud"]),
     light_window(oid)],
    500, SP3["jp-001"],
    "Subject existence per V1 catalog; pond geometry, ~500 m elevation and subject facts web-verified 2026-11-08 (sources e-d34-a/b/c in cl-data-34_web_evidence.json). Thresholds provisional pending real-shoot calibration."))

foliage_rat_aoiike = {"zh-TW": "季節窗判定（例年窗 10-05–10-31）：青池秋色是短暫的一檔——白樺與落羽松轉黃、與鈷藍水面對比最強的兩至三週（HOKKAIDO LOVE! 官方僅稱「秋の紅葉とのコントラスト」，未給日期；例年窗為氣候學估計）。實況窗優先，兩者皆缺時誠實 not_evaluatable。",
                       "en": "Seasonal-window verdict (typical window 10-05 to 10-31): the Blue Pond autumn look is a short, sharp window - birches and larches turn gold against the cobalt water for two to three weeks (HOKKAIDO LOVE! official names the autumn contrast but gives no dates; the typical window is climatological). Observed window takes precedence; with neither present, honestly not_evaluatable.",
                       "ja": "季節窓判定（例年窓10-05〜10-31）：青い池の秋色は短い一途——白樺とカラマツが黄金色に染まりコバルトブルーの水面と最も強く対比する2〜3週間（HOKKAIDO LOVE!公式は秋の紅葉とのコントラストに言及するが日程は不明、例年窓は気候学的推定）。実況窓を優先し、両方なければ誠実にnot_evaluatable。"}
oid = "jp-001-P02"
CONTRACTS.append(make_contract(
    oid, "jp-001",
    {"zh-TW": "青池秋色", "en": "Blue Pond autumn foliage", "ja": "青い池の紅葉"},
    {"zh-TW": "白樺與落羽松轉黃的兩三週裡，金黃枝葉與鈷藍水面形成年度最強對比；沿池步道取景立枯與色葉同框。",
     "en": "In the two or three weeks when the birches and larches turn gold, the foliage against the cobalt water is the pond's strongest annual contrast; frame the drowned larches together with the colored leaves from the boardwalk.",
     "ja": "白樺とカラマツが黄金色に染まる2〜3週間、金の枝葉とコバルトブルーの水面が年で最も強いコントラストを見せる。遊歩道から立ち枯れと色づいた葉を一枚に収める。"},
    (43.493611, 142.614167), "verified",
    "imported_from_v1_viewpoint_reference; CL-DATA-34 AI web verification 2026-11-08: same coordinate verification as jp-001-P01 (e-d34-a); autumn foliage named by official HOKKAIDO LOVE! page (e-d34-c)",
    {"zh-TW": "同 jp-001-P01；紅葉期常伴晨霜，步道濕滑。", "en": "Same as jp-001-P01; frost accompanies the foliage mornings and the boardwalk is slippery.", "ja": "jp-001-P01 と同じ。紅葉期は朝霜が多く遊歩道が滑りやすい。"},
    {"zh-TW": "同 jp-001-P01。", "en": "Same as jp-001-P01.", "ja": "jp-001-P01 に同じ。"},
    "seasonal_plant", "seasonal_plant-v0.1",
    [cond(oid, "S1", "REQUIRED", "seasonal_state", "eq", "window_open", None, None, "MAIN", "computed", foliage_rat_aoiike),
     cond(oid, "02", "REQUIRED", "precipitation", "lt", 0.2, "mm", gfs("precipitation_rate_mm_h", "MID"), "MAIN", "formula_derived", SEASON_RAT["prec"]),
     cond(oid, "03", "REQUIRED", "wind_speed_10m", "lt", 5.0, "m/s", gfs("wind_speed_10m_m_s", "MID"), "MAIN", "formula_derived", SEASON_RAT["wind"]),
     light_window(oid)],
    500, SP3["jp-001"],
    "Subject existence web-verified 2026-11-08 (e-d34-c official autumn foliage; window climatological). Thresholds provisional."))

# ---------------- jp-012 ----------------
DAIBUTSU_GEOM = ("imported_from_v1_viewpoint_reference; CL-DATA-34 AI web verification 2026-11-08: "
                 "Kotoku-in hours 8:00-17:30 (Apr-Sep) / 8:00-17:00 (Oct-Mar) per Kanagawa Prefecture official "
                 "(e-d34-d); V1 point matches the Kotoku-in grounds at 35.317N 139.536E")
DAIBUTSU_ACCESS = {"zh-TW": "高德院全年無休 8:00–17:30（10–3 月至 17:00），閉門前 15 分停止入場；最上相的是開門後 8–10 時的正面斜光。", "en": "Kotoku-in is open year-round 8:00-17:30 (until 17:00 Oct-Mar), last entry 15 min before closing; the best light on the face is the frontal morning light 8:00-10:00 right after opening.", "ja": "高徳院は年中無休で8:00〜17:30（10〜3月は17:00）、閉門15分前まで入場可。8〜10時の開門直後の正面斜光が最も撮影に適する。"}
oid = "jp-012-P01"
CONTRACTS.append(make_contract(
    oid, "jp-012",
    {"zh-TW": "鎌倉大佛青銅全景", "en": "Kamakura Great Buddha bronze panorama", "ja": "鎌倉大仏の青銅全景"},
    {"zh-TW": "在山門內廣場拍鎌倉大佛青銅坐像全景：開門後的低角度斜光最能把 13.35 m 青銅面的立體感拍出來；全日可拍，避開正午頂光。",
     "en": "Shoot the full bronze seated figure from the courtyard inside the main gate: low-angle raking light just after opening brings out the relief of the 13.35 m bronze surface; shootable all day, avoid high noon.",
     "ja": "山門内の広場から、鎌倉大仏の青銅坐像の全景を撮る。開門直後の低角度の斜光が高さ13.35mの青銅面の立体感を最も引き出す。終日撮影可、真昼の頂光は避ける。"},
    (35.31685, 139.53572), "verified", DAIBUTSU_GEOM, DAIBUTSU_ACCESS,
    {"zh-TW": "廣場遊客多，腳架禮讓人流；胎內拝観另行收費。", "en": "The courtyard is crowded - keep tripods clear of foot traffic; the interior visit is a separate paid ticket.", "ja": "広場は人が多い。三脚は人流に配慮し、胎内拝観は別途有料。"},
    "golden_hour", "golden_hour-v0.1",
    [cond(oid, "01", "REQUIRED", "visibility", "gte", 8.0, "km", gfs("visibility_km", "MID"), "MAIN", "formula_derived", GOLD_RAT["vis"]),
     cond(oid, "02", "REQUIRED", "aod_550nm", "lte", 0.5, None, "dataset:cams_global|field:aerosol_optical_depth_550nm|role:AEROSOL", "MAIN", "formula_derived", GOLD_RAT["aod"]),
     cond(oid, "03", "REQUIRED", "precipitation", "lt", 0.2, "mm", gfs("precipitation_rate_mm_h", "MID"), "MAIN", "formula_derived", GOLD_RAT["prec"]),
     cond(oid, "04", "QUALITY", "golden_hour_window", "none", None, None, None, "MODIFIER", "computed", GOLD_RAT["gold"]),
     light_window(oid)],
    None, SP3["jp-012"],
    "Subject existence per V1 catalog; opening hours web-verified 2026-11-08 (e-d34-d official; e-d34-f). Thresholds provisional."))
koto_fol_rat = {"zh-TW": "季節窗判定（例年窗 11-20–12-10）：高德院境內銀杏與楓葉見頃為 11 月下旬–12 月上旬（享東京（enjoytokyo）刊載且經大佛殿高德院寺務所確認；大佛後方坡面的紅葉是代表取景點）。實況窗優先，兩者皆缺時誠實 not_evaluatable。",
                 "en": "Seasonal-window verdict (typical window 11-20 to 12-10): the ginkgo and maple in the Kotoku-in grounds peak from late November to early December (published with confirmation by the Kotoku-in temple office; the maple slope behind the Great Buddha is the representative vantage). Observed window takes precedence; with neither present, honestly not_evaluatable.",
                 "ja": "季節窓判定（例年窓11-20〜12-10）：高徳院境内のイチョウとカエデの見頃は11月下旬〜12月上旬（大仏殿高徳院寺務所確認済みの情報。大仏裏の紅葉の斜面が代表撮影点）。実況窓を優先し、両方なければ誠実にnot_evaluatable。"}
oid = "jp-012-P02"
CONTRACTS.append(make_contract(
    oid, "jp-012",
    {"zh-TW": "大佛秋楓", "en": "Great Buddha autumn foliage", "ja": "大仏と紅葉"},
    {"zh-TW": "11 月下旬至 12 月上旬，大佛背後坡面的楓葉與銀杏把青銅坐像襯出年度最出名的組合；從境內後方取景大佛與色葉同框。",
     "en": "From late November into early December, the maple and ginkgo behind the Great Buddha set the bronze seated figure in its most famous seasonal frame; shoot statue and foliage together from the rear of the grounds.",
     "ja": "11月下旬から12月上旬、大仏の後ろの斜面のカエデとイチョウが青銅坐像を最も有名な季節の構図で飾る。境内後方から大仏と色づいた葉を一枚に収める。"},
    (35.31685, 139.53572), "verified", DAIBUTSU_GEOM,
    {"zh-TW": "高德院全年無休 8:00–17:30（10–3 月至 17:00）；紅葉期人潮集中後方小丘，留意動線與腳架。", "en": "Kotoku-in is open year-round 8:00-17:30 (until 17:00 Oct-Mar); foliage crowds concentrate on the small rise behind the statue - mind the paths and tripods.", "ja": "高徳院は年中無休で8:00〜17:30（10〜3月は17:00）。紅葉期は後方の小高い丘に人が集中する。動線と三脚に注意。"},
    {"zh-TW": "同 jp-012-P01。", "en": "Same as jp-012-P01.", "ja": "jp-012-P01 に同じ。"},
    "seasonal_plant", "seasonal_plant-v0.1",
    [cond(oid, "S1", "REQUIRED", "seasonal_state", "eq", "window_open", None, None, "MAIN", "computed", koto_fol_rat),
     cond(oid, "02", "REQUIRED", "precipitation", "lt", 0.2, "mm", gfs("precipitation_rate_mm_h", "MID"), "MAIN", "formula_derived", SEASON_RAT["prec"]),
     cond(oid, "03", "REQUIRED", "wind_speed_10m", "lt", 5.0, "m/s", gfs("wind_speed_10m_m_s", "MID"), "MAIN", "formula_derived", SEASON_RAT["wind"]),
     light_window(oid)],
    None, SP3["jp-012"],
    "Subject existence web-verified 2026-11-08 (e-d34-e, temple-office confirmed window). Thresholds provisional."))

# ---------------- jp-014 ----------------
TODOROKI_GEOM = ("imported_from_v1_viewpoint_reference; CL-DATA-34 AI web verification 2026-11-08: "
                 "~1 km Yazawa River gorge, the only valley in Tokyo 23 wards, per Setagaya City official "
                 "(e-d34-g); V1 point sits on the valley boardwalk at 35.6079N 139.6465E")
oid = "jp-014-P01"
CONTRACTS.append(make_contract(
    oid, "jp-014",
    {"zh-TW": "等々力溪谷清流", "en": "Todoroki Valley stream in soft light", "ja": "等々力渓谷の清流"},
    {"zh-TW": "在谷澤川沿線步道拍溪流與綠蔭：溪谷底光線柔和，全雲天（總雲量 ≥70%）的漫射光讓流水絲絹化、綠色層次最豐。",
     "en": "Shoot the Yazawa stream and its green walls from the valley boardwalk: the gorge bottom wants soft light - full overcast (total cloud ≥70%) gives silky water and the richest greens.",
     "ja": "谷沢川沿いの遊歩道から渓流と緑の谷壁を撮る。谷底は柔らかい光が適し、全曇（全雲量70%以上）の拡散光が絹のような水流と最も豊かな緑を生む。"},
    (35.607857, 139.646545), "verified", TODOROKI_GEOM,
    {"zh-TW": "公園為自由出入的散步道，全日可拍；都會區晨間遊客少。", "en": "The park paths are free-access walking trails, shootable all day; early morning has few visitors even in the city.", "ja": "公園の遊歩道は自由に出入りでき終日撮影可。都市部でも早朝は人が少ない。"},
    {"zh-TW": "步道濕滑處多，雨天長曝注意鞋底與器材防水。", "en": "The boardwalk is often wet - mind footing in rain and waterproof your gear for long exposures.", "ja": "遊歩道は濡れやすい。雨天の長時間露出では足元と機材の防水に注意。"},
    "overcast_soft", "overcast_soft-v0.1",
    [cond(oid, "01", "REQUIRED", "cloud_cover_total", "gte", 70, "%", gfs("cloud_cover_total_percent", "MID"), "MAIN", "formula_derived",
          {"zh-TW": "溪谷底靠漫射光：全雲天的柔光讓流水絲絹化、綠葉不反白；直射日光會在谷底切成過亮/過暗兩半。", "en": "The gorge floor lives on diffused light: overcast softness turns the stream silky and keeps greens from blowing out; direct sun cuts the valley into blown/blocked halves.", "ja": "谷底は拡散光が命：全曇の柔光が水流を絹のようにし、緑を白飛びさせない。直射日光は谷底を白飛び/黒つぶれに分断する。"}),
     cond(oid, "02", "REQUIRED", "precipitation", "lt", 0.5, "mm", gfs("precipitation_rate_mm_h", "MID"), "MAIN", "formula_derived",
          {"zh-TW": "細雨仍可拍（流量增加反而好看），0.5 mm/h 以上影響器材與視線才否決。", "en": "Light rain is fine (added flow even helps); veto only above 0.5 mm/h when gear and sightlines suffer.", "ja": "小雨は可（流量増はむしろ好ましい）。0.5mm/h超で機材と視界に支障が出る場合のみ否決。"}),
     cond(oid, "03", "QUALITY", "wind_speed_10m", "lt", 5.0, "m/s", gfs("wind_speed_10m_m_s", "MID"), "MODIFIER", "formula_derived",
          {"zh-TW": "無風讓樹枝倒影與水流細節更完整，作為加分項。", "en": "Calm air keeps branch reflections and stream detail intact - a bonus.", "ja": "無風だと枝の映り込みと水流の細部が整う。加点項目。"}),
     light_window(oid)],
    None, SP3["jp-014"],
    "Subject existence web-verified 2026-11-08 (e-d34-g official). Thresholds provisional."))
todoroki_fol_rat = {"zh-TW": "季節窗判定（例年窗 11-20–12-05）：等々力溪谷秋葉見頃為東京都心的 11 月下旬–12 月上旬（世田谷區官方稱「秋の紅葉」未給日期，例年窗為氣候學估計）。實況窗優先，兩者皆缺時誠實 not_evaluatable。",
                     "en": "Seasonal-window verdict (typical window 11-20 to 12-05): Todoroki's foliage peaks in central Tokyo in late November to early December (Setagaya City official names the autumn color without dates; the typical window is climatological). Observed window takes precedence; with neither present, honestly not_evaluatable.",
                     "ja": "季節窓判定（例年窓11-20〜12-05）：等々力渓谷の紅葉見頃は都心部の11月下旬〜12月上旬（世田谷区公式は「秋の紅葉」と述べるが日程は不明、例年窓は気候学的推定）。実況窓を優先し、両方なければ誠実にnot_evaluatable。"}
oid = "jp-014-P02"
CONTRACTS.append(make_contract(
    oid, "jp-014",
    {"zh-TW": "等々力溪谷紅葉", "en": "Todoroki Valley autumn foliage", "ja": "等々力渓谷の紅葉"},
    {"zh-TW": "約 600 m 溪谷步道兩側山壁染紅，紅葉順著清流落入谷澤川；是東京 23 區內唯一的渓谷紅葉。",
     "en": "Both gorge walls along the ~600 m boardwalk turn red and the leaves ride the stream down the Yazawa - the only gorge foliage inside Tokyo's 23 wards.",
     "ja": "約600mの渓谷遊歩道の両側が紅に染まり、紅葉が谷沢川に流れる。東京23区唯一の渓谷紅葉。"},
    (35.607857, 139.646545), "verified", TODOROKI_GEOM,
    {"zh-TW": "紅葉期週末人多，早朝前往最穩。", "en": "Foliage weekends are busy - go early.", "ja": "紅葉期の週末は混む。早朝が狙い目。"},
    {"zh-TW": "同 jp-014-P01。", "en": "Same as jp-014-P01.", "ja": "jp-014-P01 に同じ。"},
    "seasonal_plant", "seasonal_plant-v0.1",
    [cond(oid, "S1", "REQUIRED", "seasonal_state", "eq", "window_open", None, None, "MAIN", "computed", todoroki_fol_rat),
     cond(oid, "02", "REQUIRED", "precipitation", "lt", 0.2, "mm", gfs("precipitation_rate_mm_h", "MID"), "MAIN", "formula_derived", SEASON_RAT["prec"]),
     cond(oid, "03", "REQUIRED", "wind_speed_10m", "lt", 5.0, "m/s", gfs("wind_speed_10m_m_s", "MID"), "MAIN", "formula_derived", SEASON_RAT["wind"]),
     light_window(oid)],
    None, SP3["jp-014"],
    "Subject existence web-verified 2026-11-08 (e-d34-g official gorge; e-d34-h foliage). Thresholds provisional."))

# ---------------- jp-015 ----------------
NIJU_GEOM = ("imported_from_v1_viewpoint_reference; CL-DATA-34 AI web verification 2026-11-08: "
             "Kokyo Gaien plaza area open at all times, free, no regular holidays, and the classic Nijubashi "
             "viewpoint is the Seimon Stone Bridge view across the moat (j-eps, e-d34-i); V1 point matches "
             "the Nijubashi viewing position at 35.678N 139.755E")
oid = "jp-015-P01"
CONTRACTS.append(make_contract(
    oid, "jp-015",
    {"zh-TW": "二重橋倒影", "en": "Nijubashi moat reflection", "ja": "二重橋と水面反射"},
    {"zh-TW": "從皇居前廣場正門石橋前拍二重橋（石橋＋鐵橋＋伏見櫓）與內堀水面倒影：無風清晨水鏡最完整，石垣與雙橋一併入鏡。",
     "en": "From the Kokyo Gaien plaza in front of the Seimon Stone Bridge, frame the double bridge (stone bridge, iron bridge, Fushimi-yagura) with its mirror in the inner moat: a windless early morning gives the complete reflection of stonework and both bridges.",
     "ja": "皇居前広場の正門石橋前から、二重橋（石橋・鉄橋・伏見櫓）と内堀の水面反射を撮る。無風の早朝が水鏡が最も完全で、石垣と二つの橋が一緒に写る。"},
    (35.678475, 139.754897), "verified", NIJU_GEOM,
    {"zh-TW": "皇居前廣場常時開放、免費、原則無休（國家行事/臨時管制除外）；晨間光線最順。", "en": "The Kokyo Gaien plaza is open at all times, free, and without regular holidays (except state events/temporary controls); morning gives the best light angle.", "ja": "皇居前広場は常時開放・無料・原則無休（国の行事・臨時規制を除く）。朝の光の角度が最も良い。"},
    {"zh-TW": "廣場碎石地面放穩腳架；護城河岸不得跨越。", "en": "The plaza gravel needs firm tripod footing; do not cross the moat edge.", "ja": "広場の砂利道では三脚を安定させ、堀の縁を越えないこと。"},
    "reflection", "reflection-v0.1",
    [cond(oid, "01", "REQUIRED", "wind_speed_10m", "lte", 2.0, "m/s", gfs("wind_speed_10m_m_s", "MID"), "MAIN", "formula_derived", REFLECTION_RAT["wind"]),
     cond(oid, "02", "REQUIRED", "water_surface_state", "none", None, None, None, "MAIN", "computed", REFLECTION_RAT["wsurface"]),
     cond(oid, "03", "REQUIRED", "precipitation", "lt", 0.2, "mm", gfs("precipitation_rate_mm_h", "MID"), "MAIN", "formula_derived", REFLECTION_RAT["prec"]),
     cond(oid, "04", "QUALITY", "cloud_cover_total", "between", [20, 60], "%", gfs("cloud_cover_total_percent", "MID"), "MODIFIER", "formula_derived", REFLECTION_RAT["cloud"]),
     light_window(oid)],
    None, SP3["jp-015"],
    "Subject existence per V1 catalog; viewpoint and access facts web-verified 2026-11-08 (e-d34-i). Thresholds provisional."))

pan15_rat = {"zh-TW": "皇居廣場的黑松與白石礫廣場在晨昏低角度光下立體感最強；東京的霧霾對 10 km 能見度門檻是實際約束。",
             "en": "The plaza's black pines and white gravel read best in low-angle dawn/dusk light; Tokyo haze makes the 10 km visibility gate a real constraint.",
             "ja": "広場の黒松と白い砂利は朝夕の低角度光で最も立体的に見える。東京のヘイズは視程10kmの門檻を現実的な制約にする。"}
oid = "jp-015-P02"
CONTRACTS.append(make_contract(
    oid, "jp-015",
    {"zh-TW": "皇居廣場全景", "en": "Kokyo Gaien plaza panorama", "ja": "皇居前広場の全景"},
    {"zh-TW": "從皇居前廣場中央拍白石礫廣場、黑松與遠處伏見櫓天際線；帶碎雲的晴天給全景最好的明暗節奏。",
     "en": "From the center of the Kokyo Gaien plaza, frame the white gravel field, black pines and the Fushimi-yagura skyline beyond; broken cloud on a fair day gives the panorama its best rhythm.",
     "ja": "皇居前広場の中央から、白い砂利の広場、黒松、遠くの伏見櫓のスカイラインを撮る。晴天空雲の日に全景の明暗リズムが最も良い。"},
    (35.678475, 139.754897), "verified", NIJU_GEOM,
    {"zh-TW": "同 jp-015-P01。", "en": "Same as jp-015-P01.", "ja": "jp-015-P01 に同じ。"},
    {"zh-TW": "同 jp-015-P01。", "en": "Same as jp-015-P01.", "ja": "jp-015-P01 に同じ。"},
    "mountain_view", "mountain_view-v0.1",
    [cond(oid, "01", "REQUIRED", "cloud_cover_mid", "between", [30, 60], "%", gfs("cloud_cover_mid_percent", "MID"), "MAIN", "formula_derived",
          {"zh-TW": "全景的「層」來自中雲帶：30–60% 的中層雲讓廣場—石垣—櫓的分層有明暗對比。", "en": "A vista's layering comes from mid-cloud bands: 30-60% mid-level cloud gives the plaza-stonework-turret stack its contrast.", "ja": "眺望の「層」は中層雲が作る：全雲量30〜60%の中層雲が広場・石垣・櫓の重なりに明暗の対比を与える。"}),
     cond(oid, "02", "REQUIRED", "visibility", "gte", 10.0, "km", gfs("visibility_km", "MID"), "MAIN", "formula_derived", PAN_RAT["vis"]),
     cond(oid, "03", "REQUIRED", "precipitation", "lt", 0.2, "mm", gfs("precipitation_rate_mm_h", "MID"), "MAIN", "formula_derived", GOLD_RAT["prec"]),
     cond(oid, "04", "QUALITY", "sunrise_time_window", "none", None, None, None, "MODIFIER", "computed", PAN_RAT["sunrise"]),
     light_window(oid)],
    None, SP3["jp-015"],
    "Subject existence per V1 catalog; plaza access web-verified 2026-11-08 (e-d34-i). Thresholds provisional."))

# ---------------- jp-017 ----------------
KEN_GEOM = ("imported_from_v1_viewpoint_reference; CL-DATA-34 AI web verification 2026-11-08: "
            "Kenrokuen winter hours 10-16..2-end 8:00-17:00 (last entry 16:30), yukitsuri hung from 11-01 and "
            "complete by mid-December (e-d34-j, e-d34-k quoting Ishikawa Prefecture); V1 point matches the "
            "garden center at 36.563N 136.663E")
KEN_ACCESS = {"zh-TW": "冬季（10/16–2 月底）8:00–17:00，最後入園 16:30；另有 11/1–2 月底 6:00–7:45 的早朝開園（免費，蓮池門口/隨身坂口），是清晨拍霞池的唯一時段。", "en": "Winter hours (Oct 16-end of Feb) 8:00-17:00, last entry 16:30; an early-morning opening 6:00-7:45 runs Nov 1-end of Feb (free, Hasuike-mon / Zuishigasaki gates only) - the only way to shoot Kasumiga-ike at dawn.", "ja": "冬季（10月16日〜2月末）は8:00〜17:00、最終入園16:30。別に11月1日〜2月末は6:00〜7:45の早朝開園（無料、蓮池門と随身坂口のみ）があり、朝の霞ヶ池撮影はこの時間だけ可能。"}
oid = "jp-017-P01"
yuki_rat = {"zh-TW": "季節窗判定（例年窗 12-15–02-25）：雪吊り 11 月初動工、12 月中旬全園掛完，雪景看積雪——例年 12 月中旬–2 月下旬（tripuuu/watabi 引石川縣官方）。實況窗優先，兩者皆缺時誠實 not_evaluatable。",
             "en": "Seasonal-window verdict (typical window 12-15 to 02-25): yukitsuri work starts early November and the whole garden is hung by mid-December; the snow scene needs actual snowfall - typical view mid-December to late February (sources quoting Ishikawa Prefecture). Observed window takes precedence; with neither present, honestly not_evaluatable.",
             "ja": "季節窓判定（例年窓12-15〜02-25）：雪吊りは11月初めに着手され12月中旬に全園で完成、雪景色は積雪次第——例年12月中旬〜2月下旬（石川県公式を引用する二次資料）。実況窓を優先し、両方なければ誠実にnot_evaluatable。"}
CONTRACTS.append(make_contract(
    oid, "jp-017",
    {"zh-TW": "兼六園雪吊冬景", "en": "Kenrokuen yukitsuri snow scene", "ja": "兼六園の雪吊り冬景"},
    {"zh-TW": "12 月中旬到 2 月下旬，唐崎松雪吊與徽軫燈籠的冬景是兼六園的招牌；積雪日整座園化為雪白世界，霞池倒影最上相。",
     "en": "From mid-December to late February, the yukitsuri ropes over the Karasaki pine and the Kotoji lantern are Kenrokuen's signature winter scene; on snowy days the whole garden turns white and the Kasumiga-ike reflection is at its best.",
     "ja": "12月中旬から2月下旬、唐崎松の雪吊りと徽軫灯籠の冬景色が兼六園の看板。雪の日には園全体が雪景色となり、霞ヶ池の反射が最も美しい。"},
    (36.563367, 136.662817), "verified", KEN_GEOM, KEN_ACCESS,
    {"zh-TW": "園內石板路雪凍濕滑，务必穿防滑鞋；腳架依園方規定。", "en": "The stone paths freeze and get slippery - wear grippy soles; follow the garden's tripod rules.", "ja": "園内の石畳は凍結して滑りやすい。滑り止めの靴を履き、三脚は園の規定に従う。"},
    "snow_ice", "snow_ice-v0.1",
    [cond(oid, "S1", "REQUIRED", "seasonal_state", "eq", "window_open", None, None, "MAIN", "computed", yuki_rat),
     cond(oid, "02", "REQUIRED", "visibility", "gte", 3.0, "km", gfs("visibility_km", "MID"), "MAIN", "formula_derived",
          {"zh-TW": "雪吊線條是主體，大雪片/濃霧會把繩索細節完全吃掉（≥3 km 才保得住線條）。", "en": "The yukitsuri rope lines are the subject - heavy snowflakes or fog swallow their detail entirely (≥3 km keeps the lines readable).", "ja": "雪吊りの紐の線が主題。雪片や濃霧はその細部を完全に飲み込む（3km以上で線が読める）。"}),
     cond(oid, "03", "REQUIRED", "wind_speed_10m", "lte", 15.0, "m/s", gfs("wind_speed_10m_m_s", "MID"), "MAIN", "formula_derived",
          {"zh-TW": "暴風雪否決（繩索積雪被吹落且無法拍攝）。", "en": "Blizzard conditions veto (snow is blown off the ropes and shooting becomes impossible).", "ja": "吹雪は否決（紐の雪が飛ばされ撮影不可能）。"}),
     light_window(oid)],
    None, SP3["jp-017"],
    "Subject existence web-verified 2026-11-08 (e-d34-j/e-d34-k). Thresholds provisional."))

oid = "jp-017-P02"
CONTRACTS.append(make_contract(
    oid, "jp-017",
    {"zh-TW": "霞池晨光倒影", "en": "Kasumiga-ike morning reflection", "ja": "霞ヶ池の朝の反射"},
    {"zh-TW": "霞池與徽軫燈籠的水面倒影：早朝開園（11/1–2 月底 6:00–7:45 免費）時段水靜人稀，是園內倒影最乾淨的窗口；無早朝開園的季節以開園後清晨為主。",
     "en": "The water mirror of Kasumiga-ike and the Kotoji lantern: during the early-morning opening (6:00-7:45 free, Nov 1-end of Feb) the pond is still and empty - the garden's cleanest reflection window; outside that season, right after the regular opening.",
     "ja": "霞ヶ池と徽軫灯籠の水鏡。早朝開園（11月1日〜2月末の6:00〜7:45、無料）の時間帯は水面が静かで人が少なく、園内で最も澄んだ反射の窓。それ以外の季節は通常開園直後が狙い目。"},
    (36.563367, 136.662817), "verified", KEN_GEOM,
    {"zh-TW": "冬季（10/16–2 月底）8:00–17:00，最後入園 16:30；早朝開園僅蓮池門口與隨身坂口入園。", "en": "Winter hours (Oct 16-end of Feb) 8:00-17:00, last entry 16:30; the early-morning opening admits through the Hasuike-mon and Zuishigasaki gates only.", "ja": "冬季（10月16日〜2月末）は8:00〜17:00、最終入園16:30。早朝開園は蓮池門と随身坂口のみの入園。"},
    {"zh-TW": "池畔石板濕滑，晨霜期注意腳下。", "en": "The pond-side stones are slippery - mind morning frost.", "ja": "池畔の石畳は滑りやすい。朝霜に注意。"},
    "reflection", "reflection-v0.1",
    [cond(oid, "01", "REQUIRED", "wind_speed_10m", "lte", 2.0, "m/s", gfs("wind_speed_10m_m_s", "MID"), "MAIN", "formula_derived", REFLECTION_RAT["wind"]),
     cond(oid, "02", "REQUIRED", "water_surface_state", "none", None, None, None, "MAIN", "computed", REFLECTION_RAT["wsurface"]),
     cond(oid, "03", "REQUIRED", "precipitation", "lt", 0.2, "mm", gfs("precipitation_rate_mm_h", "MID"), "MAIN", "formula_derived", REFLECTION_RAT["prec"]),
     cond(oid, "04", "QUALITY", "cloud_cover_total", "between", [20, 60], "%", gfs("cloud_cover_total_percent", "MID"), "MODIFIER", "formula_derived", REFLECTION_RAT["cloud"]),
     light_window(oid)],
    None, SP3["jp-017"],
    "Subject existence web-verified 2026-11-08 (e-d34-j early-morning opening). Thresholds provisional."))

# ---------------- jp-018 ----------------
NAGOYA_GEOM = ("imported_from_v1_viewpoint_reference; CL-DATA-34 AI web verification 2026-11-08: "
               "Nagoya Castle grounds 9:00-16:30 (closed 17:00) per Nagoya City official tourism (e-d34-m); "
               "keep exterior illuminated every day sunset-23:00 per Nagoya Castle official FAQ (e-d34-l); "
               "V1 point matches the castle grounds at 35.185N 136.899E")
oid = "jp-018-P01"
CONTRACTS.append(make_contract(
    oid, "jp-018",
    {"zh-TW": "名古屋城天守全景", "en": "Nagoya Castle keep panorama", "ja": "名古屋城天守の全景"},
    {"zh-TW": "從本丸廣場拍名古屋城大天守（5 層 5 階、頂高 55.6 m）與金鯱：全日可拍，避開正午頂光，晨昏斜光最能把石垣與白壁拍出立體感。",
     "en": "From the Honmaru plaza, frame the Nagoya Castle great keep (5 stories, roof top 55.6 m) with its golden shachihoko: shootable all day but avoid high noon - raking dawn/dusk light gives the stone base and white walls their relief.",
     "ja": "本丸広場から名古屋城の大天守（5重5階、屋頂高さ55.6m）と金の鯱を撮る。終日撮影可だが真昼の頂光は避け、朝夕の斜光が石垣と白壁の立体感を最も引き出す。"},
    (35.185181, 136.89865), "verified", NAGOYA_GEOM,
    {"zh-TW": "城區開放 9:00–16:30（閉門 17:00），天守閣現階段內部不開放；夜間點燈在園外周邊可見（見 jp-018-P02）。", "en": "The grounds open 9:00-16:30 (close 17:00) and the keep interior is currently closed; the nightly illumination is visible from around the closed grounds (see jp-018-P02).", "ja": "城内は9:00〜16:30（閂門17:00）で、天守閣内部は現在不公開。夜間の照明は城外周辺から見える（jp-018-P02 を参照）。"},
    {"zh-TW": "廣場遊客多，腳架禮讓。", "en": "Busy plaza - keep tripods clear of foot traffic.", "ja": "広場は人が多い。三脚は人流に配慮。"},
    "golden_hour", "golden_hour-v0.1",
    [cond(oid, "01", "REQUIRED", "visibility", "gte", 8.0, "km", gfs("visibility_km", "MID"), "MAIN", "formula_derived", GOLD_RAT["vis"]),
     cond(oid, "02", "REQUIRED", "aod_550nm", "lte", 0.5, None, "dataset:cams_global|field:aerosol_optical_depth_550nm|role:AEROSOL", "MAIN", "formula_derived", GOLD_RAT["aod"]),
     cond(oid, "03", "REQUIRED", "precipitation", "lt", 0.2, "mm", gfs("precipitation_rate_mm_h", "MID"), "MAIN", "formula_derived", GOLD_RAT["prec"]),
     cond(oid, "04", "QUALITY", "golden_hour_window", "none", None, None, None, "MODIFIER", "computed", GOLD_RAT["gold"]),
     light_window(oid)],
    None, SP3["jp-018"],
    "Subject existence per V1 catalog; hours web-verified 2026-11-08 (e-d34-m official). Thresholds provisional."))

oid = "jp-018-P02"
CONTRACTS.append(make_contract(
    oid, "jp-018",
    {"zh-TW": "名古屋城夜間點燈", "en": "Nagoya Castle night illumination", "ja": "名古屋城の夜間ライトアップ"},
    {"zh-TW": "名古屋城天守外觀每日日没後點燈至 23:00（官方 FAQ），從城外周邊可見金色天守夜空剪影；本契約以夜間窗判定，園內夜間不開放、請在園外取景。",
     "en": "The Nagoya Castle keep exterior is lit every night from sunset until 23:00 (official FAQ) and the golden keep reads against the night sky from around the closed grounds; this contract judges by the night window - the grounds themselves are not open at night, so shoot from outside.",
     "ja": "名古屋城の天守外観は毎日日没から23:00までライトアップされる（公式FAQ）。城外周辺から金の天守が夜空に浮かぶ。本契約は夜間窓で判定し、城内は夜間不开放のため城外から撮る。"},
    (35.185181, 136.89865), "verified", NAGOYA_GEOM,
    {"zh-TW": "夜間城區不開放；從外堀外側與周邊道路取景，遵守夜間規定。", "en": "The grounds are closed at night; shoot from outside the outer moat and nearby streets, following nighttime rules.", "ja": "夜間は城内不开放。外堀の外側と周辺道路から撮り、夜間のルールを守ること。"},
    {"zh-TW": "夜間周邊道路車流多，勿站車道拍攝。", "en": "Nighttime traffic around the castle is heavy - never shoot from the roadway.", "ja": "夜間は周辺道路の車流が多い。車道に立って撮影しないこと。"},
    "city_night", "city_night-v0.1",
    [cond(oid, "01", "REQUIRED", "cloud_cover_total", "lte", 30, "%", gfs("cloud_cover_total_percent", "MID"), "MAIN", "formula_derived", NIGHT_RAT["cloud"]),
     cond(oid, "02", "REQUIRED", "visibility", "gte", 10.0, "km", gfs("visibility_km", "MID"), "MAIN", "formula_derived", NIGHT_RAT["vis"]),
     cond(oid, "03", "REQUIRED", "precipitation", "lt", 0.2, "mm", gfs("precipitation_rate_mm_h", "MID"), "MAIN", "formula_derived", NIGHT_RAT["prec"]),
     cond(oid, "04", "REQUIRED", "aod_550nm", "lte", 0.5, None, "dataset:cams_global|field:aerosol_optical_depth_550nm|role:AEROSOL", "MAIN", "formula_derived", NIGHT_RAT["aod"]),
     cond(oid, "05", "REQUIRED", "city_night_window", "none", None, None, None, "MAIN", "computed",
          {"zh-TW": "夜間窗判定：官方 FAQ 載明天守外觀每日日没點燈至 23:00（每月 8 日 21:30），評估以民用黑暗（太陽仰角 ≤ −6°）的整點桶判定，與官方點燈時段重疊。", "en": "Night-window verdict: the official FAQ states the keep exterior is lit daily from sunset to 23:00 (21:30 on the 8th of each month); the evaluation gates on whole-hour buckets in civil darkness (sun elevation <= -6 deg), which overlap the official illumination hours.", "ja": "夜間窓判定：公式FAQによると天守外観は毎日日没から23:00まで点灯（毎月8日は21:30）。評価は市民的暗闇（太陽高度-6°以下）の単位時間で判定し、公式の点灯時間帯と重なる。"}),
     ],
    None, SP3["jp-018"],
    "Subject existence web-verified 2026-11-08 (e-d34-l official FAQ; e-d34-m grounds hours). Thresholds provisional."))

# ---------------- jp-024 ----------------
OSAKA_GEOM = ("imported_from_v1_viewpoint_reference; CL-DATA-34 AI web verification 2026-11-08: "
              "Osaka Castle keep illumination daily sunset-24:30 per Osaka Castle official FAQ (e-d34-n); "
              "park free and effectively open at all times with the illuminated keep viewed from around "
              "Gokuraku-bashi / inner moat (e-d34-o); V1 point matches the park at 34.689N 135.527E")
oid = "jp-024-P01"
CONTRACTS.append(make_contract(
    oid, "jp-024",
    {"zh-TW": "大阪城天守夜間點燈", "en": "Osaka Castle keep night illumination", "ja": "大阪城天守の夜間ライトアップ"},
    {"zh-TW": "大阪城天守每日日没後點燈至 24:30（官方 FAQ，年僅一日檢修），從公園內極樂橋與內堀周邊可見金色天守；公園 24 小時可入園。",
     "en": "The Osaka Castle keep is lit every night from sunset until 24:30 (official FAQ; one annual inspection night is dark) and the golden keep reads from Gokuraku-bashi and around the inner moat inside the 24-hour park.",
     "ja": "大阪城天守は毎日日没から24:30までライトアップ（公式FAQ、年1回の点検日のみ消灯）。公園は24時間入園でき、極楽橋と内堀周辺から金の天守が見える。"},
    (34.6892, 135.52675), "verified", OSAKA_GEOM,
    {"zh-TW": "公園全日開放（天守閣等收費設施另計）；夜間步道照明有限，走亮處。", "en": "The park is open at all hours (paid facilities like the keep museum are separate); night paths are dimly lit - keep to the lit routes.", "ja": "公園は終日入園可（天守閣などの有料施設は別）。夜間の園路は暗いので明るい道を選ぶ。"},
    {"zh-TW": "夜間園內人少，留意隨身財物與腳下。", "en": "The park is quiet at night - mind your belongings and footing.", "ja": "夜間は園内が静か。所持品と足元に注意。"},
    "city_night", "city_night-v0.1",
    [cond(oid, "01", "REQUIRED", "cloud_cover_total", "lte", 30, "%", gfs("cloud_cover_total_percent", "MID"), "MAIN", "formula_derived", NIGHT_RAT["cloud"]),
     cond(oid, "02", "REQUIRED", "visibility", "gte", 10.0, "km", gfs("visibility_km", "MID"), "MAIN", "formula_derived", NIGHT_RAT["vis"]),
     cond(oid, "03", "REQUIRED", "precipitation", "lt", 0.2, "mm", gfs("precipitation_rate_mm_h", "MID"), "MAIN", "formula_derived", NIGHT_RAT["prec"]),
     cond(oid, "04", "REQUIRED", "aod_550nm", "lte", 0.5, None, "dataset:cams_global|field:aerosol_optical_depth_550nm|role:AEROSOL", "MAIN", "formula_derived", NIGHT_RAT["aod"]),
     cond(oid, "05", "REQUIRED", "city_night_window", "none", None, None, None, "MAIN", "computed",
          {"zh-TW": "夜間窗判定：官方 FAQ 載明天守每日日没點燈至 24:30（日没後約 1 小時漸亮），評估以民用黑暗整點桶判定，與官方點燈時段重疊。", "en": "Night-window verdict: the official FAQ states the keep is lit daily from sunset to 24:30 (ramping up over ~1 h after sunset); the evaluation gates on whole-hour buckets in civil darkness, which overlap the official illumination hours.", "ja": "夜間窓判定：公式FAQによると天守は毎日日没から24:30まで点灯（日没後約1時間かけて漸次点灯）。評価は市民的暗闇の単位時間で判定し、公式の点灯時間帯と重なる。"}),
     ],
    None, SP3["jp-024"],
    "Subject existence web-verified 2026-11-08 (e-d34-n official FAQ; e-d34-o park/viewpoints). Thresholds provisional."))

oid = "jp-024-P02"
CONTRACTS.append(make_contract(
    oid, "jp-024",
    {"zh-TW": "大阪城天守倒影", "en": "Osaka Castle keep moat reflection", "ja": "大阪城天守の堀の反射"},
    {"zh-TW": "從內堀岸邊拍天守與水面倒影：晨間水面最靜，石垣與白壁連同倒影完整入鏡；夕刻順光位在公園西側。",
     "en": "From the inner-moat bank, frame the keep with its mirror in the water: early morning has the calmest surface and the stonework plus white walls reflect whole; the evening front-light position is on the park's west side.",
     "ja": "内堀の岸から天守と水面反射を撮る。早朝の水面が最も静かで、石垣と白壁が完全に映り込む。夕暮れの順光位は公園西側。"},
    (34.6892, 135.52675), "verified", OSAKA_GEOM,
    {"zh-TW": "內堀沿線步道自由通行；拍攝點依現場公告。", "en": "The inner-moat paths are freely walkable; follow on-site notices for shooting points.", "ja": "内堀沿いの遊歩道は自由に通行可。撮影点は現地の告知に従う。"},
    {"zh-TW": "堀岸濕滑，切勿跨越欄杆取景。", "en": "Moat banks are slippery - never cross the railings for a shot.", "ja": "堀の縁は滑りやすい。欄干を越えて撮影しないこと。"},
    "reflection", "reflection-v0.1",
    [cond(oid, "01", "REQUIRED", "wind_speed_10m", "lte", 2.0, "m/s", gfs("wind_speed_10m_m_s", "MID"), "MAIN", "formula_derived", REFLECTION_RAT["wind"]),
     cond(oid, "02", "REQUIRED", "water_surface_state", "none", None, None, None, "MAIN", "computed", REFLECTION_RAT["wsurface"]),
     cond(oid, "03", "REQUIRED", "precipitation", "lt", 0.2, "mm", gfs("precipitation_rate_mm_h", "MID"), "MAIN", "formula_derived", REFLECTION_RAT["prec"]),
     cond(oid, "04", "QUALITY", "cloud_cover_total", "between", [20, 60], "%", gfs("cloud_cover_total_percent", "MID"), "MODIFIER", "formula_derived", REFLECTION_RAT["cloud"]),
     light_window(oid)],
    None, SP3["jp-024"],
    "Subject existence per V1 catalog; park/moat facts web-verified 2026-11-08 (e-d34-o). Thresholds provisional."))

# ---------------- write ----------------
os.makedirs(ROOT / 'data/v2/audits', exist_ok=True)
with open(ROOT / 'data/v2/audits/cl-data-34_web_evidence.json', 'w', encoding='utf-8') as f:
    json.dump(EVIDENCE, f, ensure_ascii=False, indent=1)

for c in CONTRACTS:
    p = OPS / f"{c['opportunity_id']}.json"
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(c, f, ensure_ascii=False, indent=1, sort_keys=False)
    print('wrote', p.name)

# ---------------- seasonal calendar entries ----------------
cal_path = ROOT / 'data/v2/seasonal-calendar.json'
cal = json.load(open(cal_path, encoding='utf-8'))
EXIST = {e['plant_id'] for e in cal['entries']}
NEW_ENTRIES = [
    {"plant_id": "aoiike_foliage", "spots": ["jp-001-P02"], "name_i18n": {"zh-TW": "青池秋色", "en": "Blue Pond autumn foliage", "ja": "青い池の紅葉"},
     "typical_window": {"start": "10-05", "end": "10-31"},
     "sources": [{"url": "https://www.visit-hokkaido.jp/spot/detail_10511.html", "kind": "official",
                   "note_i18n": {"zh-TW": "HOKKAIDO LOVE! 官方載明秋季紅葉與青池對比，未給日期；例年窗為氣候學估計（CL-DATA-34）", "en": "HOKKAIDO LOVE! official names the autumn-foliage contrast without dates; typical window is climatological (CL-DATA-34)", "ja": "HOKKAIDO LOVE! 公式は秋の紅葉とのコントラストを記載するが日程は不明。例年窓は気候学的推定（CL-DATA-34）"}}]},
    {"plant_id": "kotokuin_foliage", "spots": ["jp-012-P02"], "name_i18n": {"zh-TW": "大佛秋楓", "en": "Great Buddha autumn foliage", "ja": "大仏と紅葉"},
     "typical_window": {"start": "11-20", "end": "12-10"},
     "sources": [{"url": "https://www.enjoytokyo.jp/article/205020/", "kind": "official_forecast_note",
                   "note_i18n": {"zh-TW": "高德院紅葉見頃 11 月下旬–12 月上旬（情報提供・確認元：大仏殿高德院寺務所；CL-DATA-34）", "en": "Kotoku-in foliage peaks late Nov to early Dec (information provided/confirmed by the Kotoku-in temple office; CL-DATA-34)", "ja": "高徳院の紅葉見頃は11月下旬〜12月上旬（情報提供・確認元：大仏殿高徳院寺務所、CL-DATA-34）"}}]},
    {"plant_id": "todoroki_foliage", "spots": ["jp-014-P02"], "name_i18n": {"zh-TW": "等々力溪谷紅葉", "en": "Todoroki Valley autumn foliage", "ja": "等々力渓谷の紅葉"},
     "typical_window": {"start": "11-20", "end": "12-05"},
     "sources": [{"url": "https://www.city.setagaya.lg.jp/02075/9082.html", "kind": "official",
                   "note_i18n": {"zh-TW": "世田谷區官方載明溪谷秋景（未給日期）；例年窗為東京都心氣候學估計（CL-DATA-34）", "en": "Setagaya City official names the gorge's autumn scenery without dates; typical window is a central-Tokyo climatological estimate (CL-DATA-34)", "ja": "世田谷区公式は渓谷の秋景色を記載するが日程は不明。例年窓は都心部の気候学的推定（CL-DATA-34）"}}]},
    {"plant_id": "kenrokuen_yukitsuri", "spots": ["jp-017-P01"], "name_i18n": {"zh-TW": "兼六園雪吊り", "en": "Kenrokuen yukitsuri", "ja": "兼六園の雪吊り"},
     "typical_window": {"start": "12-15", "end": "02-25"},
     "sources": [{"url": "https://log.tripuuu.com/zh-hant/snow-scenery/chubu/kenrokuen-yukitsuri", "kind": "official_note",
                   "note_i18n": {"zh-TW": "雪吊り 12 月中旬完成、至拆除前可見（引石川縣官方作業時程；CL-DATA-34）", "en": "Yukitsuri complete by mid-December and stand until spring removal (Ishikawa Prefecture work schedule via secondary source; CL-DATA-34)", "ja": "雪吊りは12月中旬に完成し、取り外しまで見られる（石川県の作業時程を引用する二次資料、CL-DATA-34）"}}]},
]
added = []
for e in NEW_ENTRIES:
    if e['plant_id'] not in EXIST:
        cal['entries'].append(e)
        added.append(e['plant_id'])
with open(cal_path, 'w', encoding='utf-8') as f:
    json.dump(cal, f, ensure_ascii=False, indent=1)
print('calendar entries added:', added)
print('total contracts:', len(CONTRACTS))
