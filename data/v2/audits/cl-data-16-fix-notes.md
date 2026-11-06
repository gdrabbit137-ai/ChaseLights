# CL-DATA-16 事實查證修正第一波 — 執行記錄（2026-11-06）

## 已修正（本分支 task/CL-DATA-16）

### 海拔（批次 1，9 筆）
| place | 舊 | 新 | 來源（複驗日 2026-11-06） |
|---|---|---|---|
| tw-004 不厭亭 | 505 | 531 | smiletaiwan.cw.com.tw/article/1216 + myjourney.tw/buyen-pavilion |
| tw-008 觀音山硬漢嶺 | 361 | 616 | northguan-nsa.gov.tw（北觀處官方） |
| tw-013 火炎山 | 483 | 602 | forest.gov.tw/0007960（林業署官方；報告區間 596–614 內取官方值） |
| tw-016 鳶嘴山 | 2120 | 2180 | recreation.forest.gov.tw/Trail/RT?tr_id=060 |
| tw-020 金龍山 | 666 | 820 | media.taiwan.net.tw Attraction_A15010600H_000094（日月潭風管處） |
| tw-021 武界部落 | 863 | 800 | gofunit.com / chang-you.com.tw（通行引用 760–820，取約 800） |
| tw-025 二寮 | 156 | 185 | siraya-nsa.gov.tw detail/30 + taiwanviptravel.com |
| tw-029 鵝鑾鼻燈塔 | 39 | 56.4（焦點海拔語義：航港局「燈高」＝高潮面至燈火中心，非地面海拔） | motcmpb.gov.tw 燈塔資訊。main 上無 tw-029 V2 opportunity 檔；修正落在 V1 路徑 regions.py ELEVATION_OVERRIDES |
| tw-030 屏東關山 | 128 | 152 | dbnsa.gov.tw/attraction/AttractionPage?a=191（大鵬灣風管處） |

V2 侧落點：camera_contexts.altitude_m（CL-DATA-14 慣例）＋ derivation_method 溯源。
LCL 門檻（owner 公式＝海拔−200）重算：tw-004-P03 305→331、tw-008-P03 161→416、
tw-020-P02 466→620、tw-020-P03 466→620（琉璃光）、tw-021-P02 663→600；
rationale_i18n 三語同步＋notes_i18n CL-DATA-16 標記。
V1 侧：regions.py ELEVATION_OVERRIDES 新增 9 筆。

### 座標
| place | 舊 | 新 | 來源 |
|---|---|---|---|
| us-065-P01 Glen Alps | 61.10489,-149.68461 | 61.107222,-149.71472 | alaska.org/detail/glen-alps-overlook |
| tw-052-P01 崗山之眼 | 120.3497,22.8229 | 120.33472,22.81278 | zh.wikipedia 崗山之眼 + pixnet 獨立實測一致（複驗值與報告所引 120.356,22.825 不一致，以複驗為準） |
| tw-062-P01 得月樓 | 24.40971,118.29849 | 24.40583,118.30056 | zh.wikipedia 前水頭得月樓及黃輝煌洋樓 |

### DRIFT 候補複驗結果（全數 VERIFIED，未改）
- tw-042 雪山北峰：維基 24.41474,121.2404 ≈ repo（偏差 ~0.06km）
- tw-043 奇萊主山：維基 24°5′9.6″N 121°19′22.8″E ＝ repo
- tw-044 南湖主峰：太管處官方 24°21′43″N 121°26′22″E ≈ repo（~0.05km）
- tw-049 桃山：維基 24.43263,121.3049 ≈ repo；tw-050 品田山：維基 24.4282,121.2668 ＝ repo
- tw-060 雙心石滬：觀光局/維基 119.4469,23.2203 ＝ repo
- tw-071 花瓶岩：**報告 CONFLICT 判定翻案** — 大鵬灣風管處官方頁座標 120.38076,22.35566 與 repo 完全一致，維持原值。

### tw-086 名稱校正
「淡水大橋」（owner 口語）→ 官方「淡江大橋 / Danjiang Bridge」，zh/en/ja 三語（原 en 誤作 Guandu Bridge）。
來源：cna.com.tw 2026-05-12 通車報導（官方名稱淡江大橋）。

## 未執行＋原因（需 review-layer 裁決）
- tw-034-P02 / tw-036-P01 / tw-082-P01 座標缺口：三筆為 worker2 batch04 人審 gate 釘死
  記錄（camera geometry.status=unknown、geojson=None、readiness gaps=[GEOMETRY_GAP,RESEARCH_GAP]、
  crosswalk jsonl 36 row 逐 cell 釘值）。補座標＝改寫人審契約與 crosswalk，屬 owner-gated
  override（manager protocol: Human-review gates）。已 web/sibling 查得座標
  （tw-034≈121.661332,24.191966；tw-036≈121.62717,24.031426；tw-082≈121.50803,23.93493，
  皆為同 place 兄弟檔已驗證 camera 點），建議另開 owner 裁決票做 gate re-anchor 後補入。
- tw-040-P04（報告 MISMATCH #1）：不在本票清單，未動。
- 受影響景點評估重生成：evaluate_batch --only-place-id 會以單一 place 覆寫整份
  evaluations bundle，交排程 CI 重生成（LCL/座標變更影響 tw-004/008/020/021 判讀）。
