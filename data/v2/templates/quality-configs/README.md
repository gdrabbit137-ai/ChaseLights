# QUALITY 引擎 v2 規則 schema（CL-DATA-79 Phase 2）

施工規格：`data/v2/audits/spec-quality-engine.md` §3（schema）＋§4（引擎數學）＋§5（10 題材權重表）。
引擎實作：`packages/core-v2/tools/quality_engine.py`。

## 地位（並存，不遷移）

- 本目錄 `*.json` 是 **v2 quality-config**（每題材一份，`tag` 鍵唯一），由 v2 QUALITY 引擎讀取。
- **官方機會契約（`data/v2/opportunities/*.json`）暫不遷移**：現行 contract 評估路徑完全不動（引擎旁路），
  Phase 3 才把官方契約切換到 v2 schema。
- `snowfall_cm_h` 為規格 §2 標準鍵；Phase 1 ETL 的原始 cell 名 `snowfall` 在 Phase 3 接線時做別名。

## Schema（§3）

```json
{
  "tag": "astrophotography",
  "schema": "quality-v2",
  "version": "1.0",
  "status": "defined",
  "source": "<provenance>",
  "windows": {
    "time_of_day": ["astronomical_darkness"],
    "seasonal": null
  },
  "conditions": {
    "required": [ {"metric": "...", "op": "lt|lte|gt|gte|eq|between", "value": 0},
                  {"any_of": [...]}, {"all_of": [...]} ],
    "quality":  [ {"metric": "...", "weight": 3.0, "abcd": [a, b, c, d],
                   "bonus_window": "golden_hour"} ]
  }
}
```

- `windows.seasonal`：`null`（全年）或 `[{start:"12-15", end:"02-25"}]`（支援跨年）；題材模板層為 null，
  每地點實例化時由契約季節窗填入。
- `quality[].abcd`：四元組 `[a,b,c,d]`，`[b,c]` 理想區（q=1）、`[a,d]` 可接受區（斜坡線性內插、界外 0）；
  `"inf"` 支援右肩型。也可寫分離式 `ideal:[b,c]` ＋ `acceptable:[a,d]`。
- `bonus_window`：`*_match` 型指標由引擎以 `active_time_windows` 推導（1/0），不必放進 metrics。
- 必填鍵驗證：`opportunity_id / place_id / tag / windows / conditions{required,quality}`（引擎載入時檢查）。

## 引擎語意（§4）

1. **Gatekeeper G(t)**：time_of_day ∧ seasonal ∧ required（巢狀 any_of/all_of）；缺值 = fail（fail-closed）。
   G(t)=0 → `eligible=false`、`S_quality=0`、tier=`ineligible`。
2. **梯形隸屬 q_i(x)**：§4.2 五段公式；月光覆寫——astrophotography 題材在 `moon_altitude_deg < 0` 時
   `q_moon = 1.0`（月在地平線下，月光無罰分）。
3. **S_quality = 100 × Σw·q / Σw**；無 quality 規則 → 預設 `75.0`。
4. **分級**：`recommend ≥75`、`good 45–75`、`marginal <45`；`S_rank = AGLI^0.35 × S_quality^0.65`。
   Quality 指標缺值 → q=0（不能證明品質），與 required 的 propagate_unknown 不同。
