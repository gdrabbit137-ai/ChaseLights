import sys
import json
from datetime import datetime
from regions import get_spots
from fetch_data import fetch_weather_for_spot  # 依據你的專案抓取資料函式

def analyze_spot(spot):
    """
    抓取並分析單一景點的氣象資料
    （此處示範整合邏輯，若原 fetch_data 已經完成分析，可直接回傳其結果）
    """
    try:
        raw_data = fetch_weather_for_spot(spot)
        
        # 如果 raw_data 已包含完整的 score, reason 等欄位則直接回傳
        if isinstance(raw_data, dict) and "score" in raw_data:
            return raw_data

        # 基礎結構備援（若原 fetch 僅傳回原始資料，可在此做評分邏輯）
        return {
            "name": spot.get("name", "未知景點"),
            "score": raw_data.get("score", 30),
            "best_time": raw_data.get("best_time", "23:00"),
            "position": raw_data.get("position", "晴朗無雲 - 適合一般風景攝影"),
            "reason": raw_data.get("reason", "條件不足")
        }
    except Exception as e:
        print(f"⚠️ 讀取景點 {spot.get('name')} 失敗: {e}")
        return {
            "name": spot.get("name", "未知景點"),
            "score": 0,
            "best_time": "N/A",
            "position": "資料擷取失敗",
            "reason": "無法取得即時氣象資料"
        }

def main():
    # 預設區域為 台灣 (tw)
    region = sys.argv[1].lower() if len(sys.argv) > 1 else "tw"

    # 區域檔名對照表
    filename_map = {
        "tw": "latest_weather.json",
        "jp": "japan_weather.json",
        "ak": "alaska_weather.json",
        "us": "usa_weather.json"
    }

    output_filename = filename_map.get(region, f"{region}_weather.json")
    print(f"🚀 開始分析區域: [{region.upper()}] ...")

    # 從 regions.py 獲取景點清單
    spots = get_spots(region)
    if not spots:
        print(f"❌ 找不到區域 [{region}] 的景點清單！")
        return

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
        "spots": analyzed_spots
    }

    # 寫入 JSON 檔案
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 完成！已成功生成 {output_filename} (更新時間: {now_str})")

if __name__ == "__main__":
    main()
