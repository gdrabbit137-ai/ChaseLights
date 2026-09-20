import sys
import json
from datetime import datetime, timezone

from regions import get_spots
from fetch_data import fetch_weather_for_spot, fetch_noaa_kp, fetch_noaa_kp_series

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
    "阿拉斯加": {"zh-TW": "阿拉斯加", "en": "Alaska", "ja": "アラスカ"},
}


def analyze_spot(spot, lang="zh-TW", kp_rows=None):
    try:
        raw_data = fetch_weather_for_spot(spot, lang, kp_rows=kp_rows)
        if not isinstance(raw_data, dict) or not raw_data:
            return {}

        name_i18n = spot.get("name_i18n", {})
        name_main = name_i18n.get(lang) or name_i18n.get("zh-TW") or spot.get("name", "Unknown")
        name_local = spot.get("name_local", spot.get("name", ""))
        orig_category = spot.get("category", "未分類")

        return {
            "spot_id": spot.get("spot_id"),
            "name": name_main,
            "name_local": name_local,
            "category": CATEGORY_I18N.get(orig_category, {}).get(lang, orig_category),
            "tags": spot.get("tags", ["mountain"]),
            "lat": spot.get("lat"),
            "lon": spot.get("lon"),
            "elevation": spot.get("elevation"),
            "api_elevation": raw_data.get("api_elevation"),
            "timezone": raw_data.get("timezone"),
            "utc_offset_seconds": raw_data.get("utc_offset_seconds"),
            "score": raw_data.get("score", 30),
            "best_time": raw_data.get("best_time", "N/A"),
            "best_time_utc": raw_data.get("best_time_utc"),
            "reason": raw_data.get("reason", "N/A"),
            "position": raw_data.get("position", ""),
            "key_indicator": raw_data.get("key_indicator", ""),
            "hourly_forecast": raw_data.get("hourly_forecast", []),
        }
    except Exception as exc:
        print(f"⚠️ 讀取景點 {spot.get('spot_id', spot.get('name'))} 失敗: {exc}")
        return {}


def main():
    region = sys.argv[1].lower() if len(sys.argv) > 1 else "tw"
    spots = get_spots(region)
    if not spots:
        print(f"❌ 找不到區域 [{region}] 的景點清單！")
        sys.exit(1)

    languages = ["zh-TW", "en", "ja"]
    kp_rows = fetch_noaa_kp_series()
    kp_info = fetch_noaa_kp()
    latest_kp = kp_info["kp_index"] if kp_info else "N/A"
    latest_kp_source = kp_info.get("source") if kp_info else "unavailable"
    now_utc_str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # fetch_data.py internally caches the Open-Meteo response by coordinate/elevation,
    # so generating the 3 languages does not triple the external weather requests.
    for lang in languages:
        output_filename = f"{region}_weather_{lang}.json"
        print(f"🚀 開始生成 [{region.upper()}] - 語系 [{lang}] -> {output_filename} ...")

        analyzed_spots = []
        for spot in spots:
            result = analyze_spot(spot, lang, kp_rows=kp_rows)
            if result:
                analyzed_spots.append(result)

        output_data = {
            "schema_version": 2,
            "updated_at": now_utc_str,
            "region": region,
            "lang": lang,
            "latest_kp": latest_kp,
            "latest_kp_source": latest_kp_source,
            "total_spots": len(analyzed_spots),
            "spots": analyzed_spots,
        }

        with open(output_filename, "w", encoding="utf-8") as fh:
            json.dump(output_data, fh, ensure_ascii=False, indent=2)

        print(f"✅ 成功生成 {output_filename}")


if __name__ == "__main__":
    main()
