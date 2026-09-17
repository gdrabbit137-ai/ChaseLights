"""
ChaseLights — 景點座標批量校正工具
使用 OpenStreetMap Nominatim API (免費) 自動更新精準座標
"""

import time
import requests

try:
    from regions import REGIONS
except ImportError:
    REGIONS = None


def load_spots():
    """支援舊版 SPOTS_TW 與新版 REGIONS['tw']['spots'] 格式。"""
    if REGIONS is not None:
        raw_spots = REGIONS.get("tw", {}).get("spots", [])
        normalized = []
        for spot in raw_spots:
            if isinstance(spot, dict):
                normalized.append(spot)
                continue
            lat, lon, name, category = spot[:4]
            tags = spot[4] if len(spot) > 4 else ["mountain"]
            normalized.append({
                "lat": lat,
                "lon": lon,
                "name": name,
                "category": category,
                "tags": tags,
            })
        return normalized

    try:
        from regions import SPOTS_TW
        return SPOTS_TW
    except ImportError:
        raise ImportError("No spot list found. Expected REGIONS['tw']['spots'] or SPOTS_TW in regions.py.")


def geocode_spot(spot_name, category=""):
    """向 Nominatim 查詢精準地標座標"""
    # 增加搜尋關鍵字精準度
    query = f"台灣 {spot_name}"
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "ChaseLights_Coordinate_Fixer/1.0"}
    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                lat = round(float(data[0]["lat"]), 4)
                lon = round(float(data[0]["lon"]), 4)
                return lat, lon
    except Exception as e:
        print(f"❌ 查詢失敗 [{spot_name}]: {e}")
        
    return None, None

def batch_fix_coordinates():
    spots = load_spots()
    updated_spots = []
    print(f"🚀 開始批量校正 {len(spots)} 個景點座標...\n")

    for spot in spots:
        name = spot["name"]
        old_lat, old_lon = spot["lat"], spot["lon"]

        # 免費 API 限制：需延遲 1 秒避免被擋
        time.sleep(1.1)

        new_lat, new_lon = geocode_spot(name, spot.get("category", ""))

        if new_lat and new_lon:
            print(f"✅ [{name}] 舊座標: ({old_lat}, {old_lon}) ➔ 新座標: ({new_lat}, {new_lon})")
            updated_spot = {**spot, "lat": new_lat, "lon": new_lon}
        else:
            print(f"⚠️ [{name}] 未找到精準結果，保留原座標: ({old_lat}, {old_lon})")
            updated_spot = spot

        updated_spots.append(updated_spot)

    # 印出可直接貼回 regions.py 的完整格式
    print("\n" + "=" * 50)
    print("🎉 校正完成！請將以下程式碼覆蓋至 regions.py：\n")
    print("SPOTS_TW = " + repr(updated_spots))
    print("\n# 若要更新新版 REGIONS['tw']['spots']，可使用：")
    print("REGIONS['tw']['spots'] = [")
    for item in updated_spots:
        print("    (" + ", ".join([
            repr(item["lat"]),
            repr(item["lon"]),
            repr(item["name"]),
            repr(item["category"]),
            repr(item.get("tags", ["mountain"])),
        ]) + "),")
    print("]")

if __name__ == "__main__":
    batch_fix_coordinates()