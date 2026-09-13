"""
PhotoWeather — 快取產生器（多區域版）
支援依區域 fetch 天氣資料，各區獨立快取
"""

import json, os, time, requests, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
REGIONS_DIR = os.path.dirname(os.path.abspath(__file__))
if REGIONS_DIR not in sys.path:
    sys.path.insert(0, REGIONS_DIR)

from regions import REGIONS

def fetch_one(lat, lon):
    """直接 request Open-Meteo API"""
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly=relative_humidity_2m,cloud_cover_low,cloud_cover_mid,cloud_cover_high,"
        f"wind_speed_10m,visibility,weather_code,precipitation_probability,"
        f"temperature_2m,dew_point_2m"
        f"&daily=sunrise,sunset,weather_code,precipitation_sum"
        f"&timezone=auto"
        f"&forecast_days=3"
    )
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return None


def build_region_cache(region_id):
    """為單一區域建立完整的快取"""
    region = REGIONS[region_id]
    lat_min, lat_max, lon_min, lon_max = region["grid_bounds"]
    step = region["grid_step"]
    spots = region["spots"]

    # 產出網格點
    grid = []
    lat = lat_min
    while lat <= lat_max:
        lon = lon_min
        while lon <= lon_max:
            grid.append((round(lat, 5), round(lon, 5), "grid", ""))
            lon = round(lon + step, 5)
        lat = round(lat + step, 5)

    all_points = spots + grid
    print(f"  {region_id}: {len(spots)} 個景點 + {len(grid)} 個網格點 = {len(all_points)} 總點")

    results = []
    done = 0
    with ThreadPoolExecutor(max_workers=15) as pool:
        fut_map = {}
        for pt in all_points:
            if len(pt) == 4:
                lat, lon, typ, name = pt
            else:
                lat, lon, name = pt
                typ = "spot"
            fut = pool.submit(fetch_one, lat, lon)
            fut_map[fut] = (lat, lon, typ, name)

        for fut in as_completed(fut_map):
            lat, lon, typ, name = fut_map[fut]
            try:
                data = fut.result()
                if data and "hourly" in data:
                    results.append({
                        "lat": lat, "lon": lon,
                        "type": typ, "name": name,
                        "elevation": data.get("elevation"),
                        "hourly": data["hourly"],
                        "daily": data.get("daily", {}),
                    })
            except:
                pass
            done += 1
            if done % 20 == 0:
                print(f"    {done}/{len(all_points)}")

    output = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "timezone": "Asia/Taipei",
        "region_id": region_id,
        "region_name_zh": region["name_zh"],
        "region_name_en": region["name_en"],
        "map_center": region["map_center"],
        "map_zoom": region["map_zoom"],
        "bounds": region["grid_bounds"],
        "points": results,
    }

    out_path = os.path.join(CACHE_DIR, f"forecast_{region_id}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False)
    print(f"  ✅ {out_path} ({len(results)} 筆)")

    # 記錄更新時間
    status_path = os.path.join(CACHE_DIR, "update_status.json")
    from datetime import datetime as _dt, timedelta as _td, timezone as _tz
    now_utc8 = _dt.now(_tz(_td(hours=8)))
    try:
        if os.path.exists(status_path):
            with open(status_path, "r", encoding="utf-8") as f:
                status = json.load(f)
        else:
            status = {}
        next_hour = (now_utc8.hour // 6 + 1) * 6
        next_dt = now_utc8.replace(hour=next_hour % 24, minute=0, second=0, microsecond=0)
        if next_hour >= 24:
            next_dt += _td(days=1)
            next_dt = next_dt.replace(hour=0)
        status[region_id] = {
            "last_update": now_utc8.isoformat(),
            "next_update": next_dt.isoformat(),
        }
        with open(status_path, "w", encoding="utf-8") as f:
            json.dump(status, f, ensure_ascii=False)
    except:
        pass

    return output


def main():
    regions = sys.argv[1:] if len(sys.argv) > 1 else ["tw"]
    os.makedirs(CACHE_DIR, exist_ok=True)

    for region_id in regions:
        if region_id not in REGIONS:
            print(f"❌ 未知區域: {region_id}，可選: {list(REGIONS.keys())}")
            continue
        print(f"\n📡 開始 fetch: {region_id} ({REGIONS[region_id]['name_zh']})")
        build_region_cache(region_id)

    print(f"\n✅ 全部完成！快取目錄: {CACHE_DIR}")


if __name__ == "__main__":
    main()