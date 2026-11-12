#!/usr/bin/env python3
"""CL-DATA-66 Wave 7 (tail wave): scoreless intake of 11 Tier-A places
(tw-217..tw-227) — the manifest's 27 remaining pending rows; 16 of the 27
rejected (honest per-row reasons in REJECTED_PLACES). Owner rulings
(2026-11-11): intake is SCORELESS — admission = web verification
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
WAVE = 7

PLACES = [
 dict(place_id="tw-217", region="tw", slug="shiyusan-rock", score=None,
  names={"zh-TW": "石雨傘平衡岩海岬", "en": "Shiyusan balanced-rock cape (Chenggong)",
         "ja": "石雨傘のバランス岩", "local": "石雨傘"},
  lat=23.1768735, lon=121.4007995, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 石雨傘（台東成功鎮忠孝里，hamlet 節點對位台11線104.5k 海岬、待現場校準）；海拔查無權威單值誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E7%9F%B3%E9%9B%A8%E5%82%98",
                 "https://www.eastcoast-nsa.gov.tw/zh-tw/attractions/detail/40/"],
  admin="台東縣", category="本島", tags=["coast", "geology"],
  subjects=[
   dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="石雨傘平衡岩與海蝕地貌海岬", en="Shiyusan balanced-rock and sea-erosion cape", ja="石雨傘の平衡岩と海食地形",
    desc_zh="石雨傘（東部海岸國家風景區官方列名，台11線104.5k，長約1公里石灰岩隆起海岬；平衡岩、壺穴、海蝕門與小船澳沙灘）地質主體（OSM hamlet 節點對位、待現場校準；海拔誠實留空）；與既有 tw-192 長濱烏石鼻柱狀火山岩（5.86km）題材錯位——烏石鼻為柱狀火山岩體，本點為隆起石灰岩平衡岩。在此可向南遠眺三仙台（tw-038）但非同一主體。",
    desc_en="Shiyusan (officially listed by the East Coast NSA at the 104.5k mark on Highway 11; a ~1 km limestone-uplift cape with a balanced rock, potholes, a sea arch and the Xiaochuan'ao cove). Disjoint from tw-192 Wushibi's columnar volcanic rock 5.86 km away (uplifted-limestone balanced rock vs basalt columns).",
    desc_ja="石雨傘（東部海岸国家風景区公式、台11線104.5kの石灰岩海岬、平衡岩と壺穴）（OSMで対位）。烏石鼻とは題材が別。"),
  ]),
 dict(place_id="tw-218", region="tw", slug="qianying-garden", score=None,
  names={"zh-TW": "福壽山農場千櫻園", "en": "Fushoushan Farm Qianying cherry garden",
         "ja": "福壽山農場千櫻園", "local": "千櫻園"},
  lat=24.2468592, lon=121.2463891, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 福壽山農場（台中和平區梨山里福壽路，camp_site 節點對位農場園區；千櫻園在農場內、座標以農場節點對位待現場校準）；海拔查無權威單值誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E7%A6%8F%E5%A3%BD%E5%B1%B1%E8%BE%B2%E5%A0%B4",
                 "https://www.trimt-nsa.gov.tw/zh-tw/attraction/66/"],
  admin="台中市", category="本島", tags=["mountain", "forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="千櫻園櫻花海與環繞山景", en="Qianying-garden cherry blossoms and encircling ridges", ja="千櫻園の桜と山並み",
    desc_zh="千櫻園（參山國家風景區官方列名，福壽山農場內8公頃、約6000株多品種櫻花，1-2月緋寒櫻/昭和櫻/富士櫻、3-4月大島櫻/鬱金櫻）賞櫻主體（OSM 農場節點對位、待現場校準；海拔誠實留空）；季節窗為官方生態資訊但查無可繫結的逐窗契約資料源，誠實不建時間窗；與既有 tw-093 福壽山農場觀景點（7.5km）題材錯位——觀景點為農場展望主體，本點為櫻花花海主體。",
    desc_en="Qianying garden (officially listed by the Tri-Mountain NSA; 8 ha inside Fushoushan Farm with ~6,000 cherry trees of many cultivars, blooming in sequence from Jan-Feb Taiwan cherry to Mar-Apr Oshima cherries). Sakura windows are official ecology notes but no bindable per-window data source - honestly no time-window contract; disjoint from tw-093 Fushoushan farm viewpoint 7.5 km away (panorama subject vs cherry-hill subject).",
    desc_ja="千櫻園（參山国家風景区公式、福壽山農場内8ha・約6000本の桜）（OSMで対位）。桜の季節窓は権威源がなく誠実に不構築。福壽山農場展望点とは題材が別。"),
  ]),
 dict(place_id="tw-219", region="tw", slug="shuangliu-forest", score=None,
  names={"zh-TW": "雙流國家森林遊樂區", "en": "Shuangliu National Forest Recreation Area",
         "ja": "双流国家森林遊楽区", "local": "雙流森林遊樂區"},
  lat=22.2269010, lon=120.8181411, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 雙流國家森林遊樂區（屏東獅子鄉丹路村，nature_reserve 節點）；海拔 150-700m 垂直分佈（林業保育署官方頁），單值不可取、誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E9%9B%99%E6%B5%81%E5%9C%8B%E5%AE%B6%E6%A3%AE%E6%9E%97%E9%81%8A%E6%A8%82%E5%8D%80",
                 "https://pingtung.forest.gov.tw/0000135"],
  admin="屏東縣", category="本島", tags=["forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="雙流森林遊樂區白榕步道與雙流瀑布展望", en="Shuangliu banyan trail and waterfall outlook", ja="双流森林遊楽区の眺め",
    desc_zh="雙流國家森林遊樂區（林業保育署屏東分署官方頁，150-700m、白榕步道/帽子山步道/雙流瀑布；蝴蝶逾196種、螢火蟲季為官方生態資訊但查無可繫結的逐窗契約資料源，誠實不建時間窗）森林步道與瀑布展望主體（OSM nature_reserve 節點；海拔垂直分佈、單值誠實留空）；與既有 tw-155 旭海草原公園（7.33km）題材錯位。",
    desc_en="Shuangliu National Forest Recreation Area (officially listed by the Forestry and Nature Conservation Agency Pingtung branch; 150-700 m, banyan/Hat-mountain trails and the Shuangliu waterfall). Firefly/butterfly season windows are official ecology notes but no bindable per-window data source - honestly no time-window contract; disjoint from tw-155 Xuhai grassland 7.33 km away.",
    desc_ja="双流国家森林遊楽区（林業保育署屏東分署公式、白榕・帽子山步道と双流瀑布）（OSM）。蛍・蝶の季節窓は権威源がなく誠実に不構築。旭海とは題材が別。"),
  ]),
 dict(place_id="tw-220", region="tw", slug="baqi-lookout", score=None,
  names={"zh-TW": "芭崎瞭望台", "en": "Baqi highway lookout (Fengbin)",
         "ja": "芭崎展望台", "local": "芭崎"},
  lat=23.7311094, lon=121.5585614, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 芭崎瞭望台（花蓮豐濱鄉磯崎村台11線31.5k，viewpoint 節點）；海拔查無權威單值誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E8%8A%AD%E5%B4%8E%E7%9E%AD%E6%9C%9B%E5%8F%B0",
                 "https://www.eastcoast-nsa.gov.tw/zh-tw/attractions/detail/161/"],
  admin="花蓮縣", category="本島", tags=["coast"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="芭崎瞭望台磯崎灣與新社海崖層疊展望", en="Baqi lookout over Jiqi bay and Xinshi cliffs", ja="芭崎展望台の磯崎湾の眺め",
    desc_zh="芭崎瞭望台（東部海岸國家風景區官方列名，台11線31.5k 制高點；南眺磯崎海灣、龜吼海岬與新社海崖層疊海岸地景）公路瞭望主體（OSM viewpoint 節點；海拔誠實留空）；與既有 tw-203 大石鼻山步道（3.74km）題材錯位——大石鼻山為登頂步道主體，本點為公路制高瞭望台。",
    desc_en="Baqi lookout (officially listed by the East Coast NSA at the 31.5k mark on Highway 11; the highway's rare high point, looking south over Jiqi bay, the Guihou cape and the stacked Xinshi coast). Disjoint from tw-203 Dashibishan trail 3.74 km away (summit-trail subject vs roadside high lookout subject).",
    desc_ja="芭崎展望台（東部海岸国家風景区公式、台11線31.5kの制高点）（OSM）。大石鼻山歩道とは題材が別。"),
  ]),
 dict(place_id="tw-221", region="tw", slug="baimiwong-fort", score=None,
  names={"zh-TW": "白米甕砲台", "en": "Baimiwong Fort (Keelung)",
         "ja": "白米甕砲台", "local": "白米甕砲台"},
  lat=25.1554686, lon=121.7431337, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 白米甕炮台（基隆中山區太白里光華路37巷，fort 節點）；海拔查無權威單值誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E7%99%BD%E7%B1%B3%E7%94%95%E7%A0%B2%E5%8F%B0",
                 "https://tcmb.culture.tw/zh-tw/detail?indexCode=Culture_Place&id=179151"],
  admin="基隆市", category="本島", tags=["coast", "city"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="白米甕砲台四砲座一字排開與港門展望", en="Baimiwong Fort's four-gun battery and harbour-mouth view", ja="白米甕砲台の砲座と港の眺め",
    desc_zh="白米甕砲台（國家文化記憶庫/基隆市文化局列名市定古蹟，1900-1902 日治海岸型堡壘，四砲座一字排開朝港門；又稱荷蘭城）古蹟主體（OSM fort 節點；海拔誠實留空）；與既有 tw-201 基隆燈塔（0.45km）題材錯位——燈塔為現役航標古蹟主體，本點為砲台堡壘遺構主體。",
    desc_en="Baimiwong Fort (city-designated historic site per the National Culture and Memory Bank/Keelung Cultural Affairs; a 1900-1902 Japanese-era coastal fortress with four gun emplacements lined up facing the harbour mouth, aka 'Holland Castle'). Disjoint from tw-201 Keelung Lighthouse 0.45 km away (active navigation-aid subject vs fortress-ruin subject).",
    desc_ja="白米甕砲台（市定古蹟、1900-1902年の歴代海岸要塞、4砲座）（OSM）。基隆燈塔とは題材が別。"),
  ]),
 dict(place_id="tw-222", region="tw", slug="shimen-sea-arch", score=None,
  names={"zh-TW": "石門洞海蝕拱門", "en": "Shimen Cave sea arch (Shimen)",
         "ja": "石門洞", "local": "石門洞"},
  lat=25.2958668, lon=121.5683810, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 石門洞（新北石門區尖鹿里淡金公路，viewpoint 節點）；海拔查無權威單值誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E7%9F%B3%E9%96%80%E6%B4%9E%20%E7%9F%B3%E9%96%80%E5%8D%80",
                 "https://www.northguan-nsa.gov.tw//user/article.aspx?Lang=1&SNo=04002494"],
  admin="新北市", category="本島", tags=["coast", "geology"],
  subjects=[
   dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="石門洞高約10公尺海蝕拱門與觀景步道", en="Shimen Cave's ~10 m sea arch and shore walkway", ja="石門洞の海食アーチ",
    desc_zh="石門洞（北觀國家風景區官方列名，台2線28.7k；海蝕洞經海浪沖鑿與地殼抬升形成高約10公尺的海蝕拱門，步道與觀景平台）地質主體（OSM viewpoint 節點；海拔誠實留空）；與既有 tw-073 老梅綠石槽（2.44km）與 tw-143 富貴角風稜石（3.21km）題材錯位——綠石槽為石礁藻類主體、風稜石為礫灘風蝕主體，本點為海蝕拱門主體。",
    desc_en="Shimen Cave (officially listed by the North Coast NSAA at the 28.7k mark on Highway 2; waves and uplift carved a sea arch about 10 m tall, with a shore walkway and platforms). Disjoint from tw-073 Laomei green-reef 2.44 km and tw-143 Fuguijiao wind-eroded pebbles 3.21 km away (algae-reef and ventifact subjects vs sea-arch subject).",
    desc_ja="石門洞（北観公式、台2線28.7k、高さ約10mの海食アーチ）（OSM）。老梅や富貴角とは題材が別。"),
  ]),
 dict(place_id="tw-223", region="tw", slug="jinshan-mystery-coast", score=None,
  names={"zh-TW": "金山神秘海岸一線天", "en": "Jinshan Mystery Coast sea-cut shore",
         "ja": "金山の神秘海岸", "local": "神秘海岸"},
  lat=25.2269157, lon=121.6513980, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 神祕海岸（新北金山區豐漁里水尾漁港旁，viewpoint 節點）；海拔查無權威單值誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E7%A5%9E%E7%A7%98%E6%B5%B7%E5%B2%B8",
                 "https://newtaipei.travel/zh-tw/attractions/detail/402908"],
  admin="新北市", category="本島", tags=["coast", "geology"],
  subjects=[
   dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="神秘海岸一線天海蝕洞與嶙峋海蝕礁", en="Mystery Coast tide arch and sea-cut reef shore", ja="神秘海岸の海食洞と礁",
    desc_zh="神秘海岸（新北市觀光旅遊網官方列名，金山區水尾漁港旁；穿過「一線天」海蝕洞抵達的嶙峋海蝕礁海岸，遠望燭台雙嶼；漲潮時海蝕洞無法通行、需查潮汐）地質主體（OSM viewpoint 節點；海拔誠實留空）；與既有 tw-161 中角灣/沙珠灣（2.34km）題材錯位——中角灣為衝浪海灣主體，本點為海蝕洞與礁岩秘境主體。",
    desc_en="Mystery Coast (officially listed by the New Taipei travel portal beside Shuiwei fishing harbour, Jinshan; a jagged wave-cut shore reached through the narrow 'first-light' tide arch, looking out to Yeliu Islets; the arch is impassable at high tide). Disjoint from tw-161 Zhongjiao Bay 2.34 km away (surf-bay subject vs tide-arch reef subject).",
    desc_ja="神秘海岸（新北市公式、水尾漁港のそば、一線天の海食洞）（OSM）。中角湾とは題材が別。"),
  ]),
 dict(place_id="tw-224", region="tw", slug="yinhe-cave-falls", score=None,
  names={"zh-TW": "銀河洞瀑布", "en": "Yinhe Cave waterfall (Xindian)",
         "ja": "銀河洞瀑布", "local": "銀河洞"},
  lat=24.9561706, lon=121.5698330, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 銀河洞（新北新店區北宜路二段，bus_stop 節點對位步道口、瀑布主體沿楣子寮溪上游待現場校準）；海拔牆面沿革 220m 附近但查無權威單值誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E9%8A%80%E6%B2%B3%E6%B4%9E",
                 "https://etour.cwa.gov.tw/scenery_inpage.php?stn_id=3&scn_id=103"],
  admin="新北市", category="本島", tags=["forest", "city"],
  subjects=[
   dict(suffix="P01", template="waterfall", seasonal=None,
    zh="銀河洞飛瀑凌空與嵌壁小廟", en="Yinhe Cave's curtain falls and cliff-wall shrine", ja="銀河洞の滝と洞内の祠",
    desc_zh="銀河洞（氣象署數位導覽列名，新店青潭溪支流楣子寮溪上游；分上下兩段的飛瀑自山腰斷崖直下如銀河、洞內建呂洞賓/觀音小廟、銀河洞越嶺步道穿瀑而過）瀑布主體（OSM bus_stop 節點對位步道口、待現場校準；海拔誠實留空）；與既有 tw-187 貓空樟樹步道（1.94km）題材錯位——樟樹步道為茶園步道主體，本點為斷崖瀑布主體。",
    desc_en="Yinhe Cave (listed by the Central Weather Administration e-tour guide, Xindian; an upper-and-lower curtain of falls dropping from a mid-cliff like a silver river, with a small Luzu/Guanyin shrine built into the cliff wall and the Yinhe cross-ridge trail threading through). Disjoint from tw-187 Maokong camphor-tea steps 1.94 km away (tea-garden trail subject vs cliff-fall subject).",
    desc_ja="銀河洞（気象署公式、新店の断崖に懸かる二段の滝と洞内の祠）（OSMで対位）。猫空とは題材が別。"),
  ]),
 dict(place_id="tw-225", region="tw", slug="dulishan-spiral-trail", score=None,
  names={"zh-TW": "獨立山古道螺旋三迴旋", "en": "Dulishan railway-spiral historic trail (Zhuqi)",
         "ja": "独立山古道の螺旋部", "local": "獨立山步道"},
  lat=23.5370055, lon=120.6077341, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 獨立山步道（嘉義竹崎鄉緞繻村紅南坑，footway 節點）；海拔查無權威單值誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E7%8D%A8%E7%AB%8B%E5%B1%B1%E6%AD%A5%E9%81%93",
                 "https://www.forest.gov.tw/0000327"],
  admin="嘉義縣", category="本島", tags=["mountain", "forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="獨立山古道螺旋鐵道三迴旋與溪谷吊橋展望", en="Dulishan trail's triple railway spiral and creek-valley views", ja="独立山古道の三回り螺旋",
    desc_zh="獨立山古道（林業保育署國家步道官方頁，先民運物古道；日治阿里山鐵路以螺旋式環繞獨立山三週登頂，沿途溪谷、鐵道、隧道與吊橋景觀多變）步道主體（OSM footway 節點；海拔誠實留空）；與既有 tw-202 塘湖古道（2.01km）及 tw-105 太平雲梯／梅山36彎（2.74km）題材錯位——塘湖古道為石階古道主體、梅山36彎為公路髮夾彎主體，本點為鐵道螺旋環繞的國家步道主體。",
    desc_en="Dulishan trail (officially listed as a national trail by the Forestry and Nature Conservation Agency; an old supply trail now spiralled three times by the Alishan Forest Railway around the lone-standing mountain, with creeks, rails, tunnels and a suspension bridge). Disjoint from tw-202 Tanghu stone-steps 2.01 km and tw-105 M36-bend highway viewpoint 2.74 km away (historic-steps and hairpin-highway subjects vs railway-spiral trail subject).",
    desc_ja="独立山古道（林業保育署公式、阿里山林鉄が三回り螺旋で登る国家步道）（OSM）。塘湖古道や梅山36彎とは題材が別。"),
  ]),
 dict(place_id="tw-226", region="tw", slug="lailai-geology", score=None,
  names={"zh-TW": "萊萊海蝕平台魔鬼洗衣板", "en": "Lailai wave-cut platform and volcanic dikes",
         "ja": "萊萊の海食台地", "local": "萊萊海蝕平台"},
  lat=25.0004256, lon=121.9933249, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 萊萊海蝕平台（新北貢寮區福連里卯澳，viewpoint 節點）；海拔查無權威單值誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E8%90%8A%E8%90%8A%E6%B5%B7%E8%9D%95%E5%B9%B3%E5%8F%B0",
                 "https://www.necoast-nsa.gov.tw/Area-Content.aspx?a=155&l=1"],
  admin="新北市", category="本島", tags=["coast", "geology"],
  subjects=[
   dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="萊萊火成岩牆與魔鬼洗衣板線型海蝕平台", en="Lailai dike walls and the devil's-washboard shore", ja="萊萊の岩脈と洗濯板地形",
    desc_zh="萊萊（東北角管理處官方列名，東北角海蝕平台最發達地區；大桶山層砂頁岩互層中熔岩侵入形成壁狀火山岩脈，與海蝕溝、「魔鬼洗衣板」幾何線形平台；北側面向東方日出是晨拍熱點，冬季風浪大需注意安全）地質主體（OSM viewpoint 節點；海拔誠實留空）；與既有 tw-102 三貂角燈塔（1.06km）題材錯位——燈塔為極東航標主體，本點為岩脈海蝕地質主體。",
    desc_en="Lailai (officially listed by the Northeast Coast NSAA; the area's most developed wave-cut platform, where lava intruded the Tantoshan sandstone-shale layers to leave wall-like volcanic dikes, sea-cut trenches and the geometric 'devil's washboard'; the north platform faces the sunrise - a dawn-photography favourite, heavy winter seas caution). Disjoint from tw-102 Sandiaojiao Lighthouse 1.06 km away (extreme-point navigation-aid subject vs dike-geology subject).",
    desc_ja="萊萊（東北角管理処公式、岩脈の壁と洗濯板状の海食台地）（OSM）。三貂角燈塔とは題材が別。"),
  ]),
 dict(place_id="tw-227", region="tw", slug="mingfeng-trail", score=None,
  names={"zh-TW": "鳴鳳古道", "en": "Mingfeng historic trail (Shitan)",
         "ja": "鳴鳳古道", "local": "鳴鳳古道"},
  lat=24.5450793, lon=120.9109545, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 鳴鳳古道（苗栗獅潭鄉新店村向東牌，footway 節點）；海拔查無權威單值誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E9%B3%B4%E9%B3%B3%E5%8F%A4%E9%81%93",
                 "https://romantichakka.hakka.gov.tw/trail/TrailPage?a=70&id=341"],
  admin="苗栗縣", category="本島", tags=["mountain", "forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="鳴鳳古道賽夏隘道與新店村口展望", en="Mingfeng trail's Saisiyat-era path and Shitan outlook", ja="鳴鳳古道の展望",
    desc_zh="鳴鳳古道（客家委員會客庄小旅行列名台灣百大古道，橫跨獅潭鄉新店村與頭屋鄉鳴鳳村；原賽夏族狩獵山路、後為粵籍隘墾民貨運要道，今為熱門健行與春季賞桐路線；賞桐季窗為官方生態資訊但查無可繫結的逐窗契約資料源，誠實不建時間窗）古道主體（OSM footway 節點；海拔誠實留空）；與既有 tw-127 仙山靈洞宮後山（4.01km）題材錯位。",
    desc_en="Mingfeng trail (listed by the Hakka Affairs Council's Hakka-village portal among Taiwan's 100 great trails; crossing Shitan and Touwu townships, an old Saisiyat hunting path turned cargo route, now a popular hike and spring tung-blossom route). Tung windows are official ecology notes but no bindable per-window data source - honestly no time-window contract; disjoint from tw-127 Xianshan Lingdong temple back-hill 4.01 km away.",
    desc_ja="鳴鳳古道（客家委員会公式、台湾百大古道、獅潭と頭屋を跨ぐ）（OSM）。油桐の季節窓は権威源がなく誠実に不構築。仙山とは題材が別。"),
  ]),
]

# manifest-row name -> admitted id
ADM_TIER_A_NAMES = {
    "石雨傘海蝕岩柱": "tw-217", "福壽山農場千櫻園": "tw-218", "雙流森林遊樂區": "tw-219",
    "芭崎海蝕崖": "tw-220", "白米甕砲台海蝕岩": "tw-221", "石門洞海蝕拱門": "tw-222",
    "金山神秘海岸海蝕礁": "tw-223", "銀河洞瀑布": "tw-224", "獨立山古道第三迴旋": "tw-225",
    "萊萊海蝕平台魔鬼洗衣板": "tw-226", "鳴鳳古道": "tw-227",
}
assert set(ADM_TIER_A_NAMES.values()) == {f"tw-{n}" for n in range(217, 228)}
assert {p["place_id"] for p in PLACES} == set(ADM_TIER_A_NAMES.values())

DIFF_OVERRIDES = {
    "tw-221": ("tw-201", "基隆燈塔",
        "subject-disjoint: Baimiwong Fort fortress-ruin subject (1900-1902 coastal battery, city-designated historic site) vs Keelung Lighthouse active navigation-aid historic subject - 0.45km apart on the same cape, disjoint subjects"),
    "tw-222": ("tw-073", "老梅綠石槽",
        "subject-disjoint: Shimen Cave sea-arch geology (uplifted arch) vs Laomei green algae-reef subject - 2.44km apart, disjoint subjects"),
    "tw-223": ("tw-161", "中角灣/沙珠灣",
        "subject-disjoint: Mystery Coast tide-arch and wave-cut reef shore vs Zhongjiao surf-bay beach subject - 2.34km apart, disjoint subjects"),
    "tw-224": ("tw-187", "貓空樟樹步道",
        "subject-disjoint: Yinhe Cave cliff waterfall with in-wall shrine vs Maokong camphor tea-garden trail subject - 1.94km apart, disjoint subjects"),
    "tw-225": ("tw-202", "塘湖古道",
        "subject-disjoint: Dulishan national trail with Alishan-railway triple spiral vs Tanghu historic stone-steps trail subject - 2.01km apart, disjoint subjects"),
    "tw-226": ("tw-102", "三貂角燈塔",
        "subject-disjoint: Lailai volcanic-dike wave-cut platform geology vs Sandiaojiao extreme-point lighthouse subject - 1.06km apart, disjoint subjects"),
    "tw-227": ("tw-127", "仙山靈洞宮後山",
        "subject-disjoint: Mingfeng historic trail (Saisiyat-era pass, Shitan) vs Xianshan temple back-hill subject - 4.01km apart, disjoint subjects"),
    "tw-220": ("tw-203", "大石鼻山步道",
        "subject-disjoint: Baqi roadside high lookout subject vs Dashibishan summit-trail subject - 3.74km apart, disjoint subjects"),
}

REJECTED_PLACES = [
    ("石雨傘海蝕岩柱", "admitted as tw-217"),
    ("福壽山農場千櫻園", "admitted as tw-218"),
    ("雙流森林遊樂區", "admitted as tw-219"),
    ("芭崎海蝕崖", "admitted as tw-220"),
    ("白米甕砲台海蝕岩", "admitted as tw-221"),
    ("石門洞海蝕拱門", "admitted as tw-222"),
    ("金山神秘海岸海蝕礁", "admitted as tw-223"),
    ("銀河洞瀑布", "admitted as tw-224"),
    ("獨立山古道第三迴旋", "admitted as tw-225"),
    ("萊萊海蝕平台魔鬼洗衣板", "admitted as tw-226"),
    ("鳴鳳古道", "admitted as tw-227"),
    ("獅山古道", "identical existing subject: 1.97km from existing tw-170 峨眉獅山古道/六寮古道 - the same 獅山古道 system already merged in wave 4"),
    ("石梯坪壺穴平台", "identical existing subject: 0.91km from existing tw-077 石梯坪海蝕平台／壺穴群 - the same 石梯坪 platform/pothole subject"),
    ("石門山日出觀景點", "honest reject: identity/coordinate unverifiable - OSM yields no 石門山 node in 花蓮秀林 and no authoritative source for this specific sunrise viewpoint"),
    ("福壽山農場松廬", "family-cluster row: same 福壽山農場 attraction family as the admitted tw-218 千櫻園 row and existing tw-093 農場觀景點, not separately admitted"),
    ("空ㄟ農場/跑馬古道", "owner minor-spot exclusion: 空ㄟ農場 is a private café/farm business on 跑馬古道 (OSM amenity=cafe), analogous to the homestay exclusion class"),
    ("綠島牛頭山海蝕崖", "5km dedupe reject: 4.82km from existing tw-080 帆船鼻大草原／海岬 - same 綠島 cape/headland family, not subject-disjoint"),
    ("翠峰湖環山步道日出平台", "identical existing subject: 0.78km from existing tw-088 翠峰湖環山步道觀景點 - the same 環山步道 viewpoint family"),
    ("能高越嶺古道天池山莊", "identical existing subject: 0.03km from existing tw-181 能高天池山莊 (wave 5) - the same trail-station subject"),
    ("若茵農場中坑路觀景點", "owner minor-spot exclusion: private 若茵農場 homestay/farm viewpoint (OSM hotel node), analogous to the 恩愛農場 wave-6 exclusion"),
    ("若茵農場高點", "owner minor-spot exclusion: same private 若茵農場 as the sibling row (dup)"),
    ("草嶺古道", "identical existing subject family: 2.3km from existing tw-099 桃源谷（灣坑頭山草原） - 灣坑頭山 is on the 草嶺古道 ridge line, the same trail subject"),
    ("觀霧國家森林遊樂區榛山步道", "identical existing subject: 1.55km from existing tw-089 觀霧榛山步道觀景點 - the same 榛山步道 subject"),
    ("象鼻岩海蝕拱門", "honest reject: the 象鼻岩 sea arch (海蝕拱門) collapsed in 2023-12 - the list's sea-arch subject no longer exists and the remaining rock cannot carry that subject"),
    ("頭城農場/藏酒酒莊", "owner minor-spot exclusion: private 頭城農場/藏酒酒莊 homestay/farm business class, analogous to the homestay exclusion"),
    ("龍潭客家文化館/三坑古道", "honest reject: 龍潭客家文化館 is an indoor museum (not a photography subject) and the 三坑古道 row has no authoritative coordinate source; OSM yields no match"),
    ("龍磐公園星空", "identical existing subject: 0.17km from existing tw-076 龍磐公園／草原海岸 - the same 龍磐 subject already carries night-sky"),
]

REJECT_TIER_A_NAMES = [
    "獅山古道", "石梯坪壺穴平台", "石門山日出觀景點", "福壽山農場松廬",
    "空ㄟ農場/跑馬古道", "綠島牛頭山海蝕崖", "翠峰湖環山步道日出平台",
    "能高越嶺古道天池山莊", "若茵農場中坑路觀景點", "若茵農場高點",
    "草嶺古道", "觀霧國家森林遊樂區榛山步道", "象鼻岩海蝕拱門",
    "頭城農場/藏酒酒莊", "龍潭客家文化館/三坑古道", "龍磐公園星空",
]
REJECT_REASONS = {n: r for n, r in REJECTED_PLACES if n in REJECT_TIER_A_NAMES}
assert len(REJECT_REASONS) == 16, len(REJECT_REASONS)
assert len(REJECTED_PLACES) == 27


def wb(p, text): return m64.wb(p, text)


def _build_contract(p, subj):
    """Copy of the wave-6 contract builder; module globals resolve to wave-7."""
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
    existing = R.get_spots("tw")  # includes tw-125..tw-216
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

    # ---- 2) regions.py (insert AFTER the wave-6 block, before admin map) ----
    rp = ROOT / "regions.py"
    text = rp.read_bytes().decode("utf-8").replace("\r\n", "\n")
    if '"tw-217"' not in text:
        a_tw = '            (23.5625548, 119.4690827, "漁翁島燈塔", "Yuwingdao (Xiyu) Lighthouse, Penghu", "漁翁島灯台", "漁翁島燈塔", "離島", ["coast"]),  # CL-DATA-66\n'
        assert a_tw in text, "wave-6 last tuple anchor missing"
        lines = []
        for p in PLACES:
            n = p["names"]
            lines.append(
                f'            ({p["lat"]}, {p["lon"]}, "{n["zh-TW"]}", "{n["en"]}", '
                f'"{n["ja"]}", "{n["local"]}", "{p["category"]}", {json.dumps(p["tags"], ensure_ascii=False)}),  # {TICKET}\n')
        text = text.replace(a_tw, a_tw + "".join(lines), 1)
        a_admin = '    "tw-216": ["澎湖縣"],  # CL-DATA-66\n'
        assert a_admin in text, "admin anchor missing"
        adm = "".join(f'    "{p["place_id"]}": ["{p["admin"]}"],  # {TICKET}\n' for p in PLACES)
        text = text.replace(a_admin, a_admin + adm, 1)
        a_elev = '    # CL-DATA-66 wave-6 admission elevations (web-verified 2026-11-12; null elevations omitted honestly)\n'
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

    # ---- 5) web evidence registry (extend wave-6 file) ----
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
                        f"untouched; score fields left empty. 11 places admitted (tw-217..tw-227), 16 "
                        "manifest-residual candidates rejected (5 identical existing subjects 0.03-2.3km (獅山古道/石梯坪壺穴/翠峰湖日出平台/能高天池山莊/觀霧榛山步道) + "
                        "1 identical-family trail row (草嶺古道 vs tw-099 灣坑頭山) + 1 same-island cape family <5km (綠島牛頭山 vs tw-080) + "
                        "1 collapsed-subject reject (象鼻岩海蝕拱門 2023-12 崩塌) + 2 family-cluster rows (福壽山松廬/龍磐公園星空) + "
                        "4 private-business exclusions (空ㄟ農場/若茵農場×2/頭城農場) + 1 indoor-museum/unverifiable reject (龍潭客家文化館) + "
                        "1 unverifiable identity (石門山日出觀景點)); 8 sub-5km admissions carry documented subject-disjoint overrides.")
    wb(ev_path, cl.jdump(ev))
    print("web evidence extended:", len(wave_places))

    # ---- 6) tier-a manifest wave-7 status update ----
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
    assert changed == 27, changed
    tm[f"wave{WAVE}"] = {"planned": 27, "order": "n_topics desc, n_lists desc",
                         "done": len(PLACES), "rejected": len(REJECT_TIER_A_NAMES),
                         "place_ids": [p["place_id"] for p in PLACES],
                         "rejected_names": REJECT_TIER_A_NAMES}
    wb(tm_path, cl.jdump(tm))
    print("tier-a manifest updated: changed", changed, "admitted", len(PLACES), "rejected", len(REJECT_TIER_A_NAMES))
    print("DONE wave-7 stage-1 build")


if __name__ == "__main__":
    main()
