import json
import urllib.request
import os
from datetime import datetime, timezone, timedelta

# 後端多國語言狀態與指標字典
I18N_MESSAGES = {
    # 狀態 (Status)
    "MOUNTAIN_EXCELLENT_DAY": {"zh-TW": "☀️ 山景展望極佳", "en": "☀️ Excellent Mountain View", "ja": "☀️ 最高の山岳展望"},
    "MOUNTAIN_STABLE_DAY": {"zh-TW": "⛅ 山景氣象平穩", "en": "⛅ Stable Mountain Weather", "ja": "⛅ 安定した山岳気象"},
    "MOUNTAIN_FOG_DAY": {"zh-TW": "☁️ 山區濃霧雲覆", "en": "☁️ Heavy Fog / Clouds", "ja": "☁️ 山間部の濃霧・雲覆"},
    "MOUNTAIN_EXCELLENT_NIGHT": {"zh-TW": "🌙 夜間大氣清透", "en": "🌙 Clear Night Sky", "ja": "🌙 清透な夜間大気"},
    "MOUNTAIN_STABLE_NIGHT": {"zh-TW": "🌙 夜間氣象平穩", "en": "🌙 Stable Night Weather", "ja": "🌙 穏やかな夜間気象"},
    "MOUNTAIN_FOG_NIGHT": {"zh-TW": "☁️ 夜間濃霧雲覆", "en": "☁️ Night Fog / Clouds", "ja": "☁️ 夜間の濃霧・雲覆"},
    "CLOUD_SEA_GOLD": {"zh-TW": "☁️ 翻騰雲海黃金期", "en": "☁️ Prime Sea of Clouds", "ja": "☁️ 黄金の雲海期"},
    "CLOUD_SEA_FAIR": {"zh-TW": "⛅ 雲霧條件普通", "en": "⛅ Moderate Cloud & Fog", "ja": "⛅ 普通の雲霧条件"},
    "CLOUD_SEA_DRY": {"zh-TW": "☀️ 乾燥無雲海條件", "en": "☀️ Dry / No Sea of Clouds", "ja": "☀️ 乾燥・雲海条件なし"},
    "FOREST_MIST": {"zh-TW": "🌫️ 夢幻迷霧森林", "en": "🌫️ Mystical Mist Forest", "ja": "🌫️ 幻想的な霧の森林"},
    "FOREST_LIGHT": {"zh-TW": "☀️ 森林斜射光極佳", "en": "☀️ Great Forest Sunbeams", "ja": "☀️ 最高の光線・木漏れ日"},
    "FOREST_NORMAL": {"zh-TW": "🌲 森林一般氣象", "en": "🌲 Normal Forest Weather", "ja": "🌲 通常の森林気象"},
    "LAKE_MIST": {"zh-TW": "🌫️ 湖面夢幻晨霧", "en": "🌫️ Misty Lake Morning", "ja": "🌫️ 幻想的な湖畔の朝霧"},
    "LAKE_MIRROR": {"zh-TW": "🪞 靜止鏡面倒影", "en": "🪞 Mirror Reflection", "ja": "🪞 鏡面の水面倒影"},
    "LAKE_GOOD": {"zh-TW": "🌊 湖景條件良好", "en": "🌊 Good Lake Conditions", "ja": "🌊 良好な湖畔条件"},
    "LAKE_WINDY": {"zh-TW": "🌬️ 湖面風大波浪興起", "en": "🌬️ Windy Lake / Waves", "ja": "🌬️ 強風による波立ち"},
    "WATERFALL_SOFT": {"zh-TW": "🌊 瀑布漫射柔光", "en": "🌊 Soft Light Waterfall", "ja": "🌊 拡散光の滝景"},
    "WATERFALL_HARSH": {"zh-TW": "☀️ 頂光強烈反差大", "en": "☀️ Harsh Direct Sunlight", "ja": "☀️ 強い直射光・高コントラスト"},
    "WATERFALL_NORMAL": {"zh-TW": "💦 瀑布條件平穩", "en": "💦 Stable Waterfall Weather", "ja": "💦 安定した滝条件"},
    "COAST_GLOW": {"zh-TW": "🌅 暮光彩霞絕佳", "en": "🌅 Stunning Sunset Glow", "ja": "🌅 素晴らしい夕焼け"},
    "COAST_LOW_CLOUD": {"zh-TW": "☁️ 海面低雲壓頂", "en": "☁️ Low Coastal Clouds", "ja": "☁️ 沿岸の低雲覆蓋"},
    "COAST_NORMAL": {"zh-TW": "🌊 海景氣象常規", "en": "🌊 Normal Coastal Weather", "ja": "🌊 通常の沿岸気象"},
    "CITY_NIGHT_CLEAR": {"zh-TW": "🏙️ 璀璨夜景通透", "en": "🏙️ Clear City Night View", "ja": "🏙️ 清晰な都市夜景"},
    "CITY_NIGHT_FAIR": {"zh-TW": "🌃 夜景條件普通", "en": "🌃 Fair City Night View", "ja": "🌃 普通の夜景条件"},
    "CITY_NIGHT_POOR": {"zh-TW": "☁️ 夜景視線受阻", "en": "☁️ Obstructed Night View", "ja": "☁️ 視界不順の夜景"},
    "CITY_DAY_CLEAR": {"zh-TW": "🏙️ 城市遠眺極佳", "en": "🏙️ Excellent City Panorama", "ja": "🏙️ 最高の都市遠望"},
    "CITY_DAY_FAIR": {"zh-TW": "🏙️ 城市景觀普通", "en": "🏙️ Normal City View", "ja": "🏙️ 普通の都市景觀"},
    "CITY_DAY_POOR": {"zh-TW": "🌫️ 城市視線受阻", "en": "🌫️ Obstructed City View", "ja": "🌫️ 視界不順の都市景觀"},
    "STARLIGHT_GREAT": {"zh-TW": "🌌 銀河觀星極佳", "en": "🌌 Excellent Stargazing", "ja": "🌌 最高の星空・天の川"},
    "STARLIGHT_FAIR": {"zh-TW": "✨ 星空條件普通", "en": "✨ Moderate Stargazing", "ja": "✨ 普通の星空条件"},
    "STARLIGHT_POOR": {"zh-TW": "☁️ 雲層過厚無視線", "en": "☁️ Heavy Cloud Cover", "ja": "☁️ 厚い雲（視界不可）"},
    "AURORA_CLEAR": {"zh-TW": "🌌 夜間極光視野清透", "en": "🌌 Clear Aurora View", "ja": "🌌 清透なオーロラ視界"},
    "AURORA_FAIR": {"zh-TW": "🌌 極光觀察條件普通", "en": "🌌 Fair Aurora Conditions", "ja": "🌌 普通のオーロラ条件"},
    "AURORA_POOR": {"zh-TW": "☁️ 雲層過厚無視線", "en": "☁️ Heavy Cloud Cover", "ja": "☁️ 厚い雲（視界不可）"},
    "DAYLIGHT_ONLY": {"zh-TW": "☀️ 白天日光強烈", "en": "☀️ Bright Daylight", "ja": "☀️ 強烈な日光（昼間）"},
    "RAIN_RISK": {"zh-TW": "🌧️ 降雨風險高", "en": "🌧️ High Rain Risk", "ja": "🌧️ 高い降雨リスク"},
    "STABLE_WEATHER": {"zh-TW": "⛅ 氣象平穩", "en": "⛅ Stable Weather", "ja": "⛅ 安定した気象"},

    # 關鍵指標 (Indicator)
    "IND_PEAKS": {"zh-TW": "🏔️ 遠眺群峰通透無瑕", "en": "Clear View of Distant Peaks", "ja": "遠くの連峰まで超高透明度"},
    "IND_CLEAR_SKY": {"zh-TW": "💎 零雲量大氣極通透", "en": "💎 Clear Sky & High Visibility", "ja": "💎 快晴・極めて高い透明度"},
    "IND_SOME_CLOUDS": {"zh-TW": "⛅ 些許薄雲干擾", "en": "⛅ Slight Cloud Interference", "ja": "⛅ 薄雲による僅かな影響"},
    "IND_NO_STAR": {"zh-TW": "☁️ 不宜觀星攝影", "en": "☁️ Not Suitable for Stargazing", "ja": "☁️ 星空撮影に不適"},
    "IND_CLOUD_SEA": {"zh-TW": "☁️ 水氣與低雲完美配合", "en": "☁️ Perfect Moisture & Low Clouds", "ja": "☁️ 水蒸気と低雲の最適な調和"},
    "IND_CLOUD_SEA_SUB": {"zh-TW": "⛅ 低雲高度或雲量稍偏", "en": "⛅ Suboptimal Cloud Height/Amount", "ja": "⛅ 雲量または高度がやや偏斜"},
    "IND_DRY_AIR": {"zh-TW": "☀️ 大氣乾燥或無低雲", "en": "☀️ Dry Air / No Low Clouds", "ja": "☀️ 乾燥大氣・低雲なし"},
    "IND_FOREST_MIST": {"zh-TW": "🌲 濃郁霧氣瀰漫林間", "en": "🌲 Dense Mist Through Forest", "ja": "🌲 森林に立ち込める濃霧"},
    "IND_FOREST_SUN": {"zh-TW": "🌲 大氣通透耶穌光強", "en": "🌲 Clear Air & Strong Sunbeams", "ja": "🌲 高透明度・強い木漏れ日"},
    "IND_FOREST_NORM": {"zh-TW": "🌲 無特別霧氣或強光", "en": "🌲 Regular Forest Lighting", "ja": "🌲 特段の霧や強光なし"},
    "IND_LAKE_MIST": {"zh-TW": "🌊 湖面水氣飄渺極美", "en": "🌊 Ethereal Lake Mist", "ja": "🌊 湖面上に漂う幻想的な朝霧"},
    "IND_LAKE_MIRROR": {"zh-TW": "🌊 無風微波鏡面絕佳", "en": "🌊 Calm Water & Perfect Reflection", "ja": "🌊 無風・鏡面の絶景"},
    "IND_LAKE_GOOD": {"zh-TW": "🌊 風速微弱適合拍攝", "en": "🌊 Gentle Wind / Good Shooting", "ja": "🌊 微風・撮影に最適"},
    "IND_LAKE_WIND": {"zh-TW": "🌊 風速過強無倒影", "en": "🌊 High Winds / No Reflection", "ja": "🌊 強風・倒影なし"},
    "IND_WATERFALL_SOFT": {"zh-TW": "💦 陰天無強光高反差", "en": "💦 Overcast / Soft Lighting", "ja": "💦 曇天・拡散光で撮影好適"},
    "IND_WATERFALL_HARSH": {"zh-TW": "☀️ 陽光過強對比過高", "en": "☀️ Harsh Sunlight / High Contrast", "ja": "☀️ 直射日光・高コントラスト"},
    "IND_WATERFALL_NORM": {"zh-TW": "💦 水流與光線良好", "en": "💦 Good Water Flow & Lighting", "ja": "💦 水流と光の條件良好"},
    "IND_COAST_GLOW": {"zh-TW": "🌅 中高雲形成壯麗彩霞", "en": "🌅 Sunset Glow with Mid/High Clouds", "ja": "🌅 中高層雲による見事な夕焼け"},
    "IND_COAST_BLOCK": {"zh-TW": "☁️ 遮蔽地平線視線", "en": "☁️ Obstructed Horizon View", "ja": "☁️ 地平線視界の遮蔽"},
    "IND_COAST_NORM": {"zh-TW": "🌊 大氣狀況平穩", "en": "🌊 Stable Atmospheric Conditions", "ja": "🌊 安定した大気状態"},
    "IND_CITY_NIGHT_CLEAR": {"zh-TW": "💎 城市燈火清晰無霧", "en": "💎 Clear City Lights", "ja": "💎 霧なし・クリアな街の灯り"},
    "IND_CITY_NIGHT_HAZE": {"zh-TW": "⛅ 些許霧氣或輕微低雲", "en": "⛅ Slight Haze / Low Clouds", "ja": "⛅ 僅かな霧または低雲"},
    "IND_CITY_NIGHT_BLOCK": {"zh-TW": "☁️ 低雲壓頂或濃霧", "en": "☁️ Low Clouds / Dense Fog", "ja": "☁️ 低雲または濃霧覆蓋"},
    "IND_CITY_DAY_CLEAR": {"zh-TW": "💎 城市全景清晰通透", "en": "💎 Crystal Clear City Panorama", "ja": "💎 クリアな都市パノラマ"},
    "IND_CITY_DAY_FAIR": {"zh-TW": "⛅ 大氣能見度平穩", "en": "⛅ Fair Atmospheric Visibility", "ja": "⛅ 安定した視程"},
    "IND_CITY_DAY_HAZE": {"zh-TW": "🌫️ 霾害或能見度差", "en": "🌫️ Haze or Poor Visibility", "ja": "🌫️ 煙霧または不鮮明な視程"},
    "IND_NIGHT_CLEAR": {"zh-TW": "🌌 高空無視線阻礙", "en": "🌌 Clear High-Altitude View", "ja": "🌌 上空の視界良好"},
    "IND_RAIN_RISK": {"zh-TW": "🌧️ 雨勢明顯不宜外拍", "en": "🌧️ Significant Rain / Avoid Shooting", "ja": "🌧️ 明らかな雨・屋外撮影不適"},
    "IND_DEFAULT": {"zh-TW": "✅ 風和日麗良好", "en": "✅ Good Weather Conditions", "ja": "✅ 良好な天候"}
}

def get_text(key, lang="zh-TW"):
    return I18N_MESSAGES.get(key, {}).get(lang, I18N_MESSAGES.get(key, {}).get("zh-TW", ""))

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

def evaluate_tag_condition(tag, item_data, hour, lang="zh-TW"):
    c_low = item_data.get("c_low", 0)
    c_mid = item_data.get("c_mid", 0)
    c_high = item_data.get("c_high", 0)
    pop = item_data.get("pop", 0)
    vis = item_data.get("vis", 10000)
    rh = item_data.get("rh", 50)
    wind = item_data.get("wind", 0)

    is_night = (hour >= 18 or hour < 6)

    score = 75
    status_key = "STABLE_WEATHER"
    indicator_key = "IND_DEFAULT"

    # 1. 星空 / 極光
    if tag in ["starlight", "aurora"]:
        if not is_night:
            ind_k = "IND_NO_STAR" if tag == "starlight" else "IND_DEFAULT"
            return 15, get_text("DAYLIGHT_ONLY", lang), get_text(ind_k, lang)
        
        cloud_loss = (c_low * 0.9) + (c_mid * 0.7) + (c_high * 0.4)
        score = 100 - cloud_loss - (pop * 0.8)
        if rh > 85: score -= 15
        if vis < 15000: score -= ((15000 - vis) / 1000) * 1.2
        if wind > 7.0: score -= (wind - 7.0) * 2

        if tag == "aurora":
            kp_val = 0
            try: kp_val = float(item_data.get("kp", 0))
            except (ValueError, TypeError): kp_val = 0

            if kp_val >= 5:
                score += 15
                if score >= 70:
                    status = f"🔥 Aurora Outbreak (Kp {kp_val})" if lang == 'en' else (f"🔥 オーロラ大爆発 (Kp {kp_val})" if lang == 'ja' else f"🔥 極光大爆發 (Kp {kp_val})")
                    indicator = get_text("IND_CLEAR_SKY", lang)
                else:
                    status = f"☁️ Storm but Cloudy (Kp {kp_val})" if lang == 'en' else (f"☁️ 磁気嵐だが雲あり (Kp {kp_val})" if lang == 'ja' else f"☁️ 磁暴強烈但有雲 (Kp {kp_val})")
                    indicator = get_text("IND_NO_STAR", lang)
                return max(15, min(99, int(score))), status, indicator
            elif score >= 85:
                status_key, indicator_key = "AURORA_CLEAR", "IND_CLEAR_SKY"
            elif score >= 60:
                status_key, indicator_key = "AURORA_FAIR", "IND_SOME_CLOUDS"
            else:
                status_key, indicator_key = "AURORA_POOR", "IND_NO_STAR"
        else:
            if score >= 85: status_key, indicator_key = "STARLIGHT_GREAT", "IND_CLEAR_SKY"
            elif score >= 60: status_key, indicator_key = "STARLIGHT_FAIR", "IND_SOME_CLOUDS"
            else: status_key, indicator_key = "STARLIGHT_POOR", "IND_NO_STAR"

    # 2. 雲海
    elif tag == "cloud_sea":
        if rh >= 75 and 30 <= c_low <= 85 and pop < 30:
            score = 95 - (wind * 2)
            if 40 <= rh <= 95: score += 4
            status_key, indicator_key = "CLOUD_SEA_GOLD", "IND_CLOUD_SEA"
        elif rh >= 70 and (c_low > 85 or c_low < 30):
            score = 60
            status_key, indicator_key = "CLOUD_SEA_FAIR", "IND_CLOUD_SEA_SUB"
        else:
            score = 30
            status_key, indicator_key = "CLOUD_SEA_DRY", "IND_DRY_AIR"

    # 3. 森林
    elif tag == "forest":
        if rh >= 80 and vis <= 8000 and wind <= 5.0:
            score = 96 - (wind * 3) - (pop * 0.4)
            status_key, indicator_key = "FOREST_MIST", "IND_FOREST_MIST"
        elif vis >= 15000 and c_low <= 30 and pop < 20 and not is_night:
            score = 90 - (wind * 2)
            status_key, indicator_key = "FOREST_LIGHT", "IND_FOREST_SUN"
        else:
            score = 65 - (pop * 0.5) - (c_low * 0.3)
            status_key, indicator_key = "FOREST_NORMAL", "IND_FOREST_NORM"

    # 4. 湖景
    elif tag == "lake":
        if wind <= 4.0:
            if rh >= 80 and vis <= 10000 and (4 <= hour <= 8):
                score = 95
                status_key, indicator_key = "LAKE_MIST", "IND_LAKE_MIST"
            elif vis >= 15000 and (c_low + c_mid) < 30:
                score = 92
                status_key, indicator_key = "LAKE_MIRROR", "IND_LAKE_MIRROR"
            else:
                score = 80
                status_key, indicator_key = "LAKE_GOOD", "IND_LAKE_GOOD"
        else:
            score = 55 - (wind - 4.0) * 5
            status_key, indicator_key = "LAKE_WINDY", "IND_LAKE_WIND"

    # 5. 瀑布
    elif tag == "waterfall":
        if (c_low + c_mid) >= 40:
            score = 95 - (wind * 1.5)
            status_key, indicator_key = "WATERFALL_SOFT", "IND_WATERFALL_SOFT"
        elif (c_low + c_mid) < 15 and not is_night:
            score = 65
            status_key, indicator_key = "WATERFALL_HARSH", "IND_WATERFALL_HARSH"
        else:
            score = 80
            status_key, indicator_key = "WATERFALL_NORMAL", "IND_WATERFALL_NORM"
        score -= (pop * 0.3)

    # 6. 海岸
    elif tag == "coast":
        is_twilight = (hour in [5, 6, 17, 18])
        if is_twilight and 20 <= (c_high + c_mid) <= 75 and c_low < 35 and pop < 20:
            score = 95 - (wind * 1.5)
            status_key, indicator_key = "COAST_GLOW", "IND_COAST_GLOW"
        elif c_low >= 70:
            score = 45
            status_key, indicator_key = "COAST_LOW_CLOUD", "IND_COAST_BLOCK"
        else:
            score = 75 - (pop * 0.6)
            status_key, indicator_key = "COAST_NORMAL", "IND_COAST_NORM"

    # 7. 城市
    elif tag == "city":
        score = 90 - (c_low * 0.5) - (pop * 0.7)
        if vis >= 15000: score += 8
        else: score -= ((15000 - vis) / 1000) * 1.5
        score -= max(0, wind - 8.0) * 2

        if is_night:
            if score >= 85: status_key, indicator_key = "CITY_NIGHT_CLEAR", "IND_CITY_NIGHT_CLEAR"
            elif score >= 60: status_key, indicator_key = "CITY_NIGHT_FAIR", "IND_CITY_NIGHT_HAZE"
            else: status_key, indicator_key = "CITY_NIGHT_POOR", "IND_CITY_NIGHT_BLOCK"
        else:
            if score >= 85: status_key, indicator_key = "CITY_DAY_CLEAR", "IND_CITY_DAY_CLEAR"
            elif score >= 60: status_key, indicator_key = "CITY_DAY_FAIR", "IND_CITY_DAY_FAIR"
            else: status_key, indicator_key = "CITY_DAY_POOR", "IND_CITY_DAY_HAZE"

    # 8. 山景
    else:
        score = 95 - (c_low * 0.6 + c_mid * 0.4) - (pop * 0.7)
        if vis >= 18000: score += 5
        else: score -= max(0, (15000 - vis) / 400)
        score -= max(0, wind - 8.0) * 2.5

        if is_night:
            if score >= 85: status_key, indicator_key = "MOUNTAIN_EXCELLENT_NIGHT", "IND_NIGHT_CLEAR"
            elif score >= 60: status_key, indicator_key = "MOUNTAIN_STABLE_NIGHT", "IND_SOME_CLOUDS"
            else: status_key, indicator_key = "MOUNTAIN_FOG_NIGHT", "IND_NO_STAR"
        else:
            if score >= 85: status_key, indicator_key = "MOUNTAIN_EXCELLENT_DAY", "IND_PEAKS"
            elif score >= 60: status_key, indicator_key = "MOUNTAIN_STABLE_DAY", "IND_SOME_CLOUDS"
            else: status_key, indicator_key = "MOUNTAIN_FOG_DAY", "IND_NO_STAR"

    if pop >= 50:
        score = min(score, 40)
        status_key, indicator_key = "RAIN_RISK", "IND_RAIN_RISK"

    return max(15, min(99, int(score))), get_text(status_key, lang), get_text(indicator_key, lang)

def fetch_weather_for_spot(spot, lang="zh-TW"):
    lat = spot.get("lat")
    lon = spot.get("lon")
    tags = spot.get("tags", ["mountain"])
    
    if not lat or not lon:
        return {}

    try:
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
                best_status = get_text("STABLE_WEATHER", lang)
                best_indicator = get_text("IND_DEFAULT", lang)

                for tag in tags:
                    s, stat, ind = evaluate_tag_condition(tag, item_data, hour, lang)
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
                "reason": "Adaptive Weather Analysis",
                "position": best_item.get("status", get_text("STABLE_WEATHER", lang)),
                "key_indicator": best_item.get("key_indicator", get_text("IND_DEFAULT", lang)),
                "hourly_forecast": hourly_forecast
            }
    except Exception as e:
        print(f"Fetch weather error for {spot.get('name')}: {e}")
        return {}

def update_usa_weather(): pass
