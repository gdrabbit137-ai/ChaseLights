#!/usr/bin/env python3
"""CL-DATA-74 stage 2: mount the five owner-approved genres (alpenglow /
snow_scene / firefly / star_trails / moonlit_scene) onto existing catalog
places. Creates the 17 canonical opportunity docs (cloning a same-place
sibling for verified geometry/evidence structure), appends the
seasonal-calendar windows (snow / firefly) and the curation classifications.

Usage: python cl_data_74_mount.py            # write everything
       python cl_data_74_mount.py --dry-run  # report only
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OPPS = ROOT / "data/v2/opportunities"
TEMPLATES = ROOT / "data/v2/templates"
TICKET = "CL-DATA-74"

# oid -> (genre, sibling_oid, zh name, en name, ja name, zh desc, en desc, ja desc)
MOUNTS = [
    ("tw-041-P06", "alpenglow", "tw-041-P05",
     "雪山主峰日照金山", "Sunset alpenglow on Snow Mountain", "雪山主峰のアルペングロー",
     "日沒後的暖光帶把雪山主峰與一號圈谷雪面染成金紅（僅雪季成立）：主峰展望面朝西，落日直射消失後的反射光在雪面上最強；需要峰頂無雲與觀點視線淨空。",
     "The warm band just after sunset lights the Snow Mountain summit and Cirque I snow face gold-red (snow season only): the westward summit viewpoint catches the strongest reflected light once the direct disc is gone; needs a cloudless summit and a clear sightline.",
     "日没直後の暖光帯が雪山主峰と一号圏谷の雪面を金赤に染める（雪季のみ）：西向きの主峰展望は直射が沈んだ後の反射光が最も強く、山頂無雲と視線の透明度を要す。"),
    ("tw-042-P02", "alpenglow", "tw-042-P01",
     "雪山北峰聖稜線日照金山", "Alpenglow on the Holy Ridge from Snow North Peak", "雪山北峰・聖稜線のアルペングロー",
     "日沒後金山光帶沿聖稜線（北稜角—雪山北峰—凱蘭特崑山）逐峰點亮：北峰展望正對聖稜線主軸，雪季時稜線雪面依序轉金；峰頂無雲與視線淨空為必要。",
     "Just after sunset the alpenglow band lights the Holy Ridge (North Corner - Snow North Peak - Kalantai) peak by peak: the North Peak viewpoint faces the ridge axis dead-on, and in snow season the snow faces turn gold in sequence; a clear summit and sightline are required.",
     "日没直後のアルペングローが聖稜線（北稜角—雪山北峰—カランタスン）を峰ごとに照らす：北峰展望は稜線の主軸を正面に捉え、雪季には雪面が順に金色に変わる。山頂無雲と視線の透明度が必須。"),
    ("tw-044-P04", "alpenglow", "tw-044-P03",
     "南湖主峰日照金山", "Sunset alpenglow on Nanhudashan", "南湖主峰のアルペングロー",
     "日沒後暖光打亮南湖大山主峰與陶塞峰雪面（僅雪季成立）：南湖圈谷展望朝西望主峰雙峰；峰頂無雲與視線淨空為必要。",
     "The warm band just after sunset lights the Nanhudashan main summit and Taoshi face (snow season only): the cirque viewpoint faces the twin west-summits; a clear summit and sightline are required.",
     "日没直後の暖光が南湖大山主峰と陶塞峰の雪面を染める（雪季のみ）：圏谷展望は西の双峰を正面に捉える。山頂無雲と視線の透明度が必須。"),
    ("tw-046-P03", "alpenglow", "tw-046-P02",
     "大霸尖山日照金山", "Alpenglow on Dabajian Mountain", "大霸尖山のアルペングロー",
     "日沒後金山光帶把大霸尖山酒桶狀峰體與霸基雪面染成金紅（僅雪季成立）：中霸坪展望正對大霸西壁；峰頂無雲與視線淨空為必要。",
     "Just after sunset the alpenglow band turns the barrel-shaped Dabajian summit and its base snow face gold-red (snow season only): the Zhongbaping viewpoint faces the west wall dead-on; a clear summit and sightline are required.",
     "日没直後のアルペングローが大霸尖山の桶状峰体と基盤の雪面を金赤に染める（雪季のみ）：中霸坪展望は西壁を正面に捉える。山頂無雲と視線の透明度が必須。"),
    ("jp-065-P02", "alpenglow", "jp-065-P01",
     "富士山頂サンセットアルペングロー", "Sunset alpenglow on Mt. Fuji summit", "富士山頂のサンセットアルペングロー",
     "日沒後暖光帶打亮剣ヶ峰雪面（僅雪季成立）：山頂展望在日沒瞬間看峰緣由金轉紅；日語圈「マッキノー（山暉き）」現象；峰頂無雲與視線淨空為必要。",
     "The warm band just after sunset lights the Kengamine snow face (snow season only): from the summit viewpoint the crater rim turns gold then red at sunset - the Japanese 'Mackinaw' (yamagai) phenomenon; a clear summit and sightline are required.",
     "日没直後の暖光帯が剣ヶ峰の雪面を染める（雪季のみ）：山頂展望は日没の瞬間、火口縁が金から赤へ変わるのを見る（山暉き）。山頂無雲と視線の透明度が必須。"),
    ("tw-019-P07", "snow_scene", "tw-019-P06",
     "合歡主峰雪景", "Snow scene at Hehuan Main Peak", "合歓主峰の雪景色",
     "雪季的合歡主峰：步道與觀景台積雪、箭竹草原披雪、群峰稜線雪白——雪季窗內、地面有雪（降雪中或積雪）、氣溫≤1°C 且能見度≥3km（暴雪白牆否決）時成立。",
     "Hehuan Main Peak in snow season: snow-covered trail and viewing platform, frosted yushan grass, white peak ridges - qualifies inside the snow-season window with ground snow (falling or lying), air temp <= 1 C and visibility >= 3 km (blizzard/whiteout vetoes).",
     "雪季の合歓主峰：歩道と展望台の積雪、ススキ草原の雪、白い稜線 — 雪季窓内で地面に雪（降雪中か積雪）、気温 ≤1°C、視程 ≥3 km（吹雪・ホワイトアウトは否決）のとき成立。"),
    ("tw-120-P02", "snow_scene", "tw-120-P01",
     "武陵農場雪景", "Snow scene at Wuling Farm", "武陵農場の雪景色",
     "雪季寒流過境的武陵農場：七家灣溪畔與雪峰群（桃山/雪山北稜）積雪、果園披雪；雪季窗內地面有雪、氣溫≤1°C、能見度≥3km 時成立。",
     "Wuling Farm after a cold snap in snow season: snow along the Chijiawan Creek and on the peak line (Taoshan / Snow North ridge), frosted orchards - qualifies inside the snow-season window with ground snow, temp <= 1 C, visibility >= 3 km.",
     "雪季の寒波通過後の武陵農場：七家湾渓沿いとピークライン（桃山/雪山北稜）の積雪、果樹園の雪 — 雪季窓内で地面に雪、気温 ≤1°C、視程 ≥3 km のとき成立。"),
    ("tw-093-P03", "snow_scene", "tw-093-P02",
     "福壽山農場雪景", "Snow scene at Fushoushan Farm", "福寿山農場の雪景色",
     "雪季寒流過境的福壽山農場：茶園與果園步道積雪、遠望合歡群峰雪稜；雪季窗內地面有雪、氣溫≤1°C、能見度≥3km 時成立。",
     "Fushoushan Farm after a cold snap in snow season: snow on the tea terraces and orchard paths, the Hehuan ridgeline white in the distance - qualifies inside the snow-season window with ground snow, temp <= 1 C, visibility >= 3 km.",
     "雪季の寒波通過後の福寿山農場：茶園と果樹園の歩道の積雪、遠くの合歓稜線の雪 — 雪季窓内で地面に雪、気温 ≤1°C、視程 ≥3 km のとき成立。"),
    ("jp-065-P03", "snow_scene", "jp-065-P01",
     "富士山頂雪景", "Snow scene on Mt. Fuji summit", "富士山頂の雪景色",
     "雪季的富士山頂剣ヶ峰：火口緣與剣ヶ峰積雪、御來館方向的雪簷；雪季窗內（含五合目以上雪線）地面有雪、氣溫≤1°C、能見度≥3km 時成立。",
     "Mt. Fuji summit (Kengamine) in snow season: snow on the crater rim and Kengamine, snow cornices on the hut row - qualifies inside the snow-season window (snow line above the 5th station) with ground snow, temp <= 1 C, visibility >= 3 km.",
     "雪季の富士山頂剣ヶ峰：火口縁と剣ヶ峰の積雪、山小屋の雪庇 — 雪季窓内（五合目以上の雪線を含む）で地面に雪、気温 ≤1°C、視程 ≥3 km のとき成立。"),
    ("us-009-P02", "snow_scene", "us-009-P01",
     "Tunnel View Yosemite Valley snow scene", "Tunnel View Yosemite Valley snow scene", "トンネルビュー・ヨセミテ渓谷の雪景色",
     "雪季寒流過境的優勝美地隧道觀景臺：Valley floor、El Capitan 與 Bridalveil Falls 披雪的經典全景；雪季窗內地面有雪、氣溫≤1°C、能見度≥3km 時成立。",
     "Tunnel View after a cold snap in snow season: the classic panorama with the Valley floor, El Capitan and Bridalveil Falls under snow - qualifies inside the snow-season window with ground snow, temp <= 1 C, visibility >= 3 km.",
     "雪季の寒波通過後のトンネルビュー：渓谷底・エル・キャピタン・ブライダルベール滝が雪を被る定番パノラマ — 雪季窓内で地面に雪、気温 ≤1°C、視程 ≥3 km のとき成立。"),
    ("tw-151-P02", "firefly", "tw-151-P01",
     "內洞溪谷螢火蟲", "Fireflies in the Neidong stream valley", "内洞渓谷のホタル",
     "螢季（4–6月）的內洞國家森林遊樂區：南勢溪支流溪谷與森林步道的螢火蟲夜——無月（月照≤30% 或月下）、高濕≥85%、氣溫≥15°C、無雨、天文暗夜窗時成立；低海拔溪谷森林語義。",
     "Firefly nights along the tributary stream valley and forest boardwalks of Neidong Forest Recreation Area in the season window (Apr-Jun): needs a moonless night (illumination <= 30% or moon below the horizon), humidity >= 85%, temp >= 15 C, no rain and astronomical darkness; low-altitude stream-forest semantics.",
     "螢季（4〜6月）の内洞国家森林遊楽区：支流渓谷と森林歩道のホタルの夜 — 無月（月照 ≤30% か月没）、湿度 ≥85%、気温 ≥15°C、無雨、天文暗の夜窓が必要。低標高渓谷・森林の語義。"),
    ("tw-144-P03", "firefly", "tw-144-P02",
     "東眼山森林螢火蟲", "Fireflies in Dongyanshan forest", "東眼山の森のホタル",
     "螢季（4–6月）的東眼山國家森林遊樂區：柳杉林緣與步道兩側的螢火蟲夜——無月、高濕≥85%、氣溫≥15°C、無雨、天文暗夜窗時成立；中低海拔森林語義。",
     "Firefly nights along the cedar-forest edges and trails of Dongyanshan Forest Recreation Area in the season window (Apr-Jun): needs a moonless night, humidity >= 85%, temp >= 15 C, no rain and astronomical darkness; low-to-mid-altitude forest semantics.",
     "螢季（4〜6月）の東眼山国家森林遊楽区：スギ林の縁と歩道沿いのホタルの夜 — 無月、湿度 ≥85%、気温 ≥15°C、無雨、天文暗の夜窓が必要。中低標高の森の語義。"),
    ("tw-024-P06", "star_trails", "tw-024-P05",
     "小笠原山星軌", "Star trails over Ogasawara-yama", "小笠原山の星の軌跡",
     "星軌疊加拍攝：小笠原山 360° 平台以中央山脈稜線為前景的同心圓星軌——天文暗＋無月（月照≤15% 或月下）＋總雲≤20%＋AOD≤0.3＋連續晴窗 ≥2h（連續性否決）時成立。",
     "Star-trail stacking: concentric trails around the Central Range ridgeline from the Ogasawara-yama 360 platform - needs astronomical darkness, a moonless sky (illumination <= 15% or moon below the horizon), total cloud <= 20%, AOD <= 0.3 and a continuous clear window >= 2 h (the continuity veto).",
     "星景スタック撮影：小笠原山 360° 展望台から中央山脈稜線を前景にした同心円の星の軌跡 — 天文暗、無月（月照 ≤15% か月没）、全雲量 ≤20%、AOD ≤0.3、連続晴れ窓 ≥2h（連続性否決）が必要。"),
    ("tw-140-P03", "star_trails", "tw-140-P02",
     "太平山星軌", "Star trails over Taipingshan", "太平山の星の軌跡",
     "星軌疊加拍攝：太平山展望以雲海草原與稜線為前景的同心圓星軌——天文暗＋無月（月照≤15% 或月下）＋總雲≤20%＋AOD≤0.3＋連續晴窗 ≥2h 時成立。",
     "Star-trail stacking: concentric trails over the meadow and ridgeline outlooks of Taipingshan - needs astronomical darkness, a moonless sky (illumination <= 15% or moon below the horizon), total cloud <= 20%, AOD <= 0.3 and a continuous clear window >= 2 h.",
     "星景スタック撮影：太平山の展望から草地と稜線を前景にした同心円の星の軌跡 — 天文暗、無月（月照 ≤15% か月没）、全雲量 ≤20%、AOD ≤0.3、連続晴れ窓 ≥2h が必要。"),
    ("tw-027-P04", "moonlit_scene", "tw-027-P03",
     "田寮月世界月光惡地", "Moonlit badlands of Tianliao Moon World", "田寮月世界の月光悪地",
     "滿月前後的月光地景：月世界惡地泥岩在斜射月光下的灰白紋理與剪影（月仰角 5°–30° 窗）——月照≥85%、總雲≤30%、無雨時成立；地景前景語義。",
     "A moonlit landscape around full moon: the mudstone badlands of Moon World under raking moonlight - grey-white texture and silhouettes (moon elevation 5-30 deg); needs illumination >= 85%, total cloud <= 30% and no rain; foreground-landscape semantics.",
     "満月前後の月光景観：月世界の悪地泥岩が斜めの月光で白灰色の質感とシルエットを見せる（月高度 5°〜30°）— 月照 ≥85%、全雲量 ≤30%、無雨が必要。前景地景の語義。"),
    ("tw-199-P02", "moonlit_scene", "tw-199-P01",
     "利吉惡地月光地景", "Moonlit landscape of the Lichi badlands", "利吉悪地の月光景観",
     "滿月前後的月光地景：利吉惡地泥岩月柱在斜射月光下的紋理與谷線剪影（月仰角 5°–30° 窗）——月照≥85%、總雲≤30%、無雨時成立；地景前景語義。",
     "A moonlit landscape around full moon: the Lichi melange pillars under raking moonlight - texture and gully silhouettes (moon elevation 5-30 deg); needs illumination >= 85%, total cloud <= 30% and no rain; foreground-landscape semantics.",
     "満月前後の月光景観：利吉悪地の泥岩ピラーが斜めの月光で質感と谷のシルエットを見せる（月高度 5°〜30°）— 月照 ≥85%、全雲量 ≤30%、無雨が必要。前景地景の語義。"),
    ("us-121-P02", "moonlit_scene", "us-121-P01",
     "Bixby Bridge moonlit coast", "Bixby Bridge moonlit coast", "ビクスビー橋の月光の海岸",
     "滿月前後的月光海岸：比克斯比溪橋與海岸線在斜射月光下的橋影與浪緣（月仰角 5°–30° 窗）——月照≥85%、總雲≤30%、無雨時成立；海岸語義。",
     "A moonlit coast around full moon: the Bixby Creek bridge and coastline under raking moonlight - bridge shadow and wave edges (moon elevation 5-30 deg); needs illumination >= 85%, total cloud <= 30% and no rain; coast semantics.",
     "満月前後の月光の海岸：ビクスビー橋と海岸線が斜めの月光で橋の影と波の縁を見せる（月高度 5°〜30°）— 月照 ≥85%、全雲量 ≤30%、無雨が必要。海岸の語義。"),
]


def serialize_binding(binding):
    if not binding:
        return None
    return (f"dataset:{binding['dataset']}|field:{binding['field']}"
            f"|role:{binding['role']}")


def template_conditions(oid, genre, window_note):
    t = json.loads((TEMPLATES / f"{genre}.json").read_text(encoding="utf-8"))
    out = []
    for c in t["conditions"]:
        cond = {
            "id": f"C-{oid}-{c['template_ref']}",
            "role": c["role"], "domain": c["domain"],
            "evaluation_mode": c["evaluation_mode"],
            "capability": c["capability"], "condition_tier": c["condition_tier"],
            "metric": c["metric"], "operator": c["operator"],
            "threshold": c["threshold"], "unit": c["unit"],
            "unknown_policy": c["unknown_policy"],
            "claim_refs": [f"{oid}-claim-01"],
            "model_binding": serialize_binding(c.get("binding")),
            "validation_status": c["calibration_status"],
            "condition_tier": c["condition_tier"],
            "threshold_source": c["threshold_source"],
            "calibration_status": c["calibration_status"],
            "rationale_i18n": copy.deepcopy(c["rationale_i18n"]),
        }
        out.append(cond)
    return t, out


SEASONAL_WINDOWS = {
    "tw-041-P06": "11-15~03-10", "tw-042-P02": "11-15~03-10",
    "tw-044-P04": "11-15~03-10", "tw-046-P03": "11-15~03-10",
    "jp-065-P02": "11-15~04-15", "jp-065-P03": "11-15~04-15",
    "tw-019-P07": "12-01~02-28", "tw-120-P02": "12-01~02-28",
    "tw-093-P03": "12-01~02-28", "us-009-P02": "12-01~02-28",
    "tw-151-P02": "04-01~06-15", "tw-144-P03": "04-01~06-15",
}


def adapt_seasonal_rationale(cond, oid, genre):
    """Point the seasonal rationale at the spot's own typical window."""
    if cond["metric"] != "seasonal_state":
        return
    window = SEASONAL_WINDOWS[oid]
    kind = "雪季窗" if genre in ("alpenglow", "snow_scene") else "螢季窗"
    cond["rationale_i18n"] = {
        "zh-TW": (f"季節窗判定（window_open/window_closed，例年窗 {window} 讀自 "
                  "seasonal-calendar.json，實況優先，兩者皆缺時誠實 not_evaluatable）："
                  f"{kind}是本題材的硬性約束（CL-DATA-74 owner 核可資料包）。"),
        "en": (f"Seasonal-window verdict (window_open/window_closed; typical window "
               f"{window} from seasonal-calendar.json, observed takes precedence, "
               "neither present = honestly not_evaluatable): the season window is "
               "this subject's hard constraint (CL-DATA-74 owner-approved data pack)."),
        "ja": (f"季節窓判定（window_open/window_closed。例年窓 {window} は "
               "seasonal-calendar.json から、実況優先、両方なければ誠実に "
               "not_evaluatable）：季節窓は本題材のハード制約"
               "（CL-DATA-74 オーナー承認データパック）。"),
    }


def build_doc(oid, genre, sibling_oid, names, descs):
    sibling = json.loads((OPPS / f"{sibling_oid}.json").read_text(encoding="utf-8"))
    doc = copy.deepcopy(sibling)
    zh, en, ja = names
    dzh, den, dja = descs
    doc["opportunity_id"] = oid
    doc["place_id"] = sibling["place_id"]
    doc["revision"] = 1
    doc["lifecycle_status"] = "draft"
    doc["name_i18n"] = {"zh-TW": zh, "en": en, "ja": ja}
    doc["description_i18n"] = {"zh-TW": dzh, "en": den, "ja": dja}
    suffix = oid
    doc["camera_contexts"] = copy.deepcopy(sibling.get("camera_contexts") or [])
    for i, cc in enumerate(doc["camera_contexts"], start=1):
        cc["id"] = f"CZ-{suffix}-{i:02d}"
    doc["targets"] = copy.deepcopy(sibling.get("targets") or [])
    for i, tg in enumerate(doc["targets"], start=1):
        tg["id"] = f"SG-{suffix}-{i:02d}"
        tg["name_i18n"] = doc["name_i18n"]
    doc["observation_relations"] = []
    for i, cc in enumerate(doc["camera_contexts"], start=1):
        for j, tg in enumerate(doc["targets"], start=1):
            rel = {"id": f"VR-{suffix}-{i:02d}-{j:02d}",
                   "camera_context_id": cc["id"], "target_id": tg["id"],
                   "type": "foreground_background", "geometry_mode": "unknown",
                   "azimuth_deg": None, "elevation_deg": None, "distance_m": None,
                   "evidence_refs": [], "derivation_method": None,
                   "uncertainty_note": ("Subject-specific angles/distance not "
                                        "re-verified in CL-DATA-74 (same viewpoint "
                                        "geometry as the sibling subject).")}
            doc["observation_relations"].append(rel)
    doc["navigation_targets"] = copy.deepcopy(sibling.get("navigation_targets") or [])
    for i, nav in enumerate(doc["navigation_targets"], start=1):
        nav["id"] = f"NAV-{suffix}-{i:02d}"
    # evidence claims: new claim id, same pinned evidence as the sibling
    claims = []
    for k, claim in enumerate(sibling.get("evidence_claims") or [], start=1):
        newc = copy.deepcopy(claim)
        newc["claim_id"] = f"{oid}-claim-01" if k == 1 else f"{oid}-claim-{k:02d}"
        newc["scope_note"] = (
            f"CL-DATA-74 owner-approved five-genre data pack (2026-11-16): subject "
            f"mounted on the existing place with the sibling subject's verified "
            f"geometry/evidence; conditions per the {genre} template. " + newc.get("scope_note", ""))
        claims.append(newc)
    if not claims:
        claims = [{"claim_id": f"{oid}-claim-01", "claim_type": "existence",
                   "evidence_refs": [], "audit_status": "UNKNOWN",
                   "scope_note": "CL-DATA-74 owner-approved mount; evidence rides the sibling subject."}]
    doc["evidence_claims"] = claims
    t, conditions = template_conditions(oid, genre, None)
    for c in conditions:
        adapt_seasonal_rationale(c, oid, genre)
    doc["condition_contract"] = {
        "contract_id": f"CC-{oid}-v1", "status": "draft",
        "genre_template": genre, "template_version": f"{genre}-v0.1",
        "recommendation_policy_version": None, "conditions": conditions,
    }
    prov = copy.deepcopy(sibling.get("provenance") or {})
    prov["source_revision"] = f"{TICKET}-mount"
    prov["review_status"] = "pending"
    doc["provenance"] = prov
    return doc


def main():
    dry = "--dry-run" in sys.argv
    docs = []
    for row in MOUNTS:
        oid, genre, sibling = row[0], row[1], row[2]
        doc = build_doc(oid, genre, sibling, row[3:6], row[6:9])
        docs.append((oid, doc))
        if not dry:
            (OPPS / f"{oid}.json").write_text(
                json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(("DRY " if dry else "WROTE "), oid, genre, "<-", sibling)
    if dry:
        return
    # seasonal-calendar entries (snow / firefly windows)
    cal_path = ROOT / "data/v2/seasonal-calendar.json"
    cal = json.loads(cal_path.read_text(encoding="utf-8"))
    groups = {}
    for row in MOUNTS:
        oid, genre = row[0], row[1]
        if oid not in SEASONAL_WINDOWS:
            continue
        plant = "snow_season" if genre in ("alpenglow", "snow_scene") else "firefly_season"
        key = (plant, SEASONAL_WINDOWS[oid])
        groups.setdefault(key, []).append(oid)
    existing_spots = {s for e in cal["entries"] for s in e.get("spots", [])}
    for (plant, window), spots in sorted(groups.items()):
        start, end = window.split("~")
        name = ({"zh-TW": "雪季", "en": "Snow season", "ja": "雪季"}
                if plant == "snow_season" else
                {"zh-TW": "螢火蟲季", "en": "Firefly season", "ja": "ホタルの季節"})
        cal["entries"].append({
            "plant_id": plant, "spots": spots, "name_i18n": name,
            "typical_window": {"start": start, "end": end},
            "sources": [{"kind": "owner_ticket",
                         "note_i18n": {"zh-TW": "CL-DATA-74 owner 核可五題材資料包（2026-11-16）：例年窗由 owner 資料包提供；實況窗僅在具 source_url 時採信（fail-closed）。",
                                        "en": "CL-DATA-74 owner-approved five-genre data pack (2026-11-16): typical windows from the owner pack; live windows are trusted only with a source_url (fail-closed).",
                                        "ja": "CL-DATA-74 オーナー承認データパック（2026-11-16）：例年窓はオーナーパック由来。実況窓は source_url がある場合のみ採用（fail-closed）。"}}],
        })
        for s in spots:
            assert s not in existing_spots, f"spot already bound: {s}"
            existing_spots.add(s)
    cal["_meta"]["purpose"] = (
        "Owner-maintained seasonal window calendar for seasonal windows "
        "(seasonal_plant genre plus CL-DATA-74 snow_season/firefly_season "
        "windows). AI harvest may ONLY write entries' current_season (and only "
        "with a source_url). Pages display source links from "
        "current_season.source_url.")
    cal_path.write_text(json.dumps(cal, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("seasonal-calendar: +", len(groups), "entries")

    # curation classifications
    cur_path = ROOT / "data/v2/indexes/research/curation.json"
    cur = json.loads(cur_path.read_text(encoding="utf-8"))
    for oid, doc in docs:
        assert oid not in cur["classifications"], oid
        claim = doc["evidence_claims"][0]
        cur["classifications"][oid] = {
            "topic_ids": [],
            "canonical_pointers": ["/targets/0/name_i18n", "/description_i18n"],
            "evidence_claim_id": claim["claim_id"],
            "evidence_refs": claim.get("evidence_refs", []),
            "classification_basis": (
                f"CL-DATA-74 owner-approved mount (five-genre data pack "
                f"2026-11-16); W1 vocabulary has no matching topic - left "
                f"unclassified honestly"),
        }
    cur_path.write_text(json.dumps(cur, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("curation classifications: +", len(docs))


if __name__ == "__main__":
    main()
