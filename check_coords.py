# check_coords.py
from regions import REGIONS

for region_code, region_data in REGIONS.items():
    print(f"\n================ {region_data.get('name_zh')} 景點座標驗證連結 ================")
    for spot in region_data.get("spots", []):
        lat, lon = spot[0], spot[1]
        name = spot[2]
        # 產生 Google Maps 搜尋連結
        maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        print(f"📍 {name:<12} | {lat}, {lon} -> {maps_url}")