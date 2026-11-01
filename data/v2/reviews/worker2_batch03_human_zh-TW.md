# ChaseLights V2 Worker 2 Batch 03 — 可審核繁中版

本輪五個景點完成證據盤點；其中 3 個 Opportunity 已轉為 schema v2.1 的 evidence_review 文件，尚未正式核准。

## 發布限制
- V2.1 schema 已在 main：`specs/v2/schema/opportunity-v2.1.schema.json`；仍須依最新 main 執行 Schema 驗證及正式審查。
- Camera/Subject 精確幾何、方位、仰角、距離與 Navigation GPS 均 unknown。
- 條件門檻依 2026-11-02 owner 裁決改採審查修訂值（provisional，未校準；tw-016/tw-036 為 2026-11-01 manager 修訂），unknown_policy=propagate_unknown；不得用未校準條件產生 favorable。原人審研究契約（threshold 全 null）見 git 歷史 34cb70f39 之前版本。區域封閉／步道限制獨立列為警告，不得充當 REQUIRED／BLOCKER 或改變天氣適合度；未知導航點不得生成路線。

## 2026-11-02 owner 裁決（覆寫本輪人審 gate）

owner（Richard）於 2026-11-02 裁決「這 6 個題材依照 Excel 內的條件」，覆寫 worker2 人審 gate：改採審查修訂條件（provisional，未校準）。下方各題材的條件清單已同步更新為現行 canonical 契約；原人審研究契約（threshold 全為 unknown 的研究版）見 git 歷史 34cb70f39 之前版本，可回滾查閱。

## tw-016-P01 鳶嘴山岩稜與遠山層次

從鳶嘴山合法步道的安全位置拍攝裸露岩稜與遠方山巒；精確機位、方位及距離尚未驗證。

Camera：只使用合法步道的安全位置；官方記載有攀岩與危崖。
安全：濕滑、強風或惡劣天候可能使暴露岩稜危險；不可為了取景跨越危險區。
Subject：鳶嘴山裸露岩稜及遠方山巒（ridge；geometry unknown）
View relation：line_of_sight；distance/azimuth/elevation unknown。
Navigation：needs_review；未核實抵達點。
Readiness：研究成熟度 R1（evidence_review），仍有 GEOMETRY_GAP 與 RESEARCH_GAP；尚未核准發布。即時可拍攝狀態須由獨立 EvaluationResult 評估，不能由研究成熟度推定。


### REQUIRED

- 2026-11-01 manager 依既有已審模板訂立，未校準。（threshold 0.6；GUIDANCE）
- 2026-11-01 manager 依既有已審模板訂立，未校準。（threshold [30, 60]；GUIDANCE）
- 2026-11-01 manager 依既有已審模板訂立，未校準。（threshold 0.2；GUIDANCE）

### QUALITY

- 2026-11-01 manager 依既有已審模板訂立，未校準。（threshold unknown；GUIDANCE）


### 進入警告（不影響攝影條件）
- 封閉、危險路段與未核實合法取景範圍僅作安全／進入提醒，不降低天氣攝影適合度。導航仍須核實抵達點。


## tw-026-P01 井仔腳瓦盤鹽田夕照

井仔腳瓦盤鹽田的格狀鹽池與夕照已有現地攝影證據；到場可依當時合法開放範圍自行構圖，但可拍攝區域邊界尚未獨立核實；原瞭望台另有整修封閉公告。

Camera：一般遊客可合法拍攝的區域邊界尚未獨立核實；請依當日公告與現場規定選擇安全構圖。原瞭望台公告預計封閉至2026-11-30，須再次查證。
安全：施工圍籬及管制區不可進入。
Subject：瓦盤鹽池與夕照天空（area；geometry unknown）
View relation：foreground_background；distance/azimuth/elevation unknown。
Navigation：needs_review；未核實抵達點。
Readiness：研究成熟度 R1（evidence_review），仍有 GEOMETRY_GAP 與 RESEARCH_GAP；尚未核准發布。即時可拍攝狀態須由獨立 EvaluationResult 評估，不能由研究成熟度推定。


### REQUIRED

- 2026-11-02 owner（Richard）裁決覆寫 worker2 人審 gate，改採審查修訂條件（provisional，未校準）；原人審研究契約見 git 歷史 34cb70f39 之前版本。（threshold unknown；GUIDANCE）
- 2026-11-02 owner（Richard）裁決覆寫 worker2 人審 gate，改採審查修訂條件（provisional，未校準）；原人審研究契約見 git 歷史 34cb70f39 之前版本。（threshold 55；GUIDANCE）
- 2026-11-02 owner（Richard）裁決覆寫 worker2 人審 gate，改採審查修訂條件（provisional，未校準）；原人審研究契約見 git 歷史 34cb70f39 之前版本。（threshold [20, 70]；GUIDANCE）
- 2026-11-02 owner（Richard）裁決覆寫 worker2 人審 gate，改採審查修訂條件（provisional，未校準）；原人審研究契約見 git 歷史 34cb70f39 之前版本。（threshold 0.3；GUIDANCE）
- 2026-11-02 owner（Richard）裁決覆寫 worker2 人審 gate，改採審查修訂條件（provisional，未校準）；原人審研究契約見 git 歷史 34cb70f39 之前版本。（threshold 0.6；GUIDANCE）


### 進入警告（不影響攝影條件）
- 封閉、危險路段與未核實合法取景範圍僅作安全／進入提醒，不降低天氣攝影適合度。導航仍須核實抵達點。


## tw-026-P02 井仔腳鹽田晚霞

以鹽田格狀地景搭配日落前後的彩霞；彩霞是否出現須以實際天空狀態判斷。

Camera：僅可從當日確實開放、允許一般遊客拍攝且安全的位置取景；具體公共區域及邊界尚未獨立核實，須依當日公告與現場管制確認，無法確認時不可使用該構圖。原瞭望台封閉期間不得進入；替代平台的開放不證明其他區域開放。
安全：遵守施工及公共區域限制。
研究限制：上述「開放的鹽田公共區」是條件性取景限制，並非已獨立核實某個公共區的實際開放狀態或邊界；到場須查當日公告與現場管制，若無法確認合法且安全的取景位置，該構圖不可使用。
Subject：鹽田上空晚霞與格狀鹽池（dynamic_sky；geometry unknown）
View relation：foreground_background；distance/azimuth/elevation unknown。
Navigation：needs_review；未核實抵達點。
Readiness：研究成熟度 R1（evidence_review），仍有 GEOMETRY_GAP 與 RESEARCH_GAP；尚未核准發布。即時可拍攝狀態須由獨立 EvaluationResult 評估，不能由研究成熟度推定。


### REQUIRED

- 2026-11-02 owner（Richard）裁決覆寫 worker2 人審 gate，改採審查修訂條件（provisional，未校準）；原人審研究契約見 git 歷史 34cb70f39 之前版本。（threshold unknown；GUIDANCE）
- 2026-11-02 owner（Richard）裁決覆寫 worker2 人審 gate，改採審查修訂條件（provisional，未校準）；原人審研究契約見 git 歷史 34cb70f39 之前版本。（threshold 55；GUIDANCE）
- 2026-11-02 owner（Richard）裁決覆寫 worker2 人審 gate，改採審查修訂條件（provisional，未校準）；原人審研究契約見 git 歷史 34cb70f39 之前版本。（threshold [20, 70]；GUIDANCE）
- 2026-11-02 owner（Richard）裁決覆寫 worker2 人審 gate，改採審查修訂條件（provisional，未校準）；原人審研究契約見 git 歷史 34cb70f39 之前版本。（threshold 0.3；GUIDANCE）
- 2026-11-02 owner（Richard）裁決覆寫 worker2 人審 gate，改採審查修訂條件（provisional，未校準）；原人審研究契約見 git 歷史 34cb70f39 之前版本。（threshold 0.6；GUIDANCE）


### 進入警告（不影響攝影條件）
- 封閉、危險路段與未核實合法取景範圍僅作安全／進入提醒，不降低天氣攝影適合度。導航仍須核實抵達點。


## 暫緩候選

- tw-021：Tea garden camera access/permission and exact sunrise geometry unverified
- tw-026：P03 water/reflection conditions still pending canonical translation; temporary closure must be refreshed
- tw-031：P01 official mountain-view evidence, but trail status source conflict; mist P02 lacks independent formation proof
- tw-036：Sunrise public camera, Milky Way geometry, and northward cloud subject not adequately verified
