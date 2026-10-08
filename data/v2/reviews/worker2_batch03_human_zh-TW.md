# ChaseLights V2 Worker 2 Batch 03 — 可審核繁中版

本輪五個景點完成證據盤點；其中 3 個 Opportunity 已轉為 schema v2.1 的 evidence_review 文件，尚未正式核准。

## 發布限制
- Worker 1 的 schema v2.1 位於 Draft PR #428，尚未進 main。
- Camera/Subject 精確幾何、方位、仰角、距離與 Navigation GPS 均 unknown。
- 所有 condition threshold 為 null，unknown_policy=propagate_unknown；不得用未知條件產生 favorable。

## tw-016-P01 鳶嘴山岩稜與遠山層次

從鳶嘴山合法步道的安全位置拍攝裸露岩稜與遠方山巒；精確機位、方位及距離尚未驗證。

Camera：只使用合法步道的安全位置；官方記載有攀岩與危崖。
安全：濕滑、強風或惡劣天候可能使暴露岩稜危險；不可為了取景跨越危險區。
Subject：鳶嘴山裸露岩稜及遠方山巒（ridge；geometry unknown）
View relation：line_of_sight；distance/azimuth/elevation unknown。
Navigation：needs_review；未核實抵達點。
Readiness：R1 / GUIDANCE_ONLY。

### REQUIRED
- 合法步道及安全立足點必須可用；現場狀態需確認。（threshold unknown；VERIFY）
- 岩稜與遠山需可辨；未設定公里能見度門檻。（threshold unknown；GUIDANCE）

### BLOCKER
- 暴露岩稜若因濕滑或惡劣天候無法安全通行，停止推薦。（threshold unknown；VERIFY）

### QUALITY
- 遠山輪廓與空氣透明度越清楚，層次越完整；無量化門檻。（threshold unknown；GUIDANCE）

## tw-026-P01 井仔腳瓦盤鹽田夕照

從開放的鹽田公共區拍攝格狀鹽池與夕照；2026年9月起整修的原瞭望台不可當作開放機位。

Camera：只用開放公共區；原瞭望台預計封閉至2026-11-30，應核對最新公告。
安全：施工圍籬及管制區不可進入。
Subject：瓦盤鹽池與夕照天空（area；geometry unknown）
View relation：foreground_background；distance/azimuth/elevation unknown。
Navigation：needs_review；未核實抵達點。
Readiness：R1 / GUIDANCE_ONLY。

### REQUIRED
- 鹽田公共攝影區須當下開放；原瞭望台封閉不等於整個景區封閉。（threshold unknown；VERIFY）
- 夕照需實際照亮鹽田構圖；未推定太陽方位或固定時刻。（threshold unknown；GUIDANCE）

### BLOCKER
- 若取景需要進入正在封閉的原瞭望台，該機位不可使用。（threshold unknown；VERIFY）

### QUALITY
- 適當的晚霞雲層可增加色彩，但不保證每次出現。（threshold unknown；GUIDANCE）

## tw-026-P02 井仔腳鹽田晚霞

以鹽田格狀地景搭配日落前後的彩霞；彩霞是否出現須以實際天空狀態判斷。

Camera：開放的鹽田公共區；施工瞭望台不使用。
安全：遵守施工及公共區域限制。
Subject：鹽田上空晚霞與格狀鹽池（dynamic_sky；geometry unknown）
View relation：foreground_background；distance/azimuth/elevation unknown。
Navigation：needs_review；未核實抵達點。
Readiness：R1 / GUIDANCE_ONLY。

### REQUIRED
- 必須從當下開放的公共區攝影。（threshold unknown；VERIFY）
- 天空需實際出現可辨晚霞；不能以日期或一般雲量直接保證。（threshold unknown；VERIFY）

### BLOCKER
- 若構圖必須站在封閉瞭望台，該構圖不可用。（threshold unknown；VERIFY）

### QUALITY
- 鹽池幾何線條與彩霞同框可增加地方辨識度。（threshold unknown；GUIDANCE）

## 暫緩候選

- tw-021：Tea garden camera access/permission and exact sunrise geometry unverified
- tw-026：P03 water/reflection conditions still pending canonical translation; temporary closure must be refreshed
- tw-031：P01 official mountain-view evidence, but trail status source conflict; mist P02 lacks independent formation proof
- tw-036：Sunrise public camera, Milky Way geometry, and northward cloud subject not adequately verified
