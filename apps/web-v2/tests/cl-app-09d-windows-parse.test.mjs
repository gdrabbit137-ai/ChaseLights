// CL-APP-09 補丁 2 (patch-2): AI-parse repair + 三處表單修正 + anchor/multi-segment
// windows. Source-assertion suite (same harness family as cl-app-09-subject-sets).
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "..");
const read = (p) => readFileSync(`${root}/${p}`, "utf8");
const html = read("index.html");
const remindersHtml = read("reminders.html");
const subjectSets = read("assets/subject-sets.js");
const subjectLib = read("assets/subject-sets-library.js");
const customPlaces = read("assets/custom-places.js");
const subjectList = read("assets/subject-sets-list.js");

// ---------------------------------------------------------------- registration
test("patch-2: cache-bust stamps bumped for every touched asset (per-file rule)", () => {
  assert.match(html, /assets\/custom-places\.js\?v=clapp08c/);
  assert.match(html, /assets\/subject-sets\.js\?v=clapp09d/);
  assert.doesNotMatch(html, /assets\/custom-places\.js\?v=clapp08b/);
  assert.doesNotMatch(html, /assets\/subject-sets\.js\?v=clapp09c/);
  // custom-places.css untouched → keeps its stamp (never bump what you did not change)
  assert.match(html, /assets\/custom-places\.css\?v=clapp08b/);
  assert.match(remindersHtml, /assets\/subject-sets-library\.js\?v=clapp09d/);
  assert.match(subjectList, /追加2/);
});

// ---------------------------------------------------------------- item ③ 不在乎
test("patch-2 ③: every 雲量下拉 carries the 不在乎/any option (= 不帶雲量條件) in three languages", () => {
  for (const [name, src] of [["subject-sets.js", subjectSets], ["subject-sets-library.js", subjectLib]]) {
    const cloudBlock = src.slice(src.indexOf("cloud: {"), src.indexOf("fog: {"));
    assert.match(cloudBlock, /\['any', '不在乎', null\]/, `${name} zh-TW`);
    assert.match(cloudBlock, /\['any', "Don't care", null\]/, `${name} en`);
    assert.match(cloudBlock, /\['any', 'こだわらない', null\]/, `${name} ja`);
    assert.doesNotMatch(cloudBlock, /'any', '不限', null/, `${name}: the old 不限 label is gone`);
  }
  const cpCloud = customPlaces.slice(customPlaces.indexOf("cloud: {"), customPlaces.indexOf("fog: {"));
  assert.match(cpCloud, /\['any', '不在乎', '不帶雲量條件'\]/);
  assert.match(cpCloud, /\['any', "Don't care", 'no cloud condition'\]/);
  assert.match(cpCloud, /\['any', 'こだわらない', '雲の条件なし'\]/);
  assert.doesNotMatch(cpCloud, /多雲也行/, "the ambiguous 多雲也行 label is retired");
});

// ---------------------------------------------------------------- item ② 範例句
test("patch-2 ②: AI example sentences speak in a landscape photographer's voice (tri-lingual, placeholder + help)", () => {
  assert.match(customPlaces, /ai_ph: '例如：清晨六點前要有雲海，不要下雨，風要小，能見度要好'/);
  assert.match(customPlaces, /ai_ph: 'e\.g\. cloud sea before 06:00, no rain, light wind, good visibility'/);
  assert.match(customPlaces, /ai_ph: '例：6時までに雲海。雨は嫌。風は弱め。視程は良い'/);
  assert.match(customPlaces, /ai_hint: '用一句話描述你要的拍攝條件（AI 只翻譯成條件，不判斷好壞）'/);
  assert.match(customPlaces, /ai_hint: 'Describe the shot you want in one sentence \(the AI only translates it into conditions — it never judges\)'/);
  assert.match(customPlaces, /ai_hint: '撮りたい条件を一文で説明（AIは条件への翻訳のみ・良し悪しは判断しない）'/);
});

// ---------------------------------------------------------------- item ④ 按鈕位置
test("patch-2 ④: 複製官方題材 renders BELOW the AI parse block and ABOVE the manual condition options", () => {
  const formStart = customPlaces.indexOf("function themeFormModal(place, theme) {");
  const form = customPlaces.slice(formStart, customPlaces.indexOf("function delModal"));
  const aiPos = form.indexOf("(aiEnabled ? aiParseBlock() : '')");
  const copyPos = form.indexOf("id=\"cl-cp-cc-genre\"");
  const cloudPos = form.indexOf("semSel('cloud', t().sem_cloud)");
  assert.ok(aiPos >= 0 && copyPos > aiPos, "copy-genre comes after the AI parse block");
  assert.ok(copyPos < cloudPos, "copy-genre comes before 降水/能見度 etc. (the cc-params group)");
});

// ---------------------------------------------------------------- anchor windows
test("patch-2 ⛅: anchor + multi-segment editor present in ALL THREE forms (type select, offset, ＋第二段)", () => {
  const editorForms = [
    ["subject-sets.js", subjectSets, "cl-ss-ws", "cl-ss-win-area"],
    ["subject-sets-library.js", subjectLib, "sslib-ws", "sslib-win-area"],
    ["custom-places.js", customPlaces, "cl-cp-ws", "cl-cp-win-area"],
  ];
  for (const [name, src, idp, area] of editorForms) {
    assert.ok(src.includes(`'${idp}0-type'`) || src.includes(`"#${idp}"`) || src.includes(area), `${name} win area`);
    // segment ids are built dynamically ("#<idp>" + i) — assert the prefix
    // pattern, not a literal second id
    assert.ok(src.includes(`'${idp}' + i`) || src.includes(`${idp}1`), `${name} supports a second segment`);
    assert.ok(src.includes("win_add2"), `${name} ＋加第二段 label`);
    for (const t of ["before_sunrise", "after_sunrise", "before_sunset", "after_sunset"]) {
      assert.ok(src.includes(`'${t}'`), `${name} carries anchor type ${t}`);
    }
  }
});

test("patch-2 ⛅: readCc emits the windows array (single fixed stays legacy flat for backward compat)", () => {
  assert.match(subjectSets, /out\.windows = segs\.map/);
  assert.match(subjectLib, /out\.windows = wsSeg\.map/);
  assert.match(customPlaces, /out\.windows = segs\.map/);
  assert.match(subjectSets, /out\.window_start = segs\[0\]\.start/);
});

test("patch-2 ⛅: dynamic display 「日出前（每日動態）·今天 05:10 前」 via windowResolved", () => {
  assert.match(subjectSets, /function dynamicWindowLine\(ev\)/);
  assert.match(subjectSets, /每日動態/);
  assert.match(subjectSets, /windowResolved/);
  // engine side really emits it (worker source)
  const workerSubjectSets = read("workers/api/src/subject-sets.js");
  assert.match(workerSubjectSets, /windowResolved/);
  assert.match(workerSubjectSets, /resolveSegmentBounds/);
  // the honest unresolved word is tri-lingual in the panel
  assert.match(subjectSets, /fail_wp: '時段待座標同步'/);
  assert.match(subjectSets, /fail_wp: 'Window pending place sync'/);
  assert.match(subjectSets, /fail_wp: '時間帯は座標同期待ち'/);
});

// ---------------------------------------------------- extracted-function probes
function grab(src, start, end) {
  const i = src.indexOf(start);
  assert.ok(i >= 0, `marker ${start} found`);
  const j = src.indexOf(end, i);
  assert.ok(j > i, `marker ${end} found after ${start}`);
  return src.slice(i, j + end.length);
}

test("dynamicWindowLine (extracted): anchor single → 「日出前（每日動態）·…05:10 前」; two-segment → spans＋…（每日動態）", () => {
  // slice UP TO the next function (grab() includes the end marker, which
  // would splice "function setRowHtml" into the evaluated source)
  const di = subjectSets.indexOf("function dynamicWindowLine(ev) {");
  const dj = subjectSets.indexOf("  function setRowHtml");
  assert.ok(di >= 0 && dj > di);
  const src = subjectSets.slice(di, dj);
  const t = () => ({ wt_bs: "日出前（每日動態）", wt_as: "日出後（每日動態）", wt_bd: "日落前（每日動態）", wt_ads: "日落後（每日動態）", wt_fixed: "固定時段" });
  const wtLabel = (type) => ({ fixed: "固定時段", before_sunrise: "日出前（每日動態）", after_sunrise: "日出後（每日動態）", before_sunset: "日落前（每日動態）", after_sunset: "日落後（每日動態）" })[type] || "";
  const stubs = { esc: (x) => String(x), t, currentLang: () => "zh-TW", wtLabel };
  const fn = new Function(...Object.keys(stubs), `${src}\nreturn dynamicWindowLine;`)(...Object.values(stubs));
  // single before_sunrise resolved [00:00, 05:10] → label + 前-format
  const one = fn({ windowResolved: [{ type: "before_sunrise", start: "00:00", end: "05:10" }] });
  assert.equal(one.label, "日出前（每日動態）");
  assert.equal(one.spans, "05:10 前");
  // blue-hour mixed pair (owner example anatomy)
  const two = fn({ windowResolved: [
    { type: "fixed", start: "05:00", end: "06:00" },
    { type: "after_sunset", start: "17:30", end: "18:40" },
  ] });
  assert.equal(two.spans, "05:00–06:00＋17:30–18:40");
  // unresolved segments are skipped honestly; no anchor → null (legacy path)
  assert.equal(fn({ windowResolved: [{ type: "before_sunrise", start: null, end: null }] }), null);
  assert.equal(fn({ windowResolved: [{ type: "fixed", start: "05:00", end: "06:00" }] }), null);
});

test("winSegSummary (extracted): anchor labels compress to 「日出前−30分」 in the preview", () => {
  const src = grab(subjectSets, "function winSegSummary(seg, lang) {", "  // Editor: segments state");
  const t = () => ({ wt_fixed: "固定時段", wt_bs: "日出前（每日動態）", wt_ads: "日落後（每日動態）" });
  const wtLabel = (type) => ({ fixed: "固定時段", before_sunrise: "日出前（每日動態）", before_sunset: "日落前（每日動態）", after_sunset: "日落後（每日動態）" })[type] || "";
  const stubs = { t, wtLabel };
  const fn = new Function(...Object.keys(stubs), `${src}\nreturn winSegSummary;`)(...Object.values(stubs));
  assert.equal(fn({ type: "fixed", start: "04:30", end: "07:00" }, "zh-TW"), "04:30–07:00");
  assert.equal(fn({ type: "before_sunrise", offset_minutes: -30 }, "zh-TW"), "日出前−30分");
  assert.equal(fn({ type: "after_sunset" }, "zh-TW"), "日落後");
});
