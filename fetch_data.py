"""
ChaseLights — 天氣網格資料擷取模組 (含過去24H + 未來48H 專業攝影氣象欄位)
"""

import json, os, time, hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
import requests
from regions import get_spots

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
CACHE_TTL = 600  # 10 分鐘快取

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

def fetch_point(lat, lon, past_days=1, forecast_days=2):
    """抓取過去 24 小時 + 未來 48 小時氣象"""
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
        f"&past_days={past_days}"
        f"&forecast_days={forecast_days}"
        f"&timezone=Asia/Taipei"
    )
    try:
        resp = requests.get(url, timeout=15)
        data = resp.json()
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        return data
    except Exception as e:
        return {"error": str(e), "lat": lat, "lon": lon}

def calculate_cloud_base(temp, dew_point):
    """估算低雲雲底高度 (公尺) - 依據溫度與露點差 (Temp - DewPoint) * 125"""
    spread = max(0.0, temp - dew_point)
    return int(spread * 125)

def evaluate_hour_condition(c_low, c_mid, c_high, vis_km, wind_spd, prec_prob):
    """計算單時段專業評分與出景狀態"""
    score = 50
    status = "☁️ 條件普通"

    if prec_prob > 50:
        score = 15
        status = "🌧️ 降雨不佳"
    elif c_low < 30 and vis_km >= 15:
        score = 85
        status = "☀️ 晴朗通透"
    elif c_high > 40 and c_low < 30 and vis_km >= 12:
        score = 78
        status = "🌅 高雲彩霞"
    elif c_low > 70:
        score = 25
        status = "☁️ 濃雲籠罩"

    if wind_spd > 15:
        score = max(10, score - 15)
        status += " (強風警告)"

    return score, status

def fetch_weather_for_spot(spot):
    """供 analyze_weather.py 單點調用的標準介面"""
    lat = spot.get("lat")
    lon = spot.get("lon")
    raw_weather = fetch_point(lat, lon, past_days=1, forecast_days=2)
    
    if "error" in raw_weather:
        return {"score": 0, "reason": "API 讀取失敗", "category": spot.get("category", "本島"), "hourly_forecast": []}
        
    hourly = raw_weather.get("hourly", {})
    times = hourly.get("time", [])
    c_low_arr = hourly.get("cloud_cover_low", [])
    c_mid_arr = hourly.get("cloud_cover_mid", [])
    c_high_arr = hourly.get("cloud_cover_high", [])
    vis_arr = hourly.get("visibility", [])
    wind_arr = hourly.get("wind_speed_10m", [])
    temp_arr = hourly.get("temperature_2m", [])
    dew_arr = hourly.get("dew_point_2m", [])
    rh_arr = hourly.get("relative_humidity_2m", [])
    prec_arr = hourly.get("precipitation_probability", [])

    now_iso = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%dT%H:00")

    hourly_forecast = []
    max_score = 0
    best_time_str = "N/A"
    best_status = "條件普通"
    best_cloud_base = 500

    for i in range(len(times)):
        t_raw = times[i]
        t_formatted = t_raw.replace("T", " ")
        c_low = c_low_arr[i] if i < len(c_low_arr) else 0
        c_mid = c_mid_arr[i] if i < len(c_mid_arr) else 0
        c_high = c_high_arr[i] if i < len(c_high_arr) else 0
        v_val = (vis_arr[i] / 1000.0) if i < len(vis_arr) else 10.0
        w_val = wind_arr[i] if i < len(wind_arr) else 0.0
        tp_val = temp_arr[i] if i < len(temp_arr) else 0.0
        dw_val = dew_arr[i] if i < len(dew_arr) else 0.0
        rh_val = rh_arr[i] if i < len(rh_arr) else 0
        p_val = prec_arr[i] if i < len(prec_arr) else 0

        cloud_base = calculate_cloud_base(tp_val, dw_val)
        h_score, status = evaluate_hour_condition(c_low, c_mid, c_high, v_val, w_val, p_val)

        is_past = t_raw < now_iso

        if not is_past and h_score > max_score:
            max_score = h_score
            best_time_str = t_formatted.split(" ")[1]
            best_status = status
            best_cloud_base = cloud_base

        hourly_forecast.append({
            "time": t_formatted,
            "is_past": is_past,
            "score": h_score,
            "status": status,
            "cloud_base": cloud_base,
            "temp": round(tp_val, 1),
            "rh": rh_val,
            "c_low": c_low,
            "c_mid": c_mid,
            "c_high": c_high,
            "wind": round(w_val, 1),
            "visibility": round(v_val, 1)
        })

    return {
        "name": spot.get("name"),
        "category": spot.get("category", "本島"),
        "score": max_score if max_score > 0 else 30,
        "best_time": best_time_str,
        "position": f"{best_status} | 雲底高度 {best_cloud_base}m",
        "reason": f"預測最佳拍攝時段於 {best_time_str}，狀態：{best_status}",
        "hourly_forecast": hourly_forecast
    }

def fetch_all(region="tw", max_workers=10):
    points = merge_points(region)
    results = {}
    print(f"Fetching {len(points)} points for [{region}] with {max_workers} workers...")
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        fut_map = {}
        for p in points:
            fut = pool.submit(fetch_point, p["lat"], p["lon"], 1, 2)
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
    return raw

if __name__ == "__main__":
    update_all("tw")
