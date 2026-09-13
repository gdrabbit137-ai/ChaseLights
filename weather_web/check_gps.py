import json, os

cache_path = os.path.join(r"D:\Dick\Project\PhotoWeather\weather_web\.cache", "forecast_data.json")
with open(cache_path, "r", encoding="utf-8") as f:
    data = json.load(f)

spots = [p for p in data['points'] if p['type'] == 'spot']
print(f"共 {len(spots)} 個景點\n")

known_elevations = {
    "大屯山助航站": 1082, "象山": 183, "淡水漁人碼頭": 5,
    "九份不厭亭": 490, "大稻埕碼頭": 3, "碧潭": 35,
    "關渡大橋": 12, "高美濕地": 4, "合歡山主峰": 3417,
    "二延平步道": 1248, "頂石棹": 1650, "阿里山": 2216,
    "二寮": 220, "抹茶山": 900, "玉山主峰": 3952,
    "雪山主峰": 3886, "奇萊主峰": 3560, "南湖大山": 3742,
    "嘉明湖": 3310, "大霸尖山": 3492, "北大武山": 3092,
    "池有山": 3303, "清水斷崖": 100, "七星潭": 3,
}

# 對照預期位置的問題
expected_coords = {
    "象山": (25.0275, 121.5714),          # 象山六巨石
    "合歡山主峰": (24.1427, 121.2710),    # 合歡山主峰三角點
    "玉山主峰": (23.4705, 120.9569),      # 玉山主峰
    "大屯山助航站": (25.1869, 121.5208),  # 助航站
    "抹茶山": (24.8242, 121.7261),        # 聖母山莊
    "高美濕地": (24.3120, 120.5500),      # 高美濕地木棧道
    "大壩尖山": (24.4000, 121.2330),      # Wait, 大霸尖山 is 24.401, 121.240 not 24.400,121.233
}

# 找有問題的重複座標
coord_map = {}
dup_issues = []

for s in spots:
    key = f"{s['lat']:.4f}_{s['lon']:.4f}"
    if key in coord_map:
        dup_issues.append(f"⚠️ 重複座標: {coord_map[key]} 與 {s['name']} 同為 ({s['lat']:.4f}, {s['lon']:.4f})")
    else:
        coord_map[key] = s['name']

print("⚠️ 座標重複問題：")
if dup_issues:
    for i in dup_issues:
        print(f"  {i}")
else:
    print("  無")

print(f"\n📊 高程準確度分析：")
for s in spots:
    name = s.get("name", "")
    elev_api = s.get("elevation") or 0
    actual = known_elevations.get(name)
    if actual and abs(elev_api - actual) > 200:
        print(f"  ⚠️ {name}: API={elev_api}m vs 實際={actual}m (差{actual-elev_api}m)")

print(f"\n🌐 座標偏移檢查：")
# 特別檢查幾個景點的準確性
checks = [
    ("大霸尖山", 24.4010, 121.2400, 3492),
    ("秀姑巒山", 23.4668, 120.9363, 3825),
    ("馬博拉斯山", 23.4648, 120.9373, 3785),
    ("關山(百岳)", 23.2500, 120.9500, 3668),
    ("關山嶺山(南橫)", 23.2460, 120.9400, 3176),
    ("海諾南山", 23.2440, 120.9350, 3174),
    ("塔關山", 23.2669, 120.9674, 3222),
    ("郡大山", 23.6170, 121.0170, 3263),
    ("西巒大山", 23.6160, 121.0140, 3081),
    ("干卓萬山", 23.6180, 121.0160, 3284),
]

for name, exp_lat, exp_lon, exp_el in checks:
    for s in spots:
        if s['name'] == name:
            dlat = abs(s['lat'] - exp_lat) * 111
            dlon = abs(s['lon'] - exp_lon) * 111 * 0.85
            if dlat > 0.5 or dlon > 0.5:
                print(f"  ❌ {name}: 座標偏差約 {dlat+dlon:.1f}km ({s['lat']:.4f},{s['lon']:.4f} vs {exp_lat:.4f},{exp_lon:.4f})")
            break

print("\n✅ 完成檢查")