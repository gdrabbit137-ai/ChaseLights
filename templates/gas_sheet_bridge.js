/**
 * ChaseLights — Apps Script Sheet Bridge (template, CL-UI-52)
 *
 * OWNER REDEPLOY STEPS (summary — see bottom of file for the full walkthrough):
 *   1. Open your ChaseLights data Google Sheet → Extensions ▸ Apps Script.
 *   2. Replace Code.gs content with this file (keep your own CONFIG values:
 *      SECRET / SPREADSHEET_ID — they are NOT stored in the web repo).
 *   3. Save ▸ Deploy ▸ Manage deployments ▸ edit the existing deployment
 *      (version: New version) ▸ Deploy. No new URL is needed when editing
 *      the existing deployment; the /exec URL stays the same.
 *   4. Copy the /exec URL into assets/guest-comment.js → GC_ENDPOINT
 *      (deploy on GitHub Pages after that).
 *
 * Design (CL-UI-52): ONE script serves TWO actions, routed by `action`:
 *   - action === 'comment'  → APPEND one row to the 「訪客留言」 tab.
 *                             Appends never clear, so the four data tabs'
 *                             clear+setValues sync is untouched.
 *   - anything else (legacy sync, no secret → reject) → clear+setValues
 *                             the four existing data tabs, as before.
 * The comment endpoint is a PUBLIC web app on purpose: spam is mitigated by
 * a honeypot field + hard length caps (nickname ≤20, message ≤500), NOT by
 * a secret — the front end never sends one.
 */

// ---------------------------------------------------------------------------
// CONFIG — fill in YOUR values; never commit them to the ChaseLights repo.
// ---------------------------------------------------------------------------
const SECRET = '';            // existing data-sync secret (legacy action only)
const SPREADSHEET_ID = '';   // your ChaseLights data spreadsheet ID

// Existing four data tabs (legacy clear+setValues sync). Keep names in sync
// with whatever the data pipeline posts.
const DATA_TABS = ['地區景點', '天氣資料', '評估結果', '中繼資料'];

// CL-UI-52: guest comment tab. Created on first comment if missing.
const COMMENT_TAB = '訪客留言';
const COMMENT_MAX_MESSAGE = 500;
const COMMENT_MAX_NICKNAME = 20;
const COMMENT_MAX_UA = 120;

function doPost(e) {
  let payload;
  try {
    payload = parsePayload_(e);
  } catch (err) {
    return json_(ResponseShape_(false, '無法解析請求: ' + err));
  }

  // Route: the guest-comment action is public (no secret), everything else
  // is the legacy secret-gated four-tab sync.
  if (payload.action === 'comment') {
    return handleComment_(payload);
  }
  return legacySync_(payload);
}

// ---------------------------------------------------------------------------
// CL-UI-52: append to 「訪客留言」 (columns: 時間戳, 暱稱, 留言, 來源語言, user_agent)
// ---------------------------------------------------------------------------
function handleComment_(p) {
  // Honeypot: real users never fill the invisible `website` field.
  if (p.website) {
    return json_(ResponseShape_(true, 'ok')); // silently accept & drop bots
  }

  const nickname = String(p.nickname || '').trim().slice(0, COMMENT_MAX_NICKNAME);
  const message = String(p.message || '').trim().slice(0, COMMENT_MAX_MESSAGE);
  if (!message) {
    return json_(ResponseShape_(false, '留言內容不可空白'));
  }

  const lang = String(p.lang || '').trim().slice(0, 10);
  const ua = simplifyUserAgent_(String(p.ua || ''), COMMENT_MAX_UA);

  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  let sheet = ss.getSheetByName(COMMENT_TAB);
  if (!sheet) {
    sheet = ss.insertSheet(COMMENT_TAB);
    sheet.appendRow(['時間戳', '暱稱', '留言', '來源語言', 'user_agent']);
    sheet.setFrozenRows(1);
  }
  sheet.appendRow([new Date(), nickname, message, lang, ua]);
  return json_(ResponseShape_(true, 'ok'));
}

// ---------------------------------------------------------------------------
// Legacy sync: clear + setValues the four data tabs (unchanged behaviour).
// Payload: { secret, data: { '<tabName>': [[...], ...], ... } }
// ---------------------------------------------------------------------------
function legacySync_(p) {
  if (!SECRET || p.secret !== SECRET) {
    return json_(ResponseShape_(false, 'secret 錯誤'));
  }
  const data = p.data || {};
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  DATA_TABS.forEach(function (tab) {
    const rows = data[tab];
    if (!rows) return; // tab not in this payload → leave untouched
    const sheet = ss.getSheetByName(tab);
    if (!sheet) return;
    sheet.clearContents();
    if (rows.length) {
      sheet.getRange(1, 1, rows.length, rows[0].length).setValues(rows);
    }
  });
  return json_(ResponseShape_(true, 'ok'));
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function parsePayload_(e) {
  let raw = e && e.postData && e.postData.contents ? e.postData.contents : '';
  if (!raw && e && e.parameter && e.parameter.payload) {
    raw = e.parameter.payload; // form-encoded fallback
  }
  if (!raw) throw new Error('empty body');
  const parsed = JSON.parse(raw);
  if (typeof parsed !== 'object' || parsed === null) throw new Error('bad json');
  return parsed;
}

// Collapse the raw UA to a short, human-readable family string when the
// common families are recognisable; otherwise keep a truncated raw UA.
function simplifyUserAgent_(ua, max) {
  const families = [
    ['Edg/', 'Edge'], ['OPR/', 'Opera'], ['Chrome', 'Chrome'],
    ['Firefox', 'Firefox'], ['Safari', 'Safari']
  ];
  for (let i = 0; i < families.length; i++) {
    if (ua.indexOf(families[i][0]) !== -1) return families[i][1];
  }
  return ua.slice(0, max);
}

function ResponseShape_(ok, message) {
  return { ok: ok, message: message || '' };
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/* ==========================================================================
 OWNER WALKTHROUGH (step by step)

 1. Open the ChaseLights data spreadsheet in Google Sheets.
 2. Menu: 「擴充功能」 ▸ 「Apps Script」.
 3. In the editor, replace the whole Code.gs with the contents of this file.
 4. Put your existing SECRET and SPREADSHEET_ID back into the CONFIG block
    at the top (they were only in your old script — the web repo never
    stores them).
 5. Press 「儲存」 (Ctrl+S), then 「部署」 ▸ 「管理部署作業」:
      - click the existing deployment's pencil icon (✏),
      - 「版本」 choose 「新版本」,
      - press 「部署」.
    This keeps the SAME /exec URL. (Only use 「新增部署作業」 if you want a
    new URL — then the front end's GC_ENDPOINT must change too.)
 6. Copy the Web App URL (ends in /exec).
 7. In the repo, open assets/guest-comment.js and paste that URL into
    GC_ENDPOINT (one line). Commit and let GitHub Pages redeploy.
 8. Test: open the site, click the 💬 留言 footer entry, submit a short
    comment, and confirm a new row appears in the 「訪客留言」 tab.
    Note: if you bumped permissions (script not yet authorised for
    insertSheet), Apps Script shows an authorisation prompt on first run —
    approve it once, then retry the comment.
   ========================================================================== */
