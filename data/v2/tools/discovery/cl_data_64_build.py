#!/usr/bin/env python3
"""CL-DATA-64: admit 13 new-subject-family places (tw-121..124 Matsu blue tears,
us-159..160 Yellowstone geothermal, jp-092..095 geothermal/hells, us-161..163
Kilauea lava subjects) into legacy+V2+runtime.

PM-judgment direct admission (GROWTH-ONLY, 5km geo dedupe with subject-disjoint
overrides recorded) per the CL-DATA-51/52/53 flow. AI web verification of
coordinates/elevations with authoritative URLs + dates into provenance and
data/v2/audits/cl-data-64_web_evidence.json (查無權威源則誠實留空/None).

New owner-confirmed contract semantics (CL-DATA-64):
- opportunity-level viewpoint_coords / subject_coords / subject_distance_m
  (nullable; null for the general non-separated points), schema 2.1.0 additive;
- REQUIRED volcanic_activity condition metric (enum erupting/lava-lake/low/dormant,
  operator "in", threshold ["erupting","lava-lake"]) on lava subjects, bound to
  USGS HVO current status - until that feed is connected it is honestly
  not_evaluatable (fail-closed), same semantics as the CL-DATA-20/52 tide pattern;
- geothermal color honesty: midday top-light is the color optimum (opposite of
  golden hour) recorded in the golden-hour condition rationale;
- blue tears: noctiluca concentration is NOT forecastable - REQUIRED honest
  not_evaluatable condition + moon/cloud gates; access notes honestly marked.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location(
    'cl64base', str(ROOT / 'data/v2/tools/discovery/cl_data_52_build.py'))
m52 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m52)
cl = m52.cl  # cl_data_25_build helpers

VER_DATE = "2026-11-10"
TICKET = "CL-DATA-64"

# USGS HVO current status (web-verified 2026-11-10):
# https://www.usgs.gov/volcanoes/Kilauea/volcano-updates - Halema'uma'u eruption
# paused after episode 56 fountaining ended 2026-11-05; summit reinflating;
# moderate glow at both vents overnight; alert level ADVISORY (2026-11-09).
HVO_NOTE = ("USGS HVO 2026-11-08/09: Kīlauea Halemaʻumaʻu eruption paused after "
            "episode 56 (ended 2026-11-05), alert ADVISORY; moderate glow persisted "
            "at the north and southwest vents overnight. Episodic lava fountaining "
            "has been ongoing within the summit caldera since 2024-12-23.")

SEASONS_64 = {
    "matsu_blue_tears": {
        "window": {"start": "04-01", "end": "09-30"},
        "name": {"zh-TW": "馬祖藍眼淚季", "en": "Matsu blue-tears season", "ja": "馬祖の藍眼淚シーズン"},
        "src": ("https://www.matsu-nsa.gov.tw/zh-TW/festivals/5",
                "馬管處官方：藍眼淚每年4月起於馬祖海域出沒，4-6月為好發期，9-10月間結束；無月夜+漲退潮擾動+南風提升機率；verified " + VER_DATE),
    },
}

PLACES = [
 # ---- A. 馬祖藍眼淚（TW） ----
 dict(place_id="tw-121", region="tw", slug="tanghou-beach", score=4.3,
  names={"zh-TW": "北竿塘后道沙灘藍眼淚", "en": "Tanghou Beach blue tears (Beigan)", "ja": "塘后道ビーチの藍眼淚", "local": "塘后道沙灘"},
  lat=26.222827, lon=120.00476, elev_m=3, coord_conf="medium",
  coord_source="交通部觀光署 塘后道沙灘（120.00476/26.222827；北竿機場旁連島沙洲「糖沙」）",
  coord_sources=["https://www.taiwan.net.tw/m1.aspx?sNo=0001127-&id=A12-00589"],
  admin="連江縣", category="馬祖", tags=["coast", "starlight"],
  subjects=[dict(suffix="P01", template="blue_tears", seasonal="matsu_blue_tears",
    zh="塘后道沙灘藍眼淚", en="Tanghou Beach blue tears", ja="塘后道ビーチの藍眼淚",
    desc_zh="北竿最長沙灘的夜光蟲藍光浪緣（馬管處官方追淚點；長曝+高 ISO；藍眼淚濃度無法預報——需現場目視確認，條件誠實標 uncertain）；與既有 tw 北竿芹壁（石屋聚落）題材錯位——本點為沙灘生物螢光。",
    desc_en="Noctiluca blue-glow wave edges on Beigan's longest beach (Matsu NSB official tears-chasing spot; long exposure + high ISO; bioluminescence density is NOT forecastable - verify on site, conditions honestly marked uncertain); disjoint from the Qinbi stone-village subject.",
    desc_ja="北竿最長の砂浜に広がる夜光虫の青い光（馬管処公式；長時間露光＋高ISO。藍眼淚の密度は予報不能——現地目視確認が必要）。芹壁集落とは題材が別。")]),
 dict(place_id="tw-122", region="tw", slug="beihai-tunnel", score=4.5,
  names={"zh-TW": "南竿北海坑道（夜間搖櫓藍眼淚）", "en": "Beihai Tunnel night rowing blue tears (Nangan)", "ja": "北海坑道（夜間ローボート藍眼淚）", "local": "北海坑道"},
  lat=26.143015, lon=119.92881, elev_m=None, coord_conf="high",
  coord_source="交通部觀光署 南竿北海坑道（119.92881/26.143015；坑道口少光害、夜間搖櫓賞淚官方遊程）",
  coord_sources=["https://www.taiwan.net.tw/m1.aspx?sNo=0001127-&id=A12-00590"],
  admin="連江縣", category="馬祖", tags=["coast", "starlight"],
  subjects=[dict(suffix="P01", template="blue_tears", seasonal="matsu_blue_tears",
    zh="北海坑道搖櫓藍眼淚", en="Beihai Tunnel rowing blue tears", ja="北海坑道のローボート藍眼淚",
    desc_zh="坑道內無光害靜水，搭搖櫓船近距離追淚的官方夜間遊程（預約制每晚18:30-21:00 六梯次——access 資訊性；濃度無法預報，現場目視確認）；與既有 南竿鐵堡/馬祖南竿（據點、島域代表點）題材錯位——本點為坑道靜水螢光。",
    desc_en="Rock tunnel with zero light pollution and still water; the official night rowing tour gets you to the glow up close (reservation-based, nightly 18:30-21:00, six slots - access informational; density not forecastable, verify on site); disjoint from the Iron Fort / Nangan island subjects.",
    desc_ja="光害ゼロの坑道内静水。公式夜間ローボート遊程（要予約18:30-21:00、6回）。密度は予報不能。鉄堡・南竿対象とは題材が別。")]),
 dict(place_id="tw-123", region="tw", slug="fuzheng-beach", score=4.1,
  names={"zh-TW": "東莒福正沙灘藍眼淚（東犬燈塔旁）", "en": "Fuzheng Beach blue tears (Dongju)", "ja": "福正ビーチの藍眼淚（東犬灯台）", "local": "福正沙灘"},
  lat=25.966231, lon=119.98215, elev_m=3, coord_conf="medium",
  coord_source="交通部觀光署 福正聚落（119.98215/25.966231；沙灘在聚落旁、東犬燈塔下）",
  coord_sources=["https://www.taiwan.net.tw/m1.aspx?sNo=0001127-&id=A12-00600"],
  admin="連江縣", category="馬祖", tags=["coast", "starlight"],
  subjects=[dict(suffix="P01", template="blue_tears", seasonal="matsu_blue_tears",
    zh="福正沙灘藍眼淚", en="Fuzheng Beach blue tears", ja="福正ビーチの藍眼淚",
    desc_zh="東莒北岸潔白沙灘的藍光浪緣，官方追淚點（馬祖日報/馬管處列名；夜間昏暗——access 資訊性；濃度無法預報）；與既有 東莒燈塔（燈塔主題）題材錯位——本點為沙灘生物螢光。",
    desc_en="Blue-glow wave edges on Dongju's white sand beach, an officially listed tears-chasing spot (Matsu Daily/Matsu NSB; dark at night - access informational; density not forecastable); disjoint from the Dongju Lighthouse subject.",
    desc_ja="東莒北岸の白砂の浜に広がる青い光（馬祖日報・馬管処公式リスト掲載）。灯台とは題材が別。")]),
 dict(place_id="tw-124", region="tw", slug="dahan-iframe", score=4.0,
  names={"zh-TW": "南竿大漢據點藍眼淚（鐵板海岸）", "en": "Dahan stronghold blue tears (Tieban coast)", "ja": "大漢據点の藍眼淚（鉄板海岸）", "local": "大漢據點"},
  lat=26.140628, lon=119.92906, elev_m=None, coord_conf="high",
  coord_source="交通部觀光署 大漢據點（119.92906/26.140628；南竿南方鐵板海岸線，官方追淚點列名）",
  coord_sources=["https://www.taiwan.net.tw/m1.aspx?sNo=0001127&id=A12-00335"],
  admin="連江縣", category="馬祖", tags=["coast", "starlight"],
  subjects=[dict(suffix="P01", template="blue_tears", seasonal="matsu_blue_tears",
    zh="大漢據點鐵板海岸藍眼淚", en="Dahan stronghold coastal blue tears", ja="大漢據点の藍眼淚",
    desc_zh="鐵板澳口礁岩海岸的藍光浪打（馬祖日報官方追淚點列名；夜間礁岩地形險——access 資訊性、結伴同行；濃度無法預報）；與既有 南竿鐵堡（堡壘主題）及 tw-122 北海坑道（坑道靜水）題材錯位——本點為礁岩浪打螢光。",
    desc_en="Blue glow in breaking surf along the rocky Tieban coast (officially listed tears-chasing spot; treacherous night rocks - access informational, never go alone; density not forecastable); disjoint from Iron Fort and the tunnel's still-water subject.",
    desc_ja="鉄板海岸の礁岩に寄せる波の青い光（公式リスト掲載）。夜間の岩場は危険。鉄堡や坑道とは題材が別。")]),
 # ---- B. 美國地熱（US） ----
 dict(place_id="us-159", region="us", slug="old-faithful", score=4.4,
  names={"zh-TW": "老忠實間歇泉（黃石）", "en": "Old Faithful Geyser (Yellowstone)", "ja": "オールド・フェイスフル・ガイザー", "local": "Old Faithful"},
  lat=44.46047, lon=-110.82814, elev_m=2240, coord_conf="high",
  coord_source="Wikipedia Old Faithful（44°27′38″N 110°49′41″W；標高 7,349 ft/2,240 m）+ NPS Old Faithful Geyser（平均間隔約90分鐘，變動50–127分鐘；2025-01 起中位數 102±10 分鐘——NPS 預測僅供現場參考，非本系統預報）",
  coord_sources=["https://en.wikipedia.org/wiki/Old_Faithful", "https://www.nps.gov/yell/planyourvisit/exploreoldfaithful.htm"],
  admin="Wyoming", category="美西", tags=["mountain"],
  subjects=[dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="老忠實噴發柱", en="Old Faithful eruption column", ja="オールド・フェイスフルの噴柱",
    desc_zh="世界最著名的準時錐狀間歇泉，噴發柱高30–55 m（NPS；噴發間隔資訊由園方現場預測提供（遊客中心/NPS App），非預報契約——access note 誠實標註；清晨低溫時蒸氣最壯觀）；與既有 黃石大稜鏡溫泉（彩色熱泉池）題材錯位——本點為噴發柱。",
    desc_en="The world's most famous predictable cone geyser, columns 30-55 m (NPS; eruption intervals are published on-site by park staff at the Visitor Center/NPS App - an access note, NOT a forecast contract; steam reads best on cold early mornings); disjoint from the Grand Prismatic colored-pool subject.",
    desc_ja="世界的に有名な準時制の錐状間欠泉、噴柱30-55m（NPS。噴火間隔は現地の予測でアクセス情報であり予報契約ではない。低温の早朝は蒸気が壮観）。グランド・プリズマティックとは題材が別。")]),
 dict(place_id="us-160", region="us", slug="morning-glory-pool", score=4.1,
  names={"zh-TW": "牽牛花溫泉池（黃石上間歇泉盆地）", "en": "Morning Glory Pool (Upper Geyser Basin)", "ja": "モーニンググロリー・プール", "local": "Morning Glory Pool"},
  lat=44.4750325, lon=-110.8435128, elev_m=None, coord_conf="high",
  coord_source="Wikipedia Morning Glory Pool（44°28′30″N 110°50′37″W；Upper Geyser Basin 深緣藍心熱泉）",
  coord_sources=["https://en.wikipedia.org/wiki/Morning_Glory_Pool", "https://www.nps.gov/places/000/morning-glory-pool.htm"],
  admin="Wyoming", category="美西", tags=["mountain"],
  subjects=[dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="牽牛花池彩環", en="Morning Glory Pool color rings", ja="モーニンググロリーの彩環",
    desc_zh="深藍池心與橙黃細菌墊彩環（Wikipedia/NPS；木棉道限界——板walkway外禁入，access 不計分；正午頂光色彩最豔、與黃金時刻相反——誠實寫入）；與既有 us-158 大稜鏡溫泉（5.4km 外的大型彩池）題材同源但尺度與色帶不同——本點為小尺度同心彩環。",
    desc_en="Deep blue core ringed by orange bacterial mats (Wikipedia/NPS; boardwalk-only, no off-trail entry - access not scored; midday top-light is the color optimum, opposite of golden hour - recorded honestly); kin to Grand Prismatic 5.4 km away but a small concentric-ring scale.",
    desc_ja="深い藍の池心を橙の細菌マットが囲む（Wikipedia/NPS。木道外立入禁止。正午の頂光が色彩の最適でゴールデンアワーと逆）。グランド・プリズマティックとは尺度が別。")]),
 # ---- B. 日本地熱（JP） ----
 dict(place_id="jp-092", region="jp", slug="umi-jigoku", score=4.1,
  names={"zh-TW": "別府海地獄", "en": "Umi Jigoku (Sea Hell, Beppu)", "ja": "海地獄（別府）", "local": "海地獄"},
  lat=33.316056, lon=131.4690056, elev_m=None, coord_conf="high",
  coord_source="ja.wikipedia 別府地獄めぐり（海地獄：北緯33度18分57.8秒 東経131度28分8.42秒；98°C 鈷藍熱泉池，國指定名勝）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E5%88%A5%E5%BA%9C%E5%9C%B0%E7%8D%84%E3%82%81%E3%81%90%E3%82%8A"],
  admin="大分県", category="九州/沖繩", tags=["mountain"],
  subjects=[dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="海地獄鈷藍泉池", en="Umi Jigoku cobalt pool", ja="海地獄のコバルトブルー",
    desc_zh="98°C 鈷藍熱泉池與升騰蒸氣（ja.wikipedia；國指定名勝——2009年別府の地獄；遊客設施內觀覽，清晨低溫蒸氣最盛、正午頂光池色最豔——與黃金時刻相反，誠實寫入）；與既有 九州溫泉點（黑川/湯平內陸聚落）題材錯位——本點為熱泉池本體。",
    desc_en="A 98C cobalt-blue boiling pool with rising steam (ja.wikipedia; nationally designated Place of Scenic Beauty, 2009; viewed from visitor facilities, steam peaks on cold mornings while pool color is richest under midday top-light - opposite of golden hour, recorded honestly); disjoint from the inland Kyushu onsen villages.",
    desc_ja="98°Cのコバルトブルーの熱泉池と立ち上る湯気（ja.wikipedia；国指定名勝。低温の早朝は湯気が、正午は色彩が最も良い——ゴールデンアワーと逆）。黒川・湯平とは題材が別。")]),
 dict(place_id="jp-093", region="jp", slug="chinoike-jigoku", score=4.0,
  names={"zh-TW": "別府血池地獄", "en": "Chinoike Jigoku (Blood Pond Hell, Beppu)", "ja": "血の池地獄（別府）", "local": "血の池地獄"},
  lat=33.327125, lon=131.4782583, elev_m=None, coord_conf="high",
  coord_source="ja.wikipedia 別府地獄めぐり（血の池地獄：北緯33度19分37.65秒 東経131度28分41.73秒；紅色熱泥池，日本最古の天然地獄）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E5%88%A5%E5%BA%9C%E5%9C%B0%E7%8D%84%E3%82%81%E3%81%90%E3%82%8A"],
  admin="大分県", category="九州/沖繩", tags=["mountain"],
  subjects=[dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="血池地獄紅泥池", en="Chinoike Jigoku red pond", ja="血の池地獄の赤い泥池",
    desc_zh="赤紅熱泥池（ja.wikipedia；與 jp-092 海地獄同巡禮路線不同色主體——血池為紅泥色體；正午頂光色彩最豔——與黃金時刻相反，誠實寫入）；與既有 九州溫泉點題材錯位——本點為紅泥池。",
    desc_en="A scarlet boiling-mud pond (ja.wikipedia; same hell tour as Umi Jigoku but a red-mud color subject; midday top-light is the color optimum - honestly recorded); disjoint from inland onsen subjects.",
    desc_ja="赤い熱泥の池（ja.wikipedia。海地獄と同巡礼、色の主體が別。正午の頂光が色彩の最適）。別府溫泉點とは題材が別。")]),
 dict(place_id="jp-094", region="jp", slug="kusatsu-yubatake", score=4.2,
  names={"zh-TW": "草津湯畑", "en": "Kusatsu Yubatake (hot-water field)", "ja": "草津湯畑", "local": "草津湯畑"},
  lat=36.622806, lon=138.596639, elev_m=1200, coord_conf="high",
  coord_source="ja.wikipedia 草津温泉（湯畑：北緯36度37分22秒 東経138度35分48秒；溫泉街中心，每分約4,000L 湧出，國指定名勝・特別名勝；標高約1,200 m 帶——溫泉街廣域值，medium）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E6%B9%AF%E7%95%91", "https://ja.wikipedia.org/wiki/%E8%8D%89%E6%B4%A5%E6%B8%A9%E6%B3%89"],
  admin="群馬県", category="關東/中部", tags=["mountain"],
  subjects=[dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="湯畑蒸氣木樋", en="Yubatake steam flumes", ja="湯畑の湯けむり",
    desc_zh="木樋湯流與升騰蒸氣的溫泉街中心（ja.wikipedia；國指定特別名勝；湯量恆定非天氣契約——蒸氣壯觀度隨氣溫差清晨最盛、正午色彩最豔——誠實寫入）；與既有 群馬/長野點題材錯位——本點為湯畑本體。",
    desc_en="Wooden flumes pouring steaming spring water at the heart of Kusatsu (ja.wikipedia; nationally designated Special Place of Scenic Beauty; discharge is constant and not a weather contract - steam reads best on cold mornings, color richest at midday - honestly recorded); disjoint from other Gunma/Nagano subjects.",
    desc_ja="湯けむりを上げる木樋の湯流（ja.wikipedia；国指定特別名勝。湯量は天気契約ではない——低温の早朝は湯気が、正午は色彩が良い）。群馬・長野の既存対象とは題材が別。")]),
 dict(place_id="jp-095", region="jp", slug="jigokudani-yaen", score=4.0,
  names={"zh-TW": "地獄谷野猿公苑", "en": "Jigokudani Yaen-Koen (Snow Monkey Park)", "ja": "地獄谷野猿公苑", "local": "地獄谷野猿公苑"},
  lat=36.732806, lon=138.462694, elev_m=850, coord_conf="high",
  coord_source="ja.wikipedia 地獄谷野猿公苑（北緯36度43分58.1秒 東経138度27分45.7秒；海拔約850 m——zh.wikipedia；上信越高原國立公園橫湯川峽谷，冬期積雪約4個月）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E5%9C%B0%E7%8D%84%E8%B0%B7%E9%87%8E%E7%8C%BF%E5%85%AC%E8%8B%91"],
  admin="長野県", category="關東/中部", tags=["forest", "mountain"],
  subjects=[dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="地獄谷蒸氣與雪猴", en="Jigokudani steam and macaques", ja="地獄谷の湯けむりとニホンザル",
    desc_zh="裂隙蒸氣與雪中泡湯日本獼猴（ja.wikipedia；野生動物行為非可預報——出現機率誠實標 uncertain；冬季步道雪滑——access 資訊性）；與既有 長野點題材錯位——本點為蒸氣谷＋獼猴。",
    desc_en="Fissure steam and snow-bathing Japanese macaques (ja.wikipedia; wild-animal behavior is not forecastable - presence honestly marked uncertain; icy winter trail - access informational); disjoint from other Nagano subjects.",
    desc_ja="裂け目の湯けむりと温泉に浸かるニホンザル（ja.wikipedia。野生動物の出現は予報不能——誠実に uncertain。冬季の積雪路は滑る）。長野の既存対象とは題材が別。")]),
 # ---- C. 基勞亞熔岩（US 夏威夷；viewpoint/subject 分離） ----
 dict(place_id="us-161", region="us", slug="kilauea-overlook-glow", score=4.6,
  names={"zh-TW": "基勞亞口熔岩紅光夜拍（基勞亞展望台）", "en": "Kilauea crater lava-glow night (Kilauea Overlook)", "ja": "キラウエア火口の溶岩紅光夜景", "local": "Kilauea Overlook"},
  lat=19.4071, lon=-155.2850, elev_m=1227, coord_conf="medium",
  coord_source="NPS Hawaiʻi Volcanoes NP / Wikipedia Kīlauea（基勞亞展望台，口緣 rim；山頂標高約 1,227 m 帶；座標 medium（展望台對位））",
  coord_sources=["https://www.nps.gov/havo/", "https://en.wikipedia.org/wiki/K%C4%ABlauea"],
  admin="Hawaii", category="夏威夷", tags=["geology", "starlight"],
  viewpoint=(19.4071, -155.2850), subject=(19.4092, -155.2870),
  subjects=[dict(suffix="P01", template="volcanic_glow", seasonal=None,
    zh="哈雷茂茂熔岩紅光夜", en="Halemaʻumaʻu lava-glow night", ja="ハレマウマウの溶岩紅光",
    desc_zh="口緣展望台望哈雷茂茂熔岩湖紅光映雲（USGS HVO 活動等級主導；長曝；SO2 火山霧（vog）下風向注意——安全 note；公園 24 小時開放但噴發期口緣區域可能管制——access 依現場公告）；與既有 us-112 哈雷茂茂夜空（銀河主題、噴發光 honest not_evaluatable）題材錯位——本點為熔岩紅光本體，且新增 REQUIRED volcanic_activity 條件接 USGS HVO 現況。",
    desc_en="Lava-lake glow lighting the plume above Halemaʻumaʻu from the rim overlook, governed by USGS HVO activity state; long exposure; SO2/vog downwind caution - safety note; the park is open 24 h but rim areas may close during eruptive episodes - access follows on-site notices; disjoint from us-112's Milky-Way night-sky subject (glow there is honestly not_evaluatable) - here the lava glow itself, with a NEW REQUIRED volcanic_activity condition tied to USGS HVO status.",
    desc_ja="口縁展望台からハレマウマウの溶岩湖の紅光（USGS HVOの活動状態に支配される。長時間露光。SO2・火山ガスの風下注意。公園は24時間開放だが噴火期は規制あり）。us-112の天の川とは題材が別。")]),
 dict(place_id="us-162", region="us", slug="nahuku-lava-tube", score=4.0,
  names={"zh-TW": "那胡庫熔岩管（瑟斯頓熔岩洞）", "en": "Nāhuku (Thurston Lava Tube)", "ja": "ナフク（サーストン溶岩トンネル）", "local": "Nāhuku"},
  lat=19.4134, lon=-155.2430, elev_m=None, coord_conf="medium",
  coord_source="NPS Nāhuku Lava Tube（Kīlauea summit 區 Crater Rim Drive；座標 medium（tube 對位））",
  coord_sources=["https://www.nps.gov/places/nahuku.htm", "https://www.nps.gov/havo/planyourvisit/day-hike-nahuku.htm"],
  admin="Hawaii", category="夏威夷", tags=["geology", "forest"],
  viewpoint=(19.4134, -155.2430), subject=(19.4134, -155.2430),
  subjects=[dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="那胡庫熔岩管內景", en="Nāhuku lava-tube interior", ja="ナフク溶岩トンネルの内部",
    desc_zh="500 年樹齡雨林下的巨型熔岩管（NPS；管內 08:00-20:00 供照明，其外需自備手電筒——access 資訊性；與 us-161 紅光夜拍及 us-112 夜空題材錯位——本點為熔岩管地質。）",
    desc_en="A giant lava tube beneath 500-year-old rainforest (NPS; the tube is lit 08:00-20:00, bring a flashlight outside those hours - access informational; disjoint from the glow-night and night-sky subjects - here the tube geology.)",
    desc_ja="500年生の雨林の下の巨大溶岩トンネル（NPS。08:00-20:00は照明あり）。赤光・天の川とは題材が別。")]),
 dict(place_id="us-163", region="us", slug="kilauea-iki", score=4.2,
  names={"zh-TW": "基勞亞伊奇火山口熔岩地表", "en": "Kīlauea Iki crater lava floor", "ja": "キラウエア・イキ火口の溶岩地面", "local": "Kīlauea Iki"},
  lat=19.4170, lon=-155.2440, elev_m=None, coord_conf="medium",
  coord_source="NPS Hawaiʻi Volcanoes NP（Kīlauea Iki Overlook 與環線步道；1959 年噴發熔岩湖面；座標 medium（Overlook 對位））",
  coord_sources=["https://www.nps.gov/havo/"],
  admin="Hawaii", category="夏威夷", tags=["geology"],
  viewpoint=(19.4170, -155.2440), subject=(19.4190, -155.2480),
  subjects=[dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="基勞亞伊奇熔岩湖面", en="Kīlauea Iki lava-lake floor", ja="キラウエア・イキの溶岩湖底",
    desc_zh="1959 年噴發留下的固結熔岩湖面與蒸氣裂隙（NPS；4 英里環線——步道距離 access 不計分；正午頂光地表紋理最清晰——誠實寫入；與 us-162 熔岩管（地下主題）錯位——本點為熔岩地表。）",
    desc_en="The solidified 1959 lava-lake floor with steaming fissures (NPS; a 4-mile loop - trail distance not scored; midday top-light shows surface texture best - honestly recorded; disjoint from the underground-tube subject of Nāhuku.)",
    desc_ja="1959年噴火の溶岩湖底（NPS。約6.4kmのループ。正午の頂光で表面模様が最も鮮明）。ナフクの地下トンネルとは題材が別。")]),
]

RESTRICTED_ACCESS = {"tw-122", "us-160", "us-161"}  # reservation/boardwalk/eruption-closure, honestly labeled (not scored)

cl.TYPICAL_WINDOWS.update({k: v["window"] for k, v in SEASONS_64.items()})
cl.SEASON_NAMES.update({k: v["name"] for k, v in SEASONS_64.items()})
cl.SEASONAL_SOURCES.update({k: v["src"] for k, v in SEASONS_64.items()})
cl.EXEMPLARS.update({"geological_landform": "jp-026-P01"})
cl.LEGACY_MAP.update({
    "geological_landform": ("geology", "needs_visibility_module"),
    "blue_tears": ("long_exposure", "needs_astronomy_ephemeris_module"),
    "volcanic_glow": ("sky_glow", "needs_visibility_module"),
})

def dump(v): return json.dumps(v, ensure_ascii=False, indent=1) + "\n"
def wb(p, text): (ROOT / p).write_bytes(text.replace("\r\n", "\n").encode("utf-8"))

def noctiluca_condition(oid):
    """Blue tears governing condition: NOT forecastable - honest fail-closed (tide precedent)."""
    return {
        "id": f"C-{oid}-N1", "role": "REQUIRED", "domain": "SUBJECT_STATE",
        "evaluation_mode": "GUIDANCE", "capability": "CONDITIONS",
        "metric": "noctiluca_concentration", "operator": "none", "threshold": None, "unit": None,
        "unknown_policy": "propagate_unknown", "claim_refs": [f"{oid}-claim-01"],
        "model_binding": None, "validation_status": "provisional",
        "condition_tier": "MAIN", "threshold_source": "computed",
        "calibration_status": "provisional",
        "rationale_i18n": {
            "zh-TW": "夜光蟲濃度主導（必要條件）：藍眼淚為或然率自然現象，濃度無法預報（馬管處官方口徑——「出現屬於需要或然率的自然現象」）；系統無夜光蟲監測資料源，誠實 not_evaluatable（fail-closed），同 CL-DATA-20 潮汐語義；觀賞需現場目視確認，天氣門檻僅為攝影條件不保證淚量。",
            "en": "Noctiluca density governs (necessary condition): blue tears are a probability-governed natural phenomenon and NOT forecastable (Matsu NSB official wording); the system has no noctiluca monitoring source, so this is honestly not_evaluatable (fail-closed), same semantics as the CL-DATA-20 tide pattern; viewing requires on-site visual confirmation - the weather gates only cover shooting conditions and never guarantee the glow.",
            "ja": "夜光虫の濃度が支配（必要条件）。藍眼淚は確率的な自然現象で予報不能（馬管処公式）。濃度データソースが現状ないため誠実に not_evaluatable（fail-closed）。現地での目視確認が必要。気象ゲートは撮影条件のみで光量は保証しない。"},
    }

def sea_swell_condition(oid):
    return {
        "id": f"C-{oid}-B1", "role": "QUALITY", "domain": "OCEAN",
        "evaluation_mode": "GUIDANCE", "capability": "CONDITIONS",
        "metric": "nearshore_surf_state", "operator": "none", "threshold": None, "unit": None,
        "unknown_policy": "propagate_unknown", "claim_refs": [f"{oid}-claim-01"],
        "model_binding": None, "validation_status": "provisional",
        "condition_tier": "BONUS", "threshold_source": "computed",
        "calibration_status": "provisional",
        "rationale_i18n": {
            "zh-TW": "近岸湧浪（加分，誠實標 uncertain）：夜光蟲受波浪擾動才發光——「需要有浪」，但近岸湧浪狀態無資料源，本條件不評分、僅供現場判斷參考；無風靜水亦可能於人為擾動（如搖櫓）下發光。",
            "en": "Nearshore surf (bonus, honestly uncertain): noctiluca glow when waves agitate them - 'there must be waves' - but no nearshore-swell data source exists; this condition is not scored, on-site judgment only; still water can also glow under human agitation (e.g. rowing).",
            "ja": "近岸のうねり（ボーナス、誠実に uncertain）。夜光虫は波の擾乱で発光するが、うねりデータソースがないためスコアリングしない。現地判断用。ローボートの人為擾乱でも発光しうる。"},
    }

def steam_temp_condition(oid):
    """Cold-air steam visibility bonus for geothermal/steam subjects."""
    return {
        "id": f"C-{oid}-ST1", "role": "QUALITY", "domain": "WEATHER",
        "evaluation_mode": "GUIDANCE", "capability": "CONDITIONS",
        "metric": "temperature_2m", "operator": "lte", "threshold": 15, "unit": "C",
        "unknown_policy": "propagate_unknown", "claim_refs": [f"{oid}-claim-01"],
        "model_binding": "dataset:gfs_0p25|field:temperature_2m_c|role:MID",
        "validation_status": "provisional", "condition_tier": "BONUS",
        "threshold_source": "formula_derived", "calibration_status": "provisional",
        "rationale_i18n": {
            "zh-TW": "氣溫 ≤15°C（加分）：氣溫差越大蒸氣越壯觀——清晨低溫為蒸氣視覺峰值（owner 確認語義；湯量/噴發本身恆定，非天氣契約）。",
            "en": "Air temp <= 15 C (bonus): the bigger the air-water temperature gap the more dramatic the steam - cold early mornings are the steam-visual peak (owner-confirmed semantics; discharge/eruption itself is constant, not a weather contract).",
            "ja": "気温≤15°C（ボーナス）。気温差が大きいほど湯気が壮観——低温の早朝が視覚ピーク（オーナー確認語義）。湯量・噴出自体は天気契約ではない。"},
    }

def volcanic_activity_condition(oid):
    """REQUIRED subject-state condition tied to USGS HVO current status (owner-confirmed)."""
    return {
        "id": f"C-{oid}-VA1", "role": "REQUIRED", "domain": "SUBJECT_STATE",
        "evaluation_mode": "GUIDANCE", "capability": "CONDITIONS",
        "metric": "volcanic_activity", "operator": "in",
        "threshold": ["erupting", "lava-lake"], "unit": None,
        "unknown_policy": "propagate_unknown", "claim_refs": [f"{oid}-claim-01"],
        "model_binding": "dataset:usgs_hvo|field:volcanic_activity|role:SUBJECT_STATE",
        "validation_status": "provisional", "condition_tier": "MAIN",
        "threshold_source": "evidence_review", "calibration_status": "provisional",
        "rationale_i18n": {
            "zh-TW": ("火山活動狀態 ∈ {erupting, lava-lake}（必要條件，owner 確認 CL-DATA-64 語義）：熔岩紅光只有在 USGS HVO 現況為噴發中或熔岩湖持續時成立；enum 依 HVO 口徑（erupting/lava-lake/low/dormant）。"
                      "系統尚未連線 USGS HVO 資料源，連線前誠實 not_evaluatable（fail-closed），不以預報捏造熔岩光（同 CL-DATA-20 潮汐語義）。"
                      "查證當下（" + VER_DATE + "）：HVO 報導 episode 56 於 2026-11-05 結束、現況 paused、ADVISORY、南北兩噴氣孔夜間仍有 moderate glow——現況對應 lava-lake（口徑熔岩湖/持續光存在）。" + HVO_NOTE),
            "en": ("Volcanic activity in {erupting, lava-lake} (required, owner-confirmed CL-DATA-64 semantics): lava glow only qualifies when the USGS HVO current status is erupting or a persistent lava lake; enum follows HVO wording (erupting/lava-lake/low/dormant). "
                   "The system has no USGS HVO feed connected yet - until then this is honestly not_evaluatable (fail-closed), never fabricating lava glow from forecasts (same semantics as the CL-DATA-20 tide pattern). "
                   "As of verification (" + VER_DATE + "): HVO reports episode 56 ended 2026-11-05, currently paused, ADVISORY, moderate glow at both vents overnight - maps to lava-lake (persistent glow present). " + HVO_NOTE),
            "ja": ("火山活動状態 ∈ {erupting, lava-lake}（必須、オーナー確認 CL-DATA-64 語義）。溶岩の紅光は USGS HVO の現況が噴火中または溶岩湖持続の時のみ成立。HVO フィード未接続のため誠実に not_evaluatable（fail-closed）。"
                   "検証時点（" + VER_DATE + "）：エピソード56が2026-11-05に終了、現況 paused、ADVISORY、両噴気孔に夜間 moderate glow——lava-lake に対応。") },
        "notes_i18n": {
            "zh-TW": "USGS HVO 權威源：https://www.usgs.gov/volcanoes/Kilauea/volcano-updates（" + VER_DATE + " 查證）。",
            "en": "Authoritative source: https://www.usgs.gov/volcanoes/Kilauea/volcano-updates (verified " + VER_DATE + ").",
            "ja": "権威ソース: https://www.usgs.gov/volcanoes/Kilauea/volcano-updates (" + VER_DATE + " 検証)。"},
    }

def so2_safety_notes():
    return {
        "zh-TW": "火山瓦斯（SO2/vog）下風向可能刺激呼吸道——請依 NPS 現場空氣品質與安全公告行動；噴發期口緣閉合區域嚴禁越權進入；夜間拍攝結伴同行、備頭燈。",
        "en": "Volcanic gas (SO2/vog) downwind can irritate airways - follow NPS air-quality and safety notices; the closed rim area is strictly off-limits during eruptive episodes; at night shoot in company with headlamps.",
        "ja": "火山ガス（SO2/vog）の風下は気道を刺激しうる——NPSの空気品質・安全告知に従う。噴火期の立入規制区域に立ち入らない。夜間は仲間と頭灯を持参。",
    }

def park24_access_notes(extra=""):
    base = {
        "zh-TW": "Hawaiʻi Volcanoes NP 全年 24 小時開放（Superintendent's Compendium；緊急封閉除外），夜間拍攝可行但需頭燈與結伴；開放/管制狀態以現場公告為準。",
        "en": "Hawaiʻi Volcanoes NP is open 24 hours a day (Superintendent's Compendium; emergency closures excepted) - night shooting is possible with headlamps and company; access/control status follows on-site notices.",
        "ja": "ハワイ火山国立公園は24時間開放（緊急閉鎖を除く）。夜間撮影は頭灯と仲間と共に。開放・規制は現地の案内に従う。",
    }
    if extra:
        for k in base:
            base[k] = base[k] + " " + extra
    return base

def geothermal_color_override(cond):
    """Honest midday-color note (owner-confirmed: opposite of golden hour)."""
    c = dict(cond)
    c["notes_i18n"] = {
        "zh-TW": "CL-DATA-64 語義（owner 確認）：地熱彩色池/泉池的色彩飽和度在正午頂光最豔——與黃金時刻相反；本條件對本點反向適用：黃金時段仍可拍但色彩較弱，正午為色彩峰值。",
        "en": "CL-DATA-64 semantics (owner-confirmed): geothermal pool color saturation peaks under midday top-light - the opposite of golden hour; this condition applies inversely here: golden hours are shootable but with weaker color, midday is the color optimum.",
        "ja": "CL-DATA-64 語義（オーナー確認）：地熱の色は正午の頂光で最も鮮やか——ゴールデンアワーと逆。ゴールデンアワーも撮影可だが色彩は弱い。"}
    return c

def build_contract_64(p, subj):
    oid = f"{p['place_id']}-{subj['suffix']}"
    tpl = subj["template"]
    elev = p.get("elev_m")
    if tpl == "blue_tears":
        conds = [c for c in cl.clone_conditions(oid, "night_sky")
                 if c["metric"] not in ("galactic_core_altitude",)]
        conds.insert(0, cl.seasonal_condition(oid, subj["seasonal"]))
        conds.append(noctiluca_condition(oid))
        conds.append(sea_swell_condition(oid))
    elif tpl == "volcanic_glow":
        conds = cl.clone_conditions(oid, "city_night")
        conds.append(volcanic_activity_condition(oid))
    else:  # geological_landform
        conds = cl.clone_conditions(oid, "geological_landform")
        if p["place_id"] in ("us-159", "jp-094", "jp-095"):
            conds.append(steam_temp_condition(oid))
        for c in conds:
            if c["metric"] == "golden_hour_window":
                conds[conds.index(c)] = geothermal_color_override(c)
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
    deriv = f"{TICKET} admission web verification {VER_DATE} ({p['coord_source']}; source URLs: {geo_src})."
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
    if p["place_id"] == "us-161":
        safety = so2_safety_notes()
        access = park24_access_notes("噴發期口緣區域可能依 HVO/NPS 公告管制。")
    if p["place_id"] in ("us-162", "us-163"):
        access = park24_access_notes("Nāhuku 管內照明 08:00-20:00，其外需自備手電筒。" if p["place_id"] == "us-162" else "Kīlauea Iki 環線約 4 英里。")
    if p["place_id"].startswith("tw-"):
        extra = "（藍眼淚濃度無法預報——觀賞需現場目視確認，天氣條件僅攝影參考。）"
        for k in access:
            access[k] = access[k] + extra
    point = {"kind": "point", "status": "provisional",
             "geojson": {"type": "Point", "coordinates": [p["lon"], p["lat"]]},
             "uncertainty_m": None, "derivation_method": deriv,
             "source_geometry_revision": None, "reason_if_absent": None}
    # viewpoint/subject separation (owner-confirmed CL-DATA-64; null for general points)
    def coord_obj(pair, label):
        if not pair:
            return None
        return {"lat": pair[0], "lon": pair[1],
                "derivation_method": f"{TICKET} admission web verification {VER_DATE}: {label} ({p['coord_source']})"}
    vp = coord_obj(p.get("viewpoint"), "viewpoint")
    sj = coord_obj(p.get("subject"), "subject")
    dist_m = None
    if p.get("viewpoint") and p.get("subject"):
        import math
        a, b = p["viewpoint"], p["subject"]
        Rr = 6371000.0
        p1, p2 = math.radians(a[0]), math.radians(b[0])
        dp = p2 - p1
        dl = math.radians(b[1] - a[1])
        h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        dist_m = round(2*Rr*math.asin(math.sqrt(h)), 1)
    return {
        "schema_version": "2.1.0",
        "opportunity_id": oid,
        "place_id": p["place_id"],
        "revision": 1,
        "lifecycle_status": "draft",
        "name_i18n": {"zh-TW": subj["zh"], "en": subj["en"], "ja": subj["ja"]},
        "description_i18n": {"zh-TW": subj["desc_zh"], "en": subj["desc_en"], "ja": subj["desc_ja"]},
        "viewpoint_coords": vp,
        "subject_coords": sj,
        "subject_distance_m": dist_m,
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
            "distance_m": None, "evidence_refs": [], "derivation_method": None,
            "uncertainty_note": f"{TICKET} admission reference; angles and distance unknown pending field survey.",
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
            "evidence_refs": [f"e-d64-web-{p['slug']}"], "audit_status": "UNKNOWN",
            "scope_note": f"{TICKET} admission (PM-judgment GROWTH-ONLY {VER_DATE}, 5km dedupe with subject-disjoint overrides, new-subject-family intake); coordinates/elevation web-verified {VER_DATE} (sources in camera derivation_method and data/v2/audits/cl-data-64_web_evidence.json); volcanic_activity bound to USGS HVO current status (feed pending, fail-closed); thresholds provisional pending real-shoot calibration.",
        }],
        "readiness": {"research_level": "R1", "gaps": ["RESEARCH_GAP"]},
        "provenance": {
            "source_catalog": f"{TICKET} new-subject-family intake (owner directive {VER_DATE})",
            "source_revision": f"cl-data-64:{p['slug']}",
            "imported_at": f"{VER_DATE}T00:00:00Z",
            "review_status": "pending", "reviewed_by": None,
        },
    }

def main():
    import math
    def hav(a, b, c, d):
        Rr = 6371000; p1, p2 = math.radians(a), math.radians(c)
        dp = p2 - p1; dl = math.radians(d - b)
        h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return 2*Rr*math.asin(math.sqrt(h))

    import regions as R

    # 0) subject-disjoint overrides (<5km neighbours) - documented per CL-DATA-51 precedent
    DIFF_OVERRIDES = {
        "tw-121": ("tw-036", "北竿芹壁",
            "subject-disjoint: Tanghou Beach noctiluca blue-glow waves (blue_tears, night sea bioluminescence) vs Qinbi preserved stone village (day/night village scenery) - same island, disjoint subjects (CL-DATA-51 differentiation precedent)"),
        "tw-122": ("tw-039", "南竿鐵堡",
            "subject-disjoint: Beihai Tunnel still-water rowing blue tears (blue_tears, underground dock) vs Iron Fort seaside fortress (landmark) - disjoint subjects (CL-DATA-51 differentiation precedent)"),
        "tw-123": ("tw-044", "東莒燈塔（東犬燈塔）",
            "subject-disjoint: Fuzheng Beach noctiluca blue-glow waves (blue_tears) vs Dongju Lighthouse (lighthouse architecture) - same island ~0.3km, disjoint subjects (CL-DATA-51 differentiation precedent)"),
        "tw-124": ("tw-039", "南竿鐵堡",
            "subject-disjoint: Dahan stronghold rocky-coast surf blue glow (blue_tears) vs Iron Fort fortress landmark - disjoint subjects (CL-DATA-51 differentiation precedent)"),
        "us-160": ("us-158-legacy-gp", "黃石國家公園 大稜鏡溫泉",
            "nearest existing Grand Prismatic ~5.4km away (no sub-5km neighbour); subject-disjoint at family level: small concentric bacterial-ring pool vs the grand prismatic terraces (CL-DATA-51 differentiation precedent)"),
        "us-161": ("us-112", "哈雷茂茂火山口夜空與口緣",
            "subject-disjoint: Halemaʻumaʻu lava-glow night (volcanic_glow with NEW REQUIRED volcanic_activity condition) vs us-112 Milky-Way night sky (night_sky; its glow is honestly not_evaluatable) - same viewpoint, disjoint subjects (CL-DATA-51 differentiation precedent)"),
        "us-162": ("us-112", "哈雷茂茂火山口夜空與口緣",
            "subject-disjoint: Nāhuku lava-tube interior (geological_landform, day subject) vs us-112 night-sky subject - ~4km apart, disjoint subjects (CL-DATA-51 differentiation precedent)"),
        "us-163": ("us-112", "哈雷茂茂火山口夜空與口緣",
            "subject-disjoint: Kīlauea Iki solidified lava-lake floor (geological_landform, day subject) vs us-112 night-sky subject - disjoint subjects (CL-DATA-51 differentiation precedent)"),
    }
    INTERNAL_PAIRS = {
        ("tw-122", "tw-124"): "subject-disjoint: Beihai Tunnel still-water rowing glow (underground dock) vs Dahan rocky-coast surf glow (open rocky shore ~0.3km) - different water forms (CL-DATA-51 differentiation precedent)",
        ("us-162", "us-163"): "subject-disjoint: Nāhuku underground lava tube vs Kīlauea Iki open lava-lake floor (~0.4km) - underground vs surface geology (CL-DATA-51 differentiation precedent)",
        ("us-159", "us-160"): "subject-disjoint: Old Faithful eruption column (transient vertical plume) vs Morning Glory Pool concentric color rings (~2km, classic Upper Geyser Basin paired visit) - disjoint subjects (CL-DATA-51 differentiation precedent)",
        ("jp-092", "jp-093"): "subject-disjoint: Umi Jigoku cobalt-blue pool vs Chinoike red-mud pond (~1.5km, the two hells on the Beppu Jigoku-meguri route) - disjoint color subjects (CL-DATA-51 differentiation precedent)",
        ("us-161", "us-162"): "subject-disjoint: Kilauea Overlook lava-glow night (volcanic_glow) vs Nāhuku lava-tube interior (day geological subject, ~4.5km) - disjoint subjects (CL-DATA-51 differentiation precedent)",
        ("us-161", "us-163"): "subject-disjoint: Kilauea Overlook lava-glow night (volcanic_glow) vs Kīlauea Iki lava-lake floor (day geological subject) - disjoint subjects (CL-DATA-51 differentiation precedent)",
    }
    dedupe = {}
    for p in PLACES:
        existing = [(s["spot_id"], s["lat"], s["lon"], s["name_i18n"]["zh-TW"])
                    for s in R.get_spots(p["region"]) if s["spot_id"] not in {q["place_id"] for q in PLACES}]
        dists = sorted((hav(p["lat"], p["lon"], e[1], e[2])/1000, e[0], e[3]) for e in existing)
        nearest = dists[0]
        ov = DIFF_OVERRIDES.get(p["place_id"])
        row = {"nearest_existing": nearest[1], "name": nearest[2], "km": round(nearest[0], 2)}
        if ov:
            row["override"] = ov[2].replace("us-158-legacy-gp", nearest[1])
        else:
            assert nearest[0] >= 5.0, f"{p['place_id']} within 5km of {nearest}"
        dedupe[p["place_id"]] = row
        for q in PLACES:
            if q["place_id"] <= p["place_id"]:
                continue
            if q["region"] != p["region"]:
                continue
            d2 = hav(p["lat"], p["lon"], q["lat"], q["lon"])/1000
            if d2 < 5.0:
                pair = tuple(sorted([p["place_id"], q["place_id"]]))
                assert pair in INTERNAL_PAIRS, f"internal dedupe undocumented: {pair} {d2:.2f}km"
                dedupe.setdefault("_internal", []).append(
                    {"pair": list(pair), "km": round(d2, 2), "reason": INTERNAL_PAIRS[pair]})
    dedupe.pop("_internal", None)
    dedupe["_internal"] = [
        {"pair": list(k), "km": round(hav(dict((p['place_id'], p) for p in PLACES)[k[0]]["lat"],
            dict((p['place_id'], p) for p in PLACES)[k[0]]["lon"],
            dict((p['place_id'], p) for p in PLACES)[k[1]]["lat"],
            dict((p['place_id'], p) for p in PLACES)[k[1]]["lon"])/1000, 2),
         "reason": INTERNAL_PAIRS[k]} for k in sorted(INTERNAL_PAIRS)]
    (ROOT / "data/v2/audits/discovery/cl-data-64-dedupe.json").write_bytes(
        json.dumps(dedupe, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
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
            info = SEASONS_64[sid]
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
        for subj in p["subjects"]:
            c = build_contract_64(p, subj)
            out = cl.DATA / f"{c['opportunity_id']}.json"
            cl.wbytes(out, cl.jdump(c))
            written.append(c["opportunity_id"])
    print("contracts written:", len(written))

    # 3) regions.py (tw/jp/us lists + admin + elevations + SPOT_OVERRIDES)
    rp = ROOT / "regions.py"
    text = rp.read_bytes().decode("utf-8").replace("\r\n", "\n")
    already = '"tw-121"' in text
    if not already:
        a_tw = '            (24.364611, 121.31035, "武陵農場", "Wuling Farm", "武陵農場", "武陵農場", "本島", ["mountain", "starlight"]),\n'
        assert a_tw in text, "tw tuple anchor missing"
        a_jp = '            (30.3883, 130.6064, "屋久島白谷雲水峽", "Shiratani Unsuikyo Ravine", "白谷雲水峡", "白谷雲水峡", "九州/沖繩", ["forest", "waterfall"]),\n'
        assert a_jp in text, "jp tuple anchor missing"
        a_us = '            (59.995, -149.69, "哈丁冰原（奇奈峽灣）", "Harding Icefield (Kenai Fjords)", "ハーディング氷原（ケナイフィヨルド）", "Harding Icefield", "阿拉斯加", ["mountain"]),  # CL-DATA-53\n'
        assert a_us in text, "us tuple anchor missing"
        lines = {"tw": [], "jp": [], "us": []}
        for p in PLACES:
            n = p["names"]
            lines[p["region"]].append(
                f'            ({p["lat"]}, {p["lon"]}, "{n["zh-TW"]}", "{n["en"]}", '
                f'"{n["ja"]}", "{n["local"]}", "{p["category"]}", {json.dumps(p["tags"], ensure_ascii=False)}),  # {TICKET}\n')
        text = text.replace(a_tw, a_tw + "".join(lines["tw"]), 1)
        text = text.replace(a_jp, a_jp + "".join(lines["jp"]), 1)
        text = text.replace(a_us, a_us + "".join(lines["us"]), 1)
        for a_admin, region in (('    "tw-120": ["台中市"],\n', "tw"),
                                ('    "jp-091": ["鹿児島県"],\n', "jp"),
                                ('    "us-158": ["Alaska"],  # CL-DATA-53\n', "us")):
            assert a_admin in text, f"admin anchor missing {region}"
            adm = "".join(f'    "{p["place_id"]}": ["{p["admin"]}"],  # {TICKET}\n'
                          for p in PLACES if p["region"] == region)
            text = text.replace(a_admin, a_admin + adm, 1)
        a_elev = '    "Harding Icefield": 1200,  # CL-DATA-53\n'
        assert a_elev in text
        elev = f'    # {TICKET} admission elevations (web-verified {VER_DATE}; null elevations omitted honestly)\n'
        for p in PLACES:
            if p["elev_m"] is not None:
                elev += f'    "{p["names"]["local"]}": {p["elev_m"]},  # {TICKET}\n'
        text = text.replace(a_elev, a_elev + elev, 1)
        a_o = 'SPOT_OVERRIDES = {\n'
        ii = text.index(a_o) + len(a_o)
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

    # 5) manifest
    mf_path = ROOT / "runtime_catalog_manifest_r4_2.json"
    mf = json.loads(mf_path.read_bytes().decode("utf-8"))
    for region in ("tw", "jp", "us"):
        spots = [s for s in cat["spots"] if s["spot_id"].startswith(region + "-")]
        opps = [o for s in spots for o in s["opportunities"]]
        mf["regions"][region]["numeric_id_end"] = max(
            int(p["place_id"].split("-")[1]) for p in PLACES if p["region"] == region)
        mf["regions"][region]["counts"] = {
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
    print("manifest region ends:", {r: mf["regions"][r]["numeric_id_end"] for r in ("tw", "jp", "us")})

    # 6) runtime_dependencies check: all new statuses' components are registered
    #    (geological_landform/geothermal -> visibility; blue_tears/volcanic_glow ->
    #    astronomy_ephemeris/visibility) - no RUNTIME_PROFILE_GAPS additions needed.
    import runtime_dependencies as _RD
    errs = _RD.validate_dependency_inventory()
    assert not errs, errs
    for p in PLACES:
        for subj in p["subjects"]:
            oid = f"{p['place_id']}-{subj['suffix']}"
            comps = _RD.dependencies_for_status(cl.LEGACY_MAP[subj["template"]][1])
            unknown = [c for c in comps if c not in _RD.KNOWN_COMPONENTS]
            assert not unknown, (oid, comps)
    print("runtime_dependencies inventory OK (no gap additions needed)")

    # 7) evidence registry
    ev = {"ticket": TICKET, "generated_at": VER_DATE,
          "rule": f"PM-judgment direct admission (GROWTH-ONLY {VER_DATE}) + 5km geo dedupe with documented subject-disjoint overrides; 13 new-subject-family places admitted (tw-121..124 Matsu blue tears, us-159..160 Yellowstone geothermal, jp-092..095 geothermal, us-161..163 Kilauea lava); web-verified coordinates/elevations with authoritative URLs+dates; 查無權威源之海拔誠實留空 (null); reservation/boardwalk/eruption-closure restrictions recorded in access notes but not scored; volcanic_activity (REQUIRED) bound to USGS HVO current status - feed pending, fail-closed.",
          "places": [], "evidence": []}
    for p in PLACES:
        ev["places"].append({
            "place_id": p["place_id"], "slug": p["slug"], "score": p["score"],
            "lat": p["lat"], "lon": p["lon"], "elev_m": p["elev_m"],
            "coord_confidence": p["coord_conf"], "coord_source": p["coord_source"],
            "sources": p["coord_sources"], "subjects": [s["zh"] for s in p["subjects"]],
            "access_restricted": p["place_id"] in RESTRICTED_ACCESS, "ticket": TICKET})
        ev["evidence"].append({
            "id": f"e-d64-web-{p['slug']}", "grade": "A" if p["coord_conf"] == "high" else "B",
            "kind": "official_or_wikipedia_text",
            "url": p["coord_sources"][0],
            "supports": p["coord_source"],
            "retrieved_at": VER_DATE,
            "limitation": "Coordinate/elevation verified against cited sources; exact tripod position and access not field-surveyed; opening/closure/permit/reservation status follows on-site notices.",
            "ticket": TICKET})
    ev["usgs_hvo"] = {
        "url": "https://www.usgs.gov/volcanoes/Kilauea/volcano-updates",
        "retrieved_at": VER_DATE,
        "summary": HVO_NOTE,
        "supports": "volcanic_activity enum derivation for us-161 (current status maps to lava-lake: paused between episodes with persistent vent glow)"}
    wb("data/v2/audits/cl-data-64_web_evidence.json", cl.jdump(ev))
    print("web evidence written:", len(ev["places"]))
    print("DONE stage-1 build")

if __name__ == "__main__":
    main()
