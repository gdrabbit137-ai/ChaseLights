import json
import urllib.request
import os

def fetch_noaa_kp():
    # NOAA 官方太空天氣 Kp 指數 JSON API
    url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
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

# 補回原本專案需要的函式，供 analyze_weather.py 呼叫
def fetch_weather_for_spot(spot_name, lat, lon):
    # 這裡保留你原本用來抓取各景點氣象的邏輯（例如 Open-Meteo 或其他 API）
    # 如果原本裡面已有實作，請保留你原本的內容，以下為示意：
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,cloud_cover,wind_speed_10m"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('current', {})
    except Exception as e:
        print(f"Failed to fetch weather for {spot_name}: {e}")
        return {}

def update_usa_weather():
    json_file = "usa_weather.json"
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            weather_data = json.load(f)
    else:
        weather_data = {}

    # 取得最新的 Kp 指數
    kp_info = fetch_noaa_kp()
    if kp_info:
        if "alaska" not in weather_data:
            weather_data["alaska"] = {}
        weather_data["alaska"]["kp_index"] = kp_info["kp_index"]
        weather_data["alaska"]["kp_time"] = kp_info["time"]
        weather_data["latest_kp"] = kp_info["kp_index"]

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(weather_data, f, ensure_ascii=False, indent=2)
    print("usa_weather.json updated successfully.")

if __name__ == "__main__":
    update_usa_weather()
