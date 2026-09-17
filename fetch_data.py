"""
ChaseLights — 天氣網格資料擷取模組 (含月相干擾與露點差雲海演算法)
"""

import json, os, time, hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
import requests
from regions import get_spots

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
CACHE_TTL = 600

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
        "tags": s.get("tags", ["mountain"]),
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

def fetch_point(lat, lon, past_days=1, forecast_days=2, retries=3):
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
        f"&daily=moon_phase"
        f"&past_days={past_days}"
        f"&forecast_days={forecast_days}"
        f"&timezone=auto"
    )

    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
                return data
            elif resp.status_code == 429:
                time.sleep(1.5 * (attempt + 1))
        except Exception:
            time.sleep(1.0 * (attempt + 1))

    return {"error": "API Limit or Timeout", "lat": lat, "lon": lon}

def calculate_cloud_base(temp, dew_point):
    spread = max(0.0, temp - dew_point)
    return int(spread * 125)

def evaluate_hour_condition(c_low, c_mid, c_high, vis_km, wind_spd, rh, temp, dew_point, prec_prob, hour=12, moon_phase=0.5, tags=None):
    """專業多標籤動態評分 (含月相干擾與露點差雲海)"""
    if not tags:
        tags = ["mountain"]

    if prec_prob > 50:
        return 15, "🌧️ 降雨不佳"

    candidates = []
    total_cloud = max(c_low, c_mid, c_high)
    dew_spread = max(0.0, temp - dew_point) # 露點差 (Dew Point Depression)

    # 🌊 1. 湖泊標籤 (lake)
    if "lake" in tags:
        if 5 <= hour <= 8 and wind_spd < 2.0:
            if rh >= 80:
                candidates.append((95, "🌫️ 湖面晨霧/斜射光"))
            else:
                candidates.append((88, "🏞️ 湖面靜止倒影"))

    # ☁️ 2. 雲海/琉璃光標籤 (cloud_sea)
    if "cloud_sea" in tags:
        # 雲海黃金條件：露點差 <= 2.5度 (水氣極度飽和)，低雲量在 30%-70% (不全白也不空)，風速低
        if dew_spread <= 2.5 and 30 <= c_low <= 75 and wind_spd < 3.5:
            if 18 <= hour or hour <= 6:
                candidates.append((94, "☁️ 經典高山瀑布雲海/琉璃光"))
            else:
                candidates.append((90, "☁️ 翻騰高山雲海"))

    # 🌲 3. 森林標籤 (forest)
    if "forest" in tags:
        if rh >= 85 and c_low >= 50 and wind_spd < 3.0:
            if 6 <= hour <= 9:
                candidates.append((92, "🌲 迷霧森林/耶穌光"))
            else:
                candidates.append((85, "🌲 夢幻迷霧森林"))

    # 🌌 4. 觀星/銀河標籤 (starlight) - 引入月相考量 (moon_phase: 0新月 ~ 0.5滿月)
    if "starlight" in tags:
        if (hour >= 21 or hour <= 4) and total_cloud < 15 and vis_km >= 15:
            # 月相干擾判斷: 0.15 以下接近新月，無月光干擾
            if moon_phase <= 0.15 or moon_phase >= 0.85:
                candidates.append((95, "🌌 絕佳無月光純淨銀河"))
            elif 0.35 <= moon_phase <= 0.65:
                candidates.append((70, "🌕 晴朗星空 (強烈月光干擾)"))
            else:
                candidates.append((88, "🌌 清透星空銀河"))

    # 🌌 5. 極光標籤 (aurora)
    if "aurora" in tags:
        if (hour >= 20 or hour <= 5) and total_cloud < 20 and prec_prob < 10:
            candidates.append((93, "🌌 夜間爆發極光出景"))

    # 🌊 6. 海岸/漁港標籤 (coast)
    if "coast" in tags:
        if (5 <= hour <= 7 or 17 <= hour <= 19) and c_high > 30 and c_low < 40:
            candidates.append((88, "🌅 海岸晨昏大霞"))

    # 🏔️ 7. 通用 / 高山觀景標籤 (mountain/default)
    if c_low < 30 and vis_km >= 15:
        candidates.append((85, "☀️ 晴朗通透"))
    elif c_high > 40 and c_low < 30 and vis_km >= 12:
        candidates.append((78, "🌅 高雲彩霞"))
    elif c_low > 70:
        candidates.append((25, "☁️ 濃雲籠罩"))
    else:
        candidates.append((50, "☁️ 條件普通"))

    best_score, best_status = max(candidates, key=lambda x: x[0])

    if wind_spd > 15:
        best_score = max(10, best_score - 20)
        best_status += " (強風警告)"

    return best_score, best_status

def fetch_weather_for_spot(spot):
    lat = spot.get("lat")
    lon = spot.get("lon")
    tags = spot.get("tags", ["mountain"])
    raw_weather = fetch_point(lat, lon, past_days=1, forecast_days=2)
    
    if "error" in raw_weather:
        return {
            "name": spot.get("name"),
            "category": spot.get("category", "本島"),
            "tags": tags,
            "score": 0,
            "best_time": "N/A",
            "position": "資料擷取失敗",
            "reason": "API 讀取失敗（請稍後重新整理）",
            "hourly_forecast": []
        }
        
    hourly = raw_weather.get("hourly", {})
    daily = raw_weather.get("daily", {})
    moon_phases = daily.get("moon_phase", [0.5, 0.5, 0.5])
    today_moon_phase = moon_phases[1] if len(moon_phases) > 1 else 0.5

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
        hour_val = int(t_raw.split("T")[1].split(":")[0]) if "T" in t_raw else 12

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
        h_score, status = evaluate_hour_condition(
            c_low, c_mid, c_high, v_val, w_val, rh_val, tp_val, dw_val, p_val,
            hour=hour_val, moon_phase=today_moon_phase, tags=tags
        )

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
        "tags": tags,
        "score": max_score if max_score > 0 else 30,
        "best_time": best_time_str,
        "position": f"{best_status} | 雲底高度 {best_cloud_base}m",
        "reason": f"預測最佳拍攝時段於 {best_time_str}，狀態：{best_status}",
        "hourly_forecast": hourly_forecast
    }

def fetch_all(region="tw", max_workers=5):
    points = merge_points(region)
    results = {}
    print(f"Fetching {len(points)} points for [{region}] with {max_workers} workers...")
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        fut_map = {}
        for p in points:
            fut = pool.submit(fetch_point, p["lat"], p["lon"], 1, 2)
            fut_map[fut] = p
            time.sleep(0.05)
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
                    "tags": p.get("tags", ["mountain"]),
                    "data": data,
                }
            except Exception as e:
                print(f" Failed: {p.get('name') or p} — {e}")
            done += 1
            if done % 10 == 0 or done == len(points):
                print(f" Progress: {done}/{len(points)}")
    return results

def update_all(region="tw"):
    raw = fetch_all(region=region, max_workers=5)
    return raw

if __name__ == "__main__":
    update_all("tw")
