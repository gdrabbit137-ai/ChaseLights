#!/usr/bin/env python3
"""CL-DATA-66 Wave 2: scoreless intake of 15 Tier-A places (tw-147..tw-161).

Owner rulings (2026-11-11): intake is SCORELESS — admission = web verification
(authoritative URL) + 5km subject-disjoint dedupe; no rubric/AGLI scoring,
agli-final untouched; score fields left empty. Contracts built in full (V2 +
legacy dual-track). 15 of the manifest-next-30 candidates admitted; 15 rejected
(14 same-family <5km overlaps + 1 pure-swimming-beach exclusion), recorded in
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
    'cl66w1', str(ROOT / 'data/v2/tools/discovery/cl_data_66_build.py'))
m66 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m66)
cl = m66.cl

TICKET = "CL-DATA-66"
VER_DATE = "2026-11-11"
WAVE = 2

PLACES = [
 dict(place_id="tw-147", region="tw", slug="zhenting-zhenitoushan", score=None,
  names={"zh-TW": "關仔嶺枕頭山觀景台", "en": "Zhenitoushan viewpoint (Guanziling)",
         "ja": "関子嶺枕頭山の展望台", "local": "關仔嶺枕頭山觀景台"},
  lat=23.3271039, lon=120.4860274, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 枕頭山（台南白河，peak）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E6%9E%95%E9%A0%AD%E5%B1%B1%20%E5%8F%B0%E5%8D%97"],
  admin="台南市", category="本島", tags=["mountain", "city"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="枕頭山關仔嶺環景", en="Guanziling panorama from Zhenitoushan", ja="枕頭山から関子嶺を望む",
    desc_zh="白河枕頭山山頂展望關仔嶺溫泉聚落與嘉南平原（OSM peak 節點；海拔查無權威源誠實留空）；與既有 tw-022 二延平步道（隙頂茶園霧景）題材錯位——本點為溫泉聚落環景。",
    desc_en="Summit lookout over the Guanziling hot-spring settlement and Chianan plain from Zhenitoushan, Baihe (OSM peak node; elevation honestly left empty - no authoritative source).",
    desc_ja="白河の枕頭山山頂から関子嶺温泉集落と嘉南平原を望む（OSM peak ノード）。標高は未確認のため誠実に空欄。"),
   dict(suffix="P02", template="sunset", seasonal=None,
    zh="枕頭山夕照", en="Zhenitoushan sunset over the plain", ja="枕頭山の夕映え",
    desc_zh="山頂向西眺望嘉南平原夕照（與同點 P01 環景契約題材分列）；方位暫以 generic 西向 tolerance 85 註冊，待現場校準。",
    desc_en="Westward sunset over the Chianan plain from the summit (separate contract from the P01 panorama); generic west sector, tolerance 85, pending field calibration.",
    desc_ja="山頂から嘉南平原の夕日（P01 とは別契約）。"),
  ]),
 dict(place_id="tw-148", region="tw", slug="zhongliaoshan-lianhuating", score=None,
  names={"zh-TW": "中寮山蓮花亭", "en": "Zhongliaoshan Lianhua Pavilion viewpoint",
         "ja": "中寮山蓮花亭", "local": "中寮山蓮花亭"},
  lat=22.8302177, lon=120.4327770, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 中寮山（高雄田寮，peak）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E4%B8%AD%E5%AF%AE%E5%B1%B1%20%E9%AB%98%E9%9B%84"],
  admin="高雄市", category="本島", tags=["mountain", "starlight", "city"],
  subjects=[
   dict(suffix="P01", template="city_night", seasonal=None,
    zh="中寮山蓮花亭琉璃夜景", en="Zhongliaoshan night lights (liuli)", ja="中寮山の夜景",
    desc_zh="蓮花亭俯瞰田寮月世界與岡山地區夜燈（OSM peak；海拔查無權威源誠實留空）；與既有 tw-027 田寮月世界（惡地地質日景）題材錯位——本點為市街琉璃光。",
    desc_en="Pavilion lookout over the Tianliao moon-world badlands and Gangshan area night lights (OSM peak; elevation honestly left empty); disjoint from the badlands-geology subject of tw-027.",
    desc_ja="蓮花亭から田寮月世界と岡山方面の灯り（OSM peak）。月世界とは題材が別。"),
   dict(suffix="P02", template="sunset", seasonal=None,
    zh="中寮山夕照", en="Zhongliaoshan sunset", ja="中寮山の夕映え",
    desc_zh="蓮花亭向西夕照（與同點 P01 夜景契約分列）；方位暫以西向 tolerance 85 註冊。",
    desc_en="Westward sunset from the pavilion (separate from the P01 night contract); generic west sector, tolerance 85.",
    desc_ja="蓮花亭から西向きの夕日（P01 とは別契約）。"),
  ]),
 dict(place_id="tw-149", region="tw", slug="jiufenershan-quake-memorial", score=None,
  names={"zh-TW": "九份二山國家地震紀念地", "en": "Jiufenershan earthquake memorial",
         "ja": "九份二山国家地震紀念地", "local": "九份二山"},
  lat=23.9345856, lon=120.8416300, elev_m=1173, coord_conf="high",
  coord_source="OSM Nominatim 九份二山（peak）＋zh.wikipedia 九份二山（峰頂海拔1,173m）",
  coord_sources=["https://zh.wikipedia.org/wiki/%E4%B9%9D%E4%BB%BD%E4%BA%8C%E5%B1%B1"],
  admin="南投縣", category="本島", tags=["mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="sunrise", seasonal=None,
    zh="九份二山日出", en="Jiufenershan dawn", ja="九份二山の日の出",
    desc_zh="九份二山（1,173m，921大地震紀念地/堰塞湖）山頂展望日出（zh.wikipedia 海拔；OSM peak）；與既有 tw-020 金龍山（晨霧攝影勝地）題材錯位。",
    desc_en="Dawn from the 1,173 m summit of Jiufenershan (921 earthquake memorial/landslide lake; zh.wikipedia elevation; OSM peak); disjoint from Jinlongshan's morning-mist subject.",
    desc_ja="標高1,173mの九份二山（921地震紀念地・堰塞湖）山頂の日の出。金龍山とは題材が別。"),
   dict(suffix="P02", template="overlook", seasonal=None,
    zh="九份二山紀念地展望", en="Jiufenershan memorial viewpoint", ja="九份二山の展望",
    desc_zh="紀念地步道俯瞰堰塞湖遺跡與南港溪谷（與同點 P01 日出契約分列）。",
    desc_en="Trail lookout over the landslide-lake remains and the Nangang creek valley (separate from the P01 dawn contract).",
    desc_ja="堰塞湖跡と南港渓谷を見下ろす展望（P01 とは別契約）。"),
  ]),
 dict(place_id="tw-150", region="tw", slug="jiutian-sunset-tree", score=None,
  names={"zh-TW": "九天夕陽之樹/大肚山台地", "en": "Jiutian sunset tree (Dadu Plateau)",
         "ja": "九天夕陽之樹（大肚山台地）", "local": "九天夕陽之樹"},
  lat=24.1447185, lon=120.5785534, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 望高寮（台中南屯春社里，大肚山台地高點一帶）＋自由時報/墨刻報導（九天夕陽之樹位於大肚山台地高點、俯瞰台中盆地）；海拔查無獨立權威值誠實留空",
  coord_sources=["https://playing.ltn.com.tw/article/23989", "https://www.mook.com.tw/article/23799"],
  admin="台中市", category="本島", tags=["city", "starlight"],
  subjects=[
   dict(suffix="P01", template="sunset", seasonal=None,
    zh="九天夕陽之樹夕照", en="Jiutian sunset-tree golden hour", ja="九天夕陽之樹の夕焼け",
    desc_zh="大肚山台地高點孤樹夕照、遠眺台中港海線（自由時報/墨刻列名 IG 打卡夕景；座標取 OSM 望高寮一帶）；與既有 tw-015 高美濕地（濕地雲彩倒影）題材錯位。",
    desc_en="Lone-tree golden hour on the Dadu Plateau crest, overlooking Taichung port coastline (photo-community sunset landmark; coordinate from the OSM Wanggaoliao area).",
    desc_ja="大肚山台地の孤樹と夕焼け（IG有名スポット）。高美濕地とは題材が別。"),
   dict(suffix="P02", template="city_night", seasonal=None,
    zh="大肚山百萬夜景", en="Dadu Plateau million-dollar night view", ja="大肚山の夜景",
    desc_zh="夜幕後俯瞰台中盆地萬家燈火（媒體口徑「百萬夜景」；與同點 P01 夕照契約分列）。",
    desc_en="Night view over the Taichung basin lights after dusk (the 'million-dollar night view'; separate from the P01 sunset contract).",
    desc_ja="夜の台中盆地の灯りを一望（P01 とは別契約）。"),
  ]),
 dict(place_id="tw-151", region="tw", slug="neidong-forest-recreation", score=None,
  names={"zh-TW": "內洞國家森林遊樂區", "en": "Neidong National Forest Recreation Area",
         "ja": "内洞国家森林遊楽区", "local": "內洞森林遊樂區"},
  lat=24.8165785, lon=121.5478222, elev_m=230, coord_conf="high",
  coord_source="OSM Nominatim 內洞國家森林遊樂區（nature_reserve）＋zh.wikipedia（園區標高約230-800公尺，取入口帶230m）",
  coord_sources=["https://zh.wikipedia.org/wiki/%E5%85%A7%E6%B4%9E%E5%9C%8B%E5%AE%B6%E6%A3%AE%E6%9E%97%E9%81%8A%E6%A8%82%E5%8D%80"],
  admin="新北市", category="本島", tags=["forest", "waterfall"],
  subjects=[
   dict(suffix="P01", template="waterfall", seasonal=None,
    zh="內洞三層瀑布", en="Neidong three-tier waterfall", ja="内洞の三段滝",
    desc_zh="南勢溪支流內洞溪三層瀑布與負離子森林（zh.wikipedia：園區標高約230-800m；舊稱娃娃谷）；與既有 tw-144 東眼山（森林稜線）題材錯位——本點為瀑布主體。",
    desc_en="Three-tier waterfall on the Neidong creek inside the negative-ion forest (zh.wikipedia: park 230-800 m; old name 'Wawa Valley'); disjoint from Dongyanshan's ridge-forest subject.",
    desc_ja="内洞渓の三段滝と負離子の森（公式）。東眼山とは題材が別。"),
  ]),
 dict(place_id="tw-152", region="tw", slug="nanfangao-viewpoint", score=None,
  names={"zh-TW": "南方澳觀景台", "en": "Nanfangao viewing platform", "ja": "南方澳展望台",
         "local": "南方澳觀景台"},
  lat=24.5764952, lon=121.8665024, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 南方澳觀景台（park/viewpoint 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E5%8D%97%E6%96%B9%E6%BE%B3%E8%A7%80%E6%99%AF%E5%8F%B0"],
  admin="宜蘭縣", category="本島", tags=["coast", "starlight", "city"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="南方澳漁港全景", en="Nanfangao fishing-port panorama", ja="南方澳漁港の全景",
    desc_zh="觀景台俯瞰南方澳漁港、豆腐岬與太平洋（OSM viewpoint；海拔查無權威源誠實留空）；與既有 tw-033 粉鳥林（海灣秘境沙灘）題材錯位——本點為漁港全景。",
    desc_en="Lookout over Nanfangao harbour, Doufu cape and the Pacific (OSM viewpoint; elevation honestly left empty); disjoint from the secret-bay beach subject of Fenniaolin.",
    desc_ja="南方澳漁港と豆腐岬、太平洋を望む（OSM viewpoint）。粉鳥林とは題材が別。"),
   dict(suffix="P02", template="sunrise", seasonal=None,
    zh="南方澳觀日", en="Nanfangao dawn over the Pacific", ja="南方澳の日の出",
    desc_zh="觀景台面向太平洋的第一道曙光（與同點 P01 全景契約分列）；方位暫以東向 tolerance 85 註冊。",
    desc_en="First light over the Pacific from the platform (separate from the P01 panorama); generic east sector, tolerance 85.",
    desc_ja="太平洋に昇る朝日（P01 とは別契約）。"),
  ]),
 dict(place_id="tw-153", region="tw", slug="fenglin-trail-hualien", score=None,
  names={"zh-TW": "楓林步道（花蓮吉安）", "en": "Fenglin trail viewpoint (Ji'an, Hualien)",
         "ja": "楓林歩道（花蓮吉安）", "local": "楓林步道"},
  lat=23.9671719, lon=121.5471128, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 楓林步道（花蓮吉安）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E6%A5%93%E6%9E%97%E6%AD%A5%E9%81%93%20%E8%8A%B1%E8%93%AE"],
  admin="花蓮縣", category="本島", tags=["mountain", "city"],
  subjects=[
   dict(suffix="P01", template="city_night", seasonal=None,
    zh="吉安平原百萬夜景", en="Ji'an plain night view", ja="吉安平原の夜景",
    desc_zh="楓林步道高點俯瞰花蓮市區與吉安平原夜燈、遠眺太平洋漁火（OSM trail 節點；海拔查無權威源誠實留空）；與既有 tw-082 鯉魚潭（湖面倒影）題材錯位。",
    desc_en="Trail-high lookout over Hualien city and the Ji'an plain lights, with Pacific fishing-boat fires offshore (OSM trail node; elevation honestly left empty).",
    desc_ja="花蓮市街と吉安平原の灯り（OSM）。鯉魚潭とは題材が別。"),
   dict(suffix="P02", template="sunset", seasonal=None,
    zh="吉安平原夕照", en="Ji'an plain sunset", ja="吉安平原の夕映え",
    desc_zh="步道向西俯瞰縱谷平原夕照（與同點 P01 夜景契約分列）；方位暫以西向 tolerance 85 註冊。",
    desc_en="Westward sunset over the rift-valley plain (separate from the P01 night contract); generic west sector, tolerance 85.",
    desc_ja="縦谷平原の夕日（P01 とは別契約）。"),
  ]),
 dict(place_id="tw-154", region="tw", slug="taimali-shuangrufeng", score=None,
  names={"zh-TW": "太麻里雙乳蜂", "en": "Shuangrufeng (Taimali golden-daylily crest)",
         "ja": "太麻里双乳蜂", "local": "太麻里雙乳蜂"},
  lat=22.6446915, lon=120.9520793, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 千鶴亭（太麻里金針山楓林步道段；農業易遊網官方口徑：楓林步道、千鶴亭、雙乳蜂-曙光亭與千禧亭和一等三角點）；海拔查無權威源誠實留空",
  coord_sources=["https://ezgo.ardswc.gov.tw/zh-tw/leisure-area/77/"],
  admin="台東縣", category="本島", tags=["mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="sunrise", seasonal=None,
    zh="雙乳蜂曙光亭第一道曙光", en="First light at Shuguang pavilion, Shuangrufeng", ja="曙光亭の初日の出",
    desc_zh="太麻里金針山制高點段雙乳蜂（曙光亭/千禧亭，一等三角點）的元旦第一道曙光勝地（農業易遊網官方口徑；座標取 OSM 千鶴亭步道段）；與既有 tw-116 太麻里金針山（低處金針花海）題材錯位——本點為制高點曙光。",
    desc_en="First-dawn landmark at the crest of Taimali Daylily Mountain (Shuguang/Qianxi pavilions, first-order triangulation point; official ezgo wording; coordinate from the OSM Qianhe-pavilion trail section); disjoint from the lower daylily-field subject of tw-116.",
    desc_ja="太麻里金針山の最高点（曙光亭・千禧亭、一等三角点）の初日の出。tw-116 とは題材が別。"),
   dict(suffix="P02", template="seasonal_plant", seasonal="daylily_taimali",
    zh="雙乳蜂金針花海", en="Shuangrufeng daylily bloom", ja="双乳蜂の金針花",
    desc_zh="制高點周邊金針花海（沿用 seasonal-calendar 既有 daylily_taimali 窗；與同點 P01 曙光契約分列）。",
    desc_en="Daylily bloom around the crest (reuses the existing seasonal-calendar daylily_taimali window; separate from the P01 dawn contract).",
    desc_ja="最高点付近の金針花（daylily_taimali 季節窓を再利用；P01 とは別契約）。"),
  ]),
 dict(place_id="tw-155", region="tw", slug="xuhai-grassland", score=None,
  names={"zh-TW": "旭海草原公園", "en": "Xuhai grassland park", "ja": "旭海草原公園",
         "local": "旭海草原"},
  lat=22.2046787, lon=120.8852217, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 旭海草原遊樂區（viewpoint）＋草原步道（footway）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E6%97%AD%E6%B5%B7%E8%8D%89%E5%8E%9F"],
  admin="屏東縣", category="本島", tags=["coast", "mountain"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="旭海草原眺望太平洋", en="Pacific views from Xuhai grassland", ja="旭海草原から太平洋を望む",
    desc_zh="草原步道俯瞰旭海漁港與太平洋（OSM viewpoint；海拔查無權威源誠實留空）；與既有 tw-107 佳樂水（風化奇岩海岸）題材錯位——本點為草原海景。",
    desc_en="Grassland-trail lookout over Xuhai harbour and the Pacific (OSM viewpoint; elevation honestly left empty); disjoint from Jialeshui's weathered-rock coast subject.",
    desc_ja="草原歩道から旭海漁港と太平洋（OSM viewpoint）。佳樂水とは題材が別。"),
  ]),
 dict(place_id="tw-156", region="tw", slug="xianxi-rouzongjiao", score=None,
  names={"zh-TW": "線西肉粽角", "en": "Rouzongjiao breakwater point (Xianxi)", "ja": "線西肉粽角",
         "local": "肉粽角"},
  lat=24.1253989, lon=120.4132790, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 肉粽角沙灘（beach）＋zh.wikipedia 肉粽角（彰濱工業區灘地）",
  coord_sources=["https://zh.wikipedia.org/wiki/%E8%82%89%E7%B2%BD%E8%A7%92"],
  admin="彰化縣", category="本島", tags=["coast"],
  subjects=[
   dict(suffix="P01", template="sunset", seasonal=None,
    zh="肉粽角消波塊夕照", en="Rouzongjiao breakwater sunset", ja="肉粽角の夕映え",
    desc_zh="彰濱肉粽角消波塊陣、風機與夕照同框（zh.wikipedia：彰濱工業區灘地；OSM beach 節點）；與既有 tw-017 王功漁港（燈塔與蚵田）題材錯位。",
    desc_en="Tetrapod field, wind turbines and sunset together at the Changhua coastal industrial landfall (zh.wikipedia; OSM beach node); disjoint from Wanggong's lighthouse/oyster-field subject.",
    desc_ja="消波塊と風車と夕日（公式・OSM）。王功漁港とは題材が別。"),
  ]),
 dict(place_id="tw-157", region="tw", slug="shuangchun-coast", score=None,
  names={"zh-TW": "雙春濱海遊憩區", "en": "Shuangchun coastal recreation area", "ja": "双春浜海遊憩区",
         "local": "雙春濱海遊憩區"},
  lat=23.3053536, lon=120.1126626, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 雙春濱海遊憩區（bus_stop/入口節點，台南北門）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E9%9B%99%E6%98%A5%E6%BF%B1%E6%B5%B7%E9%81%8A%E6%86%A9%E5%8D%80"],
  admin="台南市", category="本島", tags=["coast"],
  subjects=[
   dict(suffix="P01", template="sunset", seasonal=None,
    zh="雙春木麻黃林夕照", en="Shuangchun casuarina-forest sunset", ja="双春の木麻黃林と夕日",
    desc_zh="木麻黃防風林步道與沙灘夕照（OSM 遊憩區入口；海拔查無權威源誠實留空）；與既有 tw-026 井仔腳瓦盤鹽田（鹽田倒影）題材錯位——本點為防風林沙灘。",
    desc_en="Casuarina windbreak boardwalk and beach sunset (OSM recreation-area entrance; elevation honestly left empty); disjoint from Jingzaijiao's salt-field mirror subject.",
    desc_ja="木麻黃の防風林歩道と砂浜の夕日（OSM）。井仔脚とは題材が別。"),
  ]),
 dict(place_id="tw-158", region="tw", slug="gaotaishan-viewpoint", score=None,
  names={"zh-TW": "高台山瞭望台", "en": "Gaotaishan lookout (Jianshi)", "ja": "高台山の展望台",
         "local": "高台山瞭望台"},
  lat=24.6541971, lon=121.2254431, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 高台山（新竹尖石，peak）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E9%AB%98%E5%8F%B0%E5%B1%B1%20%E6%96%B0%E7%AB%B9"],
  admin="新竹縣", category="本島", tags=["mountain", "forest", "starlight"],
  subjects=[
   dict(suffix="P01", template="mountain_view", seasonal=None,
    zh="高台山瞭望那羅溪谷", en="Gaotaishan lookout over the Naluo valley", ja="高台山から那羅渓谷を望む",
    desc_zh="高台山瞭望台俯瞰那羅溪谷與尖石部落群（OSM peak；海拔查無權威源誠實留空）；與既有 tw-130 宇老觀景台（秀巒線埡口）題材錯位——本點為高台山瞭望台主體。",
    desc_en="Lookout-tower view over the Naluo creek valley and Jianshi settlements (OSM peak; elevation honestly left empty); disjoint from the Yulao saddle viewpoint subject.",
    desc_ja="高台山の展望台から那羅渓谷と部落を望む（OSM peak）。宇老とは題材が別。"),
  ]),
 dict(place_id="tw-159", region="tw", slug="huangjinhai-an-tainan", score=None,
  names={"zh-TW": "黃金海岸（台南南區）", "en": "Golden Coast (South District, Tainan)", "ja": "黄金海岸（台南南区）",
         "local": "黃金海岸"},
  lat=22.93175, lon=120.1763, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 黃金海岸（台南南區，bicycle_rental 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E9%BB%83%E9%87%91%E6%B5%B7%E5%B2%B8%20%E5%8F%B0%E5%8D%97"],
  admin="台南市", category="本島", tags=["coast", "city"],
  subjects=[
   dict(suffix="P01", template="sunset", seasonal=None,
    zh="黃金海岸夕照", en="Golden Coast sunset", ja="黄金海岸の夕映え",
    desc_zh="台南市區南緣黃金海岸沙灘夕照與市燈同框（OSM 節點；海拔查無權威源誠實留空）；與既有 tw-142 安平漁人碼頭（港灣大魚裝置）題材錯位——本點為市郊沙灘線。",
    desc_en="Beach sunset with city lights behind, on Tainan's southern coastal edge (OSM node; elevation honestly left empty); disjoint from Anping wharf's harbour-art subject.",
    desc_ja="台南南区の砂浜と夕日と街灯（OSM）。安平漁人碼頭とは題材が別。"),
  ]),
 dict(place_id="tw-160", region="tw", slug="jiangjia-gucuo", score=None,
  names={"zh-TW": "三水江家古厝", "en": "Jiang Family Historic Settlement (Sanshui)", "ja": "江家古厝",
         "local": "江家古厝"},
  lat=24.8714710, lon=121.1650046, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 江家古厝（台南楠西，house 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E6%B1%9F%E5%AE%B6%E5%8F%A4%E5%8E%9D"],
  admin="台南市", category="本島", tags=["mountain", "forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="江家古厝聚落與山景展望", en="Jiang settlement and mountain outlook", ja="江家集落と山並みの展望",
    desc_zh="楠西三水江家古厝閩客傳統聚落群與周邊山景田野（OSM house 節點；海拔查無權威源誠實留空）；清單主題的花卉季窗（ginkgo/lupine/chrysanth）查無權威季節源，誠實不建時間窗契約——本契約為聚落與山景展望主體。",
    desc_en="The Hakka-Minnan traditional settlement of Jiangjia Gucuo with surrounding mountain and field views (OSM house node; elevation honestly left empty). The list's flower-season window (ginkgo/lupine/chrysanth) has no authoritative seasonal source, so no time-window contract is built - honestly.",
    desc_ja="楠西・江家古厝の伝統集落と周辺の山並み（OSM house ノード）。花卉の季節窓は権威源がなく誠実に不構築。"),
  ]),
 dict(place_id="tw-161", region="tw", slug="zhongjiao-wan", score=None,
  names={"zh-TW": "中角灣/沙珠灣", "en": "Zhongjiao Bay / Shazhu Bay (Jinshan)", "ja": "中角湾／沙珠湾",
         "local": "中角灣"},
  lat=25.2389990, lon=121.6323619, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 中角灣（新北金山，bicycle_rental 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E4%B8%AD%E8%A7%92%E7%81%A3"],
  admin="新北市", category="本島", tags=["coast"],
  subjects=[
   dict(suffix="P01", template="sunset", seasonal=None,
    zh="中角灣沙灘夕照", en="Zhongjiao Bay beach sunset", ja="中角湾の夕映え",
    desc_zh="金山中角灣弧形沙灘面向西北海平面的夕照（OSM 節點；海拔查無權威源誠實留空）；與既有 tw-074 野柳地質公園（蕈狀岩地質）題材錯位。",
    desc_en="Crescent beach sunset toward the NW sea horizon at Zhongjiao Bay, Jinshan (OSM node; elevation honestly left empty); disjoint from Yehliu's mushroom-rock geology subject.",
    desc_ja="金山中角湾の砂浜と北西水平線の夕日（OSM）。野柳とは題材が別。"),
  ]),
]

REJECTED_PLACES = [
    ("風吹砂珊瑚礁懸崖", "same-family overlap: 2.23km from tw-076 龍磐公園／草原海岸 (coastal reef cliff family)"),
    ("八斗子潮境公園海蝕平台", "same-family overlap: 0.66km from tw-009 望幽谷"),
    ("墾丁白沙灣", "same-family overlap: 3.15km from tw-030 屏東關山 (白砂灣夕照同關山夕照題材)"),
    ("對高岳觀景台", "same-family overlap: 1.20km from tw-024 阿里山祝山觀日平台"),
    ("滿月圓森林遊樂區", "same-family overlap: 3.39km from tw-144 東眼山國家森林遊樂區三角點"),
    ("漁光島月牙灣", "same-family overlap: 2.08km from tw-142 安平漁人碼頭/大魚的祝福"),
    ("石門山", "same-family overlap: 1.74km from tw-019 合歡山主峰"),
    ("船帆石+龍磐高位珊瑚礁", "same-family overlap: 2.51km from tw-076 龍磐公園／草原海岸"),
    ("西子灣/柴山海岸", "same-family overlap: 2.20km from tw-028 駁二藝術特區 (高雄港灣夕照家族)"),
    ("阿里山慈雲寺觀景台", "same-family overlap: 1.66km from tw-024 阿里山祝山觀日平台"),
    ("鳥嘴山大竹山農場", "same-family overlap: 3.03km from tw-131 山上人家農場"),
    ("三仙山西濱海蝕平台", "same-family overlap: 1.00km from tw-038 三仙台 (identical existing place)"),
    ("二尖山爽文嶺", "same-family overlap: 2.05km from tw-133 集集大山轉播站"),
    ("八仙山主峰", "same-family overlap: 3.25km from tw-087 大雪山森林遊樂區43K觀景台"),
    ("三條崙海水浴場", "pure swimming beach exclusion (owner rules)"),
]


def wb(p, text): return m66.wb(p, text)


def build_contract(p, subj):
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
    existing = R.get_spots("tw")  # already includes tw-125..tw-146
    rows = {}
    for p in PLACES:
        dists = sorted((hav(p["lat"], p["lon"], s["lat"], s["lon"])/1000, s["spot_id"],
                        s["name_i18n"]["zh-TW"]) for s in existing)
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
            c = build_contract(p, subj)
            out = cl.DATA / f"{c['opportunity_id']}.json"
            cl.wbytes(out, cl.jdump(c))
            written.append(c["opportunity_id"])
    print("contracts written:", len(written))

    # ---- 2) regions.py ----
    rp = ROOT / "regions.py"
    text = rp.read_bytes().decode("utf-8").replace("\r\n", "\n")
    if '"tw-147"' not in text:
        # anchor: last wave-1 tuple (tw-146) — positional spot_id invariant: wave-2 tuples append AFTER it
        a_tw = ('            (23.0657536, 120.7470591, "藤枝國家森林遊樂區", "Tengjhih National Forest Recreation Area", '
                '"藤枝国家森林遊楽区", "藤枝", "本島", ["forest", "mountain"]),  # CL-DATA-66\n')
        assert a_tw in text, "tw-146 tuple anchor missing"
        lines = []
        for p in PLACES:
            n = p["names"]
            lines.append(
                f'            ({p["lat"]}, {p["lon"]}, "{n["zh-TW"]}", "{n["en"]}", '
                f'"{n["ja"]}", "{n["local"]}", "{p["category"]}", {json.dumps(p["tags"], ensure_ascii=False)}),  # {TICKET}\n')
        text = text.replace(a_tw, a_tw + "".join(lines), 1)
        a_admin = '    "tw-146": ["高雄市"],  # CL-DATA-66\n'
        assert a_admin in text, "admin anchor missing"
        adm = "".join(f'    "{p["place_id"]}": ["{p["admin"]}"],  # {TICKET}\n' for p in PLACES)
        text = text.replace(a_admin, a_admin + adm, 1)
        # elevations: insert the wave-2 block before the wave-1 elevation comment (dict order irrelevant)
        a_elev = '    # CL-DATA-66 wave-1 admission elevations (web-verified 2026-11-11; null elevations omitted honestly)\n'
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

    # ---- 5) web evidence registry (extend wave-1 file) ----
    ev_path = ROOT / "data/v2/audits/cl-data-66_web_evidence.json"
    ev = json.loads(ev_path.read_bytes().decode("utf-8"))
    wave2_places = []
    wave2_evidence = []
    for p in PLACES:
        wave2_places.append({
            "place_id": p["place_id"], "slug": p["slug"], "score": None,
            "lat": p["lat"], "lon": p["lon"], "elev_m": p["elev_m"],
            "coord_confidence": p["coord_conf"], "coord_source": p["coord_source"],
            "sources": p["coord_sources"], "subjects": [s["zh"] for s in p["subjects"]],
            "ticket": TICKET, "wave": WAVE})
        wave2_evidence.append({
            "id": f"e-d66-web-{p['slug']}", "grade": "A" if p["coord_conf"] == "high" else "B",
            "kind": "official_or_wikipedia_or_osm_text",
            "url": p["coord_sources"][0],
            "supports": p["coord_source"],
            "retrieved_at": VER_DATE,
            "limitation": "Coordinate/elevation verified against cited sources; exact tripod position and access not field-surveyed; opening/closure/permit/reservation status follows on-site notices.",
            "ticket": TICKET, "wave": WAVE})
    ev["places_wave2"] = wave2_places
    ev["evidence_wave2"] = wave2_evidence
    ev["places_wave2_count"] = len(wave2_places)
    ev["rejected_wave2_count"] = len(REJECTED_PLACES)
    ev["rule_wave2"] = (f"Scoreless intake wave {WAVE} (owner ruling {VER_DATE}): admission = web verification + "
                        "5km subject-disjoint dedupe; NO rubric v2 gates, NO AGLI dual-board, agli-final "
                        f"untouched; score fields left empty. 15 places admitted (tw-147..tw-161), 15 "
                        "manifest-next-30 candidates rejected (14 same-family <5km overlaps + 1 pure-swimming-beach).")
    wb(ev_path, cl.jdump(ev))
    print("web evidence extended:", len(wave2_places))

    # ---- 6) tier-a manifest wave-2 status update ----
    tm_path = ROOT / "data/v2/audits/subject-lists/tier-a-manifest.json"
    tm = json.loads(tm_path.read_bytes().decode("utf-8"))
    adm_names = {p["names"]["zh-TW"]: p["place_id"] for p in PLACES}
    rej_names = dict(REJECTED_PLACES)
    changed = 0
    for r in tm["tier_a"]:
        if r.get("status") == "admitted" or r.get("status") == "rejected":
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
    print("DONE wave-2 stage-1 build")


if __name__ == "__main__":
    main()
