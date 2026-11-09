# Round 8 Live Audit — chaselights.app (2026-11-09)

Auditor: ChaseLights reviewer (live, read-only). Cache-busted loads (`?nc=`), desktop 1264px + 390px CDP emulation (`Emulation.setDeviceMetricsOverride`). Languages exercised: zh-TW / en / ja. Last update stamp during audit: 最後更新：11/09 下午12:06–12:11 [GMT+8].

## Overall: FAIL

(Modal-day-anchor contradiction, unfit cards without plain-language reasons, one daylight subject with a 21:00 qualifying window, terrain-word mislabel, missing-name data cards, open-modal not re-rendered on language switch, modal stacking.)

## Findings

- [Major] Modal (紐約曼哈頓天際線) — 即時條件評估「今天 符合時數 0 此日已過，時段不計入符合」 vs 同一 modal「🎯 下一個符合時段：今天 11/09 06:00」 — 同一 modal 兩個日期錨點互相矛盾：表格宣稱今天時段已過，下一窗行卻說今天 06:00 尚未到；攝影師無從判斷現在出發是否來得及。(Also contradicts 天氣預報 modal:「今天 11/09 06:00、17:05 起還有 2 小時適合拍攝」— same spot, same day.)
- [Major] 大彎國家公園・聖埃倫娜峽谷 Santa Elena Canyon — 卡片「📷 本日最佳題材：聖埃倫娜峽谷縱景 符合時數 2 ⏱️ 最佳拍攝時段：15:00、21:00」 — 白天縱景題材掛 21:00 窗（德州當地日沒約 17:50，21:00 全黑）：攝影師按卡片夜裡進峽谷什麼都拍不到。與 22:00–06:00 禁令同構（僅差 1 小時），屬同一缺陷類。
- [Major] 布萊斯峽谷國家公園 Bryce Canyon NP — 「未符 · 現在不在日出時段，等不到曙光打上海面」 — Bryce Canyon 沒有海：「打上海面」為錯誤地形詞（模板殘留），攝影師會誤解評估對象。
- [Major] 布魯克斯瀑布・鮭魚道水景 Brooks Falls (ak) — 卡片整行只有「📅 資料不足」＋天氣晶片，未說明缺什麼 — 黑盒卡片（對照知床ウトロ流氷有「評估條件尚未查證，無法判定」、聖路易斯大拱門有「攝影題材條件尚未完成查證」）：使用者不知道是缺題材定義、缺座標還是缺季節窗。
- [Minor] 諏訪湖 (jp) — 卡片完全沒有任何判定行（無 📷 本日最佳題材、無 📅 本日無符合題材、無未符原因），只有天氣晶片 — 無判定也無解釋，比「無符合題材」更黑盒。
- [Minor] 多張「本日無符合題材」卡片無任何未符原因與下一窗（franklin 級缺失）：何塞・黎剎博士公園、阿爾基海灘公園、煤氣廠公園、凱瑞公園、漢密爾頓觀景公園、默特爾・愛德華茲公園、卡特邁國家公園、冰河灣國家公園、波蒂奇冰河、抹茶山 — 違反「每個不符判定必須帶一句白話原因」；攝影師只看到「今天不行」但不知道是雲、雨還是時段。
- [Minor] 森吉山樹氷、高野山 (jp) — 正午 JST 顯示「未符 · 已過民用光線，天色太暗看不到」 — 原因與當地當下時間矛盾（中午不可能已過民用光線）：錨點或套用錯錯誤，攝影師在白天被告知天太暗。
- [Minor] 湯普森山口雪牆「下一個符合時段：11/12 11:00」、塔爾基特納「11/12 12:00」、蘇華德「11/12 09:00」、優勝美地半圓頂「11/12 16:05」 — 純絕對日期無相對詞，同頁其他卡片皆為「明天 11/10／後天 11/11」格式；且 11/12 距今 3 天卻連「大後天」都沒標，攝影師需自行換算。
- [Minor] 卡片點擊會同時留下前一景點的「🌦️ 天氣預報」modal 不關閉（實測：開曼哈頓天氣 modal 後點阿卡迪亞卡片，兩個 modal 疊開，天氣 modal 仍顯示曼哈頓內容） — 攝影師以為看的是當前景點的天氣。
- [Minor] 語言切換時已開啟的「🌦️ 天氣預報」modal 不會重新渲染：頁面切到 en/ja 後，開著的天氣 modal 仍整份 zh-TW（業主既定規則：已開 modal 應以新語言重繪；攝影資訊 modal 有正確重繪）。
- [Minor] 首頁地區選單僅 🇹🇼/🇯🇵/🇺🇸 三國 — 無獨立 ak/hi 分頁；阿拉斯加與夏威夷景點混在「美國」清單（118 卡）。若產品定義 ak/hi 為獨立 frame，首頁未反映。
- [Minor] en 顯示「Acadia NP – Cadillac Mountain (Cadillac Mountain)」 — 括號內重複同名（英文名殘留中文原名結構），攝影師看到重複名稱以為有兩個點。
- [Minor] 景點氣象分析 modal 於卡片點擊路徑下長時間（>30s 實測）僅顯示殼（無景點名、無摘要、無逐時格、無資料來源），無載入指示；同 spot 由「天氣預報」晶片進入則 8 秒內有完整內容 — 載入中無任何回饋。
- [Observation] 玉山/合歡/塔塔加/嘉明湖/蘭嶼/東莒 「星空／銀河」最佳時段 18:30–18:35 起 1 小時 — 11 月銀河核心約 19:00–19:30 沉沒，窗口僅後半有效；建議資料面覆核（未達 22:00–06:00 紅線）。
- [Observation] 美國卡片「明天 11/09」等相對詞採景點當地日期（台北 11/09 中午＝美西 11/08 晚），與頁首 GMT+8 時鐘並存時對不熟悉時區的使用者易誤讀 — 建議卡片相對日期旁加當地日期標示。

## Console / network

No failed resource loads (performance entries with status ≥400: none). Console capture unavailable in this harness — not asserted.

## Per-region sweep table (時段合理性掃描, sampled = all rendered cards)

| Region | Cards sampled | 22:00–06:00 / daylight-night violations | Unexplained cards |
|---|---|---|---|
| tw | 93 | 0 visible-light subjects in night hours (night subjects all in legitimate windows 20:00–23:00; 星空 18:30+ observed) | 抹茶山 (no reason/no window); 奎壁山、建功嶼 (資料不足 — has reason ✓) |
| jp | 63 | 0 (夜景 18:00–21:00 OK; 「已過民用光線」at noon flagged above as Minor) | 諏訪湖 (no verdict line at all); 知床ウトロ流氷、鳴門海峽漩渦 (資料不足 — both name what is missing ✓) |
| us (mainland) | ~60 | 大彎 21:00 daylight subject (Major); Bryce terrain word (Major) | 沃斯堡、冰川、大提頓、黃石、白沙、巨人柱、馬蹄灣、布萊斯、拱門、舊金山金門大橋等 — 有未符原因者 ✓；何塞・黎剎、阿爾基、煤氣廠、凱瑞、漢密爾頓、默特爾・愛德華茲無原因 ✗ |
| ak | ~40 (rendered under 美國 tab) | 0 | 布魯克斯瀑布 (bare 資料不足 ✗); 卡特邁、冰河灣、波蒂奇 (no reason ✗); Skagway/Valdez 等 12 卡「攝影題材條件尚未完成查證」✓ |
| hi | 7 (rendered under 美國 tab) | 0 | all carry 未符原因 ✓ |

## Verified OK

- Homepage cards render desktop + 390px; region country tabs (tw/jp/us) switch correctly; language switch en/ja re-renders cards and the open 攝影資訊 modal (weather modal is the exception above); ja copy natural (撮影に適した時間数), no simplified-han on ja cards.
- Modal vs card verdict consistency (Manhattan): card 06:00、17:05 / modal ✅ 符合 · 06:00、17:05 — consistent. Card → modal drill-down adds depth (conditions table with plain-language explanations).
- Next-window lines: spot-local date anchoring verified correct on multiple cards (明天 11/10 / 後天 11/11 / 大後天 11/12 all consistent with local dates); no past time shown as 'next' found on sampled cards (Manhattan modal self-contradiction above is the exception).
- Honest-access notes (opening hours, road work, 纜車 night restrictions, 不受理拍攝 notice) present and informative.

## CHALLENGER_INPUT (round 9 — jp region, 10 spots, exact on-screen card text zh-TW, 2026-11-09 12:00+ GMT+8)

1. jp-名古屋城 | 「📷 本日最佳題材：天守全景 符合時數 1 ⏱️ 最佳拍攝時段：16:15 ⏰ 一般開園 09:00–16:30；12/29–1/1 固定休園。特別活動可能延長開園，但夜間延長不視為全年常態。」
2. jp-函館山夜景 | 「📷 本日最佳題材：暮色至夜間雙灣城市景觀 符合時數 5 ⏱️ 最佳拍攝時段：18:00–21:00、23:00」
3. jp-彌彥山頂公園・Panorama Tower | 「📷 本日最佳題材：彌彥山頂公園・日本海夕日 符合時數 1 ⏱️ 最佳拍攝時段：17:00 ⏰ 彌彥山頂可由纜車、季節性彌彥山Skyline或步行路線到達，各路線限制不同；夜間纜車僅官方年度『夜景＆星空Cruise』指定日期運行，不可把一般晴朗夜晚視為可達。」
4. jp-濱名湖 | 「📷 本日最佳題材：弁天島海浜公園・濱名湖夕景 符合時數 1 ⏱️ 最佳拍攝時段：17:00」
5. jp-津別峠展望台（屈斜路湖雲海） | 「📅 本日無符合題材 未符 · 低雲淹得太高，把該有的雲海蓋成一片白」
6. jp-摩周湖 | 「📅 本日無符合題材 · 下一個符合時段：明天 11/10 06:00」
7. jp-東京鐵塔 | 「📅 本日無符合題材 · 下一個符合時段：明天 11/10 12:00 未符 · 山區下雨起霧，稜線整個被雨幕蓋住 ⏰ Main Deck 官方營業 09:00–23:00，最終入場 22:30」
8. jp-橫濱港未來21 | 「📅 本日無符合題材 · 下一個符合時段：明天 11/10 18:00 未符 · 雨下個不停，碼頭與水面灰成一片」
9. jp-神戶六甲山 | 「📅 本日無符合題材 · 下一個符合時段：明天 11/10 07:00 ⏰ 天覽台官方目前開放 07:10–21:00、無固定休息日」
10. jp-鳴門海峽漩渦 | 「📷 此題材的成立條件尚未定義，無法提供評估」

Challenger spot-id list: 名古屋城, 函館山夜景, 彌彥山頂公園・Panorama Tower, 濱名湖, 津別峠展望台（屈斜路湖雲海）, 摩周湖, 東京鐵塔, 橫濱港未來21, 神戶六甲山, 鳴門海峽漩渦
