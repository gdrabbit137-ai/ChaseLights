"""CL-DATA-76 stage-A contract edits (run inside the task worktree).

Owner rulings 2026-11-20 (first + second audit wave):
1. tw-076-P01 Longpan coastal sunrise: mountain_view -> sunrise template family
   (aligned with tw-080-P01); low-cloud gate 30 -> 35 per owner ruling; all
   rationales rewritten to Pacific sea-cliff grassland semantics (not mountain
   cloud logic). 75's §1 already demoted cloud_cover_mid to BONUS and added
   visibility >= 15 km (kept).
2. tw-074-P01: conditions untouched; genre/template family sunrise ->
   geological_landform (consistent with tw-074-P02).
3. Gemini report real gaps: Laomei seasonal window registered in
   seasonal-calendar.json (official North-Guan Feb-May, best Apr-May); legacy
   placeholder contracts tw-059/tw-060/tw-078 rebuilt as tide-decided honest
   contracts (water_surface_state REQUIRED, CL-COND-A7 pattern; the legacy
   R4.2 tide_state module already evaluates these three opportunities).
7 (second audit): tw-072-P02/tw-074-P02 landform_present removed (no observable
   source metric); tw-078 gains the official Kinmen tide-access + golden-hour
   anchors; tw-073 gains the tide threshold; jp-021-P02 bound to the official
   Shinhotaka stargazing special-operation season via seasonal-calendar +
   seasonal_state; unit normalization (precipitation mm/h, aod 'AOD' suffix
   dropped); tw-071..080 name_i18n en/ja filled (natural Japanese, no
   simplified han).

All writes are LF bytes; round-trip serialization verified before writing.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OPP = ROOT / "data/v2/opportunities"


def check_roundtrip(path, indent=2):
    raw = Path(path).read_bytes()
    doc = json.loads(raw.decode("utf-8"))
    if (json.dumps(doc, ensure_ascii=False, indent=indent) + "\n").encode("utf-8") != raw:
        raise SystemExit(f"serialization convention mismatch: {path}")
    return doc


def write(path, doc, indent=2):
    raw = (json.dumps(doc, ensure_ascii=False, indent=indent) + "\n").encode("utf-8")
    assert b"\r" not in raw
    Path(path).write_bytes(raw)
    print("wrote", Path(path).name, len(raw))


NOTE_76 = {
    "zh-TW": "2026-11-20 CL-DATA-76（owner 裁決）：龍磐為臨太平洋海崖草原題材，模板由 mountain_view 對齊 sunrise 家族（與 tw-080-P01 同族）；低雲必須門檻 30%→35%（owner 裁決值）；各條件 rationale 改寫為海岸日出語義，非山岳雲層邏輯。",
    "en": "2026-11-20 CL-DATA-76 (owner ruling): Longpan is a Pacific sea-cliff grassland subject - the template moves from mountain_view to the sunrise family (aligned with tw-080-P01); the REQUIRED low-cloud gate 30% -> 35% (owner-ruled value); all rationales rewritten to coastal-sunrise semantics, not mountain-cloud logic.",
    "ja": "2026-11-20 CL-DATA-76（オーナー裁定）：龍磐は太平洋海崖の草原題材。テンプレートを mountain_view から sunrise 家族へ（tw-080-P01 と同族整合）；低層雲の必須閾値 30%→35%（オーナー裁定値）；全 rationale を海岸日の出の意味に書き直し（山岳雲ロジックではない）。",
}

I18N_NAMES = {
    "tw-071-P01": ("Vase Rock coastal sunrise", "花瓶岩の海岸の日の出"),
    "tw-071-P02": ("Vase Rock sunset glow", "花瓶岩の夕焼け"),
    "tw-072-P01": ("Nanya Rock sunrise light", "南雅奇岩の日の出の光"),
    "tw-072-P02": ("Nanya Rock sunset glow clouds", "南雅奇岩の夕焼け雲"),
    "tw-073-P01": ("Laomei green reef spring morning light", "老梅緑石槽の春の朝の光"),
    "tw-074-P01": ("Yehliu Queen's Head landform light", "野柳クイーンズヘッド（女王頭）の地形と光"),
    "tw-074-P02": ("Yehliu mushroom rocks and candle rock textures", "野柳のキノコ岩と燭台石のテクスチャ"),
    "tw-075-P01": ("Waiao sunrise with Guishan Island", "外澳から亀山島の日の出"),
    "tw-076-P01": ("Longpan grassland coastal sunrise", "龍磐パークの海岸の日の出"),
    "tw-076-P02": ("Longpan grassland Milky Way and starry sky", "龍磐パークの天の川と星空"),
    "tw-077-P01": ("Shitiping wave-cut platform sunrise", "石梯坪の海食台の日の出"),
    "tw-078-P01": ("Jiangong Islet tidal stone causeway", "建功嶼の干潮時に現れる石板道"),
    "tw-079-P01": ("Chixi columnar basalt at sunset", "池西の柱状玄武岩と夕映え"),
    "tw-080-P01": ("Fanchuanbi grassland cape sunrise", "帆船鼻草原の海岬の日の出"),
    "tw-080-P02": ("Fanchuanbi grassland starry sky and Milky Way", "帆船鼻草原の星空と天の川"),
}


def cond(cid, role, tier, metric, operator, threshold, unit, domain, claim,
         model_binding=None, threshold_source="formula_derived", rationale=None,
         notes=None):
    item = {
        "id": cid, "role": role, "domain": domain, "evaluation_mode": "GUIDANCE",
        "capability": "CONDITIONS", "metric": metric, "operator": operator,
        "threshold": threshold, "unit": unit, "unknown_policy": "propagate_unknown",
        "claim_refs": [claim], "model_binding": model_binding,
        "validation_status": "provisional", "condition_tier": tier,
        "threshold_source": threshold_source, "calibration_status": "provisional",
        "rationale_i18n": rationale,
    }
    if notes is not None:
        item["notes_i18n"] = notes
    return item


def i18n_note(zh, en, ja):
    return {"zh-TW": zh, "en": en, "ja": ja}


# --- 1) tw-076-P01 ----------------------------------------------------------
path = OPP / "tw-076-P01.json"
doc = check_roundtrip(path)
c = doc["condition_contract"]
c["genre_template"] = "sunrise"
c["template_version"] = "sunrise-v0.1"
doc["revision"] = doc["revision"] + 1
for condition in c["conditions"]:
    metric = condition["metric"]
    if metric == "sunrise_time_window":
        condition["rationale_i18n"] = i18n_note(
            "天文窗＝日出時刻 ±40 分（座標＋日期計算）。龍磐草原面向太平洋海平線、無地形遮擋，天文日出即實際見日。",
            "Astronomy window = sunrise time +/- 40 minutes (from coordinates and date). The Longpan grassland faces the open Pacific sea horizon with no terrain occlusion, so the astronomical sunrise matches the visible one.",
            "天文ウィンドウ＝日の出時刻±40分。龍磐草原は太平洋の海平線を望み地形遮蔽がないため、天文日の出が実際の見えと一致する。")
        condition["notes_i18n"] = NOTE_76
    elif metric == "cloud_cover_low":
        condition["threshold"] = 35
        condition["rationale_i18n"] = i18n_note(
            "日出方位的低雲直接擋住海平線上的太陽；35% 仍允許塊狀低雲——碎雲反而是為日出上色的主角。這是臨海草原的日出判據，不是山岳雲層邏輯。",
            "Low cloud in the sunrise-azimuth sector blocks the sun over the sea horizon directly; 35% still allows broken low cloud, which is what actually paints the colour. This is a coastal-grassland sunrise criterion, not mountain-cloud logic.",
            "日の出方位の扇形領域の低雲は海平線上の太陽を直接遮る。35%は塊状の低雲を許容し、色を生む主役。これは臨海草原の日の出判定であり、山岳雲ロジックではない。")
        condition["notes_i18n"] = i18n_note(
            "2026-11-20 CL-DATA-75 §1 新增必須（≤30%）；同日 CL-DATA-76（owner 裁決）調整為 ≤35% 並隨模板對齊 sunrise 家族。",
            "2026-11-20 CL-DATA-75 section 1 added the REQUIRED gate (<=30%); same day CL-DATA-76 (owner ruling) moved it to <=35% as part of the sunrise-family alignment.",
            "2026-11-20 CL-DATA-75 §1 で必須追加（≤30%）；同日 CL-DATA-76（オーナー裁定）で ≤35% に調整し sunrise 家族へ整合。")
    elif metric == "cloud_cover_mid":
        condition["rationale_i18n"] = i18n_note(
            "中雲 30–60% 為天空加層次與色彩，但只是加分——太平洋海平線的晴空日出同樣是絕佳畫面（晴天不誤殺）。",
            "Mid-cloud 30-60% adds layering and colour to the sky, but as a bonus only - a clear-sky sunrise over the Pacific sea horizon is equally superb (clear skies are never vetoed).",
            "中層雲30〜60%は空に重なりと色を添えるが加点にとどめる——太平洋海平線の晴空の日の出も優れた画面（晴空を誤殺しない）。")
        condition["notes_i18n"] = i18n_note(
            "2026-11-20 CL-DATA-75（owner 規格 §1）必須 → 加分（BONUS）；2026-11-20 CL-DATA-76 rationale 隨海岸語義改寫。",
            "2026-11-20 CL-DATA-75 (owner spec section 1) demoted from REQUIRED gate to QUALITY/BONUS; 2026-11-20 CL-DATA-76 rewrote the rationale to the coastal semantics.",
            "2026-11-20 CL-DATA-75（オーナー仕様 §1）で必須から加点へ；2026-11-20 CL-DATA-76 で rationale を海岸語義に書き直し。")
    elif metric == "visibility":
        condition["rationale_i18n"] = i18n_note(
            "面向海平線的日出需要通透空氣：能見度 ≥15 km，霧霾吞掉海平線與遠處海崖輪廓時直接否決。",
            "A sunrise facing the sea horizon needs transparent air: visibility >= 15 km; haze that swallows the sea-horizon line and the distant sea cliffs vetoes the hour outright.",
            "海平線を望む日の出には透明な空気が要る：視程≥15 km。ヘイズが海平線と遠い海崖の輪郭を飲み込む場合は否決。")
    elif metric == "precipitation":
        condition["rationale_i18n"] = i18n_note(
            "拍攝受影響下限：降水 >0.2 mm/h 時草原步道濕滑、鏡面受雨點干擾。",
            "Minimum before the shoot is impaired: above 0.2 mm/h the grassland trail turns slippery and raindrops disturb the scene.",
            "撮影に支障が出る前の下限：0.2mm/h超では草原の歩道が滑り、雨粒が画面を乱す。")
write(path, doc)

# --- 2) tw-074-P01 ----------------------------------------------------------
path = OPP / "tw-074-P01.json"
doc = check_roundtrip(path)
c = doc["condition_contract"]
c["genre_template"] = "geological_landform"
c["template_version"] = "geological_landform-v0.1"
doc["revision"] = doc["revision"] + 1
note76_label = i18n_note(
    "2026-11-20 CL-DATA-76（owner 裁決）：契約條件不動；genre/家族標籤由 sunrise 改為 geological_landform（與 tw-074-P02 同家族——女王頭是全天地質光影題材，日出行維持加分語義）。",
    "2026-11-20 CL-DATA-76 (owner ruling): contract conditions untouched; the genre/family label moves from sunrise to geological_landform (same family as tw-074-P02 - Queen's Head is an all-day geological-light subject; the sunrise row stays a bonus).",
    "2026-11-20 CL-DATA-76（オーナー裁定）：契約条件は不変；genre／家族ラベルを sunrise から geological_landform へ（tw-074-P02 と同家族——女王頭は終日地質光影の題材、日の出行は加点のまま）。")
for condition in c["conditions"]:
    if condition["metric"] == "sunrise_time_window":
        existing = condition.get("notes_i18n")
        if existing:
            condition["notes_i18n"] = {
                "zh-TW": existing["zh-TW"] + " " + note76_label["zh-TW"],
                "en": existing["en"] + " " + note76_label["en"],
                "ja": existing["ja"] + " " + note76_label["ja"],
            }
        else:
            condition["notes_i18n"] = note76_label
write(path, doc)

# --- 7i) tw-074-P02: drop landform_present (no observable source) -----------
path = OPP / "tw-074-P02.json"
doc = check_roundtrip(path)
c = doc["condition_contract"]
c["conditions"] = [x for x in c["conditions"] if x["metric"] != "landform_present"]
required = [x for x in c["conditions"] if x["role"] == "REQUIRED"]
assert required, "tw-074-P02 REQUIRED set must not be empty"
doc["revision"] = doc["revision"] + 1
write(path, doc)

# --- 7i) tw-072-P02: drop landform_present ---------------------------------
path = OPP / "tw-072-P02.json"
doc = check_roundtrip(path)
c = doc["condition_contract"]
c["conditions"] = [x for x in c["conditions"] if x["metric"] != "landform_present"]
required = [x for x in c["conditions"] if x["role"] == "REQUIRED"]
assert required, "tw-072-P02 REQUIRED set must not be empty"
doc["revision"] = doc["revision"] + 1
write(path, doc)

# --- 3a/7iii) tw-073-P01: tide threshold (tide-decided, honest) -------------
TIDE_RATIONALE_LAOMEI = i18n_note(
    "潮汐決定型（CL-COND-A7 慣例）：綠石槽只在乾潮前後約 ±2 小時露出，漲潮淹沒石槽即不宜拍攝。V2 評估層尚無潮汐資料源——誠實 propagate unknown（fail-closed → NOT_EVALUABLE），不以風雨派生指標冒充潮位判據；legacy 管線已接 tide_state（相對潮位 percentile，low_exposure_strict）。拍攝指南：出發前查中央氣象署石門潮汐預報與北觀處公告。",
    "Tide-decided subject (CL-COND-A7 convention): the green reef is exposed only within about +/- 2 hours of low tide and shooting is pointless once the rising tide submerges it. The V2 evaluation layer has no tide data source - honest propagate unknown (fail-closed -> NOT_EVALUABLE), never a wind/rain proxy impersonating a tide gate; the legacy pipeline already carries tide_state (relative sea-level percentile, low_exposure_strict mode). Shooting guide: check the Central Weather Administration Shimen tide forecast and the North-Guan notices before heading out.",
    "潮位決定型（CL-COND-A7 慣例）：緑石槽は干潮前後約±2時間だけ露出し、満潮で水没すれば撮影に適さない。V2評価層に潮汐データソースがない — 誠実に propagate unknown（fail-closed → NOT_EVALUABLE）。風雨派生の指標を潮位判定の代用にしない；legacy パイプラインは tide_state を実装済み（相対潮位パーセンタイル、low_exposure_strict）。撮影ガイド：出発前に中央気象署の石門潮汐予報と北観処の告知を確認。")
path = OPP / "tw-073-P01.json"
doc = check_roundtrip(path)
c = doc["condition_contract"]
if not any(x["metric"] == "water_surface_state" for x in c["conditions"]):
    claim = c["conditions"][0]["claim_refs"][0]
    c["conditions"].append(cond(
        "C-tw-073-P01-TW1", "REQUIRED", "MAIN", "water_surface_state", "none", None,
        None, "HYDROLOGY", claim, model_binding=None,
        threshold_source="evidence_review", rationale=TIDE_RATIONALE_LAOMEI,
        notes=i18n_note(
            "2026-11-20 CL-DATA-76（owner 第二份稽核裁決）：老梅補乾潮前後 ±2 小時門檻（漲潮淹沒即不宜）。以 water_surface_state 承載潮汐決定語義（CL-COND-A7 潮汐決定型既有模式）；legacy tide_state 已涵蓋本機會點。",
            "2026-11-20 CL-DATA-76 (owner second-audit ruling): Laomei gains a low-tide +/- 2 h gate (the rising tide submerging the reef makes shooting pointless). The tide-decided semantics ride on water_surface_state (the established CL-COND-A7 tide-decided pattern); the legacy tide_state module already covers this opportunity.",
            "2026-11-20 CL-DATA-76（オーナー第二監査裁定）：老梅に干潮前後±2時間の閾値を追加（満潮で水没すれば不適）。潮位決定の意味は water_surface_state で担う（CL-COND-A7 の既存パターン）；legacy tide_state は既に本機会点をカバー。")))
doc["revision"] = doc["revision"] + 1
write(path, doc)

# --- 3b) tw-059-P01: rebuild placeholder as tide-decided honest contract ----
path = OPP / "tw-059-P01.json"
doc = check_roundtrip(path)
c = doc["condition_contract"]
claim = "tw-059-P01-claim-01"
c["conditions"] = [
    cond("C-tw-059-P01-01", "REQUIRED", "MAIN", "water_surface_state", "none", None,
         None, "HYDROLOGY", claim, model_binding=None, threshold_source="evidence_review",
         rationale=i18n_note(
             "潮汐決定型（CL-COND-A7 慣例）：摩西分海步道僅在乾潮前後露出，漲潮淹沒即封閉（過去有遊客受困救援案例）。V2 評估層尚無潮汐資料源——誠實 propagate unknown（fail-closed → NOT_EVALUABLE）；legacy 管線已接 tide_state（low_exposure_strict，相對潮位 percentile ≤30%）。拍攝指南：出發前查潮汐表與現場公告，勿憑目測冒險登踏。",
             "Tide-decided subject (CL-COND-A7 convention): the Moses-parting causeway is exposed only around low tide and the rising tide closes it (past rescue incidents). The V2 evaluation layer has no tide data source - honest propagate unknown (fail-closed -> NOT_EVALUABLE); the legacy pipeline already carries tide_state (low_exposure_strict, relative sea-level percentile <= 30%). Shooting guide: check the tide table and on-site notices; never judge by eye.",
             "潮位決定型（CL-COND-A7 慣例）：モーゼ分海の歩道は干潮前後だけ露出し、満潮で閉鎖（過去に救助事例）。V2評価層に潮汐データソースがない — 誠実に propagate unknown（fail-closed → NOT_EVALUABLE）；legacy パイプラインは tide_state を実装済み（low_exposure_strict、相対潮位パーセンタイル≤30%）。撮影ガイド：干潮表と現地告知を確認し、目測で判断しない。"),
         notes=i18n_note(
             "2026-11-20 CL-DATA-76（owner 裁決：補真實條件或誠實標記）：CL-DATA-20 的「待潮汐模組再建契約」語義由本契約取代——真實條件即潮汐決定語義，V2 誠實 not_evaluatable，legacy tide_state 繼續供卡片判讀。",
             "2026-11-20 CL-DATA-76 (owner ruling: fill real conditions or label honestly): this contract supersedes the CL-DATA-20 'wait for a tide module' stance - the real condition IS the tide-decided semantics, V2 stays honestly not_evaluatable, and the legacy tide_state module keeps feeding the card verdict.",
             "2026-11-20 CL-DATA-76（オーナー裁定：実条件の補完または誠実な標記）：本契約は CL-DATA-20 の「潮汐モジュール待ち」方針を置き換える——実条件とは潮位決定の意味であり、V2 は誠実に not_evaluatable、legacy tide_state がカード判定を継続。")),
    cond("C-tw-059-P01-02", "REQUIRED", "MAIN", "light_window", "none", None,
         None, "ASTRONOMY", claim, model_binding=None, threshold_source="computed",
         rationale=i18n_note(
             "民用光線窗（civil，太陽仰角 > −6°）：分海步道攝影是全日題材，夜間一律不符合（CL-DATA-11 同源定義）。",
             "Civil light window (sun elevation > -6 deg): the causeway shoot is an all-day subject; night hours never qualify (CL-DATA-11 same-source definition).",
             "市民光ウィンドウ（太陽高度 > -6°）：分海歩道の撮影は終日題材であり、夜間は一律成立しない（CL-DATA-11 同源定義）。")),
    cond("C-tw-059-P01-03", "REQUIRED", "SHOOT", "precipitation", "lt", 0.3,
         "mm/h", "WEATHER", claim,
         model_binding="dataset:gfs_0p25|field:precipitation_rate_mm_h|role:MID",
         rationale=i18n_note(
             "拍攝時降雨 <0.3 mm/h：既審通用門檻；雨中潮間帶岩面濕滑。",
             "Precipitation < 0.3 mm/h at shoot time: reviewed generic threshold; wet intertidal rock is slippery in rain.",
             "撮影時の降水<0.3mm/h。既承認閾値。雨の潮間帯岩面は滑りやすい。")),
]
doc["revision"] = doc["revision"] + 1
write(path, doc)

# --- 3b) tw-060-P01: rebuild placeholder ------------------------------------
path = OPP / "tw-060-P01.json"
doc = check_roundtrip(path)
c = doc["condition_contract"]
c["genre_template"] = "tidal"
c["template_version"] = "tidal-v0.1"
claim = "tw-060-P01-claim-01"
c["conditions"] = [
    cond("C-tw-060-P01-01", "REQUIRED", "MAIN", "water_surface_state", "none", None,
         None, "HYDROLOGY", claim, model_binding=None, threshold_source="evidence_review",
         rationale=i18n_note(
             "潮汐決定型（CL-COND-A7 慣例）：雙心石滬完整形態只在乾潮露出（漲潮淹沒滬石）。V2 評估層尚無潮汐資料源——誠實 propagate unknown（fail-closed → NOT_EVALUABLE）；legacy 管線已接 tide_state（low_exposure）。拍攝指南：出發前查澎湖潮汐表。",
             "Tide-decided subject (CL-COND-A7 convention): the full double-heart fish-weir form shows only at low tide (the rising tide submerges the stones). The V2 evaluation layer has no tide data source - honest propagate unknown (fail-closed -> NOT_EVALUABLE); the legacy pipeline already carries tide_state (low_exposure). Shooting guide: check the Penghu tide table first.",
             "潮位決定型（CL-COND-A7 慣例）：双心石滬の完全な形は干潮時だけ現れる（満潮で石が水没）。V2評価層に潮汐データソースがない — 誠実に propagate unknown（fail-closed → NOT_EVALUABLE）；legacy パイプラインは tide_state を実装済み（low_exposure）。撮影ガイド：出発前に澎湖の干潮表を確認。"),
         notes=i18n_note(
             "2026-11-20 CL-DATA-76（owner 裁決：補真實條件或誠實標記）：legacy_reflection 佔位由潮汐決定語義取代；V2 誠實 not_evaluatable，legacy tide_state 繼續供卡片判讀。",
             "2026-11-20 CL-DATA-76 (owner ruling: fill real conditions or label honestly): the legacy_reflection placeholder is replaced by the tide-decided semantics; V2 stays honestly not_evaluatable, and the legacy tide_state module keeps feeding the card verdict.",
             "2026-11-20 CL-DATA-76（オーナー裁定）：legacy_reflection のプレースホルダを潮位決定の意味に置換；V2 は誠実に not_evaluatable、legacy tide_state が継続。")),
    cond("C-tw-060-P01-02", "REQUIRED", "MAIN", "light_window", "none", None,
         None, "ASTRONOMY", claim, model_binding=None, threshold_source="computed",
         rationale=i18n_note(
             "民用光線窗（civil，太陽仰角 > −6°）：石滬攝影是全日題材，夜間一律不符合（CL-DATA-11 同源定義）。",
             "Civil light window (sun elevation > -6 deg): the fish-weir shoot is an all-day subject; night hours never qualify (CL-DATA-11 same-source definition).",
             "市民光ウィンドウ（太陽高度 > -6°）：石滬撮影は終日題材であり、夜間は一律成立しない（CL-DATA-11 同源定義）。")),
    cond("C-tw-060-P01-03", "REQUIRED", "SHOOT", "precipitation", "lte", 0.3,
         "mm/h", "WEATHER", claim,
         model_binding="dataset:gfs_0p25|field:precipitation_mm_h|role:MID",
         rationale=i18n_note(
             "拍攝時降雨 <0.3 mm/h：既審通用門檻。",
             "Precipitation < 0.3 mm/h at shoot time: reviewed generic threshold.",
             "撮影時の降水<0.3mm/h。既承認閾値。")),
]
doc["revision"] = doc["revision"] + 1
write(path, doc)

# --- 7ii) tw-078-P01: official tide access window + golden-hour anchor ------
KINMEN_URL = "https://www.kinmen.travel/zh-tw/guide/jiangongyu-islet-tidal"
path = OPP / "tw-078-P01.json"
doc = check_roundtrip(path)
c = doc["condition_contract"]
claim = "tw-078-P01-claim-01"
c["conditions"] = [
    cond("C-tw-078-P01-01", "REQUIRED", "MAIN", "water_surface_state", "none", None,
         None, "HYDROLOGY", claim, model_binding=None, threshold_source="evidence_review",
         rationale=i18n_note(
             "潮汐決定型（CL-COND-A7 慣例）：金門縣政府依潮汐公布每日建議登島時段（乾潮前後約 ±30 分，石板道僅乾潮露出）；漲潮淹沒即封閉，日落後禁止登島。V2 評估層尚無潮汐資料源——誠實 propagate unknown（fail-closed → NOT_EVALUABLE）；legacy 管線已接 tide_state（low_access_window）。拍攝指南：查金門觀光旅遊網建功嶼潮汐表與現場公告。",
             "Tide-decided subject (CL-COND-A7 convention): the Kinmen County Government publishes a daily recommended landing window keyed to the tide (about +/- 30 minutes around low tide; the stone causeway shows only at ebb); the rising tide closes it and landing is prohibited after sunset. The V2 evaluation layer has no tide data source - honest propagate unknown (fail-closed -> NOT_EVALUABLE); the legacy pipeline already carries tide_state (low_access_window). Shooting guide: check the Kinmen travel site tide table and on-site notices.",
             "潮位決定型（CL-COND-A7 慣例）：金門県政府は潮汐に応じて毎日の上島推奨時刻を公表（干潮前後約±30分、石板道は干潮時のみ現れる）；満潮で閉鎖、日の入り後の上島は禁止。V2評価層に潮汐データソースがない — 誠実に propagate unknown（fail-closed → NOT_EVALUABLE）；legacy パイプラインは tide_state を実装済み（low_access_window）。撮影ガイド：金門観光旅遊網の建功嶼潮汐表と現地告知を確認。"),
         notes=i18n_note(
             "2026-11-20 CL-DATA-76（owner 裁決）：legacy_mountain_view 佔位取代為官方乾潮登島窗＋黃金時段錨點。來源：金門觀光旅遊網建功嶼潮汐頁 " + KINMEN_URL,
             "2026-11-20 CL-DATA-76 (owner ruling): the legacy_mountain_view placeholder is replaced by the official low-tide landing window plus a golden-hour anchor. Source: Kinmen travel site Jiangong Islet tide page " + KINMEN_URL,
             "2026-11-20 CL-DATA-76（オーナー裁定）：legacy_mountain_view のプレースホルダを公式干潮上島窓＋ゴールデンアワーの錨に置換。出典：金門観光旅遊網 建功嶼潮汐ページ " + KINMEN_URL)),
    cond("C-tw-078-P01-02", "REQUIRED", "MAIN", "golden_hour_window", "none", None,
         None, "ASTRONOMY", claim, model_binding=None, threshold_source="computed",
         rationale=i18n_note(
             "黃金時段錨點：官方規定日落後禁止登島，拍攝窗必須在日落前的黃金光線內；夕陽金光灑在潮間帶與石板道是本題材的招牌畫面。",
             "Golden-hour anchor: landing is prohibited after sunset by the official rule, so the shoot must sit inside the golden light before sunset; golden light over the tidal flats and the stone causeway is the subject's signature frame.",
             "ゴールデンアワーの錨：公式規則で日の入り後の上島は禁止——撮影は日の入り前の黄金光の中に限る。潮間帯と石板道に差す金色の光が本題材の代表作。")),
    cond("C-tw-078-P01-03", "REQUIRED", "SHOOT", "precipitation", "lte", 0.3,
         "mm/h", "WEATHER", claim,
         model_binding="dataset:gfs_0p25|field:precipitation_mm_h|role:MID",
         rationale=i18n_note(
             "拍攝時降雨 <0.3 mm/h：既審通用門檻；雨中石板道濕滑。",
             "Precipitation < 0.3 mm/h at shoot time: reviewed generic threshold; the wet stone causeway is slippery.",
             "撮影時の降水<0.3mm/h。既承認閾値。雨の石板道は滑りやすい。")),
]
doc["revision"] = doc["revision"] + 1
write(path, doc)

# --- 7iv) jp-021-P02: bind the official special-operation season ------------
path = OPP / "jp-021-P02.json"
doc = check_roundtrip(path)
c = doc["condition_contract"]
if not any(x["metric"] == "seasonal_state" for x in c["conditions"]):
    claim = c["conditions"][0]["claim_refs"][0]
    c["conditions"].append(cond(
        "C-jp-021-P02-OP1", "REQUIRED", "MAIN", "seasonal_state", "eq", "window_open",
        None, "TEMPORAL", claim, model_binding=None, threshold_source="evidence_review",
        rationale=i18n_note(
            "西穗高口展望台夜間僅在官方「星空観賞便」特別營運日開放（2026 秋季 10/2-4、10/9-12、10/30-11/3、11/6-8，夜間 18:00–21:00，第2纜車特別運行；春季 5/3-5 已結束）。季節窗引擎以日期窗匹配（10-02〜11-08 為官方營運季粗窗超集——精確營運日由 legacy shinhotaka access provider 把關）；窗外的夜空條件再好也不成立（纜車夜間不運行）。",
            "The Nishihotakaguchi observation deck opens at night only on the official stargazing-service dates (2026 autumn: Oct 2-4, Oct 9-12, Oct 30-Nov 3, Nov 6-8, 18:00-21:00, second ropeway special service; the spring service May 3-5 has ended). The seasonal-window engine matches by date window (10-02..11-08 is the coarse official season superset - the exact service dates are enforced by the legacy shinhotaka access provider); outside the window the night-sky conditions do not matter because the ropeway does not run at night.",
            "西穂高口展望台が夜間開放されるのは公式の「星空観賞便」特別運行日のみ（2026年秋：10/2-4、10/9-12、10/30-11/3、11/6-8、18:00-21:00、第2ロープウェイ特別運行；春の5/3-5は終了）。季節窓エンジンは日付窓で照合（10-02〜11-08 は公式営業季の粗い上位集合——正確な営業日は legacy の shinhotaka access provider が担保）；窓外は星空条件が良くても成立しない（夜間は運行しない）。"),
        notes=i18n_note(
            "2026-11-20 CL-DATA-76（owner 裁決：綁西穗高口特別營業日曆）。官方營業資訊來源：https://shinhotaka-ropeway.jp/play/ （2026 運行計畫）。legacy 層 shinhotaka_access.py 已登錄官方 2026 日期集並要求當窗即時營運確認。",
            "2026-11-20 CL-DATA-76 (owner ruling: bind the Nishihotakaguchi special-operation calendar). Official operation source: https://shinhotaka-ropeway.jp/play/ (2026 service plan). The legacy layer (shinhotaka_access.py) already carries the official 2026 date set and requires a same-window live operation confirmation.",
            "2026-11-20 CL-DATA-76（オーナー裁定：西穂高口特別営業カレンダーに紐付け）。公式営業情報：https://shinhotaka-ropeway.jp/play/ （2026 運行計画）。legacy 層（shinhotaka_access.py）は公式 2026 日付セットと同窓のライブ運行確認を実装済み。")))
doc["revision"] = doc["revision"] + 1
write(path, doc)

# --- i18n: tw-071..080 name_i18n en/ja -------------------------------------
for oid, (en, ja) in I18N_NAMES.items():
    path = OPP / f"{oid}.json"
    doc = check_roundtrip(path)
    doc["name_i18n"]["en"] = en
    doc["name_i18n"]["ja"] = ja
    write(path, doc)

# --- 7v) unit normalization -------------------------------------------------
prec_fixed, aod_fixed = [], []
for path in sorted(OPP.glob("*.json")):
    doc = json.loads(path.read_bytes().decode("utf-8"))
    raw = path.read_bytes()
    changed = False
    for condition in doc.get("condition_contract", {}).get("conditions", []):
        if condition.get("metric") == "precipitation" and condition.get("unit") == "mm":
            condition["unit"] = "mm/h"
            prec_fixed.append(doc["opportunity_id"])
            changed = True
        if condition.get("metric") == "aod_550nm" and condition.get("unit") == "AOD":
            condition["unit"] = None
            aod_fixed.append(doc["opportunity_id"])
            changed = True
    if changed:
        raw_new = (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        assert b"\r" not in raw_new
        path.write_bytes(raw_new)
        print("unit-fix", path.stem)
print("precipitation mm->mm/h:", len(prec_fixed))
print("aod 'AOD'->null:", len(aod_fixed))
print("STAGE_A_OK")
