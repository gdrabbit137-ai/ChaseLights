# -*- coding: utf-8 -*-
# CL-DATA-39 batch5 access-verification content (verified 2026-11-09 against official sources; final batch)
D = '2026-11-09'
PLACE_EVID = 'e-d39-access'
PLACE_SLUG = {
 'us-037':'niagara-falls-illumination','us-038':'newfound-gap-overlook','us-039':'south-pointe-miami-beach',
 'us-040':'piers-park-east-boston','us-041':'denali-mountain-vista','us-044':'point-woronzof-anchorage',
 'us-045':'seward-waterfront-park','us-046':'hatcher-pass-summit-lake','us-047':'matanuska-glacier-srs',
 'us-048':'portage-valley-begich-boggs','us-050':'juneau-waterfront-tram','us-051':'mendenhall-glacier',
 'us-052':'homer-spit','us-055':'kennecott-mines-nhl','us-056':'atigun-pass','us-057':'arctic-circle-wayside',
 'us-059':'brooks-falls-katmai','us-060':'glacier-bay-bartlett-cove','us-061':'fort-abercrombie-kodiak',
 'us-062':'eklutna-lake-srs','us-063':'talkeetna-riverfront-park','us-064':'alyeska-mountain-station',
 'us-069':'port-alsworth-lake-clark','us-071':'kerry-park-seattle','us-072':'golden-gardens-seattle',
 'us-073':'alki-beach-seattle','us-074':'gas-works-park-seattle','us-075':'discovery-park-seattle',
 'us-076':'hamilton-viewpoint-seattle','us-077':'jose-rizal-park-seattle','us-078':'myrtle-edwards-park-seattle',
 'us-079':'snoqualmie-falls','us-080':'deception-pass-sp','us-081':'mount-rainier-paradise',
 'us-082':'reflection-lakes-mora','us-083':'mount-rainier-sunrise','us-084':'tipsoo-lake-mora',
 'us-085':'ruby-beach-olympic','us-086':'rialto-beach-olympic','us-087':'hurricane-ridge-olympic',
 'us-088':'hoh-rain-forest-olympic','us-089':'palouse-falls-sp','us-090':'diablo-lake-overlook',
 'us-091':'washington-pass-overlook','us-092':'artist-point-baker','us-093':'picture-lake-heather-meadows',
 'us-094':'steptoe-butte-sp','us-095':'cape-disappointment-sp','us-096':'dry-falls-visitor-center',
}
PLACE_SOURCES = {
 'us-037':['https://parks.ny.gov/visit/state-parks/niagara-falls-state-park','https://www.niagarafallsstatepark.com/tours-events/illuminations/'],
 'us-038':['https://www.nps.gov/places/newfound-gap-overlook.htm','https://www.nps.gov/grsm/planyourvisit/fees.htm'],
 'us-039':['https://www.miamibeachfl.gov/city-hall/parks-and-recreation/parks-facilities-directory/south-pointe-park/','https://www.miamibeachfl.gov/city-hall/parking/parking-meter-rates/'],
 'us-040':['https://piersparksailing.org/about-us/piers-park','https://piersparksailing.org/'],
 'us-041':['https://www.nps.gov/dena/planyourvisit/mountain-vista.htm','https://www.nps.gov/places/dena-mountain-vista.htm'],
 'us-044':['https://www.anchorageactivities.com/listing/point-woronzof-park/','https://parkmagnet.com/united-states/alaska/anchorage/point-woronzof-park'],
 'us-045':['https://www.seward.com/community-resources/hometown-guide/parks-and-recreation/','https://www.alaska.org/detail/seward-waterfront-park'],
 'us-046':['https://dnr.alaska.gov/parks/aspunits/matsu/summitlksrs.htm','https://matsu.gov/trails/hatcher-pass-state-recreation-area'],
 'us-047':['https://dnr.alaska.gov/parks/aspunits/matsu/matsuglsrs.htm'],
 'us-048':['https://www.fs.usda.gov/r10/chugach/recreation/begich-boggs-visitor-center','https://www.fs.usda.gov/r10/chugach/offices/begich-boggs-visitor-center'],
 'us-050':['https://juneau.org/parks-recreation/marine-park','https://www.goldbelttram.com/about/'],
 'us-051':['https://www.fs.usda.gov/r10/tongass/recreation/mendenhall-glacier-interpretive-visitor-center','https://www.fs.usda.gov/r10/tongass/offices/mendenhall-glacier-visitor-center'],
 'us-052':['https://www.cityofhomer-ak.gov/port/city-campgrounds','https://www.cityofhomer-ak.gov/port/mariner-park'],
 'us-055':['https://www.nps.gov/wrst/planyourvisit/kennecott-visitor-center.htm','https://www.nps.gov/tours/view.htm?id=C536F765-A295-C373-4643532A3E62B312'],
 'us-056':['https://www.blm.gov/visit/atigun-pass','https://www.blm.gov/learn/interpretive-centers/arctic-interagency-visitor-center/frequently-asked-questions'],
 'us-057':['https://www.blm.gov/visit/arctic-circle-wayside','https://www.blm.gov/sites/default/files/docs/2024-03/BLM-AK-2024_DaltonHwy_VisitorGuide_508_reduced.pdf'],
 'us-059':['https://www.nps.gov/places/brooks-falls-platform.htm','https://www.nps.gov/katm/planyourvisit/bear-safety-brooks-camp.htm'],
 'us-060':['https://www.nps.gov/glba/planyourvisit/tour.htm','https://www.nps.gov/glba/planyourvisit/typical-route-of-the-glacier-bay-day-tour.htm'],
 'us-061':['https://dnr.alaska.gov/parks/aspunits/kodiak/fortabercrombieshp.htm','https://dnr.alaska.gov/parks/aspunits/kodiak/kodiakindex.htm'],
 'us-062':['https://dnr.alaska.gov/parks/asp/access.htm','https://dnr.alaska.gov/parks/asp/unitfees.htm'],
 'us-063':['https://matsu.gov/communities/talkeetna','https://www.alaska.org/detail/talkeetna-riverfront-park'],
 'us-064':['https://www.alyeskaresort.com/aerial-tram-summer/','https://www.alyeskaresort.com/event/tram-opening-day-summer-2026/'],
 'us-069':['https://www.nps.gov/lacl/planyourvisit/port-alsworth.htm','https://www.nps.gov/lacl/contacts.htm'],
 'us-071':['https://www.seattle.gov/parks/parks/kerry-park'],
 'us-072':['https://www.seattle.gov/parks/parks/golden-gardens-park','https://parkways.seattle.gov/2026/04/13/seattle-parks-and-recreation-2026-summer-hours-for-alki-beach-and-golden-gardens/'],
 'us-073':['https://www.seattle.gov/parks/parks/golden-gardens-park','https://parkways.seattle.gov/2026/04/13/seattle-parks-and-recreation-2026-summer-hours-for-alki-beach-and-golden-gardens/'],
 'us-074':['https://seattle.gov/parks/parks/gas-works-park'],
 'us-075':['https://seattle.gov/parks/parks/discovery-park','https://seattle.gov/parks/parks/discovery-park/parking-and-beach-shuttles'],
 'us-076':['https://www.seattle.gov/parks/parks/hamilton-viewpoint-park'],
 'us-077':['https://www.seattle.gov/parks/parks/jose-rizal-park'],
 'us-078':['https://www.seattle.gov/parks/parks/myrtle-edwards-park'],
 'us-079':['https://www.snoqualmiewa.gov/378/Snoqualmie-Falls','https://www.snoqualmiefalls.com/faq/'],
 'us-080':['https://parks.wa.gov/find-parks/state-parks/deception-pass-state-park','https://parks.wa.gov/sites/default/files/2024-05/Deception%20Pass%20Park%20Brochure.pdf'],
 'us-081':['https://www.nps.gov/mora/planyourvisit/paradise.htm','https://www.nps.gov/mora/planyourvisit/park-brochure.htm'],
 'us-082':['https://www.nps.gov/mora/planyourvisit/park-brochure.htm'],
 'us-083':['https://www.nps.gov/mora/planyourvisit/park-brochure.htm','https://www.nps.gov/mora/planyourvisit/paradise.htm'],
 'us-084':['https://www.nps.gov/mora/planyourvisit/park-brochure.htm'],
 'us-085':['https://www.nps.gov/olym/planyourvisit/day-hiking-at-olympic.htm','https://www.nps.gov/olym/planyourvisit/hours.htm'],
 'us-086':['https://www.nps.gov/olym/planyourvisit/day-hiking-at-olympic.htm','https://www.nps.gov/olym/planyourvisit/hours.htm'],
 'us-087':['https://www.nps.gov/olym/planyourvisit/hours.htm'],
 'us-088':['https://www.nps.gov/olym/planyourvisit/day-hiking-at-olympic.htm','https://www.nps.gov/olym/planyourvisit/hours.htm'],
 'us-089':['https://parks.wa.gov/find-parks/state-parks/palouse-falls-state-park-heritage-site','https://parks.wa.gov/sites/default/files/2025-08/Palouse%20Falls%20Park%20Brochure.pdf'],
 'us-090':['https://www.nps.gov/places/diablo-lake-overlook.htm'],
 'us-091':['https://www.nps.gov/noca/planyourvisit/road-conditions.htm','https://hikingwashington.com/larch-hikes-washington/'],
 'us-092':['https://www.fs.usda.gov/r06/mbs/recreation/artist-point-trailhead','https://www.fs.usda.gov/r06/mbs/recreation/mt-baker-highway-sr-542'],
 'us-093':['https://www.fs.usda.gov/r06/mbs/recreation/mt-baker-highway-sr-542','https://www.fs.usda.gov/r06/mbs/recreation/artist-point-trailhead'],
 'us-094':['https://parks.wa.gov/find-parks/state-parks/steptoe-butte-state-park-heritage-site'],
 'us-095':['https://parks.wa.gov/find-parks/state-parks/cape-disappointment-state-park','https://parks.wa.gov/find-parks/state-parks/cape-disappointment-state-park/lewis-clark-interpretive-center'],
 'us-096':['https://parks.wa.gov/find-parks/state-parks/sun-lakes-dry-falls-state-park','https://parks.wa.gov/dry-falls-visitor-center'],
}
PLACE_NOTES = {
 'us-037': (
  "位於紐約州尼加拉瀑布州立公園（Niagara Falls State Park），全年開放，園區免費進入（停車另收費）。瀑布每晚從 dusk 起點亮 LED 照明，11–12 月時段為 16:30–02:00，時間為概估值、依天候調整；特別點燈與煙火另排。拍夜景照明時留在 Goat Island／觀景台等指定區域，冬季步道結冰與瀑布霧氣易造成濕滑，以現場告示與當日照明時刻表為準。",
  "In Niagara Falls State Park, NY — open year-round with free park entry (parking is charged). The Falls are LED-illuminated nightly from dusk; November–December runs 4:30 p.m.–2 a.m., times approximate and weather-dependent, with special illuminations and fireworks scheduled separately. For night shoots stay in designated areas (Goat Island, viewing decks); winter ice and Falls spray make surfaces slick — follow on-site notices and the daily illumination schedule.",
  "ニューヨーク州ナイアガラフォールズ州立公園内。年中無休・入園無料（駐車は有料）。滝は毎晩夕暮れからLED照明が点灯し、11〜12月は16:30〜02:00の予定（概ね・天候により変動）。特別点灯や花火は別日程。夜景撮影はGoat Islandや展望デッキなどの指定エリアに留まり、冬季は凍結と水煙で滑りやすいため、現地の掲示と当日の照明スケジュールに従うこと。"),
 'us-038': (
  "Newfound Gap Overlook 位於大煙山國家公園 Newfound Gap Road（US 441）上，停車場與季節性廁所設於眺望點。園區規定停車超過15分鐘必須持有 Smokies 停車標籤（parking tag），Newfound Gap Overlook 設有24小時自動售票機，另可線上購買。US 441 冬季可能因雪封路，行前務必查 NPS 路況；日出日落拍攝預留往返 Gatlinburg／Cherokee 的車程。",
  "Newfound Gap Overlook sits on Newfound Gap Road (US 441) in Great Smoky Mountains NP, with parking and seasonal restrooms at the overlook. A Smokies parking tag is required for any stay over 15 minutes — the overlook has a 24-hour tag machine, and tags are also sold online. US 441 can close for snow in winter; check NPS road conditions before heading out and allow extra drive time from Gatlinburg/Cherokee for dawn or dusk shoots.",
  "Newfound Gap Overlookはグレート・スモーキー山脈国立公園のNewfound Gap Road（US 441）沿いにあり、眺望点に駐車場と季節限定トイレがある。15分を超える駐車にはSmokiesパーキングタグが必須で、展望点には24時間自販機あり（オンライン購入も可）。US 441は冬に雪で閉鎖されることがあるため、出発前にNPSの道路状況を確認し、ガトリンバーグ/チェロキーからの車時間を見込むこと。"),
 'us-039': (
  "South Pointe Park／Beachwalk 位於邁阿密海灘最南端（1 Washington Avenue），公園開放時間為日出至日落，付費停車。Beachwalk 禁止電動滑板車／電子自行車等動力載具。海灣側可拍 PortMiami 郵輪與 Downtown Miami 天際線，大西洋側為沙灘日出；午後常有雲，最佳光線多在清晨。遵守海流與救生員告示，以現場公告為準。",
  "South Pointe Park/Beachwalk occupies the southern tip of Miami Beach (1 Washington Avenue); the park is open sunrise to sunset with paid parking. Motorized devices (e-scooters, e-bikes) are banned on the Beachwalk. The bay side frames PortMiami cruise ships and the Downtown Miami skyline; the ocean side gives Atlantic sunrise. Clouds often build in the afternoon — early morning light is usually best. Observe beach safety flags; follow on-site notices.",
  "South Pointe Park/Beachwalkはマイアミビーチ最南端（1 Washington Avenue）にあり、公園は日の出〜日の入り開放、駐車は有料。Beachwalkでは電動キックボード/電動自転車など動力乗り物は禁止。湾側からはPortMiamiの客船とダウンタウン・マイアミのスカイライン、大西洋側からは日の出が撮れる。午後は雲が発生しやすく、撮影は早朝が最適。海の安全フラグに従い、現地の掲示に従うこと。"),
 'us-040': (
  "Piers Park 位於東波士頓 95 Marginal Street，由 Massport 管理的濱水公園，600 呎 promenade 正對 Boston Harbor 與 downtown 天際線，設亭子、遊具與觀景台；拍攝不需費用。園內 sailing center 營業 11:00–日落。夜間拍攝注意：公園夜間照明有限，沿岸步道無護欄段請遠離水緣；詳細時間與活動公告以現場與 Massport 為準。",
  "Piers Park is a waterfront park at 95 Marginal Street, East Boston, managed by Massport: a 600-ft promenade faces Boston Harbor and the downtown skyline, with pavilions, a playground and viewing platforms; shooting is free. The on-site sailing center operates 11 a.m.–sunset. Night shoots: lighting in the park is limited, keep away from the unprotected water's edge along the promenade; hours and event postings follow the park and Massport notices.",
  "Piers Parkは東ボストン95 Marginal StreetのMassport管理のウォーターフロント公園。600フィートの遊歩道がボストン・ハーバーとダウンタウンのスカイラインを正面に望み、パビリオン・遊具・展望台がある。撮影無料。園内のセーリングセンターは11時〜日没営業。夜間撮影は園内照明が限られ、遊歩道の水際から距離を取ること。時間と催しは現地とMassportの告知に従うこと。"),
 'us-041': (
  "Mountain Vista 位於 Denali 國家公園 Denali Park Road Mile 13。園區該段技術上24小時開放：夏季建議搭乘免費 Savage River Shuttle（私人車位極少），冬季（約2月中旬起視路況）可自駕至 Mile 13，秋冬可能有雪封路於 Mile 3。晴朗時可遠眺 Denali（距離超過80哩）。露營僅限 Savage River 營地或持背野許可，夜拍請備頭燈與保暖，路況以 NPS 公告為準。",
  "Mountain Vista is at Mile 13 of the Denali Park Road. That road section is technically open 24 hours: in summer take the free Savage River Shuttle (private parking is extremely limited); from about mid-February (conditions permitting) you can drive to Mile 13, and fall/winter snow often closes the road at Mile 3. On clear days Denali itself is visible, more than 80 miles away. Camping is limited to Savage River Campground or backcountry permits — bring a headlamp and warm layers for night shoots; road status follows NPS postings.",
  "Mountain Vistaはデナリ国立公園Denali Park Roadの13マイル地点。この区間は技術的に24時間開放：夏は無料のSavage River Shuttle利用を推奨（自家用車の駐車は極めて少ない）。2月中旬頃から（路況次第）Mile 13まで自走可能で、秋〜冬はMile 3で雪により通行止めになることが多い。晴れた日には80マイル超離れたデナリ本体も望める。宿泊はSavage River Campgroundかバックカントリー許可のみ。夜撮影はヘッドライトと防寒を携行し、道路状況はNPSの告知に従うこと。"),
 'us-044': (
  "Point Woronzof Park 位於安克拉治 9700 Point Woronzof Road，濱 Cook Inlet，晴日可見 Alaska Range 與 Denali；市營公園營業時間約 06:00–23:00。Tony Knowles Coastal Trail 穿園而過（3–4哩標間），有專用停車場。西向日落光線投在上方山脈最為出色；注意潮間帶泥灘與融冰泥滑，勿走近 Beluga 觀察時的易碎堤岸，時間與規定以安克拉治市政府公告為準。",
  "Point Woronzof Park is a municipal park at 9700 Point Woronzof Road, Anchorage, on Cook Inlet with Alaska Range and Denali views on clear days; listed hours are about 6 a.m.–11 p.m. The Tony Knowles Coastal Trail passes through (mileposts 3–4) and there is dedicated parking. Westward sunset light over the range is best; the intertidal mudflats are treacherous — do not approach fragile banks when belugas are visible. Hours and rules follow City of Anchorage postings.",
  "Point Woronzof Parkはアンカレジ9700 Point Woronzof Roadの市営公園で、Cook Inletに面し晴天時はアラスカ山脈とデナリが望める。営業は概ね6時〜23時。Tony Knowles Coastal Trailが園内を通り（3〜4マイル標）、専用駐車場あり。西向きの夕日が山脈に当たる光景が最も美しい。干潟は危険で、ベルーガ観察時も脆弱な堤防には近づかないこと。時間と規則はアンカレジ市の告知に従うこと。"),
 'us-045': (
  "Seward Waterfront Park 為西沃德市管理的濱海公園，沿 Resurrection Bay 從小型船港延伸至 Alaska SeaLife Center，步道串聯歷史地標（Iditarod Trail Mile 0 等），海灘開放日間遊憩，露營另收費（約 $20–65）。拍 Mt. Alice 山景與日出時留意灣區強風與潮汐；夜間海灘無照明，公園規定以市政府現場公告為準。",
  "Seward Waterfront Park is a city-run shoreline park along Resurrection Bay, stretching from the small boat harbor to the Alaska SeaLife Center; the trail links historical landmarks (Iditarod Trail Mile 0 and more). Beach access is open for day use, camping is charged (about $20–65). Watch strong bay winds and tides when shooting Mt. Alice and sunrise; the beach has no night lighting — park rules follow City of Seward on-site postings.",
  "Seward Waterfront Parkはスワード市管理の海浜公園で、Resurrection Bay沿いに小型船港からアラスカ・シーライフセンターまで続く。遊歩道には歴史的ランドマーク（Iditarod Trail Mile 0など）が並ぶ。ビールの利用は日中、キャンプは有料（約$20〜65）。Mt. Aliceと日の出撮影時は湾の強風と潮汐に注意。夜間のビールに照明はなく、規則はスワード市の現地掲示に従うこと。"),
 'us-046': (
  "Summit Lake State Recreation Site 位於 Hatcher Pass Road（Hatcher Pass State Recreation Area 內），Alaska DNR 明示道路通車僅限夏季（約7月至9月下旬），山口積雪後封閉。湖畔有觀景與野餐設施；山口天候多變，即使盛夏也可能降雪，日出／夜拍請備保暖與頭燈，通行與關閉以 Alaska DNR 與 Matanuska-Susitna Borough 公告為準。",
  "Summit Lake State Recreation Site is on Hatcher Pass Road inside the Hatcher Pass State Recreation Area. Alaska DNR states the road is open to vehicles only in summer — usually July through late September — closing when snow builds at the pass. Lakeside viewing and picnic facilities are provided; pass weather changes fast and snow can fall even in midsummer. Bring insulation and a headlamp for dawn/night shoots; road status follows Alaska DNR and Matanuska-Susitna Borough postings.",
  "Summit Lake State Recreation SiteはHatcher Pass Road沿い（Hatcher Pass State Recreation Area内）にあり、Alaska DNRは道路の通行を夏期限定（概ね7月〜9月下旬）としている。積雪で峠は閉鎖される。湖畔に展望・ピクニック設備があるが、峠の天候は変わりやすく真夏でも雪が降り得る。夜明け/夜撮影は防寒とヘッドライトを携行し、通行状況はAlaska DNRとMatanuska-Susitna Boroughの告知に従うこと。"),
 'us-047': (
  "Matanuska Glacier State Recreation Site 位於 Glenn Highway Mile 101，由 Long Rifle Lodge 經營管理，Alaska DNR 明示：本區提供冰河觀景台（Edge Nature Trail 約20分鐘至觀景平台），但自園區無法下到冰河；日間使用收費，6 個營地先到先得。冬季視積雪關閉。實際踏冰需另經私人 Matanuska Glacier 入口（視冰況收費），安全與開放狀態以現場公告為準。",
  "Matanuska Glacier State Recreation Site is at Mile 101 of the Glenn Highway, managed by Long Rifle Lodge. Per Alaska DNR, the site offers glacier viewing platforms (the Edge Nature Trail, ~20 minutes to the platforms) but there is NO access to the glacier itself from the recreation site; day use is charged and the six campsites are first-come, first-served. The site closes when winter snow/ice conditions dictate. Walking on the ice requires the separate private Matanuska Glacier entrance (fee, conditions permitting) — safety and status follow on-site notices.",
  "Matanuska Glacier State Recreation SiteはGlenn Highway101マイルにあり、Long Rifle Lodgeが管理する。Alaska DNRによれば、園内は氷河展望台（Edge Nature Trail、展望台まで約20分）を提供するが、この遊園から氷河へ下りることはできない。日帰り利用は有料、6サイトのキャンプは先着順。冬は積雪状況で閉鎖。氷上歩行には別の私有Matanuska Glacier入口（状況次第で有料）が必要で、安全と開放状況は現地の掲示に従うこと。"),
 'us-048': (
  "Portage Valley 屬 Chugach National Forest：Begich, Boggs Visitor Center 位於 Portage Lake 北端（60.784, -148.842），夏季 Memorial Day–Labor Day 週四至週日 09:00–17:00 開放（成人 $5），展示與影片服務；Portage 冰河本體已從館內視野外退。2026年8月起北側停車場因天然氣管線施工封閉，請使用南側停車場。Portage Lake 灣畔步道與 Byron Glacier 步道免費；湖水冰冷、岸邊濕滑，且該區鄰近 Portage Lake 潛在滑坡帶，大雨後應保持警覺，安全資訊以 US Forest Service 公告為準。",
  "Portage Valley lies in Chugach National Forest: the Begich, Boggs Visitor Center is at the north end of Portage Lake (60.784, -148.842), open summer (Memorial Day–Labor Day) Thursday–Sunday 9 a.m.–5 p.m. ($5 adults), with exhibits and the park film; the Portage Glacier itself has receded out of view of the center. From August 2026 the north parking lot is closed for a natural-gas pipeline repair — use the south lot. The Portage Lake shoreline and Byron Glacier trails are free; the water is icy and banks are slick, and the area sits near a potential Portage Lake landslide zone — stay alert after heavy rain. Safety info follows US Forest Service postings.",
  "Portage Valleyはチュガチ国有林内。Begich, BoggsビジターセンターはPortage Lake北端（60.784, -148.842）にあり、夏（メモリアルデー〜レイバーデー）は木〜日9時〜17時営業（大人$5）、展示と映像あり。Portage氷河自体はセンターからは視界外に後退済み。2026年8月以降は北駐車場がガス配管工事のため閉鎖中で、南駐車場を利用。Portage Lake湖畔とByron Glacier遊歩道は無料。湖水は氷河で岸は滑りやすく、この地域はPortage Lake潜在地すべり帯の近くにあり大雨後は警戒を。安全情報はUS Forest Serviceの告知に従うこと。"),
 'us-050': (
  "朱諾市中心濱海 Marine Park 目前因重建工程暫時封閉（CBJ 公告施工自 2026 年 3 月起、預計 2027 年 4 月完工），步道繞行指示請依現場；Gastineau Channel 城市海景可改由 Seawalk 與感潮碼頭側取景。Goldbelt Tram（490 S. Franklin St）5–9 月運行、單日票可自由上下山，營運時刻每日變動且視山區天候調整；山頂可拍 Juneau／Stephens Passage／Chilkat Mountains 全景，清晨與藍調時段需先確認首末班纜車時間，資訊以官方公告為準。",
  "Downtown Juneau's waterfront Marine Park is TEMPORARILY CLOSED for rebuild construction (CBJ notices: construction from March 2026, completion expected April 2027) — follow pedestrian detour signs; Gastineau Channel city views can still be framed from the Seawalk and tideflats side. The Goldbelt Tram (490 S. Franklin St) runs May–September on an all-day pass, with hours that change daily and shut down for mountain weather; the top frames Juneau, Stephens Passage and the Chilkat Mountains. For blue-hour shoots confirm first/last tram times; info follows official postings.",
  "ジュノー市中心の海浜Marine Parkは現在再建工事のため一時閉鎖中（市公告：2026年3月着工、2027年4月完成予定）。歩行者迂回路の標示に従うこと。Gastineau Channelの眺めはSeawalk側から撮れる。Goldbelt Tram（490 S. Franklin St）は5〜9月運行で1日パス、営業時刻は日替わりで山の天候により変更。山頂からジュノー、Stephens Passage、Chilkat山脈を望める。撮影前に最初/最終のケーブルカー時刻を確認し、情報は公式告知に従うこと。"),
 'us-051': (
  "Mendenhall Glacier Visitor Center（6000 Glacier Spur Rd）夏季（5–9 月）每日 09:00–18:00 開放、圍繞步道與停車場外圍 06:00–24:00 全年開放；Nugget Falls、Photo Point 等步道免費不需門票（展示館成人收費，15 歲以下免費）。冬季館舍 2026–27 冬為整建關閉（僅餘部份週末開放，11–3 月原 10:00–16:00 週五六）。步道常見黑熊；近冰緣與瀑布側濕滑，冰上禁止，開放狀態以 US Forest Service 公告為準。",
  "Mendenhall Glacier Visitor Center (6000 Glacier Spur Rd) runs summer hours (May–Sep) 9 a.m.–6 p.m. daily; the grounds are open 6 a.m.–midnight year-round. Nugget Falls, Photo Point and the other trails are FREE — no entry fee (the exhibits are charged, under-15 free). In winter 2026–27 the center itself is closed for construction (normally Nov–Mar Fri/Sat 10 a.m.–4 p.m.). Black bears are common on trails; the glacier edge and falls spray are slick and walking on the ice is prohibited — status follows US Forest Service postings.",
  "Mendenhall Glacierビジターセンター（6000 Glacier Spur Rd）は夏期（5〜9月）毎日9時〜18時、周辺敷地は年中6時〜24時開放。Nugget Falls、Photo Pointなどの遊歩道は無料（展示館は有料、15歳以下無料）。2026〜27冬はセンター自体が改修のため閉鎖（通常11〜3月は金土10時〜16時）。遊歩道ではツキノワグマに出会うことが多く、氷河縁や滝の水煙は滑りやすく氷上は立ち入り禁止。状況はUS Forest Serviceの告知に従うこと。"),
 'us-052': (
  "Homer Spit 屬 City of Homer：Mariner Park（Spit 基部，111 英畝）有沙灘、34 個營位（4/1–10/31，每晚 $30，先到先得），Fishing Hole Campground 與 Tent Camp West 同期開放；Pay kiosk 或 text-to-pay 註冊。Spit 步行／騎車可達港灣與海濱店舖街；Kachemak Bay 潮差大，碼頭步道濕滑；日落到海灣西側為最佳方向。夜間無照明，營運與收費以市府公告為準。",
  "The Homer Spit is City of Homer property: Mariner Park (111 acres at the base of the Spit) has beach access and 34 campsites (April 1–October 31, $30/night, first-come first-served), with the Fishing Hole Campground and Tent Camp West open the same season; register at pay kiosks or by text-to-pay. The Spit's harbor and waterfront shops are walkable/bikeable; Kachemak Bay tides are large and dock surfaces are slick; sunsets fall over the western bay. There is no night lighting — operations and fees follow City of Homer postings.",
  "Homer SpitはHomer市所有：Spit基部のMariner Park（111エーカー）にはビールと34のキャンプサイト（4/1〜10/31、1泊$30、先着順）があり、Fishing Hole CampgroundとTent Camp Westも同シーズン営業。精算はペイキオスクまたはtext-to-pay。Spit内の港と海浜店舖は徒歩/自転車で回れる。カチェマック湾の潮差は大きく波止場は滑りやすい。日没は湾の西側へ。夜間照明はなく、運営と料金は市の告知に従うこと。"),
 'us-055': (
  "Kennecott Mines National Historic Landmark 位於 Wrangell-St. Elias 國家公園內，Kennecott Mill Town 距 McCarthy 北 5 哩；夏季（約5月底–9月中）Kennecott Visitor Center（Blackburn School）開放，時間請先電話 (907) 205-7106 確認。自用車不可進入 Kennecott，需私人 Shuttle／步行／自行車。冬季唯一通道是從 McCarthy 徒步／滑雪 5 哩。Root Glacier 步道自 Kennecott 出發，冰上活動建議導覽；建築區受 NPS 保護，請勿進入未開放建築，開放與安全以 NPS 公告為準。",
  "Kennecott Mines National Historic Landmark sits inside Wrangell-St. Elias NP; the Kennecott Mill Town is 5 miles north of McCarthy. The Kennecott Visitor Center (in the historic Blackburn School) opens in summer (late May–mid-September) — call (907) 205-7106 for hours. Private vehicles cannot enter Kennecott: use the private shuttle, or walk/bike. In winter the ONLY access is the 5-mile walk/ski from McCarthy. The Root Glacier trail leaves from Kennecott; guided travel is advised on the ice. Buildings are NPS-protected — stay out of non-open structures; access and safety follow NPS postings.",
  "Kennecott Mines National Historic Landmarkはランゲル・セントイライアス国立公園内、Kennecott Mill Townはマッカーシー北5マイル。Kennecottビジターセンター（Blackburn School）は夏期（5月末〜9月中旬）営業、時間は(907) 205-7106に確認。自家用車はKennecottへ入れず、民間シャトル/徒歩/自転車を利用。冬はマッカーシーからの5マイル徒歩/スキーのみ。Root Glacier遊歩道はKennecottから出発し、氷上はガイド推奨。建物はNPS保護対象で未公開建物には入れない。開放と安全はNPSの告知に従うこと。"),
 'us-056': (
  "Atigun Pass 為 Dalton Highway 最高點（BLM 標示 milepost 244、高程約 4,739 呎），免費通行。BLM 提醒：6–7 月也可能降雪暴，達爾頓公路屬偏遠粗礦路，野生動物頻繁；停車務必完全退出鋪面外。自 Fairbanks 車程約 8 小時，油料與補給須自帶；冬季與夜拍須辦理 511.alaska.gov 路況查詢，越過分水嶺後北側即為無樹凍原。安全與通行以 BLM 與 Alaska DOT&PF 公告為準。",
  "Atigun Pass is the highest point of the Dalton Highway (BLM: milepost 244, about 4,739 ft); access is free. BLM warns that snowstorms can hit even in June–July; the Dalton is a rough, remote gravel road with frequent wildlife — pull completely off the pavement when stopping. It is about 8 hours' drive from Fairbanks with no services en route; before winter or night shoots check 511.alaska.gov. North of the divide the tundra is treeless. Safety and access follow BLM and Alaska DOT&PF postings.",
  "Atigun Passはダルトン・ハイウェイの最高地点（BLM: milepost 244、標高約4,739フィート）で通行無料。BLMは6〜7月でも吹雪になり得ると注意喚起。ダルトンは荒れた未舗装路で野生動物が多く、停車時は完全に路面外へ。フェアバンクスから車で約8時間、途中サービスなし。冬や夜撮影前は511.alaska.govで路況確認。分水嶺以北は樹木のないツンドラ。安全と通行はBLMとAlaska DOT&PFの告知に従うこと。"),
 'us-057': (
  "BLM Arctic Circle Wayside 位於 Dalton Highway milepost 115 東側，設北極圈標誌、觀景台與解說牌（南北向取景最常用），現場禁止露營；BLM Arctic Circle Campground 在往東約 0.7 哩上坡處（含 pull-through 與帳位、無水）。冬季為拍極光名點但路面極冷、風雪不斷，請準備備援車輛通信與保暖；通行與露營規定以 BLM 公告為準。",
  "The BLM Arctic Circle Wayside sits on the EAST side of the Dalton Highway at milepost 115, with the Arctic Circle sign, an observation deck and interpretive panels (the classic photo). Camping is not allowed at the wayside; the BLM Arctic Circle Campground is 0.7 miles uphill to the east (pull-through and tent sites, no water). It is a celebrated aurora spot in winter, but conditions are extreme — carry warm gear and emergency communications. Access and camping rules follow BLM postings.",
  "BLM Arctic Circle Waysideはダルトン・ハイウェイmilepost 115の東側にあり、北極圏標識、展望デッキ、解説パネルがある（定番の記念撮影地）。サイト内でのキャンプは禁止。BLM Arctic Circle Campgroundは東へ0.7マイル上り（通過型とテントサイト、水なし）。冬はオーロラの名所だが気象は極めて厳しく、防寒と緊急通信手段を携行すること。通行とキャンプ規則はBLMの告知に従うこと。"),
 'us-059': (
  "Brooks Falls Platform 位於 Katmai 國家公園 Brooks Camp；進園必須先在 Brooks Camp Visitor Center 聽熊類安全簡報。雙層瀑布平台最多 40 人，滿員時需在候補名單並每次讓位 30 分鐘（旺季7月等待可超過1.5小時）；6/15–8/15 平台禁止大型三腳架（可折疊單腳使用）且 22:00–07:00 關閉（常延至9月底）。步道來回（單程1.2哩）只有開始處才有廁所。7 月中旬前後熊最多但人潮最滿，行前請確認 floatplane 與住宿。熊不會防禦地躲避相機，平台禮儀與禁令以 NPS 現場公告為準。",
  "Brooks Falls Platform is at Brooks Camp, Katmai NP: attend the mandatory bear-safety orientation at the Brooks Camp Visitor Center first. The two-tier Falls Platform holds 40 people max — when full, join the waiting list and yield after 30 minutes (July waits can exceed 1.5 hours). June 15–August 15: large tripods are banned (collapsed monopod OK) and the platforms close 10 p.m.–7 a.m. (often extended through September 30). The 1.2-mile one-way trail has the nearest restroom at its start. July has the most bears AND the most crowds — book floatplane and lodging early. Platform etiquette and bans follow NPS on-site postings.",
  "Brooks Falls Platformはカトマイ国立公園Brooks Camp内。まずBrooks Campビジターセンターで必須の熊安全オリエンテーションを受けること。二層の滝プラットフォームは定員40名で満員時は順番待ちリストに参加し30分で交代（7月の待ち時間は1.5時間超も可）。6/15〜8/15は大型三脚禁止（折りたたみモノポッド可）で22時〜7時は閉鎖（9月末まで延長されることが多い）。片道1.2マイルの遊歩道のトイレは起点のみ。7月は熊も人も最多で、水上機と宿は早めに確保。マナーと禁止事項はNPS現地告知に従うこと。"),
 'us-060': (
  "Glacier Bay National Park 的 Bartlett Cove 為唯一公路可達區：Public Dock 沿碼頭可拍 Gustavus／Glacier Bay 山海全景，無入場費但遊艇碼頭禮儀與貨物搬運注意。Glacier Bay Day Tour（Glacier Bay Lodge 運營）夏季每日早晨自 Bartlett Cove 出發整天巡灣，途經潮水冰河，受天候與浮冰影響路線；建議前一晚宿 Gustavus／Glacier Bay Lodge。實際班期與價格以 NPS 與特許商公告為準。",
  "In Glacier Bay NP, Bartlett Cove is the only road-accessible area: the Public Dock frames Glacier Bay's mountains-and-water panorama (no entry fee, but observe marina etiquette). The Glacier Bay Day Tour, run by Glacier Bay Lodge, departs Bartlett Cove each summer morning for a full day among the tidewater glaciers — the route shifts with weather and floating ice. Plan to overnight in Gustavus or at Glacier Bay Lodge the night before. Schedules and prices follow NPS and the concessioner's postings.",
  "グレイシャーベイ国立公園で道路で行けるのはBartlett Coveのみ：Public Dockからは公園の山海のパノラマが撮れる（入場無料だがマリナのマナーを守る）。Glacier Bay Lodge運営のGlacier Bay Day Tourは夏季毎朝Bartlett Coveを出発し、潮氷河を巡る一日ツアーで、路線は天候と流氷で変わる。前夜はGustavusかGlacier Bay Lodge泊を推奨。運航と価格はNPSとコンセッション事業者の告知に従うこと。"),
 'us-061': (
  "Fort Abercrombie State Historical Park 位於 Kodiak 島 1400 Abercrombie Drive（機場方向 West Rezanof Drive 轉入），Alaska DNR 管理：包括 WWII 海岸防禦遺跡（National Historic Landmark）、海蝕峭壁、雲杉林與 Lake Gertrude；有步道、8 個營位與 5 個 RV 位（限長 20 呎內，先到先得）。峭壁無護欄段請保持距離，風雨天拍照不佳，冬季可能結冰濕滑；營運時間與費用以 Alaska State Parks 公告為準。",
  "Fort Abercrombie State Historical Park is at 1400 Abercrombie Drive, Kodiak (from the airport take West Rezanof Drive). Managed by Alaska DNR, it combines WWII coastal-defense ruins (a National Historic Landmark), surf-hewn cliffs, spruce forest and Lake Gertrude; there are trails, 8 tent sites and 5 RV sites (max 20 ft, first-come first-served). Keep clear of unrailed cliff edges — storm photography is poor and winter surfaces ice over. Hours and fees follow Alaska State Parks postings.",
  "フォート・アバクロンビー州立歴史公園はコディアック島1400 Abercrombie Driveにあり（空港からはWest Rezanof Drive経由）。Alaska DNR管理で、第二次大戦の沿岸防衛遺跡（国定歴史ランドマーク）、荒波の海食崖、スプリュース林とLake Gertrudeを一域に含む。遊歩道、テント8サイト、RV5サイト（20フィート以下、先着順）。手すりのない崖端には近づかず、嵐の撮影は不向きで冬季は凍結滑落に注意。営業と料金はAlaska State Parksの告知に従うこと。"),
 'us-062': (
  "Eklutna Lake 屬 Chugach State Park，Alaska DNR 費用表：停車 $5、露營每站 $20。Lakeside Trail 是舊碎石路床，部份路面被湖水沖毀且坡度大；ATV 僅週日至週三可進入、自行車全週可騎。Eklutna 湖水冰涼，岸邊滑；夏季白天可拍湖景＋Chugach 峽谷山景，冬季常有冰雪，Eklutna Lake Road 路況以 Alaska State Parks 公告為準。",
  "Eklutna Lake is in Chugach State Park; per Alaska DNR's fee table, parking is $5 and camping $20/site. The Lakeside Trail follows an old gravel roadbed with some flood-damaged sections and a steep gradient; ATVs are allowed Sunday–Wednesday only, bicycles all week. The water is icy and banks are slick. Summer days frame the lake plus Chugach range and canyons; winter brings ice and snow. Eklutna Lake Road conditions follow Alaska State Parks postings.",
  "Eklutna Lakeはチュガチ州立公園内。Alaska DNRの料金表では駐車$5、キャンプ1サイト$20。Lakeside Trailは旧砂利道で、湖の水で部分的に破壊され勾配も急。ATVは日〜水のみ、自転車は終週可。湖水は冷たく岸は滑りやすい。夏は湖とチュガチ山地・峡谷を、冬は氷雪の景観を撮れる。Eklutna Lake Roadの状況はAlaska State Parksの告知に従うこと。"),
 'us-063': (
  "Talkeetna Riverfront Park 位於 Talkeetna 主街尾端（座標 62.3228, -150.1212），Susitna／Chulitna／Talkeetna 三河匯流處的砂礫灘上，可直面 Denali（McKinley）與 Alaska Range；清晨與傍晚山體 alpenglow 最為出色，水流湍急勿下水；Matanuska-Susitna Borough 管理無門票，公園規則與季節性淹水以現場公告為準。",
  "Talkeetna Riverfront Park is at the end of Talkeetna's Main Street (62.3228, -150.1212) — gravel bars at the confluence of the Susitna, Chulitna and Talkeetna rivers face Denali (McKinley) and the Alaska Range. Alpenglow is best at dawn and dusk; the currents are swift, never enter the water. Managed by the Matanuska-Susitna Borough with no entry fee — rules and seasonal flooding follow on-site postings.",
  "タルキートナ・リバーフロント公園はメインストリートの突き当たり（62.3228, -150.1212）にあり、Susitna・Chulitna・タルキートナの3河川合流点の砂礫州からデナリ（マッキンリー）とアラスカ山脈を正面に望む。朝夕の山影の紅光が最も美しい。流れは急で決して入水しないこと。Matanuska-Susitna Borough管理で入場料なし。規則と季節的洪水は現地の掲示に従うこと。"),
 'us-064': (
  "Alyeska Aerial Tram（Girdwood）連接度假村與 Mt. Alyeska 山頂的 Mountain Station（高程約 2,300 呎），從山頂可拍 Turnagain Arm、懸掛冰河與 Chugach 山景。官方公告：每年4月底–5月下旬年度檢修停駛，夏季約5月中–10月中每日運行、10–11月停駛、12–4月冬季每日運行；票價與時刻依季節（夏季約 10:00–19:00，視營運公告）而異。山頂溫度低且風大，藍調時段拍攝請確認末班車時間，運行與安全以 Alyeska Resort 公告為準。",
  "The Alyeska Aerial Tram (Girdwood) connects the resort to the Mountain Station on Mt. Alyeska (~2,300 ft), framing Turnagain Arm, hanging glaciers and the Chugach range. Per the resort: annual maintenance closes the tram late April–late May; summer runs daily from mid-May to early/mid-October, October–November is closed, and winter (December–April) runs daily. Times and fares vary by season (summer about 10 a.m.–7 p.m., check the tram status page). The top is cold and windy — confirm last tram time for blue-hour shoots; operations and safety follow Alyeska Resort postings.",
  "アライエスカ・エアリアル・トラム（ガードウッド）はリゾートとMt. Alyeska山頂のMountain Station（標高約2,300フィート）を結び、Turnagain Arm、つる氷河、チュガチ山地を望む。リゾート公式：年次点検のため4月末〜5月下旬は運休、夏は5月中旬〜10月上・中旬まで毎日運行、10〜11月は閉鎖、冬（12〜4月）は毎日運行。時刻と運賃は季節で変動（夏は概ね10時〜19時、トラム状況ページを確認）。山頂は冷風強く、ブルーアワー撮影は最終便を確認すること。運行と安全はAlyeska Resortの告知に従うこと。"),
 'us-069': (
  "Port Alsworth 為 Lake Clark 國家公園飛行進入門戶：NPS 明示無公路系統、鎮上無超市，需飛機（輪式或水上）抵達，中心有 NPS Visitor Center（僅夏季開放）與 Tanalian Trails 起點。湖景與環湖山脈可步行 Tanalian Falls／Kontrashibuna Lake 路線到達；訂票需直接聯繫持照 air taxi。降雪後步道結冰滑，飛機起降注意跑道，規則以 NPS 公告為準。",
  "Port Alsworth is the fly-in gateway to Lake Clark NP & Preserve: per the NPS there is no road system and NO grocery store — visitors arrive by small plane (wheels or floats), with the park Visitor Center open summer only and the Tanalian Trails starting in town. The lake-and-range panorama can be framed on the Tanalian Falls/Kontrashibuna Lake routes. Book directly with an authorized air taxi. Trails ice over after snow and aircraft use the active runways — rules follow NPS postings.",
  "ポート・アルズワースはレイククラーク国立公園の飛行機での玄関口：NPSによれば道路網がなく町に食料品店もない。小型機（車輪/フロート）で到着し、ビジターセンターは夏期のみ営業、Tanalian Trailsは町から出発する。湖と周囲の山並みはTanalian Falls/Kontrashibuna Lakeルートで撮れる。予約は認可されたエアタクシーに直接連絡。雪後は遊歩道が凍結し、滑走路は稼働中で横断に注意。規則はNPSの告知に従うこと。"),
 'us-071': (
  "Kerry Park（Franklin Place）位於 Queen Anne 山 211 W Highland Dr.，seattle.gov 官方頁面開放時間 06:00–22:00，免費、無停車場（街邊限時停車）。是 Seattle Skyline＋Space Needle＋Elliott Bay 的經典日落與夜景點，柵欄處最擠，三腳架建議早到；清晨拍日出亦有機會遠眺 Rainier。保護設備與安全以 Seattle Parks 現場規定為準。",
  "Kerry Park (Franklin Place) is on Queen Anne at 211 W Highland Dr.; the seattle.gov page lists hours 6 a.m.–10 p.m. Free, with no parking lot (limited street parking). It is THE classic Seattle Skyline + Space Needle + Elliott Bay sunset and night view — the railing gets crowded, arrive early with a tripod; dawn can also catch Rainier. Rules and safety follow Seattle Parks on-site postings.",
  "ケリー・パーク（Franklin Place）はクイーン・アン地区211 W Highland Dr.にあり、seattle.govの営業時間は6時〜22時。無料で駐車場なし（路上は時間制限）。シアトル・スカイライン＋スペース・ニードル＋エリオット湾の定番夕景・夜景撮影地で、手すり部分は混雑するため三脚は早めの到着を。朝にはレーニアも望める場合がある。規則と安全はSeattle Parksの現地掲示に従うこと。"),
 'us-072': (
  "Golden Gardens Park（8498 Seaview Pl. NW）濱 Puget Sound，夏季（5/1–9/30）04:00–22:30、其餘季節 04:00–23:30，停車場閘門 07:00 起（場外 Seaview Ave 路邊停車可提早）。沙灘西向可拍 Olympic Mountains＋日落＋篝火（fire pits 2026/5/22–9/7 開放除非禁火令）；細沙、水鳥與帆船同框。水上活動與寵物規定以 Seattle Parks 公告為準。",
  "Golden Gardens Park (8498 Seaview Pl. NW) fronts Puget Sound: summer hours (May 1–Sept 30) 4 a.m.–10:30 p.m., otherwise 4 a.m.–11:30 p.m.; the parking-lot gates open at 7 a.m. (street parking on Seaview Ave NW allows earlier access). The west-facing beach frames the Olympic Mountains, sunset and beach fires (fire pits open May 22–Sept 7, 2026, unless a burn ban) with sand, shorebirds and sailboats in the frame. Water-safety and pet rules follow Seattle Parks postings.",
  "ゴールデン・ガーデンズ・パーク（8498 Seaview Pl. NW）はピュージェット湾に面する。夏季（5/1〜9/30）は4時〜22時30分、それ以外は4時〜23時30分。駐車場の門は7時開門（Seaview Ave NWの路上ならもっと早く）。西向きのビールからオリンピック山脈、日没、ビーチファイア（2026年は5/22〜9/7、焚火禁止令がない限り）を撮れる。水の安全とペット規則はSeattle Parksの告知に従うこと。"),
 'us-073': (
  "Alki Beach Park 位於西西雅圖 Alki 海岸，與 Golden Gardens 相同之季節時制（夏季 04:00–22:30、其他 04:00–23:30）；沙灘、步道與碼頭可拍 Puget Sound＋Olympic Mountains＋渡輪剪影、以及海灘日落。海風與潮間濕滑注意，夜間部分照明有限；救生站與寵物規定以 Seattle Parks 公告為準。",
  "Alki Beach Park is on the West Seattle waterfront with the same seasonal hours as Golden Gardens (summer 4 a.m.–10:30 p.m., otherwise 4 a.m.–11:30 p.m.). Sand, promenade and the pier frame Puget Sound, the Olympic Mountains and ferry silhouettes, plus beach sunsets. Watch wind and slick intertidal surfaces; night lighting is partial. Lifeguard and pet rules follow Seattle Parks postings.",
  "アルキ・ビーチ・パークはウェスト・シアトルの海浜にあり、ゴールデン・ガーデンズと同じ季節時間制（夏4時〜22時30分、その他4時〜23時30分）。砂浜、遊歩道、桟橋からピュージェット湾、オリンピック山脈、フェリーのシルエットとビーチの夕日が撮れる。風と干潮時の滑りに注意、夜間照明は部分的。ライフガードとペット規則はSeattle Parksの告知に従うこと。"),
 'us-074': (
  "Gas Works Park 位於 2101 N Northlake Way，seattle.gov 開放 06:00–22:00。北岸草坪與 Kite Hill 對望 Lake Union 與 Seattle 天際線（含 Space Needle），日落與藍調時段水面反射尤佳；歷史煤氣廠構件為近景，雖有鏽蝕不可攀爬。水上船隻活動頻繁，安全與無人機規定以 Seattle Parks 公告為準。",
  "Gas Works Park (2101 N Northlake Way) is open 6 a.m.–10 p.m. per seattle.gov. The north lawn and Kite Hill face Lake Union and the Seattle skyline (Space Needle included); sunset and blue hour bring good water reflections, with the rusting gas-works structures in the foreground — climbable? no, stay off them. Boating traffic is heavy; drone and safety rules follow Seattle Parks postings.",
  "ガス・ワークス・パーク（2101 N Northlake Way）はseattle.govによると6時〜22時開放。北側芝生とKite Hillからレイク・ユニオンとシアトル・スカイライン（スペース・ニードル含む）を望み、夕景とブルーアワーは水面反射が良い。さびたガス製造設備が前景になるが登ることはできない。船舶の通行が多く、ドローンと安全規則はSeattle Parksの告知に従うこと。"),
 'us-075': (
  "Discovery Park（3801 Discovery Park Blvd.）是 Seattle 最大自然公園，官方開放 04:30–23:00；現階段 Visitor Center 重建中至 2027 年夏，全園照常開放但海灘層停車須许可（permit／ADA 標章以外禁止，違規拖吊），前往 West Point Lighthouse 須步行數公里。西部岬角可拍 Puget Sound＋Olympic/Cascade 山景與燈塔；步道多坡，日落到西側最理想。規定以 Seattle Parks 公告為準。",
  "Discovery Park (3801 Discovery Park Blvd.) is Seattle's largest natural park, open 4:30 a.m.–11 p.m. The Visitor Center is closed for reconstruction until Summer 2027 — the rest of the park is open as usual, but beach-level parking requires a permit (or ADA placard), with towing enforced, and the West Point Lighthouse is a multi-kilometer walk. The western headlands frame Puget Sound with Olympic/Cascade ranges and the lighthouse; trails are hilly and sunsets fall best to the west. Rules follow Seattle Parks postings.",
  "ディスカバリー・パーク（3801 Discovery Park Blvd.）はシアトル最大の自然公園で、4時30分〜23時開放。ビジターセンターは2027年夏まで再建のため閉鎖中だが公園は通常通り開放。ただしビールレベルの駐車は許可証（またはADAバッジ）が必要で違反はレッカー移動され、West Point灯台へは数キロの徒歩。西側の岬からピュージェット湾、オリンピック/カスケード山脈と灯台を撮れる。遊歩道は起伏が多く夕日は西向き。規則はSeattle Parksの告知に従うこと。"),
 'us-076': (
  "Hamilton Viewpoint Park 位於 West Seattle（1120 California Ave. SW），seattle.gov 開放 06:00–22:00，免費路邊停車。高台直接俯瞰 Seattle City＋Elliott Bay＋港口起重機與 Cascade 遠景，藍調與夜間城市燈火最為出色；小型社區公園夜間無照明、草地潮濕，安全規定以 Seattle Parks 現場公告為準。",
  "Hamilton Viewpoint Park is in West Seattle (1120 California Ave. SW), open 6 a.m.–10 p.m. per seattle.gov, with free street parking. The bluff looks straight down on the Seattle city core, Elliott Bay, harbor cranes and the distant Cascades — best at blue hour and night with city lights. It is a small neighborhood park with no night lighting and damp grass; safety rules follow Seattle Parks on-site postings.",
  "ハミルトン・ビューポイント・パークはウェスト・シアトル（1120 California Ave. SW）にあり、seattle.govでは6時〜22時開放、路上駐車無料。高台からシアトル市中心部、エリオット湾、港湾クレーン、遠くのカスケード山脈を一望でき、ブルーアワーと夜景が最適。小規模な住宅街の公園で夜間照明はなく草は湿っている。安全規則はSeattle Parksの現地掲示に従うこと。"),
 'us-077': (
  "Dr. Jose Rizal Park 位於 Beacon Hill（1007 12th Ave. S），seattle.gov 開放 04:00–23:30。高處公園俯視 I-90／South Downtown＋Elliott Bay，藍調／夜景時城市燈火與車流最為鮮明；沿樹叢步道走動注意地面濕滑與燈光不足，攝影儘量結伴並停在指定停車位，安全與規則以 Seattle Parks 公告為準。",
  "Dr. Jose Rizal Park is on Beacon Hill (1007 12th Ave. S), open 4 a.m.–11:30 p.m. per seattle.gov. The elevated park looks over I-90, South Downtown and Elliott Bay — city lights and traffic trails are sharpest at blue hour/night. Trails through thickets can be slick and dim; shoot with company and park in designated stalls. Safety and rules follow Seattle Parks postings.",
  "ホセ・リサール博士公園はビーコンヒル（1007 12th Ave. S）にあり、seattle.govでは4時〜23時30分開放。高台からI-90、ダウンタウン南部、エリオット湾を望み、ブルーアワーと夜景で都市の灯りと車の光の流れが最も鮮明。茂み沿いの道は滑りやすく照明が少ないため、仲間とともに撮影し指定駐車区画に停めること。安全と規則はSeattle Parksの告知に従うこと。"),
 'us-078': (
  "Myrtle Edwards Park（3130 Alaskan Way）沿 Elliott Bay 濱海步道，seattle.gov 列為 24 小時開放。2026 年 Elliott Bay Connections 整治後 6/4 重新開放；步道直接面向 Puget Sound＋Olympic 遠景與 Mt. Rainier 遠望，日落與藍調時段光線最佳，火車與船隻動態為近景。自行車流量大，注意安全；規定以 Seattle Parks 公告為準。",
  "Myrtle Edwards Park (3130 Alaskan Way) runs along the Elliott Bay waterfront; seattle.gov lists it as open 24 hours. It fully reopened June 4, 2026 after the Elliott Bay Connections project. The path faces Puget Sound with the distant Olympics and a far view of Mt. Rainier — sunset and blue hour are best, with trains and boats for foreground motion. Bike traffic is heavy — watch yourself; rules follow Seattle Parks postings.",
  "マートル・エドワーズ・パーク（3130 Alaskan Way）はエリオット湾の海浜沿いにあり、seattle.govでは24時間開放。2026年のElliott Bay Connections事業後、6月4日に全面再開。遊歩道からピュージェット湾、遠くのオリンピック山脈とレーニアの遠望が撮れ、夕景とブルーアワーが最適で、列車と船が前景の動きになる。自転車の通行が多いため注意。規則はSeattle Parksの告知に従うこと。"),
 'us-079': (
  "Snoqualmie Falls 為 268 呎瀑布，園區由 Puget Sound Energy 擁有與營運：每日 24 小時免費參觀（官網 FAQ：sunup–sundown 開放），上層停車場免費（跨天空步道進入）、下層停車 $7，Salish Lodge 客人另有專屬停車。多層觀景台無障礙；秋冬高水量時霧氣大，步道與欄杆濕滑，請勿越過欄杆；營運與規則以 PSE 與 City of Snoqualmie 公告為準。",
  "Snoqualmie Falls is a 268-ft waterfall owned and operated by Puget Sound Energy: free daily admission (FAQ: open sunup–sundown), free upper parking lot (sky-bridge access), $7 lower lot, with separate valet for Salish Lodge guests. Multiple ADA viewing decks; in high-water seasons spray is heavy and railings and paths are slick — stay behind the rails. Operations and rules follow PSE and City of Snoqualmie postings.",
  "スノコルミー滝は高さ268フィート、Puget Sound Energyが所有・運営：毎日無料公開（FAQ：日の出〜日の入り）、上段駐車場は無料（スカイブリッジ経由）、下段は$7、Salish Lodge宿泊者には専用バレあり。複数の展望台はバリアフリー。増水期は水煙が激しく手すりや通路が滑りやすいため柵の内側にとどまること。運営と規則はPSEとスノコルミー市の告知に従うこと。"),
 'us-080': (
  "Deception Pass State Park（41229 State Route 20, Oak Harbor）為華州最熱門州立公園之一：官方時制夏季（4–9月）06:30–dusk、冬季（10–3月）08:00–dusk，車輛需 Discover Pass。Deception Pass Bridge 人行步道可拍海峽潮流＋橋體＋Fidalgo／Whidbey 島剪影，西向日落最佳；橋上風大、欄杆低，請勿倚靠。停車與露營規定以 Washington State Parks 公告為準。",
  "Deception Pass State Park (41229 State Route 20, Oak Harbor) is one of Washington's most-visited state parks: official hours are summer (April–September) 6:30 a.m.–dusk and winter (October–March) 8 a.m.–dusk; a Discover Pass is required for vehicles. The pedestrian walkway on Deception Pass Bridge frames the tidal channel, the bridge structure and Whidbey/Fidalgo silhouettes — sunsets fall best to the west. The bridge deck is windy with low rails — do not lean on them. Parking and camping rules follow Washington State Parks postings.",
  "デセプション・パス州立公園（41229 State Route 20, Oak Harbor）はワシントン州で最も人気の州立公園の一つ：公式営業時間は夏（4〜9月）6時30分〜日没、冬（10〜3月）8時〜日没、車両にはDiscover Passが必要。デセプション・パス橋の歩道からは潮流、橋、ウィッドビー/ファイダルゴ島のシルエットが撮れ、日没は西向きが最適。橋上は風が強く手すりが低いのでもたれないこと。駐車とキャンプ規則はWashington State Parksの告知に従うこと。"),
 'us-081': (
  "Paradise（Mount Rainier 國家公園，海拔 5,400 呎）夏季主要遊客中心 Henry M. Jackson Memorial Visitor Center 每日開放（約5月至10月初），10月中至4月僅週末與假日開放；園區入場收費。夏季野花與霧草甸為 7–8 月亮點，冬季雪原；高山天氣多變，請自備保暖與防滑（冰雪時建議攜雪鏈／雪鞋），Wilderness 與步道規定以 NPS 公告為準。",
  "Paradise (Mount Rainier NP, 5,400 ft): the main Henry M. Jackson Memorial Visitor Center is open daily in summer (about May–early October) and weekends/holidays from mid-October through April; park entry is charged. Wildflower meadows peak July–August; winter is snowfield — mountain weather changes fast, bring warm layers and traction (carry chains/snowshoes when icy). Trail and wilderness rules follow NPS postings.",
  "パラダイス（マウント・レーニア国立公園、標高5,400フィート）：本館のHenry M. Jackson Memorial Visitor Centerは夏期（約5月〜10月上旬）毎日開放、10月中旬〜4月は週末と祝日のみ。入園は有料。夏は7〜8月に野花の草地、冬は雪原。山の天候は変わりやすく防寒と滑り止め（凍結時はチェーン/スノーシュー携行）を持参すること。遊歩道と wilderness の規則はNPSの告知に従うこと。"),
 'us-082': (
  "Reflection Lakes 位於 Mount Rainier 國家公園東南（Mather Memorial Parkway / SR 706 以東），海拔約 4,900 呎；官方公園手冊介紹其為拍攝 Rainier 倒影的名點。路側停車有限、無設施，清晨無風時倒影最佳；路肩狹窄且車流快，請務必停在鋪裝區外；秋季夜間結冰，冬季積雪封路（SR 123/SR 706 視季節），通行與安全以 NPS 公告為準。",
  "Reflection Lakes lie on Mount Rainier NP's southern approach — the park brochure features them as THE Rainier-reflection spot. Roadside parking is limited with no facilities; reflections are best on windless mornings. The shoulder is narrow and traffic fast — park fully off the pavement; night frosts in autumn and winter snow close the roads seasonally. Access and safety follow NPS postings.",
  "Reflection Lakesはマウント・レーニア国立公園の南側から入る道沿いにあり、公式パークパンフレットがレーニアの鏡面反射スポットとして紹介する。路側駐車は限られ設備なし。逆さ映りは無風の早朝が最適。路肩は狭く車の流れが速いため舗装外に完全停車すること。秋の夜は霜、冬は積雪で道路は季節閉鎖。通行と安全はNPSの告知に従うこと。"),
 'us-083': (
  "Sunrise（Mount Rainier 東北側，海拔 6,400 呎）為園內最高可達觀景區：官方手冊明示 Sunrise Visitor Center 與 Day Lodge 每年僅 7 月至 9 月下旬開放，Sunrise Point 附近有近 360° 山景；入園收費。高海拔夜間寒冷，秋季可能初雪，日出前車程較長請提早出發；道路與服務開放以 NPS 公告為準。",
  "Sunrise (northeast Mount Rainier, 6,400 ft) is the highest drive-in viewpoint in the park: the official brochure states the Sunrise Visitor Center and Day Lodge open only July through late September, with near-360° mountain views around Sunrise Point; entry is charged. Nights are cold at altitude and early snow can fall in autumn — leave early for dawn shoots. Road and service openings follow NPS postings.",
  "サンライズ（マウント・レーニア北東部、標高6,400フィート）は園内で最も高い車で行ける展望地：公式パンフレットではSunriseビジターセンターとデイ・ロッジは毎年7月〜9月下旬のみ開放で、Sunrise Point周辺はほぼ360°の山の見晴らし。入園は有料。高所の夜は冷え、秋には初雪もあるため日の出撮影は早めに出発すること。道路とサービスの開放はNPSの告知に従うこと。"),
 'us-084': (
  "Tipsoo Lake 位於 Chinook Pass 東側入口（SR 410 路旁、海拔 5,432 呎），官方手冊列出野餐區與廁所，是 Rainier 東面倒影與野花／秋色名點；夏末至 9 月初山區花海最盛、10 月起可能降雪，SR 410 高海拔段冬季封閉。路旁停車位有限，日出光線最佳；通行與安全以 NPS 公告為準。",
  "Tipsoo Lake sits by the eastern entrance at Chinook Pass (on SR 410, 5,432 ft); the official brochure lists a picnic area and restroom, and it is the classic Rainier east-side reflection with wildflowers and fall color. Meadows peak late summer to early September; snow can fall from October and the high section of SR 410 closes in winter. Roadside parking is limited — dawn light is best. Access and safety follow NPS postings.",
  "チプソー湖はチヌーク・パスの東入口沿い（SR 410、標高5,432フィート）にあり、公式パンフレットはピクニック場とトイレを掲載。レーニア東側の反射と野花・紅葉の名所。花盛りは夏末〜9月上旬、10月からは雪が降り始めSR 410の高標高区間は冬に閉鎖。路側駐車は限られ、日の出の光が最適。通行と安全はNPSの告知に従うこと。"),
 'us-085': (
  "Ruby Beach 位於 Olympic 國家公園太平洋海岸（Kalaloch／Ruby Beach 區）：官方說明由 US 101 停車場經約 0.2 呎步道下到海岸，是園內可及的 sea stacks 與漂流木景點（目前僅該觀景點開放）。公園全年 24 小時開放但設施季節性調整；海灘木頭濕滑、巨浪無預警，請勿背海久站或夜間越過漂流木堆，潮汐與安全以 NPS 公告為準。",
  "Ruby Beach is on Olympic NP's Pacific coast (Kalaloch/Ruby Beach area): officially reached by a short ~0.2-mile trail from the US 101 parking to the coast — the accessible sea-stack and driftwood viewpoint (only that viewpoint currently accessible). The park is open 24 hours year-round with seasonal facilities. Driftwood is slick and rogue waves strike without warning — do not stand with your back to the sea or cross driftwood piles at night. Tides and safety follow NPS postings.",
  "ルビー・ビーチはオリンピック国立公園の太平洋岸（カラロック/ルビー・ビーチ地区）：公式にはUS 101駐車場から約0.2マイルの遊歩道で海岸へ降りる。シースタックと流木の名所として利用可能（現在アクセス可能な展望点のみ）。公園は年中24時間開放だが設備は季節で変わる。流木は滑りやすく、異常な大波が突然来るため海に背を向けたまま立ったり、夜に流木を越えたりしないこと。潮汐と安全はNPSの告知に従うこと。"),
 'us-086': (
  "Rialto Beach 屬 Olympic 國家公園 Mora 區：官方說明沿海灘 1.5 哩即可達 Hole-in-the-Wall 海蝕拱門與潮池（僅低潮時露出），拱門通過需知潮汐與安全，必須事先查 NPS 潮汐表。公園全年 24 小時開放；海灘多漂流木與巨浪、西向日落最佳；拱門附近退潮路線會被海切斷，請預留返程時間，安全以 NPS 公告為準。",
  "Rialto Beach is in Olympic NP's Mora area: officially, a 1.5-mile beach walk reaches Hole-in-the-Wall, the sea arch and tidepools (exposed at low tide only) — crossing requires tide knowledge; check the NPS tide tables first. The park is open 24 hours year-round. The beach carries driftwood and heavy surf and sunsets fall to the west; the low-tide route past the arch gets cut off by the sea — budget return time. Safety follows NPS postings.",
  "リアルト・ビーチはオリンピック国立公園のモーラ地区：公式には1.5マイルのビーチウォークでHole-in-the-Wall（海食アーチ）とタイドプールに到着（干潮時のみ現れる）—通過には潮の知識が必要で、事前にNPS潮汐表を確認。公園は年中24時間開放。流木と高波があり、日没は西向き。アーチ付近の干潮ルートは海で途切れるため帰路の時間を確保すること。安全はNPSの告知に従うこと。"),
 'us-087': (
  "Hurricane Ridge 位於 Olympic 國家公園北側（海拔約 5,200 呎）：公園 24 小時開放但 Hurricane Ridge Road 感謝節與聖誕節封閉、且依天候與工程隨時封路（路面結冰／積雪時需雪鏈），官方建議撥打 360-565-3131 路況熱線。高處可拍 Olympic 山層次與雲海，冬季為滑雪場；風大且溫差大，三腳架需穩固，規定以 NPS 公告為準。",
  "Hurricane Ridge is on Olympic NP's north side (~5,200 ft): the park is open 24 hours, but Hurricane Ridge Road closes Thanksgiving and Christmas and can close any time for weather or construction (chains required when iced) — call the road line 360-565-3131. From the top, layered Olympic ranges and cloud seas frame out; it is also a ski area in winter. Wind is strong and temperatures swing; use stable tripod setups. Rules follow NPS postings.",
  "ハリケーン・リッジはオリンピック国立公園の北側（標高約5,200フィート）：公園は年中24時間開放だが、Hurricane Ridge Roadは感謝祭とクリスマスは閉鎖し、天候や工事でいつでも通行止めになり得る（凍結時はチェーン必須）。公式の道路情報 360-565-3131 を利用。高台からオリンピック山脈の層と雲海が撮れ、冬はスキー場にもなる。風が強く気温差が大きいため三脚は安定させ、規則はNPSの告知に従うこと。"),
 'us-088': (
  "Hoh Rain Forest 位於 Olympic 國家公園西側（Upper Hoh Road 終點）：官方說明 Mini Trail（0.1 哩）、Hall of Mosses（0.8 哩）與 Spruce Nature Trail（1.2 哩）為雨林苔蘚／薄霧／漫射光經典路線，Visitor Center 與設施為季節性；公園 24 小時開放但道路可能因天候封閉。請勿踐踏苔蘚與溪畔植物，步道與停車位有限，規定以 NPS 公告為準。",
  "The Hoh Rain Forest is on Olympic NP's west side (end of Upper Hoh Road): officially, the Mini Trail (0.1 mi), Hall of Mosses (0.8 mi) and Spruce Nature Trail (1.2 mi) are the classic moss, mist and diffused-light loops; the Visitor Center and facilities run seasonally. The park is open 24 hours but the road can close for weather. Do not trample mosses or streamside plants; trails and parking are limited. Rules follow NPS postings.",
  "ホー雨林はオリンピック国立公園の西側（Upper Hoh Road終点）：公式のMini Trail（0.1マイル）、Hall of Mosses（0.8マイル）、Spruce Nature Trail（1.2マイル）が苔・霧・拡散光の定番ルートで、ビジターセンターと設備は季節運営。公園は年中24時間だが道路は天候により通行止めになることがある。苔や渓畔の植物を踏まず、遊歩道と駐車は限られる。規則はNPSの告知に従うこと。"),
 'us-089': (
  "Palouse Falls State Park Heritage Site（94 英畝日間公園，Palouse Falls Road, LaCrosse）為華州官方瀑布：官方時制夏季 06:30–dusk、冬季 08:00–dusk。峽谷邊緣無護欄、玄武岩地面濕滑與鬆散，切勿越過欄杆或靠近邊緣；日出光線投在峽谷東面最為理想。車輛需 Discover Pass（以 parks.wa.gov 最新公告為準）。",
  "Palouse Falls State Park Heritage Site (94-acre day-use park, Palouse Falls Road, LaCrosse) is Washington's official state waterfall: official hours are summer 6:30 a.m.–dusk and winter 8 a.m.–dusk. The canyon rim is unrailed in places with slick, crumbling basalt — never go past fences or approach edges; sunrise light on the east-facing canyon wall is ideal. A Discover Pass is required for vehicles (per current parks.wa.gov rules).",
  "パルース・フォールズ州立公園遺産地（94エーカーのデイユース公園、Palouse Falls Road, LaCrosse）はワシントン州公式の州の滝：公式営業時間は夏6時30分〜日没、冬8時〜日没。峡谷の縁には手すりのない所があり玄武岩は滑りやすく崩れやすい。柵を越えたり縁に近づいたりしないこと。日の出の光が東向きの峡谷壁に当たるのが理想。車両にはDiscover Passが必要（最新のparks.wa.gov規則による）。"),
 'us-090': (
  "Diablo Lake Overlook 位於 North Cascades 之 State Route 20 Mile 131.7：NPS 設停車場（含 RV／巴士位）、野餐桌與廁所，免停車證（此地不收費），可拍藍綠色冰川湖＋Diablo Dam 遠景＋North Cascades 山景。夏季 7–9 月冰河粉末讓湖水最為鮮豔、晴天更佳；SR 20 冬季（約 11 月底–4 月）封閉，通行以 WSDOT／NPS 公告為準。",
  "The Diablo Lake Overlook is on State Route 20 at Mile 131.7 in the North Cascades: the NPS provides parking (including RV/bus), picnic tables and a vault toilet; no parking pass is needed there. The view frames the turquoise glacial lake, the distant Diablo Dam and North Cascades peaks. July–September glacial flour makes the color most vivid on sunny days; SR 20 closes for winter (about late November–April). Access follows WSDOT/NPS postings.",
  "ディアブロ・レイク・オブルックはノースカスケーズのState Route 20の131.7マイル地点：NPSは駐車場（RV/バス含む）、ピクニックテーブルと汲み取りトイレを設置し、ここでは駐車証不要。ターコイズの冰川湖、遠くのDiabloダム、ノースカスケーズの山並みを撮れる。7〜9月は氷河由来の微粒子で湖色が最も鮮やかで晴天向き。SR 20は冬（約11月末〜4月）閉鎖。通行はWSDOT/NPSの告知に従うこと。"),
 'us-091': (
  "Washington Pass Overlook 位於 State Route 20 東段（海拔 5,477 呎）：0.3 哩鋪面步道直達俯瞰 Liberty Bell Mountain 與 Early Winters Spires 的平台，免費、可牽繩狗。秋季（約 10 月）落葉松轉金黃最為搶眼；NPS 明示 SR 20 通常 11 月底／12 月初至 4 月／5 月初雪封（此前亦可能有野火封路），行前查 WSDOT；平台無護欄段勿靠近邊緣，規定以 WSDOT／USFS 公告為準。",
  "The Washington Pass Overlook is on the east section of State Route 20 (5,477 ft): a 0.3-mile paved path reaches the platform facing Liberty Bell Mountain and the Early Winters Spires; free, leashed dogs OK. Larches turn gold in October; the NPS notes SR 20 normally closes late November/early December to April/early May (wildfire closures can come earlier). Check WSDOT before driving; stay off unrailed edges. Rules follow WSDOT/USFS postings.",
  "ワシントン・パス展望台はState Route 20の東区間（標高5,477フィート）：0.3マイルの舗装遊歩道でLiberty Bell MountainとEarly Winters Spiresを望む展望台へ。無料でリード付き犬可。10月頃にカラマツが黄金色に変わる。NPSによればSR 20は通常11月末/12月初から4月/5月初まで雪で閉鎖（山火事による閉鎖もある）。出発前にWSDOTを確認し、手すりのない縁には近づかないこと。規則はWSDOT/USFSの告知に従うこと。"),
 'us-092': (
  "Artist Point 位於 Mount Baker Scenic Byway（SR 542）終點：USFS 明示道路冬季不除雪、無固定開放／封閉日期——首次大雪（9 月底–11 月初）後封閉，通常 7 月初開通；7–10 月為車輛可達，冬季僅非動力雪上活動（需雪崩評估）。11/1–4 月法律要求隨車雪鏈。48.8464, -121.6919 的停車場可拍 Mt. Shuksan／Mt. Baker；無自來水，高山天氣多變，通行與安全以 USFS／WSDOT 公告為準。",
  "Artist Point is at the end of the Mount Baker Scenic Byway (SR 542): per the USFS the road is NOT plowed in winter with no fixed closure date — it closes after the first significant snowfall (late September–early November) and typically reopens by early July; vehicles can reach it July–October, and winter access is non-motorized only (avalanche assessment needed). Chains are legally required on the vehicle November 1–April. The parking area at 48.8464, -121.6919 frames Mt. Shuksan and Mt. Baker; there is no potable water and mountain weather changes fast. Access and safety follow USFS/WSDOT postings.",
  "アーティスト・ポイントはマウント・ベイカー・シーニック・バイウェイ（SR 542）の終点：USFSによれば冬は排雪されず、決まった開放/閉鎖日もない。最初の大雪（9月末〜11月初）で閉鎖し通常は7月初めに開通、車両は7〜10月に到達可能、冬は非動力の雪上のみ（雪崩評価必須）。11/1〜4月は車にチェーン積載が法的義務。48.8464, -121.6919の駐車場からMt. ShuksanとMt. Bakerを撮れる。飲料水はなく山の天候は変わりやすい。通行と安全はUSFS/WSDOTの告知に従うこと。"),
 'us-093': (
  "Picture Lake 位於 Heather Meadows 休憩區（SR 542 上、Artist Point 之前）：美國林務署 Mt. Baker Highway 頁介紹 Heather Meadows 提供多處賞景點，Picture Lake 的 Mt. Shuksan 倒影為其代表；與 Artist Point 相同的季節性（約 7–10 月車輛可達，冬季道路不除雪），無門票。湖畔步道短、濕滑，三腳架位置有限，規定以 USFS／WSDOT 公告為準。",
  "Picture Lake is in the Heather Meadows Recreation Area (on SR 542, before Artist Point): the USFS Mt. Baker Highway page describes Heather Meadows as offering multiple scenic vantage points — Picture Lake's Mt. Shuksan reflection is the classic one. Same seasonal access as Artist Point (vehicles roughly July–October; no winter plowing), no fee. The lakeside path is short but slick and tripod spots are limited. Rules follow USFS/WSDOT postings.",
  "ピクチャー・レイクはヒーザー・メドーズ保養地（SR 542上、アーティスト・ポイント手前）：USFSのMt. Baker Highwayページはヒーザー・メドーズに複数の展望地があると説明し、ピクチャー・レイクのMt. Shuksanの反射がその代表。アーティスト・ポイントと同じ季節性（車両は約7〜10月、冬は排雪なし）、料金なし。湖畔の道は短いが滑りやすく三脚の設置場所は限られる。規則はUSFS/WSDOTの告知に従うこと。"),
 'us-094': (
  "Steptoe Butte State Park Heritage Site 位於 Palouse 丘陵（Whitman 郡）：官方頁面明示全年 08:00–dusk 開放。但頂部 3,612 呎的環景道路俯瞰 Palouse 農田光影，日出與日落最為經典；山路為螺旋鋪面上坡、夜間無照明，注意會車與風；發燒時段停車位有限。車輛與規定以 Washington State Parks 公告為準。",
  "Steptoe Butte State Park Heritage Site rises above the Palouse hills (Whitman County): the official page states year-round hours 8 a.m.–dusk. The summit road (3,612 ft) gives a 360° panorama of Palouse farmland light and shadow — dawn and dusk are classic. The spiraling paved road is steep with no night lighting — watch passing traffic and wind; parking is limited at peak times. Vehicles and rules follow Washington State Parks postings.",
  "ステプトー・ビュート州立公園遺産地はパルースの丘陵（ホワイトマン郡）にそびえ、公式ページでは年中8時〜日没開放。標高3,612フィートの山頂道路からパルース農地の光と影の360°パノラマが望め、日の出と日の入りが定番。螺旋状の舗装道は急で夜間照明はなく、対向車と風に注意。人気時間帯の駐車は限られる。車両と規則はWashington State Parksの告知に従うこと。"),
 'us-095': (
  "Cape Disappointment State Park（Ilwaco）位於 Columbia 河口北側：官方時制 06:30–dusk 全年；Lewis & Clark Interpretive Center（244 Robert Gray Drive）夏季（4/1–10/31）每日 10:00–17:00、冬季（11/1–3/31）週三至週日 10:00–17:00，特定假日休館。岬角燈塔、海蝕峭壁與風暴海景最為出名；峭壁無護欄段與巨浪，風暴期請遠離棧道邊緣，規定以 Washington State Parks 公告為準。",
  "Cape Disappointment State Park (Ilwaco) sits on the north side of the Columbia River mouth: official hours are 6:30 a.m.–dusk year-round. The Lewis & Clark Interpretive Center (244 Robert Gray Drive) opens daily 10 a.m.–5 p.m. in summer (April 1–October 31) and Wed–Sun 10 a.m.–5 p.m. in winter (November 1–March 31), closed certain holidays. The headland lighthouse, sea cliffs and storm seas are the signature — unrailed cliff edges and heavy surf: keep away from the edges in storms. Rules follow Washington State Parks postings.",
  "ケープ・ディサポイントメント州立公園（イルワコ）はコロンビア川河口の北側：公式営業は年中6時30分〜日没。Lewis & Clark Interpretive Center（244 Robert Gray Drive）は夏（4/1〜10/31）毎日10時〜17時、冬（11/1〜3/31）は水〜日10時〜17時、特定祝日は休館。岬の灯台、海食崖、嵐の海が名物。手すりのない崖端と大波に注意し、嵐の時期は縁から離れること。規則はWashington State Parksの告知に従うこと。"),
 'us-096': (
  "Dry Falls 解說點位於 Channeled Scabland（35661 Hwy 17 North, Coulee City）：Sun Lakes-Dry Falls State Park 官方時制夏季 06:30–dusk、冬季 08:00–dusk。官方公告：Dry Falls Visitor Center 2026 年全年整修關閉（含廁所與停車場），此地停車不需 Discover Pass。冰河洪水巨型乾瀑峭壁可自觀景平台拍攝；地面崎嶇與夏季高溫，請備水與防曬，規定以 Washington State Parks 公告為準。",
  "The Dry Falls interpretive point is in the Channeled Scabland (35661 Hwy 17 North, Coulee City): Sun Lakes-Dry Falls State Park's official hours are summer 6:30 a.m.–dusk and winter 8 a.m.–dusk. OFFICIAL NOTICE: the Dry Falls Visitor Center is closed for renovation through the end of 2026 (including restrooms and parking lot); no Discover Pass is required to park here. The giant dry-falls cliff can be framed from the viewing platform; the ground is rugged and summers are hot — carry water and sun protection. Rules follow Washington State Parks postings.",
  "ドライ・フォールズの解説地はチャネールド・スキャブラッド（35661 Hwy 17 North, Coulee City）：Sun Lakes-Dry Falls州立公園の公式営業は夏6時30分〜日没、冬8時〜日没。公式告知：Dry Fallsビジターセンターは2026年末まで改修のため閉鎖（トイレと駐車場を含む）。ここでの駐車にDiscover Passは不要。巨大な乾瀑の崖は展望台から撮れ、足場は荒く夏は高温のため水と日焼け対策を携行すること。規則はWashington State Parksの告知に従うこと。"),
}
GEOMETRY_CHECKS = {
 'us-045': ('no-conflict',
  'catalog point 60.103141,-149.434574 is on the Resurrection Bay shoreline between the small boat harbor and the SeaLife Center, matching the Seward Waterfront Park location (60.104788,-149.43355 listed for the park) — same feature'),
 'us-048': ('no-conflict',
  'catalog point 60.78452,-148.842 matches the US Forest Service coordinates for the Begich, Boggs Visitor Center (60.78394846,-148.8420394) at the north end of Portage Lake — correct feature'),
 'us-055': ('no-conflict',
  'catalog point 61.481048,-142.885231 is the Kennecott Mill Town (5 mi north of McCarthy), consistent with the NPS Kennecott Visitor Center location'),
 'us-057': ('no-conflict',
  'catalog point 66.55601,-150.8107 lies on the Dalton Highway at approximately milepost 115, matching the BLM Arctic Circle Wayside description (east side of the highway)'),
 'us-063': ('no-conflict',
  'catalog point 62.322846,-150.121177 exactly matches the Talkeetna Riverfront Park coordinates (confluence of Susitna/Chulitna/Talkeetna rivers)'),
 'us-064': ('no-conflict',
  'catalog point 60.96154,-149.07937 is on the Mt. Alyeska massif above Girdwood near the upper aerial-tram terminal area (resort maps); exact viewpoint not field-surveyed — no conflicting authoritative coordinate found in this pass'),
 'us-092': ('no-conflict',
  'catalog point 48.8465,-121.6927 matches the US Forest Service coordinates for the Artist Point trailhead (48.84637222,-121.6919444) — same feature'),
}
