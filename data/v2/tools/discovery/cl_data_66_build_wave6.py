#!/usr/bin/env python3
"""CL-DATA-66 Wave 6: scoreless intake of 16 Tier-A places (tw-201..tw-216)
from the manifest-next-30 (57 remaining; the first 30 in order n_topics desc,
n_lists desc). 14 of the 30 candidates rejected (4 identical/near-identical
existing 0.36-2.74km + 2 same-family <5km existing (大菓葉/陰陽海) + 2
same-attraction family rows (月洞/富岡) + 2 same-wave family-cluster rows
(惠蓀林場高點/旗津黑砂) + 2 private-farm exclusions (恩愛農場 rows) + 1
unverifiable identity (漢本海蝕崖) + 1 already-merged subject (國聖港燈塔 in
tw-194)... see REJECTED_PLACES for the honest per-row reasons.

Owner rulings (2026-11-11): intake is SCORELESS — admission = web verification
(authoritative URL) + 5km subject-disjoint dedupe; no rubric/AGLI scoring,
agli-final untouched; score fields left empty. Contracts built in full (V2 +
legacy dual-track). Rejections recorded in
data/v2/audits/discovery/cl-data-66-dedupe.json and tier-a-manifest.json.
"""
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
import sys  # noqa: E402
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location(
    'cl64base', str(ROOT / 'data/v2/tools/discovery/cl_data_64_build.py'))
m64 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m64)
cl = m64.cl

TICKET = "CL-DATA-66"
VER_DATE = "2026-11-12"
WAVE = 6

PLACES = [
 dict(place_id="tw-201", region="tw", slug="keelung-lighthouse", score=None,
  names={"zh-TW": "基隆燈塔", "en": "Keelung Lighthouse (Baimiwong cape)",
         "ja": "基隆燈塔", "local": "基隆燈塔"},
  lat=25.1553203, lon=121.7476317, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 基隆燈塔（基隆中山區太白里光華路，lighthouse 節點）；海拔查無權威單值誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E5%9F%BA%E9%9A%86%E7%87%88%E5%A1%94",
                 "https://zh.wikipedia.org/wiki/%E5%9F%BA%E9%9A%86%E7%87%88%E5%A1%94"],
  admin="基隆市", category="本島", tags=["coast", "city"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="基隆燈塔港岬燈塔與航道景觀", en="Keelung Lighthouse cape and harbor-channel view", ja="基隆燈塔の港と水路",
    desc_zh="基隆燈塔（zh.wikipedia 市定古蹟，1900 年建、位基隆港西岸萬人堆鼻；2024 年開放參觀）港岬燈塔與基隆港航道景觀（OSM lighthouse 節點；海拔誠實留空）；與既有 tw-010 和平島（2.08km）題材錯位——本點為西岸燈塔古蹟主體，和平島為島嶼公園地質主體。",
    desc_en="Keelung Lighthouse (city-designated historic site per zh.wikipedia, built 1900 on the west-harbour cape; opened to visitors in 2024) with its harbour-channel view (OSM lighthouse node); disjoint from tw-010 Heping Island's island-park geology subject 2.08 km away.",
    desc_ja="基隆燈塔（市定古蹟、2024年公開）の港の水路の眺め（OSM）。和平島とは題材が別。"),
  ]),
 dict(place_id="tw-202", region="tw", slug="tanghu-trail", score=None,
  names={"zh-TW": "塘湖古道", "en": "Tanghu historic trail (Zhuqi, Chiayi)",
         "ja": "塘湖古道", "local": "塘湖古道"},
  lat=23.5283330, lon=120.6250000, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 塘湖聚落（嘉義竹崎鄉仁壽村，hamlet 節點；古道由塘湖聚落下行福建坪、落差近500m，座標以聚落節點對位待現場校準）；海拔查無權威單值誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E5%A1%98%E6%B9%96%20%E7%AB%B9%E5%B4%8E",
                 "https://www.ali-nsa.net/zh-tw/attractions/detail/557"],
  admin="嘉義縣", category="本島", tags=["mountain", "forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="塘湖古道石階與塘湖嶺鞍部展望", en="Tanghu-trail stone steps and ridge-saddle outlook", ja="塘湖古道の石段と展望",
    desc_zh="塘湖古道（阿里山國家風景區官方列名，200 多年歷史、塘湖至福建坪落差近 500m、石階舊路）與鞍部展望（OSM 塘湖聚落 hamlet 節點對位、待現場校準；海拔誠實留空）；清單主題的茶園梯景查無本站可繫結的權威資料源，誠實以古道主體登記；與既有 tw-105 太平雲梯／梅山36彎（4.47km）題材錯位。",
    desc_en="The 200-year-old Tanghu historic trail (officially listed by the Alishan NSA; near-500 m descent from Tanghu to Fujiannan on old stone steps) with its ridge-saddle outlook (OSM hamlet node as proxy, pending field calibration); the list's tea-terrace wording has no source we can bind - honestly registered as the trail itself; disjoint from tw-105 Taiping suspension bridge 4.47 km away.",
    desc_ja="塘湖古道（阿里山風景区公式、200年の歴史と石段）（OSMの集落ノードで対位）。太平吊橋とは題材が別。"),
  ]),
 dict(place_id="tw-203", region="tw", slug="dashibishan-trail", score=None,
  names={"zh-TW": "大石鼻山步道", "en": "Dashibishan cape trail (Jiqi, Fengbin)",
         "ja": "大石鼻山歩道", "local": "大石鼻山"},
  lat=23.6980106, lon=121.5519903, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 大石鼻山（花蓮豐濱，peak 節點）；海拔查無權威單值誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E5%A4%A7%E7%9F%B3%E9%BC%BB%E5%B1%B1",
                 "https://www.eastcoast-nsa.gov.tw/zh-tw/attractions/detail/265/"],
  admin="花蓮縣", category="本島", tags=["coast", "mountain"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="大石鼻山步道磯崎海灣瞭望", en="Jiqi-bay outlook from the Dashibishan trail", ja="磯崎湾を望む大石鼻山歩道",
    desc_zh="大石鼻山（東部海岸國家風景區官方列名，磯崎海濱遊憩區南端突出海岬、又稱龜庵山；750m 步道登頂可 360 度眺望磯崎海灣與台11線）步道瞭望主體（OSM peak 節點；海拔誠實留空）；與既有 tw-083 雲山水夢幻湖（14.8km）題材錯位。",
    desc_en="Dashibishan (officially listed by the East Coast NSA; a cape jutting at the south end of Jiqi recreation area, with a 750 m trail and a 360-degree bay outlook; OSM peak node); disjoint from tw-083 Yunshanshui dream-lake 14.8 km away.",
    desc_ja="大石鼻山（東部海岸国家風景区公式、磯崎湾の眺め）（OSM）。雲山水とは題材が別。"),
  ]),
 dict(place_id="tw-204", region="tw", slug="fuyuan-forest", score=None,
  names={"zh-TW": "富源國家森林遊樂區／蝴蝶谷", "en": "Fuyuan National Forest Recreation Area (Butterfly Valley)",
         "ja": "富源国家森林遊楽区／蝶の谷", "local": "富源森林遊樂區"},
  lat=23.5880964, lon=121.3429456, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 富源國家森林遊樂區（花蓮萬榮/瑞穗，nature_reserve 節點）；海拔查無權威單值誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E5%AF%8C%E6%BA%90%E5%9C%8B%E5%AE%B6%E6%A3%AE%E6%9E%97%E9%81%8A%E6%A8%82%E5%8D%80",
                 "https://hualien.forest.gov.tw/0000234"],
  admin="花蓮縣", category="本島", tags=["forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="富源森林遊樂區蝴蝶谷與環山步道", en="Fuyuan butterfly-valley forest and loop trails", ja="富源森林遊楽区の蝶の谷",
    desc_zh="富源國家森林遊樂區（林業及自然保育署花蓮分署官方頁；富源溪貫穿、龍吟吊橋/瀑布、樟樹林；蝴蝶/賞螢季窗為官方生態資訊但查無可繫結的逐窗契約資料源，誠實不建時間窗）森林步道主體（OSM nature_reserve 節點；海拔誠實留空）；與既有 tw-084 大農大富平地森林園區（8.0km）題材錯位。",
    desc_en="Fuyuan National Forest Recreation Area (officially listed by the Forestry and Nature Conservation Agency Hualien branch; Fuyuan river, dragon-bridge and camphor stands). Butterfly/firefly season windows are official ecology notes but no bindable per-window data source - honestly no time-window contract; disjoint from tw-084 Danongdafu forest park 8.0 km away.",
    desc_ja="富源国家森林遊楽区（林業保育署花蓮分署公式）。蝶・蛍の季節窓は権威源がなく誠実に不構築。大農大富とは題材が別。"),
  ]),
 dict(place_id="tw-205", region="tw", slug="longxiadong-reef", score=None,
  names={"zh-TW": "小琉球龍蝦洞海蝕溝", "en": "Lobster Cave sea-cut channels (Liuqiu)",
         "ja": "小琉球・龍蝦洞の海蝕溝", "local": "龍蝦洞"},
  lat=22.3454455, lon=120.3872636, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 龍蝦洞（屏東琉球鄉漁福村三民路，bus_stop 節點對位東北岸礁區、待現場校準）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E9%BE%8D%E8%9D%A6%E6%B4%9E%20%E7%90%89%E7%90%83",
                 "https://www.rtaiwanr.com/zh-TW/xiaoliuqiu/xiaoliuqiu/lobster-cave"],
  admin="屏東縣", category="離島", tags=["coast", "geology"],
  subjects=[
   dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="龍蝦洞海蝕溝與壺穴礁岸", en="Longxiadong sea-cut channels and pothole reef shore", ja="龍蝦洞の海蝕溝と壺穴",
    desc_zh="小琉球東北岸龍蝦洞（行記/媒體列名；發達海蝕溝與壺穴珊瑚礁岸、早期捕龍蝦之處）地質主體（OSM bus_stop 節點對位、待現場校準；海拔誠實留空）；與既有 tw-071 小琉球花瓶岩（1.32km）題材錯位——花瓶岩為浮潛地標岩，本點為海蝕溝壺穴地質。",
    desc_en="The sea-cut channels and potholes of Longxiadong on Liuqiu's northeast reef shore (travel/media listings; an old lobster-fishing ground; OSM bus-stop node as proxy, pending field calibration); disjoint from tw-071 Vase Rock's snorkel-landmark subject 1.32 km away.",
    desc_ja="小琉球東北岸の龍蝦洞、海蝕溝と壺穴の地形（OSMで対位）。花瓶岩とは題材が別。"),
  ]),
 dict(place_id="tw-206", region="tw", slug="lingding-cape", score=None,
  names={"zh-TW": "嶺頂岬海蝕平台", "en": "Lingding cape wave-cut shore (Shoufeng)",
         "ja": "嶺頂岬の海蝕平台", "local": "嶺頂"},
  lat=23.9258629, lon=121.6075662, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 花蓮溪口自然保護區嶺頂（花蓮壽豐鹽寮村，nature_reserve 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E5%B6%BA%E9%A0%82%20%E8%8A%B1%E8%93%AE",
                 "https://landscape.forest.gov.tw/Front/LandscapeNews/communication/Periodicals.aspx?id=7KShBTi6PLM=&Cn=27&Sn=207"],
  admin="花蓮縣", category="本島", tags=["coast", "geology"],
  subjects=[
   dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="嶺頂岬河口礫石海蝕岸", en="Lingding cape estuary boulder wave-cut shore", ja="嶺頂岬の礫石海岸",
    desc_zh="嶺頂（嶺頂岬，海岸山脈北端起點、花蓮溪注太平洋處；林業保育署地景保育通訊列名的火山角礫岩/凝灰岩礫石海濱與沙嘴地形）地質主體（OSM nature_reserve 節點；海拔誠實留空）；與既有 tw-153 楓林步道（7.67km）題材錯位。",
    desc_en="Lingding cape at the north end of the Coastal Range where the Hualien River meets the Pacific (listed in the Forestry Agency's landscape bulletin for its volcanic-breccia boulder shore and sand-spit landforms; OSM nature_reserve node); disjoint from tw-153 Fenglin trail 7.67 km away.",
    desc_ja="海岸山脈北端の嶺頂岬、花蓮溪河口の礫石海岸（林業保育署の地景通訊）（OSM）。楓林歩道とは題材が別。"),
  ]),
 dict(place_id="tw-207", region="tw", slug="huisun-forest", score=None,
  names={"zh-TW": "惠蓀林場", "en": "Huisun Forest Station (NCHU experimental forest)",
         "ja": "恵蓀林場", "local": "惠蓀林場"},
  lat=24.0818290, lon=121.0246615, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 惠蓀實驗林場（南投仁愛鄉新生村，nature_reserve 節點）；海拔 450-2419m 垂直分佈（中興大學官方頁），單值不可取、altitude_m 誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E6%83%A0%E8%93%80%E6%9E%97%E5%A0%B4",
                 "https://www.nchu.edu.tw/important-link/mid/378"],
  admin="南投縣", category="本島", tags=["forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="惠蓀林場原生樟楓林與關刀溪谷", en="Huisun forest and Guandao-river valley", ja="恵蓀林場の林と渓谷",
    desc_zh="惠蓀林場（國立中興大學實驗林官方頁；7,477 公頃、海拔 450-2419m 垂直分佈、原生樟楓林與關刀溪谷）森林主體（OSM nature_reserve 節點；海拔帶不可單值化、誠實留空）；清單主題的紅葉/日出季窗查無本站可繫結的權威季節資料源，誠實不建時間窗契約；與同清單惠蓀林場高點（~1km）同林場家族叢集——高點列不重複入庫。",
    desc_en="Huisun Forest Station (NCHU official experimental-forest page; 7,477 ha, 450-2,419 m vertical range, native camphor-maple forest and the Guandao creek valley). The list's maple/sunrise windows have no bindable seasonal source - honestly no time-window contract; the sibling 'Huisun high point' row (~1 km) is the same forest family and not separately admitted.",
    desc_ja="恵蓀林場（中興大学実験林公式、原生林と渓谷）。紅葉・日の出の季節窓は権威源がなく誠実に不構築。"),
  ]),
 dict(place_id="tw-208", region="tw", slug="tiaoshui-trail", score=None,
  names={"zh-TW": "挑水古道", "en": "Tiaoshui (water-carrying) historic trail (Fenyuan)",
         "ja": "挑水古道", "local": "挑水古道"},
  lat=23.9617648, lon=120.6298199, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 挑水古道（彰化芬園鄉大竹村，track 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E6%8C%91%E6%B0%B4%E5%8F%A4%E9%81%93",
                 "https://www.trimt-nsa.gov.tw/zh-tw/trail/78/"],
  admin="彰化縣", category="本島", tags=["forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="挑水古道石階與龍鳳湧泉步道", en="Tiaoshui-trail stone steps and Longfeng springs", ja="挑水古道の石段と湧泉",
    desc_zh="挑水古道（參山國家風景區官方步道頁第一級步道 2.01km；先民挑水踏出的石砌路、龍鳳湧泉）森林步道主體（OSM track 節點；海拔誠實留空）；清單主題的油桐花季窗查無本站可繫結的權威季節資料源，誠實不建時間窗契約；與既有 tw-175 橫山觀日步道（7.67km）題材錯位。",
    desc_en="Tiaoshui historic trail (officially graded trail page of the Tri-Mountain NSA; 2.01 km of stone-paved water-carrying path with the Longfeng springs; OSM track node). The list's tung-blossom window has no bindable seasonal source - honestly no time-window contract; disjoint from tw-175 Hengshan sunrise trail 7.67 km away.",
    desc_ja="挑水古道（参山風景区公式の歩道頁）（OSM）。油桐の季節窓は権威源がなく誠実に不構築。"),
  ]),
 dict(place_id="tw-209", region="tw", slug="cihou-lighthouse", score=None,
  names={"zh-TW": "旗後燈塔／旗津星空隧道", "en": "Cihou Lighthouse and Qijin Star Tunnel",
         "ja": "旗後燈塔／星空トンネル", "local": "旗後燈塔"},
  lat=22.6142256, lon=120.2671891, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 旗后燈塔（高雄旗津區旗下里通山路，bus_stop 節點對位旗後山頂燈塔園區、待現場校準）；航港局 WGS84 22°36.924'；海拔查無權威單值誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E6%97%97%E5%BE%8C%E7%87%88%E5%A1%94",
                 "https://www.motcmpb.gov.tw/Lighthouse/Detail/2f3c9806-8e45-404c-9938-cbc98d879d5f?SiteId=1&NodeId=50091"],
  admin="高雄市", category="本島", tags=["coast", "city"],
  subjects=[
   dict(suffix="P01", template="city_night", seasonal=None,
    zh="旗後燈塔夜間園區與高雄港燈火", en="Cihou Lighthouse night grounds and Kaohsiung-port lights", ja="旗後燈塔の夜と高雄港の灯り",
    desc_zh="旗後燈塔（交通部航港局官方頁；1883 年建、市定古蹟、2022 年起全台首座夜間開放燈塔園區）與旗後山頂俯瞰高雄港燈火（OSM bus_stop 節點對位、待現場校準；海拔誠實留空）；與既有 tw-028 駁二藝術特區（1.64km）題材錯位——本點為旗後山燈塔古蹟夜景主體。",
    desc_en="Cihou Lighthouse (Maritime and Port Bureau official page; built 1883, city-designated historic site, the first Taiwan lighthouse ground open at night since 2022) with Kaohsiung-port lights from Cihou hill (OSM bus-stop node as proxy); disjoint from tw-028 Pier-2 art center 1.64 km away.",
    desc_ja="旗後燈塔（航港局公式、2022年から夜間公開）から高雄港の灯り（OSM）。駁二とは題材が別。"),
  ]),
 dict(place_id="tw-210", region="tw", slug="wuyanjiao-cape", score=None,
  names={"zh-TW": "東澳烏岩角海蝕拱門", "en": "Wuyanjiao sea arch (Dong'ao, Su'ao)",
         "ja": "東澳・烏岩角の海蝕アーチ", "local": "烏岩角"},
  lat=24.5343773, lon=121.8753409, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 烏岩角（宜蘭蘇澳鎮東澳灣，peak 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E7%83%8F%E5%B2%A9%E8%A7%92",
                 "https://jotdownvoyage.com/onfoottaiwan/wuyanjiao-hiking-journey/"],
  admin="宜蘭縣", category="本島", tags=["coast", "geology"],
  subjects=[
   dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="烏岩角陸連島海蝕拱門與秘境沙灘", en="Wuyanjiao tied-island arch and hidden beach", ja="烏岩角の陸繋島と海蝕アーチ",
    desc_zh="烏岩角（中央山脈起點的陸連島海岬；行記/媒體記錄的海蝕拱門與大潮沒鞍的孤島地形、台9丁線 10.8K 陡下路線）地質主體（OSM peak 節點；海拔誠實留空）；與既有 tw-152 南方澳觀景台（4.77km）題材錯位——本點為東澳灣海岬地質主體；海路/陡下路線皆有風險，access 記錄。",
    desc_en="Wuyanjiao, the tied-island cape at the northern start of the Central Range in Dong'ao bay (sea arch and tide-cut saddle per travel/media records; the steep T9D 10.8K descent route) - a geology subject (OSM peak node); disjoint from tw-152 Nanfang'ao lookout 4.77 km away; both sea and land approaches are risky (access note).",
    desc_ja="中央山脈起点の陸繋島・烏岩角の海蝕アーチ（OSM）。南方澳観景台とは題材が別。往路は危険を伴う。"),
  ]),
 dict(place_id="tw-211", region="tw", slug="alangyi-trail", score=None,
  names={"zh-TW": "阿朗壹古道海岸", "en": "Alangyi historic-trail coast (Nantian-Xuhai)",
         "ja": "阿朗壹古道の海岸", "local": "阿朗壹古道"},
  lat=22.2474301, lon=120.8946598, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 阿朗壹古道（台東達仁鄉南田村，track 節點對位南田端、待現場校準）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E9%98%BF%E6%9C%97%E5%A3%B9%E5%8F%A4%E9%81%93",
                 "https://zh.wikipedia.org/wiki/%E9%98%BF%E6%9C%97%E5%A3%B9%E5%8F%A4%E9%81%93"],
  admin="屏東縣", category="本島", tags=["coast", "geology"],
  subjects=[
   dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="阿朗壹古道礫石海岸與原生林", en="Alangyi-trail boulder shore and coastal primary forest", ja="阿朗壹古道の礫石海岸",
    desc_zh="阿朗壹古道（zh.wikipedia 瑯嶠卑南道現存段；南田至旭海的海岸礫石小徑與台灣僅存海岸原生林；屏東段位旭海觀音鼻自然保留區——入內須事先申請、解說員帶領，access 記錄）地質主體（OSM track 節點對位、待現場校準；海拔誠實留空）；與既有 tw-155 旭海草原公園（4.85km）題材錯位——本點為古道礫石海岸主體。",
    desc_en="The Alangyi (Langqiao-Beinan) historic-trail coast (zh.wikipedia; boulder shore and one of Taiwan's last primary coastal forests between Nantian and Xuhai; the Pingtung section sits in the Xuhai-Guanyinbi Nature Reserve - advance permit and guide required, access note); disjoint from tw-155 Xuhai grassland park 4.85 km away.",
    desc_ja="阿朗壹古道の礫石海岸と海岸原生林（zh.wikipedia）。屏東側は旭海観音鼻自然保留区で申請制。旭海草原とは題材が別。"),
  ]),
 dict(place_id="tw-212", region="tw", slug="zhangyuan-reef", score=None,
  names={"zh-TW": "樟原海蝕平台", "en": "Zhangyuan wave-cut platform (Changbin)",
         "ja": "樟原の海蝕平台", "local": "樟原"},
  lat=23.4160930, lon=121.4841560, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 樟原聚落（台東長濱鄉樟原村，village 節點對位；樟原橋遊憩區位水母丁溪畔、海岸海蝕平台沿台11線 77K 前後、待現場校準）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E6%A8%9F%E5%8E%9F%20%E9%95%B7%E6%BF%B1",
                 "https://www.eastcoast-nsa.gov.tw/zh-tw/attractions/detail/162/"],
  admin="台東縣", category="本島", tags=["coast", "geology"],
  subjects=[
   dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="樟原海岸海蝕平台與水母丁溪火山集塊岩", en="Zhangyuan wave-cut platform and Shuimuding volcanic agglomerate", ja="樟原の海蝕平台と水母丁渓の火山集塊岩",
    desc_zh="樟原（東部海岸國家風景區官方列名；台東海岸最北端聚落、樟原橋三橋並列與水母丁溪火山集塊岩地形）海岸地質主體（OSM village 節點對位、待現場校準；海拔誠實留空）；與既有 tw-114 赤科山金針花海（3.99km）題材錯位——本點為海岸地質主體。",
    desc_en="Zhangyuan, the northernmost coastal village of Taitung (officially listed by the East Coast NSA; three parallel bridges over the Shuimuding creek with its volcanic-agglomerate gorge and the coastal wave-cut platform) - a geology subject (OSM village node as proxy); disjoint from tw-114 Chishan daylily hills 3.99 km away.",
    desc_ja="樟原（東部海岸国家風景区公式、水母丁渓の火山集塊岩と海蝕平台）（OSM）。赤科山とは題材が別。"),
  ]),
 dict(place_id="tw-213", region="tw", slug="huayuan-bay", score=None,
  names={"zh-TW": "華源海灣天空之鏡", "en": "Huayuan bay 'sky mirror' (Taimali)",
         "ja": "華源海灣・天空の鏡", "local": "華源海灣"},
  lat=22.6477057, lon=121.0152021, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 華源海灣觀景點（台東太麻里鄉華源村南迴公路舊線，viewpoint 節點）；蓄水池倒影點沿山坡產業道路、待現場校準；海拔誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E8%8F%AF%E6%BA%90%E6%B5%B7%E7%81%A3",
                 "https://appi.news/articles/huayuan-bay-sky-mirror-guide/"],
  admin="台東縣", category="本島", tags=["coast"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="華源海灣蓄水池倒影與弧形海灣", en="Huayuan-bay cistern reflections and arc shoreline", ja="華源海灣の水鏡と弧状の海岸",
    desc_zh="華源海灣（臺東觀光旅遊網標示台9線華源段；山坡灌溉蓄水池映出海天倒影的「天空之鏡」、行記/媒體列名）觀景主體（OSM viewpoint 節點；倒影蓄水池實址沿產業道路待現場校準；海拔誠實留空）；與既有 tw-116 太麻里金針山（4.51km）題材錯位——本點為海灣倒影主體。",
    desc_en="Huayuan bay on the Taimali coast (the 'sky mirror' irrigation-cistern reflections above the arc shoreline; Taitung tourism pages and media write-ups; OSM viewpoint node, cistern site up the farm road pending field calibration); disjoint from tw-116 Taimali daylily mountain 4.51 km away.",
    desc_ja="華源海灣の「天空の鏡」蓄水池の水鏡（台東観光公式・メディア）（OSM）。金針山とは題材が別。"),
  ]),
 dict(place_id="tw-214", region="tw", slug="daniao-recarea", score=None,
  names={"zh-TW": "大鳥遊憩區觀海平台", "en": "Daniao recreation-area ocean platform (Dawu)",
         "ja": "大鳥遊憩区の観海平台", "local": "大鳥遊憩區"},
  lat=22.3884258, lon=120.9013411, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 大鳥村（台東大武鄉，administrative 節點對位台9線大鳥遊憩區、待現場校準）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E5%A4%A7%E9%B3%A5%E6%9D%91%20%E5%A4%A7%E6%AD%A6",
                 "https://cmeyy.tw/blog/post/20241105"],
  admin="台東縣", category="本島", tags=["coast"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="大鳥遊憩區觀海平台", en="Daniao ocean-viewing platform", ja="大鳥遊憩区の海の展望台",
    desc_zh="大鳥遊憩區（台9線大武段、zh.wikipedia 大武鄉旅遊列名；清水模觀海平台與太平洋海景）觀景主體（OSM 大鳥村 administrative 節點對位、待現場校準；海拔誠實留空）；清單主題的「海蝕崖」語義查無本站權威資料源——誠實以官方列名的觀海平台主體登記；與既有 tw-037 多良火車站觀景台（14.5km）題材錯位。",
    desc_en="Daniao recreation area on the T9 Dawu section (listed under Dawu tourism in zh.wikipedia; the concrete ocean-viewing platform over the Pacific). The list's 'sea cliff' wording has no authoritative source here - honestly registered as the officially listed viewing platform; disjoint from tw-037 Duoliang station lookout 14.5 km away.",
    desc_ja="大鳥遊憩区（大武郷、観海平台）（OSMで対位）。海蝕崖の語義は権威源がなく展望台主体で登録。多良駅とは題材が別。"),
  ]),
 dict(place_id="tw-215", region="tw", slug="jinshuiying-trail", score=None,
  names={"zh-TW": "浸水營古道", "en": "Jinshuiying historic trail (Fengliao-Dawu)",
         "ja": "浸水營古道", "local": "浸水營古道"},
  lat=22.4083146, lon=120.7750721, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 浸水營古道姑仔崙山登山口（台東達仁鄉新化村，trailhead 節點對位東段、待現場校準）；海拔查無權威單值誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E6%B5%B8%E6%B0%B4%E7%87%9F%E5%8F%A4%E9%81%93",
                 "https://taitung.forest.gov.tw/0000170"],
  admin="屏東縣", category="本島", tags=["mountain", "forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="浸水營古道霧林與人文史蹟", en="Jinshuiying mist forest and historic relics", ja="浸水營古道の霧林と史跡",
    desc_zh="浸水營國家步道（林業及自然保育署台東分署官方頁；枋寮水底寮至大武加羅板、越嶺點最低的古道；清代撫番道路史蹟）霧林步道主體（OSM 姑仔崙山登山口 trailhead 節點對位、待現場校準；海拔誠實留空）；清單主題的霧林季窗查無可繫結的權威季節資料源，誠實不建時間窗契約；與既有 tw-037 多良火車站（21.9km）題材錯位。",
    desc_en="The Jinshuiying National Trail (officially listed by the Forestry and Nature Conservation Agency Taitung branch; the lowest central-range crossing, from Shuidiliao to Jia luoban, with Qing-era relics) - a mist-forest trail subject (OSM Guzilun trailhead node as proxy). No bindable mist-season source - honestly no time-window contract; disjoint from tw-037 Duoliang station 21.9 km away.",
    desc_ja="浸水營国家歩道（林業保育署台東分署公式、霧林と清代の史跡）（OSMの登山口ノードで対位）。季節窓は権威源がなく不構築。"),
  ]),
 dict(place_id="tw-216", region="tw", slug="yuwengdao-lighthouse", score=None,
  names={"zh-TW": "漁翁島燈塔", "en": "Yuwingdao (Xiyu) Lighthouse, Penghu",
         "ja": "漁翁島灯台", "local": "漁翁島燈塔"},
  lat=23.5625548, lon=119.4690827, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 西嶼燈塔（澎湖西嶼鄉外垵村，lighthouse 節點）；航港局 WGS84 23°33.753'；海拔查無權威單值誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E6%BC%81%E7%BF%81%E5%B3%B6%E7%87%88%E5%A1%94",
                 "https://www.motcmpb.gov.tw/Lighthouse/Detail/d793b0f1-7230-48a8-9a7a-c0ca4b2fccb8?SiteId=1&NodeId=50091"],
  admin="澎湖縣", category="離島", tags=["coast"],
  subjects=[
   dict(suffix="P01", template="sunset", seasonal=None,
    zh="漁翁島燈塔西嶼落霞", en="Yuwingdao Lighthouse sunset (Xiyu glow)", ja="漁翁島灯台の夕焼け",
    desc_zh="漁翁島燈塔（交通部航港局官方頁；1778 年西嶼塔燈舊址、1875 年新式鐵塔、國定古蹟、外垵高地燈塔公園）向西台灣海峽的「西嶼落霞」夕照（OSM lighthouse 節點；海拔誠實留空）；與既有 tw-079 池西柱狀玄武岩（5.69km）題材錯位——本點為燈塔夕照主體。",
    desc_en="Yuwingdao (Xiyu) Lighthouse (Maritime and Port Bureau official page; on the 1778 Xiyu tower site, rebuilt 1875, a national historic site on the waitan highland) facing the famous 'Xiyu sunset glow' over the Taiwan Strait (OSM lighthouse node); disjoint from tw-079 Chixi columnar basalt 5.69 km away.",
    desc_ja="漁翁島灯台（国定古蹟、外垵の高地）から台湾海峡の「西嶼落霞」（OSM）。池西柱状玄武岩とは題材が別。"),
  ]),
]

# subject-disjoint overrides for <5km neighbours (CL-DATA-51/64/66 precedent)
DIFF_OVERRIDES = {
    "tw-201": ("tw-010", "和平島公園",
        "subject-disjoint: Keelung Lighthouse historic cape-and-channel subject vs Heping Island island-park geology - 2.08km apart, disjoint subjects"),
    "tw-202": ("tw-105", "太平雲梯／梅山36彎",
        "subject-disjoint: Tanghu historic-trail stone steps and ridge outlook (Zhuqi) vs Taiping suspension-bridge/M36-bend viewpoint (Meishan) - 4.47km apart, disjoint subjects"),
    "tw-205": ("tw-071", "小琉球花瓶岩",
        "subject-disjoint: Longxiadong sea-cut channels and pothole geology vs Vase Rock snorkel landmark - 1.32km apart, disjoint subjects"),
    "tw-209": ("tw-028", "駁二藝術特區",
        "subject-disjoint: Cihou Lighthouse historic night grounds on Cihou hill vs Pier-2 art-district harbourfront - 1.64km apart, disjoint subjects"),
    "tw-210": ("tw-152", "南方澳觀景台",
        "subject-disjoint: Wuyanjiao tied-island sea arch in Dong'ao bay vs Nanfang'ao harbour-bay lookout - 4.77km apart, disjoint subjects"),
    "tw-211": ("tw-155", "旭海草原公園",
        "subject-disjoint: Alangyi historic-trail boulder shore/coastal forest vs Xuhai grassland park - 4.85km apart, disjoint subjects"),
    "tw-212": ("tw-114", "赤科山金針花海",
        "subject-disjoint: Zhangyuan coastal wave-cut platform geology vs Chishan daylily-flower hills - 3.99km apart, disjoint subjects"),
    "tw-213": ("tw-116", "太麻里金針山",
        "subject-disjoint: Huayuan-bay cistern sky-mirror reflections vs Taimali daylily mountain - 4.51km apart, disjoint subjects"),
}

# rejected within-5km family overlaps / exclusions: recorded in manifest, NOT admitted
REJECTED_PLACES = [
    ("四角窟海蝕平台", "identical existing place: 0.36km from existing tw-102 三貂角燈塔 - same 三貂角 cape family"),
    ("國聖港燈塔", "identical existing subject: 0.66km from wave-5 tw-194 頂頭額沙洲 - the lighthouse is already named inside tw-194's sunset contract"),
    ("基隆燈塔", "admitted as tw-201"),
    ("塘湖古道", "admitted as tw-202"),
    ("大石鼻山海蝕崖", "admitted as tw-203"),
    ("大菓葉柱狀玄武岩", "5km dedupe reject: 1.66km from existing tw-079 池西柱狀玄武岩／池西岩瀑九孔池 - same columnar-basalt geology family, not subject-disjoint"),
    ("大鳥海岸海蝕崖", "re-registered: list's 海蝕崖 wording unverifiable, the official listing is 大鳥遊憩區觀海平台 (zh.wikipedia Dawu tourism) - admitted as tw-214"),
    ("太麻里華源海蝕平台", "admitted as tw-213"),
    ("富岡漁港海蝕岩", "5km dedupe reject: 0.84km from existing tw-090 加路蘭海岸遊憩區 - same 富岡 coastal family, and the specific 海蝕岩 identity is unverifiable"),
    ("富源森林遊樂區/蝴蝶谷", "admitted as tw-204"),
    ("小琉球龍蝦洞海蝕溝", "admitted as tw-205"),
    ("嶺頂頭海蝕平台", "admitted as tw-206"),
    ("恩愛農場", "owner minor-spot exclusion: private 拉拉山 homestay/farm (桃園復興), analogous to the homestay exclusion (三才靈芝農場 wave-5 precedent)"),
    ("惠蓀林場", "admitted as tw-207"),
    ("惠蓀林場高點", "family-cluster row: ~1km inside the admitted tw-207 惠蓀林場 - same forest family, not separately admitted"),
    ("拉拉山恩愛農場/神木區", "owner minor-spot exclusion: same private 恩愛農場 as the sibling row (dup)"),
    ("挑水古道", "admitted as tw-208"),
    ("旗後燈塔/旗津星空隧道", "admitted as tw-209"),
    ("旗津黑砂+旗後燈塔", "family-cluster row: same 旗後燈塔/旗後山 subject as admitted tw-209, not separately admitted"),
    ("明池國家森林遊樂區高點", "identical existing place: same OSM node as existing tw-173 明池森林遊樂區 (0km)"),
    ("月洞海蝕穴", "5km dedupe reject: 1.23km from existing tw-077 石梯坪海蝕平台／壺穴群 - same 石梯坪 attraction family, not subject-disjoint"),
    ("東澳烏岩角海蝕拱門", "admitted as tw-210"),
    ("柴山/阿朗壹古道海蝕岩", "re-registered: mixed 柴山/阿朗壹 wording, the verifiable subject is the 阿朗壹古道 coast (zh.wikipedia; OSM track nodes) - admitted as tw-211"),
    ("樟原海蝕平台", "admitted as tw-212"),
    ("水湳洞陰陽海海蝕崖", "5km dedupe reject: 1.10km from existing tw-137 報時山觀景台 - same 水湳洞/陰陽海 family (the lookout overlooks the same bay), not subject-disjoint"),
    ("浸水營古道", "admitted as tw-215"),
    ("清境青青草原/觀星園", "identical existing place: 0.67km from existing tw-103 清境農場 - same farm subject"),
    ("清水斷崖海蝕岩壁", "identical existing place: 2.74km from existing tw-034 崇德清水斷崖展望點 - same cliff subject"),
    ("漁翁島燈塔", "admitted as tw-216"),
    ("漢本海蝕崖", "honest reject: identity/coordinate unverifiable - OSM only yields the 漢本 station/hamlet nodes, no 海蝕崖 feature node and no authoritative source for the specific cliff (the area's coast is already covered by tw-200 南澳海蝕洞)"),
]

REJECT_TIER_A_NAMES = [
    "四角窟海蝕平台", "國聖港燈塔", "大菓葉柱狀玄武岩", "富岡漁港海蝕岩",
    "恩愛農場", "惠蓀林場高點", "拉拉山恩愛農場/神木區", "旗津黑砂+旗後燈塔",
    "明池國家森林遊樂區高點", "月洞海蝕穴", "水湳洞陰陽海海蝕崖",
    "清境青青草原/觀星園", "清水斷崖海蝕岩壁", "漢本海蝕崖",
]
REJECT_REASONS = {n: r for n, r in REJECTED_PLACES if n in REJECT_TIER_A_NAMES}
assert len(REJECT_REASONS) == 14, len(REJECT_REASONS)
ADM_TIER_A_NAMES = {
    "基隆燈塔": "tw-201", "塘湖古道": "tw-202", "大石鼻山海蝕崖": "tw-203",
    "富源森林遊樂區/蝴蝶谷": "tw-204", "小琉球龍蝦洞海蝕溝": "tw-205",
    "嶺頂頭海蝕平台": "tw-206", "惠蓀林場": "tw-207", "挑水古道": "tw-208",
    "旗後燈塔/旗津星空隧道": "tw-209", "東澳烏岩角海蝕拱門": "tw-210",
    "柴山/阿朗壹古道海蝕岩": "tw-211", "樟原海蝕平台": "tw-212",
    "太麻里華源海蝕平台": "tw-213", "大鳥海岸海蝕崖": "tw-214",
    "浸水營古道": "tw-215", "漁翁島燈塔": "tw-216",
}
assert set(ADM_TIER_A_NAMES.values()) == {f"tw-{n}" for n in range(201, 217)}
assert {p["place_id"] for p in PLACES} == set(ADM_TIER_A_NAMES.values())
assert len(REJECTED_PLACES) == 30


def wb(p, text): return m64.wb(p, text)


def _build_contract(p, subj):
    """Copy of the wave-5 contract builder; module globals resolve to wave-6."""
    oid = f"{p['place_id']}-{subj['suffix']}"
    tpl = subj["template"]
    if tpl == "seasonal_plant":
        conds = cl.clone_conditions(oid, "seasonal_plant")
        if "seasonal_state" not in [c["metric"] for c in conds]:
            conds.insert(0, cl.seasonal_condition(oid, subj["seasonal"]))
    elif tpl == "night_sky":
        conds = cl.clone_conditions(oid, "night_sky")
    elif tpl == "geological_landform":
        conds = cl.clone_conditions(oid, "geological_landform")
    else:
        conds = cl.clone_conditions(oid, tpl)
    lw_n = 0
    for c in conds:
        if c["id"] and c["id"].endswith("-LW1"):
            lw_n += 1
            if lw_n > 1:
                c["id"] = f"C-{oid}-LW{lw_n}"
    ids = [c["id"] for c in conds]
    assert len(ids) == len(set(ids)), f"{oid} duplicate condition ids"
    geo_src = " ; ".join(p["coord_sources"])
    deriv = (f"{TICKET} wave-{WAVE} admission web verification {VER_DATE} ({p['coord_source']}; "
             f"source URLs: {geo_src}). Scoreless intake (owner ruling 2026-11-11): "
             "admission = verification + 5km subject-disjoint dedupe; score fields empty.")
    access = {
        "zh-TW": subj["desc_zh"] + "（開放/營運狀態以現場公告為準。）",
        "en": subj["desc_en"] + " (Opening/operating status follows on-site notices.)",
        "ja": subj["desc_ja"] + "（開放・営業状況は現地の案内に従う。）",
    }
    elev = p.get("elev_m")
    point = {"kind": "point", "status": "provisional",
             "geojson": {"type": "Point", "coordinates": [p["lon"], p["lat"]]},
             "uncertainty_m": None, "derivation_method": deriv,
             "source_geometry_revision": None, "reason_if_absent": None}
    return {
        "schema_version": "2.1.0",
        "opportunity_id": oid,
        "place_id": p["place_id"],
        "revision": 1,
        "lifecycle_status": "draft",
        "name_i18n": {"zh-TW": subj["zh"], "en": subj["en"], "ja": subj["ja"]},
        "description_i18n": {"zh-TW": subj["desc_zh"], "en": subj["desc_en"], "ja": subj["desc_ja"]},
        "camera_contexts": [{
            "id": f"CZ-{oid}-01", "kind": "area", "geometry": dict(point),
            "verification_status": "provisional", "evidence_refs": [],
            "access_notes_i18n": access, "safety_notes_i18n": {
                "zh-TW": "請依現場安全指示行動；夜間/冬季天候險惡時請勿冒進。",
                "en": "Follow on-site safety guidance; do not push on in severe night/winter weather.",
                "ja": "現地の安全指示に従う。夜間・冬季の悪天候では無理をしない。",
            },
            "altitude_m": float(elev) if elev else None,
        }],
        "targets": [{
            "id": f"SG-{oid}-01", "kind": "multi_component",
            "name_i18n": {"zh-TW": subj["zh"], "en": subj["en"], "ja": subj["ja"]},
            "geometry": dict(point), "phenomenon_model_id": None,
            "evidence_refs": [], "components": [],
        }],
        "observation_relations": [{
            "id": f"VR-{oid}-01", "camera_context_id": f"CZ-{oid}-01",
            "target_id": f"SG-{oid}-01", "type": "foreground_background",
            "geometry_mode": "unknown", "azimuth_deg": None, "elevation_deg": None,
            "distance_m": None, "evidence_refs": [],
            "derivation_method": None,
            "uncertainty_note": f"{TICKET} wave-{WAVE} admission reference; angles and distance unknown pending field survey.",
        }],
        "navigation_targets": [{
            "id": f"NAV-{oid}-01", "status": "needs_review", "target_type": "other",
            "lat": p["lat"], "lon": p["lon"],
            "label_i18n": {"zh-TW": p["names"]["local"], "en": p["names"]["en"], "ja": p["names"]["local"]},
            "evidence_refs": [], "confidence": "low",
        }],
        "condition_contract": {
            "contract_id": f"CC-{oid}-v1", "status": "draft",
            "genre_template": tpl, "template_version": f"{tpl}-v0.1",
            "recommendation_policy_version": None,
            "conditions": conds,
        },
        "evidence_claims": [{
            "claim_id": f"{oid}-claim-01", "claim_type": "existence",
            "evidence_refs": [f"e-d66-web-{p['slug']}"], "audit_status": "UNKNOWN",
            "scope_note": f"{TICKET} wave-{WAVE} scoreless admission (owner ruling 2026-11-11: verification + 5km subject-disjoint dedupe; NO rubric/AGLI scoring); coordinates/elevation web-verified {VER_DATE} (sources in camera derivation_method and data/v2/audits/cl-data-66_web_evidence.json); 查無權威源之海拔誠實留空 (null); thresholds provisional pending real-shoot calibration.",
        }],
        "readiness": {"research_level": "R1", "gaps": ["RESEARCH_GAP"]},
        "provenance": {
            "source_catalog": f"{TICKET} Tier-A wave-{WAVE} intake (owner-list streams, scoreless {VER_DATE})",
            "source_revision": f"cl-data-66:{p['slug']}",
            "imported_at": f"{VER_DATE}T00:00:00Z",
            "review_status": "pending", "reviewed_by": None,
        },
    }


def main():
    # ---- 0) dedupe audit ----
    def hav(a, b, c, d):
        Rr = 6371000; p1, p2 = math.radians(a), math.radians(c)
        dp = p2 - p1; dl = math.radians(d - b)
        h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return 2*Rr*math.asin(math.sqrt(h))
    import regions as R
    dedupe_path = ROOT / "data/v2/audits/discovery/cl-data-66-dedupe.json"
    dedupe = json.loads(dedupe_path.read_bytes().decode("utf-8"))
    existing = R.get_spots("tw")  # includes tw-125..tw-200
    rows = {}
    for p in PLACES:
        pool = [s for s in existing if s["spot_id"] != p["place_id"]] + [
            {"spot_id": q["place_id"], "lat": q["lat"], "lon": q["lon"],
             "name_i18n": {"zh-TW": q["names"]["zh-TW"]}}
            for q in PLACES if q is not p]
        dists = sorted((hav(p["lat"], p["lon"], s["lat"], s["lon"])/1000, s["spot_id"],
                        s["name_i18n"]["zh-TW"]) for s in pool)
        nearest = dists[0]
        ov = DIFF_OVERRIDES.get(p["place_id"])
        if ov is None and nearest[0] < 5.0:
            raise AssertionError(f"{p['place_id']} within 5km of {nearest} without override")
        row = {"nearest_existing": nearest[1], "name": nearest[2], "km": round(nearest[0], 2)}
        if ov:
            row["override"] = ov[2]
            assert nearest[1] == ov[0], f"{p['place_id']} override {ov[0]} != nearest {nearest}"
        rows[p["place_id"]] = row
    dedupe[f"_rejected_family_overlaps_wave{WAVE}"] = [
        {"name": n, "reason": REJECT_REASONS[n]} for n in REJECT_TIER_A_NAMES]
    dedupe.update(rows)
    wb(dedupe_path, json.dumps(dedupe, ensure_ascii=False, indent=1) + "\n")
    print("dedupe OK", {k: v["km"] for k, v in rows.items()})

    # ---- 1) V2 contracts ----
    written = []
    for p in PLACES:
        for subj in p["subjects"]:
            c = _build_contract(p, subj)
            out = cl.DATA / f"{c['opportunity_id']}.json"
            cl.wbytes(out, cl.jdump(c))
            written.append(c["opportunity_id"])
    print("contracts written:", len(written))

    # ---- 2) regions.py (insert AFTER the wave-5 block, before admin map) ----
    rp = ROOT / "regions.py"
    text = rp.read_bytes().decode("utf-8").replace("\r\n", "\n")
    if '"tw-201"' not in text:
        a_tw = '            (24.4014567, 121.7891201, "南澳海蝕洞", "Nan\'ao sea cave (Su\'ao-Hualien coast)", "南澳の海蝕洞", "南澳海蝕洞", "本島", ["coast", "geology"]),  # CL-DATA-66\n'
        assert a_tw in text, "wave-5 last tuple anchor missing"
        lines = []
        for p in PLACES:
            n = p["names"]
            lines.append(
                f'            ({p["lat"]}, {p["lon"]}, "{n["zh-TW"]}", "{n["en"]}", '
                f'"{n["ja"]}", "{n["local"]}", "{p["category"]}", {json.dumps(p["tags"], ensure_ascii=False)}),  # {TICKET}\n')
        text = text.replace(a_tw, a_tw + "".join(lines), 1)
        a_admin = '    "tw-200": ["宜蘭縣"],  # CL-DATA-66\n'
        assert a_admin in text, "admin anchor missing"
        adm = "".join(f'    "{p["place_id"]}": ["{p["admin"]}"],  # {TICKET}\n' for p in PLACES)
        text = text.replace(a_admin, a_admin + adm, 1)
        a_elev = '    # CL-DATA-66 wave-3 admission elevations (web-verified 2026-11-11; null elevations omitted honestly)\n'
        assert a_elev in text, "elev anchor missing"
        elev = f'    # {TICKET} wave-{WAVE} admission elevations (web-verified {VER_DATE}; null elevations omitted honestly)\n'
        for p in PLACES:
            if p["elev_m"] is not None:
                elev += f'    "{p["names"]["local"]}": {p["elev_m"]},  # {TICKET}\n'
        text = text.replace(a_elev, elev + a_elev, 1)
        a_o = 'SPOT_OVERRIDES = {\n'
        ii = text.index(a_o) + len(a_o)
        cins = f'    # {TICKET} wave-{WAVE} admission (web-verified {VER_DATE}; keyed to full display names per get_spots contract)\n'
        for p in PLACES:
            q = p["names"]["local"]
            src = p["coord_source"].replace('"', "'")
            cins += (' "%s": {"lat": %s,\n           "lon": %s,\n           "map_query": %s,\n'
                     '           "coordinate_source": %s,\n           "coordinate_confidence": "%s"},\n'
                     % (p["names"]["zh-TW"], p["lat"], p["lon"],
                        json.dumps(q, ensure_ascii=False),
                        json.dumps(f"{TICKET} wave-{WAVE} admission web verification {VER_DATE}: " + src, ensure_ascii=False),
                        p["coord_conf"]))
        text = text[:ii] + cins + text[ii:]
        wb(rp, text)
    print("regions.py patched")

    # ---- 3) runtime catalog ----
    cat_path = ROOT / "runtime_catalog_v004_r4_2.json"
    cat = json.loads(cat_path.read_bytes().decode("utf-8"))
    max_var = 0
    for s in cat["spots"]:
        for o in s["opportunities"]:
            for v in o.get("condition_variants", []):
                max_var = max(max_var, int(str(v["variant_id"]).split("-")[1]))
    have_ids = {s["spot_id"] for s in cat["spots"]}
    var_id = max_var + 1
    for p in PLACES:
        if p["place_id"] in have_ids:
            continue
        spot, _ = cl.build_legacy_spot(p, var_id)
        var_id += len(spot["opportunities"])
        cat["spots"].append(spot)
    cat["spots"].sort(key=lambda s: (s["spot_id"].split("-")[0], int(s["spot_id"].split("-")[1])))
    cat["counts"] = {
        "spots": len({s["spot_id"] for s in cat["spots"]}),
        "opportunities": sum(len(s["opportunities"]) for s in cat["spots"]),
        "condition_variants": sum(sum(len(o.get("condition_variants", [])) for o in s["opportunities"]) for s in cat["spots"]),
        "profile_viewpoint_relations": sum(sum(len(o.get("viewpoints", [])) for o in s["opportunities"]) for s in cat["spots"]),
    }
    cl.wbytes(cat_path, cl.jdump(cat))
    print("runtime catalog counts:", cat["counts"])

    # ---- 4) manifest ----
    mf_path = ROOT / "runtime_catalog_manifest_r4_2.json"
    cat = json.loads(cat_path.read_bytes().decode("utf-8"))
    spots = [s for s in cat["spots"] if s["spot_id"].startswith("tw-")]
    opps = [o for s in spots for o in s["opportunities"]]
    mf = json.loads(mf_path.read_bytes().decode("utf-8"))
    mf["regions"]["tw"]["numeric_id_end"] = max(int(p["place_id"].split("-")[1]) for p in PLACES)
    mf["regions"]["tw"]["counts"] = {
        "spots": len(spots), "opportunities": len(opps),
        "condition_variants": sum(len(o.get("condition_variants", [])) for o in opps),
        "profile_viewpoint_relations": sum(len(o.get("viewpoints", [])) for o in opps)}
    mf["totals"] = dict(cat["counts"])
    cl.wbytes(mf_path, cl.jdump(mf))
    import opportunities as _O
    from collections import Counter as _C
    pol = _C()
    for s in cat["spots"]:
        for o in s["opportunities"]:
            pol[_O.runtime_policy(o)] += 1
    mf = json.loads(mf_path.read_bytes().decode("utf-8"))
    mf["runtime_policy_counts"] = dict(pol)
    cl.wbytes(mf_path, cl.jdump(mf))
    print("manifest tw end:", mf["regions"]["tw"]["numeric_id_end"])

    # ---- 5) web evidence registry (extend wave-5 file) ----
    ev_path = ROOT / "data/v2/audits/cl-data-66_web_evidence.json"
    ev = json.loads(ev_path.read_bytes().decode("utf-8"))
    wave_places = []
    wave_evidence = []
    for p in PLACES:
        wave_places.append({
            "place_id": p["place_id"], "slug": p["slug"], "score": None,
            "lat": p["lat"], "lon": p["lon"], "elev_m": p["elev_m"],
            "coord_confidence": p["coord_conf"], "coord_source": p["coord_source"],
            "sources": p["coord_sources"], "subjects": [s["zh"] for s in p["subjects"]],
            "ticket": TICKET, "wave": WAVE})
        wave_evidence.append({
            "id": f"e-d66-web-{p['slug']}", "grade": "A" if p["coord_conf"] == "high" else "B",
            "kind": "official_or_wikipedia_or_osm_text",
            "url": p["coord_sources"][0],
            "supports": p["coord_source"],
            "retrieved_at": VER_DATE,
            "limitation": "Coordinate/elevation verified against cited sources; exact tripod position and access not field-surveyed; opening/closure/permit/reservation status follows on-site notices.",
            "ticket": TICKET, "wave": WAVE})
    ev[f"places_wave{WAVE}"] = wave_places
    ev[f"evidence_wave{WAVE}"] = wave_evidence
    have_ids = {e["id"] for e in ev["evidence"]}
    ev["evidence"].extend([e for e in wave_evidence if e["id"] not in have_ids])
    ev[f"places_wave{WAVE}_count"] = len(wave_places)
    ev[f"rejected_wave{WAVE}_count"] = len(REJECT_TIER_A_NAMES)
    ev[f"rule_wave{WAVE}"] = (f"Scoreless intake wave {WAVE} (owner ruling 2026-11-11): admission = web verification + "
                        "5km subject-disjoint dedupe; NO rubric v2 gates, NO AGLI dual-board, agli-final "
                        f"untouched; score fields left empty. 16 places admitted (tw-201..tw-216), 14 "
                        "manifest-next-30 candidates rejected (3 identical existing 0.36-2.74km (四角窟/明池高點/清水斷崖) + "
                        "1 already-merged subject (國聖港燈塔 in tw-194) + 2 same-family <5km existing (大菓葉/陰陽海) + "
                        "2 same-attraction family rows (月洞/富岡) + 2 same-wave family-cluster rows (惠蓀林場高點/旗津黑砂) + "
                        "2 private-farm exclusions (恩愛農場 rows) + 1 unverifiable identity (漢本海蝕崖)); "
                        "2 rows re-registered to their verifiable official subjects (大鳥遊憩區 tw-214, 阿朗壹古道 tw-211).")
    wb(ev_path, cl.jdump(ev))
    print("web evidence extended:", len(wave_places))

    # ---- 6) tier-a manifest wave-6 status update ----
    tm_path = ROOT / "data/v2/audits/subject-lists/tier-a-manifest.json"
    tm = json.loads(tm_path.read_bytes().decode("utf-8"))
    rej = dict(REJECT_REASONS)
    changed = 0
    for r in tm["tier_a"]:
        if r.get("status") in ("admitted", "rejected"):
            continue
        if r["name"] in ADM_TIER_A_NAMES:
            r["status"] = "admitted"; r["wave"] = WAVE; r["admitted_place_id"] = ADM_TIER_A_NAMES[r["name"]]
            changed += 1
        elif r["name"] in rej:
            r["status"] = "rejected"; r["wave"] = WAVE; r["reject_reason"] = rej[r["name"]]
            changed += 1
    tm[f"wave{WAVE}"] = {"planned": 30, "order": "n_topics desc, n_lists desc",
                         "done": len(PLACES), "rejected": len(REJECT_TIER_A_NAMES),
                         "place_ids": [p["place_id"] for p in PLACES],
                         "rejected_names": REJECT_TIER_A_NAMES}
    wb(tm_path, cl.jdump(tm))
    print("tier-a manifest updated: changed", changed, "admitted", len(PLACES), "rejected", len(REJECT_TIER_A_NAMES))
    print("DONE wave-6 stage-1 build")


if __name__ == "__main__":
    main()
