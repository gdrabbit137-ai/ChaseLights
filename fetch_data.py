import json
import urllib.request
import os

def fetch_noaa_kp():
    url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if len(data) > 1:
                latest_entry = data[-1]
                return {
                    "kp_index": latest_entry[1],
                    "time": latest_entry[0]
                }
    except Exception as e:
        print(f"Failed to fetch NOAA Kp data: {e}")
    return None

def fetch_weather_for_spot(spot):
    """ 搭配 analyze_weather.py 呼叫介面 """
    lat = spot.get("lat")
    lon = spot.get("lon")
    
    if not lat or not lon:
        return {}

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=temperature_2m,relative_humidity_2m,cloud_cover_low,cloud_cover_mid,cloud_cover_high,wind_speed_10m,visibility"
            f"&forecast_days=3&timezone=auto"
        )
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            raw = json.loads(response.read().decode('utf-8'))
            
            hourly = raw.get("hourly", {})
            times = hourly.get("time", [])
            temps = hourly.get("temperature_2m", [])
            rhs = hourly.get("relative_humidity_2m", [])
            c_lows = hourly.get("cloud_cover_low", [])
            c_mids = hourly.get("cloud_cover_mid", [])
            c_highs = hourly.get("cloud_cover_high", [])
            winds = hourly.get("wind_speed_10m", [])
            visibilities = hourly.get("visibility", [])

            # 抓取即時 Kp 指數
            kp_info = fetch_noaa_kp()
            current_kp = kp_info["kp_index"] if kp_info else "-"

            hourly_forecast = []
            for i in range(len(times)):
                t_str = times[i].replace("T", " ")
                c_low = c_lows[i] if i < len(c_lows) else 0
                c_mid = c_mids[i] if i < len(c_mids) else 0
                c_high = c_highs[i] if i < len(c_highs) else 0
                
                total_cloud = (c_low + c_mid + c_high) / 3
                score = max(10, int(100 - total_cloud))
                status = "☀️ 晴朗" if total_cloud < 20 else ("⛅ 多雲" if total_cloud < 70 else "☁️ 陰天")

                hourly_forecast.append({
                    "time": t_str,
                    "score": score,
                    "status": status,
                    "kp": current_kp,
                    "cloud_base": 1000,
                    "temp": temps[i] if i < len(temps) else 0,
                    "rh": rhs[i] if i < len(rhs) else 0,
                    "c_low": c_low,
                    "c_mid": c_mid,
                    "c_high": c_high,
                    "wind": winds[i] if i < len(winds) else 0,
                    "visibility": round((visibilities[i] if i < len(visibilities) else 10000) / 1000, 1),
                    "is_past": False
                })

            best_item = max(hourly_forecast, key=lambda x: x["score"]) if hourly_forecast else {}

            return {
                "score": best_item.get("score", 50),
                "best_time": best_item.get("time", "12:00"),
                "reason": "氣象條件良好",
                "position": best_item.get("status", "☀️ 晴朗"),
                "hourly_forecast": hourly_forecast
            }
    except Exception as e:
        print(f"Fetch weather error for {spot.get('name')}: {e}")
        return {}

def update_usa_weather():
    pass
