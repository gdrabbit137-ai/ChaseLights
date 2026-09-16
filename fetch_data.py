"""
ChaseLights — 天氣網格資料擷取模組

從 Open-Meteo API 擷取氣象網格資料，
包含能見度、雲量、溫度、露點、風速等攝影相關參數。
"""

import json, os, time, hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
import requests
from regions import get_spots

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
CACHE_TTL = 600  # 10 分鐘快取

# 確保快取目錄存在
os.makedirs(CACHE_DIR, exist_ok=True)

GRID_LATS = [21.8, 22.2, 22.6, 23.0, 23.4, 23.8, 24.2, 24.6, 25.0, 25.4, 25.8, 26.2]
GRID_LONS = [118.2, 118.6, 119.0, 119.4, 119.8, 120.2, 120.6, 121.0, 121.4, 121.8, 122.2, 122.6]

def build_grid_points():
    points = []
    for lat in GRID_LATS:
        for lon in GRID_LONS:
            points.append({"lat": round(lat, 1), "lon": round(lon, 1), "type": "grid"})
    return points

def build_spot_points(region="tw"):
    """從 regions.py 讀取景點，包含類別 category 資訊"""
    spots = get_spots(region)
    return [{
        "lat": round(s["lat"], 4),
        "lon": round(s["lon"], 4),
        "name": s["name"],
        "category": s.get("category", "本島"),
        "type": "spot"
    } for s in spots]

def merge_points(region="tw"):
    grid = build_grid_points()
    spots = build_spot_points(region)
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
    
    if "error" in raw_weather:
        return {"score": 0, "reason": "API 讀取失敗", "category": spot.get("category", "本島")}
        
    hourly = raw_weather.get("hourly", {})
    clouds = hourly.get("cloud_cover_low", [0])
    visibility = hourly.get("visibility", [10000])
    wind = hourly.get("wind_speed_10m", [0])

    avg_cloud = clouds[0] if clouds else 0
    vis_km = (visibility[0] / 1000.0) if visibility else 10
    wind_spd = wind[0] if wind else 0

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
        "category": spot.get("category", "本島"),
        "score": score,
        "best_time": "23:00",
        "position": f"雲量: {avg_cloud}% | 能見度: {vis_km:.1f}km",
        "reason": reason
    }

def fetch_all(region="tw", max_workers=10):
    points = merge_points(region)
    results = {}
    print(f"Fetching {len(points)} points for [{region}] with {max_workers} workers...")
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        fut_map = {}
        for p in points:
            fut = pool.submit(fetch_point, p["lat"], p["lon"], 3)
            fut_map[fut] = p
            time.sleep(0.02)
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
                    "category": p.get("category", "本島"),
                    "data": data,
                }
            except Exception as e:
                print(f" Failed: {p.get('name') or p} — {e}")
            done += 1
            if done % 10 == 0 or done == len(points):
                print(f" Progress: {done}/{len(points)}")
    return results

def update_all(region="tw"):
    raw = fetch_all(region=region, max_workers=10)
    print(f"Fetch completed for region {region}.")
    return raw

if __name__ == "__main__":
    update_all("tw")
