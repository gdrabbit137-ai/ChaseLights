#!/usr/bin/env python3
"""CL-DATA-66 Wave 1: scoreless intake of 22 Tier-A places (tw-125..tw-146).

Owner rulings (2026-11-11):
- intake is SCORELESS: rubric v2 gates and AGLI dual-board scoring are NOT run;
  agli-final.json untouched; score fields left empty pending the future system.
- admission = web verification (authoritative URL + date) + 5km subject-disjoint
  dedupe (overrides documented in data/v2/audits/discovery/cl-data-66-dedupe.json).
- subject contracts built in full (V2 + legacy dual-track).
Derived from the CL-DATA-51/53/64 pipeline (byte-pinned contracts, honest unknown,
regions.py endpoints, 168h scoped regen splice).
"""
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys_root = str(ROOT)
import sys  # noqa: E402
if sys_root not in sys.path:
    sys.path.insert(0, sys_root)

spec = importlib.util.spec_from_file_location(
    'cl64base', str(ROOT / 'data/v2/tools/discovery/cl_data_64_build.py'))
m64 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m64)
cl = m64.cl

TICKET = "CL-DATA-66"
VER_DATE = "2026-11-11"

PLACES = [
 dict(place_id="tw-125", region="tw", slug="dalunshan-tea-gingko", score=None,
  names={"zh-TW": "大崙山觀光茶園/銀杏森林", "en": "Dalunshan Tea Terraces / Ginkgo Forest",
         "ja": "大崙山茶園／銀杏の森", "local": "大崙山觀光茶園"},
  lat=23.681681, lon=120.766370, elev_m=1300, coord_conf="high",
  coord_source="玩全台灣旅遊網 大崙山觀光茶園 GoogleMap座標 23.681681,120.766370；海拔1250-1500m 帶（南投旅遊網官方頁）",
  coord_sources=["https://nt.okgo.tw/scenic/2936.html",
                 "https://travel.nantou.gov.tw/attractions/dalun-mountain-gingko-forest/"],
  admin="南投縣", category="本島", tags=["mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="cloud_sea", seasonal=None,
    zh="大崙山茶園雲海", en="Dalunshan tea-terrace cloud sea", ja="大崙山茶園の雲海",
    desc_zh="鹿谷高山茶園帶冬季雲海翻湧（南投旅遊網官方：冬天的大崙山雲海更是一絕；海拔1250-1500m）；與既有 tw-104 忘憂森林（森林水鏡）題材錯位——本點為茶園雲海。",
    desc_en="Winter cloud sea rolling over the high-altitude tea terraces of Lugu (Nantou tourism official: the winter cloud sea is the signature); disjoint from Wuyou Forest's mirror-lake subject.",
    desc_ja="鹿谷の高山茶園帯に広がる冬の雲海（南投旅遊網公式）。忘憂森林とは題材が別。"),
   dict(suffix="P02", template="sunrise", seasonal=None,
    zh="大崙山觀霧亭日出", en="Dalunshan dawn over the central ranges", ja="大崙山の日の出",
    desc_zh="觀霧亭展望日出（可遠眺中部五縣市；清晨低溫雲霧最盛）；與同點雲海契約（P01）題材分列。",
    desc_en="Dawn from the Guanwu pavilion overlooking five central counties; cold early mornings give the richest mist.",
    desc_ja="観霧亭から望む日の出。中部五県市を一望。"),
  ]),
 dict(place_id="tw-126", region="tw", slug="nanshansi-xianguangmiao", score=None,
  names={"zh-TW": "坪林南山寺仙公廟", "en": "Nanshan Temple (Xianguangmiao), Pinglin",
         "ja": "坪林南山寺仙公廟", "local": "南山寺仙公廟"},
  lat=24.9675371, lon=121.7272531, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 南山寺（坪林漁光里樟空子路）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E5%9D%AA%E6%9E%97%20%E5%8D%97%E5%B1%B1%E5%AF%BA"],
  admin="新北市", category="本島", tags=["mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="city_night", seasonal=None,
    zh="仙公廟北勢溪谷夜景", en="Night view over the Beishi river valley", ja="仙公廟の北勢渓谷夜景",
    desc_zh="廟前眺望北勢溪谷與坪林市區夜燈（UDN/部落格列名夜景點；海拔查無權威源誠實留空）；與既有 坪林茶業博物館等日間茶鄉點題材錯位。",
    desc_en="Temple-front lookout over the Beishi river valley and Pinglin town lights (listed night-view spot; elevation honestly left empty - no authoritative source).",
    desc_ja="北勢渓谷と坪林市街の灯り（夜景点）。標高は未確認のため誠実に空欄。"),
  ]),
 dict(place_id="tw-127", region="tw", slug="xianshan-lingdonggong", score=None,
  names={"zh-TW": "仙山靈洞宮後山", "en": "Xianshan (Lingdong Temple back hill)",
         "ja": "仙山霊洞宮の後山", "local": "仙山靈洞宮"},
  lat=24.5415154, lon=120.9503730, elev_m=967, coord_conf="medium",
  coord_source="OSM Nominatim 協靈宮（仙山登山步道，獅潭新店村）；海拔967m（交通部觀光署多媒體開放資料：仙山海拔967公尺）",
  coord_sources=["https://media.taiwan.net.tw/en-us/portal/travel/details/attraction_376450000a_000123"],
  admin="苗栗縣", category="本島", tags=["mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="cloud_sea", seasonal=None,
    zh="仙山雲霧仙境", en="Xianshan cloud-mist sea", ja="仙山の雲霧",
    desc_zh="仙山終年雲霧繚繞「飄飄渺渺頗富仙境意味」（交通部觀光署多媒體開放資料官方口徑；海拔967m）；與既有 tw-119 加里山（山容展望）題材錯位——本點為雲霧主體。",
    desc_en="Xianshan is wrapped in drifting cloud-mist year round ('fairyland' wording from the official tourism open data; 967 m); disjoint from Chiali-shan's ridge-view subject.",
    desc_ja="仙山は年間を通して雲霧が漂う（観光署オープンデータ公式、標高967m）。加里山とは題材が別。"),
  ]),
 dict(place_id="tw-128", region="tw", slug="moyanshan-liuli", score=None,
  names={"zh-TW": "墨硯山琉璃光", "en": "Moyanshan liuli-glow night", "ja": "墨硯山の琉璃光",
         "local": "墨硯山"},
  lat=24.5558111, lon=120.8462730, elev_m=157, coord_conf="high",
  coord_source="OSM Nominatim 墨硯山南峰；海拔約157m（健行筆記/vocus 攻略）",
  coord_sources=["https://vocus.cc/article/6a7aea79fd89780001f282f4"],
  admin="苗栗縣", category="本島", tags=["city", "starlight"],
  subjects=[
   dict(suffix="P01", template="city_night", seasonal=None,
    zh="墨硯山苗栗琉璃光", en="Moyanshan glowing city lights (liuli)", ja="墨硯山の苗栗夜景",
    desc_zh="山頂平臺俯瞰苗栗市區燈海與後龍溪畔夜霧（攝影社群列名琉璃光/夜景點；海拔157m）；與既有 苗栗點題材錯位——本點為市街琉璃光主體。",
    desc_en="Summit platform over the Miaoli city light-sea (a photographer-listed liuli-glow/night spot; 157 m).",
    desc_ja="山頂から苗栗市街の灯りを望む（琉璃光・夜景点、標高157m）。"),
  ]),
 dict(place_id="tw-129", region="tw", slug="jiangziliao-shan", score=None,
  names={"zh-TW": "姜子寮山觀景台", "en": "Jiangziliao Mountain viewing platform",
         "ja": "姜子寮山の展望台", "local": "姜子寮山"},
  lat=25.0532780, lon=121.7301100, elev_m=729, coord_conf="high",
  coord_source="zh.wikipedia 姜子寮山（25°03′11.8″N 121°43′48.4″E；海拔729m，小百岳）",
  coord_sources=["https://zh.wikipedia.org/wiki/%E5%A7%9C%E5%AD%90%E5%AF%AE%E5%B1%B1"],
  admin="基隆市", category="本島", tags=["mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="sunrise", seasonal=None,
    zh="姜子寮山四面觀景台日出", en="Jiangziliao sunrise from the 4-way platform", ja="姜子寮山の日の出",
    desc_zh="山頂四方皆設觀景台（南望平溪三尖、北望五指山系與基隆嶼；zh.wikipedia；海拔729m）；與既有 基隆港夜景點題材錯位。",
    desc_en="Four viewing platforms on the summit - Pingxi peaks to the south, Wuzhi range and Keelung Isle to the north (zh.wikipedia; 729 m).",
    desc_ja="山頂の四方に展望台（標高729m）。基隆港夜景とは題材が別。"),
   dict(suffix="P02", template="city_night", seasonal=None,
    zh="姜子寮山基隆嶼夜眺", en="Jiangziliao night: Keelung Isle lights", ja="姜子寮山の夜の基隆嶼",
    desc_zh="晴夜北面可見基隆嶼與港區燈光（部落格/小百岳資料）；與同點日出契約分列。",
    desc_en="On clear nights the Keelung Isle and harbor lights are visible to the north; separate from the sunrise contract.",
    desc_ja="晴天の夜は北に基隆嶼と港の灯り。日の出契約とは別。"),
  ]),
 dict(place_id="tw-130", region="tw", slug="yulao-guanjingtai", score=None,
  names={"zh-TW": "宇老觀景台", "en": "Yulao viewing platform (Jianshi)",
         "ja": "宇老観景台", "local": "宇老觀景台"},
  lat=24.6675183, lon=121.2820376, elev_m=1450, coord_conf="high",
  coord_source="OSM Nominatim 宇老觀景台（新竹60縣道20K）；海拔1450m（新竹尖石原住民文化館/拉美公司資料）",
  coord_sources=["https://lcm.tacp.gov.tw/index.php?inter=info&category=3&museum=26&menu=tours&did=70"],
  admin="新竹縣", category="本島", tags=["mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="cloud_sea", seasonal=None,
    zh="宇老前後山雲海分界", en="Yulao cloud sea at the front/back mountain divide", ja="宇老の雲海",
    desc_zh="尖石前後山分界（海拔1450m），東望玉峰村深谷、西望那羅溪谷，雲海翻越鞍部（新竹縣原民館資料）；與既有 尖石點題材錯位。",
    desc_en="The divide between Jianshi's front and back mountains (1,450 m); cloud seas roll over the saddle; disjoint from other Jianshi subjects.",
    desc_ja="尖石前山・後山の分界（標高1450m）。雲海が鞍部を越える。"),
   dict(suffix="P02", template="city_night", seasonal=None,
    zh="宇老夜景", en="Yulao night view", ja="宇老の夜景",
    desc_zh="「天氣晴朗的夜晚，更是觀賞夜景的絕佳地點」（新竹縣尖石鄉原住民文化館官方資料）；與同點雲海契約分列。",
    desc_en="'On clear nights an excellent night-view spot' (official Jianshi cultural-museum note); separate from the cloud-sea contract.",
    desc_ja="「晴れた夜は夜景の絶好地」（新竹県尖石郷公式資料）。"),
  ]),
 dict(place_id="tw-131", region="tw", slug="shanshangrenjia-farm", score=None,
  names={"zh-TW": "山上人家農場", "en": "Shanshang Renjia Forest Farm", "ja": "山上人家森林農場",
         "local": "山上人家森林農場"},
  lat=24.6047, lon=121.0890, elev_m=1200, coord_conf="medium",
  coord_source="iot-sky 開放資料（經度121.089 緯度24.6047）＋交通部觀光署多媒體開放資料（海拔約1200m）",
  coord_sources=["https://www.iot-sky.com/iot/scenicspot?sel_city=%E6%96%B0%E7%AB%B9%E7%B8%A3",
                 "https://media.taiwan.net.tw/zh-tw/portal/travel/details/attraction_376440000a_000159"],
  admin="新竹縣", category="本島", tags=["mountain", "forest", "starlight"],
  subjects=[
   dict(suffix="P01", template="cloud_sea", seasonal=None,
    zh="山上人家雲海", en="Shanshang Renjia cloud sea", ja="山上人家の雲海",
    desc_zh="海拔約1200m 農場環抱雲海（交通部觀光署多媒體開放資料/UDN：觀雲海、看日出；鄰參山國家風景區與鵝公髻山）；與既有 新竹點題材錯位。",
    desc_en="Cloud seas surround the farm at ~1200 m (official tourism open data / UDN: cloud sea and sunrise); disjoint from other Hsinchu subjects.",
    desc_ja="標高約1200mの農場を囲む雲海（観光署オープンデータ）。"),
   dict(suffix="P02", template="sunrise", seasonal=None,
    zh="山上人家日出", en="Shanshang Renjia sunrise", ja="山上人家の日の出",
    desc_zh="農場向東日出展望（UDN 橘世代列名「觀星、觀雲海、看日出」）；與同點雲海契約分列。",
    desc_en="East-facing sunrise outlook (UDN: star-gazing, cloud sea and sunrise); separate from the cloud-sea contract.",
    desc_ja="東向きの日の出展望。"),
  ]),
 dict(place_id="tw-132", region="tw", slug="erge-shan", score=None,
  names={"zh-TW": "石門二格山觀景台", "en": "Ergeshan viewing platform (Shiding)",
         "ja": "二格山の展望台", "local": "二格山"},
  lat=24.9672358, lon=121.6196361, elev_m=678, coord_conf="medium",
  coord_source="OSM Nominatim 二格山（石碇格頭里）；海拔678m（zh.wikipedia 二格山，小百岳）",
  coord_sources=["https://zh.wikipedia.org/zh-cn/%E4%BA%8C%E6%A0%BC%E5%B1%B1"],
  admin="新北市", category="本島", tags=["mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="city_night", seasonal=None,
    zh="二格山台北盆地夜眺", en="Ergeshan night over the Taipei basin", ja="二格山の夜景",
    desc_zh="峰頂觀景平台展望台北盆地夜燈（zh.wikipedia：可展望臨近地區；海拔678m）；與既有 石碇點題材錯位。",
    desc_en="Summit platform over the Taipei basin night lights (zh.wikipedia; 678 m); disjoint from other Shiding subjects.",
    desc_ja="山頂展望台から台北盆地の夜景（標高678m）。"),
   dict(suffix="P02", template="sunrise", seasonal=None,
    zh="二格山日出", en="Ergeshan sunrise", ja="二格山の日の出",
    desc_zh="峰頂平台日出展望（小百岳登頂路線；與同點夜景契約分列）。",
    desc_en="Summit sunrise outlook; separate from the night contract.",
    desc_ja="山頂からの日の出。"),
  ]),
 dict(place_id="tw-133", region="tw", slug="jiji-dashan", score=None,
  names={"zh-TW": "集集大山轉播站", "en": "Jiji Dashan broadcast-station viewpoint",
         "ja": "集集大山の中継局展望", "local": "集集大山"},
  lat=23.8548610, lon=120.8380600, elev_m=1392, coord_conf="high",
  coord_source="zh.wikipedia 集集大山（23°51′17.5″N 120°50′17″E；主峰1,390m；南投旅遊網記1,392m）",
  coord_sources=["https://zh.wikipedia.org/zh-tw/%E9%9B%86%E9%9B%86%E5%A4%A7%E5%B1%B1",
                 "https://travel.nantou.gov.tw/theme-train-trip/"],
  admin="南投縣", category="本島", tags=["mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="city_night", seasonal=None,
    zh="集集大山日月潭夜景", en="Jiji Dashan night over Sun-Moon Lake", ja="集集大山の日月潭夜景",
    desc_zh="山頂眺望台遠眺日月潭與濁水溪谷夜燈（南投旅遊網官方：山頂的眺望台坐擁山光水色）；與既有 日月潭湖畔點題材錯位——本點為高山俯視夜景。",
    desc_en="Summit lookout over Sun-Moon Lake and the Zhuoshui valley by night (Nantou tourism official); disjoint from lakeside subjects.",
    desc_ja="山頂から日月潭と濁水渓谷の夜景（南投旅遊網公式）。湖畔対象とは題材が別。"),
   dict(suffix="P02", template="cloud_sea", seasonal=None,
    zh="集集大山雲海", en="Jiji Dashan cloud sea", ja="集集大山の雲海",
    desc_zh="海拔1,392m 峰頂雲海（zh.wikipedia/南投旅遊網；與同點夜景契約分列）。",
    desc_en="Cloud sea on the 1,392 m summit; separate from the night contract.",
    desc_ja="標高1392mの雲海。"),
  ]),
 dict(place_id="tw-134", region="tw", slug="guanjing-1314", score=None,
  names={"zh-TW": "1314觀景台", "en": "1314 Observation Deck (Meishan Ruifeng)",
         "ja": "1314観景台", "local": "1314觀景台"},
  lat=23.5595320, lon=120.6789157, elev_m=1314, coord_conf="high",
  coord_source="OSM Nominatim 海鼠山（嘉義梅山）＋阿里山國家風景區管理處官方（海鼠山最高點海拔1,311m＋觀景台=1,314m）",
  coord_sources=["https://www.ali-nsa.net/zh-tw/attractions/detail/242"],
  admin="嘉義縣", category="本島", tags=["mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="cloud_sea", seasonal=None,
    zh="1314觀景台茶園雲海", en="1314 deck cloud sea over tea terraces", ja="1314観景台の茶園雲海",
    desc_zh="海鼠山最高點360度展望，飽覽綿延茶園與雲海（阿里山國家風景區管理處官方：晴朗時眺望周邊縣市）；與既有 tw-105 太平雲梯（橋梁地標，4.9km 外）題材錯位。",
    desc_en="360-degree summit deck over endless tea terraces and cloud seas (Alishan NSB official); disjoint from the Taiping suspension-bridge landmark 4.9 km away.",
    desc_ja="360度の展望から茶園と雲海（阿里山國家風景區官方）。太平吊橋とは題材が別。"),
   dict(suffix="P02", template="city_night", seasonal=None,
    zh="1314觀景台嘉義夜景", en="1314 deck Chiayi night view", ja="1314観景台の夜景",
    desc_zh="「夜晚還能看見嘉義市區夜景，亦是觀賞阿里山日出的好去處」（阿里山風管處官方婚拍頁）；與同點雲海契約分列。",
    desc_en="'At night the Chiayi city lights appear; also a good sunrise spot' (Alishan NSB official); separate from the cloud-sea contract.",
    desc_ja="夜は嘉義市街の夜景（阿里山風管処公式）。"),
  ]),
 dict(place_id="tw-135", region="tw", slug="wufenshan-radar", score=None,
  names={"zh-TW": "五分山雷達站", "en": "Wufenshan Weather Radar Station", "ja": "五分山気象レーダー站",
         "local": "五分山雷達站"},
  lat=25.07278, lon=121.77278, elev_m=740, coord_conf="high",
  coord_source="中央氣象署官方站況頁（東經121.77305 北緯25.07305 海拔740m）＋zh.wikipedia 五分山氣象雷達站",
  coord_sources=["https://www.cwa.gov.tw/V8/C/A/organ/46685.html",
                 "https://zh.wikipedia.org/wiki/%E4%BA%94%E5%88%86%E5%B1%B1%E6%B0%A3%E8%B1%A1%E9%9B%B7%E9%81%94%E7%AB%99"],
  admin="新北市", category="本島", tags=["mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="city_night", seasonal=None,
    zh="五分山雷達站夜景", en="Wufenshan radar-station night view", ja="五分山レーダー站の夜景",
    desc_zh="山頂球體雷達站與基隆河谷燈海夜景（攝影社群列名；海拔740m——CWA 官方）；雷達站設施本身為管制區，僅步道/外圍合法拍攝——access 記錄不計分。",
    desc_en="The white radar dome against the Keelung river-valley lights at night (740 m per CWA official); the station compound is restricted - shoot only from the trail/surroundings (access note, not scored).",
    desc_ja="山頂のレーダードームと基隆河谷の灯り（標高740m、CWA公式）。敷地は立入制限。"),
   dict(suffix="P02", template="sunrise", seasonal=None,
    zh="五分山日出", en="Wufenshan sunrise", ja="五分山の日の出",
    desc_zh="山頂步道日出展望（五分山為平溪最高點；與同點夜景契約分列）。",
    desc_en="Summit-trail sunrise (Wufenshan is Pingxi's high point); separate from the night contract.",
    desc_ja="山頂からの日の出。"),
  ]),
 dict(place_id="tw-136", region="tw", slug="huxiao-shanzhuang", score=None,
  names={"zh-TW": "埔里虎頭山虎嘯山莊", "en": "Huxiao Farm, Hutoushan (Puli)", "ja": "虎嘯山荘（埔里虎頭山）",
         "local": "虎嘯山莊"},
  lat=23.964167, lon=120.9899440, elev_m=650, coord_conf="medium",
  coord_source="虎嘯山莊官方對位座標 N23°57′51 E120°59′24（easycamp 登錄）＋ddnews（虎頭山約650m）",
  coord_sources=["https://m-news.easycamp.com.tw/km/km_doc/2686", "https://ddnews.com.tw/5792/"],
  admin="南投縣", category="本島", tags=["mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="city_night", seasonal=None,
    zh="虎嘯山莊埔里盆地百萬夜景", en="Huxiao night over the Puli basin", ja="虎嘯山荘の埔里盆地夜景",
    desc_zh="俯瞰埔里盆地燈海「百萬夜景」（ddnews/easycamp 官方登錄；海拔約650m）；飛行傘活動時段注意——access 記錄；與既有 埔里點題材錯位。",
    desc_en="Overlooking the Puli basin light-sea ('million-dollar night view', official listings; ~650 m); paragliding activity hours noted - access informational; disjoint from other Puli subjects.",
    desc_ja="埔里盆地の灯りを一望（公式登錄、標高約650m）。"),
   dict(suffix="P02", template="cloud_sea", seasonal=None,
    zh="虎頭山雲霧盆景", en="Hutoushan mist over the basin", ja="虎頭山の雲霧",
    desc_zh="雨後清晨盆地雲霧（攝影社群紀錄；與同點夜景契約分列）。",
    desc_en="Post-rain morning mist over the basin (photographer records); separate from the night contract.",
    desc_ja="雨上りの朝、盆地に広がる雲霧。"),
  ]),
 dict(place_id="tw-137", region="tw", slug="baoshi-shan", score=None,
  names={"zh-TW": "報時山觀景台", "en": "Baoshishan viewing platform (Jinguashi)",
         "ja": "報時山の展望台", "local": "報時山"},
  lat=25.1136611, lon=121.8596306, elev_m=295, coord_conf="high",
  coord_source="zh.wikipedia 報時山（25°6′49.18″N 121°51′34.67″E；海拔295m；新北觀光局記260m 為步道口帶——取山頂295m 並註記）",
  coord_sources=["https://zh.wikipedia.org/wiki/%E5%A0%B1%E6%99%82%E5%B1%B1",
                 "https://newtaipei.travel/zh-tw/attractions/detail/402695"],
  admin="新北市", category="本島", tags=["coast", "starlight"],
  subjects=[
   dict(suffix="P01", template="sunset", seasonal=None,
    zh="報時山陰陽海日落", en="Baoshishan sunset over the yin-yang sea", ja="報時山の陰陽海と夕日",
    desc_zh="步道十分鐘登頂，觀景平台眺望水湳洞陰陽海與基隆山（新北觀光局官方）；全台最短海觀步道——步道距離 access 不計分；與既有 tw-072 南雅奇岩（蕈狀岩地質）題材錯位——本點為海灣日落。",
    desc_en="A ten-minute stair trail to the platform over the Yin-Yang Sea and Mt Keelung (New Taipei official; shortest sea-view trail in Taiwan - trail distance not scored); disjoint from Nanya's mushroom-rock geology.",
    desc_ja="十分で登れる展望台から陰陽海と基隆山（新北観光局公式）。南雅奇岩とは題材が別。"),
   dict(suffix="P02", template="city_night", seasonal=None,
    zh="報時山金瓜石夜眺", en="Baoshishan Jinguashi night", ja="報時山の夜",
    desc_zh="夜間俯瞰金瓜石/水湳洞聚落燈火（攝影社群紀錄；與同點日落契約分列）。",
    desc_en="Night look down at the Jinguashi/Shuinan village lights; separate from the sunset contract.",
    desc_ja="金瓜石・水湳洞の集落の灯り。"),
  ]),
 dict(place_id="tw-138", region="tw", slug="datongshan-qinglongling", score=None,
  names={"zh-TW": "大同山/青龍嶺", "en": "Datongshan / Qinglongling (Shulin)", "ja": "大同山・青龍嶺",
         "local": "大同山/青龍嶺"},
  lat=25.0033630, lon=121.4032140, elev_m=256, coord_conf="high",
  coord_source="台灣66 全景資料（座標 25.003363, 121.403214；青龍嶺海拔約256m）＋新北觀光局（大同山237m）",
  coord_sources=["https://www.taiwan66.com.tw/panoramas/detail/570",
                 "https://newtaipei.travel/zh-tw/attractions/detail/110604"],
  admin="新北市", category="本島", tags=["city", "starlight"],
  subjects=[
   dict(suffix="P01", template="city_night", seasonal=None,
    zh="青龍嶺大台北夜眺", en="Qinglongling night over greater Taipei", ja="青龍嶺の夜景",
    desc_zh="觀景台眺望大台北盆地與新海橋燈帶（台灣66/新北觀光局；海拔約256m）；與既有 樹林點題材錯位。",
    desc_en="Platform over the Taipei basin and bridge light-lines (256 m); disjoint from other Shulin subjects.",
    desc_ja="台北盆地の夜景（標高約256m）。"),
   dict(suffix="P02", template="sunset", seasonal=None,
    zh="大同山夕照", en="Datongshan sunset", ja="大同山の夕日",
    desc_zh="西向盆地夕照（與同點夜景契約分列）。",
    desc_en="West-facing basin sunset; separate from the night contract.",
    desc_ja="西向きの夕日。"),
  ]),
 dict(place_id="tw-139", region="tw", slug="waimushan-coast", score=None,
  names={"zh-TW": "大武崙白沙灘/外木山", "en": "Waimushan coastal belt (Dawulun)",
         "ja": "外木山海濱（大武崙）", "local": "大武崙白沙灘/外木山"},
  lat=25.1568, lon=121.7056, elev_m=231, coord_conf="high",
  coord_source="1968 開放資料 大武崙砲台（經度121.7056 緯度25.1568）＋基隆市文化局（大武崙山標高231m）；本點主題為外木山濱海大道日落海岸帶（非戲水）",
  coord_sources=["https://www.1968services.tw/travel/C1_A15011000H_000152",
                 "https://camera.klcg.gov.tw/node/727"],
  admin="基隆市", category="本島", tags=["coast", "starlight"],
  subjects=[
   dict(suffix="P01", template="sunset", seasonal=None,
    zh="外木山濱海日落大道", en="Waimushan coastal-belt sunset", ja="外木山の海浜サンセット",
    desc_zh="基隆最長天然海岸線（約5km）濱海大道西向日落，礁岩海岸與基隆嶼海景（基隆市文化局/NMMST 官方帶狀描述）；戲水沙灘非本點主題——本點為日落海岸帶。",
    desc_en="Keelung's longest natural coast (~5 km) with a west-facing sunset over reef shores and Keelung Isle (city culture bureau / NMMST); the swimming beach is not the subject - the sunset coast belt is.",
    desc_ja="基隆最長の天然海岸帯（約5km）の夕日。遊泳ビーチではなく夕景海岸が主題。"),
  ]),
 dict(place_id="tw-140", region="tw", slug="taipingshan-forest", score=None,
  names={"zh-TW": "太平山森林遊樂區", "en": "Taipingshan National Forest Recreation Area",
         "ja": "太平山国家森林遊楽区", "local": "太平山"},
  lat=24.5242406, lon=121.6228895, elev_m=1950, coord_conf="medium",
  coord_source="OSM Nominatim 太平山國家森林遊樂區；太平山帶海拔1,950-2,000m（林業保育署太平山官方頁/TPS）",
  coord_sources=["https://yilan.forest.gov.tw/Forest/area",
                 "https://tps.forest.gov.tw/TPSWeb/wSite/ct?xItem=3740&ctNode=309"],
  admin="宜蘭縣", category="本島", tags=["forest", "mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="cloud_sea", seasonal=None,
    zh="太平山雲海", en="Taipingshan cloud sea", ja="太平山の雲海",
    desc_zh="海拔2000m 林場雲海（林業保育署官方：海拔2000公尺的太平山；1915 年伐木起家、1983 年轉型遊樂區）；與既有 tw-088 翠峰湖環山步道（湖景，1.9km 外）題材錯位——本點為林場雲海主體。",
    desc_en="Cloud sea over the 2,000 m former logging landmark (Forestry Bureau official); disjoint from the Cueifong Lake loop subject 1.9 km away.",
    desc_ja="標高2000mの林場の雲海（林業保育署公式）。翠峰湖とは題材が別。"),
   dict(suffix="P02", template="night_sky", seasonal=None,
    zh="太平山星空", en="Taipingshan star field", ja="太平山の星空",
    desc_zh="中高海拔暗空星空（攝影社群列名；天文曆條件照 ASTRONOMY_EPHEMERIS_PROFILES 註冊——tw-121..124 教訓）；與同點雲海契約分列。",
    desc_en="Mid-altitude dark-sky star field; astronomy-ephemeris condition registered in ASTRONOMY_EPHEMERIS_PROFILES (per the tw-121..124 lesson); separate from the cloud-sea contract.",
    desc_ja="中高海拔の暗い空の星野。天文暦条件は ASTRONOMY_EPHEMERIS_PROFILES に註冊。"),
  ]),
 dict(place_id="tw-141", region="tw", slug="aowanda-maple-trail", score=None,
  names={"zh-TW": "奧萬大楓林步道", "en": "Aowanda maple trail", "ja": "奥万大の楓林古道",
         "local": "奧萬大楓林步道"},
  lat=23.9489652, lon=121.1875001, elev_m=1100, coord_conf="medium",
  coord_source="OSM Nominatim 奧萬大國家森林遊樂區；園區海拔1,100-2,600m（南投旅遊網/林業保育署）——楓林區帶取1,100m",
  coord_sources=["https://travel.nantou.gov.tw/article/%E5%A5%A7%E8%90%AC%E5%A4%A7%E6%A5%93%E8%91%89/"],
  admin="南投縣", category="本島", tags=["forest", "mountain"],
  subjects=[
   dict(suffix="P01", template="seasonal_plant", seasonal="red_maple",
    zh="奧萬大楓紅", en="Aowanda red-maple foliage", ja="奥万大の紅葉",
    desc_zh="萬大溪旁楓林區紅葉（南投旅遊網官方：楓林步道位於萬大溪旁，通往楓林區；園區1,100-2,600m）；沿用 seasonal-calendar 既有 red_maple 窗（10-20..11-10）；與既有 奧萬大既有點（若有）題材錯位——本點為楓紅主體。",
    desc_en="Red maples along the maple trail by the Wanda creek (Nantou official; park 1,100-2,600 m); reuses the existing seasonal-calendar red_maple window (10-20..11-10).",
    desc_ja="万大渓沿いの楓林の紅葉（公式）。red_maple 季節窓を再利用。"),
  ]),
 dict(place_id="tw-142", region="tw", slug="anping-fisherman-wharf", score=None,
  names={"zh-TW": "安平漁人碼頭/大魚的祝福", "en": "Anping Fisherman's Wharf / The Blessing of the Big Fish",
         "ja": "安平漁人碼頭／大魚的祝福", "local": "安平漁人碼頭"},
  lat=22.9965428, lon=120.1637900, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 安平漁人碼頭（安億路）＋台南市政府（大魚的祝福裝置藝術）；海拔查無獨立權威值誠實留空",
  coord_sources=["https://www.tainan.gov.tw/News_Content.aspx?n=13371&s=3737144"],
  admin="台南市", category="本島", tags=["coast", "city"],
  subjects=[
   dict(suffix="P01", template="sunset", seasonal=None,
    zh="安平漁人碼頭夕照大魚", en="Anping wharf sunset with the whale installation", ja="安平漁人碼頭の夕景",
    desc_zh="港灣夕陽染金與「大魚的祝福」鯨魚裝置（台南市政府官方：長23m 寬10m 高8m、448 片手工釉燒玻璃）；與既有 tw-110 四草綠色隧道（紅樹林水道，3.8km 外）題材錯位。",
    desc_en="Golden harbor sunset beside 'The Blessing of the Big Fish' whale installation (Tainan City official: 23x10x8 m, 448 glass tiles); disjoint from the Sicao green-tunnel mangrove subject 3.8 km away.",
    desc_ja="港湾の夕日と鯨のアート「大魚的祝福」（台南市政府公式）。四草とは題材が別。"),
   dict(suffix="P02", template="city_night", seasonal=None,
    zh="安平港夜景", en="Anping harbor night", ja="安平港の夜景",
    desc_zh="港區夜燈與裝置藝術夜貌（攝影社群紀錄；與同點日落契約分列）。",
    desc_en="Harbor lights and the installation at night; separate from the sunset contract.",
    desc_ja="港の灯りと夜のアート。"),
  ]),
 dict(place_id="tw-143", region="tw", slug="fuguijiao-windstone", score=None,
  names={"zh-TW": "富貴角風稜石", "en": "Fuguijiao wind-cut stones", "ja": "富貴角の風稜石",
         "local": "富貴角風稜石"},
  lat=25.298217, lon=121.5365830, elev_m=None, coord_conf="high",
  coord_source="交通部航港局 富貴角燈塔官方（WGS84 北緯25°17.893′ 東經121°32.195′）；海拔誠實留空",
  coord_sources=["https://www.motcmpb.gov.tw/Lighthouse/Detail/5a18876c-1af2-4829-b171-a7143063eec2?SiteId=1"],
  admin="新北市", category="本島", tags=["coast", "geology"],
  subjects=[
   dict(suffix="P01", template="sunset", seasonal=None,
    zh="富貴角岬角日落", en="Fuguijiao cape sunset", ja="富貴角の夕日",
    desc_zh="台灣本島最北岬角燈塔與海蝕礁岩日落（航港局燈塔官方頁；與既有 tw-073 老梅綠石槽（季節性石槽，1km 外）題材錯位——本點為岬角地質+日落）；與同點地質契約分列。",
    desc_en="Sunset at Taiwan's northernmost cape and lighthouse (Maritime/Port Bureau official); disjoint from Laomei's seasonal green-algae reef subject ~1 km away.",
    desc_ja="台湾本島最北端の岬と灯台の夕日（航港局公式）。老梅緑石槽とは題材が別。"),
   dict(suffix="P02", template="geological_landform", seasonal=None,
    zh="富貴角風稜石群", en="Fuguijiao ventifact boulders", ja="富貴角の風稜石",
    desc_zh="東北季風磨蝕而成的風稜石礫灘（地質主題；與同點日落契約分列）。",
    desc_en="Ventifact (wind-cut) boulder shore shaped by the northeast monsoon; separate from the sunset contract.",
    desc_ja="東北季風が磨いた風稜石の礫浜。"),
  ]),
 dict(place_id="tw-144", region="tw", slug="dongyanshan-tripoint", score=None,
  names={"zh-TW": "東眼山國家森林遊樂區三角點", "en": "Dongyanshan tri-point (Fuxing)",
         "ja": "東眼山国家森林遊楽区の三角点", "local": "東眼山"},
  lat=24.8187490, lon=121.4161228, elev_m=1212, coord_conf="medium",
  coord_source="OSM Nominatim 東眼山國家森林遊樂區；東眼山海拔1,212m（林業保育署官方）",
  coord_sources=["https://www.forest.gov.tw/0000180"],
  admin="桃園市", category="本島", tags=["forest", "mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="cloud_sea", seasonal=None,
    zh="東眼山雲霧柳杉林", en="Dongyanshan cloud-mist over cedar forest", ja="東眼山の雲霧と柳杉林",
    desc_zh="「雲霧繚繞、整齊美麗的柳杉林」登頂海拔1,212m 一覽桃園到大台北（林業保育署官方原文）；與既有 拉拉山等點題材錯位。",
    desc_en="'Cloud-wrapped, neatly planted Japan-cedar forest' up to the 1,212 m summit with views to Taipei (Forestry Bureau official wording); disjoint from Lalashan subjects.",
    desc_ja="「雲霧に包まれた柳杉林」、標高1212mから桃園〜台北を一望（林業保育署公式）。"),
   dict(suffix="P02", template="night_sky", seasonal=None,
    zh="東眼山星空", en="Dongyanshan star field", ja="東眼山の星空",
    desc_zh="森林遊樂區高點星空（攝影社群列名；天文曆條件照 ASTRONOMY_EPHEMERIS_PROFILES 註冊）；與同點雲霧契約分列。",
    desc_en="Star field at the forest-park high point; astronomy-ephemeris condition registered in ASTRONOMY_EPHEMERIS_PROFILES; separate from the cloud-mist contract.",
    desc_ja="森林遊楽区高點の星空。天文暦条件は ASTRONOMY_EPHEMERIS_PROFILES に註冊。"),
  ]),
 dict(place_id="tw-145", region="tw", slug="donghua-shengong", score=None,
  names={"zh-TW": "東華聖宮", "en": "Donghua Shengong temple night", "ja": "東華聖宮",
         "local": "東華聖宮"},
  lat=24.9379719, lon=121.5198804, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 東華聖宮（新店華城里）＋廟宇登錄——知名琉璃光/百萬夜景點為新店東華聖宮（mook/欣傳媒列名）；候選清單 region 欄『南投魚池』疑為誤植，座標以新店東華聖宮對位；海拔誠實留空",
  coord_sources=["https://www.mook.com.tw/article/16620",
                 "https://www.bazicopy.com/Gods/%E6%9D%B1%E8%8F%AF%E5%B8%9D%E5%90%9B/"],
  admin="新北市", category="本島", tags=["city", "starlight"],
  subjects=[
   dict(suffix="P01", template="city_night", seasonal=None,
    zh="東華聖宮琉璃光夜景", en="Donghua temple liuli-glow night", ja="東華聖宮の琉璃光夜景",
    desc_zh="廟前俯瞰台北盆地燈海，雨後琉璃光名點（mook 全台五大百萬夜景列名；與既有 tw-007 碧潭（橋梁親水，2.6km 外）題材錯位；海拔誠實留空）。",
    desc_en="Temple-front overlook of the Taipei basin light-sea, a famous post-rain liuli-glow spot (mook 'top five million-dollar night views'); disjoint from Bitan's bridge-and-river subject 2.6 km away; elevation honestly empty.",
    desc_ja="台北盆地の灯海を見下ろす琉璃光の名点（mook 五大百萬夜景）。碧潭とは題材が別。"),
  ]),
 dict(place_id="tw-146", region="tw", slug="tengzhih-forest", score=None,
  names={"zh-TW": "藤枝國家森林遊樂區", "en": "Tengjhih National Forest Recreation Area",
         "ja": "藤枝国家森林遊楽区", "local": "藤枝"},
  lat=23.0657536, lon=120.7470591, elev_m=1500, coord_conf="medium",
  coord_source="OSM Nominatim 藤枝（桃源區）＋林業保育署官方（園區海拔500-1,804m；主要遊憩帶1,500-1,804m）",
  coord_sources=["https://recreation.forest.gov.tw/Forest/RA?typ_id=0600001",
                 "https://pingtung.forest.gov.tw/0000134"],
  admin="高雄市", category="本島", tags=["forest", "mountain"],
  subjects=[
   dict(suffix="P01", template="cloud_sea", seasonal=None,
    zh="藤枝森濤雲霧", en="Tengjhih forest-cloud sea", ja="藤枝の雲霧",
    desc_zh="「森濤」之名的雲霧森林（林業保育署官方：園區海拔在1,500~1,804m 間涼爽宜人；遊樂區休園/開園依官方公告——access 記錄不計分）；與既有 高雄點題材錯位。",
    desc_en="The 'forest-wave' cloud-mist woodland (Forestry Bureau official: 1,500-1,804 m band; the area's open/closed status follows official notices - access note, not scored); disjoint from other Kaohsiung subjects.",
    desc_ja="「森涛」と呼ばれる雲霧の林（林業保育署公式、1500-1804m）。休園情報に注意。"),
  ]),
]

# subject-disjoint overrides for <5km neighbours (CL-DATA-51/64 precedent)
DIFF_OVERRIDES = {
    "tw-125": ("tw-104", "忘憂森林",
        "subject-disjoint: tea-terrace cloud sea/sunrise (open tea-terrace vista) vs Wuyou Forest flooded-forest mirror (forest water subject) - 4.4km apart, disjoint subjects"),
    "tw-127": ("tw-119", "加里山",
        "subject-disjoint: Xianshan cloud-mist 'fairyland' (cloud subject) vs Chiali-shan ridge/mountain view - 4.1km apart, disjoint subjects"),
    "tw-134": ("tw-106", "萬年峽谷",
        "subject-disjoint: 1314 deck tea-terrace cloud sea/night view vs Wannian canyon river-cut gorge - 4.9km apart, disjoint subjects"),
    "tw-137": ("tw-085", "南子吝步道",
        "subject-disjoint: Baoshishan yin-yang-sea sunset (bay sunset platform) vs Nanziwen trail coastal walk (~2.9km) - disjoint subjects"),
    "tw-140": ("tw-088", "翠峰湖環山步道觀景點",
        "subject-disjoint: Taipingshan forest cloud sea/stars (recreation-area ridge) vs Cueifong Lake loop (alpine lake) - 1.9km apart, disjoint subjects"),
    "tw-142": ("tw-110", "四草綠色隧道",
        "subject-disjoint: Anping wharf harbor sunset/installation art vs Sicao mangrove green tunnel - 3.8km apart, disjoint subjects"),
    "tw-143": ("tw-073", "老梅綠石槽",
        "subject-disjoint: Fuguijiao ventifact boulders + cape sunset (northernmost cape geology) vs Laomei seasonal green-algae reef - 1.0km apart, disjoint subjects"),
    "tw-145": ("tw-007", "碧潭",
        "subject-disjoint: Donghua temple basin light-sea liuli glow (hillside night viewpoint) vs Bitan suspension-bridge riverside - 2.6km apart, disjoint subjects"),
}
# rejected within-5km family overlaps: recorded in manifest, NOT admitted
REJECTED_PLACES = [
    ("北大武喜多麗斷崖段", "5km dedupe reject: 0.96km from existing tw-047 北大武山 - same summit/route subject family, not subject-disjoint"),
    ("薑麻園景觀茶園", "5km dedupe reject: 0.34km from existing tw-014 雲洞山莊 - same 薑麻園 cloud-sea viewpoint subject, not subject-disjoint"),
    ("加路蘭海蝕奇石群", "5km dedupe reject: 2.67km from existing tw-090 加路蘭海岸遊憩區 - same recreation-area subject (duplicate)"),
    ("好望角", "5km dedupe reject: 1.57km from existing tw-096 半天寮好望角 - same viewpoint subject (duplicate)"),
    ("鼻頭角海蝕平台/軍艦岩", "5km dedupe reject: 3.16km from existing tw-072 南雅奇岩 - same coastal mushroom-rock geology family, not subject-disjoint"),
    ("合歡北峰反射板", "5km dedupe reject: 4.44km from existing tw-019 合歡山主峰 - same high-mountain sunrise/cloud-sea summit family, not subject-disjoint"),
    ("武嶺/主峰星空", "5km dedupe reject: 0.87km from existing tw-019 合歡山主峰 - same summit stargazing/sunrise subject, not subject-disjoint"),
    ("阿拔泉山步道", "5km dedupe reject: 1.70km from existing tw-105 太平雲梯/梅山36彎 - same 竹崎 viewpoint/trail cluster, not subject-disjoint"),
]

# red_maple seasonal id exists in seasonal-calendar but not in the cl helper maps;
# register it here (window/sources quoted from the seasonal-calendar entry).
cl.TYPICAL_WINDOWS["red_maple"] = {"start": "10-20", "end": "11-10"}
cl.SEASON_NAMES["red_maple"] = {"zh-TW": "紅葉", "en": "Autumn maple", "ja": "紅葉"}
cl.SEASONAL_SOURCES["red_maple"] = (
    "https://www.weathernews.jp/koyo/",
    "季節窗沿用 seasonal-calendar 既有 red_maple 條目（10-20..11-10；ウェザーニュース紅葉リポート）")


def wb(p, text): return m64.wb(p, text)

def build_contract_66(p, subj):
    oid = f"{p['place_id']}-{subj['suffix']}"
    tpl = subj["template"]
    if tpl == "seasonal_plant":
        conds = cl.clone_conditions(oid, "seasonal_plant")
        conds.insert(0, cl.seasonal_condition(oid, subj["seasonal"]))
    elif tpl == "night_sky":
        conds = cl.clone_conditions(oid, "night_sky")
    elif tpl == "geological_landform":
        conds = cl.clone_conditions(oid, "geological_landform")
    else:
        conds = cl.clone_conditions(oid, tpl)
    # d52 fix: multiple window conditions in one exemplar collapse to the same LW id
    lw_n = 0
    for c in conds:
        if c["id"] and c["id"].endswith("-LW1"):
            lw_n += 1
            if lw_n > 1:
                c["id"] = f"C-{oid}-LW{lw_n}"
    ids = [c["id"] for c in conds]
    assert len(ids) == len(set(ids)), f"{oid} duplicate condition ids"
    geo_src = " ; ".join(p["coord_sources"])
    deriv = (f"{TICKET} wave-1 admission web verification {VER_DATE} ({p['coord_source']}; "
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
    if p["place_id"] == "tw-135":
        access["zh-TW"] += "（中央氣象署雷達站站區為管制區——僅步道及外圍合法拍攝。）"
        access["en"] += " (The CWA radar compound is restricted - shoot only from the trail and surroundings.)"
        access["ja"] += "（レーダー敷地は立入制限——登山道と周辺のみで撮影。）"
    if p["place_id"] == "tw-146":
        access["zh-TW"] += "（藤枝遊樂區休園/開園依林業保育署公告。）"
        access["en"] += " (Tengjhih's open/closed status follows Forestry Bureau notices.)"
        access["ja"] += "（藤枝の開園・休園は林業保育署公告に従う。）"
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
            "uncertainty_note": f"{TICKET} wave-1 admission reference; angles and distance unknown pending field survey.",
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
            "scope_note": f"{TICKET} wave-1 scoreless admission (owner ruling 2026-11-11: verification + 5km subject-disjoint dedupe; NO rubric/AGLI scoring); coordinates/elevation web-verified {VER_DATE} (sources in camera derivation_method and data/v2/audits/cl-data-66_web_evidence.json); 查無權威源之海拔誠實留空 (null); thresholds provisional pending real-shoot calibration.",
        }],
        "readiness": {"research_level": "R1", "gaps": ["RESEARCH_GAP"]},
        "provenance": {
            "source_catalog": f"{TICKET} Tier-A wave-1 intake (owner-list streams, scoreless {VER_DATE})",
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
    dedupe = {}
    for p in PLACES:
        existing = [(s["spot_id"], s["lat"], s["lon"], s["name_i18n"]["zh-TW"])
                    for s in R.get_spots(p["region"])]
        dists = sorted((hav(p["lat"], p["lon"], e[1], e[2])/1000, e[0], e[3]) for e in existing)
        nearest = dists[0]
        ov = DIFF_OVERRIDES.get(p["place_id"])
        row = {"nearest_existing": nearest[1], "name": nearest[2], "km": round(nearest[0], 2)}
        if ov:
            row["override"] = ov[2].replace(ov[0], nearest[1])
        else:
            assert nearest[0] >= 5.0, f"{p['place_id']} within 5km of {nearest}"
        dedupe[p["place_id"]] = row
    dedupe["_rejected_family_overlaps"] = [
        {"name": n, "reason": r} for n, r in REJECTED_PLACES]
    wb("data/v2/audits/discovery/cl-data-66-dedupe.json",
       json.dumps(dedupe, ensure_ascii=False, indent=1) + "\n")
    print("dedupe OK", {k: v["km"] for k, v in dedupe.items() if k != "_rejected_family_overlaps"})

    # ---- 1) V2 contracts ----
    written = []
    for p in PLACES:
        for subj in p["subjects"]:
            c = build_contract_66(p, subj)
            out = cl.DATA / f"{c['opportunity_id']}.json"
            cl.wbytes(out, cl.jdump(c))
            written.append(c["opportunity_id"])
    print("contracts written:", len(written))

    # ---- 2) regions.py ----
    rp = ROOT / "regions.py"
    text = rp.read_bytes().decode("utf-8").replace("\r\n", "\n")
    if '"tw-125"' not in text:
        a_tw = '            (24.364611, 121.31035, "武陵農場", "Wuling Farm", "武陵農場", "武陵農場", "本島", ["mountain", "starlight"]),\n'
        assert a_tw in text, "tw tuple anchor missing"
        lines = []
        for p in PLACES:
            n = p["names"]
            lines.append(
                f'            ({p["lat"]}, {p["lon"]}, "{n["zh-TW"]}", "{n["en"]}", '
                f'"{n["ja"]}", "{n["local"]}", "{p["category"]}", {json.dumps(p["tags"], ensure_ascii=False)}),  # {TICKET}\n')
        text = text.replace(a_tw, a_tw + "".join(lines), 1)
        a_admin = '    "tw-120": ["台中市"],\n'
        assert a_admin in text, "admin anchor missing"
        adm = "".join(f'    "{p["place_id"]}": ["{p["admin"]}"],  # {TICKET}\n' for p in PLACES)
        text = text.replace(a_admin, a_admin + adm, 1)
        a_elev = '    # CL-DATA-64 admission elevations (web-verified 2026-11-10; null elevations omitted honestly)\n'
        assert a_elev in text, "elev anchor missing"
        elev = f'    # {TICKET} wave-1 admission elevations (web-verified {VER_DATE}; null elevations omitted honestly)\n'
        for p in PLACES:
            if p["elev_m"] is not None:
                elev += f'    "{p["names"]["local"]}": {p["elev_m"]},  # {TICKET}\n'
        text = text.replace(a_elev, a_elev + elev, 1)
        a_o = 'SPOT_OVERRIDES = {\n'
        ii = text.index(a_o) + len(a_o)
        cins = f'    # {TICKET} wave-1 admission (web-verified {VER_DATE}; keyed to full display names per get_spots contract)\n'
        for p in PLACES:
            q = p["names"]["local"]
            src = p["coord_source"].replace('"', "'")
            cins += (' "%s": {"lat": %s,\n           "lon": %s,\n           "map_query": %s,\n'
                     '           "coordinate_source": %s,\n           "coordinate_confidence": "%s"},\n'
                     % (p["names"]["zh-TW"], p["lat"], p["lon"],
                        json.dumps(q, ensure_ascii=False),
                        json.dumps(f"{TICKET} wave-1 admission web verification {VER_DATE}: " + src, ensure_ascii=False),
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
    mf = json.loads(mf_path.read_bytes().decode("utf-8"))
    spots = [s for s in cat["spots"] if s["spot_id"].startswith("tw-")]
    opps = [o for s in spots for o in s["opportunities"]]
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

    # ---- 5) web evidence registry ----
    ev = {"ticket": TICKET, "wave": 1, "generated_at": VER_DATE,
          "rule": (f"Scoreless intake (owner ruling {VER_DATE}): admission = web verification + "
                   "5km subject-disjoint dedupe; NO rubric v2 gates, NO AGLI dual-board, agli-final "
                   "untouched; score fields left empty. 22 places admitted (tw-125..tw-146), 8 "
                   "manifest-top-30 candidates rejected for same-family <5km overlaps."),
          "places": [], "evidence": []}
    for p in PLACES:
        ev["places"].append({
            "place_id": p["place_id"], "slug": p["slug"], "score": None,
            "lat": p["lat"], "lon": p["lon"], "elev_m": p["elev_m"],
            "coord_confidence": p["coord_conf"], "coord_source": p["coord_source"],
            "sources": p["coord_sources"], "subjects": [s["zh"] for s in p["subjects"]],
            "ticket": TICKET})
        ev["evidence"].append({
            "id": f"e-d66-web-{p['slug']}", "grade": "A" if p["coord_conf"] == "high" else "B",
            "kind": "official_or_wikipedia_or_osm_text",
            "url": p["coord_sources"][0],
            "supports": p["coord_source"],
            "retrieved_at": VER_DATE,
            "limitation": "Coordinate/elevation verified against cited sources; exact tripod position and access not field-surveyed; opening/closure/permit/reservation status follows on-site notices.",
            "ticket": TICKET})
    wb("data/v2/audits/cl-data-66_web_evidence.json", cl.jdump(ev))
    print("web evidence written:", len(ev["places"]))

    # ---- 6) manifest wave-1 status update ----
    tm_path = ROOT / "data/v2/audits/subject-lists/tier-a-manifest.json"
    tm = json.loads(tm_path.read_bytes().decode("utf-8"))
    adm_names = {p["names"]["zh-TW"]: p["place_id"] for p in PLACES}
    rej_names = dict(REJECTED_PLACES)
    for r in tm["tier_a"][:30]:
        if r["name"] in adm_names:
            r["status"] = "admitted"
            r["wave"] = 1
            r["admitted_place_id"] = adm_names[r["name"]]
        elif r["name"] in rej_names:
            r["status"] = "rejected"
            r["wave"] = 1
            r["reject_reason"] = rej_names[r["name"]]
    tm["wave1"] = {"planned": 30, "order": "n_topics desc, n_lists desc",
                   "done": len(PLACES), "rejected": len(REJECTED_PLACES),
                   "place_ids": [p["place_id"] for p in PLACES]}
    cl.wbytes(tm_path, cl.jdump(tm))
    print("tier-a manifest updated: admitted", len(PLACES), "rejected", len(REJECTED_PLACES))
    print("DONE stage-1 build")

if __name__ == "__main__":
    main()
