import json
from datetime import datetime
from pathlib import Path

data_dir = Path(r'D:\Dick\Project\PhotoWeather\.weather_cache')
data_dir.mkdir(exist_ok=True)

# WMO天氣代碼中文對照
WMO_DESC = {
    0: "☀️ 晴天", 1: "🌤️ 晴時多雲", 2: "⛅ 局部多雲", 3: "☁️ 陰天",
    45: "🌫️ 霧", 48: "🌫️ 霧淞",
    51: "🌦️ 小毛毛雨", 53: "🌦️ 中毛毛雨", 55: "🌧️ 大毛毛雨",
    61: "🌧️ 小雨", 63: "🌧️ 中雨", 65: "🌧️ 大雨",
    80: "🌦️ 小陣雨", 81: "🌦️ 中陣雨", 82: "🌧️ 大陣雨",
    95: "⛈️ 雷陣雨", 96: "⛈️ 雷+冰雹", 99: "⛈️ 強雷+冰雹",
}

# ─── 雲層定義（WMO 國際標準，亞熱帶適用） ───
CLOUD_LAYERS = {
    'low':  (0, 2000),    # 低雲：0~2,000m
    'mid':  (2000, 6000), # 中雲：2,000~6,000m
    'high': (6000, 12000),# 高雲：6,000m 以上
}

def calc_cloud_base(temp_c, dew_c):
    """使用溫度-露點差估算雲底高度（公尺 AGL）"""
    spread = temp_c - dew_c
    if spread <= 0:
        return 0  # 已飽和，雲底在地面
    base_agl = spread * 125
    return min(base_agl, 6000)  # 合理上限

def classify_photographer_position(elevation, cloud_base_agl, low_cc, mid_cc, high_cc):
    """
    判斷攝影師相對於雲層的位置。
    回傳：position, description, score_modifier
    """
    cloud_base_msl = cloud_base_agl + elevation  # 雲底海拔

    # ── 情況 1：低雲層大量存在 ──
    if low_cc > 40:
        low_ceiling = CLOUD_LAYERS['low'][1]  # 2,000m
        if elevation > low_ceiling:
            # 攝影師在低雲層上方（如合歡山 3,300m > 2,000m）
            return ('above_low',
                    '🏔️ 站在低雲層之上 → 絕佳雲海視角！',
                    1.2)
        elif elevation > cloud_base_msl - 200:
            # 攝影師接近/在雲底高度 → 可能身處霧中
            if low_cc > 70:
                return ('in_cloud',
                        '🌫️ 身處雲層中 → 濃霧，能見度差 ⚠️',
                        0.3)
            else:
                return ('near_cloud',
                        '🌁 接近雲層邊緣 → 局部霧氣',
                        0.7)
        else:
            # 攝影師在低雲下方
            return ('below_low',
                    '☁️ 雲在頭頂上方 → 天氣陰沉',
                    0.5)

    # ── 情況 2：中雲層為主 ──
    if mid_cc > 50:
        if elevation > 3000:
            return ('above_mid',
                    '🏔️ 接近中雲層高度 → 有機會雲海或身處雲中',
                    1.0)
        else:
            return ('below_mid',
                    '☁️ 中雲在頭頂 → 一般多雲天氣',
                    0.6)

    # ── 情況 3：晴朗或高雲 ──
    if high_cc > 50:
        return ('high_only',
                '☀️ 高雲為主 → 火燒雲素材！',
                1.0)

    return ('clear',
            '☀️ 晴朗無雲 → 適合一般風景攝影',
            0.8)


spots_data = {
    '合歡山主峰 (雲海/星空)': data_dir / 'hehuan.json',
    '阿里山隙頂 (雲海/夕陽)': data_dir / 'alishan.json',
    '大屯山助航站 (琉璃光/夜景)': data_dir / 'datun.json',
    '淡水漁人碼頭 (火燒雲/日落)': data_dir / 'tamsui.json',
    '高美濕地 (夕陽倒影)': data_dir / 'gaomei.json',
}

now = datetime.now()
now_s = now.strftime('%Y-%m-%dT%H:00')

print('📸 攝影天氣報告（雲層高度版）')
print(f'⏰ {now.strftime("%Y/%m/%d %H:%M")} 台灣時間')
print('=' * 95)

for name, fpath in spots_data.items():
    if not fpath.exists():
        print(f'\n📍 {name}\n   暫無數據')
        continue

    with open(fpath) as f:
        d = json.load(f)
    if 'error' in d:
        print(f'\n📍 {name}\n   ❌ {d["error"]}')
        continue

    h = d['hourly']
    times = h['time']
    si = next((i for i, t in enumerate(times) if t >= now_s), 0)
    elevation = d.get('elevation', 0)
    is_mt = '合歡山' in name or '阿里山' in name or '大屯山' in name
    is_coast = '淡水' in name or '高美' in name

    sunrise_str = d.get('sunrise', '')
    sunset_str = d.get('sunset', '')

    print(f'\n📍 {name}  (海拔 {elevation:.0f}m)')
    if sunrise_str and sunset_str:
        print(f'   🌅 日出 {sunrise_str[-5:]}   🌇 日落 {sunset_str[-5:]}')
    print('─' * 95)

    # ─── 最佳時段搜尋（48h，含雲層高度判斷） ───
    best_i, best_sc = si, 0
    best_reason, best_pos = '', ''
    for i in range(si, min(si + 48, len(times))):
        rh = h['relative_humidity_2m'][i] or 0
        cl = h['cloud_cover_low'][i] or 0
        cm = h['cloud_cover_mid'][i] or 0
        ch = h['cloud_cover_high'][i] or 0
        ws = h['wind_speed_10m'][i] or 0
        vis = h['visibility'][i] or 0
        wc = h['weather_code'][i] if h['weather_code'][i] is not None else -1
        ppt = h['precipitation_probability'][i] or 0
        temp = h['temperature_2m'][i] or 0
        dew = h['dew_point_2m'][i] or 0

        # 排除降雨
        if wc in (61, 63, 65, 80, 81, 82, 95, 96, 99) or ppt > 60:
            continue

        # 雲底高度估算
        cloud_base_agl = calc_cloud_base(temp, dew)
        pos, pos_desc, mod = classify_photographer_position(elevation, cloud_base_agl, cl, cm, ch)

        # ── 山區雲海評分（考慮高度） ──
        if is_mt:
            if pos == 'above_low' and cl > 60 and ws < 10:
                sc = 95
                reason = f'站在低雲層上方(海拔{elevation:.0f}m)↓雲底{cloud_base_agl:.0f}m AGL'
            elif pos == 'above_low' and cl > 40 and ws < 15:
                sc = 82
                reason = f'低雲層在腳下，微風，雲底{cloud_base_agl:.0f}m AGL'
            elif pos == 'in_cloud':
                sc = 20
                reason = '⚠️ 身處雲中=濃霧，不適合拍照'
            elif rh > 85 and cl > 50 and ws < 15:
                sc = 70
                reason = f'雲量充足，但海拔{elevation:.0f}m與低雲層關係普通'
            elif rh > 75 and cl > 30:
                sc = 50
                reason = '條件一般'
            else:
                sc = 30
                reason = '雲量不足'
        # ── 海岸火燒雲（高度影響小，但能見度重要） ──
        else:
            if wc in (0, 1, 2) and ch and 30 <= ch <= 70 and cl < 20 and vis > 15000:
                sc = 92
                reason = f'晴天+高雲{ch}%+能見{vis//1000}km→完美火燒雲'
            elif ch and 20 <= ch <= 80 and cl < 30 and vis > 10000:
                sc = 65
                reason = f'高雲{ch}% 能見{vis//1000}km 有機會'
            else:
                sc = 30
                reason = f'條件不足'

        sc = int(sc * mod) if is_mt else sc  # 套用高度位置修正
        if sc > best_sc:
            best_sc = sc
            best_i = i
            best_reason = reason
            best_pos = pos_desc

    # ─── 逐時顯示（前12小時） ───
    for i in range(si, min(si + 12, len(times))):
        t = times[i][-5:]
        rh = h['relative_humidity_2m'][i] or 0
        cl = h['cloud_cover_low'][i] or 0
        cm = h['cloud_cover_mid'][i] or 0
        ch = h['cloud_cover_high'][i] or 0
        ws = h['wind_speed_10m'][i] or 0
        vis = h['visibility'][i] or 0
        wc = h['weather_code'][i]
        ppt = h['precipitation_probability'][i] or 0
        temp = h['temperature_2m'][i] or 0
        dew = h['dew_point_2m'][i] or 0

        # 雲底高度 + 位置判斷
        cloud_base_agl = calc_cloud_base(temp, dew)
        pos, pos_desc, mod = classify_photographer_position(elevation, cloud_base_agl, cl, cm, ch)

        wc_desc = WMO_DESC.get(wc, f'碼{wc}') if wc is not None else '?'

        # 黃金時段標記
        is_golden = False
        if sunrise_str:
            sr_h = int(sunrise_str[-5:][:2])
            if abs(int(t[:2]) - sr_h) <= 1:
                is_golden = True
        if sunset_str and not is_golden:
            ss_h = int(sunset_str[-5:][:2])
            if abs(int(t[:2]) - ss_h) <= 1:
                is_golden = True

        # 位置 emoji
        pos_emoji = {'above_low': '⛰️', 'in_cloud': '🌫️', 'near_cloud': '🌁',
                     'below_low': '☁️', 'above_mid': '🏔️', 'below_mid': '⛅',
                     'high_only': '☀️', 'clear': '☀️'}.get(pos, '❓')

        # 評分
        if is_mt:
            if pos == 'above_low' and cl > 60 and ws < 10:
                sc, tag = 92, '🔥🔥絕佳雲海'
            elif pos == 'above_low' and cl > 40:
                sc, tag = 82, '🔥雲海上空'
            elif pos == 'in_cloud':
                sc, tag = 20, '🌫️身處雲中'
            elif rh > 85 and cl > 50:
                sc, tag = 70, '⭐雲海潛力'
            elif rh > 75 and cl > 30:
                sc, tag = 50, '⬜普通'
            else:
                sc, tag = 30, '⬜普通'
        else:
            if wc in (0, 1, 2) and ch and 30 <= ch <= 70 and cl < 20 and vis > 15000:
                sc, tag = 92, '🔥🔥絕佳火燒雲'
            elif ch and 20 <= ch <= 80 and cl < 30 and vis > 10000:
                sc, tag = 65, '⭐有機會'
            else:
                sc, tag = 30, '⬜普通'

        golden_mark = ' 🌅' if is_golden else ''
        bar = '█' * (sc // 10) + '░' * (10 - sc // 10)
        vis_km = f'{vis // 1000}km' if vis else 'N/A'
        ppt_s = f'  {ppt}%☂' if ppt > 20 else ''

        # 簡要位置提示
        pos_hint = {'above_low': '⛰️雲上', 'in_cloud': '🌫️霧中', 'near_cloud': '🌁雲邊',
                    'below_low': '☁️雲下', 'above_mid': '🏔️中雲', 'below_mid': '⛅中雲下',
                    'high_only': '☀️高雲', 'clear': '☀️晴'}.get(pos, '❓')

        print(f'{t}{golden_mark} {bar} {sc:2d}分 {tag:8s} | {pos_hint:4s} 雲底{cloud_base_agl:3.0f}m | {temp:3.0f}°C 濕{rh:3d}% 低雲{cl:3d}% 中雲{cm:3d}% 高雲{ch:3d}% 風{ws:4.1f} 能見{vis_km}{ppt_s}')

    # 最佳時段總結
    best_t = times[best_i][-5:]
    best_temp = h['temperature_2m'][best_i] or 0
    best_dew = h['dew_point_2m'][best_i] or 0
    best_cl = h['cloud_cover_low'][best_i] or 0
    best_cm = h['cloud_cover_mid'][best_i] or 0
    best_ws = h['wind_speed_10m'][best_i] or 0
    best_vis = h['visibility'][best_i] or 0
    best_wc = h['weather_code'][best_i]
    best_wc_desc = WMO_DESC.get(best_wc, '') if best_wc is not None else ''
    best_cb = calc_cloud_base(best_temp, best_dew)

    print(f'  🏆 最佳：{best_t}（{best_sc}分）')
    print(f'     📋 {best_reason}')
    print(f'     📐 海拔{elevation:.0f}m | 雲底{best_cb:.0f}m AGL ({best_cb+elevation:.0f}m MSL)')
    print(f'     🌡️ {best_temp:.0f}°C 露點{best_dew:.0f}°C | 低雲{best_cl}% 中雲{best_cm}% | 風{best_ws:.1f}km/h 能見{best_vis//1000}km | {best_wc_desc}')

    # 專業攝影建議
    print(f'     📷 鏡頭建議：', end='')
    if is_mt:
        if best_cl > 60 and elevation > 2000:
            print('14-24mm超廣角 + ND減光鏡（雲海縮時）')
            print(f'     ⚠️ 雲海在腳下{best_cb:.0f}m處，三腳架要夠穩，風{best_ws:.1f}km/h')
        elif best_cl > 50:
            print('24-70mm標準變焦 + 70-200mm長焦（雲海層次壓縮）')
        else:
            print('16-35mm廣角（星空銀河），ISO 3200-6400')
    else:
        print('70-200mm長焦（壓縮夕陽/倒影），漸層減光鏡')

print(f'\n{"=" * 95}')
print('🌤️  新增：雲底高度估算（T-Td）×125，判斷拍照者與雲層的垂直位置')
print('📐  WMO雲層標準：低雲 0~2km | 中雲 2~6km | 高雲 >6km')
print('💡  判斷邏輯：海拔 > 雲層頂 → 雲海上空 | 海拔 ≈ 雲底 → 身處霧中')