"""檢查景點的日出/夕陽標籤與最佳時間是否吻合（含逐日 tip）"""
import json, sys
sys.path.insert(0, __file__[:__file__.rfind("\\")])
from app import app

with app.test_client() as c:
    resp = c.get('/api/best-spots?region=tw')
    data = resp.get_json()

issues = []

for day_key, day_label in [("today", "今日"), ("tomorrow", "明日"), ("dayafter", "後日")]:
    tip_key = f"tip_{day_key}"
    spots = data.get(day_key, [])
    for s in spots:
        info = s.get(day_key)
        if not info:
            continue
        genre = info.get("best_genre", "")
        best_time = info.get("best_time", "")
        sunrise = info.get("sunrise", "")
        sunset = info.get("sunset", "")
        score = info.get("score", 0)
        tip = s.get(tip_key, "")
        
        if not best_time or "T" not in best_time:
            continue
        t_h = int(best_time.split("T")[1].split(":")[0])
        sunrise_h = int(sunrise.split("T")[1].split(":")[0]) if sunrise and "T" in sunrise else None
        sunset_h = int(sunset.split("T")[1].split(":")[0]) if sunset and "T" in sunset else None
        
        is_golden_morning = sunrise_h is not None and abs(t_h - sunrise_h) <= 2
        is_golden_evening = sunset_h is not None and abs(t_h - sunset_h) <= 2
        
        # Check tip vs time
        tip_has_sunrise = "日出" in tip
        tip_has_sunset = "夕陽" in tip or "日落" in tip
        
        if tip_has_sunset and not tip_has_sunrise and sunrise_h is not None and is_golden_morning and not is_golden_evening:
            issues.append(f"[{day_label}] {s['name']}: tip 說「夕陽」({tip[:30]}...) 但最佳時間={best_time}h 近日出")
        if tip_has_sunrise and not tip_has_sunset and sunset_h is not None and is_golden_evening and not is_golden_morning:
            issues.append(f"[{day_label}] {s['name']}: tip 說「日出」({tip[:30]}...) 但最佳時間={best_time}h 近日落")

print("=" * 60)
print(f"景點時段吻合度檢查 ({day_key})")
print("=" * 60)
if not issues:
    print("✅ 全部通過！所有景點的 tip 都吻合日出/日落時段。")
else:
    print(f"⚠️ 發現 {len(issues)} 個問題：")
    for i in issues:
        print(f"  • {i}")

# Show sample of per-day tips
print("\n\n=== 逐日 tip 抽檢 ===")
for day_key, day_label in [("today", "今日"), ("tomorrow", "明日")]:
    tip_key = f"tip_{day_key}"
    spots = data.get(day_key, [])
    print(f"\n{day_label} (前10):")
    for s in spots[:10]:
        info = s.get(day_key, {})
        t = s.get(tip_key, "")
        scr = info.get("score", 0)
        print(f"  {scr:3d} {s['name']:10s} → {t[:40]}")
print("\nDone!")