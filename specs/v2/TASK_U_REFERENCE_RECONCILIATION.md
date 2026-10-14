# Task U attachment — bounded Task W reconciliation

Owner W1. Follow-up to Draft #489 after the user supplied the original ChatGPT attachment. This is a reference reconciliation for 02A/02B/02C, **not** a new 40-feature inventory or implementation of the attachment's other task prompts. Current user scope, main/AGENTS and applicable specifications still govern. No attached instruction authorizes W2/W3/W4/W5 edits, merge or deployment.

## Provenance and exactly what was read

Attachment: `ChaseLights_Task_U_UI_UX_Research_and_Roadmap(1).zip` (533145 bytes).
ZIP SHA-256: `e47c50ff2ee148526ee133e5f45f27327235241058600b0cc5f0fed5a739efcc`.

| Original member | SHA-256 | Read scope |
| --- | --- | --- |
| V2_FEATURE_GAP_MATRIX.xlsx | `4001018f019fbb9731dcdc7b0e6c595c4826244c8ee0f6d2665f8d5ab22ec080` | Opened actual workbook with openpyxl; worksheet 功能差距, rows 12–19 = U-F05–U-F12. No claim of checking all 40 rows. |
| V2_W4_CODEX_ROADMAP.md | `dd23db8f525572fdfc062020bafe1cca40315137c0786f54b21628b5699d57a9` | Read Roadmap; reconciliation limited to 02A/B/C and ownership/dependency context. |
| V2_UI_UX_PRODUCT_SPEC.md | `13c7b669730a42c893d4beed9fd6635ff849931bed00043ad66e683885e0a009` | Relevant region/topic/search/sort, date, state and W1/W2 handoff sections. |
| V1_V2_FEATURE_INVENTORY.md | `ab155a0e8ae24dfda3a28696a62961e8440d99bed1d1c0aca8eecfb627a85e4c` | Existing U-F05–U-F12 only; no re-audit of its Legacy evidence links. |
| V1_HISTORICAL_UX_ISSUES.md | `b4e3d4540c9e9b1f75c456ece9e808a82d8e862da2f39aa879b3799cca856923` | H03/04/05/07/26/28 relevant to admin/default order/date/favorites/races only. |

The archive also has README, Task01 prompt and historical evidence. Those historical PASS/FAIL numbers are **not** this Task W's test results. The attachment's historical base `8bd2256…` / final main `77ecfb8…` is not current main. Follow-up observed current main `500ec3a76b5f77a0752ecdca5cc1b12fa63d223d`; its difference from Task W base remains two generated WeatherGrid files only, with AGENTS/R4.2/owner specs unchanged. #489 was read back open/Draft at initial HEAD `3e5a6007c57e704dfec401976f64da74b8321faf` before updating the same branch.

## Targeted mapping and resulting clarifications

| Original reference | W1 contract / action |
| --- | --- |
| U-F05 (row12), 02B | Added explicit TODAY/TOMORROW/DAY_AFTER_TOMORROW normalization from frozen UTC now per verified Place zone; mixed-place dates stay explicit; provider daily lookup uses date keys, never array positions. Existing UNKNOWN/DST/date-generation gates remain. |
| U-F06 (row13), 02B / later 04 | Existing RESEARCH_ONLY/WINDOW/RAW_ONLY/EVALUATION separation and local interval/time-awareness cover the shared contract. Timeline UI and real recommendation integration remain later W3/W4 tasks. |
| U-F07 (row14), 02C | Existing stable taxonomy, same-dimension OR/cross-dimension AND and researched-only binding retained. No inferred subjects or new W2 assignments. |
| U-F08 (row15), 02A | Added complete-picker acceptance TW22/JP47/US50+DC, Kinmen/Lienchiang labels, registered-but-uncatalogued state. This counts administrative options, never requires fake Places or hardcodes the schema to existing seven Places. |
| U-F09 (row16), 02A / W4 | Added immediate selection, no hidden Apply state and close/focus/scroll interaction handoff. W1 does not implement the mobile sheet or claim browser acceptance. |
| U-F10 (row17), 02A | Expanded search scope to sourced registry names/codes/IDs; added same-name disambiguation and per-dimension clear behavior. Added administrative-search acceptance truth table. |
| U-F11 (row18), 02C | Corrected initial/fallback order from NAME to REGION ASC; retained explicit NAME sorting, comparability gates, unknown-distance retention and permission request only after selecting distance. |
| U-F12 (row19), 02C | Existing versioned V2-only favorites/local storage and unknown-ID handling retained. Filter/date/unit persistence beyond the present favorite+locale envelope remains future versioned work; the inventory's Legacy capability description does not silently expand Task W. |

The six schema shapes need no change: they already support these fields and explicit sort/date values. Two additional W1 acceptance tests cover sourced administrative search with stable IDs and per-Place relative dates/date-key selection from shuffled arrays. Default/fallback region order and complete registry contents require W4/W2 implementation tests, as listed in the updated handoff; no production code or fabricated registry was added.

Remaining limits: no full 40-row comparison, no re-verification of historical Legacy claims, no human translation/geographic/timezone/evidence approval, and no W4 browser or W5 integration pass is inferred. The original “not yet received” limitation is retained only as history of the first commit; it is no longer a claim about attachment access now.
