#!/usr/bin/env python3
"""CL-DATA-66 Wave 4: scoreless intake of 10 Tier-A places (tw-174..tw-183)
from the manifest-next-30 (indices 90..119). 20 of the 30 candidates rejected
(4 identical existing places + 9 same-family <5km overlaps + 3 pure-swimming-
beach + 1 private night-view restaurant + 1 unverifiable identity + ...
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
    'cl66w3', str(ROOT / 'data/v2/tools/discovery/cl_data_66_build_wave3.py'))
m3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m3)
cl = m3.cl

TICKET = "CL-DATA-66"
VER_DATE = "2026-11-11"
WAVE = 4

PLACES = [
 dict(place_id="tw-174", region="tw", slug="dongshi-forest", score=None,
  names={"zh-TW": "東勢林場", "en": "Dongshi Forest Garden (Taichung)",
         "ja": "東勢林場", "local": "東勢林場"},
  lat=24.2799392, lon=120.8789334, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 東勢林場（台中东勢，theme_park 節點，勢林街6-1）；海拔官方農業旅遊場域資料為 500–700 公尺區間值，誠實不取單值、altitude_m 留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E6%9D%B1%E5%8B%A2%E6%9E%97%E5%A0%B4",
                 "https://www.taiwanfarm.org.tw/zh-TW/Front/Farm/Detail/411"],
  admin="台中市", category="本島", tags=["mountain", "forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="東勢林場雲霧森林步道", en="Dongshi Forest Garden mist-forest trail",
    ja="東勢林場の霧の森",
    desc_zh="東勢林場（212公頃森林遊樂區，大安溪畔）園區森林步道的雲霧林與螢火/油桐季景（OSM theme_park 節點；官方海拔資料為 500–700 公尺區間，誠實不取單值）；清單主題的螢火蟲/油桐花季窗查無本站可繫結的權威季節資料源，誠實不建時間窗契約——本契約為森林步道主體。",
    desc_en="Mist-forest trails inside the 212-hectare Dongshi Forest Garden by the Dajia river (OSM theme-park node; official elevation is a 500-700 m range, honestly not collapsed to a single value). The list's firefly/tung-blossom windows have no authoritative seasonal source we can bind, so no time-window contract is built - honestly.",
    desc_ja="大甲溪畔の東勢林場（212ヘクタール）の霧の森と園内歩道（OSM）。標高は公式資料が500-700mの幅で、単一値にしないため空欄。蛍・油桐の季節窓は権威源がなく誠実に不構築。"),
   dict(suffix="P02", template="mountain_view", seasonal=None,
    zh="東勢林場大安溪谷展望", en="Dongshi Dajia-valley outlook", ja="東勢林場の大甲渓谷展望",
    desc_zh="園區高點向大安溪谷與東勢山城方向展望（與同點 P01 森林步道契約分列）。",
    desc_en="Outlook over the Dajia creek valley and the Dongshi hill town from the garden's high point (separate from the P01 forest-trail contract).",
    desc_ja="園内高台から大甲渓谷と東勢の町を望む（P01 とは別契約）。"),
  ]),
 dict(place_id="tw-175", region="tw", slug="hengshan-guanyi", score=None,
  names={"zh-TW": "橫山觀日步道（橫山仙境）", "en": "Hengshan sun-watching trail (Bagua range)",
         "ja": "横山観日歩道（横山仙境）", "local": "橫山觀日步道"},
  lat=23.8932820, lon=120.6389840, elev_m=443, coord_conf="medium",
  coord_source="OSM Nominatim 橫山（南投市永興里，hamlet 節點，八卦山台地最高峰）；海拔443公尺（政府 i運動資訊平台臺灣小百岳 NO.048）",
  coord_sources=["https://www.openstreetmap.org/search?query=%E6%A9%AB%E5%B1%B1%20%E5%8D%97%E6%8A%95",
                 "https://isports.sa.gov.tw/Apps/TIS/TIS05/TIS0550M_02V1.aspx?PKNO=47"],
  admin="南投縣", category="本島", tags=["mountain"],
  subjects=[
   dict(suffix="P01", template="sunrise", seasonal=None,
    zh="橫山觀日平台日出", en="Hengshan sun-watching platform sunrise",
    ja="横山観日プラットフォームの日の出",
    desc_zh="八卦山台地最高峰（443m，臺灣小百岳NO.048）橫山觀日步道/觀日平台向東欣賞日出、俯瞰彰化平原（i運動資訊平台小百岳頁＋彰化旅遊網橫山觀日步道頁；OSM hamlet 節點對位）；方位暫以 generic 東向 tolerance 85 註冊，待現場校準。",
    desc_en="Sunrise from the sun-watching platform on Hengshan, the 443 m high point of the Bagua plateau (Taiwan's Top-100 Y_MOUNT NO.048, government iSports page; Changhua tourism page; OSM hamlet node); generic east sector, tolerance 85, pending field calibration.",
    desc_ja="八卦山台地最高峰（443m、台湾小百岳NO.048）横山の観日プラットフォームからの日の出（政府 iSports）。方位は暫定の東向き。"),
   dict(suffix="P02", template="overlook", seasonal=None,
    zh="橫山茶園與彰化平原展望", en="Hengshan tea-terrace and Changhua-plain outlook",
    ja="横山の茶園と彰化平原の展望",
    desc_zh="橫山三角點周邊台地茶樹園與彰化平原展望、灰面鵟鷹過境季賞鷹（小百岳頁；與同點 P01 日出契約分列）；清單主題的雲海查無本站權威資料源，誠實不建雲海時間窗——本契約為展望主體。",
    desc_en="Terraced tea rows on the Hengshan plateau and the Changhua plain outlook, plus the March grey-faced-buzzard passage season (Top-100 page; separate from the P01 sunrise contract). The list's cloud-sea topic has no authoritative source we can bind - honestly no cloud-sea window contract.",
    desc_ja="横山の茶畑と彰化平原の展望、三月のサシバ渡り（小百岳頁）。雲海の季節窓は権威源がなく誠実に不構築。"),
  ]),
 dict(place_id="tw-176", region="tw", slug="xizhi-cuihu", score=None,
  names={"zh-TW": "汐止翠湖步道", "en": "Xizhi Cuihu (Green Lake) trail",
         "ja": "汐止翠湖歩道", "local": "汐止翠湖步道"},
  lat=25.0891603, lon=121.6289131, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 翠湖（新北汐止，water 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E7%BF%A0%E6%B9%96%20%E6%B1%90%E6%AD%A2",
                 "https://www.xizhi.ntpc.gov.tw/home.jsp?id=b4cafbf11e0d8c3b&act=be4f48068b2b0031&dataserno=27790e400b3c2d233a62"],
  admin="新北市", category="本島", tags=["lake", "forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="翠湖環湖森林與湖景", en="Cuihu lake-and-forest loop trail",
    ja="翠湖の湖と森",
    desc_zh="汐止內溝山翠湖環湖步道：森林環繞的小湖與湖畔步道（OSM water 節點；汐止區公所旅遊頁；海拔查無權威源誠實留空）；清單主題的螢火蟲/油桐花季窗查無本站可繫結的權威季節資料源，誠實不建時間窗契約——本契約為湖景森林主體。",
    desc_en="The lakeside loop around Green Lake (Cuihu) on Neigou mountain, Xizhi: a small forest-ringed lake (OSM water node; Xizhi District page; elevation honestly left empty). The list's firefly/tung-blossom windows have no authoritative seasonal source we can bind, so no time-window contract is built - honestly.",
    desc_ja="汐止の翠湖の環湖歩道と森（OSM）。蛍・油桐の季節窓は権威源がなく誠実に不構築。"),
  ]),
 dict(place_id="tw-177", region="tw", slug="tefuya-trail", score=None,
  names={"zh-TW": "特富野古道", "en": "Tefuya Historic Trail (Zizhong end)",
         "ja": "特富野古道", "local": "特富野古道"},
  lat=23.4841681, lon=120.8302710, elev_m=2275, coord_conf="high",
  coord_source="林務局特富野古道頁（全長6.32km；自忠入口海拔2,275m、步道最高2,282m最低1,798m）＋OSM Nominatim 特富野古道（自忠 trailhead 節點）",
  coord_sources=["https://www.forest.gov.tw/0000323",
                 "https://www.openstreetmap.org/search?query=%E7%89%B9%E5%AF%8C%E9%87%8E%E5%8F%A4%E9%81%93"],
  admin="嘉義縣", category="本島", tags=["mountain", "forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="特富野古道自忠端雲霧森林", en="Tefuya trail Zizhong-end mist forest",
    ja="特富野古道自忠側の霧の森",
    desc_zh="特富野古道自忠端（海拔2,275m，林務局官方資料）沿舊鐵道雲霧森林與柳杉林展望（forest.gov.tw 步道頁＋OSM trailhead 節點）；清單主題的茶園季窗與本站古道主體不符，誠實不建時間窗契約——本契約為古道雲霧林主體；與既有 tw-024 阿里山祝山觀日平台（3.21km）題材錯位——本點為森林古道，祝山為觀日平台。",
    desc_en="Mist forest and old-railway cedar woods from the Zizhong entrance of the Tefuya Historic Trail (2,275 m, Forestry Bureau page; OSM trailhead node); the list's teaterrace window doesn't fit the trail subject - honestly no window contract. Disjoint from tw-024 Zhushan sunrise platform 3.21 km away (trail forest vs sunrise platform).",
    desc_ja="特富野古道自忠側（標高2,275m、林務局）の霧の森と旧線（OSM）。茶園の季節窓は不構築。祝山観日平台とは題材が別。"),
  ]),
 dict(place_id="tw-178", region="tw", slug="baishuihu-shoudao", score=None,
  names={"zh-TW": "白水湖壽島", "en": "Shoudao islet, Baishuihu (Chiayi)",
         "ja": "白水湖寿島", "local": "白水湖壽島"},
  lat=23.4036301, lon=120.1521167, elev_m=None, coord_conf="high",
  coord_source="OSM Nominatim 白水湖壽島（嘉義東石，viewpoint 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E7%99%BD%E6%B0%B4%E6%B9%96%E5%A3%BD%E5%B3%B6"],
  admin="嘉義縣", category="本島", tags=["coast"],
  subjects=[
   dict(suffix="P01", template="sunset", seasonal=None,
    zh="壽島水上古厝與蚵棚夕照", en="Shoudao drowned-house and oyster-rack sunset",
    ja="寿島の水中古厝と牡蠣棚の夕焼け",
    desc_zh="白水湖壽島沙洲：退潮顯露的水中古厝、倒電桿與蚵棚，向西台灣海峽夕照（OSM viewpoint 節點；海拔查無權威源誠實留空）；清單主題的 beach（泳灘）語義不符——壽島為鹽田沙洲/蚵田景觀非泳灘，誠實以夕照主體登記；方位暫以 generic 西向 tolerance 85 註冊，待現場校準。",
    desc_en="The Shoudao sandbar on Baishuihu: drowned houses, tilted poles and oyster racks exposed at low tide, sunset west toward the Taiwan Strait (OSM viewpoint node; elevation honestly left empty). The list's 'beach' topic doesn't fit - this is a salt-pan/oyster-landscape islet, not a swimming beach - honestly registered as a sunset subject; generic west sector, tolerance 85, pending field calibration.",
    desc_ja="白水湖寿島の水中古厝・倒れた電柱・牡蠣棚と台湾海峡の夕日（OSM）。リストのビーチ語義と合わないため夕景主体で登録。方位は暫定の西向き。"),
  ]),
 dict(place_id="tw-179", region="tw", slug="bishanyan-neihu", score=None,
  names={"zh-TW": "碧山巖", "en": "Bishanyan viewpoint (Neihu, Taipei)",
         "ja": "碧山巖", "local": "碧山巖"},
  lat=25.0970721, lon=121.5875981, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 碧山巖開漳聖王廟（台北內湖，place_of_worship 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E7%A2%A7%E5%B1%B1%E5%B7%96%E9%96%8B%E6%BC%B3%E8%81%96%E7%8E%8B%E5%BB%9F",
                 "https://zh.wikipedia.org/wiki/%E7%A2%A7%E5%B1%B1%E5%B7%96%E9%96%8B%E6%BC%B3%E8%81%96%E7%8E%8B%E5%BB%9F"],
  admin="台北市", category="本島", tags=["mountain", "city"],
  subjects=[
   dict(suffix="P01", template="city_night", seasonal=None,
    zh="碧山巖台北盆地琉璃夜景", en="Taipei-basin liuli night view from Bishanyan",
    ja="碧山巖から台北盆地の夜景",
    desc_zh="碧山巖開漳聖王廟前觀景平台俯瞰台北盆地與101一帶萬家燈火（OSM place_of_worship 節點＋zh.wikipedia 條目；海拔查無權威源誠實留空）；與同波 tw-176 汐止翠湖（4.25km）題材錯位——本點為廟前平台城市夜景，翠湖為森林湖景。",
    desc_en="The temple-front viewing platform at Bishanyan overlooking the Taipei basin and the Taipei-101 lights (OSM place-of-worship node; zh.wikipedia entry; elevation honestly left empty); disjoint from wave-sibling tw-176 Cuihu forest-lake subject 4.25 km away.",
    desc_ja="碧山巖の参道展望台から台北盆地と101の灯り（OSM・zh.wikipedia）。同波の翠湖（4.25km）とは題材が別。"),
   dict(suffix="P02", template="overlook", seasonal=None,
    zh="碧山巖晨昏盆地展望", en="Bishanyan basin dawn outlook", ja="碧山巖の朝の盆地展望",
    desc_zh="廟前平台向盆地側晨昏展望（與同點 P01 夜景契約分列）；清單主題的日出查無本站向位的權威資料源，誠實不註冊方向窗——本契約為晨昏展望主體。",
    desc_en="Dawn/dusk basin outlook from the same platform (separate from the P01 night-view contract); the list's sunrise topic has no authoritative azimuth source for this site - honestly no directional window registered.",
    desc_ja="同プラットフォームから盆地側の朝の展望（P01 とは別契約）。日の出の方位は権威源がなく方向窓は不登録。"),
  ]),
 dict(place_id="tw-180", region="tw", slug="shenzhuoshan", score=None,
  names={"zh-TW": "神桌山", "en": "Shenzhuoshan ridge (Sanyuan/Nanzhuang)",
         "ja": "神卓山", "local": "神桌山"},
  lat=24.58306, lon=120.97444, elev_m=762, coord_conf="high",
  coord_source="zh.wikipedia 神桌山（峰頂海拔762公尺；座標24°34′59″N 120°58′28″E，苗栗三灣/獅潭/南庄交界，加里山山脈八卦力山系北稜）",
  coord_sources=["https://zh.wikipedia.org/zh-tw/%E7%A5%9E%E6%A1%8C%E5%B1%B1"],
  admin="苗栗縣", category="本島", tags=["mountain", "forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="神桌山稜線與南庄河谷展望", en="Shenzhuoshan ridge and Nanzhuang valley outlook",
    ja="神卓山の稜線と南庄河谷の展望",
    desc_zh="神桌山（762m，zh.wikipedia）稜線步道俯瞰南庄河谷與中港溪上游山林（zh.wikipedia 海拔/座標）；清單主題的螢火蟲季窗查無本站可繫結的權威季節資料源、雲海查無本站權威資料源，誠實不建時間窗契約——本契約為稜線展望主體。",
    desc_en="Ridge-trail outlook over the Nanzhuang creek valley and the upper Zhonggang woods from Shenzhuoshan (762 m, zh.wikipedia elevation/coordinates). The list's firefly window has no authoritative seasonal source we can bind, and the cloud-sea topic no authoritative source for this site, so no time-window contract is built - honestly.",
    desc_ja="標高762mの神卓山稜線から南庄河谷を望む（zh.wikipedia）。蛍・雲海の季節窓は権威源がなく誠実に不構築。"),
  ]),
 dict(place_id="tw-181", region="tw", slug="nenggao-tianchi-hut", score=None,
  names={"zh-TW": "能高天池山莊", "en": "Nenggao Tianchi hut (Mountains of Nantou)",
         "ja": "能高天池山荘", "local": "天池山莊"},
  lat=24.0453035, lon=121.2796483, elev_m=2860, coord_conf="high",
  coord_source="林業保育署南投分署天池山莊頁（南投仁愛精英村，海拔2,860公尺，能高北峰西側山坳）＋OSM Nominatim 天池山莊（alpine_hut 節點）",
  coord_sources=["https://nantou.forest.gov.tw/tchills",
                 "https://www.openstreetmap.org/search?query=%E5%A4%A9%E6%B1%A0%E5%B1%B1%E8%8E%8A"],
  admin="南投縣", category="本島", tags=["mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="cloud_sea", seasonal=None,
    zh="天池山莊能高雲海雲瀑", en="Nenggao cloud sea and cloud waterfall from Tianchi hut",
    ja="天池山荘からの雲海と雲瀑",
    desc_zh="天池山莊（海拔2,860m，林業保育署官方資料）能高越嶺道上的高山雲海與雲瀑展望（nantou.forest.gov.tw 山莊頁＋OSM alpine_hut 節點）；與既有 tw-043 奇萊主峰（6.31km）題材錯位——本點為越嶺道山莊雲海主體。",
    desc_en="Alpine cloud sea and cloud waterfall over the Nenggao crossing from Tianchi hut (2,860 m, Forestry and Nature Conservation Agency Nantou page; OSM alpine-hut node); disjoint from tw-043 Qilai main peak's summit subject 6.31 km away.",
    desc_ja="標高2,860mの天池山荘（林業保育署）から能高越嶺道の雲海と雲瀑（OSM）。奇萊主峰とは題材が別。"),
   dict(suffix="P02", template="mountain_view", seasonal=None,
    zh="天池山莊奇萊南峰晨光", en="Tianchi hut dawn on Qilai South Peak", ja="天池山荘の朝の光",
    desc_zh="山莊前緣向奇萊南峰/能高南峰方向的晨光山景（與同點 P01 雲海契約分列）；清單主題的日出查無本站向位的權威資料源，誠實不註冊方向窗——本契約為晨光山景主體。",
    desc_en="Dawn mountain view toward Qilai South / Nenggao South peaks from the hut frontage (separate from the P01 cloud-sea contract); the list's sunrise topic has no authoritative azimuth source for this site - honestly no directional window registered.",
    desc_ja="山荘から奇萊南峰・能高南峰方面の朝の光（P01 とは別契約）。日の出の方位は権威源がなく方向窓は不登録。"),
  ]),
 dict(place_id="tw-182", region="tw", slug="wanggaoliao-hunter-trail", score=None,
  names={"zh-TW": "望高寮瞭望台（獵人古道）", "en": "Wanggaoliao watchtower (Hunter trail, Xinyi)",
         "ja": "望高寮展望台（獵人古道）", "local": "望高寮瞭望台"},
  lat=23.5917017, lon=120.8748369, elev_m=1517, coord_conf="medium",
  coord_source="自由時報望鄉部落獵人古道（登上海拔1517公尺的望高寮瞭望台，能眺望玉山群峰）＋OSM Nominatim 獵人古道（信義卡里布安村 path 節點；瞭望台實址沿古道向上約1.5km，座標以古道節點對位、待現場校準）",
  coord_sources=["https://news.ltn.com.tw/news/Nantou/breakingnews/3897675",
                 "https://www.openstreetmap.org/search?query=%E7%8D%B5%E4%BA%BA%E5%8F%A4%E9%81%93"],
  admin="南投縣", category="本島", tags=["mountain", "starlight"],
  subjects=[
   dict(suffix="P01", template="sunrise", seasonal=None,
    zh="望高寮玉山群峰晨光", en="Yushan massif dawn from Wanggaoliao",
    ja="望高寮から玉山連峰の朝の光",
    desc_zh="海拔1,517公尺望高寮瞭望台（自由時報）眺望玉山主峰與玉山群峰晨光——望鄉為全台唯一清楚眺望玉山主峰的部落（LTN＋pixnet 行程記錄；OSM 獵人古道 path 節點對位）；方位暫以 generic 東向 tolerance 85 註冊，待現場校準。",
    desc_en="Dawn on the Yushan main peak and massif from the 1,517 m Wanggaoliao watchtower (Liberty Times; OSM hunter-trail path node as proxy - the tower sits ~1.5 km up-trail, pending field calibration); generic east sector, tolerance 85.",
    desc_ja="標高1,517mの望高寮展望台から玉山主峰・連峰の朝の光（自由時報）。方位は暫定の東向き。"),
   dict(suffix="P02", template="overlook", seasonal=None,
    zh="望高寮陳有蘭溪谷展望", en="Wanggaoliao Chenyoulan-valley outlook", ja="望高寮の陳有蘭渓谷展望",
    desc_zh="瞭望台俯瞰陳有蘭溪谷與望鄉/望美聚落（與同點 P01 晨光契約分列）；清單主題的雲海查無本站權威資料源，誠實不建雲海時間窗——本契約為溪谷展望主體。",
    desc_en="Outlook over the Chenyoulan creek gorge and the Wangxiang/Wangmei settlements from the watchtower (separate from the P01 dawn contract); the list's cloud-sea topic has no authoritative source for this site - honestly no cloud-sea window.",
    desc_ja="展望台から陳有蘭渓谷と望郷・望美集落を望む（P01 とは別契約）。雲海の季節窓は権威源がなく誠実に不構築。"),
  ]),
 dict(place_id="tw-183", region="tw", slug="xiuluan-warship-rock", score=None,
  names={"zh-TW": "秀巒軍艦岩／控溪吊橋", "en": "Xiuluan warship-rock and Kongxi footbridge",
         "ja": "秀巒軍艦岩・控溪吊橋", "local": "秀巒軍艦岩／控溪吊橋"},
  lat=24.6185541, lon=121.2851526, elev_m=None, coord_conf="medium",
  coord_source="OSM Nominatim 秀巒（新竹尖石，hamlet 節點）；海拔查無權威源誠實留空",
  coord_sources=["https://www.openstreetmap.org/search?query=%E7%A7%80%E5%B5%AC%20%E6%96%B0%E7%AB%B9",
                 "https://blog.udn.com/shine016/132221192"],
  admin="新竹縣", category="本島", tags=["mountain", "forest"],
  subjects=[
   dict(suffix="P01", template="overlook", seasonal=None,
    zh="軍艦岩白石溪谷與吊橋展望", en="Warship-rock Baisha gorge and footbridge outlook",
    ja="軍艦岩の白石渓谷と吊橋の展望",
    desc_zh="秀巒村控溪吊橋與軍艦岩吊橋俯瞰白石溪（薩克亞金溪）與泰崗溪匯流處的軍艦岩巨岩河景（OSM hamlet 節點＋多篇行記；海拔查無權威源誠實留空）；與既有 tw-091 司馬庫斯部落觀景點（4.62km）題材錯位——本點為溪谷吊橋河景主體，司馬庫斯為部落觀景。",
    desc_en="Outlook over the Baisha (Sakyajin) creek gorge and the warship-rock monolith from the Kongxi and warship-rock footbridges at Xiuluan village (OSM hamlet node; elevation honestly left empty); disjoint from tw-091 Smangus tribal viewpoint 4.62 km away (river-landform subject vs tribal viewpoint).",
    desc_ja="秀巒の控溪・軍艦岩の吊橋から白石渓と軍艦岩の河景（OSM）。司馬庫斯部落とは題材が別。"),
   dict(suffix="P02", template="seasonal_plant", seasonal="red_maple",
    zh="控溪吊橋楓香林楓紅", en="Kongxi bridge maple woods in autumn", ja="控溪吊橋の楓の紅葉",
    desc_zh="控溪吊橋對岸滿植楓香的楓紅季（沿用 seasonal-calendar 既有 red_maple 窗 10-20..11-10；海拔查無權威源誠實留空；與同點 P01 河景契約分列）。",
    desc_en="Autumn color of the maple woods across the Baisha creek from the Kongxi footbridge (reuses the existing seasonal-calendar red_maple window 10-20..11-10; separate from the P01 river-landform contract).",
    desc_ja="控溪吊橋対岸の楓香林の紅葉（red_maple 季節窓を再利用）。P01 とは別契約。"),
  ]),
]

# subject-disjoint overrides for <5km neighbours (CL-DATA-51/64/66 precedent)
DIFF_OVERRIDES = {
    "tw-177": ("tw-024", "阿里山祝山觀日平台",
        "subject-disjoint: Tefuya old-trail mist-forest/historic-railway hike vs Zhushan sunrise platform - 3.21km apart, disjoint subjects"),
    "tw-179": ("tw-176", "汐止翠湖步道",
        "subject-disjoint: Bishanyan temple-front Taipei-basin night view vs Cuihu forest-ring lake trail - 4.25km apart (same-wave siblings), disjoint subjects"),
    "tw-183": ("tw-091", "司馬庫斯部落觀景點",
        "subject-disjoint: Xiuluan warship-rock/footbridge river-gorge landform + wild-spring valley vs Smangus tribal viewpoint - 4.62km apart, disjoint subjects"),
}

# rejected within-5km family overlaps / exclusions: recorded in manifest, NOT admitted
REJECTED_PLACES = [
    ("望高寮夜景公園", "5km dedupe reject: 0.36km from existing tw-150 九天夕陽之樹/大肚山台地 - same 大肚山台地夜景/夕照 subject (near-duplicate), not subject-disjoint"),
    ("望高寮農路觀景台", "admitted as tw-182 望高寮瞭望台（獵人古道） — manifest display name alias"),
    ("松雪樓/奇萊登山口平台", "5km dedupe reject: 1.51km from existing tw-019 合歡山主峰 - same 合歡群峰 sunrise/cloud-sea summit family, not subject-disjoint"),
    ("東勢林場", "admitted as tw-174"),
    ("梅山36彎28-36彎", "identical existing place: name-matched tw-105 太平雲梯／梅山36彎 already in catalog - same 梅山36彎 switchback subject"),
    ("梅山36彎36彎", "identical existing place: name-matched tw-105 太平雲梯／梅山36彎 already in catalog - same 梅山36彎 switchback subject"),
    ("梧棲漁港/台中港", "5km dedupe reject: 4.02km from existing tw-015 高美濕地 - same 台中港海岸夕照/漁港 family, not subject-disjoint"),
    ("橫山仙境", "admitted as tw-175 橫山觀日步道（橫山仙境） — manifest display name alias"),
    ("水山巨木步道高點", "5km dedupe reject: 1.23km from existing tw-024 阿里山祝山觀日平台 - same 阿里山森林遊樂區 family, not subject-disjoint"),
    ("汐止翠湖步道", "admitted as tw-176"),
    ("淺水灣", "pure swimming beach exclusion (owner rules)"),
    ("清境觀星園/翠湖步道", "5km dedupe reject: 1.37km from existing tw-103 清境農場 - same 清境 family, not subject-disjoint"),
    ("湖口祥喜路/大尖山", "honest reject: identity/coordinate unverifiable - all Hukou night-view sources resolve to private landscape restaurants; no authoritative source for a public 祥喜路/大尖山 viewpoint"),
    ("烏來瀑布/桶後林道", "5km dedupe reject: 3.47km from existing tw-151 內洞國家森林遊樂區 - same 烏來溪谷瀑布/森林 family, not subject-disjoint"),
    ("特富野古道", "admitted as tw-177"),
    ("玉山北峰氣象站", "5km dedupe reject: 1.93km from existing tw-040 玉山主峰 - same 玉山群峰 summit family, not subject-disjoint"),
    ("瑞峰1314觀景台", "identical existing place: 0.0km from existing tw-134 1314觀景台 - same 海鼠山 deck"),
    ("白水湖壽島", "admitted as tw-178"),
    ("白沙灣", "pure swimming beach exclusion (owner rules); also 2.46km from tw-143 富貴角風稜石"),
    ("石梯坪單面山+壺穴", "identical existing place: 0.91km from existing tw-077 石梯坪海蝕平台／壺穴群 - same reef platform subject"),
    ("碧山巖", "admitted as tw-179"),
    ("碧湖山茶園", "5km dedupe reject: 3.37km from existing tw-105 太平雲梯／梅山36彎 - same 梅山茶區雲海茶園 family, not subject-disjoint"),
    ("碧湖山觀光茶園", "5km dedupe reject: 3.37km from existing tw-105 太平雲梯／梅山36彎 - same 梅山茶區雲海茶園 family (also near-duplicate of manifest row 碧湖山茶園), not subject-disjoint"),
    ("社頭極光森林/高鐵觀景區", "owner minor-spot exclusion: private night-view 景觀餐廳 (員林山腳路), analogous to the homestay exclusion"),
    ("神桌山桐花賞螢", "admitted as tw-180"),
    ("秀巒楓音瀑布/控溪吊橋", "admitted as tw-183 秀巒軍艦岩／控溪吊橋 — manifest display name alias"),
    ("翡翠灣", "pure swimming beach exclusion (owner rules); also 2.64km from tw-074 野柳地質公園"),
    ("能高天池山莊", "admitted as tw-181"),
    ("花蓮磯崎海水浴場", "pure swimming beach exclusion (owner rules)"),
    ("萬里桐潮池", "5km dedupe reject: 3.91km from existing tw-030 屏東關山 - same 恆春西海岸夕照 family, not subject-disjoint"),
]

REJECT_TIER_A_NAMES = [
    "望高寮夜景公園", "松雪樓/奇萊登山口平台", "梅山36彎28-36彎", "梅山36彎36彎",
    "梧棲漁港/台中港", "水山巨木步道高點", "淺水灣", "清境觀星園/翠湖步道",
    "湖口祥喜路/大尖山", "烏來瀑布/桶後林道", "玉山北峰氣象站", "瑞峰1314觀景台",
    "白沙灣", "石梯坪單面山+壺穴", "碧湖山茶園", "碧湖山觀光茶園",
    "社頭極光森林/高鐵觀景區", "翡翠灣", "花蓮磯崎海水浴場", "萬里桐潮池",
]
REJECT_REASONS = {n: r for n, r in REJECTED_PLACES if n in REJECT_TIER_A_NAMES}
assert len(REJECT_REASONS) == 20, len(REJECT_REASONS)
ADM_TIER_A_NAMES = {
    "東勢林場": "tw-174", "橫山仙境": "tw-175", "汐止翠湖步道": "tw-176",
    "特富野古道": "tw-177", "白水湖壽島": "tw-178", "碧山巖": "tw-179",
    "神桌山桐花賞螢": "tw-180", "能高天池山莊": "tw-181",
    "望高寮農路觀景台": "tw-182", "秀巒楓音瀑布/控溪吊橋": "tw-183",
}


def wb(p, text): return m3.wb(p, text)


def _build_contract(p, subj):
    """Copy of the wave-3 contract builder; module globals resolve to wave-4."""
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
    if p["place_id"] == "tw-181":
        access["zh-TW"] += " 能高越嶺道需林業保育署入山入園申請，屯寶登山口起約14公里步行。"
        access["en"] += " The Nenggao crossing requires a Forest Service mountain-entry permit; ~14 km walk from the trailhead."
        access["ja"] += " 能高越嶺道は入山・入園許可が必要。"
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
    existing = R.get_spots("tw")  # includes tw-125..tw-173 (tw-092 coordinate corrected 2026-11-11)
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
            # allow the override to be documented on the neighbour side
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
    if '"tw-174"' not in text:
        a_tw = '            (24.6501, 121.4706, "明池森林遊樂區", "Mingchi National Forest Recreation Area", "明池国家森林遊楽区", "明池森林遊樂區", "本島", ["mountain", "forest"]),  # CL-DATA-66\n'
        assert a_tw in text, "tw-173 tuple anchor missing"
        lines = []
        for p in PLACES:
            n = p["names"]
            lines.append(
                f'            ({p["lat"]}, {p["lon"]}, "{n["zh-TW"]}", "{n["en"]}", '
                f'"{n["ja"]}", "{n["local"]}", "{p["category"]}", {json.dumps(p["tags"], ensure_ascii=False)}),  # {TICKET}\n')
        text = text.replace(a_tw, a_tw + "".join(lines), 1)
        a_admin = '    "tw-173": ["宜蘭縣"],  # CL-DATA-66\n'
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

    # ---- 5) web evidence registry (extend wave-3 file) ----
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
    ev["places_wave4"] = wave_places
    ev["evidence_wave4"] = wave_evidence
    have_ids = {e["id"] for e in ev["evidence"]}
    ev["evidence"].extend([e for e in wave_evidence if e["id"] not in have_ids])
    ev["places_wave4_count"] = len(wave_places)
    ev["rejected_wave4_count"] = len(REJECT_TIER_A_NAMES)
    ev["rule_wave4"] = (f"Scoreless intake wave {WAVE} (owner ruling {VER_DATE}): admission = web verification + "
                        "5km subject-disjoint dedupe; NO rubric v2 gates, NO AGLI dual-board, agli-final "
                        f"untouched; score fields left empty. 10 places admitted (tw-174..tw-183), 20 "
                        "manifest-next-30 candidates rejected (4 identical existing places + 9 same-family "
                        "<5km overlaps + 3 pure-swimming-beaches + 1 private night-view restaurant + 1 "
                        "unverifiable identity + 1 sub-5km family 茶園 cluster (row counted once)). "
                        "Also recorded: tw-092 北關海潮公園 coordinate correction (retired place, regions.py "
                        "legacy pool 24.793->24.9119,121.8772 OSM way 545947415).")
    wb(ev_path, cl.jdump(ev))
    print("web evidence extended:", len(wave_places))

    # ---- 6) tier-a manifest wave-4 status update ----
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
    print("DONE wave-4 stage-1 build")


if __name__ == "__main__":
    main()
