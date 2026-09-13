import sys, requests, json

# 天氣現象代碼對照表（WMO Code）
WMO_CODES = {
    0:  "☀️ 晴天",
    1:  "🌤️ 多雲轉晴",
    2:  "⛅ 局部多雲",
    3:  "☁️ 陰天",
    45: "🌫️ 霧",
    48: "🌫️ 霧淞",
    51: "🌦️ 小毛毛雨",
    53: "🌦️ 中毛毛雨",
    55: "🌧️ 大毛毛雨",
    56: "🌧️ 小凍雨",
    57: "🌧️ 大凍雨",
    61: "🌧️ 小雨",
    63: "🌧️ 中雨",
    65: "🌧️ 大雨",
    66: "🌧️ 小凍雨",
    67: "🌧️ 大凍雨",
    71: "🌨️ 小雪",
    73: "🌨️ 中雪",
    75: "❄️ 大雪",
    77: "❄️ 雪粒",
    80: "🌦️ 小陣雨",
    81: "🌦️ 中陣雨",
    82: "🌧️ 大陣雨",
    85: "🌨️ 小陣雪",
    86: "🌨️ 中陣雪",
    95: "⛈️ 雷陣雨",
    96: "⛈️ 雷陣雨+冰雹",
    99: "⛈️ 強雷陣雨+冰雹",
}

# 傳入經緯度
lat = sys.argv[1] if len(sys.argv) > 1 else "24.137"
lon = sys.argv[2] if len(sys.argv) > 2 else "121.272"

# 查詢未來 3 天（Open-Meteo 免費上限）
url = (
    f"https://api.open-meteo.com/v1/forecast"
    f"?latitude={lat}&longitude={lon}"
    f"&hourly=relative_humidity_2m,cloud_cover_low,cloud_cover_mid,cloud_cover_high,"
    f"wind_speed_10m,visibility,weather_code,precipitation_probability,"
    f"temperature_2m,dew_point_2m"
    f"&daily=sunrise,sunset,uv_index_max,precipitation_sum,weather_code"
    f"&timezone=Asia/Taipei"
    f"&forecast_days=5"
)

try:
    res = requests.get(url, timeout=10)
    raw = res.json()

    # 合併成便於分析的統一格式
    output = {
        "lat": lat,
        "lon": lon,
        "elevation": raw.get("elevation"),
        "timezone": raw.get("timezone"),
        "hourly": raw["hourly"],
        "daily": raw["daily"],
        "wmo_codes": WMO_CODES,  # 附上天氣代碼對照表
        "sunrise": raw["daily"]["sunrise"][0] if raw.get("daily") else None,
        "sunset": raw["daily"]["sunset"][0] if raw.get("daily") else None,
    }

    print(json.dumps(output, ensure_ascii=False))
except Exception as e:
    print(json.dumps({"error": str(e)}, ensure_ascii=False))