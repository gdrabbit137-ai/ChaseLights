"""
ChaseLights — 天氣網格資料擷取模組

從 Open-Meteo API 擷取氣象網格資料，
包含能見度、雲量、溫度、露點、風速等攝影相關參數。
"""

import json, os, time, hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
import requests

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
CACHE_TTL = 600  # 10 分鐘快取

# 確保快取目錄存在，避免寫入檔案時報錯
os.makedirs(CACHE_DIR, exist_ok=True)

# ─── 台灣網格點定義 ───────────────────────────────────────────
GRID_LATS = [21.8, 22.2, 22.6, 23.0, 23.4, 23.8, 24.2, 24.6, 25.0, 25.4, 25.8, 26.2]
GRID_LONS = [118.2, 118.6, 119.0, 119.4, 119.8, 120.2, 120.6, 121.0, 121.4, 121.8, 122.2, 122.6]

PHOTO_SPOTS = [
    {"name": "大屯山", "lat": 25.1869, "lon": 121.5208},
    {"name": "象山", "lat": 25.0275, "lon": 121.5700},
    {"name": "淡水漁人碼頭", "lat": 25.1761, "lon": 121.4103},
    {"name": "九份不厭亭", "lat": 25.1058, "lon": 121.8403},
    {"name": "金瓜石茶壺山", "lat": 25.1083, "lon": 121.8600},
    {"name": "大稻埕碼頭", "lat": 25.0508, "lon": 121.5050},
    {"name": "關渡大橋", "lat": 25.1270, "lon": 121.4600},
    {"name": "碧潭", "lat": 24.9590, "lon": 121.5340},
    {"name": "觀音山硬漢嶺", "lat": 25.1410, "lon": 121.4210},
    {"name": "基隆望幽谷", "lat": 25.1550, "lon": 121.7830},
    {"name": "和平島", "lat": 25.1620, "lon": 121.7690},
    {"name": "桃園永安漁港", "lat": 24.9850, "lon": 121.0190},
    {"name": "新竹香山濕地", "lat": 24.7610, "lon": 120.9090},
    {"name": "苗栗火炎山", "lat": 24.3630, "lon": 120.7400},
    {"name": "苗栗雲洞山莊", "lat": 24.4040, "lon": 120.8200},
    {"name": "高美濕地", "lat": 24.3120, "lon": 120.5500},
    {"name": "台中鳶嘴山", "lat": 24.2440, "lon": 120.9790},
    {"name": "彰化王功漁港", "lat": 23.9670, "lon": 120.3340},
    {"name": "日月潭", "lat": 23.8560, "lon": 120.9370},
    {"name": "合歡山主峰", "lat": 24.1370, "lon": 121.2720},
    {"name": "金龍山", "lat": 23.9120, "lon": 120.9310},
    {"name": "武界部落", "lat": 23.8930, "lon": 121.0140},
    {"name": "二延平步道", "lat": 23.4720, "lon": 120.6830},
    {"name": "頂石棹", "lat": 23.4750, "lon": 120.6850},
    {"name": "阿里山", "lat": 23.5100, "lon": 120.8020},
    {"name": "二寮", "lat": 23.0020, "lon": 120.4130},
    {"name": "井仔腳鹽田", "lat": 23.2820, "lon": 120.1160},
    {"name": "田寮月世界", "lat": 22.8910, "lon": 120.3930},
    {"name": "駁二藝術特區", "lat": 22.6200, "lon": 120.2810},
    {"name": "墾丁鵝鑾鼻", "lat": 21.9010, "lon": 120.8530},
    {"name": "屏東關山", "lat": 21.9670, "lon": 120.7240},
    {"name": "抹茶山", "lat": 24.8240, "lon": 121.7260},
    {"name": "見晴懷古步道", "lat": 24.4820, "lon": 121.4930},
    {"name": "粉鳥林", "lat": 24.4420, "lon": 121.7800},
    {"name": "清水斷崖", "lat": 24.2260, "lon": 121.6880},
    {"name": "六十石山", "lat": 23.2310, "lon": 121.3250},
    {"name": "七星潭", "lat": 24.0260, "lon": 121.6320},
    {"name": "多良車站", "lat": 22.4440, "lon": 120.9920},
    {"name": "三仙台", "lat": 23.1260, "lon": 121.4200},
    {"name": "池上伯朗大道", "lat": 23.1010, "lon": 121.2210},
    {"name": "玉山主峰", "lat": 23.4700, "lon": 120.9570},
    {"name": "雪山主峰", "lat": 24.3830, "lon": 121.2330},
    {"name": "雪山北峰", "lat": 24.4230, "lon": 121.2400},
    {"name": "奇萊主峰", "lat": 24.1160, "lon": 121.3250},
    {"name": "南湖大山", "lat": 24.3620, "lon": 121.4390},
    {"name": "嘉明湖", "lat": 23.2830, "lon": 120.9830},
    {"name": "大霸尖山", "lat": 24.4610, "lon": 121.2580},
    {"name": "北大武山", "lat": 22.6170, "lon": 120.7500},
    {"name": "池有山", "lat": 24.4320, "lon": 121.2860},
    {"name": "桃山", "lat": 24.4320, "lon": 121.3050},
    {"name": "品田山", "lat": 24.4370, "lon": 121.2640},
    {"name": "澎湖跨海大橋", "lat": 23.6160, "lon": 119.5300},
    {"name": "澎湖奎壁山", "lat": 23.5810, "lon": 119.7200},
    {"name": "澎湖七美雙心石滬", "lat": 23.1940, "lon": 119.4340},
    {"name": "金門得月樓", "lat": 24.4490, "lon": 118.3360},
    {"name": "金門翟山坑道", "lat": 24.4050, "lon": 118.3280},
    {"name": "馬祖南竿", "lat": 26.1580, "lon": 119.9420},
    {"name": "馬祖東引燈塔", "lat": 26.3670, "lon": 120.5080},
    {"name": "馬祖北竿芹壁", "lat": 26.2230, "lon": 119.9780},
    {"name": "綠島朝日溫泉", "lat": 22.6400, "lon": 121.4910},
    {"name": "蘭嶼東清灣", "lat": 22.0670, "lon": 121.5560},
    {"name": "蘭嶼青青草原", "lat": 22.0370, "lon": 121.5370},
    {"name": "小琉球花瓶岩", "lat": 22.3430, "lon": 120.3800},
]

def build_grid_points():
    points = []
    for lat in GRID_LATS:
        for lon in GRID_LONS:
            points.append({"lat": round(lat, 1), "lon": round(lon, 1), "type": "grid"})
    return points

def build_spot_points():
    return [{"lat": round(s["lat"], 4), "lon": round(s["lon"], 4),
             "name": s["name"], "type": "spot"} for s in PHOTO_SPOTS]

def merge_points():
    grid = build_grid_points()
    spots = build_spot_points()
    grid_keys = set()
    for p in grid:
        grid_keys.add((round(p["lat"], 1), round(p["lon"], 1)))
    for s in spots:
        sk = (round(s["lat"], 1), round(s["lon"], 1))
        if sk in grid_keys:
            grid_keys.remove(sk)
    filtered_grid = []
    for p in grid:
        if (round(p["lat"], 1), round(p["lon"], 1)) in grid_keys:
            filtered_grid.append(p)
    return filtered_grid + spots

def cache_key(lat, lon):
    raw = f"{lat:.4f}_{lon:.4f}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]

def fetch_point(lat, lon, forecast_days=3):
    cache_path = os.path.join(CACHE_DIR, f"{cache_key(lat, lon)}.json")
    if os.path.exists(cache_path):
        age = time.time() - os.path.getmtime(cache_path)
        if age < CACHE_TTL:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly=relative_humidity_2m,cloud_cover_low,cloud_cover_mid,cloud_cover_high,"
        f"wind_speed_10m,visibility,weather_code,precipitation_probability,"
        f"temperature_2m,dew_point_2m"
        f"&daily=sunrise,sunset,weather_code,precipitation_sum"
        f"&timezone=Asia/Taipei"
        f"&forecast_days={forecast_days}"
    )
    try:
        resp = requests.get(url, timeout=15)
        data = resp.json()
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        return data
    except Exception as e:
        return {"error": str(e), "lat": lat, "lon": lon}

def fetch_weather_for_spot(spot):
    """供 analyze_weather.py 單點調用的標準介面"""
    lat = spot.get("lat")
    lon = spot.get("lon")
    raw_weather = fetch_point(lat, lon, forecast_days=3)
    
    # 簡化計算分數與評估邏輯
    if "error" in raw_weather:
        return {"score": 0, "reason": "API 讀取失敗"}
        
    hourly = raw_weather.get("hourly", {})
    clouds = hourly.get("cloud_cover_low", [0])
    visibility = hourly.get("visibility", [10000])
    wind = hourly.get("wind_speed_10m", [0])

    avg_cloud = clouds[0] if clouds else 0
    vis_km = (visibility[0] / 1000.0) if visibility else 10
    wind_spd = wind[0] if wind else 0

    # 計算基本評分
    score = 30
    reason = "出景機率普通"

    if avg_cloud < 30 and vis_km >= 15:
        score = 85
        reason = "大晴天、能見度高，極適合風景與星空拍攝"
    elif avg_cloud > 80:
        score = 20
        reason = "雲量過厚，出景機率較低"
    elif wind_spd > 15:
        score = 40
        reason = f"風速較大 ({wind_spd}m/s)，請注意立三腳架安全"

    return {
        "name": spot.get("name"),
        "score": score,
        "best_time": "23:00",
        "position": f"雲量: {avg_cloud}% | 能見度: {vis_km:.1f}km",
        "reason": reason
    }

def fetch_all(max_workers=10):
    points = merge_points()
    results = {}
    print(f"Fetching {len(points)} points with {max_workers} workers...")
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        fut_map = {}
        for p in points:
            fut = pool.submit(fetch_point, p["lat"], p["lon"], 3)
            fut_map[fut] = p
            time.sleep(0.02)  # 避免過快連線觸發 API rate limit
        done = 0
        for fut in as_completed(fut_map):
            p = fut_map[fut]
            try:
                data = fut.result()
                key = f"{p['lat']:.4f},{p['lon']:.4f}"
                results[key] = {
                    "lat": p["lat"],
                    "lon": p["lon"],
                    "type": p.get("type", "grid"),
                    "name": p.get("name", ""),
                    "data": data,
                }
            except Exception as e:
                print(f" Failed: {p.get('name') or p} — {e}")
            done += 1
            if done % 10 == 0 or done == len(points):
                print(f" Progress: {done}/{len(points)}")
    return results

def build_forecast_json(results):
    now = datetime.now(timezone(timedelta(hours=8)))
    points_out = []
    for key, val in results.items():
        d = val["data"]
        if "error" in d:
            continue
        hourly = d.get("hourly", {})
        daily = d.get("daily", {})
        points_out.append({
            "lat": val["lat"],
            "lon": val["lon"],
            "type": val["type"],
            "name": val["name"],
            "elevation": d.get("elevation"),
            "hourly": hourly,
            "daily": daily,
        })
    return {
        "generated_at": now.isoformat(),
        "timezone": "Asia/Taipei",
        "points": points_out,
    }

def update_all():
    raw = fetch_all(max_workers=10)
    data = build_forecast_json(raw)
    out_path = os.path.join(CACHE_DIR, "forecast_data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"Saved {len(data['points'])} points to {out_path}")
    return data

if __name__ == "__main__":
    update_all()
