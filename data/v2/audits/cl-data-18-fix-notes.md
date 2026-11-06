# CL-DATA-18 人審閘門改制：AI 查證取代 — 執行記錄（2026-11-06）

Owner 裁決（2026-11-06）：worker2 batch gate 的人審前置取消——AI 查證（來源 URL＋查證日期）
齊備即可修改人審/byte-pin 釘死的幾何/時段欄位；閘門本身保留（防無來源竄改），
admission 條件改為 provenance 齊備，閘門測試重新錨定到新狀態。

## 補入（AI web 複驗後填入，每筆 derivation_method + provenance.reviewed_by 記來源＋日期＋owner 裁決）

| opportunity | 補入 | 來源（複驗日 2026-11-06） | 一致性 |
|---|---|---|---|
| tw-034-P02 崇德清水斷崖山海遠眺 | camera geojson 121.661332,24.191966 + nav lat/lon | 同 place 兄弟 tw-034-P01 已驗證 camera 點；web 複驗 yingtingshih.com/2021-12-21-4272/（崇德休憩區 24°11′31.2″N 121°39′40.8″E = 24.1920,121.6613） | 完全一致 |
| tw-036-P01 七星潭礫石海岸日出 | 121.62717,24.031426 | 兄弟 tw-036-P02；en.wikipedia.org/wiki/Qixingtan_Beach 24°01′58.4″N 121°37′40.6″E（=24.03289,121.62794，同月牙灘 ~0.16km） | 一致 |
| tw-082-P01 鯉魚潭湖光與水面倒影 | 121.50803,23.93493 | 兄弟 tw-082-P02；官方 media.taiwan.net.tw Attraction_A15010300H_000001 花東縱谷風管處 23.93501,121.50778（~0.09km） | 一致 |
| jp-010-P01 河口湖大石公園 | 138.7461483,35.5230652 | 兄弟 jp-010-P02；山梨縣觀光官方 yamanashi-kankou.jp p_8334（35.5229,138.7455；webcam GPS 35.52366,138.746889 一致） | 一致 |
| us-071-P01 Kerry Park 西雅圖天際線暮色 | -122.35993,47.62941 | 兄弟 us-071-P02；en.wikipedia.org/wiki/Kerry_Park_(Seattle) 47°37′46″N 122°21′36″W（=47.62944,-122.36000） | 一致 |
| tw-026-P01 井仔腳瓦盤鹽田夕照 / tw-026-P02 井仔腳鹽田晚霞 | 120.10757,23.25883 | 兄弟 tw-026-P03；官方 tad.gov.tw A12-00023 交通部觀光署 120.10756/23.258830（~1m） | 一致 |
| us-057-P01 北極圈標誌地標照 | light_window（civil，太陽仰角 > −6°，CL-DATA-11 同源定義；condition_tier MAIN，role REQUIRED，threshold_source computed） | CL-DATA-12 group F 同批定義（us-063-P01 模板）；緯度 66.556°N 北極圈上，極夜/白夜語義正確化。2026-11-06 人審閘門改制後由 AI 直接補入 | — |

## 誠實保留 unknown（查不到權威源）

- tw-016-P01：camera geometry（鳶嘴山岩稜安全機位——無權威單點來源）、nav 抵達點。
- tw-086-P01/P02/P03：nav「實際抵達點未核實」——八里側眺望點之抵達路線無獨立權威來源
  （camera 座標維持 owner-provided provisional）。
- 全數 records 的 targets/0/geometry/status=unknown（subject 幾何如稜線/湖面範面範圍）維持 unknown。

## 同步改動

- worker2_batch04_evidence.json：+5 條 AI 查證來源（b04c-tw034/tw036/tw082/jp010/us071，URL＋date）；
  camera claim audit_status PARTIAL→OK（5 筆）；review.human_geo PENDING→AI_VERIFIED（改制註記）。
- worker2_batch03_evidence.json：+1 條 e026f（tad.gov.tw 官方座標）。
- crosswalk jsonl：6 檔逐 cell 重錨（geometry-status derived、verification representative、
  nav lat/lon/confidence low、gaps/1 移除——GEOMETRY_GAP 已解）。
- fixtures/worker2：tw-026-P01/P02 + preview 重新釘（blob/sha256）；core-v2 tw-026-P01 fixture 同步。
- 閘門測試重新錨定：test_worker2_batch04.py、test_worker2_batch03.py、
  cl-data-12-contract-fixes.test.mjs（us-057 反向釘→正向釘）、worker2-canonical-records.test.mjs、
  ops/v2/postmerge_verify.py（改制語義：provenance 齊備 admission + AI_VERIFIED signoff）。
- 新增改制測試：data/v2/tests/test_cl_data_18_ai_verification_gate.py。

## 評估重生成

geometry/座標/光窗補入不改變任何評分欄位（research-only records 本就 NO_VERIFIED_GEOMETRY
skipped；us-057 light_window 為新 condition）——交排程 CI 重生成 --only-place-id
(us-057) 即可；本地不跑整批 evaluate_batch。
