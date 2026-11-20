# CL-DATA-81 audit — 海景日出補能見度 / 星空契約月光去重 / 弱點清單同步 / jp-002–022 題材名翻譯

Ticket: task/CL-DATA-81（base: origin/main b9aa52a0e）
Date: 2026-11-20

## Stage A — contract edits (commits 1206636cb + revert 6a75e76da)

1. **海景日出補能見度**（jp-008-P01 松島双観山 / tw-072-P01 南雅 / tw-075-P01 外澳）：
   各新增 REQUIRED `visibility >= 15 km`（gfs_0p25|visibility_km|MID）＋ REQUIRED
   `aod_550nm <= 0.4`（cams_global|aerosol_optical_depth_550nm|AEROSOL），
   condition_tier MAIN、trilingual rationale；與龍磐（tw-076-P01）／諏訪湖同族
   「海霧/霧霾攔截」對齊（龍磐既有 vis≥15；AOD≤0.4 沿用遠景地景已審門檻家族）。
   同步寫入 conditions_v2.required（schema v2.2.0）。
2. **星空契約月光去重（34 筆）**：根因確認＝CL-DATA-75 Phase 0（4ac19a2c6）為實作
   owner §1.2 第二軌（月照≤0.25）時，未刪除星空模板遺留的基層閘（月照≤0.5 REQUIRED，
   「半月以下亮星可拍」分層語意），遷移/Phase-0 雙條目並存 → 顯示層月照重複兩次。
   處置：契約層刪除 ≤0.5 條目（conditions＋conditions_v2.required）。月光閘＝
   any_of（月下 OR（月照≤0.25 ∧ 分離≥45°））；評估器 M2/M3 交替語意不變——
   月下時月照條件直接放行、第二軌不適用；月升時 ≤0.25∧≥45° 判定（原 ≤0.5 閘在
   owner 規則下完全被支配：月升 0.25–0.5 本就應否決，月下本就放行）。
   藍眼淚（tw-121~124）的 ≤0.5 月照閘為刻意分層（rationale 註明），不動。
3. **弱點清單同步**：data/v2/audits/discovery/catalog-scoring.json 的
   low_weather_light 8 筆全數加註 disposition（CL-DATA-77 裁定對照）：
   jp-070/081/083/091/tw-151/tw-224＝已收緊（評估層 river_flow_state 派生）；
   tw-082-P01＝過期誤報結案（CL-DATA-72 batch A 已派生水面狀態）；
   us-111-P01＝已裁撤（CL-DATA-76）。僅加註不重算分數（審計快照）。
4. **jp-002–jp-022 題材名 en/ja 翻譯**：本票先做了 20 筆（web 查證地景後翻譯），
   owner 範圍凍結裁定（2026-11-20）後自本票移除——revert commit 6a75e76da 恢復原
   zh-TW 複製字串與 revision，改為獨立純 metadata 票（只跑 schema 驗證、跳過氣象
   全量重算）。查證素材留存於 git 歷史（stage A commit 1206636cb）。

## Stage B — re-pin + regen chain (commits …)

- 54 筆變更契約 schema validate PASS（specs/v2/tests/validate_contract.py）。
- repin_canonical：54 canonical records re-pin（commit_sha=stage A head）。
- research_index build --git-provenance --w1-root specs/v2：初跑 FAIL（task-x fixtures
  留存舊 index_revision 678da9b1…）→ 重錨 browse-query/date-query fixtures 至
  91db81e9… → build PASS（canonical/index/source/reference consistency）。
- build_web_catalog（459 places / 720 opportunities）→ make_display_contracts →
  sync_integration_sources SYNCED。

## Stage C — scoped evaluations regen（37 places，禁全量）

- cl_data_81_eval_regen.py：BEFORE snapshot（100 opportunities）→
  `--only-place-id × --forecast-hours 168`（temp out/archive/details，不覆寫 published）
  → AFTER → splice 回 evaluations-latest + per-place details shards →
  verdict comparison → data/v2/audits/cl-data-81-verdict-comparison.txt。
- 預期翻轉方向：星空契約在「月升、月照 0.25–0.5、分離≥45°」的時段由可拍轉否決
  （owner §1.2 收緊）；三筆海景日出在 AOD>0.4 或能見度<15km 時段轉否決。

## Stage D — export layer（試算表）

- export_catalog_xlsx.py：月光 any_of 雙軌不再平鋪三行 REQUIRED——
  偵測（月高度<0）＋（分離≥45°）＋（月照≤0.25）三件組 → 單行
  「月光雙軌（any_of）｜月下 OR（月照≤0.25 ∧ 分離≥45°）」，rationale 三段合併保留。
- exports/catalog_20261120.xlsx 重推：34 筆星空題材各一單行（台16/日5/美13）。
