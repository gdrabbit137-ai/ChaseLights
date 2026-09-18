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

def evaluate_tag_condition(tag, item_data, hour):
    """
    核心演算法：依據單一攝影題材與晝夜時間（hour），評估當前氣象條件符合度
    """
    c_low = item_data.get("c_low", 0)
    c_mid = item_data.get("c_mid", 0)
    c_high = item_data.get("c_high", 0)
    pop = item_data.get("pop", 0)
    vis = item_data.get("vis", 10000)
    rh = item_data.get("rh", 50)
    wind = item_data.get("wind", 0)

    is_night = (hour >= 18 or hour < 6)

    score = 75
    status = "⛅ 氣象平穩"
    indicator = "✅ 風和日麗良好"

    # --- 1. 星空 / 極光 (starlight / aurora) ---
    if tag in ["starlight", "aurora"]:
        if not is_night:
            return 15, "☀️ 白天日光強烈", "☀️ 白天無法觀測極光" if tag == "aurora" else "☀️ 白天無法觀測星空"
        
        cloud_loss = (c_low * 0.9) + (c_mid * 0.7) + (c_high * 0.4)
        score = 100 - cloud_loss - (pop * 0.8)
        if rh > 85: score -= 15
        if vis < 15000: score -= ((15000 - vis) / 1000) * 1.2
        if wind > 7.0: score -= (wind - 7.0) * 2

        if tag == "aurora":
            kp_val = 0
            try:
                kp_val = float(item_data.get("kp", 0))
            except (ValueError, TypeError):
                kp_val = 0

            if kp_val >= 5:
                score += 15
                if score >= 70:
                    status = f"🔥 極光大爆發 (Kp {kp_val})"
                    indicator = "🌌 磁暴強烈且夜空視野良好"
                else:
                    status = f"☁️ 磁暴強烈但有雲 (Kp {kp_val})"
                    indicator = "☁️ 極光爆發中但被雲層遮蔽"
            elif score >= 85:
                status = "🌌 夜間極光視野清透"
                indicator = "💎 夜空無雲極適合追極光"
            elif score >= 60:
                status = "🌌 極光觀察條件普通"
                indicator = "⛅ 些許薄雲干擾"
            else:
                status = "☁️ 雲層過厚無視線"
                indicator = "☁️ 不宜觀測極光"
        else:
            if score >= 85:
                status = "🌌 銀河觀星極佳"
                indicator = "💎 零雲量大氣極通透"
            elif score >= 60:
                status = "✨ 星空條件普通"
                indicator = "⛅ 些許薄雲干擾"
            else:
                status = "☁️ 雲層過厚無視線"
                indicator = "☁️ 不宜觀星攝影"

    # --- 2. 雲海 / 琉璃光 (cloud_sea) ---
    elif tag == "cloud_sea":
        if rh >= 75 and 30 <= c_low <= 85 and pop < 30:
            score = 95 - (wind * 2)
            if 40 <= rh <= 95: score += 4
            status = "☁️ 翻騰雲海黃金期"
            indicator = "☁️ 水氣與低雲完美配合"
        elif rh >= 70 and (c_low > 85 or c_low < 30):
            score = 60
            status = "⛅ 雲霧條件普通"
            indicator = "⛅ 低雲高度或雲量稍偏"
        else:
            score = 30
            status = "☀️ 乾燥無雲海條件"
            indicator = "☀️ 大氣乾燥或無低雲"

    # --- 3. 迷霧森林 / 耶穌光 (forest) ---
    elif tag == "forest":
        if rh >= 80 and vis <= 8000 and wind <= 5.0:
            score = 96 - (wind * 3) - (pop * 0.4)
            status = "🌫️ 夢幻迷霧森林"
            indicator = "🌲 濃郁霧氣瀰漫林間"
        elif vis >= 15000 and c_low <= 30 and pop < 20 and not is_night:
            score = 90 - (wind * 2)
            status = "☀️ 森林斜射光極佳"
            indicator = "🌲 大氣通透耶穌光強"
        else:
            score = 65 - (pop * 0.5) - (c_low * 0.3)
            status = "🌲 森林一般氣象"
            indicator = "🌲 無特別霧氣或強光"

    # --- 4. 湖泊晨霧 / 靜止倒影 (lake) ---
    elif tag == "lake":
        if wind <= 4.0:
            if rh >= 80 and vis <= 10000 and (4 <= hour <= 8):
                score = 95
                status = "🌫️ 湖面夢幻晨霧"
                indicator = "🌊 湖面水氣飄渺極美"
            elif vis >= 15000 and (c_low + c_mid) < 30:
                score = 92
                status = "🪞 靜止鏡面倒影"
                indicator = "🌊 無風微波鏡面絕佳"
            else:
                score = 80
                status = "🌊 湖景條件良好"
                indicator = "🌊 風速微弱適合拍攝"
        else:
            score = 55 - (wind - 4.0) * 5
            status = "🌬️ 湖面風大波浪興起"
            indicator = "🌊 風速過強無倒影"

    # --- 5. 瀑布溪流 (waterfall) ---
    elif tag == "waterfall":
        if (c_low + c_mid) >= 40:
            score = 95 - (wind * 1.5)
            status = "🌊 瀑布漫射柔光"
            indicator = "💦 陰天無強光高反差"
        elif (c_low + c_mid) < 15 and not is_night:
            score = 65
            status = "☀️ 頂光強烈反差大"
            indicator = "☀️ 陽光過強對比過高"
        else:
            score = 80
            status = "💦 瀑布條件平穩"
            indicator = "💦 水流與光線良好"
        score -= (pop * 0.3)

    # --- 6. 海岸彩霞 / 晨昏 (coast) ---
    elif tag == "coast":
        is_twilight = (hour in [5, 6, 17, 18])
        if is_twilight and 20 <= (c_high + c_mid) <= 75 and c_low < 35 and pop < 20:
            score = 95 - (wind * 1.5)
            status = "🌅 暮光彩霞絕佳"
            indicator = "🌅 中高雲形成壯麗彩霞"
        elif c_low >= 70:
            score = 45
            status = "☁️ 海面低雲壓頂"
            indicator = "☁️ 遮蔽地平線視線"
        else:
            score = 75 - (pop * 0.6)
            status = "🌊 海景氣象常規"
            indicator = "🌊 大氣狀況平穩"

    # --- 7. 城市景觀 (city) ---
    elif tag == "city":
        score = 90 - (c_low * 0.5) - (pop * 0.7)
        if vis >= 15000: score += 8
        else: score -= ((15000 - vis) / 1000) * 1.5
        score -= max(0, wind - 8.0) * 2

        if is_night:
            if score >= 85:
                status = "🏙️ 璀璨夜景通透"
                indicator = "💎 城市燈火清晰無霧"
            elif score >= 60:
                status = "🌃 夜景條件普通"
                indicator = "⛅ 些許霧氣或輕微低雲"
            else:
                status = "☁️ 夜景視線受阻"
                indicator = "☁️ 低雲壓頂或濃霧"
        else:
            if score >= 85:
                status = "🏙️ 城市遠眺極佳"
                indicator = "💎 城市全景清晰通透"
            elif score >= 60:
                status = "🏙️ 城市景觀普通"
                indicator = "⛅ 大氣能見度平穩"
            else:
                status = "🌫️ 城市視線受阻"
                indicator = "🌫️ 霾害或能見度差"

    # --- 8. 山景展望 (mountain) ---
    else:
        score = 95 - (c_low * 0.6 + c_mid * 0.4) - (pop * 0.7)
        if vis >= 18000: score += 5
        else: score -= max(0, (15000 - vis) / 400)
        score -= max(0, wind - 8.0) * 2.5

        if is_night:
            if score >= 85:
                status = "🌙 夜間大氣清透"
                indicator = "🌌 高空無視線阻礙"
            elif score >= 60:
                status = "🌙 夜間氣象平穩"
                indicator = "⛅ 局部微雲干擾"
            else:
                status = "☁️ 夜間濃霧雲覆"
                indicator = "☁️ 視線受阻"
        else:
            if score >= 85:
                status = "☀️ 山景展望極佳"
                indicator = "🏔️ 遠眺群峰通透無瑕"
            elif score >= 60:
                status = "⛅ 山景氣象平穩"
                indicator = "⛅ 局部雲量普通"
            else:
                status = "☁️ 山區濃霧雲覆"
                indicator = "☁️ 展望受限無視線"

    if pop >= 50:
        score = min(score, 40)
        status = "🌧️ 降雨風險高"
        indicator = "🌧️ 雨勢明顯不宜外拍"

    return max(15, min(99, int(score))), status, indicator

def fetch_weather_for_spot(spot):
    lat = spot.get("lat")
    lon = spot.get("lon")
    tags = spot.get("tags", ["mountain"])
    
    if not lat or not lon:
        return {}

    try:
        # 加入 past_days=1 確保 API 回傳過去 24 小時資料
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=temperature_2m,dew_point_2m,relative_humidity_2m,cloud_cover_low,cloud_cover_mid,cloud_cover_high,wind_speed_10m,visibility,precipitation_probability"
            f"&forecast_days=3&past_days=1&timezone=auto"
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

            tz_tw = timezone(timedelta(hours=8))
            now_str = datetime.now(tz_tw).strftime("%Y-%m-%d %H:00")

            hourly_forecast = []
            for i in range(len(times)):
                t_str = times[i].replace("T", " ")
                
                time_part = t_str.split(" ")[1] if " " in t_str else "12:00"
                hour = int(time_part.split(":")[0])

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
                    "wind": winds[i] if i < len(winds) else 0,
                    "kp": current_kp
                }
                
                best_score = -1
                best_status = "⛅ 氣象平穩"
                best_indicator = "✅ 風和日麗良好"

                for tag in tags:
                    s, stat, ind = evaluate_tag_condition(tag, item_data, hour)
                    if s > best_score:
                        best_score = s
                        best_status = stat
                        best_indicator = ind

                hourly_forecast.append({
                    "time": t_str,
                    "score": best_score,
                    "status": best_status,
                    "kp": current_kp,
                    "cloud_base": estimated_cloud_base,
                    "temp": temp,
                    "rh": item_data["rh"],
                    "c_low": item_data["c_low"],
                    "c_mid": item_data["c_mid"],
                    "c_high": item_data["c_high"],
                    "wind": item_data["wind"],
                    "visibility": round(item_data["vis"] / 1000, 1),
                    "key_indicator": best_indicator,
                    "is_past": t_str < now_str
                })

            future_items = [h for h in hourly_forecast if not h["is_past"]]
            search_pool = future_items if future_items else hourly_forecast
            best_item = max(search_pool, key=lambda x: x["score"]) if search_pool else {}

            return {
                "score": best_item.get("score", 50),
                "best_time": best_item.get("time", "12:00"),
                "reason": "題材與晝夜動態氣象分析",
                "position": best_item.get("status", "⛅ 多雲"),
                "key_indicator": best_item.get("key_indicator", "✅ 風和日麗良好"),
                "hourly_forecast": hourly_forecast
            }
    except Exception as e:
        print(f"Fetch weather error for {spot.get('name')}: {e}")
        return {}

def update_usa_weather():
    pass
