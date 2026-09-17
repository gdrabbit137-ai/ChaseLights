#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChaseLights - 攝影天氣分析工具（全球版 & 全景點特殊題材擴充版）
支援台灣、日本、美國、阿拉斯加等區域的攝影天氣分析

使用方法：
  python analyze_weather.py [region]
  
參數：
  region: tw (台灣, 預設), jp (日本), us (美國), ak (阿拉斯加)
  
範例：
  python analyze_weather.py tw      # 台灣區域
  python analyze_weather.py jp      # 日本區域
  python analyze_weather.py us      # 美國區域
  python analyze_weather.py ak      # 阿拉斯加區域
"""

# 修正模組導入路徑
import os, sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'weather_web'))
sys.path.insert(0, BASE_DIR)

import json
from datetime import datetime
from pathlib import Path
import argparse

# 設定編碼為 UTF-8
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加專案根目錄到 Python 路徑
current_dir = Path(__file__).parent
project_root = current_dir.parent if current_dir.name == 'weather_web' else current_dir
sys.path.insert(0, str(project_root))

try:
    import regions
    import fetch_data
    MODULES_AVAILABLE = True
    print("✓ 成功載入景點與天氣模組")
except ImportError as e:
    print(f"❌ 無法載入必要模組: {e}")
    print("請確認您在正確的專案目錄中執行此腳本")
    sys.exit(1)

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
    return min(base_agl, 3500)  # 台灣亞熱帶山區合理上限

def fetch_spots(region_code):
    """精確取得該區域的景點列表"""
    raw_data = None
    if hasattr(regions, 'get_region_spots'):
        raw_data = regions.get_region_spots(region_code)
    elif hasattr(regions, 'get_spots_by_region'):
        raw_data = regions.get_spots_by_region(region_code)
    elif hasattr(regions, 'REGIONS'):
        raw_data = regions.REGIONS.get(region_code, [])
        
    if isinstance(raw_data, dict):
        return raw_data.get('spots', [])
    elif isinstance(raw_data, list):
        return raw_data
    return []

def fetch_weather(lat, lon):
    """相容性函式：支援 fetch_data 的不同 API 名稱"""
    if hasattr(fetch_data, 'get_cached_weather'):
        return fetch_data.get_cached_weather(lat, lon)
    elif hasattr(fetch_data, 'fetch_weather_grid'):
        return fetch_data.fetch_weather_grid(lat, lon)
    elif hasattr(fetch_data, 'get_weather'):
        return fetch_data.get_weather(lat, lon)
    return None

def classify_photographer_position(elevation, cloud_base_agl, low_cc, mid_cc, high_cc):
    """
    判斷攝影師相對於雲層的位置。
    回傳：position, description, score_modifier
    """
    cloud_base_msl = cloud_base_agl + elevation  # 雲底海拔

    if low_cc > 40:
        low_ceiling = CLOUD_LAYERS['low'][1]  # 2,000m
        if elevation > low_ceiling:
            return ('above_low', '🏔️ 站在低雲層之上 → 絕佳雲海視角！', 1.2)
        elif elevation > cloud_base_msl - 200:
            if low_cc > 70:
                return ('in_cloud', '🌫️ 身處雲層中 → 濃霧，能見度差 ⚠️', 0.3)
            else:
                return ('near_cloud', '🌁 接近雲層邊緣 → 局部霧氣', 0.7)
        else:
            return ('below_low', '☁️ 雲在頭頂上方 → 天氣陰沉', 0.5)

    if mid_cc > 50:
        if elevation > 3000:
            return ('above_mid', '🏔️ 接近中雲層高度 → 有機會雲海或身處雲中', 1.0)
        else:
            return ('below_mid', '☁️ 中雲在頭頂 → 一般多雲天氣', 0.6)

    if high_cc > 50:
        return ('high_only', '☀️ 高雲為主 → 火燒雲素材！', 1.0)

    return ('clear', '☀️ 晴朗無雲 → 適合一般風景攝影', 0.8)

def evaluate_special_conditions(spot_name, month, hour, temp, rh, ws, vis_km, cl, cm, ch, elevation, t_td_diff):
    """
    逐景點精細化拍照條件與題材匹配
    回傳：(bonus_score, special_reason, lens_recommendation) 或 None
    """
    # 1. 雪山 / 合歡山 / 阿里山高山雪景與冰霜
    if any(k in spot_name for k in ['雪山', '合歡', '大霸', '玉山']) and month in [12, 1, 2]:
        if temp <= 0 and rh > 85:
            return (95, f'❄️ 極致雪景/霧淞 - 氣溫{temp:.1f}°C 濕度{rh}%，高山冰雪奇景', '14-24mm 廣角鏡 + CPL 偏光鏡（強烈雪地反光）')

    # 2. 阿里山 / 小笠原山 櫻花與日出彩霞
    if '阿里山' in spot_name or '小笠原' in spot_name:
        if month in [3, 4] and hour in [5, 6] and 30 <= ch <= 60:
            return (95, f'🌸 櫻花日出彩霞 - 櫻花季黃金晨光+高雲{ch}%霞光反光板', '24-70mm 中焦段 + 漸層減光鏡')

    # 3. 見晴懷古步道 / 司馬庫斯 / 竹山忘憂森林 - 耶穌光與森林晨霧
    if any(k in spot_name for k in ['見晴', '司馬庫斯', '忘憂森林', '棲蘭', '明池']):
        if 8 <= hour <= 11 and 0.5 <= t_td_diff <= 2.0 and 40 <= (cl + cm) <= 70:
            return (92, f'✨ 森林耶穌光（丁達爾效應）- 輕霧(T-Td={t_td_diff:.1f}°C)與透射林光', '35-85mm 定焦/標準變焦（捕捉光束細節）')

    # 4. 老梅綠石槽 - 抹茶地毯與浪花
    if '老梅' in spot_name:
        if month in [3, 4, 5]:
            if vis_km >= 10.0 and ws < 8.0:
                return (95, f'🌊 綠石槽黃金期 - 春季綠藻生長盛期+浪花長曝（風速{ws:.1f}m/s）', '24-70mm + ND1000 減光鏡（絲絹浪花）')

    # 5. 和平島 / 野柳 / 石門洞 - 海岸奇岩與晨昏
    if any(k in spot_name for k in ['和平島', '野柳', '石門洞', '鼻頭角', '三貂角']):
        if month in [3, 4, 5] and hour in [5, 6, 17, 18] and vis_km >= 15.0:
            return (90, f'🪨 海岸奇岩黃金光 - 春季藻類與極佳能見度({vis_km:.0f}km)', '16-35mm 超廣角 + 腳架低角度張力')

    # 6. 二延平 / 頂石棹 - 琉璃光與茶園雲海
    if any(k in spot_name for k in ['二延平', '頂石棹', '隙頂']):
        if 17 <= hour <= 21 and 70 <= cl <= 95 and t_td_diff < 1.0:
            return (98, f'🌃 絕美琉璃光 - 低雲滿溢蓋城鎮(低雲{cl}%)，夜間燈光透出', '24-70mm + 長曝光 15-30s')

    # 7. 日月潭（朝霧/水社） - 湖面蒸氣霧與水沙連晨光
    if '日月潭' in spot_name or '朝霧' in spot_name or '水社' in spot_name:
        if hour in [5, 6, 7] and t_td_diff <= 1.0 and ws <= 1.5:
            return (94, f'🌫️ 水沙連蒸氣晨霧 - 微風({ws:.1f}m/s)湖面如鏡，倒影與霧氣繚繞', '50-135mm 中長焦（特寫水面船隻與晨霧）')

    # 8. 池上伯朗大道 / 稻浪
    if '伯朗大道' in spot_name or '池上' in spot_name:
        if month in [5, 6, 10, 11]:
            if hour in [6, 7, 16, 17] and 2.5 <= ws <= 5.5:
                return (92, f'🌾 黃金稻浪盛景 - 收割季光影+微風({ws:.1f}m/s)吹拂動態稻浪', '70-200mm 長焦（壓縮金黃稻田 S 彎道）')

    # 9. 六十石山 / 赤柯山 - 金針花海與耶穌光
    if '六十石' in spot_name or '赤柯山' in spot_name:
        if month in [8, 9]:
            if 14 <= hour <= 16 and 50 <= (cl + cm) <= 80:
                return (96, f'🌼 金針花海雲隙光 - 盛開季山谷積雲帶出強烈耶穌光', '16-35mm 超廣角 + CPL 偏光鏡')

    # 10. 九份老街 / 阿妹茶樓 - 雨夜藍調與黃金山城
    if '九份' in spot_name or '阿妹茶樓' in spot_name:
        if hour in [17, 18, 19] and vis_km >= 8.0:
            return (88, f'🏮 藍調山城燈火 - 夕照後藍調時段與地面濕潤光影反射', '35mm/50mm 大光圈定焦（人像與建築交融）')

    # 11. 高山暗空星空（大霸 / 水漾 / 武嶺 / 龍磐）
    if any(k in spot_name for k in ['大霸', '水漾', '武嶺', '合歡', '龍磐', '石梯坪']):
        if (hour >= 21 or hour <= 4) and (cl + cm + ch) < 15 and vis_km >= 20.0:
            return (95, f'🌌 極致璀璨銀河 - 超高大氣透明度(能見度{vis_km:.0f}km)，零雲層干擾', '14-24mm F2.8 超廣角 + 赤道儀/超高 ISO')

    # 12. 奎壁山摩西分海 / 七美雙心石滬
    if '奎壁山' in spot_name or '雙心石滬' in spot_name:
        if 9 <= hour <= 15 and vis_km >= 15.0 and (cl + cm) < 40:
            return (90, f'🏝️ 澎湖果凍海與石滬地景 - 太陽直射透光度極佳(海藍色清澈)', '24-70mm + CPL 偏光鏡（消除水面反光）')

    # 13. 台北 101 / 象山 - 竹雲出土（台北盆地雲海）
    if '101' in spot_name or '象山' in spot_name:
        if hour in [6, 7] and cl > 70 and elevation < 300:
            return (88, f'🏢 台北 101 竹雲出土 - 晨間輻射低雲籠罩盆地，高樓伸出雲海', '70-200mm 長焦（遠眺 101 雲海特寫）')

    return None

def get_weather_data_for_spot(spot):
    try:
        lat = float(spot['lat'])
        lon = float(spot['lon'])
        spot_name = spot.get('name', '未命名景點')
    except (ValueError, KeyError, TypeError) as e:
        print(f"  ❌ 座標格式錯誤: {e}")
        return None

    print(f"  🌐 即時抓取資料: {spot_name} ({lat}, {lon})")
    
    weather_data = None
    try:
        if hasattr(fetch_data, 'fetch_point'):
            weather_data = fetch_data.fetch_point(lat, lon, forecast_days=3)
        elif hasattr(fetch_data, 'fetch_weather'):
            weather_data = fetch_data.fetch_weather(lat, lon)
    except Exception as e:
        print(f"  ⚠️ 即時抓取 Exception: {e}")

    if weather_data and isinstance(weather_data, dict) and 'hourly' in weather_data:
        print(f"  ✅ 即時抓取成功: {spot_name}")
        return weather_data
    
    print(f"  ❌ 無法獲取天氣資料: {spot_name}")
    return None

def analyze_spot_weather(spot, weather_data, region):
    """分析單個景點的攝影天氣條件（含特殊題材擴充）"""
    if not weather_data or 'error' in weather_data:
        return None
        
    spot_name = spot['name']
    elevation = spot.get('elevation', weather_data.get('elevation', 0))
    
    is_mountain = elevation > 1000 or '山' in spot_name or '峰' in spot_name
    is_coast = elevation < 100 and ('海' in spot_name or '港' in spot_name or '灣' in spot_name)
    
    h = weather_data['hourly']
    times = h['time']
    
    now = datetime.now()
    now_s = now.strftime('%Y-%m-%dT%H:00')
    current_index = 0
    for i, time_str in enumerate(times):
        if time_str >= now_s:
            current_index = i
            break
    
    sunrise_str = weather_data.get('sunrise', '')
    sunset_str = weather_data.get('sunset', '')
    
    print(f'\n📍 {spot_name}  (海拔 {elevation:.0f}m)')
    if sunrise_str and sunset_str:
        print(f'   🌅 日出 {sunrise_str[-5:]}   🌇 日落 {sunset_str[-5:]}')
    print('─' * 95)
    
    best_score = 0
    best_time = ""
    best_reason = ""
    best_position = ""
    best_lens_custom = None
    
    display_hours = min(12, len(times) - current_index)
    
    for i in range(current_index, current_index + display_hours):
        if i >= len(times):
            break
            
        time_str = times[i]
        hour = time_str[-5:]
        dt_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%00')
        month = dt_obj.month
        current_hour = dt_obj.hour
        
        rh = h.get('relative_humidity_2m', [None] * len(times))[i] or 0
        cl = h.get('cloud_cover_low', [None] * len(times))[i] or 0
        cm = h.get('cloud_cover_mid', [None] * len(times))[i] or 0
        ch = h.get('cloud_cover_high', [None] * len(times))[i] or 0
        ws = h.get('wind_speed_10m', [None] * len(times))[i] or 0
        vis = h.get('visibility', [None] * len(times))[i] or 0
        wc = h.get('weather_code', [None] * len(times))[i]
        ppt = h.get('precipitation_probability', [None] * len(times))[i] or 0
        temp = h.get('temperature_2m', [None] * len(times))[i] or 0
        dew = h.get('dew_point_2m', [None] * len(times))[i] or 0
        
        # 排除降雨時段
        if wc in (61, 63, 65, 80, 81, 82, 95, 96, 99) or ppt > 60:
            continue
            
        cloud_base_agl = calc_cloud_base(temp, dew)
        pos, pos_desc, mod = classify_photographer_position(elevation, cloud_base_agl, cl, cm, ch)
        
        score = 0
        reason = ""
        lens_rec = None
        
        vis_km = vis / 1000.0 if vis > 0 else 0
        t_td_diff = temp - dew
        is_in_fog = vis_km < 1.0 or t_td_diff < 0.8
        
        if is_in_fog:
            score = 15
            reason = f'🌫️ 濃霧白牆 - 身處雲霧中，視線受阻（能見度{vis_km:.1f}km，T-Td={t_td_diff:.1f}°C）'
        else:
            # 先檢查有無特殊景點條件觸發
            spec_eval = evaluate_special_conditions(
                spot_name, month, current_hour, temp, rh, ws, vis_km, cl, cm, ch, elevation, t_td_diff
            )
            
            if spec_eval:
                score, reason, lens_rec = spec_eval
            else:
                is_sunrise_window = current_hour in [5, 6]
                is_sunset_window = current_hour in [17, 18]
                is_golden_hour = is_sunrise_window or is_sunset_window
                
                if is_mountain:
                    if pos == 'above_low' and cl > 60 and ws < 10 and vis >= 2000:
                        score = 100
                        reason = f'⛰️ 絕佳雲海 - 站在低雲層上方(海拔{elevation:.0f}m)↓雲底{cloud_base_agl:.0f}m'
                    elif pos == 'above_low' and cl > 40 and ws < 15 and vis >= 2000:
                        score = 82
                        reason = f'低雲層在腳下，微風，雲底{cloud_base_agl:.0f}m AGL'
                    elif pos == 'in_cloud':
                        score = 20
                        reason = '⚠️ 身處雲中=濃霧，不適合拍照'
                    elif rh > 85 and cl > 50 and ws < 15:
                        score = 70
                        reason = f'雲量充足，但海拔{elevation:.0f}m與低雲層關係普通'
                    elif rh > 75 and cl > 30:
                        score = 50
                        reason = '條件一般'
                    else:
                        score = 30
                        reason = '雲量不足'
                else:
                    if is_golden_hour and wc in (0, 1, 2) and ch and 30 <= ch <= 70 and cl < 20 and vis > 15000:
                        score = 92
                        reason = f'🌅 火燒雲潛力 - 黃金時段高雲{ch}%+能見{vis_km:.0f}km→完美火燒雲'
                    elif is_golden_hour and ch and 20 <= ch <= 80 and cl < 30 and vis > 10000:
                        score = 65
                        reason = f'黃金時段+高雲{ch}% 能見{vis_km:.0f}km 有機會火燒雲'
                    elif not is_golden_hour and ch and 30 <= ch <= 70 and vis > 10000:
                        score = 55
                        reason = f'高雲景致{ch}% 能見{vis_km:.0f}km（非火燒雲時段）'
                    elif not is_golden_hour and ch and 20 <= ch <= 80:
                        score = 45
                        reason = f'高雲{ch}% 一般景致（非火燒雲時段）'
                    else:
                        score = 30
                        reason = f'條件不足'
                        
        # 風速安全閥：風速過大時扣分與警告（長曝/空拍防晃）
        if ws >= 10.0 and score > 20:
            score = max(20, score - 15)
            reason += f' ⚠️ 強風警告({ws:.1f}m/s)'
            
        if is_mountain and not is_in_fog and not spec_eval:
            score = int(score * mod)
        
        score = min(score, 100)
        
        if score > best_score:
            best_score = score
            best_time = hour
            best_reason = reason
            best_position = pos_desc
            best_lens_custom = lens_rec
        
        is_golden = False
        if sunrise_str:
            sr_h = int(sunrise_str[-5:][:2])
            if abs(current_hour - sr_h) <= 1:
                is_golden = True
        if sunset_str and not is_golden:
            ss_h = int(sunset_str[-5:][:2])
            if abs(current_hour - ss_h) <= 1:
                is_golden = True
        
        if score >= 90:
            tag = '🔥🔥絕佳'
        elif score >= 80:
            tag = '🔥優秀'
        elif score >= 70:
            tag = '⭐良好'
        elif score >= 50:
            tag = '⬜普通'
        else:
            tag = '❌不佳'
        
        golden_mark = ' 🌅' if is_golden else ''
        bar = '█' * (score // 10) + '░' * (10 - score // 10)
        vis_str = f'{vis_km:.0f}km' if vis else 'N/A'
        ppt_s = f'  {ppt}%☂' if ppt > 20 else ''
        
        pos_hint = {'above_low': '⛰️雲上', 'in_cloud': '🌫️霧中', 'near_cloud': '🌁雲邊',
                    'below_low': '☁️雲下', 'above_mid': '🏔️中雲', 'below_mid': '⛅中雲下',
                    'high_only': '☀️高雲', 'clear': '☀️晴'}.get(pos, '❓')
        
        print(f'{hour}{golden_mark} {bar} {score:2d}分 {tag:8s} | {pos_hint:4s} 雲底{cloud_base_agl:3.0f}m | {temp:3.0f}°C 濕{rh:3d}% 低雲{cl:3d}% 中雲{cm:3d}% 高雲{ch:3d}% 風{ws:4.1f} 能見{vis_str}{ppt_s}')
    
    if best_score > 0:
        print(f'  🏆 最佳：{best_time}（{best_score}分）')
        print(f'     📋 {best_reason}')
        print(f'     📐 海拔{elevation:.0f}m | {best_position}')
        
        print(f'     📷 鏡頭建議：', end='')
        if best_lens_custom:
            print(best_lens_custom)
        elif is_mountain:
            if best_score > 80:
                print('14-24mm超廣角 + ND減光鏡（雲海縮時）')
            elif best_score > 60:
                print('24-70mm標準變焦 + 70-200mm長焦（雲海層次壓縮）')
            else:
                print('16-35mm廣角（星空銀河），ISO 3200-6400')
        else:
            best_hour = int(best_time[:2]) if best_time else 12
            is_sunset_golden = best_hour in [17, 18]
            if is_sunset_golden:
                print('70-200mm長焦（壓縮夕陽/倒影），漸層減光鏡')
            else:
                print('70-200mm長焦（特寫地景/雲霧細節），漸層減光鏡')
    
    return {
        'score': best_score,
        'time': best_time,
        'reason': best_reason,
        'position': best_position
    }

def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='ChaseLights - 全球攝影天氣分析工具（全題材擴充版）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
支援區域：
  tw - 台灣（預設）
  jp - 日本  
  us - 美國
  ak - 阿拉斯加

範例：
  python analyze_weather.py tw      # 分析台灣攝影景點
  python analyze_weather.py jp      # 分析日本攝影景點
        """
    )
    
    parser.add_argument(
        'region', 
        nargs='?', 
        default='tw',
        choices=['tw', 'jp', 'us', 'ak'],
        help='選擇分析區域 (預設: tw)'
    )
    
    args = parser.parse_args()
    region = args.region
    
    region_names = {
        'tw': '🇹🇼 台灣',
        'jp': '🇯🇵 日本', 
        'us': '🇺🇸 美國',
        'ak': '🇺🇸 阿拉斯加'
    }
    
    now = datetime.now()
    
    print('📸 ChaseLights 全球攝影天氣報告（全景點特殊題材擴充版）')
    print(f'🌍 分析區域：{region_names.get(region, region.upper())}')
    print(f'⏰ {now.strftime("%Y/%m/%d %H:%M")} 當地時間')
    print('=' * 95)
    
    try:
        print(f'\n🔍 正在載入 {region_names.get(region, region)} 區域景點...')
        spots = fetch_spots(region)
        
        if not spots:
            print(f'❌ {region_names.get(region, region)} 區域暫無景點資料')
            return
            
        print(f'✅ 找到 {len(spots)} 個攝影景點')
        
        analyzed_spots = []
        
        for i, spot in enumerate(spots, 1):
            if isinstance(spot, dict):
                spot_name = spot.get('name', f'景點_{i+1}')
                spot_lat = spot.get('lat')
                spot_lon = spot.get('lon')
            elif isinstance(spot, (list, tuple)):
                str_item = next((x for x in spot if isinstance(x, str)), f'景點_{i+1}')
                num_items = [x for x in spot if isinstance(x, (int, float))]
                
                spot_name = str_item
                spot_lat = num_items[0] if len(num_items) > 0 else None
                spot_lon = num_items[1] if len(num_items) > 1 else None
            else:
                spot_name = str(spot)
                spot_lat, spot_lon = None, None
            
            print(f'\n📡 [{i}/{len(spots)}] 正在分析 {spot_name}...')
            
            if spot_lat is None or spot_lon is None:
                print(f'❌ {spot_name} 缺少有效座標，跳過分析')
                continue
            
            normalized_spot = {
                'name': spot_name,
                'lat': float(spot_lat),
                'lon': float(spot_lon)
            }
            
            weather_data = get_weather_data_for_spot(normalized_spot)
            
            if weather_data:
                result = analyze_spot_weather(normalized_spot, weather_data, region)
                if result:
                    analyzed_spots.append({
                        'spot': normalized_spot,
                        'analysis': result
                    })
            else:
                print(f'❌ 跳過 {spot_name} - 無法獲取天氣資料')
        
        if analyzed_spots:
            print(f'\n{"=" * 95}')
            print('🏆 今日最佳攝影景點排名')
            print(f'{"=" * 95}')
            
            analyzed_spots.sort(key=lambda x: x['analysis']['score'], reverse=True)
            
            for i, item in enumerate(analyzed_spots[:10], 1):
                spot = item['spot']
                analysis = item['analysis']
                
                score_emoji = '🔥🔥' if analysis['score'] >= 90 else '🔥' if analysis['score'] >= 80 else '⭐' if analysis['score'] >= 70 else '⬜'
                
                print(f'{i:2d}. {score_emoji} {spot["name"]:20s} | {analysis["score"]:3d}分 | {analysis["time"]} | {analysis["reason"]}')
        
        print(f'\n{"=" * 95}')
        print('🌤️  功能整合：雲底高度（T-Td）+ 霧牆防護 + 時段火燒雲 + 景點專屬特殊題材配對')
        print('🌬️  新增機制：風速過大防晃動扣分（>10m/s）與相應專業鏡頭建議')
        print(f'✨  本次分析了 {len(analyzed_spots)} 個景點，資料來源 Open-Meteo API')
        
    except Exception as e:
        print(f'❌ 程式執行錯誤: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()