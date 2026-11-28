// CL-UI-100 (DESIGN-7 Stage 2): place rating + report/comment UGC channel UI
// on the V1 shell, implemented from data/v2/audits/design-mockups/mockup-rating.html
// (task/DESIGN-4 head ddbf4bcfc). Covers the ticket's test list:
//   ① chip cold-start hidden (n_eff<2 renders no chip),
//   ② evaluation area rendering (aggregate + L/P axes + masked-name list),
//   ③ submission flows (rating edit/delete, report six types + photo_url +
//      fix_suggest, first-review site comment),
//   ④ masked nickname 「山風·#4F2」 rendering + anonymous fallback,
//   ⑤ gray release: nothing mounts unless /feedback/config answers enabled.
// Backend behavior (config endpoint, masked name logic) is covered by
// workers/api/test/feedback.test.js — the CL-UI-100 block there.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const fbSource = readFileSync(new URL('../../../assets/feedback-ui.js', import.meta.url), 'utf8');
const fbCss = readFileSync(new URL('../../../assets/feedback-ui.css', import.meta.url), 'utf8');
const indexSource = readFileSync(new URL('../../../index.html', import.meta.url), 'utf8');
const appSource = readFileSync(new URL('../../../assets/app.js', import.meta.url), 'utf8');

const grab = (start, end, src = fbSource) => {
  const a = src.indexOf(start);
  const b = src.indexOf(end, a + 1);
  assert.ok(a >= 0 && b > a, `grab failed: ${start} .. ${end}`);
  return src.slice(a, b);
};

// i18n dict + RTYPES + text helpers (lang/t/esc/fmt) with Node-safe stubs.
const HELPERS = grab('var I18N = {', 'function chipHtml');
const fillFn = grab('function scaleFill', 'function axisLabel');
const axisFn = grab('function axisLabel', 'function evalHtml');
const chipFn = grab('function chipHtml', 'function scaleFill');
const evalFn = grab('function evalHtml', 'function rateHtml');
const rateDoneFn = grab('function rateDoneHtml', 'function reportHtml');
const reportDoneFn = grab('function reportDoneHtml', 'function fbHtml');
const fbDoneFn = grab('function fbDoneHtml', 'function needLoginHtml');
const needLoginFn = grab('function needLoginHtml', '  // ===========================================================================\n  // Runtime');

function makeFns(withDoneFns) {
  const prelude = `
    var document = { getElementById: function () { return null; } };
    var localStorage = { getItem: function () { return null; } };
  `;
  const doneFns = withDoneFns ? rateDoneFn + reportDoneFn + fbDoneFn + needLoginFn : '';
  const doneExports = withDoneFns ? ', rateDoneHtml: rateDoneHtml, reportDoneHtml: reportDoneHtml, fbDoneHtml: fbDoneHtml, needLoginHtml: needLoginHtml' : '';
  return new Function(prelude + HELPERS + fillFn + axisFn + chipFn + evalFn + doneFns +
    ' return { chipHtml: chipHtml, evalHtml: evalHtml, scaleFill: scaleFill, axisLabel: axisLabel, t: t' + doneExports + ' };')();
}

const AGG_OK = {
  insufficient: false, lFinal: 4.1, pFinal: 3.9, nRaw: 34, nEff: 30.8, nLast30: 8, pctP4plus: 0.78,
  comments: [
    { message: '雲海值得，日出後半小時最紅', maskedName: '山風·#4F2', lp: { l: 4, p: 5 } },
    { message: '風大要帶濾鏡', maskedName: null, lp: null },
    { message: '到達成本偏高', maskedName: '山影·#77AA', lp: { l: 3, p: 3 } },
    { message: '第四則不應顯示', maskedName: '多餘·#0000', lp: null }
  ]
};
const AGG_COLD = { insufficient: true, lFinal: null, pFinal: null, nRaw: 2, nEff: 1.4, nLast30: 2, pctP4plus: 0.5, comments: [] };
const MINE = { l: 4, p: 5, shotDate: '2026-11-15', commentText: '機位在北側', maskedName: '山風·#9ABC' };

// ---------------------------------------------------------------- ① chip
test('CL-UI-100 ①: chip renders ★+score·n only past the gate; cold start renders none', () => {
  const f = makeFns('');
  const chip = f.chipHtml(AGG_OK);
  assert.match(chip, /class="clfb r-chip"/);
  assert.match(chip, /<b>★3\.9<\/b>·34/);  // mockup chip shows P (出片 is the hard signal)
  assert.match(chip, /title="/); // carries the rb_title tooltip
  // cold start / gate: empty string — the chip element stays hidden
  assert.equal(f.chipHtml(AGG_COLD), '');
  assert.equal(f.chipHtml(null), '');
  assert.equal(f.chipHtml({ insufficient: false, lFinal: 4, pFinal: null, nRaw: 5 }), '');
});

test('CL-UI-100 ①: scanCards never mounts chips while the channel is disabled', () => {
  assert.ok(fbSource.includes('function scanCards() {\n    if (!state.enabled) return;'), 'gray gate must guard the chip scan');
});

// ---------------------------------------------------------------- ② evaluation area
test('CL-UI-100 ②: evaluation area renders aggregate, L/P axes, stats, masked list, mine row', () => {
  const f = makeFns('');
  const html = f.evalHtml(AGG_OK, MINE, '山風·#9ABC');
  assert.match(html, /class="fact-sep"/); // owner ruling: facts | ratings divider
  assert.match(html, /<b>L<\/b> /);
  assert.match(html, /<b>P<\/b> /);
  assert.match(html, /class="av">4\.1<small> \/5<\/small>/);
  assert.match(html, /class="av">3\.9<small> \/5<\/small>/);
  assert.match(html, /78%/); // P≥4 rate
  assert.match(html, /n=34/);
  assert.match(html, /class="k">8<\/span>/); // last 30 days
  // masked nickname list — verbatim 「山風·#4F2」-style names, ≤3 rows
  assert.match(html, /山風·#4F2/);
  assert.match(html, /L4·P5/);
  assert.ok(!html.includes('第四則不應顯示'), 'only 3 comment rows render');
  // anonymous fallback for members without a display name
  assert.match(html, /攝影者/);
  // my rating row: L/P + edit + delete entries
  assert.match(html, /class="mine"/);
  assert.match(html, /L4 · P5/);
  assert.match(html, /11\/15/);
  assert.match(html, /data-fbx-open="rate-edit"/);
  assert.match(html, /data-fbx-open="rate-del"/);
  assert.match(html, /data-fbx-open="rate"/);
  assert.match(html, /data-fbx-open="report"/);
});

test('CL-UI-100 ②: cold start renders the dashed 「尚無足夠評價」 box + first-rating CTA, never a score', () => {
  const f = makeFns('');
  const html = f.evalHtml(AGG_COLD, null, null);
  assert.match(html, /fbx-empty/);
  assert.match(html, /尚無足夠評價/);
  assert.match(html, /已有 2 人評過（樣本不足，暫不出示分數）/);
  assert.match(html, /data-fbx-open="rate"/);
  assert.ok(!html.includes('class="axis"'), 'no axes below the gate');
  assert.ok(!html.includes('class="rstat"'), 'no stats below the gate');
});

// ---------------------------------------------------------------- ③ submission flows
test('CL-UI-100 ③: rating POST is the upsert (l/p/commentText); edit/delete paths exist', () => {
  assert.match(fbSource, /type: 'rating',\s*\n\s*placeId: placeId,/);
  assert.match(fbSource, /l: rateState\.L,/);
  assert.match(fbSource, /p: rateState\.P,/);
  assert.match(fbSource, /commentText: \(pre && pre\.value\.trim\(\)\) \|\| null/);
  // delete = DELETE /feedback?place_id=...
  assert.match(fbSource, /method: 'DELETE'/);
  // edit prefills from mine and re-submits as the same upsert (one vote per user×place)
  assert.match(fbSource, /data-fbx-open="rate-edit"/);
  assert.match(fbSource, /data-fbx-open="rate-del"/);
});

test('CL-UI-100 ③: report flow — six types, required description gates the submit, fix_suggest + photo_url ride the POST', () => {
  for (const code of ['data_wrong', 'location_wrong', 'condition_wrong', 'seasonal_wrong', 'place_gone', 'other']) {
    assert.ok(fbSource.includes(`'${code}'`), `report type ${code} wired`);
  }
  assert.match(fbSource, /reportCategory: reportType,/);
  assert.match(fbSource, /commentText: desc\.value\.trim\(\),/);
  assert.match(fbSource, /fixSuggest: \(ov\.querySelector\('#fbx-report-fix'\)\.value \|\| ''\)\.trim\(\) \|\| null/);
  assert.match(fbSource, /photoUrl: photo && photo\.value\.trim\(\) \? photo\.value\.trim\(\) : null/);
  // fail-closed submit: type AND description required before the button arms
  assert.match(fbSource, /var ready = !!reportType && desc && desc\.value\.trim\(\)\.length > 0;/);
  assert.match(fbSource, /submit\.disabled = !ready;/);
});

test('CL-UI-100 ③: site comment POST carries no placeId; done state says 「送出後待審」', () => {
  assert.match(fbSource, /var body = \{ type: 'comment', commentText: note\.value\.trim\(\) \}; \/\/ no placeId = site feedback/);
  const f = makeFns(true);
  const done = f.fbDoneHtml();
  assert.match(done, /已送出，待審核後公開/); // first-review notice (task ③)
  assert.match(done, /class="done amber"/);
});

test('CL-UI-100 ③: done states — rating green (aggregated), report amber (never public), flagged copy honest', () => {
  const f = makeFns(true);
  const rateDone = f.rateDoneHtml({ placeName: '崇德', region: '花蓮', l: 4, p: 5 });
  assert.match(rateDone, /class="done"/);
  assert.match(rateDone, /L4 · P5/);
  assert.match(rateDone, /修改會覆蓋原評分（不重複計票）/);
  const rateFlagged = f.rateDoneHtml({ placeName: 'x', region: '', l: 4, p: 5, flagged: true });
  assert.match(rateFlagged, /已送出，待人工審核/);
  const repDone = f.reportDoneHtml({ placeName: 'x', region: '' });
  assert.match(repDone, /class="done amber"/);
  assert.match(repDone, /已收到，審閱中/);
  assert.match(repDone, /回報不公開顯示/);
});

test('CL-UI-100 ③: member-only submissions — anonymous openers get the login wall with OAuth links', () => {
  assert.ok(fbSource.includes("function requireMemberThen(placeId, fn) {\n    currentMember().then(function (member) {\n      if (!member) { showOverlay('fbx-login-overlay', needLoginHtml()); return; }"));
  const f = makeFns(true);
  const nl = f.needLoginHtml();
  assert.match(nl, /href="\/api\/v1\/auth\/line\/start"/);
  assert.match(nl, /href="\/api\/v1\/auth\/google\/start"/);
});

// ---------------------------------------------------------------- ④ masked nickname
test('CL-UI-100 ④: masked nickname renders verbatim from the API; unnamed members fall back to 攝影者', () => {
  const f = makeFns('');
  const html = f.evalHtml(AGG_OK, null, null);
  assert.match(html, /<span class="who">山風·#4F2<\/span>/);
  assert.match(html, /<span class="who">攝影者<\/span>/);
  // self mask: member name masked to first two chars + ** when the API gives none
  assert.match(fbSource, /m\.displayName\.slice\(0, 2\) \+ '\*\*'/);
});

// ---------------------------------------------------------------- ⑤ gray release
test('CL-UI-100 ⑤: nothing mounts unless GET /feedback/config answers {enabled:true}; 404/403 fail closed', () => {
  assert.ok(fbSource.includes("fetch(CFG_ENDPOINT"), 'config probe endpoint');
  assert.ok(fbSource.includes("if (!res.ok) return null; // 404 (pre-config deploy) / 403 (off) → hidden, fail closed"));
  assert.ok(fbSource.includes('doc.enabled === true'), 'only enabled===true boots the UI');
  assert.ok(fbSource.includes('.catch(function () { /* offline → hidden */ })'));
});

// ---------------------------------------------------------------- surfaces + stamps
test('CL-UI-100: index.html mounts the widget with the bumped clui102 stamps', () => {
  assert.match(indexSource, /assets\/app\.js\?v=clui145/);
  assert.match(indexSource, /assets\/app\.css\?v=clui145/);
  assert.match(indexSource, /assets\/feedback-ui\.js\?v=clui102/);
  assert.match(indexSource, /assets\/feedback-ui\.css\?v=clui102/);
  assert.ok(!indexSource.includes('clui100'), 'stale stamp must be gone');
});

test('CL-UI-100: app.js carries exactly the three additive place-id hooks', () => {
  assert.ok(appSource.includes("card.dataset.placeId=cp?'':(spot.spot_id||'')"), 'place-id hook kept (CL-APP-09 patch-6 bridge form)');
  assert.ok(appSource.includes("document.getElementById('modal-overlay').dataset.placeId=spot.spot_id||'';"));
  assert.ok(appSource.includes("overlay.dataset.placeId=spot.spot_id||'';"));
  // CL-UI-45: the card-click binding adds reads of the SAME hook (the pressed
  // card's id, the live card's id, and the private-point key fallback) — no new
  // hook surface, and every addition is named so the pin cannot drift silently.
  assert.ok(appSource.includes("clui45LastPress=card?{placeId:clui45CardKey(card)"), 'press-intent hook (CL-UI-45)');
  assert.ok(appSource.includes("const diverged=!!(pressedId&&liveId&&pressedId!==liveId);"), 'press/release mismatch guard (CL-UI-45)');
  assert.ok(appSource.includes("function clui45CardKey(card){"), 'one stable per-card key reader (CL-UI-45)');
  assert.equal((appSource.match(/dataset\.placeId/g) || []).length, 6, 'hook surface stays minimal (3 + 3 CL-UI-45 reads)');
});

test('CL-UI-100: overlay CSS carries the CL-UI-47 [hidden] guard; widgets scope under .clfb', () => {
  assert.match(fbCss, /\.clfb-overlay\[hidden\]\{display:none!important\}/);
  assert.match(fbCss, /\.clfb-overlay\.open\{display:flex\}/);
  assert.match(fbCss, /span\.clfb\.r-chip\{/);
  assert.match(fbCss, /\.clfb \.rbox\{/);
  assert.match(fbCss, /\.clfb \.lev\.sel\{/);
  assert.match(fbCss, /\.clfb \.type\.sel\{/);
  assert.match(fbCss, /\.clfb \.done\.amber\{/);
});

test('CL-UI-100: trilingual coverage — every user-visible key exists in zh-TW, en and ja', () => {
  const dict = grab('var I18N = {', 'var RTYPES =');
  for (const pack of ["'zh-TW': {", "'en': {", "'ja': {"]) {
    const a = dict.indexOf(pack);
    assert.ok(a >= 0, `pack ${pack} present`);
  }
  for (const key of ['rb_title', 'e1', 'e2_n', 'cta', 'mine_lbl', 'edit', 'del', 'b_rate', 'b_report',
    'rate_title', 'rate_edit_title', 'qd_L', 'qd_P', 'ph', 'anon', 'submit', 'done1', 'done3',
    'rep_title', 'rep_sub', 'rep_desc', 'rep_fix', 'rep_photo', 'rep_submit', 'rep_done1', 'rep_done3',
    'nl1', 'fb_title', 'fb_submit', 'fb_done1', 'foot_feedback', 'fact_sep', 'error', 'flagged',
    'rt_data', 'rt_loc', 'rt_cond', 'rt_seas', 'rt_gone', 'rt_other', 'anon_fallback', 'need_desc']) {
    const re = new RegExp("(^|[^A-Za-z0-9_'])" + key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + "(?=\\s*:)", 'g');
    const count = (dict.match(re) || []).length;
    assert.equal(count, 3, `key ${key} must exist in all three dictionaries (got ${count})`);
  }
});

test('CL-UI-100: mockup copy is verbatim — zh-TW anchors from mockup-rating.html appear in the widget', () => {
  for (const s of ['為這個景點評分', '尚無足夠評價', '去過？留下第一個評價', '回報站上錯誤', '更正建議（選填）',
    '已收到，審閱中', '評分已送出，已計入聚合', '留言給站長', '送出後顯示為', '有效評價', '近 30 天',
    'P≥4 出片率', '資料錯誤', '封閉/消失', '季節/時窗錯', '登入後才能送出']) {
    assert.ok(fbSource.includes(s), `mockup string missing: ${s}`);
  }
});
