// CL-APP-09 tests: 自訂題材 on official spots — V1 shell client (self-contained
// asset assets/subject-sets.js + subject-sets.css, NO app.js edits).
// Static contract + extracted-function tests (cl-ui harness pattern):
//   registration: index.html carries the stamped css+js tags
//   i18n: every key exists in ALL THREE dictionaries, tri-lingual, no
//         internal/ticket wording in any user-visible string
//   duplicates: duplicate names are NOT blocked (no uniqueness gate in copy)
//   caps: concrete numbers in the cap copy + gray upgrade card class
//   fork: 自訂 badge / diff view / 重設回官方 / 官方已更新可同步
//   ±30%: warn-not-block (advisory copy + diff flag)
//   months multi-select: 12 chips in the editor
//   card ⋯: portal menu fixed-position (never clipped by card overflow)
//   read-time eval: the panel reads /subject_sets/eval (shared grid)
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "..");
const jsSrc = readFileSync(join(root, "assets", "subject-sets.js"), "utf8");
const listJsSrc = readFileSync(join(root, "assets", "subject-sets-list.js"), "utf8");
const appJsSrc = readFileSync(join(root, "assets", "app.js"), "utf8");
const cssSrc = readFileSync(join(root, "assets", "subject-sets.css"), "utf8");
const html = readFileSync(join(root, "index.html"), "utf8");

function grab(src, start, end) {
  const i = src.indexOf(start);
  assert.ok(i >= 0, "slice start not found: " + start);
  const j = src.indexOf(end, i);
  assert.ok(j > i, "slice end not found: " + end);
  return src.slice(i, j);
}

// ---------------------------------------------------------------- registration
test("index.html registers subject-sets css+js+list-loader with the clapp09b stamp", () => {
  assert.match(html, /assets\/subject-sets\.css\?v=clapp09b/);
  assert.match(html, /<script src="\.\/assets\/subject-sets\.js\?v=clapp09b"><\/script>/);
  // 追加2②: the card-list lazy loader rides the same page
  assert.match(html, /<script src="\.\/assets\/subject-sets-list\.js\?v=clapp09b"><\/script>/);
});

test("no app.js internals reach-in (asset stays self-contained)", () => {
  // the module must not reach into app.js internals (no app.js marker imports)
  assert.doesNotMatch(jsSrc, /assets\/app\.js/);
  assert.doesNotMatch(jsSrc, /window\.ChaseLightsCustomPlaces/); // no cross-module reach-in
});

// ---------------------------------------------------------------- lazy loader (追加2②)
test("card-list lazy loader: ONE batch endpoint, visible-range first, transient-safe", () => {
  assert.match(listJsSrc, /api\/v1\/subject_sets\/eval_batch/); // the ONE batch endpoint
  assert.match(listJsSrc, /IntersectionObserver/); // visible range first
  assert.match(listJsSrc, /backoffMs \*= 2/); // 429/5xx exponential backoff (house rule)
  assert.match(listJsSrc, /next_cursor/); // server-driven pagination
  // app.js hands over the ids + resets on every re-render (one call site)
  assert.match(appJsSrc, /window\.CLSubjectSetsList\.reset\(\)/);
  assert.match(appJsSrc, /window\.CLSubjectSetsList\.init\(/);
});

// ---------------------------------------------------------------- i18n
test("every T key exists in zh-TW, en AND ja", () => {
  const keys = [...jsSrc.matchAll(/^\s{6}([a-z0-9_]+):\s*'[^']*'/gm)].map((m) => m[1]);
  assert.ok(keys.length > 30, "expected a substantial tri-lingual pack, got " + keys.length);
  for (const lang of ["'zh-TW'", "en", "ja"]) {
    for (const k of keys) {
      const re = new RegExp("\\n\\s*" + lang + ":\\s*\\{[\\s\\S]*?\\n\\s*" + k + ":");
      assert.match(jsSrc, re, lang + " missing key " + k);
    }
  }
});

test("no internal vocabulary / ticket IDs in user-visible copy", () => {
  // every string literal inside the T pack must be clean
  const packStart = jsSrc.indexOf("var T = {");
  const packEnd = jsSrc.indexOf("var state = {");
  const pack = jsSrc.slice(packStart, packEnd);
  assert.doesNotMatch(pack, /CL-[A-Z]+-\d+/);
  assert.doesNotMatch(pack, /已上線|同規格|引擎|灰度|flag/i);
  // ja pack: no simplified-han residue (题材 is simplified; 題材 is correct)
  const jaStart = pack.indexOf("ja: {");
  const jaPack = pack.slice(jaStart);
  assert.doesNotMatch(jaPack, /题材|适合时间数/);
});

// ---------------------------------------------------------------- duplicates
test("duplicate names are allowed — no uniqueness gate exists", () => {
  // the T pack (user-visible copy) must never claim uniqueness or block names
  const pack = grab(jsSrc, "var T = {", "var state = {");
  assert.doesNotMatch(pack, /已存在|already exists|duplicate name/i);
  // naming hint never claims uniqueness
  assert.match(jsSrc, /ed_name_ph/);
});

// ---------------------------------------------------------------- caps (FINAL ruling)
test("cap copy carries CONCRETE numbers (5 per place all tiers / free TOTAL 5 / daily add 5)", () => {
  assert.match(jsSrc, /此景點已達 5 組上限/);
  // the OLD numbers must be gone, not merely unused
  assert.doesNotMatch(jsSrc, /20 組上限|限 1 組試用|每個景點限 1 組/);
  assert.match(jsSrc, /全站總量 5 組/);   // free TOTAL (server copy mirror + cap_free)
  assert.match(jsSrc, /每日新增 5 組|每日上限 5 組/); // daily add throttle
  // gray upgrade card class exists in css (owner spec §3 灰度樣式)
  assert.match(cssSrc, /\.cl-ss-upgrade\{/);
  assert.match(jsSrc, /cl-ss-upgrade/);
  // caps null = owner/unlimited — the JSON-safe convention (never Infinity on the wire)
  assert.match(jsSrc, /caps\.place === null/);
});

test("quota line renders the real counts (concrete numbers, not vague)", () => {
  assert.match(jsSrc, /quota_fmt: '此景點 \{p\}\/\{pc\} 組'/);
  // free tier shows the TOTAL budget + the daily-add cap explicitly
  assert.match(jsSrc, /quota_free: '此景點 \{p\}\/\{pc\} 組 · 全站 \{t\}\/\{tc\} 組 · 每日新增 \{d\} 組'/);
  // paid never sees a stale total-cap suffix
  assert.match(jsSrc, /level === 'free' && caps\.total != null/);
});

// ---------------------------------------------------------------- fork semantics
test("自訂 badge + tri-lingual badge pack", () => {
  assert.match(jsSrc, /badge: '自訂', stale_badge: '官方已更新可同步'/);
  assert.match(jsSrc, /badge: 'Custom', stale_badge: 'Official template updated — sync available'/);
  assert.match(jsSrc, /badge: '自作', stale_badge: '公式テンプレ更新あり・同期可能'/);
  assert.match(cssSrc, /\.cl-ss-badge\{/);
});

test("重設回官方 + 同步官方更新 actions exist (fork reset + sync)", () => {
  assert.match(jsSrc, /reset_btn: '重設回官方', sync_btn: '同步官方更新'/);
  assert.match(jsSrc, /data-ss-act="reset"/);
  assert.match(jsSrc, /data-ss-act="sync"/);
  assert.match(jsSrc, /reset_to_official: true/);
});

test("diff view vs official snapshot (fork diff rows)", () => {
  assert.match(jsSrc, /diff_official: '官方', diff_mine: '此組'/);
  assert.match(cssSrc, /\.cl-ss-diff-row\{/);
});

// ---------------------------------------------------------------- ±30%
test("±30% is advisory only — warn line rendered, submit never blocked on it", () => {
  assert.match(jsSrc, /超出官方門檻 ±30%（僅提示，不阻擋）/);
  assert.match(jsSrc, /warn: pct !== null && pct > 30/);
  assert.match(cssSrc, /\.cl-ss-warn-line\{/);
});

test("extracted diffRows computes ±30% against the official snapshot", () => {
  const src = grab(jsSrc, "var CC_LABELS = {", "// ───────────────────────── shared ⋯ menu");
  const { diffRows } = new Function(src + "\nreturn { diffRows };")();
  // within ±30% → a row with warn=false (advisory), not a refusal
  const ok = diffRows({ visibility_min_km: 11 }, { visibility_min_km: 10 });
  assert.equal(ok.length, 1);
  assert.equal(ok[0].warn, false);
  const warn = diffRows({ visibility_min_km: 14 }, { visibility_min_km: 10 });
  assert.equal(warn.length, 1);
  assert.equal(warn[0].metric, "visibility_min_km");
  assert.equal(warn[0].warn, true);
  // no official snapshot → no diff at all (built from scratch)
  assert.deepEqual(diffRows({ wind_max_ms: 2 }, {}), []);
});

// ---------------------------------------------------------------- months
test("editor carries the 12-chip 適用月份 multi-select", () => {
  const src = grab(jsSrc, "function monthsHtml(", "function semanticValue(");
  const { monthsHtml } = new Function(src + "\nreturn { monthsHtml };")();
  const html12 = monthsHtml([4, 11]);
  assert.equal((html12.match(/type="checkbox"/g) || []).length, 12);
  assert.match(html12, /value="4" checked/);
  assert.match(html12, /value="11" checked/);
  assert.match(html12, /value="5"(?![^>]*checked)/);
});

// ---------------------------------------------------------------- eval / strip
test("panel reads the read-time eval endpoint (shared grid, zero extra API)", () => {
  assert.match(jsSrc, /API \+ '\/eval\?place_id='/);
  assert.match(jsSrc, /'\/api\/v1\/subject_sets'/);
});

test("extracted mergeHours compresses consecutive half-hours like the official strip", () => {
  const src = grab(jsSrc, "function mergeHours(", "function dayHtml(");
  const { mergeHours } = new Function(src + "\nreturn { mergeHours };")();
  assert.equal(mergeHours(["06:00", "06:30", "07:00", "09:00"]), "06:00–07:00 09:00");
  assert.equal(mergeHours(["05:10"]), "05:10");
  assert.equal(mergeHours([]), "");
});

test("custom set rows reuse the OFFICIAL v2-day strip anatomy", () => {
  assert.match(jsSrc, /class="v2-day '/);
  assert.match(jsSrc, /v2-badge '/);
  assert.match(jsSrc, /v2-day-label/);
  assert.match(jsSrc, /v2-hours/);
});

// ---------------------------------------------------------------- card ⋯ menu
test("official cards gain a ⋯ portal menu with 加自訂題材 (44px targets, fixed pos)", () => {
  assert.match(jsSrc, /className = 'cl-ss-more'/);
  assert.match(cssSrc, /\.cl-ss-menu\{position:fixed/);
  assert.match(jsSrc, /data-ss-menu-item="add"/);
  assert.match(jsSrc, /add_btn: '＋ 加自訂題材'/);
  // portal to body, never inside the card (overflow clipping)
  assert.match(jsSrc, /document\.body\.appendChild\(m\)/);
});

// ---------------------------------------------------------------- auth / fail-closed
test("signed-out state is honest; 403 surfaces the worker's concrete message", () => {
  assert.match(jsSrc, /login_note: '登入後可在此建立自訂題材'/);
  assert.match(jsSrc, /memberMsg\(r\.body && r\.body\.message\)/);
  assert.match(jsSrc, /auth\/refresh/); // silent refresh before signing out
});

test("gray identity: the section never borrows ✓○✗ semantic colors", () => {
  // token-only colors, no hex literals outside comments
  assert.doesNotMatch(cssSrc.replace(/\/\*[\s\S]*?\*\//g, ""), /#[0-9a-fA-F]{3,8}\b/);
});
