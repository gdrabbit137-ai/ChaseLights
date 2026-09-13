#!/usr/bin/env python3
import json, os

TMP = os.environ.get('TEMP', os.environ.get('TMP', 'C:/Users/Dick_/AppData/Local/Temp'))
TMP = TMP.replace('\\', '/')

WMO = {0:"☀️晴天",1:"🌤️晴時多雲",2:"⛅局部多雲",3:"☁️陰天",
       45:"🌫️霧",51:"🌦️毛毛雨",61:"🌧️小雨",63:"🌧️中雨",80:"🌦️陣雨",95:"⛈️雷雨"}

spots = [
    ("大屯山助航站", f"{TMP}/datun_wk.json", "琉璃光/夜景/雲海", 1082, True),
    ("淡水漁人碼頭", f"{TMP}/tamsui_wk.json", "火燒雲/日落", 0, False),
    ("高美濕地", f"{TMP}/gaomei_wk.json", "夕陽倒影/風車", 4, False),
    ("陽明山擎天崗", f"{TMP}/yangming_wk.json", "草原晨光/芒草", 800, True),
    ("基隆和平島", f"{TMP}/keelung_wk.json", "日出/岩石地景", 20, False),
    ("北海岸富貴角", f"{TMP}/fuguijiao_wk.json", "燈塔/夕陽/綠石槽", 10, False),
    ("九份不厭亭", f"{TMP}/jiufen_wk.json", "山海/夕陽/雲海", 540, True),
    ("象山夜景", f"{TMP}/elephant_wk.json", "101/城市夜景", 180, False),
]

sat, sun = "2026-09-05", "2026-09-06"
lines = []

lines.append("=" * 90)
lines.append("📸 北台灣週末攝影天氣評測  (週六 9/5 → 週日 9/6)")
lines.append("=" * 90)

for name, fpath, theme, elev, is_mt in spots:
    with open(fpath) as f:
        data = json.load(f)
    if 'hourly' not in data:
        lines.append(f"\n❌ {name}: 無數據")
        continue

    lines.append(f"\n📍 {name} — {theme}  (海拔{elev}m)")

    for day_label, day_str in [("週六 9/5", sat), ("週日 9/6", sun)]:
        if day_str not in data['daily']['time']:
            lines.append(f"   {day_label}: 預報不足")
            continue

        di = data['daily']['time'].index(day_str)
        sunrise = data['daily']['sunrise'][di][-5:]
        sunset = data['daily']['sunset'][di][-5:]
        sr_h = int(sunrise[:2])
        ss_h = int(sunset[:2])

        h = data['hourly']
        day_hours = [i for i, t in enumerate(h['time']) if t.startswith(day_str)]

        best_sc = 0
        best_tag = ""
        good_hours = []

        for i in day_hours:
            t = h['time'][i][-5:]
            hr = int(t[:2])
            rh = h['relative_humidity_2m'][i] or 0
            cl = h['cloud_cover_low'][i] or 0
            ch = h['cloud_cover_high'][i] or 0
            ws = h['wind_speed_10m'][i] or 0
            vis = h['visibility'][i] or 0
            ppt = h['precipitation_probability'][i] or 0
            temp = h['temperature_2m'][i] or 0
            wc = h['weather_code'][i] if h['weather_code'][i] is not None else -1

            if wc in (61,63,65,80,81,82,95,96,99) or ppt > 60:
                continue

            is_golden = abs(hr - sr_h) <= 2 or abs(hr - ss_h) <= 2

            if is_mt:
                if cl > 60 and rh > 80 and ws < 10:
                    sc = 92 if elev > 1000 else 75
                    tag = "🔥🔥雲海" if sc > 85 else "⭐雲海"
                elif cl > 50 and rh > 75 and ws < 15:
                    sc = 65; tag = "⭐有機會"
                else:
                    sc = 35; tag = "⬜普通"
            else:
                if wc in (0,1,2) and ch and 30<=ch<=70 and cl<20 and vis>15000:
                    sc = 92; tag = "🔥🔥火燒雲"
                elif ch and 20<=ch<=80 and cl<30 and vis>10000:
                    sc = 65; tag = "⭐有機會"
                else:
                    sc = 35; tag = "⬜"

            if not (sc >= 50 or is_golden):
                continue

            if sc >= best_sc:
                best_sc = sc
                best_tag = tag

            emoji = " 🌅" if is_golden else ""
            t_mark = ""
            if hr == sr_h: t_mark = " 日出!"
            elif hr == ss_h: t_mark = " 日落!"

            bar = "█" * (sc // 10) + "░" * (10 - sc // 10)
            wc_d = WMO.get(wc, f"碼{wc}")
            good_hours.append(f"   {t}{emoji} {bar} {sc:2d}分 {tag:8s} | {temp:2.0f}°C 濕{rh:2.0f}% 低雲{cl:2.0f}% 高雲{ch:2.0f}% 風{ws:3.1f} 能見{vis//1000}km {wc_d}{t_mark}")

        lines.append(f"   {day_label} 日出{sunrise}→日落{sunset}  最佳:{best_sc}分 {best_tag}")
        for g in good_hours[:8]:
            lines.append(g)

print("\n".join(lines))