"""CL-DATA-76 stage-A2: seasonal-calendar.json entries (owner rulings).

- Laomei green reef (tw-073-P01): official North-Guan window Feb-May,
  best Apr-May (owner ruling: the official 2-5月 window, NOT the narrower
  03-15~05-05 Gemini proposal). Sources: northguan-nsa.gov.tw.
- Shinhotaka Nishihotakaguchi stargazing special operation (jp-021-P02):
  official 2026 autumn service season (Oct 2 - Nov 8), coarse superset window;
  the exact service dates are enforced by the legacy shinhotaka access
  provider. Source: shinhotaka-ropeway.jp/play/.

Writes are LF bytes, indent=1 (the file's existing convention).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / "data/v2/seasonal-calendar.json"

raw = PATH.read_bytes()
doc = json.loads(raw.decode("utf-8"))
if (json.dumps(doc, ensure_ascii=False, indent=1) + "\n").encode("utf-8") != raw:
    raise SystemExit("serialization convention mismatch")

existing_plants = {e.get("plant_id") for e in doc["entries"]}
existing_spots = {s for e in doc["entries"] for s in (e.get("spots") or [])}

new_entries = []
if "green_reef_laomei" not in existing_plants:
    new_entries.append({
        "plant_id": "green_reef_laomei",
        "spots": ["tw-073-P01"],
        "name_i18n": {
            "zh-TW": "老梅綠石槽",
            "en": "Laomei green algae reef",
            "ja": "老梅緑石槽",
        },
        "typical_window": {"start": "02-01", "end": "05-31"},
        "sources": [
            {
                "url": "https://www.northguan-nsa.gov.tw/user/Article.aspx?Lang=1&SNo=04002497",
                "kind": "official",
                "note_i18n": {
                    "zh-TW": "北觀處景點頁：每年 2–5 月綠石槽季（每年更新）。最佳觀賞為 4、5 月間（同處另篇公告）。",
                    "en": "North Guan spot page: the green-reef season runs every February-May (annual). Best viewing in April-May per the agency's separate notice.",
                    "ja": "北観処スポット頁：毎年2〜5月が緑石槽の季節（毎年更新）。観賞は4・5月が最適（同処の別告知）。",
                },
            },
            {
                "url": "https://www.northguan-nsa.gov.tw/USER/Article.aspx?Lang=1&SNo=04007403",
                "kind": "official",
                "note_i18n": {
                    "zh-TW": "北觀處新聞：造訪綠石槽最佳時機為 4、5 月間；出發前請查中央氣象署石門每日退潮時間。",
                    "en": "North Guan news: the best visiting window is April-May; check the Central Weather Administration's daily Shimen low-tide times before departure.",
                    "ja": "北観処ニュース：観賞最適は4〜5月。出発前に中央気象署の石門干潮時刻を確認。",
                },
            },
        ],
    })
else:
    print("green_reef_laomei entry already present")

if "shinhotaka_stargazing" not in existing_plants:
    new_entries.append({
        "plant_id": "shinhotaka_stargazing",
        "spots": ["jp-021-P02"],
        "name_i18n": {
            "zh-TW": "西穗高口星空觀賞便（特別夜間營運）",
            "en": "Shinhotaka Nishihotakaguchi stargazing service (special night operation)",
            "ja": "新穂高ロープウェイ星空観賞便（特別夜間運行）",
        },
        "typical_window": {"start": "10-02", "end": "11-08"},
        "sources": [
            {
                "url": "https://shinhotaka-ropeway.jp/play/",
                "kind": "official",
                "note_i18n": {
                    "zh-TW": "新穂高ロープウェイ官方 2026 星空観賞便：秋 10/2-4、10/9-12、10/30-11/3、11/6-8 夜間 18:00–21:00（第2纜車特別運行）；春 5/3-5 已結束。本窗為官方營運季的粗窗超集——僅官方公告日期夜間營運，精確日期由 legacy shinhotaka access provider（shinhotaka_access.py）把關。",
                    "en": "Shinhotaka Ropeway official 2026 stargazing service: autumn Oct 2-4, Oct 9-12, Oct 30-Nov 3, Nov 6-8, nights 18:00-21:00 (second ropeway special service); the spring service May 3-5 has ended. This window is the coarse superset of the official operation season - the ropeway runs at night ONLY on the officially published dates, enforced precisely by the legacy shinhotaka access provider (shinhotaka_access.py).",
                    "ja": "新穂高ロープウェイ公式 2026 星空観賞便：秋 10/2-4、10/9-12、10/30-11/3、11/6-8、夜間 18:00–21:00（第2ロープウェイ特別運行）；春 5/3-5 は終了。本窓は公式営業季の粗い上位集合——夜間運行は公式発表日のみで、正確な日付は legacy の shinhotaka access provider（shinhotaka_access.py）が担保。",
                },
            },
        ],
    })
else:
    print("shinhotaka_stargazing entry already present")

if new_entries:
    doc["entries"].extend(new_entries)
    write_raw = (json.dumps(doc, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    assert b"\r" not in write_raw
    PATH.write_bytes(write_raw)
    print("added entries:", [e["plant_id"] for e in new_entries])
print("STAGE_A2_OK")
