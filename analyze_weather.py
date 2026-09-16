import sys
import json
from datetime import datetime
from regions import get_spots
from fetch_data import fetch_weather_for_spot

def analyze_spot(spot):
    """
    抓取並分析單一景點的氣象資料
    """
    try:
        raw_data = fetch_weather_for_spot(spot)
        
        # 若 raw_data 已包含完整的分析欄位，直接回傳
        if isinstance(raw_data, dict) and "score" in raw_data:
            return {
                "name": spot.get("name", "未知景點"),
                "lat": spot.get("lat"),
                "lon": spot.get("lon"),
                "score": raw_data.get("score", 30),
                "best_time": raw_data.get("best_time", "23:00"),
                "reason": raw_data.get("reason", "條件不足"),
                "position": raw_data.get("position", "☀️ 晴朗無雲 → 適合一般風景攝影")
            }

        # 備援結構
        return {
            "name": spot.get("name", "未知景點"),
            "lat": spot.get("lat"),
            "lon": spot.get("lon"),
            "score": 30,
            "best_time": "23:00",
            "reason": "條件不足",
            "position": "☀️ 晴朗無雲 → 適合一般風景攝影"
        }
    except Exception as e:
        print(f"⚠️ 讀取景點 {spot.get('name')} 失敗: {e}")
        return {
            "name": spot.get("name", "未知景點"),
            "lat": spot.get("lat"),
            "lon": spot.get("lon"),
            "score": 0,
            "best_time": "N/A",
            "reason": "無法取得即時氣象資料",
            "position": "資料擷取失敗"
        }

def main():
    # 預設區域為 台灣 (tw)
    region = sys.argv[1].lower() if len(sys.argv) > 1 else "tw"

    # 區域檔名對照表 (阿拉斯加已整合至 us)
    filename_map = {
        "tw": "latest_weather.json",
        "jp": "japan_weather.json",
        "us": "usa_weather.json"
    }

    output_filename = filename_map.get(region, f"{region}_weather.json")
    print(f"🚀 開始分析區域: [{region.upper()}] ...")

    # 從 regions.py 獲取景點清單
    spots = get_spots(region)
    if not spots:
        print(f"❌ 找不到區域 [{region}] 的景點清單！")
        sys.exit(1)

    analyzed_spots = []
    for spot in spots:
        print(f"🔍 正在分析: {spot.get('name')}...")
        result = analyze_spot(spot)
        analyzed_spots.append(result)

    # 組合最終 JSON 格式
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_data = {
        "updated_at": now_str,
        "region": region,
        "total_spots": len(analyzed_spots),
        "spots": analyzed_spots
    }

    # 寫入 JSON 檔案
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 完成！已成功生成 {output_filename} (共 {len(analyzed_spots)} 個景點，更新時間: {now_str})")

if __name__ == "__main__":
    main()
