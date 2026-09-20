"""Development CLI for inspecting raw Open-Meteo data used by ChaseLights.

Usage:
    python get_weather.py <lat> <lon> [elevation_m]

This helper intentionally mirrors the Score V5 production request shape: local timezone,
24h past + 72h forecast, Unix timestamps, and wind speed in m/s.
"""
import sys
import json
import requests

WMO_CODES = {
    0: "☀️ 晴天", 1: "🌤️ 多雲轉晴", 2: "⛅ 局部多雲", 3: "☁️ 陰天",
    45: "🌫️ 霧", 48: "🌫️ 霧淞", 51: "🌦️ 小毛毛雨", 53: "🌦️ 中毛毛雨",
    55: "🌧️ 大毛毛雨", 56: "🌧️ 小凍雨", 57: "🌧️ 大凍雨", 61: "🌧️ 小雨",
    63: "🌧️ 中雨", 65: "🌧️ 大雨", 66: "🌧️ 小凍雨", 67: "🌧️ 大凍雨",
    71: "🌨️ 小雪", 73: "🌨️ 中雪", 75: "❄️ 大雪", 77: "❄️ 雪粒",
    80: "🌦️ 小陣雨", 81: "🌦️ 中陣雨", 82: "🌧️ 大陣雨", 85: "🌨️ 小陣雪",
    86: "🌨️ 中陣雪", 95: "⛈️ 雷陣雨", 96: "⛈️ 雷陣雨+冰雹", 99: "⛈️ 強雷陣雨+冰雹",
}

lat = sys.argv[1] if len(sys.argv) > 1 else "24.1426"
lon = sys.argv[2] if len(sys.argv) > 2 else "121.2712"
elevation = sys.argv[3] if len(sys.argv) > 3 else None

params = {
    "latitude": lat,
    "longitude": lon,
    "hourly": ",".join([
        "relative_humidity_2m", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high",
        "wind_speed_10m", "visibility", "weather_code", "precipitation_probability",
        "temperature_2m", "dew_point_2m", "is_day",
    ]),
    "daily": "sunrise,sunset,uv_index_max,precipitation_sum,weather_code",
    "timezone": "auto",
    "timeformat": "unixtime",
    "wind_speed_unit": "ms",
    "past_hours": 24,
    "forecast_hours": 72,
}
if elevation is not None:
    params["elevation"] = elevation

try:
    res = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=15)
    res.raise_for_status()
    raw = res.json()
    output = {
        "lat": lat,
        "lon": lon,
        "requested_elevation": elevation,
        "api_elevation": raw.get("elevation"),
        "timezone": raw.get("timezone"),
        "timezone_abbreviation": raw.get("timezone_abbreviation"),
        "utc_offset_seconds": raw.get("utc_offset_seconds"),
        "hourly_units": raw.get("hourly_units"),
        "hourly": raw.get("hourly", {}),
        "daily": raw.get("daily", {}),
        "wmo_codes": WMO_CODES,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
except Exception as exc:
    print(json.dumps({"error": str(exc)}, ensure_ascii=False))
    sys.exit(1)
