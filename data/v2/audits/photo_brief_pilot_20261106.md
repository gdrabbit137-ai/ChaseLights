# 攝影師委託書試點稽查（photo_brief_pilot_20261106）

- 日期：2026-11-06（UTC+8）／分支：task/CL-PHOTO-02（自 origin/main a0633b007 建立，獨立 worktree）
- 範圍：tw-001/003/005/010/011/019/024/027/035/040/054/062/076/086、jp-010/022、us-001/024/059/083 共 20 景點之全部機會（65 筆）。
- 方法：逐機會寫攝影師委託書（主體／成立需求／光向 view_azimuth×太陽方位／條件服務映射／缺口），對照 condition_contract（schema 2.1.0）與 genre 模板（sunset/cloud_sea/mountain_view 等，metric-vocabulary 0.8）。
- 本報告為重跑（前次回報遭 log 截斷），結論以本檔為準。

## 漏洞分類統計

| 分類 | 筆數 | 說明 |
|---|---|---|
| LCL_ELEV_ERR | 1 | LCL 門檻引用錯誤觀點高度 |
| THRESH_NULL | 1 | 條件 threshold 欄位為 null |
| BINDING_DATASET | 1 | model_binding 資料集寫錯 |
| PROXY_COARSE | 1 | 裂雲窗以雲量總量代理，語義矛盾 |
| SNOW_ABSENT | 3 | 雪覆/冰川主體無雪況代理條件 |
| SEASON_ABSENT | 2 | 主體含季節成分但無 seasonal_state |
| AZIMUTH_SEASON | 4 | 光向季變未編碼（扇形 sector 全年固定） |
| LCL_DEM | 3 | LCL 門檻源自觀點高度但無 DEM 溯源、altitude_m=null |
| AZIMUTH_NULL_ONLY | 46 | 除 view_azimuth null 通案外無契約級漏洞 |
| GENRE_FIT | 1 | 模板與主體不匹配（已知妥協） |

> 65 機會全部 view_azimuth=null（observation_relations 65/65），此為通案另計（見光向資料結論），不重複計入上表。

## 委託書逐機會

### jp-010-P01　河口湖大石公園季節植栽與富士山
- genre：seasonal_plant（template_version seasonal_plant-v0.1；recommendation_policy_version=None；research_level=R1，gaps=GEOMETRY_GAP,RESEARCH_GAP）
- 主體：河口湖大石公園季節植栽與富士山；claims=5（audit_status=['OK', 'PARTIAL', 'UNKNOWN', 'PARTIAL', 'PARTIAL']）
- 成立需求（REQUIRED 判據）：C-jp-010-P01-01 seasonal_state eq window_open [REQUIRED/MAIN|provisional]; C-jp-010-P01-02 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-jp-010-P01-03 wind_speed_10m lt 5 m/s [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-jp-010-P01-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:gfs_0p25', '未綁定']；欄位/代理：['field:precipitation_rate_mm_h', 'field:wind_speed_10m_m_s', 'seasonal_state']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；季節窗（seasonal-calendar 例年窗/實況窗對拍）、precip、wind 判據齊；光向缺 view_azimuth 為通案。
- 判定：✅ 通過（備註）
- 修法建議：季節窗（seasonal-calendar 例年窗/實況窗對拍）、precip、wind 判據齊；光向缺 view_azimuth 為通案。

### jp-010-P02　大石公園・逆さ富士
- genre：reflection（template_version reflection-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：大石公園・逆さ富士；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-jp-010-P02-01 seasonal_state eq window_open [REQUIRED/MAIN|provisional]; C-jp-010-P02-02 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-jp-010-P02-03 wind_speed_10m lte 2 m/s [REQUIRED/MAIN|provisional]; C-jp-010-P02-04 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]; C-jp-010-P02-05 cloud_cover_mid between [30, 60] % [QUALITY/BONUS|provisional]; C-jp-010-P02-07 sunset_window none None [QUALITY/MODIFIER|provisional]; C-jp-010-P02-WS1 water_surface_state none None [REQUIRED/MAIN|None]
- 光向：view_azimuth=null（VR-jp-010-P02-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_mid_percent', 'field:precipitation_rate_mm_h', 'field:wind_speed_10m_m_s', 'seasonal_state', 'sunset_window']…
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；reflection 判據含 wind ≤2 m/s＋AOD＋中雲染料，正確；water_surface_state 宣告型成立。光向通案缺 view_azimuth。
- 判定：✅ 通過（備註）
- 修法建議：reflection 判據含 wind ≤2 m/s＋AOD＋中雲染料，正確；water_surface_state 宣告型成立。光向通案缺 view_azimuth。

### jp-022-P01　彌彥山頂公園・越後平野與日本海全景
- genre：mountain_view（template_version mountain_view-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：彌彥山頂公園・越後平野與日本海全景；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-jp-022-P01-01 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]; C-jp-022-P01-02 cloud_cover_mid between [30, 60] % [REQUIRED/MAIN|provisional]; C-jp-022-P01-03 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-jp-022-P01-04 sunset_window none None [QUALITY/MODIFIER|provisional]
- 光向：view_azimuth=null（VR-jp-022-P01-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_mid_percent', 'field:precipitation_rate_mm_h', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### jp-022-P02　彌彥山頂公園・日本海夕日
- genre：sunset（template_version sunset-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：彌彥山頂公園・日本海夕日；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-jp-022-P02-01 sunset_window none None [REQUIRED/MAIN|provisional]; C-jp-022-P02-02 cloud_cover_low lte 55 % [REQUIRED/MAIN|provisional]; C-jp-022-P02-03 cloud_cover_mid_and_high between [20, 70] % [REQUIRED/MODIFIER|provisional]; C-jp-022-P02-04 precipitation lt 0.3 mm/h [REQUIRED/MAIN|provisional]; C-jp-022-P02-05 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-jp-022-P02-01，geometry_mode=unknown，elevation_deg=None）×太陽方位：日落方位 300.2°(夏至)→269.4°(分)→239.8°(冬至)——sun_azimuth_sector 格點帶無法以 view_azimuth 定心，契約目前無法定義。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_low_percent', 'field:cloud_cover_mid_percent+cloud_cover_high_percent', 'field:precipitation_rate_mm_h', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### jp-022-P03　彌彥山夜景＆星空Cruise・越後平野夜景
- genre：night_sky（template_version night_sky-v0.4；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：彌彥山夜景＆星空Cruise・越後平野夜景；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-jp-022-P03-01 astronomical_darkness none None [REQUIRED/MAIN|provisional]; C-jp-022-P03-02 moon_illumination_fraction lte 0.5 [REQUIRED/MAIN|provisional]; C-jp-022-P03-03 cloud_cover_total lte 20 % [REQUIRED/MAIN|provisional]; C-jp-022-P03-04 aod_550nm lte 0.3 [REQUIRED/MAIN|provisional]; C-jp-022-P03-05 galactic_core_altitude gte 10 ° [REQUIRED/MAIN|provisional]; C-jp-022-P03-06 moon_altitude lt 0 ° [REQUIRED/MAIN|provisional]; C-jp-022-P03-07 moon_target_separation_deg gte 40 ° [REQUIRED/MAIN|provisional]; C-jp-022-P03-08 moon_illuminance_proxy lte 0.15 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-jp-022-P03-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['astronomical_darkness', 'field:aerosol_optical_depth_550nm', 'field:cloud_cover_total_percent', 'galactic_core_altitude', 'moon_altitude', 'moon_illuminance_proxy']…
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-001-P01　大屯山夕照山稜＋秋芒
- genre：sunset（template_version sunset-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：大屯山夕照山稜＋秋芒；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-001-P01-01 sunset_window none None [REQUIRED/MAIN|provisional]; C-tw-001-P01-02 cloud_cover_low lte 55 % [REQUIRED/MAIN|provisional]; C-tw-001-P01-03 cloud_cover_mid_and_high between [20, 70] % [REQUIRED/MODIFIER|provisional]; C-tw-001-P01-04 precipitation lt 0.3 mm/h [REQUIRED/MAIN|provisional]; C-tw-001-P01-05 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-001-P01-01，geometry_mode=unknown，elevation_deg=None）×太陽方位：日落方位 296.1°(夏至)→269.5°(分)→244.0°(冬至)——sun_azimuth_sector 格點帶無法以 view_azimuth 定心，契約目前無法定義。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_low_percent', 'field:cloud_cover_mid_percent+cloud_cover_high_percent', 'field:precipitation_rate_mm_h', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；主體含「秋芒」季節成分（秋季芒草期），但契約只有 sunset 判據，無 seasonal_state 條件——「一般夕照」與「秋芒」兩種成立語義被合併。建議補 seasonal_state window_open（10–11 月，propagate_unknown）並以 condition_tier 分層。
- 判定：⚠ 季節條件缺失
- 修法建議：主體含「秋芒」季節成分（秋季芒草期），但契約只有 sunset 判據，無 seasonal_state 條件——「一般夕照」與「秋芒」兩種成立語義被合併。建議補 seasonal_state window_open（10–11 月，propagate_unknown）並以 condition_tier 分層。

### tw-001-P02　大屯山台北盆地下方雲海
- genre：cloud_sea（template_version cloud_sea-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：大屯山台北盆地下方雲海；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-001-P02-01 relative_humidity_925hpa gte 85 % [REQUIRED/MAIN|provisional]; C-tw-001-P02-02 relative_humidity_850hpa gte 55 % [REQUIRED/MAIN|provisional]; C-tw-001-P02-03 lcl_height_m_agl lt 882 m [REQUIRED/MAIN|provisional]; C-tw-001-P02-04 cloud_cover_low gte 60 % [REQUIRED/MAIN|provisional]; C-tw-001-P02-05 aod_550nm lte 0.4 [REQUIRED/MAIN|provisional]; C-tw-001-P02-06 visibility gte 1 km [REQUIRED/MAIN|provisional]; C-tw-001-P02-07 temperature_delta_850_925_c gte 0.0 °C [QUALITY/MODIFIER|provisional]; C-tw-001-P02-08 wind_speed_850hpa lt 12.0 m/s [QUALITY/MODIFIER|provisional]; C-tw-001-P02-LW1 light_window none None [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-001-P02-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['未綁定']；欄位/代理：['aod_550nm', 'cloud_cover_low', 'lcl_height_m_agl', 'light_window', 'relative_humidity_850hpa', 'relative_humidity_925hpa']…
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；LCL 門檻 882 m 由「觀點 1,082 m − 200 m」推出，但 camera_contexts.altitude_m=null，1,082 m 的 DEM 溯源（資料集/版本/不確定度）未記錄；threshold_source=computed 無法複算。
- 判定：⚠ LCL DEM 溯源
- 修法建議：LCL 門檻 882 m 由「觀點 1,082 m − 200 m」推出，但 camera_contexts.altitude_m=null，1,082 m 的 DEM 溯源（資料集/版本/不確定度）未記錄；threshold_source=computed 無法複算。

### tw-001-P03　大屯山俯瞰台北盆地暮色／夜景
- genre：blue_hour_city（template_version blue_hour_city-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：大屯山俯瞰台北盆地暮色／夜景；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-001-P03-01 blue_hour_window none None [REQUIRED/MAIN|provisional]; C-tw-001-P03-02 cloud_cover_total lte 70 % [REQUIRED/MAIN|provisional]; C-tw-001-P03-03 aod_550nm lte 0.5 [REQUIRED/MAIN|provisional]; C-tw-001-P03-04 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-001-P03-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['blue_hour_window', 'field:aerosol_optical_depth_550nm', 'field:cloud_cover_total_percent', 'field:precipitation_rate_mm_h']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-003-P01　淡水河口夕照＋情人橋／港景
- genre：sunset（template_version sunset-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：淡水河口夕照＋情人橋／港景；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-003-P01-01 sunset_window none None [REQUIRED/MAIN|provisional]; C-tw-003-P01-02 cloud_cover_low lte 55 % [REQUIRED/MAIN|provisional]; C-tw-003-P01-03 cloud_cover_mid_and_high between [20, 70] % [REQUIRED/MODIFIER|provisional]; C-tw-003-P01-04 precipitation lt 0.3 mm/h [REQUIRED/MAIN|provisional]; C-tw-003-P01-05 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-003-P01-01，geometry_mode=unknown，elevation_deg=None）×太陽方位：日落方位 296.1°(夏至)→269.5°(分)→243.9°(冬至)——sun_azimuth_sector 格點帶無法以 view_azimuth 定心，契約目前無法定義。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_low_percent', 'field:cloud_cover_mid_percent+cloud_cover_high_percent', 'field:precipitation_rate_mm_h', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；淡水河口夕照：河口/海面剪影對位隨季節大變——日落方位冬約 244°、夏約 296°（52° 擺幅），僅秋冬太陽才落向河口；「太陽方位扇形」若以全年固定扇形取格點會取錯方向。建議 view_azimuth 落實後以月別太陽方位定心 sector 並做季節標註。
- 判定：⚠ 光向季變
- 修法建議：淡水河口夕照：河口/海面剪影對位隨季節大變——日落方位冬約 244°、夏約 296°（52° 擺幅），僅秋冬太陽才落向河口；「太陽方位扇形」若以全年固定扇形取格點會取錯方向。建議 view_azimuth 落實後以月別太陽方位定心 sector 並做季節標註。

### tw-003-P02　情人橋暮色光雕＋港灣
- genre：blue_hour_city（template_version blue_hour_city-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：情人橋暮色光雕＋港灣；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-003-P02-01 blue_hour_window none None [REQUIRED/MAIN|provisional]; C-tw-003-P02-02 cloud_cover_total lte 70 % [REQUIRED/MAIN|provisional]; C-tw-003-P02-03 aod_550nm lte 0.5 [REQUIRED/MAIN|provisional]; C-tw-003-P02-04 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-003-P02-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['blue_hour_window', 'field:aerosol_optical_depth_550nm', 'field:cloud_cover_total_percent', 'field:precipitation_rate_mm_h']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-003-P03　情人橋夜景＋水面倒影
- genre：city_night（template_version city_night-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：情人橋夜景＋水面倒影；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-003-P03-01 cloud_cover_total lte 30 % [REQUIRED/MAIN|provisional]; C-tw-003-P03-02 visibility gte 10 km [REQUIRED/MAIN|provisional]; C-tw-003-P03-03 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-tw-003-P03-04 aod_550nm lte 0.5 [REQUIRED/MODIFIER|provisional]; C-tw-003-P03-05 city_night_window none None [REQUIRED/MAIN|provisional]; C-tw-003-P03-WD1 wind_speed_10m lte 2 m/s [REQUIRED/MAIN|None]
- 光向：view_azimuth=null（VR-tw-003-P03-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['city_night_window', 'field:aerosol_optical_depth_550nm', 'field:cloud_cover_total_percent', 'field:precipitation_rate_mm_h', 'field:visibility_km', 'field:wind_speed_10m_m_s']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-005-P01　大稻埕淡水河夕照
- genre：golden_hour（template_version golden_hour-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：大稻埕淡水河夕照；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-005-P01-01 golden_hour_window none None [REQUIRED/MAIN|provisional]; C-tw-005-P01-02 cloud_cover_total lte 70 % [REQUIRED/MAIN|provisional]; C-tw-005-P01-03 aod_550nm lte 0.5 [REQUIRED/MAIN|provisional]; C-tw-005-P01-04 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-005-P01-01，geometry_mode=unknown，elevation_deg=None）×太陽方位：日落方位 296.1°(夏至)→269.5°(分)→244.0°(冬至)——sun_azimuth_sector 格點帶無法以 view_azimuth 定心，契約目前無法定義。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_total_percent', 'field:precipitation_rate_mm_h', 'golden_hour_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；大稻埕夕照同屬淡水光向季變語義：觀音山剪影對位只在秋冬成立；建議季節標註＋扇形 sector 依月別方位計算。
- 判定：⚠ 光向季變
- 修法建議：大稻埕夕照同屬淡水光向季變語義：觀音山剪影對位只在秋冬成立；建議季節標註＋扇形 sector 依月別方位計算。

### tw-005-P02　大稻埕河岸暮色／夜景
- genre：blue_hour_city（template_version blue_hour_city-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：大稻埕河岸暮色／夜景；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-005-P02-01 blue_hour_window none None [REQUIRED/MAIN|provisional]; C-tw-005-P02-02 cloud_cover_total lte 70 % [REQUIRED/MAIN|provisional]; C-tw-005-P02-03 aod_550nm lte 0.5 [REQUIRED/MAIN|provisional]; C-tw-005-P02-04 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-005-P02-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['blue_hour_window', 'field:aerosol_optical_depth_550nm', 'field:cloud_cover_total_percent', 'field:precipitation_rate_mm_h']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-010-P01　阿拉寶灣奇岩海岸日出
- genre：geological_landform（template_version geological_landform-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：阿拉寶灣奇岩海岸日出；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-010-P01-01 landform_present none None level [REQUIRED/MAIN|approved]; C-tw-010-P01-02 precipitation lte 0.3 mm/h [REQUIRED/SHOOT|approved]; C-tw-010-P01-03 golden_hour_window none None [QUALITY/BONUS|provisional]; C-tw-010-P01-04 aod_550nm lte 0.4 AOD [QUALITY/BONUS|provisional]
- 光向：view_azimuth=null（VR-tw-010-P01-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aod_550nm', 'field:precipitation_mm_h', 'golden_hour_window', 'landform_present']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-010-P02　和平島奇岩海蝕地景晨昏
- genre：geological_landform（template_version geological_landform-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：和平島奇岩海蝕地景晨昏；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-010-P02-01 landform_present none None level [REQUIRED/MAIN|approved]; C-tw-010-P02-02 precipitation lte 0.3 mm/h [REQUIRED/SHOOT|approved]; C-tw-010-P02-03 golden_hour_window none None [QUALITY/BONUS|provisional]; C-tw-010-P02-04 aod_550nm lte 0.4 AOD [QUALITY/BONUS|provisional]
- 光向：view_azimuth=null（VR-tw-010-P02-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aod_550nm', 'field:precipitation_mm_h', 'golden_hour_window', 'landform_present']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-010-P03　和平島奇岩海岸夕照
- genre：sunset（template_version sunset-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：和平島奇岩海岸夕照；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-010-P03-01 sunset_window none None [REQUIRED/MAIN|provisional]; C-tw-010-P03-02 cloud_cover_low lte 55 % [REQUIRED/MAIN|provisional]; C-tw-010-P03-03 cloud_cover_mid_and_high between [20, 70] % [REQUIRED/MODIFIER|provisional]; C-tw-010-P03-04 precipitation lt 0.3 mm/h [REQUIRED/MAIN|provisional]; C-tw-010-P03-05 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-010-P03-01，geometry_mode=unknown，elevation_deg=None）×太陽方位：日落方位 296.1°(夏至)→269.5°(分)→244.0°(冬至)——sun_azimuth_sector 格點帶無法以 view_azimuth 定心，契約目前無法定義。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_low_percent', 'field:cloud_cover_mid_percent+cloud_cover_high_percent', 'field:precipitation_rate_mm_h', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-011-P01　永安漁港夕照＋觀海橋
- genre：sunset（template_version sunset-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：永安漁港夕照＋觀海橋；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-011-P01-01 sunset_window none None [REQUIRED/MAIN|provisional]; C-tw-011-P01-02 cloud_cover_low lte 55 % [REQUIRED/MAIN|provisional]; C-tw-011-P01-03 cloud_cover_mid_and_high between [20, 70] % [REQUIRED/MODIFIER|provisional]; C-tw-011-P01-04 precipitation lt 0.3 mm/h [REQUIRED/MAIN|provisional]; C-tw-011-P01-05 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-011-P01-01，geometry_mode=unknown，elevation_deg=None）×太陽方位：日落方位 296.0°(夏至)→269.5°(分)→244.0°(冬至)——sun_azimuth_sector 格點帶無法以 view_azimuth 定心，契約目前無法定義。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_low_percent', 'field:cloud_cover_mid_percent+cloud_cover_high_percent', 'field:precipitation_rate_mm_h', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-011-P02　觀海橋暮色／夜間燈景＋港池倒影
- genre：city_night（template_version city_night-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：觀海橋暮色／夜間燈景＋港池倒影；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-011-P02-01 cloud_cover_total lte 30 % [REQUIRED/MAIN|provisional]; C-tw-011-P02-02 visibility gte 10 km [REQUIRED/MAIN|provisional]; C-tw-011-P02-03 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-tw-011-P02-04 aod_550nm lte 0.5 [QUALITY/BONUS|provisional]; C-tw-011-P02-05 city_night_window none None [REQUIRED/MAIN|provisional]; C-tw-011-P02-WD1 wind_speed_10m lte 2 m/s [REQUIRED/MAIN|None]
- 光向：view_azimuth=null（VR-tw-011-P02-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['city_night_window', 'field:aerosol_optical_depth_550nm', 'field:cloud_cover_total_percent', 'field:precipitation_rate_mm_h', 'field:visibility_km', 'field:wind_speed_10m_m_s']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-019-P01　合歡主峰東向日出與群峰
- genre：sunrise（template_version sunrise-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：合歡主峰東向日出與群峰；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-019-P01-01 sunrise_time_window none None [REQUIRED/MAIN|provisional]; C-tw-019-P01-02 cloud_cover_low lte 55 % [REQUIRED/MAIN|provisional]; C-tw-019-P01-03 cloud_cover_mid_and_high between [20, 70] % [QUALITY/MODIFIER|provisional]; C-tw-019-P01-04 precipitation lt 0.3 mm/h [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null×日出方位 64.1°(夏至)→90.5°(分)→115.8°(冬至)——同上。
- 條件服務映射：資料集 ['dataset:gfs_0p25', '未綁定']；欄位/代理：['field:cloud_cover_low_percent', 'field:cloud_cover_mid_percent+cloud_cover_high_percent', 'field:precipitation_rate_mm_h', 'sunrise_time_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；東向日出：日出方位冬約 115°→夏約 64°，20° 扇形 sector 若全年固定會偏；建議月別方位。
- 判定：⚠ 光向季變
- 修法建議：東向日出：日出方位冬約 115°→夏約 64°，20° 扇形 sector 若全年固定會偏；建議月別方位。

### tw-019-P02　合歡主峰西向夕照與群山
- genre：sunset（template_version sunset-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：合歡主峰西向夕照與群山；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-019-P02-01 sunset_window none None [REQUIRED/MAIN|provisional]; C-tw-019-P02-02 cloud_cover_low lte 55 % [REQUIRED/MAIN|provisional]; C-tw-019-P02-03 cloud_cover_mid_and_high between [20, 70] % [REQUIRED/MODIFIER|provisional]; C-tw-019-P02-04 precipitation lt 0.3 mm/h [REQUIRED/MAIN|provisional]; C-tw-019-P02-05 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-019-P02-01，geometry_mode=unknown，elevation_deg=None）×太陽方位：日落方位 295.9°(夏至)→269.5°(分)→244.2°(冬至)——sun_azimuth_sector 格點帶無法以 view_azimuth 定心，契約目前無法定義。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_low_percent', 'field:cloud_cover_mid_percent+cloud_cover_high_percent', 'field:precipitation_rate_mm_h', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-019-P03　合歡主峰360°高山群峰全景
- genre：mountain_view（template_version mountain_view-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：合歡主峰360°高山群峰全景；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-019-P03-01 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]; C-tw-019-P03-02 cloud_cover_mid between [30, 60] % [REQUIRED/MAIN|provisional]; C-tw-019-P03-03 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-tw-019-P03-04 sunset_window none None [QUALITY/MODIFIER|provisional]
- 光向：view_azimuth=null（VR-tw-019-P03-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_mid_percent', 'field:precipitation_rate_mm_h', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-019-P04　合歡主峰下方雲海與露出群峰
- genre：cloud_sea（template_version cloud_sea-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：合歡主峰下方雲海與露出群峰；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-019-P04-01 relative_humidity_700hpa gte 85 % [REQUIRED/MAIN|provisional]; C-tw-019-P04-02 relative_humidity_600hpa gte 55 % [REQUIRED/MAIN|provisional]; C-tw-019-P04-03 lcl_height_m_agl lt 3217 m [REQUIRED/MAIN|provisional]; C-tw-019-P04-04 cloud_cover_low gte 60 % [REQUIRED/MAIN|provisional]; C-tw-019-P04-05 aod_550nm lte 0.4 [REQUIRED/MAIN|provisional]; C-tw-019-P04-06 visibility gte 1 km [REQUIRED/MAIN|provisional]; C-tw-019-P04-07 temperature_delta_700_600_c gte 0.0 °C [QUALITY/MODIFIER|provisional]; C-tw-019-P04-08 wind_speed_600hpa lt 12.0 m/s [QUALITY/MODIFIER|provisional]; C-tw-019-P04-LW1 light_window none None [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-019-P04-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:cwa_wrf3', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_low_percent', 'field:lcl_height_m_agl', 'field:relative_humidity_850hpa_percent', 'field:relative_humidity_925hpa_percent', 'field:temperature_850hpa_c+temperature_925hpa_c']…
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；LCL 門檻 3,217 m＝觀點 3,417 m−200 m；觀點高度無 DEM 溯源欄位。綁定 cwa_wrf3 與同型機會（gfs_0p25）不一致，需統一並記錄溯源。
- 判定：⚠ LCL DEM 溯源
- 修法建議：LCL 門檻 3,217 m＝觀點 3,417 m−200 m；觀點高度無 DEM 溯源欄位。綁定 cwa_wrf3 與同型機會（gfs_0p25）不一致，需統一並記錄溯源。

### tw-019-P05　合歡主峰高山星空／銀河
- genre：night_sky（template_version night_sky-v0.4；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：合歡主峰高山星空／銀河；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-019-P05-01 astronomical_darkness none None [REQUIRED/MAIN|provisional]; C-tw-019-P05-02 moon_illumination_fraction lte 0.5 [REQUIRED/MAIN|provisional]; C-tw-019-P05-03 cloud_cover_total lte 20 % [REQUIRED/MAIN|provisional]; C-tw-019-P05-04 aod_550nm lte 0.3 [REQUIRED/MAIN|provisional]; C-tw-019-P05-05 galactic_core_altitude gte 10 ° [REQUIRED/MAIN|provisional]; C-tw-019-P05-06 moon_altitude lt 0 ° [REQUIRED/MAIN|provisional]; C-tw-019-P05-07 moon_target_separation_deg gte 40 ° [REQUIRED/MAIN|provisional]; C-tw-019-P05-08 moon_illuminance_proxy lte 0.15 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-019-P05-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['astronomical_darkness', 'field:aerosol_optical_depth_550nm', 'field:cloud_cover_total_percent', 'galactic_core_altitude', 'moon_altitude', 'moon_illuminance_proxy']…
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-019-P06　合歡主峰雪覆山稜
- genre：mountain_view（template_version mountain_view-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：合歡主峰雪覆山稜；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-019-P06-01 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]; C-tw-019-P06-02 cloud_cover_mid between [30, 60] % [REQUIRED/MAIN|provisional]; C-tw-019-P06-03 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-tw-019-P06-04 sunset_window none None [QUALITY/MODIFIER|provisional]
- 光向：view_azimuth=null（VR-tw-019-P06-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_mid_percent', 'field:precipitation_rate_mm_h', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；主體「雪覆山稜」但契約無任何雪況條件（無 seasonal_state、無雪深/雪線代理）——無雪的夏季也能全數通過。建議補 seasonal_state window（11–4 月）或溫度/降水史雪況代理，標 provisional。
- 判定：⚠ 雪況代理缺失
- 修法建議：主體「雪覆山稜」但契約無任何雪況條件（無 seasonal_state、無雪深/雪線代理）——無雪的夏季也能全數通過。建議補 seasonal_state window（11–4 月）或溫度/降水史雪況代理，標 provisional。

### tw-024-P01　祝山日出與中央山脈稜線
- genre：sunrise（template_version sunrise-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：祝山日出與中央山脈稜線；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-024-P01-01 sunrise_time_window none None [REQUIRED/MAIN|provisional]; C-tw-024-P01-02 cloud_cover_low lte 55 % [REQUIRED/MAIN|provisional]; C-tw-024-P01-03 cloud_cover_mid_and_high between [20, 70] % [QUALITY/BONUS|provisional]; C-tw-024-P01-04 precipitation lt 0.3 mm/h [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null×日出方位 64.3°(夏至)→90.5°(分)→115.7°(冬至)——同上。
- 條件服務映射：資料集 ['dataset:gfs_0p25', '未綁定']；欄位/代理：['field:cloud_cover_low_percent', 'field:cloud_cover_mid_percent+cloud_cover_high_percent', 'field:precipitation_rate_mm_h', 'sunrise_time_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-024-P02　祝山日出雲海
- genre：cloud_sea（template_version cloud_sea-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：祝山日出雲海；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-024-P02-01 sunrise_time_window none None [REQUIRED/MAIN|provisional]; C-tw-024-P02-04 precipitation lt 0.3 mm/h [REQUIRED/MAIN|provisional]; C-tw-024-P02-CS1 relative_humidity_925hpa gte 85 % [REQUIRED/MAIN|None]; C-tw-024-P02-CS2 relative_humidity_850hpa gte 55 % [REQUIRED/MAIN|None]; C-tw-024-P02-CS3 lcl_height_m_agl lt 2250 m [REQUIRED/MAIN|None]; C-tw-024-P02-CS4 cloud_cover_low gte 60 % [REQUIRED/MAIN|None]; C-tw-024-P02-LW1 light_window none None [REQUIRED/MAIN|None]
- 光向：view_azimuth=null（VR-tw-024-P02-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cwa_wrf3', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:cloud_cover_low_percent', 'field:lcl_height_m_agl', 'field:precipitation_rate_mm_h', 'field:relative_humidity_850hpa_percent', 'field:relative_humidity_925hpa_percent', 'light_window']…
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；雲海語義已於 2026-11-06 CL-DATA-12 batch d 重構為模板判據（RH925/低雲/LCL），方向正確；仍缺觀點高度 DEM 溯源。
- 判定：⚠ LCL DEM 溯源
- 修法建議：雲海語義已於 2026-11-06 CL-DATA-12 batch d 重構為模板判據（RH925/低雲/LCL），方向正確；仍缺觀點高度 DEM 溯源。

### tw-024-P03　小笠原山360°群山全景
- genre：sunrise（template_version sunrise-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：小笠原山360°群山全景；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-024-P03-01 sunrise_time_window none None [QUALITY/MODIFIER|provisional]; C-tw-024-P03-02 cloud_cover_low lte 55 % [REQUIRED/MAIN|provisional]; C-tw-024-P03-03 cloud_cover_mid_and_high between [20, 70] % [QUALITY/MODIFIER|provisional]; C-tw-024-P03-04 precipitation lt 0.3 mm/h [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null×日出方位 64.3°(夏至)→90.5°(分)→115.7°(冬至)——同上。
- 條件服務映射：資料集 ['dataset:gfs_0p25', '未綁定']；欄位/代理：['field:cloud_cover_low_percent', 'field:cloud_cover_mid_percent+cloud_cover_high_percent', 'field:precipitation_rate_mm_h', 'sunrise_time_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-024-P04　小笠原山晚霞與群山
- genre：sunset（template_version sunset-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：小笠原山晚霞與群山；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-024-P04-01 sunset_window none None [REQUIRED/MAIN|provisional]; C-tw-024-P04-02 cloud_cover_low lte 55 % [REQUIRED/MAIN|provisional]; C-tw-024-P04-03 cloud_cover_mid_and_high between [20, 70] % [REQUIRED/MODIFIER|provisional]; C-tw-024-P04-04 precipitation lt 0.3 mm/h [REQUIRED/MAIN|provisional]; C-tw-024-P04-05 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-024-P04-01，geometry_mode=unknown，elevation_deg=None）×太陽方位：日落方位 295.7°(夏至)→269.5°(分)→244.3°(冬至)——sun_azimuth_sector 格點帶無法以 view_azimuth 定心，契約目前無法定義。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_low_percent', 'field:cloud_cover_mid_percent+cloud_cover_high_percent', 'field:precipitation_rate_mm_h', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-024-P05　小笠原山群星夜空
- genre：night_sky（template_version night_sky-v0.4；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：小笠原山群星夜空；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-024-P05-01 astronomical_darkness none None [REQUIRED/MAIN|provisional]; C-tw-024-P05-02 moon_illumination_fraction lte 0.5 [REQUIRED/MAIN|provisional]; C-tw-024-P05-03 cloud_cover_total lte 20 % [REQUIRED/MAIN|provisional]; C-tw-024-P05-04 aod_550nm lte 0.3 [REQUIRED/MAIN|provisional]; C-tw-024-P05-05 galactic_core_altitude gte 10 ° [REQUIRED/MAIN|provisional]; C-tw-024-P05-06 moon_altitude lt 0 ° [REQUIRED/MAIN|provisional]; C-tw-024-P05-07 moon_target_separation_deg gte 40 ° [REQUIRED/MAIN|provisional]; C-tw-024-P05-08 moon_illuminance_proxy lte 0.15 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-024-P05-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['astronomical_darkness', 'field:aerosol_optical_depth_550nm', 'field:cloud_cover_total_percent', 'galactic_core_altitude', 'moon_altitude', 'moon_illuminance_proxy']…
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-027-P01　月世界惡地層次
- genre：geological_landform（template_version geological_landform-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：月世界惡地層次；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-027-P01-01 landform_present none None level [REQUIRED/MAIN|approved]; C-tw-027-P01-02 precipitation lte 0.3 mm/h [REQUIRED/SHOOT|approved]; C-tw-027-P01-03 golden_hour_window none None [QUALITY/BONUS|provisional]; C-tw-027-P01-04 aod_550nm lte 0.4 AOD [QUALITY/BONUS|provisional]
- 光向：view_azimuth=null（VR-tw-027-P01-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aod_550nm', 'field:precipitation_mm_h', 'golden_hour_window', 'landform_present']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-027-P02　月世界夜間投光地景
- genre：night_sky（template_version geological_landform-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：月世界夜間投光地景；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-027-P02-01 landform_present none None level [REQUIRED/MAIN|approved]; C-tw-027-P02-02 precipitation lte 0.3 mm/h [REQUIRED/SHOOT|approved]; C-tw-027-P02-05 cloud_cover_total lte 20 % [REQUIRED/MAIN|provisional]; C-tw-027-P02-06 aod_550nm lte 0.3 [REQUIRED/MAIN|provisional]; C-tw-027-P02-07 galactic_core_altitude gte 10 ° [REQUIRED/MAIN|provisional]; C-tw-027-P02-11 city_night_window none None [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-027-P02-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['city_night_window', 'field:aerosol_optical_depth_550nm', 'field:cloud_cover_total_percent', 'field:precipitation_mm_h', 'galactic_core_altitude', 'landform_present']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-027-P03　月世界夕照地貌
- genre：geological_landform（template_version geological_landform-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：月世界夕照地貌；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-027-P03-01 landform_present none None level [REQUIRED/MAIN|approved]; C-tw-027-P03-02 precipitation lte 0.3 mm/h [REQUIRED/SHOOT|approved]; C-tw-027-P03-03 golden_hour_window none None [QUALITY/BONUS|provisional]; C-tw-027-P03-04 aod_550nm lte 0.4 AOD [QUALITY/BONUS|provisional]
- 光向：view_azimuth=null（VR-tw-027-P03-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aod_550nm', 'field:precipitation_mm_h', 'golden_hour_window', 'landform_present']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-035-P01　六十石山花東縱谷層巒＋季節花田
- genre：seasonal_plant（template_version seasonal_plant-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：六十石山花東縱谷層巒＋季節花田；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-035-P01-01 seasonal_state eq window_open [REQUIRED/MAIN|provisional]; C-tw-035-P01-02 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-tw-035-P01-03 wind_speed_10m lt 5 m/s [REQUIRED/MAIN|provisional]; C-tw-035-P01-04 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]; C-tw-035-P01-05 cloud_cover_mid between [30, 60] % [REQUIRED/MAIN|provisional]; C-tw-035-P01-07 sunset_window none None [QUALITY/MODIFIER|provisional]
- 光向：view_azimuth=null（VR-tw-035-P01-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_mid_percent', 'field:precipitation_rate_mm_h', 'field:wind_speed_10m_m_s', 'seasonal_state', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-035-P02　六十石山午後雲隙光＋縱谷／花田
- genre：seasonal_plant（template_version seasonal_plant-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：六十石山午後雲隙光＋縱谷／花田；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-035-P02-01 seasonal_state eq window_open [REQUIRED/MAIN|provisional]; C-tw-035-P02-02 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-tw-035-P02-03 wind_speed_10m lt 5 m/s [REQUIRED/MAIN|provisional]; C-tw-035-P02-04 golden_hour_window none None [REQUIRED/MAIN|provisional]; C-tw-035-P02-05 cloud_cover_total lte 50 % [REQUIRED/MAIN|provisional]; C-tw-035-P02-07 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-035-P02-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_total_percent', 'field:precipitation_rate_mm_h', 'field:wind_speed_10m_m_s', 'golden_hour_window', 'seasonal_state']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；裂雲窗判據用 cloud_cover_total ≤50% 總量代理：連續 45% 層雲幕可通過但無直射光，65% 碎積雲反被否決——與其 rationale「塊狀雲可穿隙、連續雲幕即無直射光」自身矛盾。建議改 cloud_cover_low lte（直射光前題）＋cloud_cover_mid/high between 20–70 作染料項，或引入碎雲/雲隙代理指標並校準。
- 判定：❌ 裂雲代理過粗
- 修法建議：裂雲窗判據用 cloud_cover_total ≤50% 總量代理：連續 45% 層雲幕可通過但無直射光，65% 碎積雲反被否決——與其 rationale「塊狀雲可穿隙、連續雲幕即無直射光」自身矛盾。建議改 cloud_cover_low lte（直射光前題）＋cloud_cover_mid/high between 20–70 作染料項，或引入碎雲/雲隙代理指標並校準。

### tw-035-P03　六十石山丘陵／縱谷夕照
- genre：sunset（template_version sunset-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：六十石山丘陵／縱谷夕照；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-035-P03-01 sunset_window none None [REQUIRED/MAIN|provisional]; C-tw-035-P03-02 cloud_cover_low lte 55 % [REQUIRED/MAIN|provisional]; C-tw-035-P03-03 cloud_cover_mid_and_high between [20, 70] % [REQUIRED/MODIFIER|provisional]; C-tw-035-P03-04 precipitation lt 0.3 mm/h [REQUIRED/MAIN|provisional]; C-tw-035-P03-05 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-035-P03-01，geometry_mode=unknown，elevation_deg=None）×太陽方位：日落方位 295.7°(夏至)→269.5°(分)→244.4°(冬至)——sun_azimuth_sector 格點帶無法以 view_azimuth 定心，契約目前無法定義。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_low_percent', 'field:cloud_cover_mid_percent+cloud_cover_high_percent', 'field:precipitation_rate_mm_h', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-035-P04　六十石山黃昏彩霞＋丘陵／縱谷
- genre：sunset（template_version sunset-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：六十石山黃昏彩霞＋丘陵／縱谷；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-035-P04-01 sunset_window none None [REQUIRED/MAIN|provisional]; C-tw-035-P04-02 cloud_cover_low lte 55 % [REQUIRED/MAIN|provisional]; C-tw-035-P04-03 cloud_cover_mid_and_high between [20, 70] % [REQUIRED/MODIFIER|provisional]; C-tw-035-P04-04 precipitation lt 0.3 mm/h [REQUIRED/MAIN|provisional]; C-tw-035-P04-05 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-035-P04-01，geometry_mode=unknown，elevation_deg=None）×太陽方位：日落方位 295.7°(夏至)→269.5°(分)→244.4°(冬至)——sun_azimuth_sector 格點帶無法以 view_azimuth 定心，契約目前無法定義。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_low_percent', 'field:cloud_cover_mid_percent+cloud_cover_high_percent', 'field:precipitation_rate_mm_h', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-035-P05　六十石山丘陵／涼亭銀河星空
- genre：night_sky（template_version night_sky-v0.4；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：六十石山丘陵／涼亭銀河星空；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-035-P05-02 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-tw-035-P05-03 wind_speed_10m lt 5 m/s [REQUIRED/MAIN|provisional]; C-tw-035-P05-04 astronomical_darkness none None [REQUIRED/MAIN|provisional]; C-tw-035-P05-05 moon_illumination_fraction lte 0.5 [REQUIRED/MAIN|provisional]; C-tw-035-P05-06 cloud_cover_total lte 20 % [REQUIRED/MAIN|provisional]; C-tw-035-P05-07 aod_550nm lte 0.3 [REQUIRED/MAIN|provisional]; C-tw-035-P05-08 galactic_core_altitude gte 10 ° [REQUIRED/MAIN|provisional]; C-tw-035-P05-09 moon_altitude lt 0 ° [REQUIRED/MAIN|provisional]; C-tw-035-P05-10 moon_target_separation_deg gte 40 ° [REQUIRED/MAIN|provisional]; C-tw-035-P05-11 moon_illuminance_proxy lte 0.15 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-035-P05-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['astronomical_darkness', 'field:aerosol_optical_depth_550nm', 'field:cloud_cover_total_percent', 'field:precipitation_rate_mm_h', 'field:wind_speed_10m_m_s', 'galactic_core_altitude']…
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；芒草逆光已綁 golden_hour＋wind 5 m/s provisional，但無 seasonal_state（芒草期）條件，季節成立語義缺。
- 判定：⚠ 季節條件缺失
- 修法建議：芒草逆光已綁 golden_hour＋wind 5 m/s provisional，但無 seasonal_state（芒草期）條件，季節成立語義缺。

### tw-035-P06　六十石山觀景點下方縱谷雲海
- genre：cloud_sea（template_version cloud_sea-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：六十石山觀景點下方縱谷雲海；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-035-P06-01 seasonal_state eq window_open [QUALITY/MODIFIER|provisional]; C-tw-035-P06-02 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-tw-035-P06-03 wind_speed_10m lt 5 m/s [REQUIRED/MAIN|provisional]; C-tw-035-P06-CS1 relative_humidity_925hpa gte 85 % [REQUIRED/MAIN|None]; C-tw-035-P06-CS2 cloud_cover_low gte 60 % [REQUIRED/MAIN|None]; C-tw-035-P06-LW1 light_window none None [REQUIRED/MAIN|None]
- 光向：view_azimuth=null（VR-tw-035-P06-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cwa_wrf3', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:cloud_cover_low_percent', 'field:precipitation_rate_mm_h', 'field:relative_humidity_925hpa_percent', 'field:wind_speed_10m_m_s', 'light_window', 'seasonal_state']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-035-P07　黃花亭金針花田與山景
- genre：seasonal_plant（template_version seasonal_plant-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：黃花亭金針花田與山景；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-035-P07-01 seasonal_state eq window_open [REQUIRED/MAIN|provisional]; C-tw-035-P07-02 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-tw-035-P07-03 wind_speed_10m lt 5 m/s [REQUIRED/MAIN|provisional]; C-tw-035-P07-04 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]; C-tw-035-P07-05 cloud_cover_mid between [30, 60] % [REQUIRED/MAIN|provisional]; C-tw-035-P07-07 sunset_window none None [QUALITY/MODIFIER|provisional]
- 光向：view_azimuth=null（VR-tw-035-P07-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_mid_percent', 'field:precipitation_rate_mm_h', 'field:wind_speed_10m_m_s', 'seasonal_state', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-035-P08　小瑞士金針花坡與丘陵曲線
- genre：seasonal_plant（template_version seasonal_plant-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：小瑞士金針花坡與丘陵曲線；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-035-P08-01 seasonal_state eq window_open [REQUIRED/MAIN|provisional]; C-tw-035-P08-02 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-tw-035-P08-03 wind_speed_10m lt 5 m/s [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-035-P08-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:gfs_0p25', '未綁定']；欄位/代理：['field:precipitation_rate_mm_h', 'field:wind_speed_10m_m_s', 'seasonal_state']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-035-P09　忘憂亭縱谷雲隙光與夕照
- genre：golden_hour（template_version golden_hour-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：忘憂亭縱谷雲隙光與夕照；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-035-P09-01 golden_hour_window none None [REQUIRED/MAIN|provisional]; C-tw-035-P09-02 cloud_cover_total lte 50 % [REQUIRED/MAIN|provisional]; C-tw-035-P09-03 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-tw-035-P09-04 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-035-P09-01，geometry_mode=unknown，elevation_deg=None）×太陽方位：日落方位 295.7°(夏至)→269.5°(分)→244.4°(冬至)——sun_azimuth_sector 格點帶無法以 view_azimuth 定心，契約目前無法定義。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_total_percent', 'field:precipitation_rate_mm_h', 'golden_hour_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-035-P10　鹿蔥亭金針花丘陵與縱谷層次
- genre：seasonal_plant（template_version seasonal_plant-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：鹿蔥亭金針花丘陵與縱谷層次；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-035-P10-01 seasonal_state eq window_open [REQUIRED/MAIN|provisional]; C-tw-035-P10-02 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-tw-035-P10-03 wind_speed_10m lt 5 m/s [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-035-P10-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:gfs_0p25', '未綁定']；欄位/代理：['field:precipitation_rate_mm_h', 'field:wind_speed_10m_m_s', 'seasonal_state']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-040-P01　玉山主峰日出與高山群峰
- genre：mountain_view（template_version mountain_view-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：玉山主峰日出與高山群峰；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-040-P01-01 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]; C-tw-040-P01-02 cloud_cover_mid between [30, 60] % [REQUIRED/MAIN|provisional]; C-tw-040-P01-03 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-tw-040-P01-04 sunset_window none None [QUALITY/MODIFIER|provisional]; C-tw-040-P01-SR1 sunrise_time_window none None [REQUIRED/MAIN|None]
- 光向：view_azimuth=null（VR-tw-040-P01-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_mid_percent', 'field:precipitation_rate_mm_h', 'sunrise_time_window', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-040-P02　玉山主峰四方群峰全景
- genre：mountain_view（template_version mountain_view-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：玉山主峰四方群峰全景；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-040-P02-01 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]; C-tw-040-P02-02 cloud_cover_mid between [30, 60] % [REQUIRED/MAIN|provisional]; C-tw-040-P02-03 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-tw-040-P02-04 sunset_window none None [QUALITY/MODIFIER|provisional]
- 光向：view_azimuth=null（VR-tw-040-P02-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_mid_percent', 'field:precipitation_rate_mm_h', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-040-P03　玉山主峰雪覆岩稜
- genre：mountain_view（template_version mountain_view-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：玉山主峰雪覆岩稜；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-040-P03-01 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]; C-tw-040-P03-02 cloud_cover_mid between [30, 60] % [REQUIRED/MAIN|provisional]; C-tw-040-P03-03 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-tw-040-P03-04 sunset_window none None [QUALITY/MODIFIER|provisional]
- 光向：view_azimuth=null（VR-tw-040-P03-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_mid_percent', 'field:precipitation_rate_mm_h', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；同 tw-019-P06：主體「雪覆岩稜」，契約無雪況代理，夏季全通過。
- 判定：⚠ 雪況代理缺失
- 修法建議：同 tw-019-P06：主體「雪覆岩稜」，契約無雪況代理，夏季全通過。

### tw-040-P04　排雲山莊下方雲海與山稜
- genre：cloud_sea（template_version cloud_sea-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：排雲山莊下方雲海與山稜；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-040-P04-01 relative_humidity_700hpa gte 85 % [REQUIRED/MAIN|provisional]; C-tw-040-P04-02 relative_humidity_600hpa gte 55 % [REQUIRED/MAIN|provisional]; C-tw-040-P04-03 lcl_height_m_agl lt 3752 m [REQUIRED/MAIN|provisional]; C-tw-040-P04-04 cloud_cover_low gte 60 % [REQUIRED/MAIN|provisional]; C-tw-040-P04-05 aod_550nm lte 0.4 [REQUIRED/MAIN|provisional]; C-tw-040-P04-06 visibility gte 1 km [REQUIRED/MAIN|provisional]; C-tw-040-P04-07 temperature_delta_700_600_c gte 0.0 °C [QUALITY/MODIFIER|provisional]; C-tw-040-P04-08 wind_speed_600hpa lt 12.0 m/s [QUALITY/MODIFIER|provisional]; C-tw-040-P04-LW1 light_window none None [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-040-P04-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:cwa_wrf3', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_low_percent', 'field:lcl_height_m_agl', 'field:relative_humidity_850hpa_percent', 'field:relative_humidity_925hpa_percent', 'field:temperature_850hpa_c+temperature_925hpa_c']…
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；複驗：門檻 3,752 m 由「觀點 3,952 m−200 m」推出，3,952 m 是玉山主峰高度（沿自 tw-040-P01/P02）；本機會觀點是排雲山莊（約 3,468 m），高度抄錯來源，LCL 應約 3,268 m——偏寬 ~484 m，會把雲頂高於視線的案例誤判為成立。
- 判定：❌ LCL 觀點高度錯誤
- 修法建議：複驗：門檻 3,752 m 由「觀點 3,952 m−200 m」推出，3,952 m 是玉山主峰高度（沿自 tw-040-P01/P02）；本機會觀點是排雲山莊（約 3,468 m），高度抄錯來源，LCL 應約 3,268 m——偏寬 ~484 m，會把雲頂高於視線的案例誤判為成立。

### tw-040-P05　排雲山莊夕照與山稜
- genre：mountain_view（template_version mountain_view-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：排雲山莊夕照與山稜；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-040-P05-01 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]; C-tw-040-P05-02 cloud_cover_mid between [30, 60] % [REQUIRED/MAIN|provisional]; C-tw-040-P05-03 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-tw-040-P05-04 sunset_window none None [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-040-P05-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_mid_percent', 'field:precipitation_rate_mm_h', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-040-P06　排雲—主峰線高山星空／銀河
- genre：night_sky（template_version night_sky-v0.4；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：排雲—主峰線高山星空／銀河；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-040-P06-01 astronomical_darkness none None [REQUIRED/MAIN|provisional]; C-tw-040-P06-02 moon_illumination_fraction lte 0.5 [REQUIRED/MAIN|provisional]; C-tw-040-P06-03 cloud_cover_total lte 20 % [REQUIRED/MAIN|provisional]; C-tw-040-P06-04 aod_550nm lte 0.3 [REQUIRED/MAIN|provisional]; C-tw-040-P06-05 galactic_core_altitude gte 10 ° [REQUIRED/MAIN|provisional]; C-tw-040-P06-06 moon_altitude lt 0 ° [REQUIRED/MAIN|provisional]; C-tw-040-P06-07 moon_target_separation_deg gte 40 ° [REQUIRED/MAIN|provisional]; C-tw-040-P06-08 moon_illuminance_proxy lte 0.15 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-040-P06-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['astronomical_darkness', 'field:aerosol_optical_depth_550nm', 'field:cloud_cover_total_percent', 'galactic_core_altitude', 'moon_altitude', 'moon_illuminance_proxy']…
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-054-P01　正濱漁港色彩屋倒影
- genre：reflection（template_version reflection-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：正濱漁港色彩屋倒影；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-054-P01-01 wind_speed_10m lte 2 m/s [REQUIRED/MAIN|provisional]; C-tw-054-P01-02 water_surface_state none None [REQUIRED/MAIN|provisional]; C-tw-054-P01-03 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-tw-054-P01-04 cloud_cover_total between [20, 60] % [QUALITY/BONUS|provisional]
- 光向：view_azimuth=null（VR-tw-054-P01-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:gfs_0p25', '未綁定']；欄位/代理：['field:cloud_cover_total_percent', 'field:precipitation_rate_mm_h', 'field:wind_speed_10m_m_s', 'water_surface_state']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-054-P02　正濱漁港藍調夜景
- genre：blue_hour_city（template_version blue_hour_city-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：正濱漁港藍調夜景；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-054-P02-01 blue_hour_window none None [REQUIRED/MAIN|provisional]; C-tw-054-P02-02 cloud_cover_total lte 70 % [REQUIRED/MAIN|provisional]; C-tw-054-P02-03 aod_550nm lte 0.5 [REQUIRED/MAIN|provisional]; C-tw-054-P02-04 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-054-P02-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['blue_hour_window', 'field:aerosol_optical_depth_550nm', 'field:cloud_cover_total_percent', 'field:precipitation_rate_mm_h']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-062-P01　得月樓與水頭洋樓建築外觀
- genre：overcast_soft（template_version overcast_soft-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：得月樓與水頭洋樓建築外觀；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-062-P01-02 precipitation lt 0.5 mm/h [REQUIRED/MAIN|approved]; C-tw-062-P01-03 golden_hour_window none None [QUALITY/BONUS|provisional]; C-tw-062-P01-04 aod_550nm lte 0.4 AOD [QUALITY/BONUS|provisional]; C-tw-062-P01-OV1 cloud_cover_total gte 70 % [REQUIRED/MAIN|None]; C-tw-062-P01-OV3 wind_speed_10m lt 5 m/s [QUALITY/BONUS|None]
- 光向：view_azimuth=null（VR-tw-062-P01-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aod_550nm', 'field:cloud_cover_total_percent', 'field:precipitation_mm_h', 'field:wind_speed_10m_m_s', 'golden_hour_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-076-P01　龍磐草原海岸日出
- genre：mountain_view（template_version mountain_view-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：龍磐草原海岸日出；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-076-P01-01 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]; C-tw-076-P01-02 cloud_cover_mid between [30, 60] % [REQUIRED/MAIN|provisional]; C-tw-076-P01-03 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-tw-076-P01-SR1 sunrise_time_window none None [REQUIRED/MAIN|None]
- 光向：view_azimuth=null（VR-tw-076-P01-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_mid_percent', 'field:precipitation_rate_mm_h', 'sunrise_time_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；龍磐草原日出面向太平洋，光向自由度高，通案缺 view_azimuth 仍記。
- 判定：⚠ 光向季變
- 修法建議：龍磐草原日出面向太平洋，光向自由度高，通案缺 view_azimuth 仍記。

### tw-076-P02　龍磐草原銀河／星空
- genre：night_sky（template_version night_sky-v0.4；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：龍磐草原銀河／星空；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-tw-076-P02-01 astronomical_darkness none None [REQUIRED/MAIN|provisional]; C-tw-076-P02-02 moon_illumination_fraction lte 0.5 [REQUIRED/MAIN|provisional]; C-tw-076-P02-03 cloud_cover_total lte 20 % [REQUIRED/MAIN|provisional]; C-tw-076-P02-04 aod_550nm lte 0.3 [REQUIRED/MAIN|provisional]; C-tw-076-P02-05 galactic_core_altitude gte 10 ° [REQUIRED/MAIN|provisional]; C-tw-076-P02-06 moon_altitude lt 0 ° [REQUIRED/MAIN|provisional]; C-tw-076-P02-07 moon_target_separation_deg gte 40 ° [REQUIRED/MAIN|provisional]; C-tw-076-P02-08 moon_illuminance_proxy lte 0.15 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-076-P02-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['astronomical_darkness', 'field:aerosol_optical_depth_550nm', 'field:cloud_cover_total_percent', 'galactic_core_altitude', 'moon_altitude', 'moon_illuminance_proxy']…
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-086-P01　八里崁頭里・淡水大橋觀景點：霧中淡水大橋（霧景）
- genre：cloud_sea（template_version cloud_sea-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：八里崁頭里・淡水大橋觀景點：霧中淡水大橋（霧景）；claims=4（audit_status=['PARTIAL', 'PARTIAL', 'UNKNOWN', 'PARTIAL']）
- 成立需求（REQUIRED 判據）：C-tw-086-P01-01 relative_humidity_925hpa gte 85 % [REQUIRED/MAIN|provisional]; C-tw-086-P01-02 cloud_cover_low gte 60 % [REQUIRED/MAIN|provisional]; C-tw-086-P01-03 precipitation lt 0.3 mm/h [REQUIRED/MAIN|provisional]; C-tw-086-P01-04 wind_speed_10m lt 3 m/s [REQUIRED/MAIN|provisional]; C-tw-086-P01-LW1 light_window none None [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-086-P01-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:gfs_0p25', '未綁定']；欄位/代理：['field:cloud_cover_low_percent', 'field:precipitation_rate_mm_h', 'field:relative_humidity_925hpa_percent', 'field:wind_speed_10m_m_s', 'light_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-086-P02　八里崁頭里・淡水大橋觀景點：淡水大橋日景通透（白天通透）
- genre：overlook（template_version overlook-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：八里崁頭里・淡水大橋觀景點：淡水大橋日景通透（白天通透）；claims=4（audit_status=['PARTIAL', 'PARTIAL', 'UNKNOWN', 'PARTIAL']）
- 成立需求（REQUIRED 判據）：C-tw-086-P02-01 visibility gte 5 km [REQUIRED/MAIN|provisional]; C-tw-086-P02-02 aod_550nm lte 0.4 [REQUIRED/MAIN|provisional]; C-tw-086-P02-03 cloud_cover_low lte 30 % [REQUIRED/MAIN|provisional]; C-tw-086-P02-04 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-086-P02-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:gfs_0p25']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_low_percent', 'field:precipitation_rate_mm_h', 'field:visibility_m']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### tw-086-P03　八里崁頭里・淡水大橋觀景點：淡水大橋火燒雲（日落）
- genre：sunset（template_version sunset-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：八里崁頭里・淡水大橋觀景點：淡水大橋火燒雲（日落）；claims=4（audit_status=['PARTIAL', 'PARTIAL', 'UNKNOWN', 'PARTIAL']）
- 成立需求（REQUIRED 判據）：C-tw-086-P03-01 sunset_window none None [REQUIRED/MAIN|provisional]; C-tw-086-P03-02 cloud_cover_low lte 55 % [REQUIRED/MAIN|provisional]; C-tw-086-P03-03 cloud_cover_mid_and_high between [20, 70] % [REQUIRED/MODIFIER|provisional]; C-tw-086-P03-04 precipitation lt 0.3 mm/h [REQUIRED/MAIN|provisional]; C-tw-086-P03-05 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-tw-086-P03-01，geometry_mode=unknown，elevation_deg=None）×太陽方位：日落方位 296.1°(夏至)→269.5°(分)→244.0°(冬至)——sun_azimuth_sector 格點帶無法以 view_azimuth 定心，契約目前無法定義。
- 條件服務映射：資料集 ['dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_low_percent', 'field:cloud_cover_mid_percent+cloud_cover_high_percent', 'field:precipitation_rate_mm_h', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；C-tw-086-P03-05 aod_550nm 的 model_binding 寫成 dataset:gfs_0p25|field:aerosol_optical_depth…——AOD 應綁 cams_global（其餘機會皆如此）；資料集名與欄位字尾亦不自洽。
- 判定：❌ 綁定資料集錯誤
- 修法建議：C-tw-086-P03-05 aod_550nm 的 model_binding 寫成 dataset:gfs_0p25|field:aerosol_optical_depth…——AOD 應綁 cams_global（其餘機會皆如此）；資料集名與欄位字尾亦不自洽。

### us-001-P01　大峽谷南緣・Mather Point 日出峽谷層次
- genre：overlook（template_version overlook-v0.2；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：大峽谷南緣・Mather Point 日出峽谷層次；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-us-001-P01-01 visibility gte 24 km [REQUIRED/MAIN|provisional]; C-us-001-P01-02 aod_550nm lte 0.4 [REQUIRED/MAIN|provisional]; C-us-001-P01-03 cloud_cover_low lte None % [REQUIRED/MAIN|provisional]; C-us-001-P01-04 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-us-001-P01-SR1 sunrise_time_window none None [REQUIRED/MAIN|None]
- 光向：view_azimuth=null（VR-us-001-P01-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_low_percent', 'field:precipitation_rate_mm_h', 'field:visibility_km', 'sunrise_time_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；C-us-001-P01-03 cloud_cover_low lte threshold=null（unit=%），rationale 明說「≤30%（owner 2026-10-26 修正）」——門檻值漏寫。對照同型 us-083-P01/us-059 應為 30。
- 判定：❌ threshold null
- 修法建議：C-us-001-P01-03 cloud_cover_low lte threshold=null（unit=%），rationale 明說「≤30%（owner 2026-10-26 修正）」——門檻值漏寫。對照同型 us-083-P01/us-059 應為 30。

### us-001-P02　大峽谷南緣・Desert View 夕照與Watchtower前景
- genre：sunset（template_version sunset-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：大峽谷南緣・Desert View 夕照與Watchtower前景；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-us-001-P02-01 sunset_window none None [REQUIRED/MAIN|provisional]; C-us-001-P02-02 cloud_cover_low lte 55 % [REQUIRED/MAIN|provisional]; C-us-001-P02-03 cloud_cover_mid_and_high between [20, 70] % [REQUIRED/MODIFIER|provisional]; C-us-001-P02-04 precipitation lt 0.3 mm/h [REQUIRED/MAIN|provisional]; C-us-001-P02-05 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-us-001-P02-01，geometry_mode=unknown，elevation_deg=None）×太陽方位：日落方位 299.5°(夏至)→269.4°(分)→240.6°(冬至)——sun_azimuth_sector 格點帶無法以 view_azimuth 定心，契約目前無法定義。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_low_percent', 'field:cloud_cover_mid_percent+cloud_cover_high_percent', 'field:precipitation_rate_mm_h', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### us-001-P03　大峽谷南緣・星空／銀河與峽谷或Watchtower前景
- genre：night_sky（template_version night_sky-v0.4；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：大峽谷南緣・星空／銀河與峽谷或Watchtower前景；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-us-001-P03-01 astronomical_darkness none None [REQUIRED/MAIN|provisional]; C-us-001-P03-02 moon_illumination_fraction lte 0.5 [REQUIRED/MAIN|provisional]; C-us-001-P03-03 cloud_cover_total lte 20 % [REQUIRED/MAIN|provisional]; C-us-001-P03-04 aod_550nm lte 0.3 [REQUIRED/MAIN|provisional]; C-us-001-P03-05 galactic_core_altitude gte 10 ° [REQUIRED/MAIN|provisional]; C-us-001-P03-06 moon_altitude lt 0 ° [REQUIRED/MAIN|provisional]; C-us-001-P03-07 moon_target_separation_deg gte 40 ° [REQUIRED/MAIN|provisional]; C-us-001-P03-08 moon_illuminance_proxy lte 0.15 [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-us-001-P03-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['astronomical_darkness', 'field:aerosol_optical_depth_550nm', 'field:cloud_cover_total_percent', 'galactic_core_altitude', 'moon_altitude', 'moon_illuminance_proxy']…
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### us-024-P01　Space Needle・Seattle Center地標外觀
- genre：overcast_soft（template_version overcast_soft-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：Space Needle・Seattle Center地標外觀；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-us-024-P01-02 precipitation lt 0.5 mm/h [REQUIRED/MAIN|approved]; C-us-024-P01-03 golden_hour_window none None [QUALITY/BONUS|provisional]; C-us-024-P01-04 aod_550nm lte 0.4 AOD [QUALITY/BONUS|provisional]; C-us-024-P01-OV1 cloud_cover_total gte 70 % [REQUIRED/MAIN|None]; C-us-024-P01-OV3 wind_speed_10m lt 5 m/s [QUALITY/BONUS|None]
- 光向：view_azimuth=null（VR-us-024-P01-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aod_550nm', 'field:cloud_cover_total_percent', 'field:precipitation_mm_h', 'field:wind_speed_10m_m_s', 'golden_hour_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### us-024-P02　Space Needle觀景台・Seattle 360度全景
- genre：city_night（template_version city_night-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：Space Needle觀景台・Seattle 360度全景；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-us-024-P02-01 cloud_cover_total lte 30 % [REQUIRED/MAIN|provisional]; C-us-024-P02-02 visibility gte 10 km [REQUIRED/MAIN|provisional]; C-us-024-P02-03 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-us-024-P02-04 aod_550nm lte 0.5 [REQUIRED/MODIFIER|provisional]; C-us-024-P02-05 city_night_window none None [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-us-024-P02-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['city_night_window', 'field:aerosol_optical_depth_550nm', 'field:cloud_cover_total_percent', 'field:precipitation_rate_mm_h', 'field:visibility_km']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### us-059-P01　Brooks Falls Platform・瀑布／Brooks River景觀
- genre：mountain_view（template_version mountain_view-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：Brooks Falls Platform・瀑布／Brooks River景觀；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-us-059-P01-01 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]; C-us-059-P01-02 cloud_cover_mid between [30, 60] % [REQUIRED/MAIN|provisional]; C-us-059-P01-03 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-us-059-P01-04 sunset_window none None [QUALITY/MODIFIER|provisional]; C-us-059-P01-LW1 light_window none None [REQUIRED/MAIN|None]
- 光向：view_azimuth=null（VR-us-059-P01-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_mid_percent', 'field:precipitation_rate_mm_h', 'light_window', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

### us-059-P02　Brooks Falls・棕熊捕鮭
- genre：mountain_view（template_version mountain_view-v0.1；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：Brooks Falls・棕熊捕鮭；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-us-059-P02-01 aod_550nm lte 0.6 [REQUIRED/MAIN|provisional]; C-us-059-P02-02 cloud_cover_mid between [30, 60] % [REQUIRED/MAIN|provisional]; C-us-059-P02-03 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-us-059-P02-04 sunset_window none None [QUALITY/MODIFIER|provisional]; C-us-059-P02-LW1 light_window none None [REQUIRED/MAIN|None]; C-us-059-P02-SS1 seasonal_state eq window_open [REQUIRED/MAIN|None]
- 光向：view_azimuth=null（VR-us-059-P02-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_mid_percent', 'field:precipitation_rate_mm_h', 'light_window', 'seasonal_state', 'sunset_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；主體為棕熊捕鮭（行為＋季節），套 mountain_view 模板（AOD/中雲/sunset 窗）；CL-DATA-12 已補 seasonal_state（7–9 月）與 light_window（高緯），判據合理，但模板與主體不匹配宜記為已知妥協。
- 判定：✅ 模板不匹配（已知妥協）
- 修法建議：主體為棕熊捕鮭（行為＋季節），套 mountain_view 模板（AOD/中雲/sunset 窗）；CL-DATA-12 已補 seasonal_state（7–9 月）與 light_window（高緯），判據合理，但模板與主體不匹配宜記為已知妥協。

### us-083-P01　Sunrise・日出光照 Mount Rainier＋Emmons Glacier
- genre：overlook（template_version overlook-v0.2；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：Sunrise・日出光照 Mount Rainier＋Emmons Glacier；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-us-083-P01-01 visibility gte 20 km [REQUIRED/MAIN|provisional]; C-us-083-P01-02 aod_550nm lte 0.4 [REQUIRED/MAIN|provisional]; C-us-083-P01-03 cloud_cover_low lte 30 % [REQUIRED/MAIN|provisional]; C-us-083-P01-04 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]; C-us-083-P01-SR1 sunrise_time_window none None [REQUIRED/MAIN|None]
- 光向：view_azimuth=null（VR-us-083-P01-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25', '未綁定']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_low_percent', 'field:precipitation_rate_mm_h', 'field:visibility_km', 'sunrise_time_window']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；主體含 Emmons Glacier 冰川語義，無冰川/雪況條件；SR1 日出窗已補（CL-DATA-12 batch h）正確。建議補季節性雪況代理。
- 判定：⚠ 雪況代理缺失
- 修法建議：主體含 Emmons Glacier 冰川語義，無冰川/雪況條件；SR1 日出窗已補（CL-DATA-12 batch h）正確。建議補季節性雪況代理。

### us-083-P02　Sunrise Point・Rainier＋Cascade Range 近360°山景
- genre：overlook（template_version overlook-v0.2；recommendation_policy_version=None；research_level=R0，gaps=RESEARCH_GAP,GEOMETRY_GAP）
- 主體：Sunrise Point・Rainier＋Cascade Range 近360°山景；claims=1（audit_status=['UNKNOWN']）
- 成立需求（REQUIRED 判據）：C-us-083-P02-01 visibility gte 24 km [REQUIRED/MAIN|provisional]; C-us-083-P02-02 aod_550nm lte 0.4 [REQUIRED/MAIN|provisional]; C-us-083-P02-03 cloud_cover_low lte 30 % [REQUIRED/MAIN|provisional]; C-us-083-P02-04 precipitation lt 0.2 mm/h [REQUIRED/MAIN|provisional]
- 光向：view_azimuth=null（VR-us-083-P02-01，geometry_mode=unknown，elevation_deg=None）；委託書無法程式化給出構圖光向指引。
- 條件服務映射：資料集 ['dataset:cams_global', 'dataset:gfs_0p25']；欄位/代理：['field:aerosol_optical_depth_550nm', 'field:cloud_cover_low_percent', 'field:precipitation_rate_mm_h', 'field:visibility_km']
- 缺口：GEOMETRY_GAP（view_azimuth/geometry_mode unknown）為通案；條件契約與模板一致。
- 判定：✅ 大體符合契約
- 修法建議：補 view_azimuth（由 camera→target 幾何推導）並將 geometry_mode unknown 收斂為 known。

## 前次回收與本輪修正建議（前 10 筆）

1. tw-040-P04：LCL 門檻複驗——觀點高度 3,952 m 實為玉山主峰值，排雲山莊約 3,468 m，LCL 門檻應由 3,752 m 修正為約 3,268 m（偏低 484 m，誤判方向：把雲頂高於視線判為成立）。
2. us-001-P01：C-us-001-P01-03 cloud_cover_low threshold=null 補 30（rationale 與同型 us-083-P01 一致）。
3. tw-035-P02：裂雲窗代理由 cloud_cover_total ≤50% 改為 low lte ＋ mid/high 20–70 分層（或引入碎雲指標），避免連續雲幕通過／碎積雲否決的矛盾。
4. tw-001-P02／tw-019-P04／tw-024-P02／tw-040-P04：LCL 溯源補 DEM 資料集、版本、不確定度與 −200 m 餘量依據；altitude_m 由 null 補為 DEM 值。
5. 全 65 機會：view_azimuth=null——由 camera→target 幾何推導觀察方位；sunset/sunrise/golden_hour 的 sun_azimuth_sector 以月別太陽方位定心。
6. 淡水光向季變（tw-003-P01、tw-005-P01、tw-086-P03 等）：日落方位冬 244°→夏 296°（52° 擺幅），太陽方位扇形格點帶需月別化或加季節標註，避免全年固定扇形。
7. 大屯山秋芒（tw-001-P01）：補 seasonal_state window_open（10–11 月）或拆出第二機會，分離「一般夕照」與「秋芒」成立語義。
8. 雪況代理（tw-019-P06、tw-040-P03、us-083-P01）：雪覆/冰川主體缺雪況條件——補 seasonal_state 或溫度/降水史代理（provisional），否則無雪季全數通過。
9. tw-086-P03：C-tw-086-P03-05 AOD 綁定資料集由 gfs_0p25 改 cams_global（欄位名同步對齊 metric-vocabulary）。
10. tw-019-P04：LCL 綁定 cwa_wrf3 與同型 gfs_0p25 機會不一致，統一至 cwa_wrf3（SHORT_HQ）並記錄觀點高度溯源。

## 光向資料結論

- 65/65 機會 observation_relations.azimuth_deg 均為 null（elevation_deg、distance_m 同 null，geometry_mode=unknown）——光向資料鏈目前完全缺位，委託書無法程式化產出光向指引；sunset/golden_hour 模板 T2 所需的 sun_azimuth_sector 參數無法定心。
- 太陽方位季變是實質風險：台灣緯度日落方位季節擺幅約 52°（冬 244°↔夏 296°）、日出約 51°（冬 115°↔夏 64°）；固定扇形半年後會把「太陽方向格點」取到錯誤側。建議：view_azimuth 補齊 → sector 由月別太陽方位計算 → 契約儲存月別扇形或 seasonal 標註。
- 特殊語義已由既有修法誠實覆蓋：tw-086-P01 霧景能見度反語義、us-001 系 GFS 能見度 24 km 上限鈍化、高緯 light_window（us-059-P02）——rationale 標註完整，列為通過。