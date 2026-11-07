"""CL-INT-90: backfill op-level name_i18n/best_time_i18n for CL-DATA-25/25R catalog records."""
import json

BT_ZH = "本題材尚未核定特定拍攝時段；實際成立與否以當日評估資料為準"
BT_EN = "No specific shooting window has been verified for this subject; whether it forms is judged from the day's evaluation data."
BT_JA = "この題材の特定の撮影時間帯はまだ確認されていません。成立するかは当日の評価データで判断します。"
NEW_SPOTS = tuple(
    [f"jp-{n:03d}" for n in range(37, 51)] + [f"tw-{n:03d}" for n in range(87, 99)]
)

path = "runtime_catalog_v004_r4_2.json"
cat = json.load(open(path, encoding="utf-8"))
patched = 0
for sp in cat["spots"]:
    if sp["spot_id"] not in NEW_SPOTS:
        continue
    for op in sp["opportunities"]:
        variants = op.get("condition_variants") or []
        vi18n = variants[0].get("variant_name_i18n") if variants else None
        assert vi18n and vi18n.get("en") and vi18n.get("ja"), op["opportunity_id"]
        if not op.get("name_i18n"):
            op["name_i18n"] = {"zh-TW": op["name_zh"], "en": vi18n["en"], "ja": vi18n["ja"]}
            patched += 1
        if op.get("best_time") == op.get("name_zh") or not op.get("best_time"):
            op["best_time"] = BT_ZH
            op["best_time_i18n"] = {"zh-TW": BT_ZH, "en": BT_EN, "ja": BT_JA}
            patched += 1
        elif not op.get("best_time_i18n"):
            op["best_time_i18n"] = {"zh-TW": op["best_time"], "en": BT_EN, "ja": BT_JA}
            patched += 1
out = json.dumps(cat, ensure_ascii=False, indent=1) + "\n"
open(path, "w", encoding="utf-8", newline="\n").write(out)
print("patched fields:", patched)
