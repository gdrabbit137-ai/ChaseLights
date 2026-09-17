import sys
import json
from datetime import datetime, timezone
from regions import get_spots
from fetch_data import fetch_weather_for_spot, fetch_noaa_kp

def analyze_spot(spot):
    """
    抓取並分析單一景點氣象 (包含歷史與預報數據，並帶入主題標籤與動態氣象指標)
    """
    try:
        raw_data = fetch_weather_for_spot(spot)
        
        score = raw_data.get("score", 30) if isinstance(raw_data, dict) else 30
        best_time = raw_data.get("best_time", "23:00") if isinstance(raw_data, dict) else "23:00"
        reason = raw_data.get("reason", "條件不足") if isinstance(raw_data, dict) else "條件不足"
        position = raw_data.get("position", "☀️ 晴朗無雲 → 適合一般風景攝影") if isinstance(raw_data, dict) else "☀️ 晴朗無雲"
        key_indicator = raw_data.get("key_indicator", "✅ 風和日麗良好") if isinstance(raw_data, dict) else "✅ 風和日麗良好"
        hourly_forecast = raw_data.get("hourly_forecast", []) if isinstance(raw_data, dict) else []
        tags = spot.get("tags", ["mountain"])

        return {
            "name": spot.get("name", "未知景點"),
            "category": spot.get("category", "未分類"),
            "tags": tags,
            "lat": spot.get("lat"),
            "lon": spot.get("lon"),
            "score": score,
            "best_time": best_time,
            "reason": reason,
            "position": position,
            "key_indicator": key_indicator,
            "hourly_forecast": hourly_forecast
        }
    except Exception as e:
        print(f"⚠️ 讀取景點 {spot.get('name')} 失敗: {e}")
        return {
            "name": spot.get("name", "未知景點"),
            "category": spot.get("category", "未分類"),
            "tags": spot.get("tags", ["mountain"]),
            "lat": spot.get("lat"),
            "lon": spot.get("lon"),
            "score": 0,
            "best_time": "N/A",
            "reason": "無法取得即時氣象資料",
            "position": "資料擷取失敗",
            "key_indicator": "⚠️ 資料擷取失敗",
            "hourly_forecast": []
        }

def main():
    region = sys.argv[1].lower() if len(sys.argv) > 1 else "tw"

    filename_map = {
        "tw": "tw_weather.json",
        "jp": "japan_weather.json",
        "us": "usa_weather.json"
    }

    output_filename = filename_map.get(region, f"{region}_weather.json")
    print(f"🚀 開始分析區域: [{region.upper()}] ...")

    spots = get_spots(region)
    if not spots:
        print(f"❌ 找不到區域 [{region}] 的景點清單！")
        sys.exit(1)

    analyzed_spots = []
    for spot in spots:
        print(f"🔍 正在分析: {spot.get('name')}...")
        result = analyze_spot(spot)
        analyzed_spots.append(result)

    # 輸出 ISO 8601 UTC 標準時間，例如 2026-09-18T03:14:10Z
    now_utc_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    output_data = {
        "updated_at": now_utc_str,
        "region": region,
        "total_spots": len(analyzed_spots),
        "spots": analyzed_spots
    }

    # 抓取最新 NOAA Kp 指數並寫入 JSON 根層級，確保前端 Header 隨時能讀取
    kp_info = fetch_noaa_kp()
    if kp_info:
        output_data["latest_kp"] = kp_info["kp_index"]

    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 完成！成功生成 {output_filename} (共 {len(analyzed_spots)} 個景點，UTC時間: {now_utc_str})")

if __name__ == "__main__":
    main()
