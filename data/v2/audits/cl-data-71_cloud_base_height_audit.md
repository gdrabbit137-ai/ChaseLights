# CL-DATA-71 高度敏感題材契約審計（雲底高度窗 / cloud_base_height）

工作樹：`task/CL-DATA-71`（from origin/main 7627967bc）。owner 發現：墨硯山琉璃光契約無雲海高度條件，晴天無雲也判 ✓；而凝結高度（LCL，2m 溫度/露點推算）已在管線。

## 條件定義

- metric：`cloud_base_height`（unit m），照現行 condition contract 格式
  （id/metric/operator/threshold/role/domain/evaluation_mode/capability/
  unknown_policy/claim_refs/model_binding/threshold_source/condition_tier/
  calibration_status/rationale_i18n/notes_i18n）。
- 評估值＝既有 LCL 代理 cell（`lcl_height_m_agl`：batch adapter 由觀點格點 2m
  溫度/露點以 125·(T−Td) 推算，相對觀點格點地面，單位 m）。評估器由 batch runner
  把觀點海拔綁到條件上（`camera_contexts[].altitude_m` web-verified 優先，
  否則 V1 spot catalog DEM `api_elevation`）。
- 觀點相對語義：
  - catalog 有記載帶 → `between [lo, hi]`，`threshold_source=evidence_review`
    （帶值照 `data/v2/audits/subject-lists/liuli-cloudheights.json` 記載）。
  - 無記載 → 派生規則「觀點海拔 − 200 m」→ `lt (elev−200)`，
    `threshold_source=computed`（沿 CL-DATA-12 雲海族既行慣例：jp-037-P01 /
    tw-001-P02 / tw-020-P03 均為 `lcl_height_m_agl lt 觀點−200`）。
- 觀點海拔缺落時誠實 `UNKNOWN`（VIEWPOINT_ELEVATION_UNKNOWN），不虛構判決。

## 審計範圍

掃描全部 705 份 opportunity 契約之 zh-TW 名稱＋描述，命中高度敏感語義
（琉璃光/琉璃/雲海/雲瀑/霧海 及 頂石棹/金龍山/墨硯山/大屯山/雲洞山莊/隙頂）
共 73 份；其中 40 份已有雲底高度條件（`lcl_height_m_agl`，多为 lt 觀點−200），
33 份缺——逐份以「主題語義是否以高度窗為決勝條件」判定（owner 量身定做準則）。

## 補上條件者（13 份）

| oid | 主題 | 閾值 | threshold_source | 觀點海拔來源 |
|---|---|---|---|---|
| tw-128-P01 | 墨硯山苗栗琉璃光 | between [50,120] | evidence_review（catalog 帶） | camera altitude_m 157 |
| tw-145-P01 | 東華聖宮琉璃光夜景 | lt 105 | computed（305−200） | catalog DEM 305 |
| tw-148-P01 | 中寮山蓮花亭琉璃夜景 | lt 201 | computed（401−200） | catalog DEM 401 |
| tw-163-P01 | 半天岩嘉義市區琉璃夜景 | lt 218 | computed（418−200） | catalog DEM 418 |
| tw-179-P01 | 碧山巖台北盆地琉璃夜景 | lt 53 | computed（253−200） | catalog DEM 253 |
| tw-035-P06 | 六十石山下方縱谷雲海 | lt 744 | computed（944−200） | catalog DEM 944 |
| tw-043-P02 | 奇萊主稜夕照雲海 | lt 3360 | computed（3560−200） | catalog DEM 3560 |
| tw-047-P01 | 喜多麗秋冬雲海 | lt 2892 | computed（3092−200） | catalog curated 3092 |
| tw-047-P02 | 喜多麗夕照雲海 | lt 2892 | computed（3092−200） | catalog curated 3092 |
| tw-049-P03 | 桃山雲海 | lt 3125 | computed（3325−200） | catalog DEM 3325 |
| jp-037-P02 | トマム朝景（雲海ゴンドラ） | lt 888 | computed（1088−200） | camera altitude_m 1088 |
| us-087-P01 | Hurricane Ridge 山岳層次／雲海 | lt 1390 | computed（1590−200） | catalog DEM 1590 |
| us-113-P01 | 哈雷阿卡拉山頂雲海日出 | lt 2855 | computed（3055−200） | camera altitude_m 3055 |

## 審計排除（缺高度條件但主題語義不以其為決勝條件，維持原契約）

- 兄弟契約已分列雲海/琉璃語義、本契約為另一主體：tw-001-P01/P03、tw-014-P01、
  tw-020-P01/P04、tw-022-P01、tw-023-P01、tw-125-P02、tw-130-P02、tw-131-P02、
  tw-134-P02、tw-181-P02、tw-182-P02、tw-196-P02、tw-098-P02。
  （例：tw-130-P02 宇老夜景官方語「晴朗的夜晚…觀賞夜景」——晴天判 ✓ 正確。）
- 純展望/夕照/星空/花楓季主體（雲海僅描述附帶提及）：jp-065-P01、tw-120-P01、
  tw-140-P02、tw-169-P01、tw-175-P02、tw-180-P01、tw-184-P01。

## 驗證

- `packages/core-v2/tests/test_cl_data_71_cloud_base_height.py`（16 cases）：
  墨硯山晴天無雲夜（LCL 代理 549 m）→ FAIL → 小時桶 UNFAVORABLE；帶內
  （80 m）→ PASS；帶緣 49/50/120/121；13 份契約逐一釘審計值；誠實路徑
  （無觀點海拔／無 LCL cell／畸形 threshold）全部 UNKNOWN。
- 契約 schema：`specs/v2/tests/validate_contract.py` 對 13 份修改檔全 PASS。
