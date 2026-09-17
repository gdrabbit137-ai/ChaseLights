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

def calculate_spot_score(spot, item):
    """ 依據景點主題標籤與即時氣象進行動態加扣分 """
    tags = spot.get("tags", [])
    c_low = item.get("c_low", 0)
    c_mid = item.get("c_mid", 0)
    c_high = item.get("c_high", 0)
    pop = item.get("pop", 0)
    vis = item.get("vis", 10000)
    rh = item.get("rh", 50)
    wind = item.get("wind", 0)
    
    score = 100
    
    # 基礎降雨與能見度扣分
    score -= (pop * 0.7)
    if vis < 15000:
        score -= ((15000 - vis) / 1000) * 1.2

    # 針對不同攝影題材進行客製化條件評估
    if "starlight" in tags or "aurora" in tags:
        # 星空/極光：極度依賴無雲與低濕度
        cloud_penalty = (c_low * 1.0) + (c_mid * 0.9) + (c_high * 0.5)
        score -= cloud_penalty
        if rh > 85:
            score -= 15
    elif "cloud_sea" in tags:
        # 雲海：需要高濕度與適當中低雲量
        if 40 <= c_low <= 85 and rh >= 80:
            score += 10
        else:
            score -= 20
    else:
        # 一般風景/高山：常規雲量扣分
        cloud_penalty = (c_low * 0.8) + (c_mid * 0.5) + (c_high * 0.2)
        score -= cloud_penalty

    # 強風扣分 (影響長曝腳架穩定度)
    if wind > 8.0:
        score -= (wind - 8.0) * 3.0

    return max(15, min(98, int(score)))

def fetch_weather_for_spot(spot):
    lat = spot.get("lat")
    lon = spot.get("lon")
    
    if not lat or not lon:
        return {}

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=temperature_2m,relative_humidity_2m,cloud_cover_low,cloud_cover_mid,cloud_cover_high,wind_speed_10m,visibility,precipitation_probability"
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
            pops = hourly.get("precipitation_probability", [])

            kp_info = fetch_noaa_kp()
            current_kp = kp_info["kp_index"] if kp_info else "-"

            hourly_forecast = []
            for i in range(len(times)):
                t_str = times[i].replace("T", " ")
                item_data = {
                    "c_low": c_lows[i] if i < len(c_lows) else 0,
                    "c_mid": c_mids[i] if i < len(c_mids) else 0,
                    "c_high": c_highs[i] if i < len(c_highs) else 0,
                    "pop": pops[i] if i < len(pops) else 0,
                    "vis": visibilities[i] if i < len(visibilities) else 10000,
                    "rh": rhs[i] if i < len(rhs) else 50,
                    "wind": winds[i] if i < len(winds) else 0
                }
                
                # 計算動態分數
                score = calculate_spot_score(spot, item_data)

                if item_data["pop"] > 40:
                    status = "🌧️ 降雨風險高"
                elif score >= 80:
                    status = "☀️ 條件優良"
                elif score >= 55:
                    status = "⛅ 條件普通"
                else:
                    status = "☁️ 出景機率低"

                hourly_forecast.append({
                    "time": t_str,
                    "score": score,
                    "status": status,
                    "kp": current_kp,
                    "cloud_base": 1000,
                    "temp": temps[i] if i < len(temps) else 0,
                    "rh": item_data["rh"],
                    "c_low": item_data["c_low"],
                    "c_mid": item_data["c_mid"],
                    "c_high": item_data["c_high"],
                    "wind": item_data["wind"],
                    "visibility": round(item_data["vis"] / 1000, 1),
                    "is_past": False
                })

            # 計算當前黃金視窗（平均權重而非極端單一最高分）
            sorted_items = sorted(hourly_forecast, key=lambda x: x["score"], reverse=True)
            best_item = sorted_items[0] if sorted_items else {}

            return {
                "score": best_item.get("score", 50),
                "best_time": best_item.get("time", "12:00"),
                "reason": "多因子氣象權重分析",
                "position": best_item.get("status", "⛅ 多雲"),
                "hourly_forecast": hourly_forecast
            }
    except Exception as e:
        print(f"Fetch weather error for {spot.get('name')}: {e}")
        return {}

def update_usa_weather():
    pass
