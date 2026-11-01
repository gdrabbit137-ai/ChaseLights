import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync, existsSync, readdirSync} from "node:fs";
import {dirname, join} from "node:path";
import {fileURLToPath} from "node:url";
import {displayLocalizedName, localized} from "../model.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..", "..", "..");

// CL-UI-07: the four exact internal-state markers the pre-fix W2 generator
// baked into user-visible display strings. The shipped UI bundle must never
// contain any of them (defense in depth for regenerated data).
const MARKERS = [
  " (provisional English title, pending review)",
  "（暫定日本語タイトル、レビュー待ち）",
  " (zh-TW source values retained pending translation).",
  "（zh-TW原文のまま、翻訳待ち）。",
];

const shipped = [
  "apps/web-v2/catalog.v2.json",
  "apps/web-v2/browse-index.v2.json",
  "apps/web-v2/opportunity-contracts.json",
  "apps/web-v2/evaluations-latest.json",
];

test("shipped UI bundles contain no provisional/pending title markers", () => {
  const files = [...shipped];
  const details = join(root, "apps/web-v2/evaluations-details");
  if (existsSync(details)) {
    for (const f of readdirSync(details)) {
      if (f.endsWith(".json")) files.push(join("apps/web-v2/evaluations-details", f));
    }
  }
  const found = [];
  for (const rel of files) {
    const p = join(root, rel);
    if (!existsSync(p)) continue;
    const text = readFileSync(p, "utf8");
    for (const marker of MARKERS) {
      if (text.includes(marker)) found.push({file: rel, marker});
    }
  }
  assert.deepEqual(found, [],
    "UI-visible generated artifacts must never carry provisional/pending internal-state markers (CL-UI-07)");
});

test("name display falls back to zh-TW and never renders a provisional marker", () => {
  // Unreviewed English title as it was baked by the pre-fix generator.
  const tainted = {
    name_i18n: {
      "zh-TW": "測試地點",
      "en": "測試地點 (provisional English title, pending review)",
      "ja": "測試地點（暫定日本語タイトル、レビュー待ち）",
    },
  };
  // en/ja users see the neutral zh-TW source name, never the internal marker.
  assert.equal(localized(tainted, "name", "en"), "測試地點");
  assert.equal(localized(tainted, "name", "ja"), "測試地點");
  // Raw name_i18n dicts (topic labels) get the same treatment.
  assert.equal(displayLocalizedName(tainted.name_i18n, "en"), "測試地點");
  assert.equal(displayLocalizedName(tainted.name_i18n, "ja"), "測試地點");
  assert.equal(displayLocalizedName(tainted.name_i18n, "zh-TW"), "測試地點");
});

test("name display falls back to zh-TW when the reviewed title is absent", () => {
  const missing = {name_i18n: {"zh-TW": "青青草原", "en": "", "ja": ""}};
  assert.equal(localized(missing, "name", "en"), "青青草原");
  assert.equal(localized(missing, "name", "ja"), "青青草原");
  assert.equal(displayLocalizedName(missing.name_i18n, "en"), "青青草原");
  // Non-name fields keep the no-silent-fallback rule (honest missing state).
  const desc = {description_i18n: {"zh-TW": "內容", "en": "", "ja": ""}};
  assert.equal(localized(desc, "description", "en"), null);
});

test("reviewed English titles still win over the zh-TW fallback", () => {
  const reviewed = {name_i18n: {"zh-TW": "中山林道", "en": "Zhonglin Forest Road", "ja": ""}};
  assert.equal(localized(reviewed, "name", "en"), "Zhonglin Forest Road");
  assert.equal(localized(reviewed, "name", "ja"), "中山林道");
});

test("description pending-translation markers never reach the UI", () => {
  const stale = {
    description_i18n: {
      "zh-TW": "內容",
      "en": "內容 (V1 best time: 全年 (zh-TW source values retained pending translation). V1 migration skeleton; content to be refined in round 2.)",
      "ja": "內容（V1ベスト時間帯: 全年（zh-TW原文のまま、翻訳待ち）。V1移行スケルトン。）",
    },
  };
  assert.equal(localized(stale, "description", "en"), null);
  assert.equal(localized(stale, "description", "ja"), null);
});
