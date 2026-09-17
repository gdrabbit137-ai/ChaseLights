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
            # NOAA 回傳格式通常第一列標題，後續為資料 [time, kp, a_running, station_count]
            # 我們取最新的一筆（即倒數第一筆資料）
            if len(data) > 1:
                latest_entry = data[-1]
                kp_value = latest_entry[1]
                time_tag = latest_entry[0]
                return {
                    "kp_index": kp_value,
                    "time": time_tag
                }
    except Exception as e:
        print(f"Failed to fetch NOAA Kp data: {e}")
    return None

def update_usa_weather():
    json_file = "usa_weather.json"
    
    # 讀取現有的 usa_weather.json
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            weather_data = json.load(f)
    else:
        weather_data = {}

    # 取得最新的 Kp 指數
    kp_info = fetch_noaa_kp()
    
    if kp_info:
        # 將 Kp 指數更新到阿拉斯加（或其他對應地區）的資料結構中
        # 假設你的結構內有針對阿拉斯加的欄位，這裡以寫入根目錄或阿拉斯加物件為例
        if "alaska" not in weather_data:
            weather_data["alaska"] = {}
        
        weather_data["alaska"]["kp_index"] = kp_info["kp_index"]
        weather_data["alaska"]["kp_time"] = kp_info["time"]
        
        # 同樣存入整體共用或一般紀錄
        weather_data["latest_kp"] = kp_info["kp_index"]

    # 寫回檔案
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(weather_data, f, ensure_ascii=False, indent=2)
    print("usa_weather.json updated successfully with Kp index.")

if __name__ == "__main__":
    update_usa_weather()
