import sys
import json
from datetime import datetime, timezone
from regions import get_spots
from fetch_data import fetch_weather_for_spot, fetch_noaa_kp

CATEGORY_I18N = {
    "本島": {"zh-TW": "本島", "en": "Main Island", "ja": "本島"},
    "澎湖": {"zh-TW": "澎湖", "en": "Penghu", "ja": "澎湖"},
    "金門": {"zh-TW": "金門", "en": "Kinmen", "ja": "金門"},
    "馬祖": {"zh-TW": "馬祖", "en": "Matsu", "ja": "馬祖"},
    "綠島/蘭嶼/小琉球": {"zh-TW": "綠島/蘭嶼/小琉球", "en": "Islands", "ja": "離島"},
    "北海道/東北": {"zh-TW": "北海道/東北", "en": "Hokkaido/Tohoku", "ja": "北海道/東北"},
    "關東/中部": {"zh-TW": "關東/中部", "en": "Kanto/Chubu", "ja": "関東/中部"},
    "關西/中四國": {"zh-TW": "關西/中四國", "en": "Kansai/Chugoku", "ja": "関西/中国・四国"},
    "九州/沖繩": {"zh-TW": "九州/沖繩", "en": "Kyushu/Okinawa", "ja": "九州/沖縄"},
    "美西": {"zh-TW": "美西", "en": "US West", "ja": "全米西部"},
    "美中": {"zh-TW": "美中", "en": "US Central", "ja": "全米中部"},
    "美東": {"zh-TW": "美東", "en": "US East", "ja": "全米東部"},
    "阿拉斯加": {"zh-TW": "阿拉斯加", "en": "Alaska", "ja": "アラスカ"}
}

def analyze_spot(spot, lang="zh-TW"):
    try:
        raw_data = fetch_weather_for_spot(spot, lang)
        
        score = raw_data.get("score", 30) if isinstance(raw_data, dict) else 30
        best_time = raw_data.get("best_time", "23:00") if isinstance(raw_data, dict) else "23:00"
        reason = raw_data.get("reason", "N/A") if isinstance(raw_data, dict) else "N/A"
        position = raw_data.get("position", "") if isinstance(raw_data, dict) else ""
        key_indicator = raw_data.get("key_indicator", "") if isinstance(raw_data, dict) else ""
        hourly_forecast = raw_data.get("hourly_forecast", []) if isinstance(raw_data, dict) else []
        tags = spot.get("tags", ["mountain"])

        orig_category = spot.get("category", "未分類")
        translated_category = CATEGORY_I18N.get(orig_category, {}).get(lang, orig_category)

        # 💡 取得多國語言名稱與當地原文名稱
        name_i18n = spot.get("name_i18n", {})
        name_main = name_i18n.get(lang) or name_i18n.get("zh-TW") or spot.get("name", "Unknown")
        name_local = spot.get("name_local", spot.get("name", ""))

        return {
            "name": name_main,          # 主標題：依據當前語言顯示
            "name_local": name_local,   # 副標題：當地官方原文名稱
            "category": translated_category,
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
        return {}

def main():
    region = sys.argv[1].lower() if len(sys.argv) > 1 else "tw"
    spots = get_spots(region)
    if not spots:
        print(f"❌ 找不到區域 [{region}] 的景點清單！")
        sys.exit(1)

    languages = ["zh-TW", "en", "ja"]
    kp_info = fetch_noaa_kp()
    latest_kp = kp_info["kp_index"] if kp_info else "N/A"
    now_utc_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for lang in languages:
        output_filename = f"{region}_weather_{lang}.json"
        print(f"🚀 開始生成 [{region.upper()}] - 語系 [{lang}] -> {output_filename} ...")

        analyzed_spots = []
        for spot in spots:
            result = analyze_spot(spot, lang)
            if result:
                analyzed_spots.append(result)

        output_data = {
            "updated_at": now_utc_str,
            "region": region,
            "lang": lang,
            "latest_kp": latest_kp,
            "total_spots": len(analyzed_spots),
            "spots": analyzed_spots
        }

        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 成功生成 {output_filename}")

if __name__ == "__main__":
    main()
