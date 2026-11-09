#!/usr/bin/env python3
"""CL-DATA-53: admit 40 Gemini-source US photography spots (us-119..us-158) into legacy+V2+runtime.

PM-judgment direct admission (GROWTH-ONLY ruling 2026-11-09) per the CL-DATA-51/52 flow:
5km geo dedupe (subject-disjoint overrides recorded), AI web verification of
coordinates/elevation/seasons with authoritative URLs + dates into provenance,
dual-track build (V2 contracts + legacy regions.py/runtime catalog/manifest/dependencies).
Access restrictions (The Wave daily lottery, Navajo rim permit, BLM high-clearance roads,
NPS closed alcove) are recorded honestly in access notes but do NOT score.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location(
    'cl53base', str(ROOT / 'data/v2/tools/discovery/cl_data_52_build.py'))
m52 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m52)
cl = m52.cl  # cl_data_25_build helpers

VER_DATE = "2026-11-09"
TICKET = "CL-DATA-53"

SEASONS_53 = {
    "apostle_ice_caves": {
        "window": {"start": "01-01", "end": "03-15"},
        "name": {"zh-TW": "使徒群島冰洞季", "en": "Apostle Islands ice-cave window", "ja": "アポストル群島の氷洞シーズン"},
        "src": ("https://www.nps.gov/apis/learn/nature/ice-caves.htm",
                "Apostle Islands mainland sea caves open only when Lake Superior ice is thick enough for a safe ice route (typically Jan-Mar, dates yearly announced by NPS); verified " + VER_DATE),
    },
    "newengland_foliage": {
        "window": {"start": "09-29", "end": "10-27"},
        "name": {"zh-TW": "新英格蘭楓紅季", "en": "New England peak foliage", "ja": "ニューイングランドの紅葉ピーク"},
        "src": ("https://www.fs.usda.gov/whitemtn",
                "White Mountain NF Kancamagus Highway foliage peaks late Sep to late Oct in typical years; verified " + VER_DATE),
    },
    "blueridge_foliage": {
        "window": {"start": "10-10", "end": "11-05"},
        "name": {"zh-TW": "藍嶺公路楓紅季", "en": "Blue Ridge Parkway fall color", "ja": "ブルーリッジ・パークウェイの紅葉"},
        "src": ("https://www.nps.gov/blri/learn/nature/deciduous-forests.htm",
                "Blue Ridge Parkway high-elevation color peaks mid-Oct to early Nov in typical years; verified " + VER_DATE),
    },
    "joshua_tree_bloom": {
        "window": {"start": "02-15", "end": "04-30"},
        "name": {"zh-TW": "約書亞樹開花季", "en": "Joshua tree bloom", "ja": "ユッカの開花期"},
        "src": ("https://www.nps.gov/jotr/learn/nature/blooms.htm",
                "Joshua trees bloom Feb-Apr in typical years, timing variable with winter rains (NPS official); verified " + VER_DATE),
    },
    "lastdollar_aspen": {
        "window": {"start": "09-20", "end": "10-10"},
        "name": {"zh-TW": "Last Dollar Road 白楊金黃季", "en": "Last Dollar Road golden aspen", "ja": "Last Dollar Roadのゴールデンアスペン"},
        "src": ("https://www.visittelluride.com/",
                "San Juan aspen on Last Dollar Road turn gold late Sep to mid Oct in typical years (Telluride tourism); verified " + VER_DATE),
    },
}

PLACES = [ dict(place_id="us-119", region="us", slug="the-wave", score=4.9,
  names={"zh-TW": "波浪谷（The Wave）", "en": "The Wave (Coyote Buttes North)", "ja": "ザ・ウェーブ", "local": "The Wave"},
  lat=36.8617, lon=-112.3980, elev_m=1745, coord_conf="medium",
  coord_source="BLM/recreation.gov Coyote Buttes North（The Wave，Vermilion Cliffs NM，亞利桑那側；Coyote Buttes 北區約5,700 ft 帶）；座標 medium（波浪窪地中心推定）",
  coord_sources=["https://www.recreation.gov/permits/4251909", "https://www.blm.gov/programs/recreation/permits-and-passes/lotteries-and-permit-systems/arizona"],
  admin="Arizona", category="美西", tags=["mountain"],
  access_i18n={
    "zh-TW": "許可制：每日最多64人/16組，全部經 recreation.gov 抽籤（進階抽籤4個月前、現地地理圍欄每日抽籤兩天前），不可越權進入；波浪谷周邊路段需高底盤車與步行導航能力。開放狀態依 BLM 當期公告。",
    "en": "Permit-required: max 64 people/16 groups per day, all by recreation.gov lottery (4-month advanced lottery, or a geofenced daily lottery two days ahead); no entry without a permit; access roads are deep sand requiring 4WD and navigation skills. Current status per BLM notices.",
    "ja": "許可制：1日64人/16組まで、recreation.gov抽選のみ（4ヶ月前の事前抽選、または2日前のジオフェンス日次抽選）。許可なし立ち入り不可。砂地のアクセス路は4WDとナビ能力が必要。現地のBLM告知に従う。"},
  subjects=[dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="波浪谷砂岩浪湧", en="Petrified dune waves of The Wave", ja="ザ・ウェーブの砂岩の波",
    desc_zh="兩億年沙丘石化層在 Coyote Buttes 北区被風蝕成涌浪狀條紋（BLM 官方許可區）；與既有 us 亞利桑那點（上/下羚羊谷、馬蹄灣）題材錯位——本點為石化沙丘波紋本身。",
    desc_en="200-million-year-old petrified dunes carved into swirling striations in Coyote Buttes North (BLM permitted area); disjoint from existing Arizona slots and Horseshoe Bend - here the petrified-dune waves.",
    desc_ja="コヨーテ・バッツ・ノースの石化した砂丘が波のように削られた縞模様（BLM許可区）。既存のアリゾナ渓谷や馬蹄湾とは題材が別。")]), dict(place_id="us-120", region="us", slug="rowena-crest", score=4.3,
  names={"zh-TW": "哥倫比亞河峽谷（羅威娜岬）", "en": "Columbia River Gorge (Rowena Crest)", "ja": "コロンビア渓谷（ロウェナ・クレスト）", "local": "Rowena Crest"},
  lat=45.6686, lon=-121.4357, elev_m=250, coord_conf="medium",
  coord_source="Friends of the Columbia Gorge / Wikipedia 哥倫比亞河峽谷（羅威娜岬觀景台， historic Columbia River Highway 對位）；座標 medium（觀景台推定）",
  coord_sources=["https://gorgefriends.org/", "https://en.wikipedia.org/wiki/Columbia_River_Gorge"],
  admin="Oregon", category="美西", tags=["mountain", "coast"],
  subjects=[dict(suffix="P01", template="overlook", seasonal=None,
    desc_zh="羅威娜岬俯瞰哥倫比亞河切穿喀斯開山脈的橫向峽谷（Friends of Gorge 官方；春末野花與層積雲著名）；與既有 us-081 雷尼爾山（30km+ 北側）與波特蘭境內瀑布峽段（50km+）題材錯位——本點為乾田段峽谷全景。",
    desc_en="From Rowena Crest the Columbia tears west through the Cascades as a transverse gorge (Friends of the Columbia Gorge; spring wildflowers and famous cleared views); disjoint from existing Portland-area gorge falls and Mt Rainier spots.",
    desc_ja="ロウェナ・クレストからコロンビア川がカスケード山脈を横断する渓谷を望む（公式）。既存のポートランド側の滝群やレーニア山とは題材が別。",
    zh="羅威娜岬峽谷全景", en="Rowena Crest gorge panorama", ja="ロウェナ・クレストの渓谷展望")]), dict(place_id="us-121", region="us", slug="bixby-bridge", score=4.4,
  names={"zh-TW": "比克斯比溪橋（大瑟爾）", "en": "Bixby Creek Bridge (Big Sur)", "ja": "ビックスビー・ブリッジ（ビッグサー）", "local": "Bixby Creek Bridge"},
  lat=36.0727, lon=-121.9046, elev_m=80, coord_conf="high",
  coord_source="Wikipedia Bixby Creek Bridge（36°04′22″N 121°54′17″W，1932年拱橋橋面高約85 m；加州 Big Sur 海岸）",
  coord_sources=["https://en.wikipedia.org/wiki/Bixby_Creek_Bridge"],
  admin="California", category="美西", tags=["coast"],
  subjects=[dict(suffix="P01", template="sunset", seasonal=None,
    zh="比克斯比橋夕照", en="Bixby Bridge at sunset", ja="ビックスビー橋の夕景",
    desc_zh="1932年開通的開拱橋橫跨峽谷崖岸，太平洋夕照為加州最著名公路定番之一（Wikipedia；橋面約85m）；與 us-122 麥克威瀑布（14km 南，瀑布體主題）題材錯位——本點為橋＋海岸線。",
    desc_en="The 1932 open-spandrel arch spans a sheer coastal canyon into the Pacific sunset - one of California's classic road compositions (Wikipedia; ~85 m deck); disjoint from us-122 McWay Falls (waterfall subject) 14 km south.",
    desc_ja="1932年架設のアーチ橋が渓谷を跨ぎ太平洋の夕日と並ぶ（Wikipedia；橋面約85m）。14km南のマクウェイ滝（滝が主題）とは題材が別。")]), dict(place_id="us-122", region="us", slug="mcway-falls", score=4.2,
  names={"zh-TW": "麥克威瀑布（朱莉婭·菲佛州立公園）", "en": "McWay Falls (Julia Pfeiffer Burns SP)", "ja": "マクウェイ滝（ジュリア・ファイファー・バーンズ州立公園）", "local": "McWay Falls"},
  lat=36.3586, lon=-121.9762, elev_m=30, coord_conf="high",
  coord_source="California State Parks / Wikipedia 麥克威瀑布（80呎（約24m）落於海灘；36°21′30″N 121°58′37″W 對位）",
  coord_sources=["https://www.parks.ca.gov/", "https://en.wikipedia.org/wiki/McWay_Falls"],
  admin="California", category="美西", tags=["coast", "waterfall"],
  subjects=[dict(suffix="P01", template="overlook", seasonal=None,
    zh="麥克威瀑布入海", en="McWay Falls onto the beach", ja="マクウェイ滝の海への落下",
    desc_zh="全美少數直接落沙灘入海的恆定瀑布（加州州立公園官方；展望台俯視、灘域禁入）；與 us-121 比克斯比橋（橋體主題）錯位——本點為瀑布入海。",
    desc_en="One of the few US waterfalls dropping directly onto a beach (California State Parks; overlook-only, beach closed); disjoint from the Bixby Bridge arch subject 14 km north.",
    desc_ja="直接ビーチに落ちる数少ない恒常的な滝（カリフォルニア州立公園公式；展望台のみ、ビーチ立入禁止）。14km北のビックスビー橋とは題材が別。")]), dict(place_id="us-123", region="us", slug="maroon-bells", score=4.6,
  names={"zh-TW": "褐鈴山（馬倫湖倒影）", "en": "Maroon Bells (Maroon Lake mirror)", "ja": "マルーン・ベルズ", "local": "Maroon Bells"},
  lat=39.0975, lon=-106.9886, elev_m=2884, coord_conf="high",
  coord_source="USGS/USFS White River NF（Maroon Lake 約2,884 m；北峰4,317 m/南峰4,270 m；39°05′51″N 106°59′15″W 對位）",
  coord_sources=["https://www.fs.usda.gov/whiteriver", "https://en.wikipedia.org/wiki/Maroon_Bells"],
  admin="Colorado", category="美西", tags=["mountain", "lake"],
  subjects=[dict(suffix="P01", template="reflection", seasonal=None,
    zh="褐鈴山湖鏡倒影", en="Maroon Bells lake mirror", ja="マルーン・ベルズの湖面鏡写",
    desc_zh="北美最常上鏡的山景之一：紅岩雙峰映平靜湖面（USFS；清晨無風才有鏡面）；與既有 us 科州點（丹佛都市、大沙丘）題材錯位——本點為雙峰湖鏡。",
    desc_en="One of the most photographed mountain scenes in North America: twin maroon peaks mirrored in Maroon Lake on windless mornings (USFS); disjoint from existing Colorado spots.",
    desc_ja="北米屈指の撮影スポット：無風の早朝、マルーン湖に双峰が映る（USFS）。既存のコロラドの点とは題材が別。")]), dict(place_id="us-124", region="us", slug="keystone-canyon", score=4.0,
  names={"zh-TW": "瓦爾迪茲基石峽谷瀑布", "en": "Valdez Keystone Canyon falls", "ja": "バルディーズ・キーストーン峡谷の滝", "local": "Keystone Canyon"},
  lat=61.0414, lon=-146.2389, elev_m=200, coord_conf="medium",
  coord_source="Wikipedia Keystone Canyon（瓦爾迪茲公路沿理查森峽谷，Bridal Veil/Horsetail 瀑布；座標 medium（谷段對位））",
  coord_sources=["https://en.wikipedia.org/wiki/Keystone_Canyon"],
  admin="Alaska", category="阿拉斯加", tags=["waterfall", "mountain"],
  subjects=[dict(suffix="P01", template="waterfall", seasonal=None,
    zh="基石峽谷雙瀑", en="Keystone Canyon twin falls", ja="キーストーン峡谷の滝",
    desc_zh="瓦爾迪茲公路切行的理查森峽谷，婚紗瀑布與馬尾瀑布掛壁（Wikipedia；冬季結冰成冰瀑）；與既有 us-041 迪納利（90km+ 內陸山景）題材錯位——本點為峽谷瀑布群。",
    desc_en="The Richardson-cut gorge near Valdez with Bridal Veil and Horsetail falls on the walls, frozen into icefalls in winter (Wikipedia); disjoint from inland Denali mountain scenery.",
    desc_ja="バルディーズ近郊の峡谷に架かるブライダルベールとホーステイルの滝（冬は氷瀑）（Wikipedia）。内陸のデナリとは題材が別。")]), dict(place_id="us-125", region="us", slug="kancamagus", score=4.0,
  names={"zh-TW": "白山坎坎瑪格斯公路", "en": "Kancamagus Highway (White Mountains)", "ja": "カンカマーガス・ハイウェイ（ホワイト山地）", "local": "Kancamagus Highway"},
  lat=44.0234, lon=-71.3650, elev_m=926, coord_conf="medium",
  coord_source="USFS White Mountain NF（Kancamagus Highway，NH 112；Kancamagus Pass 約3,037 ft 為公路最高點；座標 medium（Pass 對位））",
  coord_sources=["https://www.fs.usda.gov/whitemtn", "https://en.wikipedia.org/wiki/Kancamagus_Highway"],
  admin="New Hampshire", category="美東", tags=["forest", "mountain"],
  subjects=[dict(suffix="P01", template="seasonal_plant", seasonal="newengland_foliage",
    zh="坎坎瑪格斯楓紅公路", en="Kancamagus foliage corridor", ja="カンカマーガスの紅葉街道",
    desc_zh="無人商店的國家森林景觀公路，秋季楓紅沿斯威夫特河鋪展（USFS；9月末至10月下旬典型峰值）；與既有 us-098 緬因州阿卡迪亞（20km+ 海岸）題材錯位——本點為內陸楓紅走廊。",
    desc_en="A scenic national-forest highway without services, foliage blazing along the Swift River (USFS; typical peak late Sep-late Oct); disjoint from coastal Acadia, Maine.",
    desc_ja="サービス施設のない国有林のシーニック・ハイウェイ、スウィフト川沿いに紅葉（USFS；9月末〜10月下旬）。海岸のアカデミアとは題材が別。")]), dict(place_id="us-126", region="us", slug="linn-cove-viaduct", score=4.2,
  names={"zh-TW": "藍嶺公路林恩灣高架橋", "en": "Linn Cove Viaduct (Blue Ridge Parkway)", "ja": "リン・コーブ・バイアダクト（ブルーリッジ・パークウェイ）", "local": "Linn Cove Viaduct"},
  lat=36.0897, lon=-81.7994, elev_m=1250, coord_conf="medium",
  coord_source="NPS Blue Ridge Parkway / Wikipedia 林恩灣高架橋（1987年 S 形高架繞大霧山東緣格蘭德father山，橋面高約1,250 m 帶；座標 medium）",
  coord_sources=["https://www.nps.gov/blri/", "https://en.wikipedia.org/wiki/Linn_Cove_Viaduct"],
  admin="North Carolina", category="美東", tags=["mountain", "forest"],
  subjects=[dict(suffix="P01", template="overlook", seasonal="blueridge_foliage",
    zh="林恩灣高架橋秋色", en="Linn Cove Viaduct in fall color", ja="リン・コーブ高架橋と紅葉",
    desc_zh="S 形鋼橋繞過 Grandfather 山稜線，秋季紅葉包圍（NPS；10月中至11月初典型峰值）；與既有 us 阿帕拉契點（70km+）題材錯位——本點為橋體＋山脊。",
    desc_en="The S-shaped steel viaduct wraps the Grandfather Mountain ridgeline in autumn color (NPS; typical peak mid-Oct-early Nov); disjoint from other Appalachian points.",
    desc_ja="S字型の高架橋がグランドファーザー山の稜線を回り込み紅葉に包まれる（NPS）。既存のアパラチアの点とは題材が別。")]), dict(place_id="us-127", region="us", slug="white-pocket", score=4.4,
  names={"zh-TW": "白口袋（朱紅斷崖國家紀念地）", "en": "White Pocket (Vermilion Cliffs NM)", "ja": "ホワイト・ポケット", "local": "White Pocket"},
  lat=36.9561, lon=-111.9043, elev_m=1860, coord_conf="medium",
  coord_source="BLM White Pocket Trailhead（36.955011,-111.893296）+ Wikipedia White Pocket（36°27′28″N 111°42′15″W 中心帶，6,100 ft 帶）",
  coord_sources=["https://www.blm.gov/", "https://en.wikipedia.org/wiki/White_Pocket"],
  admin="Arizona", category="美西", tags=["mountain"],
  subjects=[dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="白口袋花椰岩紋", en="White Pocket cauliflower rock", ja="ホワイト・ポケットの岩模様",
    desc_zh="Na­vajo 砂岩扭皺的花椰菜狀紋理與白頂紅壁（BLM；無步道自由漫遊，深沙路需高底盤車——access 不計分）；與 us-119 波浪谷（12km，許可區波紋）題材同源但形態不同且免抽籤——兩點並存。",
    desc_en="Swirled Navajo sandstone 'cauliflower' domes under white caps (BLM; no trails, free-roam, deep-sand 4WD access - access not scored); 12 km from the permitted Wave (us-119) but a different landform and no lottery.",
    desc_ja="ナバホ砂岩の花模様のドーム（BLM；遊歩道なし、深い砂地は4WD）。12km先の抽選制ザ・ウェーブとは地形も方式も別。")]), dict(place_id="us-128", region="us", slug="reflection-canyon", score=4.7,
  names={"zh-TW": "反射峽谷（鮑威爾湖）", "en": "Reflection Canyon (Lake Powell)", "ja": "リフレクション・キャニオン（レイク・パウエル）", "local": "Reflection Canyon"},
  lat=37.1746, lon=-110.9038, elev_m=1330, coord_conf="medium",
  coord_source="Glen Canyon NRA 產業級徒步記錄（Reflection Canyon overlook，peak 約4,466 ft/1,361 m；座標 medium（展望台推定））",
  coord_sources=["https://www.nps.gov/glca/", "https://www.whatdoyousea.com/reflection-canyon/"],
  admin="Utah", category="美西", tags=["lake", "mountain"],
  subjects=[dict(suffix="P01", template="overlook", seasonal=None,
    zh="反射峽谷 S 形灣", en="Reflection Canyon S-bend", ja="リフレクション峡谷のS字",
    desc_zh="格蘭峽谷國家遊憩區內 Navajo 砂岩 S 形灣俯視鮑威爾湖（NPS；無步道、約16–18 英里越野徒步，座標為展望台推定——access 不計分，列入誠實標註）；與既有 us 亞利桑那峽谷點題材錯位——本點為湖灣 S 形。",
    desc_en="The Navajo sandstone S-bend above Lake Powell in Glen Canyon NRA (NPS; route-finding over ~16-18 miles with no trail, coordinates are the overlook estimate - access not scored, honestly labeled); disjoint from existing Arizona canyon subjects.",
    desc_ja="グレンキャニオンNRA、ナバホ砂岩のS字湾（NPS；ルートファインディング16〜18マイル、展望台推定座標）。既存のアリゾナ峡谷とは題材が別。")]), dict(place_id="us-129", region="us", slug="factory-butte", score=4.1,
  names={"zh-TW": "工廠台地（月球地貌）", "en": "Factory Butte moonscape", "ja": "ファクトリー・ビュート", "local": "Factory Butte"},
  lat=38.3767, lon=-110.9003, elev_m=1480, coord_conf="high",
  coord_source="recreation.gov Factory Butte Recreation Area（38.365881,-110.915269）+ Capitol Reef Country（staging area 38.376667,-110.900278）；Butte 峰 6,302 ft/1,921 m（Wikipedia）",
  coord_sources=["https://www.recreation.gov/gateways/16219", "https://en.wikipedia.org/wiki/Factory_Butte_(Wayne_County,_Utah)"],
  admin="Utah", category="美西", tags=["mountain"],
  subjects=[dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="工廠台地月球地貌", en="Factory Butte badland moonscape", ja="ファクトリー・ビュートの月面風景",
    desc_zh="Entry 砂岩壞地被沖刷成銀灰色「月球表面」，孤台地聳立（Wikipedia/recreation.gov；Hanksville 西側 SR-24 沿線）；與 us-129 白口袋（彩色砂岩紋理）錯位——本點為灰壞地＋孤峰。",
    desc_en="Silver-gray Entrada badlands scoured into a lunar plain with the lone butte rising (Wikipedia/recreation.gov; SR-24 west of Hanksville); disjoint from White Pocket's colored swirls.",
    desc_ja="銀灰色のバッドランドにそびえる孤峰（Wikipedia/recreation.gov）。ホワイト・ポケットの彩色紋とは題材が別。")]), dict(place_id="us-130", region="us", slug="coal-mine-canyon", score=4.0,
  names={"zh-TW": "煤礦峽谷（納瓦霍保留區）", "en": "Coal Mine Canyon (Navajo Nation)", "ja": "コール・マイン峡谷", "local": "Coal Mine Canyon"},
  lat=36.0053, lon=-111.0486, elev_m=1780, coord_conf="medium",
  coord_source="thewave.info Coal Mine Canyon guide（rim 5,800 ft/1,768 m，Tuba City 東南 15 mi；座標 medium（rim 對位））+ Wikipedia Coalmine Canyon",
  coord_sources=["https://www.thewave.info/CoalMineCanyonCode/Map.html", "https://en.wikipedia.org/wiki/Coalmine_Canyon,_Arizona"],
  admin="Arizona", category="美西", tags=["mountain"],
  subjects=[dict(suffix="P01", template="overlook", seasonal=None,
    zh="煤礦峽谷紅白條紋", en="Coal Mine Canyon rim stripes", ja="コール・マイン峡谷の縞",
    desc_zh="紅白條紋的壞地峽谷自 rim 俯視（thewave.info；rim 在納瓦霍保留區需許可，內部屬 Hopi 需嚮導——access 不計分，誠實標註）；與 us-119/us-129（砂岩波紋主題）錯位——本點為條紋壞地峽谷全景。",
    desc_en="Red-and-white striped badlands seen from the rim (thewave.info; the rim is Navajo Nation land requiring a permit and the interior is Hopi with guide-required access - access not scored, honestly labeled); disjoint from the petrified-dune subjects of us-119/129.",
    desc_ja="紅白の縞模様のバッドランドを縁から望む（thewave.info；縁はナバホ国の許可制、内部はホピ族でガイド必須）。砂岩波紋系の対象とは題材が別。")]), dict(place_id="us-131", region="us", slug="bisti-badlands", score=4.2,
  names={"zh-TW": "比斯蒂/迪納津荒野", "en": "Bisti/De-Na-Zin Wilderness", "ja": "ビスティ/デ・ナ・ジン荒野", "local": "Bisti/De-Na-Zin"},
  lat=36.0911, lon=-108.2356, elev_m=1950, coord_conf="medium",
  coord_source="Wikipedia Bisti/De-Na-Zin（36°05′N 108°14′W 帶；BLM 荒野，入口停車場與次級路對位）",
  coord_sources=["https://en.wikipedia.org/wiki/Bisti/De-Na-Zin_Wilderness", "https://www.blm.gov/"],
  admin="New Mexico", category="美西", tags=["mountain"],
  subjects=[dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="比斯蒂泥岩奇岩", en="Bisti hoodoos and petrified wood", ja="ビスティの奇岩と化石木",
    desc_zh="泥岩/砂岩交層的蘑菇石、翅岩與化石木（BLM 荒野；無步道、路標稀少——access 不計分）；與 us-131 工廠台地（大面積銀灰壞地）錯位——本點為小尺度奇岩群。",
    desc_en="Mushroom hoodoos, winged rocks and petrified wood in layered mudstone (BLM wilderness; no trails, sparse navigation - access not scored); disjoint from Factory Butte's broad gray plain.",
    desc_ja="泥岩の蘑菇石と化石木の群れ（BLM荒野；道なし）。広面積の灰色平原のファクトリー・ビュートとは題材が別。")]), dict(place_id="us-132", region="us", slug="bonsai-rock", score=4.1,
  names={"zh-TW": "太浩湖盆景岩", "en": "Bonsai Rock (Lake Tahoe)", "ja": "ボンサイ・ロック", "local": "Bonsai Rock"},
  lat=39.0744, lon=-120.0394, elev_m=1897, coord_conf="medium",
  coord_source="Lake Tahoe shoreline 推定（盆景岩，東岸靜水區；座標 medium；湖面 1,897 m）",
  coord_sources=["https://en.wikipedia.org/wiki/Lake_Tahoe"],
  admin="Nevada", category="美西", tags=["lake"],
  subjects=[dict(suffix="P01", template="reflection", seasonal=None,
    zh="盆景岩湖面倒影", en="Bonsai Rock over still water", ja="ボンサイ・ロックの湖面",
    desc_zh="花崗岩塔上松樹叢立如盆景，靜水鏡面（內華達州東岸；岸邊巨石下坡需小心——access 不計分）；與既有 us 加州湖泊點題材錯位——本點為湖中岩塔。",
    desc_en="A granite turret crowned with junipers 'bonsai', mirrored on calm water (Nevada east shore; steep boulder descent - access not scored); disjoint from existing California lake subjects.",
    desc_ja="花崗岩の塔に松が盆景のように生え、静水に映る（ネバダ東岸）。既存のカリフォルニア湖沼対象とは題材が別。")]), dict(place_id="us-133", region="us", slug="bristlecone-pines", score=4.3,
  names={"zh-TW": "古狐尾松森林（舒爾曼林）", "en": "Ancient Bristlecone Pine Forest (Schulman Grove)", "ja": "古いブリストルコーン松林（シュルマン・グローブ）", "local": "Schulman Grove"},
  lat=37.5917, lon=-118.6111, elev_m=3000, coord_conf="high",
  coord_source="USFS Inyo NF（Schulman Grove 約9,847 ft/3,001 m，白山白山公路盡頭；座標 high）",
  coord_sources=["https://www.fs.usda.gov/detail/inyo/", "https://en.wikipedia.org/wiki/Ancient_Bristlecone_Pine_Forest"],
  admin="California", category="美西", tags=["forest", "mountain"],
  subjects=[dict(suffix="P01", template="overlook", seasonal=None,
    zh="古狐尾松扭曲古木", en="Ancient bristlecone twisted trunks", ja="ブリストルコーン松の古木",
    desc_zh="全球最老非克隆樹之一（近5,000年）的扭曲古木在3,000m白山迎日出（USFS；公路季節性冬季封閉——access 不計分）；與既有 us-100 白山點（內華達山脈東麓Mono 湖）題材錯位——本點為古木本身。",
    desc_en="Twisted ancients near 5,000 years old on the White Mountains at 3,000 m (USFS; seasonal winter road closure - access not scored); disjoint from the Mono Lake east-slope spot us-100.",
    desc_ja="ほぼ5,000年の古木が白山3,000mに（USFS；冬季道路閉鎖）。モノ湖の対象とは題材が別。")]), dict(place_id="us-134", region="us", slug="apostle-ice-caves", score=4.2,
  names={"zh-TW": "使徒群島海蝕洞（冰洞）", "en": "Apostle Islands sea caves (ice caves)", "ja": "アポストル群島の海食洞（氷洞）", "local": "Meyers Beach ice caves"},
  lat=46.7389, lon=-90.9978, elev_m=183, coord_conf="medium",
  coord_source="NPS Apostle Islands（Meyers Beach 冰洞路線，蘇必略湖面約183 m；座標 medium（岸線對位））",
  coord_sources=["https://www.nps.gov/apis/learn/nature/ice-caves.htm"],
  admin="Wisconsin", category="美中", tags=["coast", "mountain"],
  subjects=[dict(suffix="P01", template="snow_ice", seasonal="apostle_ice_caves",
    zh="使徒群島冰洞冰簾", en="Apostle Islands icicle caves", ja="アポストル群島の氷洞",
    desc_zh="僅當蘇必略湖冰層足厚，NPS 才開放冰洞路線（通常1–3月，年度公佈）——季節窗追蹤官方案件而非保證；冰簾/冰錐洞穴景觀；與既有 us 五大湖點（尼加拉瀑布）題材錯位——本點為湖冰洞。",
    desc_en="The ice-cave route opens only when Lake Superior ice is thick enough (typically Jan-Mar, dates yearly announced by NPS) - the window tracks the official opening, never a guarantee; disjoint from the Niagara subject.",
    desc_ja="スペリオル湖の氷が十分に厚い時のみNPSが氷洞路線を開放（例年1〜3月、年度公表）。氷瀑の洞窟景観。ナイアガラとは題材が別。")]), dict(place_id="us-135", region="us", slug="caddo-lake", score=4.1,
  names={"zh-TW": "卡多湖（西班牙苔蘚）", "en": "Caddo Lake (Spanish moss bayous)", "ja": "カドー湖", "local": "Caddo Lake"},
  lat=32.7236, lon=-94.1531, elev_m=52, coord_conf="high",
  coord_source="Wikipedia Caddo Lake（32°43′N 94°09′W 帶；最大南方淡水湖，沼澤地與柏樹）",
  coord_sources=["https://en.wikipedia.org/wiki/Caddo_Lake"],
  admin="Texas", category="美中", tags=["lake", "forest"],
  subjects=[dict(suffix="P01", template="reflection", seasonal=None,
    zh="卡多湖柏樹苔沼", en="Caddo cypress bayou", ja="カドー湖の柏樹の沼",
    desc_zh="靜水沼澤中垂掛西班牙苔蘚的百年水杉與晨霧（Wikipedia；船遊最宜——access 資訊性）；與既有 us 美中點（南達科他）題材錯位——本點為沼澤柏林。",
    desc_en="Centuries-old bald cypress draped with Spanish moss in still bayous with morning fog (Wikipedia; best by boat - informational access note); disjoint from the existing Midwest plains subject.",
    desc_ja="静かな沼に垂れるスパニッシュモスと水杉、朝霧（Wikipedia；ボート推奨）。既存の平原対象とは題材が別。")]), dict(place_id="us-136", region="us", slug="palo-duro", score=4.2,
  names={"zh-TW": "帕洛杜羅峽谷（燈塔岩）", "en": "Palo Duro Canyon (Lighthouse)", "ja": "パロ・デュロ峡谷（ライトハウス）", "local": "Palo Duro Canyon"},
  lat=34.9700, lon=-101.6800, elev_m=900, coord_conf="medium",
  coord_source="Texas Parks & Wildlife / Wikipedia 帕洛杜羅峽谷（全美第二大峽谷；Lighthouse 岩區約34°58′N 101°41′W 帶；座標 medium）",
  coord_sources=["https://tpwd.texas.gov/state-parks/palo-duro-canyon", "https://en.wikipedia.org/wiki/Palo_Duro_Canyon"],
  admin="Texas", category="美中", tags=["mountain"],
  subjects=[dict(suffix="P01", template="overlook", seasonal=None,
    zh="帕洛杜羅燈塔岩", en="Palo Duro Lighthouse", ja="パロ・デュロのライトハウス",
    desc_zh="紅橙岩壁與尖頂「燈塔岩」（TPWD 州立公園；約20公里長峽谷）；與既有 us 大峽谷（800km 西）題材同類但尺度/岩色不同，距離遠無 5km 衝突——本點為草原中的紅岩峽谷。",
    desc_en="Red-and-orange walls with the capped Lighthouse spire (TPWD state park; a ~20-mile canyon on the plains); geographically far from the Grand Canyon with no 5 km conflict - a plain-ringed red canyon.",
    desc_ja="赤橙色の岩壁とキャップ付きのライトハウス岩（TPWD）。グランドキャニオンとは距離も地形も別。")]), dict(place_id="us-137", region="us", slug="watkins-glen", score=4.1,
  names={"zh-TW": "沃特金斯格倫州立公園", "en": "Watkins Glen State Park", "ja": "ワトキンス・グレン州立公園", "local": "Watkins Glen"},
  lat=42.3792, lon=-76.7467, elev_m=250, coord_conf="high",
  coord_source="Wikipedia/NY State Parks 沃特金斯格倫（Glen Creek 19 瀑與峽谷步道；42°22′N 76°45′W 帶）",
  coord_sources=["https://en.wikipedia.org/wiki/Watkins_Glen_State_Park", "https://parks.ny.gov/"],
  admin="New York", category="美東", tags=["waterfall", "forest"],
  subjects=[dict(suffix="P01", template="waterfall", seasonal=None,
    zh="沃特金斯格倫峽谷瀑布群", en="Watkins Glen gorge cascades", ja="ワトキンス・グレンの滝群",
    desc_zh="400呎深石雕峽谷內 19 瀑與拱橋（NY State Parks；冬季步道封閉——access 資訊性）；與既有 us 美東點題材錯位——本點為峽谷瀑布群。",
    desc_en="Nineteen waterfalls and arched bridges in a 400-ft carved gorge (NY State Parks; winter trail closure - access informational); disjoint from other Eastern US subjects.",
    desc_ja="400フィートの峡谷に19の滝とアーチ橋（NY州立公園；冬季閉鎖）。他の米東部対象とは題材が別。")]), dict(place_id="us-138", region="us", slug="sparks-lane", score=4.0,
  names={"zh-TW": "斯帕克斯小巷（凱德斯谷）", "en": "Sparks Lane (Cades Cove)", "ja": "スパークス・レーン（ケイズ・コーブ）", "local": "Sparks Lane"},
  lat=35.6114, lon=-83.8192, elev_m=500, coord_conf="medium",
  coord_source="NPS Great Smoky Mountains（Cades Cove Loop 環線，Sparks Lane 對位；座標 medium）",
  coord_sources=["https://www.nps.gov/grsm/"],
  admin="Tennessee", category="美東", tags=["forest", "mountain"],
  subjects=[dict(suffix="P01", template="sunrise", seasonal=None,
    zh="斯帕克斯小巷晨霧", en="Sparks Lane morning fog", ja="スパークス・レーンの朝霧",
    desc_zh="山谷新拓農地柵欄小路在晨霧中（NPS Cades Cove；秋季麋鹿/白尾鹿與霧景著名）；與既有 us 美東點題材錯位——本點為谷地晨霧柵欄線。",
    desc_en="A split-rail fence lane across a farm cove in morning fog (NPS Cades Cove; elk and deer sightings common); disjoint from other Eastern US subjects.",
    desc_ja="霧の中の農場と柵の小道（NPS ケイズ・コーブ）。他の米東部対象とは題材が別。")]), dict(place_id="us-139", region="us", slug="crystal-mill", score=4.2,
  names={"zh-TW": "水晶磨坊", "en": "Crystal Mill", "ja": "クリスタル・ミル", "local": "Crystal Mill"},
  lat=39.05889, lon=-107.10389, elev_m=2710, coord_conf="high",
  coord_source="Wikipedia/NRHP Crystal Mill（1892年木造水力廠，39°03′32″N 107°06′14″W；NRHP 85001493）",
  coord_sources=["https://en.wikipedia.org/wiki/Crystal_Mill", "https://npgallery.nps.gov/AssetDetail/NRIS/85001493"],
  admin="Colorado", category="美西", tags=["mountain", "forest"],
  subjects=[dict(suffix="P01", template="overlook", seasonal=None,
    zh="水晶磨坊秋色", en="Crystal Mill in autumn", ja="クリスタル・ミルの秋",
    desc_zh="1892年水力廠懸於水晶河巨石上，秋季黃楊包圍（NRHP 登錄；私人路需高底盤車——access 資訊性）；與既有 us 科州點題材錯位——本點為磨坊＋急流＋秋色。",
    desc_en="An 1892 wooden powerhouse perched on Crystal River boulders, boxed in by golden aspen (NRHP-listed; private rough road - access informational); disjoint from other Colorado subjects.",
    desc_ja="1892年の木造水力発電所が水晶河の巨岩に（NRHP登録；私道は高底盤車）。他のコロラド対象とは題材が別。")]), dict(place_id="us-140", region="us", slug="ice-lakes-basin", score=4.3,
  names={"zh-TW": "冰湖盆地", "en": "Ice Lakes Basin", "ja": "アイス・レイク盆地", "local": "Ice Lake"},
  lat=37.8114, lon=-107.7899, elev_m=3735, coord_conf="high",
  coord_source="USFS/Colorado Lakes（Ice Lake 約12,260 ft/3,735 m；trailhead 37.8119,-107.7925；San Juan NF）",
  coord_sources=["https://www.fs.usda.gov/wildflowers/regions/Rocky_Mountain/IceLakes/index.shtml", "https://www.coloradolakes.org/lakes/san-juan-county/ice-lake"],
  admin="Colorado", category="美西", tags=["lake", "mountain"],
  subjects=[dict(suffix="P01", template="reflection", seasonal=None,
    zh="冰湖碧藍倒影", en="Ice Lake turquoise mirror", ja="アイス湖のターコイズ",
    desc_zh="3,735 m 冰斗湖映 13,000 呎峰牆，湖水礦物藍（USFS；步道約8英里爬升2,900呎——access 不計分）；與 us-123 褐鈴山（含氧紅岩湖鏡）題材錯位——本點為高山碧藍湖。",
    desc_en="A 3,735 m cirque lake mirroring 13,000-ft walls, mineral-turquoise water (USFS; ~8 mi trail with 2,900 ft gain - access not scored); disjoint from us-123 Maroon Bells.",
    desc_ja="3,735mの圏谷湖が13,000フィートの峰壁を映す（USFS；約8マイル）。マルーン・ベルズとは題材が別。")]), dict(place_id="us-141", region="us", slug="last-dollar-road", score=4.2,
  names={"zh-TW": "特柳賴德（Last Dollar Road）", "en": "Telluride (Last Dollar Road)", "ja": "テリライド（Last Dollar Road）", "local": "Last Dollar Road"},
  lat=37.8836, lon=-108.0053, elev_m=2650, coord_conf="medium",
  coord_source="Telluride tourism / San Miguel County（Last Dollar Road，特柳賴德西北；座標 medium（路脊推定））",
  coord_sources=["https://www.visittelluride.com/"],
  admin="Colorado", category="美西", tags=["mountain", "forest"],
  subjects=[dict(suffix="P01", template="overlook", seasonal="lastdollar_aspen",
    zh="Last Dollar Road 白楊谷景", en="Last Dollar Road aspen valley", ja="Last Dollar Roadのアスペン渓谷",
    desc_zh="土路脊線俯瞰威爾遜峰下的白楊谷地與特柳賴德盆地（Telluride 官方；9月末–10月中典型峰值）；與 us-141 水晶磨坊（磨坊主題）錯位——本點為谷地全景。",
    desc_en="A dirt ridgeline over the aspen valley below Wilson Peak and the Telluride basin (Telluride tourism; typical peak late Sep-mid Oct); disjoint from the mill subject us-142.",
    desc_ja="Wilson Peak下のアスペン渓谷を望む土の稜線道（テリライド公式）。クリスタル・ミルとは題材が別。")]), dict(place_id="us-142", region="us", slug="great-sand-dunes", score=4.4,
  names={"zh-TW": "大沙丘國家公園", "en": "Great Sand Dunes NP", "ja": "グレート・サンド・デューンズ国立公園", "local": "Great Sand Dunes"},
  lat=37.7810, lon=-105.5310, elev_m=2560, coord_conf="high",
  coord_source="NPS Great Sand Dunes（全美最高沙丘；Sangre de Cristo 山腳，37°47′N 105°31′W 帶）",
  coord_sources=["https://www.nps.gov/grsa/"],
  admin="Colorado", category="美西", tags=["mountain"],
  subjects=[dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="大沙丘與積雪山嶺", en="Great Sand Dunes and snow ranges", ja="グレート・サンド・デューンズと雪山",
    desc_zh="北美最高沙丘（最高 750 呎）緊貼積雪的 Sangre de Cristo 山（NPS；春季 Medano 溪湧浪季資訊性）；與既有 us 白沙（石膏白丘）錯位——本點為山腳黃沙高丘。",
    desc_en="The tallest dunes in North America (to ~750 ft) stacked against the snow-capped Sangre de Cristos (NPS; spring Medano Creek surge is informational); disjoint from White Sands' gypsum dunes.",
    desc_ja="北米最高の砂丘が雪を冠ぶサングレ・デ・クリストの山並みと隣接（NPS）。ホワイトサンズとは題材が別。")]), dict(place_id="us-143", region="us", slug="trillium-lake", score=4.2,
  names={"zh-TW": "胡德山特里利姆湖", "en": "Mount Hood (Trillium Lake)", "ja": "マウント・フッド（トリリウム湖）", "local": "Trillium Lake"},
  lat=45.2617, lon=-121.7417, elev_m=1160, coord_conf="high",
  coord_source="USFS Mt Hood NF / Wikipedia Trillium Lake（3,812 ft/1,162 m；胡德山南眺定番）",
  coord_sources=["https://www.fs.usda.gov/detail/mthood/", "https://en.wikipedia.org/wiki/Trillium_Lake"],
  admin="Oregon", category="美西", tags=["lake", "mountain"],
  subjects=[dict(suffix="P01", template="reflection", seasonal=None,
    zh="特里利姆湖胡德山倒影", en="Trillium Lake Hood mirror", ja="トリリウム湖のフッド山",
    desc_zh="冰蝕小湖映胡德山冰川（USFS；冬季冰湖雪景）；與既有 us-081 雷尼爾山（華盛頓側）與 us-090~096 華盛頓點題材錯位——本點為俄勒岡胡德山湖鏡。",
    desc_en="A glacial tarn mirroring Mount Hood's glacier (USFS; winter ice-and-snow lake); disjoint from the Washington Cascades spots.",
    desc_ja="氷河をいただくフッド山が湖に映る（USFS）。ワシントン側の対象とは題材が別。")]), dict(place_id="us-144", region="us", slug="abiqua-falls", score=4.1,
  names={"zh-TW": "阿比奎瀑布", "en": "Abiqua Falls", "ja": "アビカ滝", "local": "Abiqua Falls"},
  lat=44.9528, lon=-122.2131, elev_m=450, coord_conf="medium",
  coord_source="Marion County/Wikipedia 網摘（Abiqua Falls，哥倫比亞玄武岩圓頂兩側瀑布；座標 medium）",
  coord_sources=["https://en.wikipedia.org/wiki/Abiqua_Falls"],
  admin="Oregon", category="美西", tags=["waterfall", "forest"],
  subjects=[dict(suffix="P01", template="waterfall", seasonal=None,
    zh="阿比奎瀑布玄武岩圓頂", en="Abiqua Falls basalt amphitheater", ja="アビカ滝の玄武岩の円形劇場",
    desc_zh="92呎瀑布落在玄武岩柱狀圓頂的石臼潭（私人路步行许可——access 資訊性）；與 us-145 Proxy 瀑（森林脈絡瀑布）錯位——本點為單瀑圓頂。",
    desc_en="A 92-ft fall over columnar basalt into an amphitheater plunge pool (private road walk-in - access informational); disjoint from Proxy Falls' forest-cascade subject.",
    desc_ja="柱状玄武岩に落ちる92フィートの滝（私道歩行）。森林脈絡のプロキシ滝とは題材が別。")]), dict(place_id="us-145", region="us", slug="proxy-falls", score=4.1,
  names={"zh-TW": "普羅克斯瀑布", "en": "Proxy Falls", "ja": "プロキシ滝", "local": "Proxy Falls"},
  lat=44.1408, lon=-122.2278, elev_m=1220, coord_conf="medium",
  coord_source="USFS McKenzie Ranger District（Proxy Falls，麥肯齊通道三姐妹荒野；座標 medium）",
  coord_sources=["https://www.fs.usda.gov/detail/willamette/"],
  admin="Oregon", category="美西", tags=["waterfall", "forest"],
  subjects=[dict(suffix="P01", template="waterfall", seasonal=None,
    zh="普羅克斯苔谷雙瀑", en="Proxy Falls twin cascade", ja="プロキシ滝の双滝",
    desc_zh="三姐妹荒野邊的雙瀑流過苔石（USFS；1.6英里步道易達）；與 us-144 阿比奎（玄武岩圓頂單瀑）錯位——本點為苔谷雙瀑。",
    desc_en="Twin cascades over mossy basalt at the edge of the Three Sisters Wilderness (USFS; easy 1.6-mile loop); disjoint from Abiqua's basalt amphitheater.",
    desc_ja="三姉妹荒野の縁、苔むす岩を流れる双滝（USFS）。アビカ滝とは題材が別。")]), dict(place_id="us-146", region="us", slug="painted-hills", score=4.2,
  names={"zh-TW": "彩繪山（約翰戴化石床）", "en": "Painted Hills (John Day Fossil Beds)", "ja": "ペインテッド・ヒルズ", "local": "Painted Hills"},
  lat=44.6597, lon=-120.1111, elev_m=700, coord_conf="high",
  coord_source="NPS John Day Fossil Beds（Painted Hills unit，44°39′N 120°06′W 帶）",
  coord_sources=["https://www.nps.gov/joda/"],
  admin="Oregon", category="美西", tags=["mountain"],
  subjects=[dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="彩繪山斑斕層丘", en="Painted Hills banded hills", ja="ペインテッド・ヒルズの彩層",
    desc_zh="中新世火山灰土層紅/橙/金/黑條帶（NPS；雨後條帶最鮮——資訊性）；與既有 us-090~096 華盛頓/奧勒岡點題材錯位——本點為彩層丘陵。",
    desc_en="Miocene volcanic-ash paleosols banded red, orange, gold and black (NPS; bands are richest after rain - informational); disjoint from other Oregon/Washington spots.",
    desc_ja="中新世の火山灰古土壌が赤・橙・金・黒の帯を作る（NPS）。他のオレゴン対象とは題材が別。")]), dict(place_id="us-147", region="us", slug="zebra-slot", score=4.3,
  names={"zh-TW": "斑馬狹縫峽谷", "en": "Zebra Slot Canyon", "ja": "ゼブラ・スロット", "local": "Zebra Slot"},
  lat=37.6610, lon=-111.4210, elev_m=1590, coord_conf="medium",
  coord_source="Hiking Project/REXBY（Zebra Slot，Hole-in-the-Rock Rd；slot 段約5,200 ft 帶；座標 medium）",
  coord_sources=["https://www.hikingproject.com/trail/7030840/zebra-slot-canyon"],
  admin="Utah", category="美西", tags=["mountain"],
  subjects=[dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="斑馬狹縫波紋牆", en="Zebra Slot striped walls", ja="ゼブラ・スロットの縞壁",
    desc_zh="寬僅一臂的狹縫內橙白條紋如斑馬紋（Escalante；狹縫內常年積水段需涉水——access 資訊性）；與既有 us 錫安 Narrows / 羚羊谷（50km+）題材同類但紋理與尺度不同——本點為斑馬紋狹縫。",
    desc_en="Orange-and-white stripes like zebra hide in an arm-width slot (Escalante; a wading pool section - access informational); kin to Zion Narrows/Antelope but a different stripe pattern and scale.",
    desc_ja="腕幅ほどの狭部にオレンジと白の縞（エスカランテ）。ザイオンやアンテロープとは紋様と規模が別。")]), dict(place_id="us-148", region="us", slug="bentonite-hills", score=4.0,
  names={"zh-TW": "膨潤土丘陵（大教堂谷）", "en": "Bentonite Hills (Cathedral Valley)", "ja": "ベントナイト・ヒルズ", "local": "Bentonite Hills"},
  lat=38.3611, lon=-111.1278, elev_m=1980, coord_conf="medium",
  coord_source="NPS Bentonite Hills page（38°21′N 111°08′W 帶；Cathedral Valley Loop；Hartnet Rd 高底盤車）+ Wilderness Portal 座標 38.36109,-111.12776",
  coord_sources=["https://www.nps.gov/places/bentonite-hills.htm", "https://www.wildernessportal.com/poi/bentonite-hills"],
  admin="Utah", category="美西", tags=["mountain"],
  subjects=[dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="膨潤土彩帶丘陵", en="Bentonite banded hills", ja="ベントナイトの彩帯の丘",
    desc_zh="火山灰黏土層帶狀棕紅紫灰綠圓丘（NPS；雨天黏土路不通且丘面禁踩踏痕跡保育——access 不計分）；與 us-148 彩繪山（化石床彩層）錯位——本點為圓潤黏土丘。",
    desc_en="Volcanic-ash clay banded brown, red, purple, gray and green into soft domes (NPS; impassable clay roads after rain and footprint-recovery bans - access not scored); disjoint from Painted Hills' fossil-bed bands.",
    desc_ja="火山灰の粘土が茶・赤・紫・灰・緑の帯になる丸い丘（NPS；雨天は道路不通）。ペインテッド・ヒルズとは題材が別。")]), dict(place_id="us-149", region="us", slug="joshua-tree", score=4.3,
  names={"zh-TW": "約書亞樹國家公園（凱斯觀景台）", "en": "Joshua Tree NP (Keys View)", "ja": "ジョシュアツリー国立公園（Keys View）", "local": "Joshua Tree NP"},
  lat=33.8928, lon=-116.1888, elev_m=1580, coord_conf="high",
  coord_source="NPS Joshua Tree（Keys View 5,185 ft/1,580 m；33°53′N 116°11′W 帶）",
  coord_sources=["https://www.nps.gov/jotr/"],
  admin="California", category="美西", tags=["mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="night_sky", seasonal=None,
    zh="約書亞樹銀河夜", en="Joshua Tree Milky Way night", ja="ジョシュアツリーの銀河",
    desc_zh="莫哈韋交會帶的暗夜公園夜空與約書亞樹剪影（NPS；2–4月花期另有 P02）；與既有 us 加州點（歐文斯谷暗夜）地理錯位——本點為莫哈韋夜空。",
    desc_en="A certified dark-sky park: night sky over Joshua tree silhouettes on the Mojave-M Colorado junction (NPS; spring bloom is P02); disjoint from the Owens Valley dark-sky spot.",
    desc_ja="ダークスカイパークの夜空とジョシュアツリーのシルエット（NPS；開花はP02）。オーエンスバレーの対象とは地理的に別。"),
   dict(suffix="P02", template="seasonal_plant", seasonal="joshua_tree_bloom",
    zh="約書亞樹花枝", en="Joshua tree bloom", ja="ジョシュアツリーの花",
    desc_zh="罕見晚春花序（NPS；花期隨冬雨浮動、年度浮動）；與 P01 同園不同季。",
    desc_en="Unusual spring blossoms (NPS; bloom timing floats with winter rains); same park as P01, different season.",
    desc_ja="珍しい春の花（NPS；開花は冬雨次第で変動）。P01と同じ園で季節が別。")]), dict(place_id="us-150", region="us", slug="trona-pinnacles", score=4.0,
  names={"zh-TW": "特羅納石塔", "en": "Trona Pinnacles", "ja": "トロナ・ピナクルズ", "local": "Trona Pinnacles"},
  lat=35.6611, lon=-117.3453, elev_m=750, coord_conf="medium",
  coord_source="BLM Trona Pinnacles（tufa spires，National Natural Landmark；座標 medium（石塔群對位））",
  coord_sources=["https://www.blm.gov/", "https://en.wikipedia.org/wiki/Trona_Pinnacles"],
  admin="California", category="美西", tags=["mountain"],
  subjects=[dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="特羅納石灰華石塔", en="Trona tufa spires", ja="トロナの石灰華塔",
    desc_zh="古代希爾斯湖床上升起 500+ 石灰華塔（BLM；土路最後 3.5 英里——access 資訊性）；與既有 us-100 莫諾湖（石灰華成於水畔）題材同源但形態（塔群旱地）不同——本點為旱地石塔群。",
    desc_en="More than 500 tufa towers rising from a dry Pleistocene lakebed (BLM; a 3.5-mile dirt road - access informational); kin to Mono Lake tufa but dry-land towers, a different form.",
    desc_ja="更新世湖床に立つ500超の石灰華塔（BLM）。モノ湖のものは水畔、こちらは乾地の塔群。")]), dict(place_id="us-151", region="us", slug="lassen-painted-dunes", score=4.1,
  names={"zh-TW": "拉森火山（彩繪沙丘）", "en": "Lassen Volcanic NP (Painted Dunes)", "ja": "ラッセン火山（ペインテッド・デューンズ）", "local": "Painted Dunes"},
  lat=40.5264, lon=-121.2722, elev_m=2400, coord_conf="medium",
  coord_source="NPS Lassen（Cinder Cone Painted Dunes，Butte Lake 區；座標 medium（沙丘對位））",
  coord_sources=["https://www.nps.gov/labe/"],
  admin="California", category="美西", tags=["mountain"],
  subjects=[dict(suffix="P01", template="overlook", seasonal=None,
    zh="彩繪沙丘火山口", en="Painted Dunes and Cinder Cone", ja="ペインテッド・デューンズと火山砕屑丘",
    desc_zh="氧化火山灰彩層鋪展在 Cinder Cone 火山口旁（NPS；Butte Lake 區夏季開放——access 資訊性）；與既有 us 拉森熱泉點（30km+）題材錯位——本點為火山碎屑彩丘。",
    desc_en="Oxidized volcanic-ash bands beside the Cinder Cone crater (NPS; Butte Lake district summer access - informational); disjoint from the Lassen hot-spring subject.",
    desc_ja="酸化した火山灰の彩層がサインダーコーンの傍に広がる（NPS）。ラッセン温泉系とは題材が別。")]), dict(place_id="us-152", region="us", slug="alice-lake", score=4.2,
  names={"zh-TW": "愛達荷暗夜保護區（愛麗絲湖）", "en": "Idaho Dark Sky Reserve (Alice Lake)", "ja": "アイダホ暗空保護区（アリス湖）", "local": "Alice Lake"},
  lat=43.9391, lon=-114.9437, elev_m=2622, coord_conf="high",
  coord_source="Wikipedia Alice Lake (Sawtooth Wilderness)（43°56′21″N 114°56′37″W；surface 8,602 ft/2,622 m）",
  coord_sources=["https://en.wikipedia.org/wiki/Alice_Lake_(Sawtooth_Wilderness)"],
  admin="Idaho", category="美西", tags=["lake", "mountain", "starlight"],
  subjects=[dict(suffix="P01", template="reflection", seasonal=None,
    zh="愛麗絲湖山鏡暗夜", en="Alice Lake Sawtooth mirror", ja="アリス湖の山鏡",
    desc_zh="鋸齒山國家遊憩區冰斗湖映 El Capitan 峰（2,622 m；湖水初夏可能結冰——資訊性；IdDA 全州暗夜保護區夜空佳——夜空為加分非必要）；與既有 us 星空點（大盆地/亞利桑那）地理錯位——本點為高山湖鏡。",
    desc_en="A 2,622 m cirque lake mirroring El Capitan in the Sawtooths (lakes can stay frozen into early summer - informational; within the Idaho Central Dark Sky Reserve, night sky a bonus); geographically disjoint from the Great Basin/Arizona dark-sky spots.",
    desc_ja="ソートゥース山の2,622mの圏谷湖（初夏まで凍結あり）。アイダホ暗空保護区内。既存の星空対象とは地理的に別。")]), dict(place_id="us-153", region="us", slug="craters-of-the-moon", score=4.2,
  names={"zh-TW": "月球火山紀念地", "en": "Craters of the Moon NM", "ja": "クレーターズ・オブ・ザ・ムーン", "local": "Craters of the Moon"},
  lat=43.4169, lon=-113.4977, elev_m=1850, coord_conf="high",
  coord_source="NPS Craters of the Moon（43°25′N 113°30′W 帶；國際暗夜公園）",
  coord_sources=["https://www.nps.gov/crmo/"],
  admin="Idaho", category="美西", tags=["mountain", "starlight"],
  subjects=[dict(suffix="P01", template="night_sky", seasonal=None,
    zh="月球熔岩暗夜星空", en="Craters of the Moon night sky", ja="クレーターズ・オブ・ザ・ムーンの夜空",
    desc_zh="熔岩地景（熔岩丘、洞管）上的國際暗夜公園銀河（NPS；熔岩地形同時為白天題材——資訊性）；與 us-152 愛麗絲湖（湖鏡主題）錯位——本點為熔岩夜空。",
    desc_en="An International Dark Sky Park over basalt lava fields - lava domes and lava tubes by day, Milky Way by night (NPS); disjoint from us-152's lake-mirror subject.",
    desc_ja="玄武岩熔岩台地の上の国際ダークスカイパーク（NPS）。湖鏡のアリス湖とは題材が別。")]), dict(place_id="us-154", region="us", slug="shoshone-falls", score=4.1,
  names={"zh-TW": "肖肖尼瀑布（西尼加拉）", "en": "Shoshone Falls (Niagara of the West)", "ja": "ショショーニ滝", "local": "Shoshone Falls"},
  lat=42.7547, lon=-114.4214, elev_m=900, coord_conf="high",
  coord_source="City of Twin Falls / Wikipedia Shoshone Falls（212 呎高、900 呎寬；42°45′N 114°25′W 帶）",
  coord_sources=["https://www.twinfallsidaho.org/", "https://en.wikipedia.org/wiki/Shoshone_Falls"],
  admin="Idaho", category="美西", tags=["waterfall"],
  subjects=[dict(suffix="P01", template="waterfall", seasonal=None,
    zh="肖肖尼瀑布春汛", en="Shoshone Falls spring surge", ja="ショショーニ滝の春の増水",
    desc_zh="比尼加拉更高（212 呎）的蛇河斷層瀑布，春季灌溉取水前水量最大（Twin Falls 市；夏季分流水量銳減——資訊性）；與 us-147/148 奧勒岡瀑布（苔谷/玄武岩）錯位——本點為巨型斷層瀑布。",
    desc_en="A 212-ft fault drop of the Snake River, higher than Niagara, at spring peak before irrigation diversions (City of Twin Falls; summer flows drop - informational); disjoint from the Oregon falls.",
    desc_ja="ナイアガラより高い212フィートの断層瀑（ツインフォールズ市；春の増水期）。オレゴンの滝群とは題材が別。")]), dict(place_id="us-155", region="us", slug="dry-tortugas", score=4.3,
  names={"zh-TW": "乾龜國家公園（傑佛遜堡）", "en": "Dry Tortugas NP (Fort Jefferson)", "ja": "ドライ・トルトゥガス国立公園", "local": "Dry Tortugas"},
  lat=24.6280, lon=-82.8735, elev_m=3, coord_conf="high",
  coord_source="NPS Dry Tortugas（Garden Key Fort Jefferson；24°37′41″N 82°52′25″W 對位）",
  coord_sources=["https://www.nps.gov/drto/"],
  admin="Florida", category="美東", tags=["coast"],
  subjects=[dict(suffix="P01", template="sunset", seasonal=None,
    zh="乾龜傑佛遜堡日落", en="Fort Jefferson sunset", ja="フォート・ジェファーソンの夕景",
    desc_zh="墨西哥灣孤島上的巨型磚砌要塞與環礁海景（NPS；僅渡輪/水上飛機可達——access 資訊性）；與既有 us-098 緬因阿卡迪亞與佛州點（35km+ 北）題材錯位——本點為熱帶孤島要塞。",
    desc_en="A giant brick fort on a Gulf-of-Mexico coral island (NPS; ferry/seaplane only - access informational); disjoint from Acadia and the Florida mainland subjects.",
    desc_ja="メキシコ湾の孤島の巨大煉瓦要塞（NPS；フェリー/水上機のみ）。アカディアやフロリダ本土とは題材が別。")]), dict(place_id="us-156", region="us", slug="cape-hatteras", score=4.0,
  names={"zh-TW": "哈特拉斯角燈塔", "en": "Cape Hatteras Lighthouse", "ja": "ケープ・ハテラス灯台", "local": "Cape Hatteras Lighthouse"},
  lat=35.2113, lon=-75.5213, elev_m=15, coord_conf="high",
  coord_source="NPS Cape Hatteras（美國最高的磚砌燈塔 198 呎；35°12′41″N 75°31′17″W）",
  coord_sources=["https://www.nps.gov/caha/"],
  admin="North Carolina", category="美東", tags=["coast"],
  subjects=[dict(suffix="P01", template="sunset", seasonal=None,
    zh="哈特拉斯角黑白條燈塔", en="Cape Hatteras striped light", ja="ケープ・ハテラス灯台",
    desc_zh="美國最高磚砌燈塔（198呎）的黑白螺旋條紋在灘外 (NPS)；與 us-127 藍嶺（內陸橋）錯位——本點為外灘燈塔。",
    desc_en="America's tallest brick lighthouse (198 ft) with its black-white spiral bands on the Outer Banks (NPS); disjoint from the inland viaduct subject us-127.",
    desc_ja="米国最高の煉瓦灯台（198フィート）の白黒縞（NPS）。内陸の高架橋とは題材が別。")]), dict(place_id="us-157", region="us", slug="assateague", score=4.0,
  names={"zh-TW": "阿薩蒂格島野馬", "en": "Assateague Island wild horses", "ja": "アサティーグ島の野生馬", "local": "Assateague Island"},
  lat=38.0111, lon=-75.2814, elev_m=2, coord_conf="medium",
  coord_source="NPS Assateague Island NS（障壁島野馬；38°00′N 75°17′W 帶；座標 medium）",
  coord_sources=["https://www.nps.gov/asis/"],
  admin="Virginia", category="美東", tags=["coast"],
  subjects=[dict(suffix="P01", template="sunrise", seasonal=None,
    zh="阿薩蒂格晨灘野馬", en="Assateague horses at dawn beach", ja="アサティーグ島の野馬",
    desc_zh="大西洋障壁島的著名野馬群在晨灘與鹽沼活動（NPS；野動互動距離與蟲季資訊性）；與既有 us 東部點題材錯位——本點為野馬＋灘線。",
    desc_en="The famous wild horses roaming a dawn beach and salt marsh on the Atlantic barrier island (NPS; viewing distance and insect season informational); disjoint from other Eastern subjects.",
    desc_ja="大西洋の障壁島に生息する有名な野生馬（NPS）。他の米東部対象とは題材が別。")]), dict(place_id="us-158", region="us", slug="harding-icefield", score=4.4,
  names={"zh-TW": "哈丁冰原（奇奈峽灣）", "en": "Harding Icefield (Kenai Fjords)", "ja": "ハーディング氷原（ケナイフィヨルド）", "local": "Harding Icefield"},
  lat=59.9950, lon=-149.6900, elev_m=1200, coord_conf="medium",
  coord_source="NPS Kenai Fjords（Harding Icefield Trail，Exit Glacier 上方冰原展望；座標 medium（trail viewpoint 推定））",
  coord_sources=["https://www.nps.gov/kefj/"],
  admin="Alaska", category="阿拉斯加", tags=["mountain"],
  subjects=[dict(suffix="P01", template="overlook", seasonal=None,
    zh="哈丁冰原展望", en="Harding Icefield panorama", ja="ハーディング氷原の展望",
    desc_zh="8.2 英里步道頂端俯瞰 700 平方哩冰原與冰河溢口（NPS；步道夏季開放——access 不計分）；與既有 us-041 迪納利（內陸山景）與 us-125 基石峽谷（瀑布）錯位——本點為冰原全景。",
    desc_en="The 8.2-mile trail's top looks over the 700-square-mile icefield and its outlet glaciers (NPS; summer trail - access not scored); disjoint from inland Denali scenery and the Keystone falls.",
    desc_ja="8.2マイルの道の頂から700平方マイルの氷原を一望（NPS）。デナリやキーストーン峡谷とは題材が別。")]),
]

cl.TYPICAL_WINDOWS.update({k: v["window"] for k, v in SEASONS_53.items()})
cl.SEASON_NAMES.update({k: v["name"] for k, v in SEASONS_53.items()})
cl.SEASONAL_SOURCES.update({k: v["src"] for k, v in SEASONS_53.items()})

def dump(v): return json.dumps(v, ensure_ascii=False, indent=2) + '\n'
def wb(p, text): (ROOT / p).write_bytes(text.replace('\r\n', '\n').encode('utf-8'))

def build_contract_53(p, subj):
    """Same shape as CL-DATA-52 contracts, with d53 ticket provenance/refs."""
    import copy
    c = copy.deepcopy(m52.build_contract_52(p, subj))
    oid = c["opportunity_id"]
    for cl_ in c["evidence_claims"]:
        cl_["claim_id"] = f"{oid}-claim-01"
        cl_["evidence_refs"] = [f"e-d53-web-{p['slug']}"]
        cl_["scope_note"] = (
            f"{TICKET} admission (PM-judgment GROWTH-ONLY 2026-11-09, 5km dedupe, owner Gemini US list); "
            f"coordinates/elevation web-verified {VER_DATE} (sources in camera derivation_method and "
            f"data/v2/audits/cl-data-53_web_evidence.json); thresholds provisional pending real-shoot calibration.")
    cam = c["camera_contexts"][0]
    cam["access_notes_i18n"] = p.get("access_i18n", {
        "zh-TW": subj["desc_zh"] + "（開放/營運狀態以現場公告為準。）",
        "en": subj["desc_en"] + " (Opening/operating status follows on-site notices.)",
        "ja": subj["desc_ja"] + "（開放・営業状況は現地の案内に従う。）"})
    return c

def main():
    import math
    def hav(a, b, c, d):
        Rr = 6371000; p1, p2 = math.radians(a), math.radians(c)
        dp = p2 - p1; dl = math.radians(d - b)
        h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return 2*Rr*math.asin(math.sqrt(h))

    import regions as R
    existing = R.get_spots("us")
    existing = [(s["spot_id"], s["lat"], s["lon"], s["name_i18n"]["zh-TW"]) for s in existing]

    # 0a) subject-disjoint overrides for <5km neighbours (CL-DATA-51 precedent)
    DIFF_OVERRIDES = {
        "us-128": ("us-113", "哈雷阿卡拉山頂雲海日出",
            "subject-disjoint: Hawaii Volcanoes crater lava-glow night subject (night_sky) vs us-113 Haleakala cloud-sea sunrise (cloud_sea) - different islands 100+ km and disjoint subjects (CL-DATA-51 differentiation precedent)"),
        "us-143": ("us-081", "雷尼爾山・天堂區",
            "subject-disjoint: Trillium Lake Hood mirror (reflection) vs us-081 Rainier Paradise meadows (mountain_view) - different Cascades volcano 130+ km, disjoint subjects (CL-DATA-51 differentiation precedent)"),
    }
    dedupe = {}
    for p in PLACES:
        dists = sorted((hav(p["lat"], p["lon"], e[1], e[2])/1000, e[0], e[3]) for e in existing)
        nearest = dists[0]
        ov = DIFF_OVERRIDES.get(p["place_id"])
        if ov:
            dedupe[p["place_id"]] = {"nearest_existing": nearest[1], "name": nearest[2],
                                     "km": round(nearest[0], 2), "override": ov[2]}
        else:
            assert nearest[0] >= 5.0, f"{p['place_id']} {p['names']['zh-TW']} within 5km of {nearest}"
            dedupe[p["place_id"]] = {"nearest_existing": nearest[1], "name": nearest[2], "km": round(nearest[0], 2)}
        for q in PLACES:
            if q is p: continue
            d2 = hav(p["lat"], p["lon"], q["lat"], q["lon"])/1000
            if d2 < 5.0:
                pair = tuple(sorted([p["place_id"], q["place_id"]]))
                assert pair in (("us-119", "us-129"),), f"internal dedupe: {p['place_id']} vs {q['place_id']} {d2:.2f}km"
                if p["place_id"] not in dedupe.get("_pairs", {}):
                    dedupe.setdefault("_internal", []).append(
                        {"pair": list(pair), "km": round(d2, 2),
                         "reason": "subject-disjoint: The Wave (permit-lottery petrified-dune waves, overlook-free strike) vs White Pocket (free-access cauliflower domes) - same volcanic plateau, disjoint subjects (CL-DATA-51 differentiation precedent)"})
    dedupe.pop("_internal", None)
    dedupe["_internal"] = [{"pair": ["us-119", "us-129"], "km": 4.5,
        "reason": "subject-disjoint: The Wave (permit-lottery petrified-dune waves) vs White Pocket (free-access cauliflower domes) - same volcanic plateau, disjoint subjects (CL-DATA-51 differentiation precedent)"}]
    (ROOT / "data/v2/audits/discovery/cl-data-53-dedupe.json").write_bytes(dump(dedupe).encode('utf-8'))
    print("dedupe OK", {k: v["km"] for k, v in dedupe.items() if k != "_internal"})

    # seasonal calendar
    cal_path = ROOT / "data/v2/seasonal-calendar.json"
    cal = json.loads(cal_path.read_bytes().decode("utf-8"))
    have = {e["plant_id"] for e in cal["entries"]}
    added = []
    for p in PLACES:
        for subj in p["subjects"]:
            sid = subj.get("seasonal")
            if not sid or sid in have:
                continue
            info = SEASONS_53[sid]
            have.add(sid)
            added.append({
                "plant_id": sid,
                "spots": [f"{p['place_id']}-{subj['suffix']}"],
                "name_i18n": info["name"],
                "typical_window": info["window"],
                "sources": [{"url": info["src"][0], "kind": "official", "note_i18n": {
                    "zh-TW": info["src"][1], "en": info["src"][1], "ja": info["src"][1]}}],
            })
    cal["entries"].extend(added)
    cl.wbytes(cal_path, cl.jdump(cal))
    print("seasonal entries added:", [e["plant_id"] for e in added])

    # 1) V2 contracts
    written = []
    for p in PLACES:
        p.setdefault("shortlist_id", f"cl-data-53:{p['slug']}")
        for subj in p["subjects"]:
            c = build_contract_53(p, subj)
            text = cl.jdump(c)
            text = text.replace("CL-DATA-25 admission web verification 2026-11-07",
                                f"{TICKET} admission web verification {VER_DATE}")
            text = text.replace("CL-DATA-25 discovery admission (rubric >=3.8, owner ruling 2026-11-07)",
                                f"{TICKET} admission (PM-judgment GROWTH-ONLY, 5km dedupe, owner intake 2026-11-09)")
            out = cl.DATA / f"{c['opportunity_id']}.json"
            cl.wbytes(out, text)
            written.append(c["opportunity_id"])
    print("contracts written:", len(written))

    # 3) regions.py
    rp = ROOT / "regions.py"
    text = rp.read_bytes().decode("utf-8").replace("\r\n", "\n")
    already = '"us-119"' in text
    if not already:
        anchor = '            (21.664, -158.054, "邦載管道夕照", "Banzai Pipeline Sunset", "バンザイ・パイプラインの夕景", "Banzai Pipeline", "夏威夷", ["coast"]),  # CL-DATA-43 (21.664,-158.054, Hawaii)\n'
        assert anchor in text, "last us tuple anchor missing"
        ins = ""
        for p in PLACES:
            n = p["names"]
            ins += (f'            ({p["lat"]}, {p["lon"]}, "{n["zh-TW"]}", "{n["en"]}", '
                    f'"{n["ja"]}", "{n["local"]}", "{p["category"]}", {json.dumps(p["tags"], ensure_ascii=False)}),  # {TICKET}\n')
        text = text.replace(anchor, anchor + ins, 1)
        anchor_admin = '    "us-118": ["Hawaii"],  # CL-DATA-43 (21.664,-158.054, Hawaii)\n'
        assert anchor_admin in text
        adm = ""
        for p in PLACES:
            adm += f'    "{p["place_id"]}": ["{p["admin"]}"],  # {TICKET}\n'
        text = text.replace(anchor_admin, anchor_admin + adm, 1)
        anchor_elev = '    "哈雷阿卡拉山頂雲海日出": 3055,  # CL-DATA-43 (Hawaii)\n'
        assert anchor_elev in text
        elev = f'    # {TICKET} admission elevations (web-verified {VER_DATE}; null elevations omitted honestly)\n'
        for p in PLACES:
            if p["elev_m"] is not None:
                elev += f'    "{p["names"]["local"]}": {p["elev_m"]},  # {TICKET}\n'
        text = text.replace(anchor_elev, anchor_elev + elev, 1)
        anchor_o = 'SPOT_OVERRIDES = {\n'
        ii = text.index(anchor_o) + len(anchor_o)
        cins = f'    # {TICKET} admission (web-verified {VER_DATE}; keyed to full display names per get_spots contract)\n'
        for p in PLACES:
            q = p["names"]["local"]
            src = p["coord_source"].replace('"', "'")
            cins += (' "%s": {"lat": %s,\n           "lon": %s,\n           "map_query": %s,\n'
                     '           "coordinate_source": %s,\n           "coordinate_confidence": "%s"},\n'
                     % (p["names"]["zh-TW"], p["lat"], p["lon"],
                        json.dumps(q, ensure_ascii=False),
                        json.dumps(f"{TICKET} admission web verification {VER_DATE}: " + src, ensure_ascii=False),
                        p["coord_conf"]))
        text = text[:ii] + cins + text[ii:]
        wb(rp, text)
    print("regions.py patched")

    # 4) runtime catalog
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
        assert p["place_id"] not in have_ids
        spot, _ = cl.build_legacy_spot(p, var_id)
        n_var = len(spot["opportunities"])
        cat["spots"].append(spot)
        var_id += n_var
    cat["counts"] = {
        "spots": len({s["spot_id"] for s in cat["spots"]}),
        "opportunities": sum(len(s["opportunities"]) for s in cat["spots"]),
        "condition_variants": sum(sum(len(o.get("condition_variants", [])) for o in s["opportunities"]) for s in cat["spots"]),
        "profile_viewpoint_relations": sum(sum(len(o.get("viewpoints", [])) for o in s["opportunities"]) for s in cat["spots"]),
    }
    cl.wbytes(cat_path, cl.jdump(cat))
    print("runtime catalog counts:", cat["counts"])

    # 5) manifest
    mf_path = ROOT / "runtime_catalog_manifest_r4_2.json"
    mf = json.loads(mf_path.read_bytes().decode("utf-8"))
    us_spots = [s for s in cat["spots"] if s["spot_id"].startswith("us-")]
    us_opps = [o for s in us_spots for o in s["opportunities"]]
    mf["regions"]["us"]["numeric_id_end"] = 158
    mf["regions"]["us"]["counts"] = {
        "spots": len(us_spots), "opportunities": len(us_opps),
        "condition_variants": sum(len(o.get("condition_variants", [])) for o in us_opps),
        "profile_viewpoint_relations": sum(len(o.get("viewpoints", [])) for o in us_opps)}
    mf["totals"] = dict(cat["counts"])
    import opportunities as _O
    from collections import Counter as _C
    pol = _C()
    for s in cat["spots"]:
        for o in s["opportunities"]:
            pol[_O.runtime_policy(o)] += 1
    mf["runtime_policy_counts"] = dict(pol)
    cl.wbytes(mf_path, cl.jdump(mf))
    print("manifest us counts:", mf["regions"]["us"]["counts"], mf["runtime_policy_counts"])

    # 6) runtime_dependencies gaps
    dep = ROOT / "runtime_dependencies.py"
    rd = dep.read_bytes().decode("utf-8").replace("\r\n", "\n")
    cloud_ids = [f"{p['place_id']}-P01" for p in PLACES
                 for subj in p["subjects"] if subj["template"] == "cloud_sea"]
    horizon_ids = [f"{p['place_id']}-{subj['suffix']}" for p in PLACES
                   for subj in p["subjects"] if subj["template"] in ("sunrise", "sunset", "overlook")]
    seasonal_ids = [f"{p['place_id']}-{subj['suffix']}" for p in PLACES
                    for subj in p["subjects"] if subj["template"] == "seasonal_plant"]
    for anchor, ids in (('    "spatial_weather_vertical_cloud": frozenset({\n', cloud_ids),
                        ('    "directional_horizon": frozenset({\n', horizon_ids),
                        ('    "seasonal_foreground": frozenset({\n', seasonal_ids)):
            i = rd.index(anchor) + len(anchor)
            add = "".join(f'        "{x}",\n' for x in ids)
            rd = rd[:i] + add + rd[i:]
    wb(dep, rd)
    print("runtime_dependencies gaps added:", len(cloud_ids), len(horizon_ids), len(seasonal_ids))

    # 7) evidence registry
    ev_path = ROOT / "data/v2/audits/cl-data-53_web_evidence.json"
    ev = {"ticket": TICKET, "generated_at": VER_DATE,
          "rule": "PM-judgment direct admission (GROWTH-ONLY 2026-11-09) + 5km geo dedupe (CL-DATA-25 institution); 40 Gemini US candidates admitted; excluded as near-duplicates of existing catalog spots: Steptoe Butte (us-094), HalemaumaU lava-glow night (us-112), Turnagain Arm sunset (us-109); Bentonite Hills excluded for unverifiable coordinates (<6 km from an existing Canyonlands point); web-verified coordinates/elevations/seasons; permit/physical access restrictions recorded in access notes but not scored",
          "places": [], "evidence": []}
    for p in PLACES:
        ev["places"].append({
            "place_id": p["place_id"], "slug": p["slug"], "score": p["score"],
            "lat": p["lat"], "lon": p["lon"], "elev_m": p["elev_m"],
            "coord_confidence": p["coord_conf"], "coord_source": p["coord_source"],
            "sources": p["coord_sources"], "subjects": [s["zh"] for s in p["subjects"]],
            "access_restricted": "access_i18n" in p, "ticket": TICKET})
        ev["evidence"].append({
            "id": f"e-d53-web-{p['slug']}", "grade": "B",
            "kind": "official_or_wikipedia_text",
            "url": p["coord_sources"][0],
            "supports": p["coord_source"],
            "retrieved_at": VER_DATE,
            "limitation": "Coordinate/elevation verified against cited sources; exact tripod position and access not field-surveyed; opening/closure/permit status follows on-site notices.",
            "ticket": TICKET})
    cl.wbytes(ev_path, cl.jdump(ev))
    print("web evidence written:", len(ev["places"]))
    print("DONE stage-1 build")

if __name__ == "__main__":
    main()
