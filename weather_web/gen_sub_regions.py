"""Generate SUB_REGION_MAP JS for summary.html"""
import json

# From countries_list.md
SUB_MAP = {}
def add(region, sub, names):
    for n in names:
        SUB_MAP[n] = sub

# Taiwan
add('tw', 'mainland', [
    "大屯山助航站","象山","淡水漁人碼頭","九份不厭亭","金瓜石茶壺山",
    "大稻埕碼頭","關渡大橋","碧潭","觀音山硬漢嶺","望幽谷","和平島",
    "永安漁港","香山濕地","火炎山","雲洞山莊","高美濕地","鳶嘴山",
    "王功漁港","日月潭","合歡山主峰","金龍山","武界部落","二延平步道",
    "頂石棹","阿里山","二寮","井仔腳鹽田","田寮月世界","駁二藝術特區",
    "墾丁鵝鑾鼻","屏東關山","抹茶山","見晴懷古步道","粉鳥林","清水斷崖",
    "六十石山","七星潭","多良車站","三仙台","池上伯朗大道",
    "玉山主峰","雪山主峰","雪山北峰","奇萊主峰","南湖大山","嘉明湖",
    "大霸尖山","北大武山","池有山","桃山","品田山","杉林溪",
    "五峰旗瀑布","小崗山雲臺","大古山","正濱漁港",
])
add('tw', 'outlier', [
    "澎湖跨海大橋","奎壁山","七美雙心石滬","澎湖觀音亭",
    "金門得月樓","翟山坑道","金門慈湖",
    "馬祖南竿","東引燈塔","北竿芹壁",
    "綠島朝日溫泉","蘭嶼東清灣","蘭嶼青青草原","小琉球花瓶岩",
])

# Japan
add('jp', 'hokkaido', [
    "摩周湖","美瑛青い池","旭岳(北海道)","釧路湿原","函館山","小樽運河",
])
add('jp', 'tohoku', ["松島","磐梯山","十和田湖"])
add('jp', 'kanto', [
    "東京鐵塔","鎌倉大仏","等々力渓谷(東京)","皇居(東京)",
    "横浜山下公園","みなとみらい(横浜)",
])
add('jp', 'chubu', [
    "富士山(山梨)","諏訪湖","金沢兼六園","名古屋城",
    "浜名湖","新穂高ロープウェイ","弥彦山",
])
add('jp', 'kansai', ["清水寺(京都)","大阪城","六甲山(神戶)","高野山","伊賀上野城"])
add('jp', 'chugoku_shikoku', ["萩市城下町","出雲大社","倉敷美観地区","鳴門海峡(徳島)"])
add('jp', 'kyushu', ["福岡城跡","唐津城","長崎グラバー園","福岡タワー"])

# USA
add('us', 'west', [
    "Grand Canyon","Horseshoe Bend","Antelope Canyon","Monument Valley",
    "Arches NP","Bryce Canyon","Zion NP","Canyonlands Mesa Arch",
    "Yosemite Half Dome","Yosemite Tunnel View","Death Valley","White Sands",
    "Golden Gate Bridge SF","Crater Lake","Mount Rainier","Mount St. Helens",
    "Olympic NP","Seattle Space Needle","Pike Place Market",
    "Redwood NP","Joshua Tree NP","Saguaro NP",
    "Santa Monica Pier","Los Angeles Observatory","Las Vegas Strip",
])
add('us', 'central', [
    "Yellowstone Grand Prismatic","Grand Teton NP","Rocky Mountains",
    "Denver Skyline","Glacier NP","Sawtooth Mountains",
    "Great Smoky Mountains","St Louis Gateway Arch","Chicago Skyline",
])
add('us', 'east', [
    "Manhattan Skyline","Niagara Falls","Boston Skyline",
    "New Orleans French Quarter","Miami Beach","Fort Worth Stockyards",
])

# Output as JS const
js = "// Spot → sub-region mapping\nconst SUB_REGION_MAP = {\n"
for name, sub in sorted(SUB_MAP.items()):
    js += f'  "{name}": "{sub}",\n'
js += "};\n\n"
js += "// Sub-region definitions per country\nconst SUB_REGIONS = {\n"
js += '  tw: [["mainland","台灣本島","Mainland"],["outlier","外島","Outer Islands"]],\n'
js += '  jp: [["hokkaido","北海道","Hokkaido"],["tohoku","東北","Tohoku"],["kanto","關東","Kanto"],["chubu","中部北陸","Chubu"],["kansai","關西","Kansai"],["chugoku_shikoku","中國四國","Chugoku/Shikoku"],["kyushu","九州","Kyushu"]],\n'
js += '  us: [["west","美西","West"],["central","美中","Central"],["east","美東","East"],["alaska","阿拉斯加","Alaska"]],\n'
js += '  ak: [["alaska","阿拉斯加","Alaska"]],\n'
js += "};\n"

print(js)
print(f"Total mapped: {len(SUB_MAP)} spots", file=__import__('sys').stdout)