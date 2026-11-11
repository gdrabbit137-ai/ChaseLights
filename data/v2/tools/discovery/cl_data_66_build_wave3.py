#!/usr/bin/env python3
"""CL-DATA-66 Wave 3: scoreless intake of 12 Tier-A places (tw-162..tw-173)
from the manifest-next-30 (indices 60..89). 18 of the 30 candidates rejected.

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
    'cl66w2', str(ROOT / 'data/v2/tools/discovery/cl_data_66_build_wave2.py'))
m2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m2)
cl = m2.cl

TICKET = "CL-DATA-66"
VER_DATE = "2026-11-11"
WAVE = 3

PLACES = [
 dict(place_id="tw-162", region="tw", slug="baguashan-skywalk", score=None,
  names={"zh-TW": "八卦山天空步道", "en": "Baguashan skywalk (Changhua)",
         "ja": "八卦山スカイウォーク", "local": "八卦山天空步道"},
  lat=24.0780, lon=120.5535, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 八卦山天空步道（彰化，footway 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E5%85%AB%E5%8D%A6%E5%B1%B1%E5%A4%A9%E7%A9%BA%E6%AD%A5%E9%81%93"],
  admin="彰化縣", category="本島", tags=["mountain", "city"],
  subjects=[
   dict(suffix="P01", template="sunset", seasonal=None,
    zh="八卦山天空步道彰化平原夕照", en="Changhua plain sunset from Baguashan skywalk",
    ja="八卦山スカイウォークの夕焼け",
    desc_zh="天空步道高架棧道向西眺望彰化平原與鹿港方向夕照（OSM footway 節點；海拔查無權威源誠實留空）；與既有 tw-150 九天夕陽之樹（大肚山台地孤樹）題材錯位——本點為彰化市緣山稜步道。",
    desc_en="Elevated boardwalk sunset over the Changhua plain toward Lukang (OSM footway node; elevation honestly left empty); disjoint from tw-150's Dadu-plateau lone-tree subject.",
    desc_ja="八卦山スカイウォークから彰化平原と鹿港方面の夕日（OSM）。九天夕陽之樹とは題材が別。"),
   dict(suffix="P02", template="sunrise", seasonal=None,
    zh="八卦山晨光", en="Baguashan dawn", ja="八卦山の朝焼け",
    desc_zh="清早晨光越過台中盆地側的稜線展望（與同點 P01 夕照契約分列）；方位暫以 generic 東向 tolerance 85 註冊，待現場校準。",
    desc_en="Dawn light over the Taichung-basin side of the ridge (separate from the P01 sunset contract); generic east sector, tolerance 85, pending field calibration.",
    desc_ja="早朝の光（P01 とは別契約）。方位は暫定の東向き。"),
  ]),
 dict(place_id="tw-163", region="tw", slug="bantianyan-ziyunsi", score=None,
  names={"zh-TW": "半天岩紫雲寺後山", "en": "Bantianyan Ziyun Temple back hill",
         "ja": "半天岩紫雲寺の裏山", "local": "半天岩紫雲寺"},
  lat=23.4621, lon=120.5958, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 半天岩紫雲寺（嘉義番路，place_of_worship 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E5%8D%8A%E5%A4%A9%E5%B2%A9%E7%B4%AB%E9%9B%B2%E5%AF%BA"],
  admin="嘉義縣", category="本島", tags=["mountain", "city", "starlight"],
  subjects=[
   dict(suffix="P01", template="city_night", seasonal=None,
    zh="半天岩嘉義市區琉璃夜景", en="Chiayi city liuli night view from Bantianyan",
    ja="半天岩から嘉義市街の夜景",
    desc_zh="紫雲寺後山高點俯瞰嘉義市區萬家燈火與蘭潭方向琉璃光（OSM place_of_worship 節點；海拔查無權威源誠實留空）；與既有 tw-022 二延平步道（隙頂霧景）題材錯位——本點為市街夜景。",
    desc_en="Back-hill lookout over Chiayi city lights and the Lantan direction (OSM place-of-worship node; elevation honestly left empty); disjoint from Eryanping's mist subject.",
    desc_ja="紫雲寺裏山から嘉義市街の灯り（OSM）。二延平とは題材が別。"),
  ]),
 dict(place_id="tw-164", region="tw", slug="lijia-forest-road", score=None,
  names={"zh-TW": "利嘉林道", "en": "Lijia forest road (Beinan)", "ja": "利嘉林道",
         "local": "利嘉林道"},
  lat=22.8050, lon=121.0418, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 利嘉林道（台東卑南，track 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E5%88%A9%E5%98%89%E6%9E%97%E9%81%93%20%E5%8F%B0%E6%9D%B1"],
  admin="台東縣", category="本島", tags=["mountain", "forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="利嘉林道茶園與台東平原展望", en="Lijia tea terraces and Taitung plain outlook",
    ja="利嘉林道の茶園と台東平原の展望",
    desc_zh="利嘉林道高段俯瞰利嘉茶園與台東平原、遠眺太平洋（OSM track 節點；海拔查無權威源誠實留空）；清單主題的螢火蟲季窗查無本站可繫結的權威季節資料源，誠實不建時間窗契約——本契約為茶園與平原展望主體。",
    desc_en="Upper Lijia forest road lookout over tea terraces and the Taitung plain toward the Pacific (OSM track node; elevation honestly left empty). The list's firefly-season window has no authoritative seasonal source we can bind, so no time-window contract is built - honestly.",
    desc_ja="利嘉林道から茶園と台東平原を望む（OSM）。蛍の季節窓は権威源がなく誠実に不構築。"),
  ]),
 dict(place_id="tw-165", region="tw", slug="nanheng-yakou", score=None,
  names={"zh-TW": "南橫埡口/大關山隧道口", "en": "Nanheng Yakou (Daguanshan tunnel east portal)",
         "ja": "南横埡口（大関山隧道東口）", "local": "南橫埡口"},
  lat=23.2680, lon=120.9734, elev_m=2722, coord_conf="high",
  coord_source="zh.wikipedia 南橫公路（埡口＝台20線142K，海拔2722公尺，大關山隧道東口）＋OSM Nominatim 南橫埡口（節點）",
  coord_sources=["https://zh.wikipedia.org/wiki/%E5%8D%97%E6%A9%AB%E5%85%AC%E8%B7%AF",
                 "https://www.openstreetmap.org/search?query=%E5%8D%97%E6%A9%AB%E5%9F%A1%E5%8F%A3"],
  admin="台東縣", category="本島", tags=["mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="sunrise", seasonal=None,
    zh="南橫埡口關山嶺晨光", en="Nanheng Yakou dawn toward Guanshanling",
    ja="南横埡口の朝の光",
    desc_zh="海拔2,722公尺埡口（大關山隧道東口）面向關山嶺山稜線晨光（zh.wikipedia 海拔；OSM 節點）；與既有 tw-045 嘉明湖（高山湖泊）題材錯位——本點為公路埡口晨景。",
    desc_en="Dawn over the Guanshanling ridge from the 2,722 m saddle at the Daguanshan tunnel east portal (zh.wikipedia elevation; OSM node); disjoint from Jiaming Lake's alpine-lake subject.",
    desc_ja="標高2,722mの埡口（大関山隧道東口）から関山嶺山方面の朝の光。嘉明湖とは題材が別。"),
   dict(suffix="P02", template="cloud_sea", seasonal=None,
    zh="南橫埡口雲海雲瀑", en="Nanheng Yakou cloud sea and cloud waterfall",
    ja="南横埡口の雲海と雲瀑",
    desc_zh="埡口經典南橫雲海/雲瀑展望（與同點 P01 晨光契約分列；清單主題的「雲瀑」以 cloud_sea 模板登記，雲瀑語義待現場校準）。",
    desc_en="The classic Yakou cloud sea / cloud-waterfall outlook (separate from the P01 dawn contract; the list's 'cloud waterfall' topic is registered under the cloud_sea template, semantics pending field calibration).",
    desc_ja="埡口の雲海・雲瀑の展望（P01 とは別契約）。"),
  ]),
 dict(place_id="tw-166", region="tw", slug="taixi-haiyuan", score=None,
  names={"zh-TW": "台西海園木棧道", "en": "Taixi Haiyuan boardwalk (Yunlin)",
         "ja": "台西海園の木道", "local": "台西海園"},
  lat=23.7317, lon=120.1744, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 台西海園（雲林台西，hamlet 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E5%8F%B0%E8%A5%BF%E6%B5%B7%E5%9C%92"],
  admin="雲林縣", category="本島", tags=["coast"],
  subjects=[
   dict(suffix="P01", template="sunset", seasonal=None,
    zh="台西海園蚵田夕照", en="Taixi oyster-field sunset", ja="台西海園の夕焼け",
    desc_zh="台西海園木棧道與蚵田海堤向西台灣海峽夕照（OSM hamlet 節點；海拔查無權威源誠實留空）；與既有 tw-017 王功漁港（燈塔與蚵田）題材錯位——本點為台西海岸木棧道主體（30km 錯位）。",
    desc_en="Boardwalk and oyster-field sunset toward the Taiwan Strait at Taixi (OSM hamlet node; elevation honestly left empty); disjoint from Wanggong's lighthouse subject 30 km away.",
    desc_ja="台西海園の木道と牡蠣田の夕日（OSM）。王功漁港とは題材が別。"),
  ]),
 dict(place_id="tw-167", region="tw", slug="taman-magic-forest", score=None,
  names={"zh-TW": "塔曼山魔幻森林展望點", "en": "Taman Mountain magic-forest lookout",
         "ja": "タマン山の魔幻の森展望", "local": "塔曼山"},
  lat=24.706000, lon=121.450417, elev_m=2128, coord_conf="high",
  coord_source="zh.wikipedia 塔曼山（海拔2,127.9公尺；座標24.706000,121.450417，國土測繪中心1/5000像片基本圖）",
  coord_sources=["https://zh.wikipedia.org/zh-tw/%E5%A1%94%E6%9B%BC%E5%B1%B1"],
  admin="桃園市", category="本島", tags=["mountain", "forest", "starlight"],
  subjects=[
   dict(suffix="P01", template="mountain_view", seasonal=None,
    zh="塔曼山魔幻森林稜線展望", en="Taman Mountain magic-forest ridge outlook",
    ja="タマン山の稜線展望",
    desc_zh="塔曼山（2,127.9m，新北市最高山，插天山自然保留區邊緣）魔幻森林步道稜線展望雲霧森林（zh.wikipedia 海拔/座標）；與既有 tw-056 松蘿湖（湖泊）題材錯位——本點為塔魔巴稜線森林。",
    desc_en="Ridge outlook through the 'magic forest' on Taman Mountain (2,127.9 m, New Taipei's highest; zh.wikipedia elevation/coordinates, NLSC 1/5000 base map); disjoint from Songluo Lake's lake subject.",
    desc_ja="標高2,127.9mのタマン山（新北市最高峰）の魔幻の森と稜線の展望。松蘿湖とは題材が別。"),
  ]),
 dict(place_id="tw-168", region="tw", slug="zhuangwei-dune-coast", score=None,
  names={"zh-TW": "壯圍沙丘海岸", "en": "Zhuangwei dune coast (Yilan)",
         "ja": "壮圍の砂丘海岸", "local": "壯圍沙丘"},
  lat=24.7379, lon=121.8201, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 壯圍沙丘旅遊服務園區（宜蘭壯圍，park 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E5%A3%AF%E5%9C%8D%E6%B2%99%E4%B8%98%E6%97%85%E9%81%8A%E6%9C%8D%E5%8B%99%E5%9C%92%E5%8D%80"],
  admin="宜蘭縣", category="本島", tags=["coast", "beach"],
  subjects=[
   dict(suffix="P01", template="sunset", seasonal=None,
    zh="壯圍沙丘海岸線夕照", en="Zhuangwei dune-coast sunset", ja="壮圍砂丘海岸の夕焼け",
    desc_zh="壯圍沙丘旅遊服務園區周邊沙丘海岸線與蘭陽溪口夕照（OSM park 節點；海拔查無權威源誠實留空）；與既有 tw-092 外澳沙灘／龜山朝日（8.3km， surf/朝日）題材錯位——本點為沙丘地景。",
    desc_en="Dune-coastline sunset near the Zhuangwei Dune Visitor Service area and the Lanyang river mouth (OSM park node; elevation honestly left empty); disjoint from Waiao's surf/sunrise subject 8.3 km away.",
    desc_ja="壮圍砂丘と蘭陽渓河口の夕日（OSM）。外澳とは題材が別。"),
  ]),
 dict(place_id="tw-169", region="tw", slug="daxueshan-48k-yakou", score=None,
  names={"zh-TW": "大雪山48K啞口", "en": "Daxueshan 48K saddle lookout",
         "ja": "大雪山48K埡口", "local": "大雪山48K啞口"},
  lat=24.2688, lon=121.0306, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 大雪山森林遊樂區埡口觀景台停車場（台中大雪山林道高段）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E5%A4%A7%E9%9B%AA%E5%B1%B1%E6%A3%AE%E6%9E%97%E9%81%8A%E6%A8%82%E5%8D%80%E5%9F%A1%E5%8F%A3%E8%A7%80%E6%99%AF%E5%8F%B0"],
  admin="台中市", category="本島", tags=["mountain", "forest", "starlight"],
  subjects=[
   dict(suffix="P01", template="sunset", seasonal=None,
    zh="大雪山48K啞口雪山西稜夕照", en="Daxueshan 48K saddle sunset over the Xueshan west ridge",
    ja="大雪山48K埡口の夕焼け",
    desc_zh="大雪山林道48K啞口高點向西雪山西稜夕照與雲瀑（OSM 埡口觀景台停車場節點；海拔查無權威源誠實留空）；與既有 tw-087 大雪山森林遊樂區43K觀景台（9.6km 錯位）及 tw-016 鳶嘴山（8.3km）題材錯位——本點為48K啞口主體。",
    desc_en="Sunset over the Xueshan west ridge and cloud waterfall from the 48K saddle on the Daxueshan forest road (OSM saddle-lookout parking node; elevation honestly left empty); disjoint from the 43K lookout (9.6 km) and Yuanzui Mountain (8.3 km).",
    desc_ja="大雪山林道48K埡口から雪山山脈西稜の夕日と雲瀑（OSM）。43K観景台・鳶嘴山とは題材が別。"),
  ]),
 dict(place_id="tw-170", region="tw", slug="shishan-liuliao-trail", score=None,
  names={"zh-TW": "峨眉獅山古道/六寮古道", "en": "Shishan / Liuliao historic trails (Emei)",
         "ja": "獅山古道・六寮古道（峨眉）", "local": "獅山古道"},
  lat=24.6490, lon=121.0197, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 獅山古道（新竹峨眉/獅頭山，service way 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E7%8D%85%E5%B1%B1%E5%8F%A4%E9%81%93%20%E6%96%B0%E7%AB%B9"],
  admin="新竹縣", category="本島", tags=["mountain", "forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="獅山古道稜線與六寮溪谷展望", en="Shishan trail ridge and Liuliao creek outlook",
    ja="獅山古道の稜線と六寮渓谷の展望",
    desc_zh="獅頭山獅山古道稜線段俯瞰六寮溪谷與峨眉湖方向（OSM service way 節點；海拔查無權威源誠實留空）；清單主題的螢火蟲/油桐花季窗查無本站可繫結的權威季節資料源，誠實不建時間窗契約——本契約為古道稜線展望主體。",
    desc_en="Ridge section of the Shishan historic trail overlooking the Liuliao creek valley toward Emei Lake (OSM service-way node; elevation honestly left empty). The list's firefly/tung-blossom windows have no authoritative seasonal source we can bind, so no time-window contract is built - honestly.",
    desc_ja="獅山古道の稜線から六寮渓谷と峨眉湖方面を望む（OSM）。蛍・桐の季節窓は権威源がなく誠実に不構築。"),
  ]),
 dict(place_id="tw-171", region="tw", slug="chenglong-wetland", score=None,
  names={"zh-TW": "成龍濕地", "en": "Chenglong wetland (Kouhu, Yunlin)",
         "ja": "成龍溼地", "local": "成龍濕地"},
  lat=23.5586, lon=120.1625, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 成龍濕地（雲林口湖，wetland 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E6%88%90%E9%BE%8D%E6%BF%95%E5%9C%B0"],
  admin="雲林縣", category="本島", tags=["coast"],
  subjects=[
   dict(suffix="P01", template="sunset", seasonal=None,
    zh="成龍濕地水鳥夕照", en="Chenglong wetland waterbird sunset", ja="成龍溼地の夕焼け",
    desc_zh="成龍濕地觀海樓周邊水鳥棲地與夕照同框（OSM wetland 節點；海拔查無權威源誠實留空）；與既有 tw-157 雙春濱海遊憩區（28.6km，木麻黃防風林）題材錯位——本點為內陸化濕地主體。",
    desc_en="Waterbird habitat and sunset around the Guanhai pavilion at Chenglong wetland (OSM wetland node; elevation honestly left empty); disjoint from Shuangchun's casuarina-forest subject 28.6 km away.",
    desc_ja="成龍溼地の水鳥と夕日（OSM）。双春浜海遊憩区とは題材が別。"),
  ]),
 dict(place_id="tw-172", region="tw", slug="lalashan-baling", score=None,
  names={"zh-TW": "拉拉山巴陵", "en": "Lalashan Baling (Taoyuan)", "ja": "拉拉山巴陵",
         "local": "拉拉山巴陵"},
  lat=24.6780, lon=121.3851, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 巴陵（桃園復興華陵里，bus_stop 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E5%B7%B4%E9%99%B5%20%E6%A1%83%E5%9C%92"],
  admin="桃園市", category="本島", tags=["mountain", "forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="巴陵橋與大漢溪谷展望", en="Baling bridge and Dahan creek gorge outlook",
    ja="巴陵大橋と大漢渓谷の展望",
    desc_zh="巴陵地區（巴陵橋/巴陵古道一帶）俯瞰大漢溪谷與爺亨方向山巒（OSM bus_stop 節點；海拔查無權威源誠實留空）；清單主題的芒花/茶園季窗查無本站可繫結的權威季節資料源，誠實不建時間窗契約——本契約為巴陵溪谷展望主體。",
    desc_en="Outlook over the Dahan creek gorge from the Baling area (Baling bridge/old trail; OSM bus-stop node; elevation honestly left empty). The list's silvergrass/teaterrace windows have no authoritative seasonal source we can bind, so no time-window contract is built - honestly.",
    desc_ja="巴陵地区から大漢渓谷を望む（OSM）。芒草・茶園の季節窓は権威源がなく誠実に不構築。"),
  ]),
 dict(place_id="tw-173", region="tw", slug="mingchi-forest", score=None,
  names={"zh-TW": "明池森林遊樂區", "en": "Mingchi National Forest Recreation Area",
         "ja": "明池国家森林遊楽区", "local": "明池森林遊樂區"},
  lat=24.6501, lon=121.4706, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 明池國家森林遊樂區（宜蘭大同，nature_reserve 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E6%98%8E%E6%B1%A0%E5%9C%8B%E5%AE%B6%E6%A3%AE%E6%9E%97%E9%81%8A%E6%A8%82%E5%8D%80"],
  admin="宜蘭縣", category="本島", tags=["mountain", "forest"],
  subjects=[
   dict(suffix="P01", template="seasonal_plant", seasonal="red_maple",
    zh="明池紅葉", en="Mingchi autumn maple", ja="明池の紅葉",
    desc_zh="明池山莊周邊紅葉與湖沼森林（沿用 seasonal-calendar 既有 red_maple 窗 10-20..11-10；海拔查無權威源誠實留空）；與既有 tw-140 太平山森林遊樂區（14.3km，檜木林與蹦蹦車）題材錯位——本點為明池湖沼紅葉主體。",
    desc_en="Autumn maple around the Mingchi lake villa (reuses the existing seasonal-calendar red_maple window 10-20..11-10; elevation honestly left empty); disjoint from Taipingshan's cypress-forest subject 14.3 km away.",
    desc_ja="明池湖畔の紅葉（red_maple 季節窓を再利用）。太平山とは題材が別。"),
   dict(suffix="P02", template="mountain_view", seasonal=None,
    zh="明池湖沼霧林展望", en="Mingchi lake and mist-forest outlook", ja="明池の湖と霧の森",
    desc_zh="明池湖沼與北橫霧林山巒展望（與同點 P01 紅葉季窗契約分列）。",
    desc_en="Lake and mist-forest mountain outlook (separate from the P01 seasonal-maple contract).",
    desc_ja="明池の湖沼と霧の森の展望（P01 とは別契約）。"),
  ]),
]

REJECTED_PLACES = [
    ("北投四季長廊/吳氏宗祠", "5km dedupe reject: 3.05km from existing tw-001 大屯山助航站 - same 大屯山系台北盆地夜景/夕照 family, not subject-disjoint"),
    ("北關海潮公園單面山/豆腐岩", "identical existing place: name-matched tw-092 北關海潮公園 already in catalog (OSM coordinate 24.9119,121.8772 vs recorded tw-092 24.793,121.875 - coordinate discrepancy noted honestly)"),
    ("南橫摩天農場", "5km dedupe reject: 1.56km from existing tw-118 栗松溫泉野溪峽谷 - same 南橫利稻段山場 family, not subject-disjoint"),
    ("司馬庫斯巨木群", "5km dedupe reject: 2.32km from existing tw-091 司馬庫斯部落觀景點 - same 司馬庫斯部落 family, not subject-disjoint"),
    ("合歡東峰", "5km dedupe reject: 1.26km from existing tw-019 合歡山主峰 - same 合歡群峰日出/雲海 summit family, not subject-disjoint"),
    ("吉安日光步道", "5km dedupe reject: 1.42km from existing tw-153 楓林步道（花蓮吉安） - same 吉安平原夜景/夕照家族, not subject-disjoint"),
    ("向陽森林遊樂區", "5km dedupe reject: 1.75km from wave-3 admitted tw-165 南橫埡口/大關山隧道口 - same 南橫埡口-向陽鞍部 family, not subject-disjoint"),
    ("基隆嶼蝙蝠洞/海蝕峭壁", "5km dedupe reject: 4.27km from existing tw-010 和平島 - same 基隆嶼/和平島海景 family, not subject-disjoint"),
    ("大尖山/二尖山茶園步道", "5km dedupe reject: 3.44km from existing tw-105 太平雲梯／梅山36彎 - same 梅山茶園步道 cluster, not subject-disjoint"),
    ("大肚山藍色公路", "5km dedupe reject: 1.33km from existing tw-150 九天夕陽之樹/大肚山台地 - same 大肚山台地夜景/夕照 family, not subject-disjoint"),
    ("大霸中霸坪", "identical existing place: 0.06km from existing tw-046 大霸尖山 - same summit massif"),
    ("小門嶼鯨魚洞框景", "5km dedupe reject: 3.54km from existing tw-058 澎湖跨海大橋 - same 澎湖西嶼夕照 family, not subject-disjoint"),
    ("尾寮山觀景亭", "5km dedupe reject: 3.29km from existing tw-108 龍頭山／多納環流丘 - same 屏東山系展望 family, not subject-disjoint"),
    ("拉拉山恩愛農場/巴陵觀景台", "5km dedupe reject: 4.22km from wave-3 admitted tw-172 拉拉山巴陵 and 3.19km from wave-3 admitted tw-167 塔曼山 - same 拉拉山-塔曼山稜線 family, not subject-disjoint"),
    ("文化大學後山情人坡", "5km dedupe reject: 4.76km from existing tw-001 大屯山助航站 (4.90km tw-097 擎天崗) - same 大屯山系台北夜景 family, not subject-disjoint"),
    ("新豐新月沙灣", "pure swimming beach exclusion (owner rules)"),
    ("旗後燈塔/旗津海水浴場", "5km dedupe reject: 1.64km from existing tw-028 駁二藝術特區 - same 高雄港灣夕照 family, not subject-disjoint"),
    ("望洋山日出觀景台", "5km dedupe reject: 1.05km from existing tw-088 翠峰湖環山步道觀景點 - same 太平山山系晨霧日出 family, not subject-disjoint"),
]


def wb(p, text): return m2.wb(p, text)


def _build_contract(p, subj):
    """Copy of the wave-2 contract builder; module globals (TICKET/WAVE) resolve to wave-3."""
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
    safety = {
        "zh-TW": "請依現場安全指示行動；夜間/冬季天候險惡時請勿冒進。",
        "en": "Follow on-site safety guidance; do not push on in severe night/winter weather.",
        "ja": "現地の安全指示に従う。夜間・冬季の悪天候では無理をしない。",
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
            "access_notes_i18n": access, "safety_notes_i18n": safety,
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
    existing = R.get_spots("tw")  # already includes tw-125..tw-161
    rows = {}
    for p in PLACES:
        pool = existing + [ {"spot_id": q["place_id"], "lat": q["lat"], "lon": q["lon"],
                             "name_i18n": {"zh-TW": q["names"]["zh-TW"]}}
                            for q in PLACES if q is not p ]
        dists = sorted((hav(p["lat"], p["lon"], s["lat"], s["lon"])/1000, s["spot_id"],
                        s["name_i18n"]["zh-TW"]) for s in pool)
        nearest = dists[0]
        assert nearest[0] >= 5.0, f"{p['place_id']} within 5km of {nearest}"
        rows[p["place_id"]] = {"nearest_existing": nearest[1], "name": nearest[2],
                               "km": round(nearest[0], 2)}
    dedupe[f"_rejected_family_overlaps_wave{WAVE}"] = [
        {"name": n, "reason": r} for n, r in REJECTED_PLACES]
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
    if '"tw-162"' not in text:
        # anchor: last wave-2 tuple (tw-161) — positional spot_id invariant: wave-3 tuples append AFTER it
        a_tw = ('            (25.238999, 121.6323619, "中角灣/沙珠灣", "Zhongjiao Bay / Shazhu Bay (Jinshan)", '
                '"中角湾／沙珠湾", "中角灣", "本島", ["coast"]),  # CL-DATA-66\n')
        assert a_tw in text, "tw-161 tuple anchor missing"
        lines = []
        for p in PLACES:
            n = p["names"]
            lines.append(
                f'            ({p["lat"]}, {p["lon"]}, "{n["zh-TW"]}", "{n["en"]}", '
                f'"{n["ja"]}", "{n["local"]}", "{p["category"]}", {json.dumps(p["tags"], ensure_ascii=False)}),  # {TICKET}\n')
        text = text.replace(a_tw, a_tw + "".join(lines), 1)
        a_admin = '    "tw-161": ["新北市"],  # CL-DATA-66\n'
        assert a_admin in text, "admin anchor missing"
        adm = "".join(f'    "{p["place_id"]}": ["{p["admin"]}"],  # {TICKET}\n' for p in PLACES)
        text = text.replace(a_admin, a_admin + adm, 1)
        # elevations: insert the wave-3 block before the wave-2 elevation comment
        a_elev = '    # CL-DATA-66 wave-2 admission elevations (web-verified 2026-11-11; null elevations omitted honestly)\n'
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

    # ---- 5) web evidence registry (extend wave-2 file) ----
    ev_path = ROOT / "data/v2/audits/cl-data-66_web_evidence.json"
    ev = json.loads(ev_path.read_bytes().decode("utf-8"))
    wave3_places = []
    wave3_evidence = []
    for p in PLACES:
        wave3_places.append({
            "place_id": p["place_id"], "slug": p["slug"], "score": None,
            "lat": p["lat"], "lon": p["lon"], "elev_m": p["elev_m"],
            "coord_confidence": p["coord_conf"], "coord_source": p["coord_source"],
            "sources": p["coord_sources"], "subjects": [s["zh"] for s in p["subjects"]],
            "ticket": TICKET, "wave": WAVE})
        wave3_evidence.append({
            "id": f"e-d66-web-{p['slug']}", "grade": "A" if p["coord_conf"] == "high" else "B",
            "kind": "official_or_wikipedia_or_osm_text",
            "url": p["coord_sources"][0],
            "supports": p["coord_source"],
            "retrieved_at": VER_DATE,
            "limitation": "Coordinate/elevation verified against cited sources; exact tripod position and access not field-surveyed; opening/closure/permit/reservation status follows on-site notices.",
            "ticket": TICKET, "wave": WAVE})
    ev["places_wave3"] = wave3_places
    ev["evidence_wave3"] = wave3_evidence
    ev["places_wave3_count"] = len(wave3_places)
    ev["rejected_wave3_count"] = len(REJECTED_PLACES)
    ev["rule_wave3"] = (f"Scoreless intake wave {WAVE} (owner ruling {VER_DATE}): admission = web verification + "
                        "5km subject-disjoint dedupe; NO rubric v2 gates, NO AGLI dual-board, agli-final "
                        f"untouched; score fields left empty. 12 places admitted (tw-162..tw-173), 18 "
                        "manifest-next-30 candidates rejected (15 same-family <5km overlaps + 2 identical "
                        "existing places + 1 pure-swimming-beach).")
    wb(ev_path, cl.jdump(ev))
    print("web evidence extended:", len(wave3_places))

    # ---- 6) tier-a manifest wave-3 status update ----
    tm_path = ROOT / "data/v2/audits/subject-lists/tier-a-manifest.json"
    tm = json.loads(tm_path.read_bytes().decode("utf-8"))
    adm_names = {p["names"]["zh-TW"]: p["place_id"] for p in PLACES}
    rej_names = dict(REJECTED_PLACES)
    changed = 0
    for r in tm["tier_a"]:
        if r.get("status") in ("admitted", "rejected"):
            continue
        if r["name"] in adm_names:
            r["status"] = "admitted"; r["wave"] = WAVE; r["admitted_place_id"] = adm_names[r["name"]]
            changed += 1
        elif r["name"] in rej_names:
            r["status"] = "rejected"; r["wave"] = WAVE; r["reject_reason"] = rej_names[r["name"]]
            changed += 1
    tm[f"wave{WAVE}"] = {"planned": 30, "order": "n_topics desc, n_lists desc",
                         "done": len(PLACES), "rejected": len(REJECTED_PLACES),
                         "place_ids": [p["place_id"] for p in PLACES],
                         "rejected_names": [n for n, _ in REJECTED_PLACES]}
    wb(tm_path, cl.jdump(tm))
    print("tier-a manifest updated: changed", changed, "admitted", len(PLACES), "rejected", len(REJECTED_PLACES))
    print("DONE wave-3 stage-1 build")


if __name__ == "__main__":
    main()
