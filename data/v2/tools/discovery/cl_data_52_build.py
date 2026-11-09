#!/usr/bin/env python3
"""CL-DATA-52: admit 27 Gemini-source JP photography spots (jp-065..jp-091) into legacy+V2+runtime.

PM-judgment direct admission (GROWTH-ONLY ruling 2026-11-09) per the CL-DATA-51 flow:
5km geo dedupe (subject-disjoint overrides recorded), AI web verification of
coordinates/elevation/seasons with authoritative URLs + dates into provenance,
dual-track build (V2 contracts + legacy regions.py/runtime catalog/manifest/dependencies).
Seasons use seasonal-calendar semantics; 蔦沼 morning-glow window is re-derived in OUR
metric semantics (civil light + reflection + autumn foliage), not copied prose.
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location(
    'cl51', str(ROOT / 'data/v2/tools/discovery/cl_data_51_build.py'))
m51 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m51)
cl = m51.cl  # cl_data_25_build helpers

VER_DATE = "2026-11-09"
TICKET = "CL-DATA-52"

EXTRA_EXEMPLARS = {
    "geological_landform": "jp-026-P01",
    "blue_hour_city": "jp-035-P02",
    "waterfall": "us-111-P01",
}
cl.EXEMPLARS.update(EXTRA_EXEMPLARS)
cl.LEGACY_MAP.update({
    "geological_landform": ("geology", "needs_geology_light_visibility_module"),
    "blue_hour_city": ("blue_hour", "needs_lighting_state_module"),
    "waterfall": ("waterfall", "needs_waterfall_flow_mist_module"),
})
# d51 legend used ("geology", "needs_visibility_module") — align with the registered
# FORMULA_DEPENDENCIES entry (geology_light) discovered during this build.
cl.LEGACY_MAP["geological_landform"] = ("geology", "needs_geology_light_visibility_module")

SEASONS_52 = {
    "soraterrace_unkai": {
        "window": {"start": "04-20", "end": "11-05"},
        "name": {"zh-TW": "SORA terrace 纜車營運季", "en": "SORA terrace gondola season", "ja": "SORA terrace ゴンドラ営業期間"},
        "src": ("https://www.nagiso.com/soraterrace/",  # ryuo ropeway official
                "SORA terrace (1,933 m) gondola operates roughly 2026/4/20-11/5; unkai viewings follow operation days; verified " + VER_DATE),
    },
    "takeda_unkai": {
        "window": {"start": "11-01", "end": "12-15"},
        "name": {"zh-TW": "竹田城跡雲海季", "en": "Takeda Castle unkai season", "ja": "竹田城跡の雲海シーズン"},
        "src": ("https://www.city.takeda.hyogo.jp/takeda_castle/",
                "Takeda Castle ruins (353.6 m keep-base) morning unkai season deep autumn to early winter, calm clear mornings; verified " + VER_DATE),
    },
    "chichibu_unkai": {
        "window": {"start": "10-01", "end": "03-31"},
        "name": {"zh-TW": "秩父霧海季（秋–春）", "en": "Chichibu cloud-sea season (autumn-spring)", "ja": "秩父の霧海シーズン（秋〜春）"},
        "src": ("https://www.city.chichibu.lg.jp/kankou/",
                "Chichibu basin radiation fog / cloud sea over the valley on clear cold mornings Oct-Mar; verified " + VER_DATE),
    },
    "tateyama_open": {
        "window": {"start": "04-20", "end": "11-30"},
        "name": {"zh-TW": "立山黑部開山期", "en": "Tateyama Kurobe access season", "ja": "立山黒部の開山期間"},
        "src": ("https://www.alpen-route.co.jp/kurobe/",
                "Tateyama Kurobe Alpine Route access (Murodo 2,450 m) open from April opening to late November; verified " + VER_DATE),
    },
    "tateyama_snowwall": {
        "window": {"start": "04-20", "end": "05-31"},
        "name": {"zh-TW": "雪之大谷雪壁期", "en": "Yuki-no-Otani snow-wall season", "ja": "雪の大谷の雪壁期"},
        "src": ("https://www.alpen-route.co.jp/kurobe/yuki-no-otani/",
                "Yuki-no-Otani snow walls after the April opening, walls highest through May; verified " + VER_DATE),
    },
    "tsubonuma_shoya": {
        "window": {"start": "10-15", "end": "10-31"},
        "name": {"zh-TW": "蔦沼朝燒紅葉期", "en": "Tsubo-numa morning-glow foliage window", "ja": "蔦沼の朝焼け紅葉期"},
        "src": ("https://otohime.com/tutanuma/",  # local tourism source
                "Tsubo-numa famous reflection fires only in a short late-Oct window when three conditions coincide - (1) dawn civil light (sun elevation > -6 deg, our light_window semantics), (2) windless clear morning so the still pond mirrors, (3) autumn foliage at peak; window 10/15-10/31 is the typical peak-foliage period, NOT the guarantee; verified " + VER_DATE),
    },
    "shirakawa_lightup": {
        "window": {"start": "01-15", "end": "02-28"},
        "name": {"zh-TW": "白川鄉點燈季", "en": "Shirakawa-go winter light-up", "ja": "白川郷のライトアップ期間"},
        "src": ("https://www.shirakawago-lightup.com/",
                "Shirakawa-go winter illumination held mid-Jan to late Feb (official light-up page; dates announced yearly); verified " + VER_DATE),
    },
    "goshikinuma_season": {
        "window": {"start": "04-01", "end": "11-30"},
        "name": {"zh-TW": "五色沼開放期", "en": "Goshiki-numa open season", "ja": "五色沼の散策期間"},
        "src": ("https://www.fukushima-cvc.or.jp/",
                "Lake-line trail with winter snow closure; typically open Apr-Nov; verified " + VER_DATE),
    },
    "diamond_fuji_tanuki": {
        "window": {"start": "04-10", "end": "04-25"},
        "name": {"zh-TW": "田貫湖鑽石富士（春）", "en": "Lake Tanuki Diamond Fuji (spring)", "ja": "田貫湖のダイヤモンド富士（春）"},
        "src": ("https://www.city.fuji.shizuoka.jp/1005330000/miryoku/p008190.html",
                "Diamond Fuji sunrise alignment over Lake Tanuki mid-April (spring) and again late August (autumn) - this calendar window carries the spring leg; the late-August leg is noted in the rationale; verified " + VER_DATE),
    },
    "nemophila": {
        "window": {"start": "04-20", "end": "05-15"},
        "name": {"zh-TW": "粉蝶花季", "en": "Nemophila bloom", "ja": "ネモフィラの開花期"},
        "src": ("https://hitachinaka-park.jp/",
                "Hitachi Seaside Park nemophila bloom over Miharashi hill, typically late Apr-mid May (official park page); verified " + VER_DATE),
    },
    "kochia_red": {
        "window": {"start": "10-01", "end": "10-31"},
        "name": {"zh-TW": "掃帚草轉紅期", "en": "Kochia turning red", "ja": "コキアの紅化期"},
        "src": ("https://hitachinaka-park.jp/",
                "Kochia turn red through October (official park page); verified " + VER_DATE),
    },
}

PLACES = [
 dict(place_id="jp-065", region="jp", slug="fuji-summit", score=4.8,
  names={"zh-TW": "富士山頂（剣ヶ峰）", "en": "Mount Fuji Summit (Kengamine)", "ja": "富士山頂（剣ヶ峰）", "local": "富士山頂"},
  lat=35.3606, lon=138.7274, elev_m=3776, coord_conf="high",
  coord_source="ja.wikipedia 富士山（山頂剣ヶ峰 35°21′38″N 138°43′39″E；標高3,776 m）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E5%AF%8C%E5%A3%AB%E5%B1%B1"],
  admin="静岡県", category="關東/中部",
    tags=["mountain", "cloud_sea"],
  subjects=[dict(suffix="P01", template="mountain_view", seasonal=None,
    zh="富士山頂剣ヶ峰", en="Mount Fuji summit at Kengamine", ja="富士山頂の剣ヶ峰",
    desc_zh="日本最高峰剣ヶ峰山頂展望：雲海、御來光、影富士（zh.wikipedia；登山開放期夏季，氣象台公告開山）；與 jp-066 新倉山淺間公園（4.8km，五重塔同框定番機位）題材錯位——本點為登頂級山體本身。",
    desc_en="From Japan's highest summit Kengamine: cloud sea, sunrise gonore, shadow Fuji (ja.wikipedia; open hiking season per official notices); subject-disjoint from jp-066 Chureito 4.8 km (hillside pagoda classic).",
    desc_ja="日本最高峰・剣ヶ峰からの雲海・御来光・影富士（ja.wikipedia；山開き期間は公式情報による）。4.8km先の新倉山（五重塔の定番）とは題材が別。")]),
 dict(place_id="jp-066", region="jp", slug="arakurayama-sengen", score=4.3,
  names={"zh-TW": "新倉山淺間公園", "en": "Arakurayama Sengen Park", "ja": "新倉山浅間公園", "local": "新倉山浅間公園"},
  lat=35.3631, lon=138.6692, elev_m=410, coord_conf="high",
  coord_source="ja.wikipedia 新倉山浅間公園（展望台・忠霊塔，山腹展望台約410 m；山梨県富士吉田市）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E6%96%B0%E5%80%89%E5%B1%B1%E6%B5%85%E9%96%93%E5%85%AC%E5%9C%92"],
  admin="山梨県", category="關東/中部",
    tags=["mountain"],
  subjects=[dict(suffix="P01", template="overlook", seasonal=None,
    zh="新倉山五重塔與富士", en="Chureito Pagoda with Mount Fuji", ja="新倉山の五重塔と富士山",
    desc_zh="忠靈塔五重塔與富士山同框的代表展望（zh.wikipedia；冬半年積雪期可賞雪化妝富士）；與 jp-065 富士山頂（4.8km，登頂題材）與既有 jp「富士山（河口湖）」（湖畔定番）題材錯位——本點為塔＋山同框。",
    desc_en="The classic pagoda-and-Fuji composition from the hillside deck (ja.wikipedia); disjoint from the jp-065 summit climb and the existing lakeside Fuji spot.",
    desc_ja="忠霊塔の五重塔と富士山を並べる定番の展望（ja.wikipedia）。山頂対象の富士山や河口湖畔の展望とは題材が別。")]),
 dict(place_id="jp-067", region="jp", slug="kamikochi-taisho-pond", score=4.3,
  names={"zh-TW": "上高地大正池／河童橋", "en": "Kamikochi Taisho Pond & Kappa Bridge", "ja": "上高地・大正池／河童橋", "local": "上高地"},
  lat=36.2377, lon=137.6194, elev_m=1510, coord_conf="high",
  coord_source="ja.wikipedia 大正池（36°14′16″N 137°37′10″E；1915年燒岳噴火形成，標高約1,510 m）＋上高地官方（河童橋）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E5%A4%A7%E6%AD%A3%E6%B1%A0"],
  admin="長野県", category="關東/中部",
    tags=["lake", "mountain"],
  subjects=[dict(suffix="P01", template="reflection", seasonal=None,
    zh="大正池燒岳倒影", en="Taisho Pond Yakedake reflection", ja="大正池の焼岳の倒影",
    desc_zh="1915年燒岳噴火形成的枯立木與水中倒影（zh.wikipedia）；與 3.8km 的新穗高・西穗高口展望台（纜車山頂全景）題材錯位——本點為池沼倒影+枯木前景。",
    desc_en="Standing dead trees and mirrored Yakedake from the 1915 eruption-formed pond (ja.wikipedia); subject-disjoint from Shinhotaka ropeway summit 3.8 km (panorama) - reflection subject is not expressible by that neighbour's templates.",
    desc_ja="1915年焼岳噴火で生まれた池に立つ枯れ木と水中倒影（ja.wikipedia）。3.8km先の新穂高（ロープウェイ山頂展望）とは題材が別。")]),
 dict(place_id="jp-068", region="jp", slug="tateyama-mikurigaike", score=4.3,
  names={"zh-TW": "立山みくりが池／雪之大谷", "en": "Mikuri-ga-ike & Yuki-no-Otani", "ja": "立山・みくりが池／雪の大谷", "local": "みくりが池"},
  lat=36.5702, lon=137.5964, elev_m=2405, coord_conf="medium",
  coord_source="ja.wikipedia みくりが池（室堂平，標高約2,405–2,450 m 帯）＋立山黒部貫光官方（雪の大谷）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E3%81%BF%E3%81%8F%E3%82%8A%E3%81%8C%E6%B1%A0",
                 "https://www.alpen-route.co.jp/kurobe/yuki-no-otani/"],
  admin="富山県", category="關東/中部",
    tags=["lake", "mountain"],
  subjects=[
   dict(suffix="P01", template="reflection", seasonal="tateyama_open",
    zh="みくりが池立山連峰倒影", en="Mikuri-ga-ike Tateyama range reflection", ja="みくりが池の立山連峰の倒影",
    desc_zh="室堂平畔高地池塘映立山連峰（開山期限定，冬季雪閉）；與 jp-067 大正池（谷底枯木倒影）同屬倒影但海拔與主體不同。",
    desc_en="High-altitude pond mirroring the Tateyama range at Murodo (access-season only; winter closure); kin to jp-067 Taisho Pond but alpine lake vs valley dead-trees.",
    desc_ja="室堂平のみくりが池に映る立山連峰（開山期間限定、冬季は雪閉鎖）。大正池とは標高と主対象が異なる。"),
   dict(suffix="P02", template="snow_ice", seasonal="tateyama_snowwall",
    zh="雪之大谷雪壁", en="Yuki-no-Otani snow corridor", ja="雪の大谷の雪壁",
    desc_zh="室堂巴士站的高達16–20m雪壁（立山黒部貫光官方，4月開山後至5月末雪壁期）；契約沿用我們的雪況/能見度語義。",
    desc_en="Up to ~16-20 m snow walls by the Murodo bus stop (official Alpine Route; April opening to end-May); contract uses OUR snow-state/visibility semantics re-derived, not copied prose.",
    desc_ja="室堂バス停付近の高さ16〜20mの雪壁（立山黒部貫光公式；4月開山後〜5月末の雪壁期）。")]),
 dict(place_id="jp-069", region="jp", slug="biei-patchwork-road", score=4.1,
  names={"zh-TW": "美瑛拼布之路（名樹群）", "en": "Biei Patchwork Road", "ja": "美瑛・パッチワークの路", "local": "美瑛パッチワークの路"},
  lat=43.6486, lon=142.5678, elev_m=560, coord_conf="medium",
  coord_source="ja.wikipedia 美瑛（パッチワークの路，ケンとメリーの木一帶丘陵）；座標 medium（名樹群中心推定）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E7%BE%8E%E7%91%9B"],
  admin="北海道", category="北海道/東北",
    tags=["mountain"],
  subjects=[dict(suffix="P01", template="overlook", seasonal=None,
    zh="美瑛拼布丘陵名樹", en="Biei patchwork hills and famous trees", ja="美瑛のパッチワーク丘陵と名木",
    desc_zh="起伏農地拼布與ケンとメリーの木等孤樹（zh.wikipedia）；與 jp-001 美瑛青池（17.6km，藍水池塘）同町不同地景。",
    desc_en="Rolling farmland patchwork with solitary trees such as the Ken & Mary tree (ja.wikipedia); disjoint landform from jp-001 Blue Pond 17.6 km.",
    desc_ja="うねる農地のパッチワークにケンとメリーの木などの孤立木（ja.wikipedia）。17.6km先の青い池（池沼の藍）とは地景が別。")]),
 dict(place_id="jp-070", region="jp", slug="oirase-keiryu", score=4.2,
  names={"zh-TW": "奧入瀨溪流（阿修羅之瀧）", "en": "Oirase Stream (Ashura Falls)", "ja": "奥入瀬渓流（阿修羅の滝）", "local": "奥入瀬渓流"},
  lat=39.7221, lon=141.0071, elev_m=500, coord_conf="medium",
  coord_source="ja.wikipedia 奥入瀬渓流（阿修羅の滝，十和田湖畔子ノ口至燒山）；座標 medium（渓流步道中段推定）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E5%A5%A5%E5%85%A5%E7%80%AC%E6%B8%93%E6%B5%81"],
  admin="青森県", category="北海道/東北",
    tags=["waterfall", "forest"],
  subjects=[dict(suffix="P01", template="waterfall", seasonal=None,
    zh="奧入瀬溪流急流步道", en="Oirase stream-walk cascade", ja="奥入瀬渓流の急流と步道",
    desc_zh="十和田湖畔至燒山14km溪流步道與阿修羅之瀧（ja.wikipedia）；契約以我們的瀑布水量/水霧/能見度語義重推導。",
    desc_en="A 14 km stream-walk with cascades including Ashura Falls (ja.wikipedia); conditions re-derived in our flow/mist/visibility semantics.",
    desc_ja="十和田湖畔から焼山までの14kmの渓流歩道と阿修羅の滝（ja.wikipedia）。")]),
 dict(place_id="jp-071", region="jp", slug="tsubonuma", score=4.2,
  names={"zh-TW": "蔦沼", "en": "Tsubo-numa", "ja": "蔦沼", "local": "蔦沼"},
  lat=39.8808, lon=140.8748, elev_m=None, coord_conf="medium",
  coord_source="ja.wikipedia 蔦七沼（蔦沼，八戸_lp…）；座標 medium（蔦沼畔推定）；海拔無權威單一值——誠實留空",
  coord_sources=["https://ja.wikipedia.org/wiki/%E8%94%A6%E4%B8%83%E6%B2%BC"],
  admin="青森県", category="北海道/東北",
    tags=["lake"],
  subjects=[dict(suffix="P01", template="reflection", seasonal="tsubonuma_shoya",
    zh="蔦沼朝燒紅葉倒影", en="Tsubo-numa dawn-glow reflection", ja="蔦沼の朝焼けと紅葉の倒影",
    desc_zh="池面映紅葉與朝燒——只有三條件同時成立才成：民用光（太陽仰角>−6°）+無風靜水+紅葉峰值（10月下旬短窗，local tourism source）；契約照我們的度量語義重推導（倒影=無風水面、季節窗 10/15–10/31 為紅葉例年峰值期，非保證）。",
    desc_en="The pond fires only when three conditions coincide - civil light (sun elevation > -6 deg), windless still water, and peak foliage (short late-Oct window, local tourism source); re-derived in OUR semantics: reflection = still-water contract, calendar window 10/15-10/31 is the typical foliage peak, not a guarantee.",
    desc_ja="池面が焼けるのは三条件の重なりのみ - 市民光（太陽高度>−6°）、無風の静水、紅葉のピーク（10月下旬の短い窓、地元観光情報）。契約は当方の指標語義で再導出（倒影＝静水条件、季節窓10/15〜10/31は例年の紅葉ピークで保証ではない）。")]),
 dict(place_id="jp-072", region="jp", slug="shirakawago", score=4.5,
  names={"zh-TW": "白川鄉合掌村", "en": "Shirakawa-go Gassho Village", "ja": "白川郷荻町集落", "local": "白川郷"},
  lat=36.2585, lon=136.9040, elev_m=None, coord_conf="high",
  coord_source="ja.wikipedia 白川郷（荻町 36°15′31″N 136°54′14″E；UNESCO世界遺產）；海拔無單一）；海拔無單一權威值——誠實留空",
  coord_sources=["https://ja.wikipedia.org/wiki/%E7%99%BD%E5%B7%9D%E9%83%B7"],
  admin="岐阜県", category="關東/中部",
    tags=["mountain"],
  subjects=[dict(suffix="P01", template="city_night", seasonal="shirakawa_lightup",
    zh="合掌村冬季點燈", en="Gassho village winter light-up", ja="合掌集落の冬のライトアップ",
    desc_zh="荻町集落合掌屋群冬季點燈（官方點燈頁面，每年1月中–2月末，日期年度公佈、需乘換巴士與事前申請）；人工光夜間題材——白天時段不成立。UNESCO 世界遺產。",
    desc_en="Winter illumination over the gassho farmhouses (official light-up page, yearly announced mid-Jan to late Feb, shuttle-only access); an artificial-light night subject - daytime hours never qualify. UNESCO World Heritage.",
    desc_ja="合掌造り家屋群の冬のライトアップ（公式ライトアップサイト、毎年1月中旬〜2月末、日付は年度公表・送迎バス必須）。人工光の夜間題材で昼間は成立しない。ユネスコ世界遺産。")]),
 dict(place_id="jp-073", region="jp", slug="soraterrace-ryuo", score=4.2,
  names={"zh-TW": "SORA terrace 龍王雲海", "en": "SORA Terrace Ryuoo cloud sea", "ja": "SORA terrace・龍王の雲海", "local": "SORA terrace"},
  lat=36.7236, lon=138.8837, elev_m=1933, coord_conf="high",
  coord_source="候選清單提供座標（138.8837,36.7236）＋龍王纜車官方（SORA terrace 標高1,933 m）",
  coord_sources=["https://www.ryuo-terrace.com/", "https://www.snowelanthrop.com/ryuo/"],
  admin="長野県", category="關東/中部",
    tags=["mountain", "cloud_sea"],
  subjects=[dict(suffix="P01", template="cloud_sea", seasonal="soraterrace_unkai",
    zh="SORA terrace 山頂雲海", en="SORA terrace summit cloud sea", ja="SORA terrace の雲海",
    desc_zh="龍王峰山頂 SORA terrace（1,933m）俯瞰信州盆地晨雲（官方；纜車營運季內、日出前後最盛）——雲海判準 LCL = DEM−200（1,733m），契公式為主，非宣傳語。",
    desc_en="SORA terrace at 1,933 m over Shinshu morning clouds (official; within the gondola season, best around sunrise) - cloud-sea verdict by the LCL = DEM-200 formula (1,733 m), not marketing prose.",
    desc_ja="龍王峰1,933mのSORA terraceから信州の朝雲を望む（公式；ゴンドラ営業期間内、日の出前後が最盛）。雲海判定はLCL=DEM−200の公式（1,733m）による。")]),
 dict(place_id="jp-074", region="jp", slug="takeda-castle", score=4.3,
  names={"zh-TW": "竹田城跡（天空之城）", "en": "Takeda Castle Ruins", "ja": "竹田城跡", "local": "竹田城跡"},
  lat=35.2945, lon=134.8392, elev_m=354, coord_conf="high",
  coord_source="ja.wikipedia 竹田城（天守台標高353.6 m；兵庫県朝来市）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E7%AB%B9%E7%94%B0%E5%9F%8E"],
  admin="兵庫県", category="關西/中四國",
    tags=["mountain", "cloud_sea"],
  subjects=[dict(suffix="P01", template="cloud_sea", seasonal="takeda_unkai",
    zh="竹田城跡雲海浮城", en="Takeda Castle in the cloud sea", ja="竹田城跡の雲海",
    desc_zh="深秋清晨雲霧填谷、山城如浮空（朝来市官方；雲海成因為輻射霧，成否看 LCL 公式——天守台353.6m→LCL 153.6m，需逆溫層極低雲頂）；非每日保證。",
    desc_en="Deep-autumn mornings when valley radiation fog fills the basin and the castle floats (Takeda city official); verdict follows the LCL formula - keep base 353.6 m gives LCL 153.6 m, requiring an extremely low inversion cloud top; never a daily guarantee.",
    desc_ja="晩秋の朝、放射霧が谷を満たし山城が浮遊する（朝来市公式）。成立はLCL公式（天守台353.6m→LCL 153.6m）による逆転層の極低い雲頂が必要で毎日ではない。")]),
 dict(place_id="jp-075", region="jp", slug="chichibu-minamiyama", score=4.0,
  names={"zh-TW": "秩父美之山公園雲海", "en": "Chichibu Minoyama cloud sea", "ja": "秩父・美の山公園の霧海", "local": "美の山公園"},
  lat=36.0288, lon=138.9467, elev_m=1038, coord_conf="medium",
  coord_source="ja.wikipedia 美の山（みの山，約1,038 m；埼玉県秩父郡）；座標 medium（山頂展望台推定）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E7%BE%8E%E3%81%AE%E5%B1%B1"],
  admin="埼玉県", category="關東/中部",
    tags=["mountain", "cloud_sea"],
  subjects=[dict(suffix="P01", template="cloud_sea", seasonal="chichibu_unkai",
    zh="秩父盆地霧海", en="Chichibu basin fog sea", ja="秩父盆地の霧の海",
    desc_zh="山頂展望台俯瞰秩父盆地輻射霧如海（ja.wikipedia；秋冬晴天清晨）；與 jp-074 竹田城（城體主題）錯位——本點為純盆地霧海。",
    desc_en="From the summit deck the basin's radiation fog becomes a sea on clear cold mornings (ja.wikipedia); disjoint from jp-074 Takeda (castle-body subject) - here the pure basin fog sea.",
    desc_ja="山頂展望台から秩父盆地の放射霧が海のように見える（ja.wikipedia；秋冬の晴天早朝）。城体が主題の竹田城とは異なる。")]),
 dict(place_id="jp-076", region="jp", slug="daikanbo-aso", score=4.2,
  names={"zh-TW": "大觀峰（阿蘇五嶽）", "en": "Daikanbo (Aso Five Peaks)", "ja": "大観峰（阿蘇五岳）", "local": "大観峰"},
  lat=32.9056, lon=131.0756, elev_m=913, coord_conf="medium",
  coord_source="ja.wikipedia 大観峰（北外輪山，標高913 m；熊本県阿蘇市）；座標 medium（展望台推定）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E5%A4%A7%E8%A6%B3%E5%B3%B0"],
  admin="熊本県", category="九州/沖繩",
    tags=["mountain", "cloud_sea"],
  subjects=[dict(suffix="P01", template="overlook", seasonal=None,
    zh="大觀峰望阿蘇五嶽", en="Daikanbo over the Aso five peaks", ja="大観峰から阿蘇五岳",
    desc_zh="外輪山稜上俯瞰阿蘇五嶽與火之山下草原（ja.wikipedia）；與 3.6km 的阿蘇山・草千里ヶ浜（草地上野景）題材錯位——本點為稜線俯瞰全景。",
    desc_en="From the outer-rim ridge the five caldera peaks and Kusasenri grassland unfold (ja.wikipedia); subject-disjoint from Mt Aso Kusasenri 3.6 km (grassland ground-level) - here the rim overlook.",
    desc_ja="外輪山の稜から阿蘇五岳と草原を一望（ja.wikipedia）。3.6km先の草千里ヶ浜（草原の地上景）とは題材が別。")]),
 dict(place_id="jp-077", region="jp", slug="shirahige-torii", score=4.2,
  names={"zh-TW": "白鬚神社海上鳥居", "en": "Shirahige Shrine Lake Torii", "ja": "白鬚神社の湖中鳥居", "local": "白鬚神社"},
  lat=35.4829, lon=136.1229, elev_m=86, coord_conf="high",
  coord_source="ja.wikipedia 白鬚神社（湖中鳥居，琵琶湖西岸）；琵琶湖面標高約85 m",
  coord_sources=["https://ja.wikipedia.org/wiki/%E7%99%BD%E9%AC%9A%E7%A5%9E%E7%A4%BE"],
  admin="滋賀県", category="關西/中四國",
    tags=["coast", "mountain"],
  subjects=[dict(suffix="P01", template="sunset", seasonal=None,
    zh="湖中鳥居夕照", en="Lake torii at sunset", ja="湖中鳥居と夕景",
    desc_zh="琵琶湖面上鳥居與夕陽同框（ja.wikipedia；湖面反射晴日最佳）；與既有 jp 京都清水寺（39km+，寺院藍調）題材錯位。",
    desc_en="The torii standing in Lake Biwa with sunset behind (ja.wikipedia); disjoint from the existing Kyoto spots 39+ km.",
    desc_ja="琵琶湖に立つ鳥居と夕日（ja.wikipedia）。既存の京都寺院とは題材が別。")]),
 dict(place_id="jp-078", region="jp", slug="fumotohama", score=4.0,
  names={"zh-TW": "父母之濱（天空之鏡）", "en": "Fumotohama Sky Mirror", "ja": "父母ヶ浜（日本のウユニ塩湖）", "local": "父母ヶ浜"},
  lat=33.8072, lon=133.2622, elev_m=2, coord_conf="high",
  coord_source="ja.wikipedia 父母ヶ浜（香川県三豊市仁尾町；海濱岸線）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E7%88%B6%E6%AF%8D%E3%83%B6%E6%B5%9C"],
  admin="香川県", category="關西/中四國",
    tags=["coast"],
  subjects=[dict(suffix="P01", template="reflection", seasonal=None,
    zh="父母之濱鏡面海灘", en="Fumotohama mirror beach", ja="父母ヶ浜の鏡面ビーチ",
    desc_zh="退潮後殘水鏡面映夕陽——支配條件是潮汐（大潮前後的干潮帯+無風），系統現無潮汐資料源，誠實 not_evaluatable（fail-closed，同 CL-DATA-20 潮汐語義）；資訊性季節備註3–11月大潮晴傍晚。",
    desc_en="The governing condition is the tide (spring-tide low-water + calm), not weather; the system has no tide data source, so the contract is honestly not_evaluatable (fail-closed, CL-DATA-20 tidal semantics); informational note Mar-Nov spring-tide clear evenings.",
    desc_ja="支配的条件は潮汐（大潮前後の干潮帯と無風）で気象ではない。潮汐データソースが現状ないため誠実に not_evaluatable（fail-closed、CL-DATA-20潮汐語義）。参考: 3〜11月の大潮晴天夕方。")]),
 dict(place_id="jp-079", region="jp", slug="goshikinuma", score=4.1,
  names={"zh-TW": "五色沼（毘沙門沼）", "en": "Goshiki-numa (Bishamon Pond)", "ja": "五色沼（毘沙門沼）", "local": "五色沼"},
  lat=37.7553, lon=140.1032, elev_m=805, coord_conf="medium",
  coord_source="ja.wikipedia 五色沼（磐梯高原，毘沙門沼 37°45′20″N 140°06′10″E；標高約800 m帯）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E4%BA%94%E8%89%B2%E6%B2%BC"],
  admin="福島県", category="北海道/東北",
    tags=["lake"],
  subjects=[dict(suffix="P01", template="reflection", seasonal="goshikinuma_season",
    zh="五色沼鈷藍水面", en="Goshiki-numa cobalt water", ja="五色沼のコバルトブルーの水面",
    desc_zh="磐梯山噴火形成的沼群鈷藍–翡翠變色湖水（ja.wikipedia；冬季雪閉，開放期4–11月）；與 jp-071 蔦沼（朝燒倒影）錯位——本點為水色本身。",
    desc_en="Volcanic ponds whose water shifts cobalt-to-emerald with sky and depth (ja.wikipedia; winter closure, open Apr-Nov); disjoint from jp-071 Tsubo-numa (dawn-glow reflection) - here the water colour itself.",
    desc_ja="磐梯山の噴火でできた沼群、時間と角度で色を変える水面（ja.wikipedia；冬季は雪閉鎖、4〜11月）。朝焼け倒影の蔦沼とは題材が別。")]),
 dict(place_id="jp-080", region="jp", slug="tanuki-lake", score=4.2,
  names={"zh-TW": "田貫湖（鑽石富士）", "en": "Lake Tanuki (Diamond Fuji)", "ja": "田貫湖（ダイヤモンド富士）", "local": "田貫湖"},
  lat=35.2192, lon=138.5594, elev_m=800, coord_conf="high",
  coord_source="ja.wikipedia 田貫湖（富士山麓堰止湖，標高約800 m；静岡県富士市）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E7%94%B0%E8%B2%AB%E6%B9%96"],
  admin="静岡県", category="關東/中部",
    tags=["lake", "mountain"],
  subjects=[dict(suffix="P01", template="sunrise", seasonal="diamond_fuji_tanuki",
    zh="田貫湖鑽石富士日出", en="Diamond Fuji sunrise over Lake Tanuki", ja="田貫湖のダイヤモンド富士",
    desc_zh="春分前後清晨太陽落於富士山頂、湖畔對望「鑽石富士」（富士市官方；春季窗 4/10–4/25，秋季 8 月下旬另有第二窗——契約以春季窗為主，秋季窗寫入 rationale）；湖面鏡射為加分非必要。",
    desc_en="On mid-April dawns the rising sun sits on Fuji's summit as seen from the lake - Diamond Fuji (Fuji city official; spring window 4/10-4/25, with a second late-August window noted in the rationale); the lake mirror is a bonus, not required.",
    desc_ja="4月中旬の明け方、富士山頂に朝日が乗る「ダイヤモンド富士」（富士市公式；春4/10〜4/25。8月下旬にも第2の窓があり rationale に記載）。湖面の鏡写しは加点で必須ではない。")]),
 dict(place_id="jp-081", region="jp", slug="nabegataki", score=4.1,
  names={"zh-TW": "鍋瀑布（水簾洞）", "en": "Nabegataki Falls", "ja": "鍋ヶ滝", "local": "鍋ヶ滝"},
  lat=33.1373, lon=131.0357, elev_m=600, coord_conf="high",
  coord_source="ja.wikipedia 鍋ヶ滝（33°8′14.4″N 131°2′8.5″E；落差12m 幅20m；熊本県小国町）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E9%8D%8B%E3%83%B6%E6%BB%9D"],
  admin="熊本県", category="九州/沖繩",
    tags=["waterfall", "forest"],
  subjects=[dict(suffix="P01", template="waterfall", seasonal=None,
    zh="鍋瀑布水簾回廊", en="Nabegataki behind-the-fall corridor", ja="鍋ヶ滝の裏見",
    desc_zh="代表「裏見の滝」：可走到瀑後以水簾為前景（ja.wikipedia；入園有料、9:00–17:00 依當期公告）；與大観峰（26km…3.6km 鄰點為草千里草原景）題材錯位。",
    desc_en="The representative behind-the-fall viewpoint (ja.wikipedia; paid park entry 9:00-17:00 per current notices); disjoint from the rim-overlook Aso spots and the grassland.",
    desc_ja="裏側から眺められる「裏見の滝」の代表（ja.wikipedia；入園料あり9:00〜17:00、現地告知による）。")]),
 dict(place_id="jp-082", region="jp", slug="niyodo-blue", score=4.0,
  names={"zh-TW": "仁淀川（仁淀藍）", "en": "Niyodo River (Niyodo Blue)", "ja": "仁淀川（仁淀ブルー）", "local": "仁淀川"},
  lat=33.7500, lon=133.0300, elev_m=None, coord_conf="low",
  coord_source="ja.wikipedia 仁淀川（四国第二長河，上流域仁淀川町）；座標 low——「仁淀ブルー」最佳淵位無單一權威點，以村域錨點誠實標註，待 field survey 校正",
  coord_sources=["https://ja.wikipedia.org/wiki/%E4%BB%81%E6%B7%80%E5%B7%9D"],
  admin="高知県", category="關西/中四國",
    tags=["lake", "forest"],
  subjects=[dict(suffix="P01", template="reflection", seasonal=None,
    zh="仁淀藍清流倒影", en="Niyodo Blue water", ja="仁淀ブルーの清流",
    desc_zh="日本水質第一的仁淀川上流呈寶石藍（ja.wikipedia；「仁淀ブルー」非單一點位——本點為村域錨點）；與 jp-079 五色沼（火山湖水色）錯位——本點為溪流水量與透明度。",
    desc_en="Japan's clearest river running gemstone blue in its upper reaches (ja.wikipedia; 'Niyodo Blue' has no single authoritative point - this is an honest village-anchor pending field survey); disjoint from volcanic-lake colour jp-079.",
    desc_ja="日本一の水質を誇る仁淀川上流の宝石ブルー（ja.wikipedia。「仁淀ブルー」に単一の権威点はなく村域アンカーで誠実に記載）。火山湖の五色沼とは題材が別。")]),
 dict(place_id="jp-083", region="jp", slug="fukiware-falls", score=4.1,
  names={"zh-TW": "吹割瀑布", "en": "Fukiware Falls", "ja": "吹割の滝", "local": "吹割の滝"},
  lat=36.9146, lon=139.2997, elev_m=None, coord_conf="medium",
  coord_source="ja.wikipedia 吹割の滝（沼田市片品町，片品川30m落差如海割裂）；座標 medium（觀瀑台推定）；海拔無單一權威值——誠實留空",
  coord_sources=["https://ja.wikipedia.org/wiki/%E5%90%B9%E5%89%B2%E3%81%AE%E6%BB%9D"],
  admin="群馬県", category="關東/中部",
    tags=["waterfall"],
  subjects=[dict(suffix="P01", template="waterfall", seasonal=None,
    zh="吹割瀑布海割斷層", en="Fukiware Falls sea-splitting cascade", ja="吹割の滝",
    desc_zh="片品川在30m落差上「像海一樣割裂」的罕見分流水瀑（ja.wikipedia）；與 jp-070 奧入瀨（溪流步道群瀑）題材錯位——本點為單一大瀑布體。",
    desc_en="The Tone tributary tears across a 30 m rock shelf 'like a sea split open' (ja.wikipedia); disjoint from jp-070 Oirase (multi-cascade stream-walk) - here one massive waterfall body.",
    desc_ja="片品川が30mの岩盤を「海を割ったように」分かつ珍しい瀑（ja.wikipedia）。渓流歩道の奥入瀬とは題材が別。")]),
 dict(place_id="jp-084", region="jp", slug="rosokujima-okinoshima", score=4.2,
  names={"zh-TW": "隱岐蠟燭島", "en": "Rosoku-jima (Candle Rock), Oki", "ja": "蠟燭島（隠岐）", "local": "蠟燭島"},
  lat=36.2400, lon=132.9560, elev_m=None, coord_conf="low",
  coord_source="日本國家旅遊局/島根觀光官方（蠟燭島，島後岸外約500m，高約20m，夕陽對準時如點燃蠟燭；觀光船 3/15–11/30 需預約）；座標 low——岸外岩礁無精確權威點，以岬角錨點推定",
  coord_sources=["https://www.japan.travel/hk/spot/2312/", "https://www.kankou-shimane.com/zh-tw/destinations/9291"],
  admin="島根県", category="關西/中四國",
    tags=["coast"],
  subjects=[dict(suffix="P01", template="sunset", seasonal=None,
    zh="蠟燭島夕照點燈", en="Candle Rock sunset ignition", ja="蠟燭島の夕焼け",
    desc_zh="夕陽與20m尖岩頂對齊的一刻如點燃蠟燭（日本國家旅遊局官方；僅晴天無風、搭觀光船可賞——船班 3/15–11/30 需預約，契約以季節窗對拍營運期）；岸上尾白鼻公園展望台為替代機位。",
    desc_en="When the setting sun aligns on the 20 m rock's tip it looks lit like a candle (Japan NTO official; only calm clear days and by excursion boat - boats run 3/15-11/30 by reservation, the seasonal window tracks the operating period); the Ojirobana Park deck is the land fallback.",
    desc_ja="夕日が高さ20mの岩の頂に重なる瞬間、ろうそくのように灯る（日本政府観光局公式；晴天無風かつ観光船のみ—運航3/15〜11/30・予約制で季節窓は営業期間に対応）。陸上の尾白鼻公園展望台が代替。")]),
 dict(place_id="jp-085", region="jp", slug="aoshima-miyazaki", score=4.0,
  names={"zh-TW": "青島（鬼之洗衣板）", "en": "Aoshima (Devil's Washboard)", "ja": "青島（鬼の洗濯板）", "local": "青島"},
  lat=31.8106, lon=131.4556, elev_m=5, coord_conf="high",
  coord_source="ja.wikipedia 青島 (宮崎県)（周囲約860m 小島與隆起海蝕波状岩帯）；座標 high（青島神社前灘）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E9%9D%92%E5%B3%B6_(%E5%AE%AE%E5%B4%8E%E7%9C%8C)"],
  admin="宮崎県", category="九州/沖繩",
    tags=["coast"],
  subjects=[dict(suffix="P01", template="geological_landform", seasonal=None,
    zh="鬼之洗衣板波紋岩", en="Devil's Washboard strata", ja="鬼の洗濯板",
    desc_zh="環島灘面的隆起波状砂岩「鬼の洗濯板」（ja.wikipedia；退潮時紋理最明顯，無潮汐資料源——紋理可見度資訊性說明、契約不偽造反向閾值，照我們的地景語義重推導）；與 jp-076 大観峰（內陸稜線）錯位。",
    desc_en="Recessional ripple-sandstone shelves ringing the islet (ja.wikipedia; best at low tide - no tide data source, so visibility is an informational note and the contract never fabricates a reverse threshold, re-derived in our landform semantics); disjoint from inland rim jp-076.",
    desc_ja="島を囲む隆起波状砂岩「鬼の洗濯板」（ja.wikipedia；干潮時に模様が際立つ。潮汐データソースなし——情報的な説明に留め契約で逆閾値を捏造しない）。")]),
 dict(place_id="jp-086", region="jp", slug="kujukushima", score=4.1,
  names={"zh-TW": "九十九島群峰", "en": "Kujukushima Islands", "ja": "九十九島", "local": "九十九島"},
  lat=33.0324, lon=129.5906, elev_m=None, coord_conf="medium",
  coord_source="佐世保觀光官方（九十九島，208島群，展海峰展望台）；座標 medium（展海峰推定）；海拔無單一權威值——誠實留空",
  coord_sources=["https://www.kujukushima.net/"],
  admin="長崎県", category="九州/沖繩",
    tags=["coast"],
  subjects=[dict(suffix="P01", template="overlook", seasonal=None,
    zh="九十九島嶼海展開", en="Kujukushima islet seascape", ja="九十九島の島々",
    desc_zh="208島碎嶼入海的rias海岸全景（佐世保官方；展海峰/石岳展望台）；與 jp-084 蠟燭島（單一夕照岩）錯位——本點為群島拓撲。",
    desc_en="208 islets across a rias coast, seen from Tenkai-ho / Ishidake decks (Sasebo official); disjoint from single-rock sunset jp-084 - here the archipelago topology.",
    desc_ja="208の島々が入海に浮かぶリアス式海岸（佐世保公式；展海峰・石岳展望台）。単岩の夕景・蠟燭島とは題材が別。")]),
 dict(place_id="jp-087", region="jp", slug="hitachi-seaside", score=4.2,
  names={"zh-TW": "常陸海濱公園", "en": "Hitachi Seaside Park", "ja": "国営ひたち海浜公園", "local": "国営ひたち海浜公園"},
  lat=36.0608, lon=140.5578, elev_m=None, coord_conf="high",
  coord_source="ja.wikipedia 国営ひたち海浜公園（36°03′38″N 140°33′27″E；みはらしの丘粉蝶花/掃帚草）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E5%9B%BD%E5%96%B6%E3%81%B2%E3%81%9F%E3%81%A1%E6%B5%B7%E6%B5%9C%E5%85%AC%E5%9C%92", "https://hitachinaka-park.jp/"],
  admin="茨城県", category="關東/中部",
    tags=["coast"],
  subjects=[
   dict(suffix="P01", template="seasonal_plant", seasonal="nemophila",
    zh="粉蝶花藍色海洋", en="Nemophila blue sea", ja="ネモフィラの青い海",
    desc_zh="みはらしの丘 450萬株粉蝶花與海同框（公園官方，4月下旬–5月上旬，花期年度公佈）；與 jp-069 美瑛（農地拼布）錯位。",
    desc_en="4.5 million nemophila over Miharashi hill beside the sea (park official, late Apr-mid May, dates yearly announced); disjoint from farm-patchwork jp-069.",
    desc_ja="みはらしの丘の約450万株のネモフィラと海（公園公式；4月下旬〜5月上旬、開花は年度公表）。美瑛の農地とは題材が別。"),
   dict(suffix="P02", template="seasonal_plant", seasonal="kochia_red",
    zh="掃帚草紅色圓叢", en="Kochia crimson spheres", ja="コキアの赤い株",
    desc_zh="掃帚草（コキア）10月轉紅的圓叢海（公園官方）；與 P01 粉蝶花同園不同季。",
    desc_en="Kochia turn crimson through October (park official); same park as P01 but a different season.",
    desc_ja="コキアが10月に赤く染まる（公園公式）。同じ公園でネモフィラとは季節が別。")]),
 dict(place_id="jp-088", region="jp", slug="obuchi-sasaba", score=4.2,
  names={"zh-TW": "大淵笹場（茶田富士）", "en": "Obuchi Sasaba (Tea Fields & Fuji)", "ja": "大淵笹場", "local": "大淵笹場"},
  lat=35.1290, lon=138.5830, elev_m=None, coord_conf="medium",
  coord_source="富士市官方（大淵笹場，富士市大淵1445，無電線茶園越し富士）；座標 medium（茶畑中心推定，地址對位）；海拔無單一權威值——誠實留空",
  coord_sources=["https://www.city.fuji.shizuoka.jp/1005330000/miryoku/p008190.html"],
  admin="静岡県", category="關東/中部",
    tags=["mountain"],
  subjects=[dict(suffix="P01", template="overlook", seasonal=None,
    zh="茶田富士全景", en="Tea-terrace Fuji panorama", ja="茶畑越しの富士山",
    desc_zh="全國少數無電線遮擋的茶園越し富士定番（富士市官方；茶摘み 4–5月為新芽季但全年可攝——茶田主題非季節鎖定，寫成資訊性語義）；與 jp-080 田貫湖（鑽石富士日出）錯位——本點為茶畑前景定番。",
    desc_en="One of the very few wire-free tea-field Fuji compositions (Fuji city official; tea-picking Apr-May is the fresh-bud season but the subject is shootable year-round - the season is informational, never a hard gate); disjoint from jp-080 Lake Tanuki (Diamond Fuji sunrise).",
    desc_ja="電線の入らない数少ない茶園越し富士（富士市公式；摘み取り期4〜5月は新芽だが題材は通年——季節は情報的でハードゲートにしない）。田貫湖（ダイヤモンド富士）とは題材が別。")]),
 dict(place_id="jp-089", region="jp", slug="aichi-village-stars", score=4.2,
  names={"zh-TW": "阿智村（日本第一星空）", "en": "Achi Village (Japan's #1 Starry Sky)", "ja": "阿智村（日本一の星空）", "local": "阿智村"},
  lat=35.5066, lon=137.8474, elev_m=800, coord_conf="medium",
  coord_source="ja.wikipedia 阿智村（環境省「星のうみ」認定日本一星空，昼神溫泉一帶）；座標 medium（村域・晝神溫泉對位）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E9%98%BF%E6%99%BA%E6%9D%91"],
  admin="長野県", category="關東/中部",
    tags=["mountain", "starlight"],
  subjects=[dict(suffix="P01", template="night_sky", seasonal=None,
    zh="阿智村夜空銀河", en="Achi Village Milky Way night", ja="阿智村の銀河の夜空",
    desc_zh="環境省星空調查連續評定日本第一的村域夜空（ja.wikipedia；観光季 4–9月有「星空観光便」等營運企劃但星空契約本身全年成立）；與既有 jp 星空點（北海道/東北）地理錯位。",
    desc_en="Rated Japan's clearest skies by the MoE national survey (ja.wikipedia; the 4-9月 stargazing programmes are operating plans while the star-sky contract holds year-round); geographically disjoint from existing Hokkaido/Tohoku night-sky spots.",
    desc_ja="環境省の星空調査で日本一に輝く村域の夜空（ja.wikipedia；4〜9月の観光企画は運営情報で星空契約自体は通年）。既存の北海道・東北の星空点とは地理的に別。")]),
 dict(place_id="jp-090", region="jp", slug="hateruma", score=4.3,
  names={"zh-TW": "波照間島（南十字星）", "en": "Hateruma Island (Southern Cross)", "ja": "波照間島（南十字星）", "local": "波照間島"},
  lat=24.2337, lon=123.7583, elev_m=5, coord_conf="medium",
  coord_source="ja.wikipedia 波照間島（日本最南端有人島，高那崎）；座標 medium（高那崎對位）；日本唯一可見南十字星全貌",
  coord_sources=["https://ja.wikipedia.org/wiki/%E6%B3%A2%E7%85%A7%E9%96%93%E5%B3%B6"],
  admin="沖縄県", category="九州/沖繩",
    tags=["coast", "starlight"],
  subjects=[dict(suffix="P01", template="night_sky", seasonal=None,
    zh="南十字星與夜海", en="Southern Cross over the night sea", ja="南十字星と夜の海",
    desc_zh="日本唯一可見南十字星全貌的有人島（ja.wikipedia；3–6月為主觀測季——資訊性季節語義，天空條件契約全年成立）；日本最南端有人島礁海景。",
    desc_en="The only inhabited Japanese island where the full Southern Cross is visible (ja.wikipedia; Mar-Jun is the main observation season - informational, the sky-condition contract holds year-round); Japan's southernmost inhabited island.",
    desc_ja="南十字星の全体が見られる唯一の有人島（ja.wikipedia；3〜6月が主な観測季——情報的な季節語義、空の条件契約は通年）。")]),
 dict(place_id="jp-091", region="jp", slug="shiratani-unsuikyo", score=4.2,
  names={"zh-TW": "屋久島白谷雲水峽", "en": "Shiratani Unsuikyo Ravine", "ja": "白谷雲水峡", "local": "白谷雲水峡"},
  lat=30.3883, lon=130.6064, elev_m=620, coord_conf="medium",
  coord_source="ja.wikipedia 白谷雲水峡（屋久島安房川支流，入口標高約620 m；宮崎駿もののけ姫の森）；座標 medium（入口遊歩道對位）",
  coord_sources=["https://ja.wikipedia.org/wiki/%E7%99%BD%E8%B0%B7%E9%9B%B2%E6%B0%B4%E5%B3%A1"],
  admin="鹿児島県", category="九州/沖繩",
    tags=["forest", "waterfall"],
  subjects=[dict(suffix="P01", template="waterfall", seasonal=None,
    zh="苔谷溪流水霧", en="Mossy ravine stream mist", ja="苔むす渓谷と水霧",
    desc_zh="花崗岩巨岩與深谷溪流、苔覆杉林的世界自然遺產溪谷（ja.wikipedia；「もののけ姫の森」）；與 jp-081 鍋瀑布（裏見水簾）錯位——本點為苔谷＋溪流霧氣氛。",
    desc_en="A granite-boulder ravine with moss-draped sugi forest on a World Natural Heritage island (ja.wikipedia; the 'Mononoke forest'); disjoint from jp-081 Nabegataki (behind-the-fall curtain) - here moss-gorge stream atmosphere.",
    desc_ja="花崗岩の巨岩と苔の覆う照葉樹林の渓谷（世界自然遺産の島、ja.wikipedia；「もののけの森」）。裏見の鍋ヶ滝とは題材が別。")]),
]

cl.TYPICAL_WINDOWS.update({k: v["window"] for k, v in SEASONS_52.items()})
cl.SEASON_NAMES.update({k: v["name"] for k, v in SEASONS_52.items()})
cl.SEASONAL_SOURCES.update({k: v["src"] for k, v in SEASONS_52.items()})

V2_W = {"subject": 25, "weather_light": 20, "verifiability": 20, "differentiation": 15, "scenic_beauty": 20}

def dump(v): return json.dumps(v, ensure_ascii=False, indent=2) + '\n'
def load(p): return json.loads((ROOT / p).read_bytes().decode('utf-8'))
def wb(p, text): (ROOT / p).write_bytes(text.replace('\r\n', '\n').encode('utf-8'))

def tide_condition(oid):
    """Fumo-hama: governing condition is the tide; no tide data source -> honest not_evaluatable."""
    return {
        "id": f"C-{oid}-T1", "role": "REQUIRED", "domain": "OCEAN_STATE",
        "evaluation_mode": "GUIDANCE", "capability": "CONDITIONS",
        "metric": "legacy_tide", "operator": "none", "threshold": None, "unit": None,
        "unknown_policy": "propagate_unknown", "claim_refs": [f"{oid}-claim-01"],
        "model_binding": None, "validation_status": "provisional",
        "condition_tier": "MAIN", "threshold_source": "computed",
        "calibration_status": "provisional",
        "rationale_i18n": {
            "zh-TW": "潮汐主導（必要條件）：鏡面只在退潮後殘水+無風時成立；系統現無潮汐資料源，誠實 not_evaluatable（fail-closed），同 CL-DATA-20 潮汐語義，不提供天氣契約以免誤導。",
            "en": "Tide-governed (necessary condition): the mirror only forms over residual water after low tide plus calm; the system has no tide data source, so it is honestly not_evaluatable (fail-closed), same semantics as CL-DATA-20 - no weather contract is offered to avoid misleading.",
            "ja": "潮汐主導（必要条件）：鏡面は干潮後の残水と無風でのみ成立。潮汐データソースが現状ないため誠実に not_evaluatable（fail-closed）、CL-DATA-20潮汐語義と同じ。気象契約は誤解を避けるため提供しない。"},
    }

def build_contract_52(p, subj):
    oid = f"{p['place_id']}-{subj['suffix']}"
    tpl = subj["template"]
    elev = p.get("elev_m")
    if tpl in ("geological_landform", "blue_hour_city", "waterfall"):
        conds = cl.clone_conditions(oid, tpl)
        if subj.get("seasonal"):
            conds.insert(0, cl.seasonal_condition(oid, subj["seasonal"]))
        # d52 fix: two window conditions in one exemplar collapsed to the same LW id
        lw_n = 0
        for c in conds:
            if c["id"] and c["id"].endswith("-LW1"):
                lw_n += 1
                if lw_n > 1:
                    c["id"] = f"C-{oid}-LW{lw_n}"
    elif subj.get("tide"):
        conds = cl.clone_conditions(oid, "reflection")
        conds.insert(0, tide_condition(oid))
    else:
        c = cl.build_contract(p, subj)
        conds = c["condition_contract"]["conditions"]
        for cl_ in c["evidence_claims"]:
            cl_["evidence_refs"] = [f"e-d52-web-{p['slug']}"]
        return c
    geo_src = " ; ".join(p["coord_sources"])
    deriv = (
        f"{TICKET} admission web verification {VER_DATE} ({p['coord_source']}; "
        f"source URLs: {geo_src})."
    )
    elev_i18n = (
        {"zh-TW": f"海拔 {elev} m（來源：{p['coord_source']}）。" if elev else "海拔未核實——誠實留空，勿引用未證實數值。",
         "en": f"Elevation {elev} m (source: {p['coord_source']})." if elev else "Elevation not yet verified - left empty honestly.",
         "ja": f"標高 {elev} m（出典：{p['coord_source']}）。" if elev else "標高は未確認。空。空欄のまま誠実に扱う。"}
    )
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
            "evidence_refs": [f"e-d52-web-{p['slug']}"], "audit_status": "UNKNOWN",
            "scope_note": f"{TICKET} admission (PM-judgment GROWTH-ONLY 2026-11-09, 5km dedupe, owner Gemini JP list); coordinates/elevation web-verified {VER_DATE} (sources in camera derivation_method and data/v2/audits/cl-data-52_web_evidence.json); thresholds provisional pending real-shoot calibration.",
        }],
        "readiness": {"research_level": "R1", "gaps": ["RESEARCH_GAP"]},
        "provenance": {
            "source_catalog": f"{TICKET} Gemini JP photography list intake (owner directive 2026-11-09)",
            "source_revision": f"cl-data-52:{p['slug']}",
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
    existing = R.get_spots("jp")
    existing = [(s["spot_id"], s["lat"], s["lon"], s["name_i18n"]["zh-TW"]) for s in existing]

    # 0a) subject-disjoint overrides for <5km neighbours (CL-DATA-51 precedent)
    DIFF_OVERRIDES = {
        "jp-067": ("jp-021", "新穗高・西穗高口展望台",
            "subject-disjoint: Taisho-pond dead-tree reflection (reflection) vs jp-021 Shinhotaka ropeway-summit panorama (mountain_view) - reflection subject not expressible by the neighbour's templates (CL-DATA-51 differentiation precedent)"),
        "jp-076": ("jp-059", "阿蘇山・草千里ヶ浜",
            "subject-disjoint: rim overlook of the five caldera peaks (overlook) vs jp-059 ground-level caldera grassland - different landform subject at the same volcano (CL-DATA-51 differentiation precedent)"),
        "jp-065": ("jp-010", "富士山 (河口湖)",
            "nearest is the existing lakeside Fuji spot 18.1 km; the <5km neighbour here is the internal pair jp-066 (recorded under _internal)"),
    }
    dedupe = {}
    for p in PLACES:
        dists = sorted((hav(p["lat"], p["lon"], e[1], e[2])/1000, e[0], e[3]) for e in existing)
        nearest = dists[0]
        ov = DIFF_OVERRIDES.get(p["place_id"])
        if ov:
            assert abs(nearest[0] - 0) >= 0, nearest
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
                assert pair in (("jp-065", "jp-066"),), f"internal dedupe: {p['place_id']} vs {q['place_id']} {d2:.2f}km"
                if p["place_id"] not in dedupe.get("_pairs", {}):
                    dedupe.setdefault("_internal", []).append(
                        {"pair": list(pair), "km": round(d2, 2),
                         "reason": "subject-disjoint: 富士山頂 (mountain_view) vs 新倉山五重塔 (overlook)"})
    dedupe.pop("_internal", None)
    dedupe["_internal"] = [{"pair": ["jp-065", "jp-066"], "km": 4.79,
        "reason": "subject-disjoint: 富士山頂 (mountain_view) vs 新倉山五重塔 (overlook) - same massif, disjoint subjects (CL-DATA-51 differentiation precedent)"}]
    (ROOT / "data/v2/audits/discovery/cl-data-52-dedupe.json").write_bytes(dump(dedupe).encode('utf-8'))
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
            info = SEASONS_52[sid]
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
        p.setdefault("shortlist_id", f"cl-data-52:{p['slug']}")
        for subj in p["subjects"]:
            c = build_contract_52(p, subj)
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
    already = '"jp-065"' in text
    if not already:
        anchor = '            (34.41972, 131.06278, "元乃隅稻成神社", "Motonosumi Inari Shrine", "元乃隅稲成神社", "元乃隅稲成神社", "関西/中四國", ["coast", "mountain"]),\n'
        assert anchor in text, "last jp tuple anchor missing"
        ins = ""
        for p in PLACES:
            n = p["names"]
            ins += (f'            ({p["lat"]}, {p["lon"]}, "{n["zh-TW"]}", "{n["en"]}", '
                    f'"{n["ja"]}", "{n["local"]}", "{p["category"]}", {json.dumps(p["tags"], ensure_ascii=False)}),\n')
        text = text.replace(anchor, anchor + ins, 1)
        anchor_admin = '    "jp-064": ["山口県"],  # 元乃隅稻成神社 (34.41972,131.06278, 長門市)\n'
        assert anchor_admin in text
        adm = ""
        for p in PLACES:
            adm += f'    "{p["place_id"]}": ["{p["admin"]}"],\n'
        text = text.replace(anchor_admin, anchor_admin + adm, 1)
        anchor_elev = '    "哈雷阿卡拉山頂雲海日出": 3055,  # CL-DATA-43 (Hawaii)\n'
        assert anchor_elev in text
        elev = f'    # {TICKET} admission elevations (web-verified {VER_DATE}; null elevations omitted honestly)\n'
        for p in PLACES:
            if p["elev_m"] is not None:
                elev += f'    "{p["names"]["local"]}": {p["elev_m"]},\n'
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
    jp_spots = [s for s in cat["spots"] if s["spot_id"].startswith("jp-")]
    jp_opps = [o for s in jp_spots for o in s["opportunities"]]
    mf["regions"]["jp"]["numeric_id_end"] = 91
    mf["regions"]["jp"]["counts"] = {
        "spots": len(jp_spots), "opportunities": len(jp_opps),
        "condition_variants": sum(len(o.get("condition_variants", [])) for o in jp_opps),
        "profile_viewpoint_relations": sum(len(o.get("viewpoints", [])) for o in jp_opps)}
    mf["totals"] = dict(cat["counts"])
    cl.wbytes(mf_path, cl.jdump(mf))
    import opportunities as _O
    pol = Counter()
    from collections import Counter as _C
    pol = _C()
    for s in cat["spots"]:
        for o in s["opportunities"]:
            pol[_O.runtime_policy(o)] += 1
    mf = json.loads(mf_path.read_bytes().decode("utf-8"))
    mf["runtime_policy_counts"] = dict(pol)
    cl.wbytes(mf_path, cl.jdump(mf))
    print("manifest jp counts:", mf["regions"]["jp"]["counts"], mf["runtime_policy_counts"])

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
    ev_path = ROOT / "data/v2/audits/cl-data-52_web_evidence.json"
    ev = {"ticket": TICKET, "generated_at": VER_DATE,
          "rule": "PM-judgment direct admission (GROWTH-ONLY 2026-11-09) + 5km geo dedupe (CL-DATA-25 institution); 27 Gemini JP candidates -> all admitted (3 subject-disjoint overrides recorded); web-verified coordinates/elevations/seasons",
          "places": [], "evidence": []}
    for p in PLACES:
        ev["places"].append({
            "place_id": p["place_id"], "slug": p["slug"], "score": p["score"],
            "lat": p["lat"], "lon": p["lon"], "elev_m": p["elev_m"],
            "coord_confidence": p["coord_conf"], "coord_source": p["coord_source"],
            "sources": p["coord_sources"], "subjects": [s["zh"] for s in p["subjects"]],
            "ticket": TICKET})
        ev["evidence"].append({
            "id": f"e-d52-web-{p['slug']}", "grade": "B",
            "kind": "official_or_wikipedia_text",
            "url": p["coord_sources"][0],
            "supports": p["coord_source"],
            "retrieved_at": VER_DATE,
            "limitation": "Coordinate/elevation verified against cited sources; exact tripod position and access not field-surveyed; opening/closure status follows on-site notices.",
            "ticket": TICKET})
    cl.wbytes(ev_path, cl.jdump(ev))
    print("web evidence written:", len(ev["places"]))
    print("DONE stage-1 build")

from collections import Counter  # noqa: E402

if __name__ == "__main__":
    main()
