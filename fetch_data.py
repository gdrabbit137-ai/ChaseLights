import json
import urllib.request
import os
from datetime import datetime, timezone, timedelta

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

def calculate_spot_score(spot, item):
    tags = spot.get("tags", [])
    c_low = item.get("c_low", 0)
    c_mid = item.get("c_mid", 0)
    c_high = item.get("c_high", 0)
    pop = item.get("pop", 0)
    vis = item.get("vis", 10000)
    rh = item.get("rh", 50)
    wind = item.get("wind", 0)
    
    score = 100
    score -= (pop * 0.6)
    if vis < 15000:
        score -= ((15000 - vis) / 1000) * 1.0

    if "starlight" in tags or "aurora" in tags:
        cloud_penalty = (c_low * 0.9) + (c_mid * 0.7) + (c_high * 0.4)
        score -= cloud_penalty
        if rh > 85:
            score -= 10
    elif "cloud_sea" in tags:
        if 40 <= c_low <= 85 and rh >= 80:
            score += 10
        else:
            score -= 15
    else:
        cloud_penalty = (c_low * 0.6) + (c_mid * 0.4) + (c_high * 0.2)
        score -= cloud_penalty

    if wind > 8.0:
        score -= (wind - 8.0) * 2.0

    return max(20, min(99, int(score)))

def fetch_weather_for_spot(spot):
    lat = spot.get("lat")
    lon = spot.get("lon")
    
    if not lat or not lon:
        return {}

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=temperature_2m,dew_point_2m,relative_humidity_2m,cloud_cover_low,cloud_cover_mid,cloud_cover_high,wind_speed_10m,visibility,precipitation_probability"
            f"&forecast_days=3&timezone=auto"
        )
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            raw = json.loads(response.read().decode('utf-8'))
            
            hourly = raw.get("hourly", {})
            times = hourly.get("time", [])
            temps = hourly.get("temperature_2m", [])
            dews = hourly.get("dew_point_2m", [])
            rhs = hourly.get("relative_humidity_2m", [])
            c_lows = hourly.get("cloud_cover_low", [])
            c_mids = hourly.get("cloud_cover_mid", [])
            c_highs = hourly.get("cloud_cover_high", [])
            winds = hourly.get("wind_speed_10m", [])
            visibilities = hourly.get("visibility", [])
            pops = hourly.get("precipitation_probability", [])

            kp_info = fetch_noaa_kp()
            current_kp = kp_info["kp_index"] if kp_info else "-"

            # 強制使用 UTC+8 時間比對歷史時段，解決 GitHub Actions (UTC+0) 的 8 小時時差問題
            tz_tw = timezone(timedelta(hours=8))
            now_str = datetime.now(tz_tw).strftime("%Y-%m-%d %H:00")

            hourly_forecast = []
            for i in range(len(times)):
                t_str = times[i].replace("T", " ")
                temp = temps[i] if i < len(temps) else 0
                dew = dews[i] if i < len(dews) else 0
                
                estimated_cloud_base = max(100, int((temp - dew) * 125))

                item_data = {
                    "c_low": c_lows[i] if i < len(c_lows) else 0,
                    "c_mid": c_mids[i] if i < len(c_mids) else 0,
                    "c_high": c_highs[i] if i < len(c_highs) else 0,
                    "pop": pops[i] if i < len(pops) else 0,
                    "vis": visibilities[i] if i < len(visibilities) else 10000,
                    "rh": rhs[i] if i < len(rhs) else 50,
                    "wind": winds[i] if i < len(winds) else 0
                }
                
                score = calculate_spot_score(spot, item_data)

                if item_data["pop"] > 50:
                    status = "🌧️ 降雨風險高"
                    indicator = "🌧️ 攜帶雨具預防"
                elif visibilities[i] >= 20000 and (item_data["c_low"] + item_data["c_mid"]) < 20:
                    status = "☀️ 條件極佳"
                    indicator = "💎 極佳大氣通透度"
                elif item_data["rh"] >= 80 and 30 <= item_data["c_low"] <= 80:
                    status = "☁️ 雲海機率高"
                    indicator = "☁️ 翻騰雲海黃金期"
                elif item_data["wind"] > 8.0:
                    status = "💨 風速強勁"
                    indicator = "💨 強風注意腳架穩定"
                else:
                    status = "⛅ 氣象平穩"
                    indicator = "✅ 風和日麗良好"

                hourly_forecast.append({
                    "time": t_str,
                    "score": score,
                    "status": status,
                    "kp": current_kp,
                    "cloud_base": estimated_cloud_base,
                    "temp": temp,
                    "rh": item_data["rh"],
                    "c_low": item_data["c_low"],
                    "c_mid": item_data["c_mid"],
                    "c_high": item_data["c_high"],
                    "wind": item_data["wind"],
                    "visibility": round(item_data["vis"] / 1000, 1),
                    "key_indicator": indicator,
                    "is_past": t_str < now_str
                })

            future_items = [h for h in hourly_forecast if not h["is_past"]]
            search_pool = future_items if future_items else hourly_forecast
            best_item = max(search_pool, key=lambda x: x["score"]) if search_pool else {}

            return {
                "score": best_item.get("score", 50),
                "best_time": best_item.get("time", "12:00"),
                "reason": "多因子氣象權重分析",
                "position": best_item.get("status", "⛅ 多雲"),
                "key_indicator": best_item.get("key_indicator", "✅ 風和日麗良好"),
                "hourly_forecast": hourly_forecast
            }
    except Exception as e:
        print(f"Fetch weather error for {spot.get('name')}: {e}")
        return {}

def update_usa_weather():
    pass
