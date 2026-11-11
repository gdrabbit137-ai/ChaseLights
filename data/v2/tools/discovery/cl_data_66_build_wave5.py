#!/usr/bin/env python3
"""CL-DATA-66 Wave 5: scoreless intake of 17 Tier-A places (tw-184..tw-200)
from the manifest-next-30 (indices 120..149). 13 of the 30 candidates rejected
(1 identical/0.08km existing + 2 same-family <5km existing + 2 same-family
<5km among more-distant rows (關刀山/馬崙山 大雪山&薑麻園 family clusters) + 1
出風鼻 family row + 2 unverifiable identities + 1 private farm row + 1
private lingzhi farm (minor-spot) + 1 restricted-access islet + 1 private
night-view farm (公老坪/若茵) + 1 identical 0.26km existing 六寮古道...
see REJECTED_PLACES for the honest per-row reasons).

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

# red_maple seasonal id exists in seasonal-calendar but not in the cl helper maps
# (same registration the wave-1 build performs at import time).
cl.TYPICAL_WINDOWS["red_maple"] = {"start": "10-20", "end": "11-10"}
cl.SEASON_NAMES["red_maple"] = {"zh-TW": "紅葉", "en": "Autumn maple", "ja": "紅葉"}
cl.SEASONAL_SOURCES["red_maple"] = (
    "https://www.weathernews.jp/koyo/",
    "季節窗沿用 seasonal-calendar 既有 red_maple 條目（10-20..11-10；ウェザーニュース紅葉リポート）")

TICKET = "CL-DATA-66"
VER_DATE = "2026-11-11"
WAVE = 5

PLACES = [
 dict(place_id="tw-184", region="tw", slug="lianhuchi-center", score=None,
  names={"zh-TW": "蓮華池研究中心", "en": "Lianhuachi Research Center (Yuchi)",
         "ja": "蓮華池研究中心", "local": "蓮華池研究中心"},
  lat=23.9296754, lon=120.8978683, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 蓮華池（南投魚池五城村，pond 節點，林業試驗所蓮華池研究中心範圍）；海拔為 600-800m 區間帶，誠實不取單值、altitude_m 留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E8%93%AE%E8%8F%AF%E6%B1%A0%20%E9%AD%9A%E6%B1%A0",
                 "https://www.sunmoonlake.gov.tw/zh-tw/Attractions/Attractions?A=20&Id=98&P=5"],
  admin="南投縣", category="本島", tags=["forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="蓮華池森林與池塘景觀", en="Lianhuachi forest-and-pond landscape", ja="蓮華池の森と池",
    desc_zh="林業試驗所蓮華池研究中心（日月潭國家風景區官方列名）的天然闊葉林與池塘景觀（OSM pond 節點）；清單主題的螢火蟲/油桐花季窗查無本站可繫結的權威季節資料源，誠實不建時間窗契約——本契約為森林池塘主體；與既有 tw-020 金龍山（3.45km）題材錯位——金龍山為日出雲海展望平台。",
    desc_en="Forest-and-pond landscape inside the Taiwan Forestry Research Institute's Lianhuachi Research Center (listed by the Sun-Moon Lake NSA official site; OSM pond node). The list's firefly/tung-blossom windows have no authoritative seasonal source we can bind, so no time-window contract is built - honestly. Disjoint from tw-020 Jinlongshan's sunrise/cloud-sea lookout 3.45 km away.",
    desc_ja="林業試驗所蓮華池研究中心（日月潭国家風景区公式掲載）の林と池（OSM）。蛍・油桐の季節窓は権威源がなく誠実に不構築。金龍山とは題材が別。"),
  ]),
 dict(place_id="tw-185", region="tw", slug="caota-sand-dune", score=None,
  names={"zh-TW": "觀音草漯沙丘", "en": "Caota sand dunes (Guanyin, Taoyuan)",
         "ja": "草漯砂丘（観音）", "local": "草漯沙丘"},
  lat=25.0742030, lon=121.1292800, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 草漯沙丘（桃園觀音草漯里，beach 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E8%8D%89%E6%BC%B2%E6%B2%99%E4%B8%98",
                 "https://www.forest.gov.tw/0008127"],
  admin="桃園市", category="本島", tags=["coast", "geology"],
  subjects=[
   dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="草漯沙丘地形帶", en="Caota dune landform belt", ja="草漯砂丘の地形",
    desc_zh="觀音草漯沙丘（林業及自然保育署草漯沙丘地質公園官方列名）濱海沙丘地形帶（OSM beach 節點；海拔誠實留空）；清單主題的 beach（泳灘）語義不符——沙丘為地質地景非泳灘，誠實以地質主體登記；與同波 tw-186 許厝港濕地（4.3km）題材錯位——本點為沙丘地質，許厝港為濕地夕照。",
    desc_en="The Caota sand-dune belt on the Guanyin coast (officially listed as the Caota Dune Geopark by the Forestry and Nature Conservation Agency; OSM beach node) - a dune-geology subject, not a swimming beach (the list's 'beach' wording doesn't fit - honestly registered as geology); disjoint from wave-sibling tw-186 Xucuogang wetland-sunset subject 4.3 km away.",
    desc_ja="観音の草漯砂丘（林業保育署の地質公園公式）。遊泳ビーチではなく砂丘地形が主題。同波の許厝港とは題材が別。"),
  ]),
 dict(place_id="tw-186", region="tw", slug="xucuogang-wetland", score=None,
  names={"zh-TW": "許厝港濕地", "en": "Xucuogang wetland (Dayuan, Taoyuan)",
         "ja": "許厝港湿地", "local": "許厝港濕地"},
  lat=25.0860866, lon=121.1749149, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 許厝港濕地（桃園大園內海里，wetland 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E8%A8%B1%E5%8E%9D%E6%B8%AF%E6%BF%95%E5%9C%B0",
                 "https://www.taiwan.nps.gov.tw/home/zh-tw/wetlands/21741.html"],
  admin="桃園市", category="本島", tags=["coast"],
  subjects=[
   dict(suffix="P01", template="sunset", seasonal=None,
    zh="許厝港濕地夕照與候鳥", en="Xucuogang wetland sunset and shorebirds", ja="許厝港湿地の夕日と渡り鳥",
    desc_zh="許厝港國家級重要濕地（內政部國家公園署濕地官方頁）濱海泥灘夕照與候鳥棲地（OSM wetland 節點；海拔誠實留空）；方位暫以 generic 西向 tolerance 85 註冊，待現場校準；與同波 tw-185 草漯沙丘（4.3km）題材錯位——本點為濕地夕照主體。",
    desc_en="Sunset over the tidal flats and shorebird habitat of Xucuogang, a nationally listed important wetland (National Park Service wetland page; OSM wetland node); generic west sector, tolerance 85, pending field calibration; disjoint from wave-sibling tw-185 dune-geology subject 4.3 km away.",
    desc_ja="国家級重要湿地の許厝港（内政部公式）の干潟夕景と渡り鳥（OSM）。方位は暫定の西向き。草漯砂丘とは題材が別。"),
  ]),
 dict(place_id="tw-187", region="tw", slug="maokong-zhangshu-trail", score=None,
  names={"zh-TW": "貓空樟樹步道", "en": "Maokong Zhangshu (camphor) trail",
         "ja": "猫空・樟樹歩道", "local": "貓空樟樹步道"},
  lat=24.9672938, lon=121.5846918, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 樟樹步道（台北文山指南里，footway 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E6%A8%9F%E6%A8%B9%E6%AD%A5%E9%81%93%20%E8%B2%93%E7%A9%BA",
                 "https://www.travel.taipei/zh-tw/news/details/65059"],
  admin="台北市", category="本島", tags=["mountain", "city"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="貓空樟樹步道茶園景觀", en="Maokong camphor-trail tea-terrace landscape", ja="猫空・樟樹歩道の茶園",
    desc_zh="貓空樟樹步道沿線茶園與台北南郊丘陵景觀（台北旅遊網官方貓空農村小旅行；OSM footway 節點；海拔誠實留空）；清單主題的油桐花/菊花季窗查無本站可繫結的權威季節資料源，誠實不建時間窗契約——本契約為茶園步道主體；與既有 tw-132 二格山觀景台（3.52km）題材錯位——本點為茶園步道景觀。",
    desc_en="Tea terraces and southern-Taipei hillside views along the Maokong Zhangshu trail (Taipei travel official Maokong farm-village page; OSM footway node). The list's tung-blossom/chrysanthemum windows have no authoritative seasonal source we can bind, so no time-window contract - honestly. Disjoint from tw-132 Ergeshan's basin night-view platform 3.52 km away.",
    desc_ja="猫空・樟樹歩道沿いの茶園と台北南郊の丘（台北旅遊網公式）。油桐・菊の季節窓は権威源がなく誠実に不構築。二格山とは題材が別。"),
  ]),
 dict(place_id="tw-188", region="tw", slug="maobitou-reef", score=None,
  names={"zh-TW": "貓鼻頭裙礁/貓岩", "en": "Maobitou fringing reef and cat-rock cape",
         "ja": "猫鼻頭の裙礁と猫岩", "local": "貓鼻頭裙礁"},
  lat=21.9206026, lon=120.7387692, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 貓鼻頭（屏東恆春水泉里，cape 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E8%B2%93%E9%BC%BB%E9%A0%AD",
                 "https://www.taiwan.nps.gov.tw/home/zh-tw/quarterly/7971/7525.html"],
  admin="屏東縣", category="本島", tags=["coast", "geology"],
  subjects=[
   dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="貓鼻頭裙礁與貓岩岬角", en="Maobitou fringing reef and cat-shaped cape", ja="猫鼻頭の裙礁と岬",
    desc_zh="貓鼻頭（墾丁國家公園官方列名，台灣海峽與巴士海峽分界岬角）裙礁海岸與貓岩巨岩地形（OSM cape 節點；海拔誠實留空）；與既有 tw-030 屏東關山（5.31km）題材錯位——本點為裙礁岬角地質主體。",
    desc_en="Fringing-reef shore and the cat-shaped monolith at Maobitou, the cape dividing the Taiwan Strait from the Bashi Channel (Kenting National Park official; OSM cape node); disjoint from tw-030 Guanshan's sunset-hill subject 5.31 km away.",
    desc_ja="台湾海峡とバシー海峡を分ける猫鼻頭（墾丁国家公园公式）の裙礁と猫岩（OSM）。関山とは題材が別。"),
   dict(suffix="P02", template="sunset", seasonal=None,
    zh="貓鼻頭岬角夕照", en="Maobitou cape sunset", ja="猫鼻頭の夕日",
    desc_zh="岬角觀景平台向西台灣海峽夕照（與同點地質契約分列）；方位暫以 generic 西向 tolerance 85 註冊，待現場校準。",
    desc_en="West-facing sunset over the Taiwan Strait from the cape lookout (separate from the P01 geology contract); generic west sector, tolerance 85, pending field calibration.",
    desc_ja="岬の展望台から台湾海峡の夕日（P01 とは別契約）。方位は暫定の西向き。"),
  ]),
 dict(place_id="tw-189", region="tw", slug="jundalin-32k", score=None,
  names={"zh-TW": "郡大林道32K望洋點", "en": "Junda forest-road 32K overlook (Xinyi)",
         "ja": "郡大林道32Kの展望点", "local": "郡大林道32K望洋點"},
  lat=23.5954151, lon=120.9712389, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 郡大林道（南投信義豐丘村，track 節點；32K望洋點實址沿林道再上，座標以林道節點對位、待現場校準）；清單海拔 3265m 為郡大山三角點之值、非本望洋點，誠實不取、altitude_m 留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E9%83%A1%E5%A4%A7%E6%9E%97%E9%81%93",
                 "https://www.samejantravel.tw/place/24fb67b2-847a-4f4d-a767-e0958bfc1c85"],
  admin="南投縣", category="本島", tags=["mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="cloud_sea", seasonal=None,
    zh="郡大林道望洋點雲海", en="Cloud sea from the Junda-road overlook", ja="郡大林道展望点の雲海",
    desc_zh="郡大林道高處望洋點的雲海與玉山群峰/西巒大山方向展望（行記列名；OSM 林道 track 節點對位、實址沿林道再上待現場校準；海拔誠實留空）；與既有 tw-182 望高寮瞭望台（8.8km）題材錯位——本點為林道高點雲海主體。",
    desc_en="Cloud sea and Yushan-massif / Xiluanshan outlooks from the high Junda forest-road overlook (travel write-ups; OSM forest-road track node as proxy - the viewpoint sits farther up the road, pending field calibration); disjoint from tw-182 Wanggaoliao watchtower 8.8 km away.",
    desc_ja="郡大林道の高点からの雲海と玉山連峰の展望（OSMの林道ノートで対位、現地校正待ち）。望高寮とは題材が別。"),
  ]),
 dict(place_id="tw-190", region="tw", slug="dulanji-cliff", score=None,
  names={"zh-TW": "都蘭鼻海蝕崖", "en": "Dulanji sea cliff and reef flat", "ja": "都蘭鼻の海蝕崖",
         "local": "都蘭鼻"},
  lat=22.8655356, lon=121.2315214, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 都蘭鼻（台東東河都蘭村，cape 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E9%83%BD%E8%98%AD%E9%BC%BB",
                 "https://www.eastcoast-nsa.gov.tw/zh-tw/attractions/detail/34/"],
  admin="台東縣", category="本島", tags=["coast", "geology"],
  subjects=[
   dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="都蘭鼻海蝕平台與礁岩海岸", en="Dulanji wave-cut platform and reef shore", ja="都蘭鼻の波食台と礁岩海岸",
    desc_zh="都蘭鼻（東部海岸國家風景區官方都蘭頁；阿美族傳統聖地）海蝕平台與礁岩海岸地形（OSM cape 節點；海拔誠實留空）；拍攝請尊重部落祭儀與現場公告——access 記錄；與既有 tw-090 加路蘭海岸遊憩區（10.1km）題材錯位——本點為海蝕地質主體。",
    desc_en="Wave-cut platform and reef shore at Dulanji (East Coast NSA official Dulan page; an Amis traditional sacred site; OSM cape node) - respect tribal ceremonies and on-site notices (access note); disjoint from tw-090 Jialulan recreation area's subject 10.1 km away.",
    desc_ja="都蘭鼻（東部海岸国家風景区公式・アミ族の聖地）の波食台と礁岩海岸（OSM）。祭儀と現地の案内を尊重。加路蘭とは題材が別。"),
  ]),
 dict(place_id="tw-191", region="tw", slug="tiezhenshan-platform", score=None,
  names={"zh-TW": "鐵砧山碉堡平台", "en": "Tiezhanshan fort-platform overlook (Dajia)",
         "ja": "鉄砧山の砲台展望台", "local": "鐵砧山"},
  lat=24.3597572, lon=120.6510659, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 鐵砧山小百岳認證點（台中大甲頂店里，checkpoint 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E9%90%B5%E7%A0%A7%E5%B1%B1%20%E5%A4%A7%E7%94%B2",
                 "https://zh.wikipedia.org/zh-tw/%E9%90%B5%E7%A0%A7%E5%B1%B1"],
  admin="台中市", category="本島", tags=["mountain", "city"],
  subjects=[
   dict(suffix="P01", template="city_night", seasonal=None,
    zh="鐵砧山碉堡平台夜景", en="Night view from the Tiezhanshan fort platform", ja="鉄砧山の夜景",
    desc_zh="鐵砧山（zh.wikipedia 小百岳；舊碉堡/劍井史蹟區）展望平台俯瞰大甲與海線聚落夜燈（OSM checkpoint 節點；海拔誠實留空）；與既有 tw-013 火炎山（7.9km）題材錯位——本點為海線夜景主體。",
    desc_en="Night lights of Dajia and the coastal towns from the Tiezhanshan overlook (small-hundred-peaks hill; old battery historic area; zh.wikipedia; OSM checkpoint node); disjoint from tw-013 Huoyanshan's badland ridge 7.9 km away.",
    desc_ja="鉄砧山（zh.wikipedia、小百岳）の展望台から大甲と海線の灯り（OSM）。火炎山とは題材が別。"),
   dict(suffix="P02", template="sunset", seasonal=None,
    zh="鐵砧山西向夕照", en="Tiezhanshan west sunset", ja="鉄砧山の夕日",
    desc_zh="平台西向台灣海峽方向夕照（與同點夜景契約分列）；方位暫以 generic 西向 tolerance 85 註冊，待現場校準。",
    desc_en="West-facing sunset toward the Taiwan Strait from the same platform (separate from the P01 night contract); generic west sector, tolerance 85, pending field calibration.",
    desc_ja="同じ展望台から台湾海峡側の夕日（P01 とは別契約）。方位は暫定の西向き。"),
  ]),
 dict(place_id="tw-192", region="tw", slug="wushibi-changbin", score=None,
  names={"zh-TW": "長濱烏石鼻柱狀火山岩", "en": "Wushibi columnar volcanic rocks (Changbin)",
         "ja": "長浜・烏石鼻の柱状火山岩", "local": "烏石鼻"},
  lat=23.2269268, lon=121.4186000, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 烏石鼻（台東長濱寧埔村，cape 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E7%83%8F%E7%9F%B3%E9%BC%BB%20%E9%95%B7%E6%BF%B1",
                 "https://www.eastcoast-nsa.gov.tw/zh-tw/attractions/detail/38/"],
  admin="台東縣", category="本島", tags=["coast", "geology"],
  subjects=[
   dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="烏石鼻柱狀火山岩岬角", en="Wushibi columnar-ventifact cape", ja="烏石鼻の柱状岩の岬",
    desc_zh="烏石鼻（東部海岸國家風景區官方列名）向海延伸的柱狀火山岩岬角與潮池（OSM cape 節點；海拔誠實留空）；清單主題的 lighthouse 語義不符——本岬無燈塔主體，誠實以地質主體登記；與既有 tw-035 六十石山（10.4km）題材錯位。",
    desc_en="The columnar volcanic-rock cape and tide pools of Wushibi (East Coast NSA official listing; OSM cape node). The list's 'lighthouse' topic doesn't fit - no lighthouse subject here - honestly registered as geology; disjoint from tw-035 Liushishi Mountain 10.4 km away.",
    desc_ja="烏石鼻（東部海岸国家風景区公式）の柱状火山岩の岬と潮溜まり（OSM）。灯台の語義と合わないため地質主体で登録。六十石山とは題材が別。"),
  ]),
 dict(place_id="tw-193", region="tw", slug="azhaowu-shan", score=None,
  names={"zh-TW": "阿罩霧山", "en": "Azhaowushan (Wufeng, Taichung)", "ja": "阿罩霧山",
         "local": "阿罩霧山"},
  lat=24.0612506, lon=120.7135114, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 阿罩霧山（台中霧峰萊園里仁德巷，checkpoint 節點，小百岳登頂認證點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E9%98%BF%E7%BD%A9%E9%9C%A7%E5%B1%B1",
                 "https://www.peakstw.com/mountain/small_046"],
  admin="台中市", category="本島", tags=["mountain", "city"],
  subjects=[
   dict(suffix="P01", template="city_night", seasonal=None,
    zh="阿罩霧山霧峰夜景", en="Night over Wufeng from Azhaowushan", ja="阿罩霧山の霧峰の夜景",
    desc_zh="阿罩霧山（小百岳；登頂點近霧峰市街）俯瞰霧峰與台中盆地南緣夜燈（OSM checkpoint 節點＋小百岳攻略頁；海拔誠實留空）；與既有 tw-150 九天夕陽之樹（16.6km）等點題材錯位——本點為霧峰市街夜景主體。",
    desc_en="Wufeng town and the southern Taipei-basin edge lights from Azhaowushan (small-hundred-peaks hill; OSM checkpoint node; elevation honestly left empty); disjoint from tw-150 and other Taichung subjects.",
    desc_ja="阿罩霧山（小百岳）から霧峰と台中盆地南縁の灯り（OSM）。標高は未確認のため空欄。"),
   dict(suffix="P02", template="sunrise", seasonal=None,
    zh="阿罩霧山晨景", en="Azhaowushan dawn", ja="阿罩霧山の朝",
    desc_zh="步道晨間展望（與同點夜景契約分列）；清單主題的日出方位查無本站權威資料源，誠實不註冊方向窗——本契約為晨景主體。",
    desc_en="Morning outlook from the trail (separate from the P01 night contract); the list's sunrise topic has no authoritative azimuth source for this site - honestly no directional window registered.",
    desc_ja="歩道からの朝の展望（P01 とは別契約）。日の出の方位は権威源がなく方向窓は不登録。"),
  ]),
 dict(place_id="tw-194", region="tw", slug="dingtoue-shazhou", score=None,
  names={"zh-TW": "頂頭額沙洲", "en": "Dingtoue sandbar (Qigu, Tainan)", "ja": "頂頭額砂洲",
         "local": "頂頭額沙洲"},
  lat=23.1062397, lon=120.0383364, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 頂頭額汕（台南七股十份里，sand 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E9%A0%82%E9%A0%AD%E9%A1%8D%E6%B1%95",
                 "https://www.swcoast-nsa.gov.tw/zh-tw/attraction/details/1652"],
  admin="台南市", category="本島", tags=["coast"],
  subjects=[
   dict(suffix="P01", template="sunset", seasonal=None,
    zh="頂頭額沙洲與國聖港燈塔夕照", en="Dingtoue sandbar and Guosheng-lighthouse sunset", ja="頂頭額砂洲と国聖港灯台の夕日",
    desc_zh="頂頭額沙洲（雲嘉南濱海國家風景區官方列名）沙洲地景與國聖港燈塔（國聖港燈塔為官方列名景點）向西台灣海峽夕照（OSM sand 節點；海拔誠實留空）；清單主題的 beach（泳灘）語義不符——沙洲為地景非泳灘，誠實以夕照主體登記；方位暫以 generic 西向 tolerance 85 註冊，待現場校準；與既有 tw-109 七股鹽山／潟湖（8.8km）題材錯位。",
    desc_en="Sunset over the Dingtoue sandbar and Guosheng Lighthouse (Southwest Coast NSA official pages; OSM sand node). The list's 'beach' topic doesn't fit - this is a sandbar landform, not a swimming beach - honestly registered as a sunset subject; generic west sector, tolerance 85; disjoint from tw-109 Qigu salt-mountain/lagoon 8.8 km away.",
    desc_ja="頂頭額砂洲と国聖港灯台（雲嘉南風景区公式）の台湾海峡の夕日（OSM）。遊泳ビーチではなく砂洲の夕景で登録。七股塩山とは題材が別。"),
  ]),
 dict(place_id="tw-195", region="tw", slug="feifengshan-guanriting", score=None,
  names={"zh-TW": "飛鳳山觀日亭", "en": "Feifengshan sun-watching pavilion (Qionglin)",
         "ja": "飛鳳山・観日亭", "local": "飛鳳山觀日亭"},
  lat=24.7665291, lon=121.1189650, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 中坑山（新竹芎林，peak 節點；飛鳳山步道最高點/觀日亭所在）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E4%B8%AD%E5%9D%91%E5%B1%B1%20%E8%8A%8E%E6%9E%97",
                 "https://isports.sa.gov.tw/apps/TIS/TIS05/TIS0550M_02V1.aspx?PKNO=27"],
  admin="新竹縣", category="本島", tags=["mountain", "city"],
  subjects=[
   dict(suffix="P01", template="city_night", seasonal=None,
    zh="飛鳳山新竹夜景", en="Hsinchu night view from Feifengshan", ja="飛鳳山の新竹の夜景",
    desc_zh="飛鳳山/中坑山觀日亭俯瞰頭前溪谷與新竹市區夜燈（小百岳官方 iSports 頁；OSM peak 節點；海拔誠實留空）；與既有 tw-160/tw-170（12.6km 外）題材錯位——本點為新竹市區夜景主體。",
    desc_en="Night lights over the Touqian river valley and Hsinchu city from the Feifengshan/Chungkengshan sun-watching pavilion (small-hundred-peaks official iSports page; OSM peak node); disjoint from tw-160/tw-170 subjects 12.6 km away.",
    desc_ja="飛鳳山・中坑山の観日亭から頭前渓谷と新竹市街の灯り（小百岳公式 iSports）。標高は空欄。"),
   dict(suffix="P02", template="sunset", seasonal=None,
    zh="飛鳳夕照", en="Feifeng sunset glow", ja="飛鳳の夕焼け",
    desc_zh="「飛鳳夕照」名景的西向夕照（小百岳列名特色；與同點夜景契約分列）；方位暫以 generic 西向 tolerance 85 註冊，待現場校準。",
    desc_en="The listed 'Feifeng sunset glow' west-facing phenomenon (small-hundred-peaks feature; separate from the P01 night contract); generic west sector, tolerance 85, pending field calibration.",
    desc_ja="「飛鳳夕照」の西向きの夕焼け（小百岳の名物）。P01 とは別契約。方位は暫定の西向き。"),
  ]),
 dict(place_id="tw-196", region="tw", slug="manapan-summit", score=None,
  names={"zh-TW": "馬那邦山頂峰展望", "en": "Manapanshan summit outlook (Dahu/Tai'an)",
         "ja": "馬那邦山の山頂展望", "local": "馬那邦山"},
  lat=24.3672289, lon=120.9138040, elev_m=1407, coord_conf="medium",
  coord_source="OSM Nominatim 馬那邦山（苗栗大湖/泰安，checkpoint 節點，小百岳認證點）；海拔1,407m（清單層資料 zh.wikipedia 馬那邦山）",
  coord_sources=["https://www.openstreetmap.org/search?query=%E9%A6%AC%E9%82%A3%E9%82%A6%E5%B1%B1",
                 "https://zh.wikipedia.org/zh-tw/%E9%A6%AC%E9%82%A3%E9%82%A6%E5%B1%B1"],
  admin="苗栗縣", category="本島", tags=["mountain", "forest"],
  subjects=[
   dict(suffix="P01", template="cloud_sea", seasonal=None,
    zh="馬那邦山雲海", en="Manapanshan cloud sea", ja="馬那邦山の雲海",
    desc_zh="馬那邦山（小百岳，海拔1,407m）山頂秋冬雲海與大霸尖山方向展望（小百岳/行記列名；OSM checkpoint 節點）；與既有 tw-014 雲洞山莊（9.6km）題材錯位——本點為小百岳山頂雲海主體。",
    desc_en="Autumn-winter cloud sea from the 1,407 m Manapanshan summit (small-hundred-peaks hill; OSM checkpoint node); disjoint from tw-014 Yundong Villa's tea-region cloud sea 9.6 km away.",
    desc_ja="標高1407mの馬那邦山（小百岳）山頂の雲海（OSM）。雲洞山荘とは題材が別。"),
   dict(suffix="P02", template="seasonal_plant", seasonal="red_maple",
    zh="馬那邦山楓紅", en="Manapanshan red-maple foliage", ja="馬那邦山の紅葉",
    desc_zh="馬那邦山古道的楓紅季（沿用 seasonal-calendar 既有 red_maple 窗 10-20..11-10；與同點雲海契約分列）。",
    desc_en="Autumn maple color along the Manapanshan historic trail (reuses the existing seasonal-calendar red_maple window 10-20..11-10; separate from the P01 cloud-sea contract).",
    desc_ja="馬那邦山古道の紅葉（red_maple 季節窓を再利用）。P01 とは別契約。"),
  ]),
 dict(place_id="tw-197", region="tw", slug="aofengshan-platform", score=None,
  names={"zh-TW": "鰲峰山觀景平台", "en": "Aofengshan viewing platform (Qingshui)",
         "ja": "鰲峰山の展望台", "local": "鰲峰山觀景平台"},
  lat=24.2711925, lon=120.5815880, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 鰲峰山公園（台中清水，park 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E9%B0%B0%E5%B3%B0%E5%B1%B1%E5%85%AC%E5%9C%92",
                 "https://okgo.tw/butyview.html?id=3653"],
  admin="台中市", category="本島", tags=["mountain", "city"],
  subjects=[
   dict(suffix="P01", template="city_night", seasonal=None,
    zh="鰲峰山海線夜景", en="Coastal-town night view from Aofengshan", ja="鰲峰山から海線の夜景",
    desc_zh="鰲峰山觀景平台俯瞰清水市街、台中港區與海線聚落夜燈（玩全台灣旅遊網列名；OSM park 節點；海拔誠實留空）；與既有 tw-015 高美濕地（5.6km）題材錯位——本點為山頂平台城市夜景，高美為濕地夕照。",
    desc_en="Qingshui town, Taichung-port and coastal-town lights from the Aofengshan platform (okgo listing; OSM park node); disjoint from tw-015 Gaomei wetland's sunset subject 5.6 km away (hilltop city night vs wetland sunset).",
    desc_ja="鰲峰山の展望台から清水・台中港・海線の灯り（OSM）。高美湿地とは題材が別。"),
  ]),
 dict(place_id="tw-198", region="tw", slug="shiyizhi-trail", score=None,
  names={"zh-TW": "十一指古道", "en": "Shiyizhi historic trail (Daxi)", "ja": "十一指古道",
         "local": "十一指古道"},
  lat=24.8421501, lon=121.2786819, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 十一指古道（桃園大溪義和里，path 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E5%8D%81%E4%B8%80%E6%8C%87%E5%8F%A4%E9%81%93",
                 "https://taiwantour.net/11"],
  admin="桃園市", category="本島", tags=["forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="十一指古道森林步道", en="Shiyizhi forest trail", ja="十一指古道の森の道",
    desc_zh="大溪十一指古道（百年石階與百年茄苳，行記列名）森林步道主體（OSM path 節點；海拔誠實留空）；清單主題的油桐花季窗查無本站可繫結的權威季節資料源，誠實不建時間窗契約——本契約為古道森林主體。",
    desc_en="The forested Shiyizhi historic trail with its century-old stone steps and nanmu trees (travel write-ups; OSM path node). The list's tung-blossom window has no authoritative seasonal source we can bind, so no time-window contract - honestly.",
    desc_ja="大渓の十一指古道（石段と老樹）の森の道（OSM）。油桐の季節窓は権威源がなく誠実に不構築。"),
  ]),
 dict(place_id="tw-199", region="tw", slug="liji-badland", score=None,
  names={"zh-TW": "卑南溪/利吉惡地", "en": "Liji badland by the Beinan river (Taitung)",
         "ja": "卑南渓・利吉悪地", "local": "利吉惡地"},
  lat=22.8150524, lon=121.1433470, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 利吉月世界（台東卑南利吉村利吉路，scree 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E5%88%A9%E5%90%89%E6%9C%88%E4%B8%96%E7%95%8C",
                 "https://www.forest.gov.tw/0008143"],
  admin="台東縣", category="本島", tags=["geology"],
  subjects=[
   dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="利吉惡地泥岩地形", en="Liji mudstone badland", ja="利吉悪地の泥岩地形",
    desc_zh="利吉惡地（林業及自然保育署地質公園官方列名，利吉層泥岩惡地形）與卑南溪畔月世界景觀（OSM scree 節點；海拔誠實留空）；清單主題的 miscanthus 芒花季窗查無本站可繫結的權威季節資料源，誠實不建時間窗契約——本契約為惡地地質主體；與既有 tw-090 加路蘭海岸遊憩區（5.2km）題材錯位——本點為內陸泥岩惡地。",
    desc_en="The Liji mudstone badland (officially listed geopark by the Forestry and Nature Conservation Agency; Liji-layer melange terrain) above the Beinan river (OSM scree node). The list's miscanthus window has no authoritative seasonal source we can bind, so no time-window contract - honestly; disjoint from tw-090 Jialulan's coastal subject 5.2 km away (inland mudstone badland vs coastal recreation area).",
    desc_ja="利吉悪地（林業保育署の地質公園公式、利吉層の泥岩悪地形）（OSM）。芒草の季節窓は権威源がなく誠実に不構築。加路蘭とは題材が別。"),
  ]),
 dict(place_id="tw-200", region="tw", slug="nanau-seacave", score=None,
  names={"zh-TW": "南澳海蝕洞", "en": "Nan'ao sea cave (Su'ao-Hualien coast)", "ja": "南澳の海蝕洞",
         "local": "南澳海蝕洞"},
  lat=24.4014567, lon=121.7891201, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 南澳海蝕洞（宜蘭南澳武塔村觀音隧道旁，cave_entrance 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E5%8D%97%E6%BE%B3%E6%B5%B7%E8%9D%95%E6%B4%9E",
                 "https://www.forest.gov.tw/0008013"],
  admin="宜蘭縣", category="本島", tags=["coast", "geology"],
  subjects=[
   dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="南澳神秘海灘海蝕洞", en="Nan'ao mystery-beach sea cave", ja="南澳・神秘海灘の海蝕洞",
    desc_zh="南澳神秘海灘（蘇花古道觀音段濱線）的巨型海蝕洞（OSM cave_entrance 節點＋行記/媒體記錄；位處觀音海岸野生動物重要棲息環境——請依主管機關管制與潮汐安全前往，access 記錄；海拔誠實留空）；與既有 tw-033 粉鳥林（12km）題材錯位。",
    desc_en="The giant sea cave on Nan'ao's 'mystery beach' along the old Su'ao-hualien coastal route (OSM cave-entrance node; travel/media records) inside the Guanyin Coast Wildlife Important Habitat - follow the managing agency's access rules and tide safety (access note); disjoint from tw-033 Feniaolin 12 km away.",
    desc_ja="南澳・神秘海灘の巨大な海蝕洞（OSM）。観音海岸野生動物重要棲息環境内——管理者の規制と潮汐に従う。粉鳥林とは題材が別。"),
  ]),
]

# subject-disjoint overrides for <5km neighbours (CL-DATA-51/64/66 precedent)
DIFF_OVERRIDES = {
    "tw-184": ("tw-020", "金龍山",
        "subject-disjoint: Lianhuachi research-forest pond landscape (forestry research station) vs Jinlongshan sunrise/cloud-sea lookout platform - 3.45km apart, disjoint subjects"),
    "tw-185": ("tw-186", "許厝港濕地",
        "subject-disjoint: Caota dune-geology landform vs Xucuogang wetland sunset/shorebird subject - 4.3km apart (same-wave siblings), disjoint subjects"),
    "tw-186": ("tw-185", "觀音草漯沙丘",
        "subject-disjoint: Xucuogang wetland sunset/shorebird subject vs Caota dune-geology landform - 4.3km apart (same-wave siblings), disjoint subjects"),
    "tw-187": ("tw-132", "石門二格山觀景台",
        "subject-disjoint: Maokong camphor-trail tea-terrace landscape vs Ergeshan Taipei-basin night-view platform - 3.52km apart, disjoint subjects"),
}

# rejected within-5km family overlaps / exclusions: recorded in manifest, NOT admitted
REJECTED_PLACES = [
    ("蓮華池研究中心", "admitted as tw-184"),
    ("虎仔山KEELUNG地標", "5km dedupe reject: 3.45km from existing tw-054 正濱漁港 - same 基隆港 harbor family (hillside KEELUNG-sign harbor night view vs harbor-front fishing port), not subject-disjoint (梧棲漁港 wave-4 precedent)"),
    ("觀音草漯沙丘", "admitted as tw-185"),
    ("許厝港濕地", "admitted as tw-186"),
    ("豆腐岬海蝕平台/珊瑚礁", "5km dedupe reject: 0.95km from existing tw-152 南方澳觀景台 - same 南方澳 coastal family (near-duplicate bay), not subject-disjoint"),
    ("貓空樟樹步道", "admitted as tw-187"),
    ("貓鼻頭裙礁/貓岩", "admitted as tw-188"),
    ("郡大山32K望洋點", "admitted as tw-189"),
    ("都蘭鼻海蝕崖", "admitted as tw-190"),
    ("鐵砧山碉堡平台", "admitted as tw-191"),
    ("長濱烏石鼻柱狀火山岩", "admitted as tw-192"),
    ("關刀山出關步道", "5km dedupe reject: 1.87km from existing tw-014 雲洞山莊 - same 薑麻園/關刀山雲海茶園 family, not subject-disjoint"),
    ("阿罩霧山", "admitted as tw-193"),
    ("雙龍林道高點", "honest reject: identity/coordinate unverifiable - OSM only yields forest-road track nodes for 雙龍林道, no 高點/望洋點 node and no authoritative source for the specific viewpoint"),
    ("雪山東峰哭坡頂", "5km dedupe reject: 4.02km from existing tw-041 雪山主峰 - same 雪山群峰 summit/route family, not subject-disjoint"),
    ("頂頭額沙洲", "admitted as tw-194"),
    ("飛鳳山觀日亭", "admitted as tw-195"),
    ("馬崙山新山遺址", "5km dedupe reject: 1.66km from existing tw-087 大雪山森林遊樂區43K觀景台 - same 大雪山林道 cloud-sea family (tw-087/tw-169 both in catalog), not subject-disjoint"),
    ("馬那邦山頂峰展望", "admitted as tw-196"),
    ("鰲峰山觀景平台", "admitted as tw-197"),
    ("龜山島龜首海蝕洞/海底噴口", "honest reject: restricted-access islet - landing requires permit-managed boat tours, the 龜首 sea cave/sea-vent subject is only viewable from licensed boats; no shore/island-accessible camera context verifiable"),
    ("三才靈芝農場", "owner minor-spot exclusion: private lingzhi/agri farm (石碇), identity not even OSM-locable; analogous to the homestay exclusion"),
    ("三貂角海蝕平台/大姆指岩", "identical existing place: 0.08km from existing tw-102 三貂角燈塔 - same cape subject"),
    ("公老坪/若茵農場", "owner minor-spot exclusion: 若茵農場 is a private night-view 景觀農場 (豐原公老坪), analogous to the homestay/private-restaurant exclusion (社頭極光森林 wave-4 precedent)"),
    ("六寮古道/獅山步道", "identical existing place: 0.26km from existing tw-170 峨眉獅山古道/六寮古道 - same trail subject"),
    ("出風鼻海蝕岩/風吹石", "5km dedupe reject: 4.44km from existing tw-107 佳樂水 - same 恆春東南海岸礁岩 family, not subject-disjoint"),
    ("十一指古道", "admitted as tw-198"),
    ("卑南溪/利吉惡地", "admitted as tw-199"),
    ("南澳海蝕洞", "admitted as tw-200"),
    ("和平海蝕崖", "honest reject: identity/coordinate unverifiable - OSM only resolves the 和平 village/industrial node, no 海蝕崖 feature node and no authoritative source for the specific cliff"),
]

REJECT_TIER_A_NAMES = [
    "虎仔山KEELUNG地標", "豆腐岬海蝕平台/珊瑚礁", "關刀山出關步道", "雙龍林道高點",
    "雪山東峰哭坡頂", "馬崙山新山遺址", "龜山島龜首海蝕洞/海底噴口", "三才靈芝農場",
    "三貂角海蝕平台/大姆指岩", "公老坪/若茵農場", "六寮古道/獅山步道",
    "出風鼻海蝕岩/風吹石", "和平海蝕崖",
]
REJECT_REASONS = {n: r for n, r in REJECTED_PLACES if n in REJECT_TIER_A_NAMES}
assert len(REJECT_REASONS) == 13, len(REJECT_REASONS)
ADM_TIER_A_NAMES = {
    "蓮華池研究中心": "tw-184", "觀音草漯沙丘": "tw-185", "許厝港濕地": "tw-186",
    "貓空樟樹步道": "tw-187", "貓鼻頭裙礁/貓岩": "tw-188", "郡大山32K望洋點": "tw-189",
    "都蘭鼻海蝕崖": "tw-190", "鐵砧山碉堡平台": "tw-191", "長濱烏石鼻柱狀火山岩": "tw-192",
    "阿罩霧山": "tw-193", "頂頭額沙洲": "tw-194", "飛鳳山觀日亭": "tw-195",
    "馬那邦山頂峰展望": "tw-196", "鰲峰山觀景平台": "tw-197", "十一指古道": "tw-198",
    "卑南溪/利吉惡地": "tw-199", "南澳海蝕洞": "tw-200",
}
assert set(ADM_TIER_A_NAMES.values()) == {f"tw-{n}" for n in range(184, 201)}
assert {p["place_id"] for p in PLACES} == set(ADM_TIER_A_NAMES.values())
assert len(REJECTED_PLACES) == 30


def wb(p, text): return m64.wb(p, text)


def _build_contract(p, subj):
    """Copy of the wave-4 contract builder; module globals resolve to wave-5."""
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
    existing = R.get_spots("tw")  # includes tw-125..tw-183
    rows = {}
    for p in PLACES:
        pool = [s for s in existing if s["spot_id"] != p["place_id"]] + [
            {"spot_id": q["place_id"], "lat": q["lat"], "lon": q["lon"],
             "name_i18n": {"zh-TW": q["names"]["zh-TW"]}}
            for q in PLACES if q is not p]
        dists = sorted((hav(p["lat"], p["lon"], s["lat"], s["lon"])/1000, s["spot_id"],
                        s["name_i18n"]["zh-TW"]) for s in pool)
        nearest = dists[0]
        ov_pairs = {(k, v[0]) for k, v in DIFF_OVERRIDES.items()}
        ov = DIFF_OVERRIDES.get(p["place_id"])
        if ov is None and nearest[0] < 5.0 and (nearest[1], p["place_id"]) in ov_pairs:
            v = DIFF_OVERRIDES[nearest[1]]
            ov = (nearest[1], v[1], v[2].replace("vs " + v[1], "vs " + p["names"]["zh-TW"]))
        row = {"nearest_existing": nearest[1], "name": nearest[2], "km": round(nearest[0], 2)}
        if ov:
            row["override"] = ov[2]
            assert (p["place_id"], nearest[1]) in ov_pairs or (nearest[1], p["place_id"]) in ov_pairs, \
                f"{p['place_id']} override {nearest} not documented"
        else:
            assert nearest[0] >= 5.0, f"{p['place_id']} within 5km of {nearest}"
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

    # ---- 2) regions.py ----
    rp = ROOT / "regions.py"
    text = rp.read_bytes().decode("utf-8").replace("\r\n", "\n")
    if '"tw-184"' not in text:
        a_tw = '            (24.6501, 121.4706, "明池森林遊樂區", "Mingchi National Forest Recreation Area", "明池国家森林遊楽区", "明池森林遊樂區", "本島", ["mountain", "forest"]),  # CL-DATA-66\n'
        assert a_tw in text, "tw-173 tuple anchor missing"
        lines = []
        for p in PLACES:
            n = p["names"]
            lines.append(
                f'            ({p["lat"]}, {p["lon"]}, "{n["zh-TW"]}", "{n["en"]}", '
                f'"{n["ja"]}", "{n["local"]}", "{p["category"]}", {json.dumps(p["tags"], ensure_ascii=False)}),  # {TICKET}\n')
        text = text.replace(a_tw, a_tw + "".join(lines), 1)
        a_admin = '    "tw-183": ["新竹縣"],  # CL-DATA-66\n'
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

    # ---- 5) web evidence registry (extend wave-4 file) ----
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
    ev[f"rule_wave{WAVE}"] = (f"Scoreless intake wave {WAVE} (owner ruling {VER_DATE}): admission = web verification + "
                        "5km subject-disjoint dedupe; NO rubric v2 gates, NO AGLI dual-board, agli-final "
                        f"untouched; score fields left empty. 17 places admitted (tw-184..tw-200), 13 "
                        "manifest-next-30 candidates rejected (1 identical 0.08km + 1 identical 0.26km + "
                        "2 same-family <5km existing (虎仔山/出風鼻) + 2 family-cluster rows (關刀山/馬崙山) + "
                        "2 unverifiable identities (雙龍林道高點/和平海蝕崖) + 1 restricted-access islet "
                        "(龜山島) + 2 private-farm exclusions (三才靈芝農場/公老坪若茵農場)).")
    wb(ev_path, cl.jdump(ev))
    print("web evidence extended:", len(wave_places))

    # ---- 6) tier-a manifest wave-5 status update ----
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
    print("DONE wave-5 stage-1 build")


if __name__ == "__main__":
    main()
