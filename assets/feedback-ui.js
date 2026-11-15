/* CL-UI-100 (DESIGN-7 Stage 2): place rating + report/comment UGC channel for
   the V1 shell. Implements data/v2/audits/design-mockups/mockup-rating.html
   (task/DESIGN-4 head ddbf4bcfc) verbatim on the real surfaces:

   ① card rating chip 「★4.1·34」 in the card head (mono, amber figure) —
     never rendered below the cold-start gate (n_eff<2 / n_raw<3);
   ② evaluation block in the forecast modal (#modal-overlay) and the subject
     panel (#place-modal-overlay): aggregate + L/P two-axis detail + masked
     nickname list (「山風·#4F2」 short-code names from the Worker) + my-rating
     row (edit / delete) + ✎評分 / 🚩回報錯誤 entries; cold start = dashed
     「尚無足夠評價」 box with the first-rating CTA;
   ③ submission flows: rating (two five-level axes, edit overwrites, delete),
     report (six issue types + optional photo_url + fix_suggest, never public),
     site comment via the footer slot (first-review: 「送出後待審」);
   ④ gray release: nothing mounts at all unless GET /api/v1/feedback/config
     answers {enabled:true} — any failure (404/403/offline) means hidden.

   Self-contained on purpose (member-auth.js / favorites-client.js precedent):
   assets/app.js is only touched by three additive dataset hooks
   (card.dataset.placeId / overlay.dataset.placeId) that tag the rendered
   surfaces with the place id this widget reads. Member sessions ride the
   same-origin HttpOnly cookies; identity state follows the chaselights:auth
   event member-auth.js broadcasts.

   window.__FBX_FIXTURES (screenshot/browser test harness only): when present,
   network calls resolve from the fixture object instead of the live API.
*/
(function () {
  'use strict';

  var CFG_ENDPOINT = '/api/v1/feedback/config';
  var FB_ENDPOINT = '/api/v1/feedback';
  var ME_ENDPOINT = '/api/v1/auth/me';

  var I18N = {
    'zh-TW': {
      foot_feedback: '留言／回報',
      rb_title: '評價（會員 UGC）', ax_L: 'L 景色', ax_P: 'P 出片滿意度', p_rate: 'P≥4 出片率', n_total: '有效評價', n_30: '近 30 天',
      mine_lbl: '我的評分', edit: '✎ 編輯', del: '刪除', b_rate: '✎ 評分', b_report: '🚩 回報錯誤',
      e1: '尚無足夠評價', e2_n: '已有 {n} 人評過（樣本不足，暫不出示分數）', cta: '去過？留下第一個評價',
      rate_title: '為這個景點評分', rate_edit_title: '編輯我的評分',
      qd_L: '這個景點本身值不值得？景色、氛圍、專程程度', qd_P: '實際拍攝的收穫：成功率、片子滿意度',
      lv: ['不佳', '普通', '尚可', '好', '極佳'],
      ph: '選填：這裡拍什麼最值、哪個題材好、機位在哪…',
      anon: '送出後顯示為', anon_fallback: '攝影者', submit: '送出評分', submit_edit: '更新評分',
      done1: '評分已送出，已計入聚合', done2_fmt: 'L{L} · P{P}', done3: '修改會覆蓋原評分（不重複計票）', done_btn: '完成',
      rep_title: '回報站上錯誤', rep_sub: '回報不公開顯示——直接送到站長的審閱佇列',
      rt_data: ['📡', '資料錯誤', 'Wrong data'], rt_loc: ['📍', '位置錯誤', 'Wrong location'],
      rt_cond: ['🎚', '條件錯誤', 'Wrong conditions'], rt_seas: ['🍁', '季節/時窗錯', 'Wrong season/window'],
      rt_gone: ['🚧', '封閉/消失', 'Closed or gone'], rt_other: ['💬', '其他', 'Other'],
      rep_desc: '說明（必填）', rep_ph: '哪裡錯、當時狀況、什麼時候遇到的…',
      rep_fix: '更正建議（選填）', rep_fix_ph: '正確的值／正確的位置／建議的門檻…',
      rep_photo: '照片連結（選填）', rep_photo_ph: 'https://…（出片佐證，可空白）',
      rep_private: '不公開顯示',
      rep_submit: '送出回報', rep_done1: '已收到，審閱中', rep_done2: '🚩', rep_done3: '回報不公開顯示；處置結果不另行通知（v1）',
      nl1: '登入後才能送出', nl2: '評分／回報／留言都是會員功能；匿名顯示，永不公開你的帳號資訊',
      fb_title: '留言給站長', fb_sub: '站務留言：建議、想要的功能、任何想法',
      fb_submit: '送出留言', fb_done1: '已送出，待審核後公開',
      fact_sep: '事實欄（data 層）｜評價（會員 UGC）',
      error: '送出失敗，請重試', flagged: '已送出，待人工審核',
      need_desc: '需填寫說明'
    },
    'en': {
      foot_feedback: 'Feedback / Report',
      rb_title: 'Member ratings', ax_L: 'L Scenery', ax_P: 'P Photo yield', p_rate: 'P≥4 success rate', n_total: 'Effective ratings', n_30: 'Last 30 days',
      mine_lbl: 'My rating', edit: '✎ Edit', del: 'Delete', b_rate: '✎ Rate', b_report: '🚩 Report an issue',
      e1: 'Not enough ratings yet', e2_n: '{n} rated so far (too few to show a score)', cta: 'Been there? Leave the first rating',
      rate_title: 'Rate this place', rate_edit_title: 'Edit my rating',
      qd_L: 'Is the place itself worth it? scenery, mood, dedication', qd_P: 'The haul: hit rate, how you feel about the shots',
      lv: ['Poor', 'Fair', 'OK', 'Good', 'Superb'],
      ph: 'Optional: what is worth shooting here, best subjects, where the spot is…',
      anon: 'Will be shown as', anon_fallback: 'Photographer', submit: 'Submit rating', submit_edit: 'Update rating',
      done1: 'Rating submitted and aggregated', done2_fmt: 'L{L} · P{P}', done3: 'Edits overwrite your original vote (never double-counted)', done_btn: 'Done',
      rep_title: 'Report an issue', rep_sub: 'Reports are never shown publicly — they go straight to the owner\'s review queue',
      rt_data: ['📡', 'Wrong data', 'Data'], rt_loc: ['📍', 'Wrong location', 'Location'],
      rt_cond: ['🎚', 'Wrong conditions', 'Conditions'], rt_seas: ['🍁', 'Wrong season/window', 'Season'],
      rt_gone: ['🚧', 'Closed or gone', 'Gone'], rt_other: ['💬', 'Other', 'Other'],
      rep_desc: 'Description (required)', rep_ph: 'What is wrong, the conditions then, when it happened…',
      rep_fix: 'Suggested fix (optional)', rep_fix_ph: 'The correct value / location / threshold…',
      rep_photo: 'Photo link (optional)', rep_photo_ph: 'https://… (proof of the shot, may stay empty)',
      rep_private: 'never shown publicly',
      rep_submit: 'Send report', rep_done1: 'Received — under review', rep_done2: '🚩', rep_done3: 'Reports are never public; you will not be notified of the outcome (v1)',
      nl1: 'Log in to submit', nl2: 'Ratings / reports / comments are member-only; shown anonymously, your account is never exposed',
      fb_title: 'Message the owner', fb_sub: 'Site feedback: suggestions, feature requests, anything',
      fb_submit: 'Send message', fb_done1: 'Sent — pending review before it is published',
      fact_sep: 'facts · data',
      error: 'Submit failed, please try again', flagged: 'Submitted — queued for manual review',
      need_desc: 'Description required'
    },
    'ja': {
      foot_feedback: 'コメント／報告',
      rb_title: 'メンバー評価', ax_L: 'L 景色', ax_P: 'P 出来栄え', p_rate: 'P≥4 成功率', n_total: '有効評価', n_30: '直近30日',
      mine_lbl: 'マイ評価', edit: '✎ 編集', del: '削除', b_rate: '✎ 評価', b_report: '🚩 問題を報告',
      e1: 'まだ評価が足りません', e2_n: '{n} 件の評価あり（表示には不足）', cta: '行ったことある？最初の評価を',
      rate_title: 'この場所を評価', rate_edit_title: 'マイ評価を編集',
      qd_L: 'その場所自体の価値：景色・雰囲気・専程の価値', qd_P: '撮影の収穫：成功率・写真好み',
      lv: ['悪い', '普通', 'まあ', '良い', '最高'],
      ph: '任意：ここは何を撮るべきか、良い題材、場所…',
      anon: '表示名', anon_fallback: '撮影者', submit: '評価を送信', submit_edit: '評価を更新',
      done1: '評価を送信・集計に反映', done2_fmt: 'L{L} · P{P}', done3: '編集は元の票を上書き（二重計上なし）', done_btn: '完了',
      rep_title: '問題を報告', rep_sub: '報告は公開されません — オーナーのレビュー列に直接届きます',
      rt_data: ['📡', 'データ誤り', 'Data'], rt_loc: ['📍', '位置誤り', 'Location'],
      rt_cond: ['🎚', '条件誤り', 'Conditions'], rt_seas: ['🍁', '季節/時間窓誤り', 'Season'],
      rt_gone: ['🚧', '閉鎖/消失', 'Gone'], rt_other: ['💬', 'その他', 'Other'],
      rep_desc: '説明（必須）', rep_ph: '何が違うか、当時の状況、いつ…',
      rep_fix: '修正案（任意）', rep_fix_ph: '正しい値／位置／しきい値…',
      rep_photo: '写真URL（任意）', rep_photo_ph: 'https://…（撮影の証拠、空欄可）',
      rep_private: '非公開',
      rep_submit: '報告を送信', rep_done1: '受付完了 — 審査中', rep_done2: '🚩', rep_done3: '報告は非公開；結果の通知はありません（v1）',
      nl1: '送信にはログインが必要', nl2: '評価／報告／コメントは会員機能；匿名表示、アカウント情報は非公開',
      fb_title: 'オーナーへのメッセージ', fb_sub: 'サイトへのご意見：提案・ご要望など',
      fb_submit: 'メッセージを送信', fb_done1: '送信しました。審査後に公開されます',
      fact_sep: '事実欄（data層）｜評価（メンバーUGC）',
      error: '送信に失敗しました。もう一度お試しください', flagged: '送信されました。手動審査の待ち',
      need_desc: '説明が必要'
    }
  };

  var RTYPES = [['rt_data', 'data_wrong'], ['rt_loc', 'location_wrong'], ['rt_cond', 'condition_wrong'],
                ['rt_seas', 'seasonal_wrong'], ['rt_gone', 'place_gone'], ['rt_other', 'other']];

  function lang() {
    var sel = document.getElementById('lang-select');
    var v = (sel && typeof sel.value === 'string' && sel.value) ||
            (function () { try { return localStorage.getItem('chaselights_lang'); } catch (e) { return null; } }()) || 'zh-TW';
    return I18N[v] ? v : 'zh-TW';
  }
  function t(key) {
    var p = I18N[lang()];
    return (p && p[key]) || I18N['zh-TW'][key] || '';
  }
  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
  function fmt(v) { return typeof v === 'number' && isFinite(v) ? v.toFixed(1) : '—'; }

  // ===========================================================================
  // Pure render functions (test grabs + harness reuse). Data in, HTML out.
  // ===========================================================================

  /* card chip — hidden (empty string) whenever the gate is not met (task ①) */
  function chipHtml(agg) {
    if (!agg || agg.insufficient || typeof agg.pFinal !== 'number') return '';
    return '<span class="clfb r-chip" data-fbx-chip title="' + esc(t('rb_title')) + '"><b>★' + esc(fmt(agg.pFinal)) + '</b>·' + esc(String(agg.nRaw)) + '</span>';
  }

  function scaleFill(v) {
    var s = '';
    for (var i = 1; i <= 5; i++) s += '<i class="' + (v >= i - 0.5 ? 'fill' : '') + '"></i>';
    return s;
  }
  function axisLabel(key) { return String(t(key) || '').split(' ')[1] || t(key); }

  /* evaluation block — mockup rbox(); cold start keeps the dashed box + CTA */
  function evalHtml(agg, mine, maskedSelf) {
    var head = '<div class="fact-sep"><span>' + esc(t('fact_sep')) + '</span></div>';
    if (!agg || agg.insufficient || typeof agg.lFinal !== 'number' || typeof agg.pFinal !== 'number') {
      var n = agg && typeof agg.nRaw === 'number' ? agg.nRaw : 0;
      return head +
        '<div class="rbox"><div class="r-t"><span class="lbl">' + esc(t('rb_title')) + '</span></div>' +
        '<div class="fbx-empty"><div class="e1">' + esc(t('e1')) + '</div>' +
        '<div class="e2">' + esc(t('e2_n').replace('{n}', String(n))) + '</div>' +
        '<button data-fbx-open="rate">' + esc(t('cta')) + '</button></div></div>';
    }
    var pct = (typeof agg.pctP4plus === 'number' ? Math.round(agg.pctP4plus * 100) : null);
    var revs = ((agg.comments || []).slice(0, 3)).map(function (c) {
      var who = c.maskedName || t('anon_fallback');
      var lp = (c.lp && (typeof c.lp.l === 'number' || typeof c.lp.p === 'number'))
        ? '<span class="lp">L' + esc(c.lp.l == null ? '—' : c.lp.l) + '·P' + esc(c.lp.p == null ? '—' : c.lp.p) + '</span>' : '';
      return '<div class="row"><span class="who">' + esc(who) + '</span>' + lp +
        '<span class="txt">' + esc(c.message || '') + '</span></div>';
    }).join('');
    var mineRow = '';
    if (mine && typeof mine.l === 'number' && typeof mine.p === 'number') {
      var day = mine.shotDate || (mine.createdAt ? String(mine.createdAt).slice(0, 10) : '');
      var dayBits = day ? day.split('-') : [];
      var dayText = dayBits.length === 3 ? Number(dayBits[1]) + '/' + Number(dayBits[2]) : '';
      mineRow = '<div class="mine"><span class="mk">' + esc(t('mine_lbl')) + '</span>' +
        '<span class="mv">L' + esc(mine.l) + ' · P' + esc(mine.p) + '</span>' +
        '<span style="color:var(--cl-text-3)">' + esc(dayText) + '</span>' +
        '<button class="edit" data-fbx-open="rate-edit">' + esc(t('edit')) + '</button>' +
        '<button class="del" data-fbx-open="rate-del">' + esc(t('del')) + '</button></div>';
    }
    return head + '<div class="rbox">' +
      '<div class="axis"><span class="an"><b>L</b> ' + esc(axisLabel('ax_L')) + '</span>' +
      '<span class="scale">' + scaleFill(agg.lFinal) + '</span>' +
      '<span class="av">' + esc(fmt(agg.lFinal)) + '<small> /5</small></span></div>' +
      '<div class="axis"><span class="an"><b>P</b> ' + esc(axisLabel('ax_P')) + '</span>' +
      '<span class="scale">' + scaleFill(agg.pFinal) + '</span>' +
      '<span class="av">' + esc(fmt(agg.pFinal)) + '<small> /5</small></span></div>' +
      '<div class="rstat">' +
      '<span>' + esc(t('p_rate')) + ' <span class="k">' + (pct == null ? '—' : pct + '%') + '</span></span>' +
      '<span>' + esc(t('n_total')) + ' <span class="k">n=' + esc(String(agg.nRaw)) + '</span></span>' +
      '<span>' + esc(t('n_30')) + ' <span class="k">' + esc(String(agg.nLast30 == null ? 0 : agg.nLast30)) + '</span></span>' +
      '</div>' +
      (revs ? '<div class="rev">' + revs + '</div>' : '') +
      mineRow +
      '<div class="racts"><button class="b-rate" data-fbx-open="rate">' + esc(t('b_rate')) + '</button>' +
      '<button data-fbx-open="report">' + esc(t('b_report')) + '</button></div>' +
      '</div>';
  }

  /* rate submission modal (mockup rateHTML; the masked self name rides the API) */
  function rateHtml(o) {
    o = o || {};
    var state = o.isEdit && o.mine ? { L: o.mine.l, P: o.mine.p } : { L: 0, P: 0 };
    function levs(ax) {
      var s = '';
      for (var v = 1; v <= 5; v++) {
        s += '<button class="lev' + (state[ax] === v ? ' sel' : '') + '" data-ax="' + ax + '" data-v="' + v + '">' +
          '<span class="dots">' + '●'.repeat(v) + '○'.repeat(5 - v) + '</span><span>' + esc(t('lv')[v - 1]) + '</span></button>';
      }
      return s;
    }
    var who = o.maskedSelf || t('anon_fallback');
    return '<div class="m-head"><div><div class="name">' + esc(o.isEdit ? t('rate_edit_title') : t('rate_title')) + '</div>' +
      '<div class="sub">' + esc(o.placeName || '') + ' · ' + esc(o.region || '') + '</div></div>' +
      '<button class="close" data-fbx-close>✕</button></div>' +
      '<div class="ctx"><span class="g">' + esc(o.placeName || '') + '</span></div>' +
      '<div class="qaxis"><div class="qh"><span class="qn">L — ' + esc(axisLabel('ax_L')) + '</span>' +
      '<span class="qd">' + esc(t('qd_L')) + '</span><span class="qhint" id="fbx-q-l">' + (state.L ? '★' + state.L : '') + '</span></div>' +
      '<div class="levs" id="fbx-lev-L">' + levs('L') + '</div></div>' +
      '<div class="qaxis"><div class="qh"><span class="qn">P — ' + esc(axisLabel('ax_P')) + '</span>' +
      '<span class="qd">' + esc(t('qd_P')) + '</span><span class="qhint" id="fbx-q-p">' + (state.P ? '★' + state.P : '') + '</span></div>' +
      '<div class="levs" id="fbx-lev-P">' + levs('P') + '</div></div>' +
      '<textarea class="txt-note" id="fbx-rate-note" maxlength="500" placeholder="' + esc(t('ph')) + '">' + esc(o.isEdit && o.mine ? (o.mine.commentText || '') : '') + '</textarea>' +
      '<div class="anon"><span>🔒 ' + esc(t('anon')) + '</span><span class="who">' + esc(who) + '</span></div>' +
      '<div class="fbx-error" id="fbx-rate-error" hidden></div>' +
      '<button class="submit' + (state.L && state.P ? ' ready' : '') + '" id="fbx-rate-submit"' + (state.L && state.P ? '' : ' disabled') + '>' + esc(o.isEdit ? t('submit_edit') : t('submit')) + '</button>';
  }

  function rateDoneHtml(o) {
    o = o || {};
    return '<div class="m-head"><div><div class="name">' + esc(o.placeName || '') + '</div>' +
      '<div class="sub">' + esc(o.region || '') + '</div></div><button class="close" data-fbx-close>✕</button></div>' +
      '<div class="done"><div class="d1">✓ ' + esc(o.flagged ? t('flagged') : t('done1')) + '</div>' +
      '<div class="d2">' + esc(t('done2_fmt').replace('{L}', String(o.l)).replace('{P}', String(o.p))) + '</div>' +
      '<div class="d3">' + esc(o.flagged ? t('rep_done3') : t('done3')) + '</div>' +
      '<button data-fbx-close>' + esc(t('done_btn')) + '</button></div>';
  }

  /* report modal (mockup reportHTML + the ticket's optional photo_url field) */
  function reportHtml(o) {
    o = o || {};
    var types = RTYPES.map(function (p) {
      var d = t(p[0]);
      return '<button class="type" data-code="' + p[1] + '"><span class="ic">' + d[0] + '</span>' +
        '<span class="nm">' + esc(d[1]) + '</span><span class="en">' + esc(d[2]) + '</span></button>';
    }).join('');
    var who = o.maskedSelf || t('anon_fallback');
    return '<div class="m-head"><div><div class="name">🚩 ' + esc(t('rep_title')) + '</div>' +
      '<div class="sub">' + esc(t('rep_sub')) + '</div></div><button class="close" data-fbx-close>✕</button></div>' +
      '<div class="ctx"><span class="g">' + esc(o.placeName || '') + '</span><span style="color:var(--cl-text-3)">' + esc(o.region || '') + '</span></div>' +
      '<div class="types" id="fbx-rtypes">' + types + '</div>' +
      '<div style="font-size:var(--cl-fs-12);font-weight:600;margin-bottom:4px">' + esc(t('rep_desc')) + '</div>' +
      '<textarea class="txt-note" id="fbx-report-desc" maxlength="500" placeholder="' + esc(t('rep_ph')) + '"></textarea>' +
      '<div style="font-size:var(--cl-fs-12);font-weight:600;margin-bottom:4px">' + esc(t('rep_fix')) + '</div>' +
      '<input class="fix-input" id="fbx-report-fix" maxlength="300" placeholder="' + esc(t('rep_fix_ph')) + '">' +
      '<div style="font-size:var(--cl-fs-12);font-weight:600;margin-bottom:4px">' + esc(t('rep_photo')) + '</div>' +
      '<input class="fix-input" id="fbx-report-photo" maxlength="2000" placeholder="' + esc(t('rep_photo_ph')) + '">' +
      '<div class="anon"><span>🔒 ' + esc(t('anon')) + '</span><span class="who">' + esc(who) + '</span>' +
      '<span style="margin-left:auto;color:var(--cl-red-text);font-size:11px">' + esc(t('rep_private')) + '</span></div>' +
      '<div class="fbx-error" id="fbx-report-error" hidden></div>' +
      '<button class="submit" id="fbx-report-submit" disabled title="' + esc(t('need_desc')) + '">' + esc(t('rep_submit')) + '</button>';
  }

  function reportDoneHtml(o) {
    o = o || {};
    return '<div class="m-head"><div><div class="name">' + esc(o.placeName || '') + '</div>' +
      '<div class="sub">' + esc(o.region || '') + '</div></div><button class="close" data-fbx-close>✕</button></div>' +
      '<div class="done amber"><div class="d1">' + esc(t('rep_done1')) + ' ' + t('rep_done2') + '</div>' +
      '<div class="d3" style="margin-top:var(--cl-sp-2)">' + esc(o.flagged ? t('flagged') : t('rep_done3')) + '</div>' +
      '<button data-fbx-close>' + esc(t('done_btn')) + '</button></div>';
  }

  /* site comment (footer channel; first-review notice is the done copy) */
  function fbHtml(o) {
    o = o || {};
    var who = o.maskedSelf || t('anon_fallback');
    return '<div class="m-head"><div><div class="name">💬 ' + esc(t('fb_title')) + '</div>' +
      '<div class="sub">' + esc(t('fb_sub')) + '</div></div><button class="close" data-fbx-close>✕</button></div>' +
      '<textarea class="txt-note" id="fbx-fb-note" style="height:110px" maxlength="500" placeholder="' + esc(t('fb_sub')) + '"></textarea>' +
      '<div class="anon"><span>🔒 ' + esc(t('anon')) + '</span><span class="who">' + esc(who) + '</span></div>' +
      '<div class="fbx-error" id="fbx-fb-error" hidden></div>' +
      '<button class="submit" id="fbx-fb-submit" disabled>' + esc(t('fb_submit')) + '</button>';
  }

  function fbDoneHtml() {
    return '<div class="m-head"><div><div class="name">💬</div></div><button class="close" data-fbx-close>✕</button></div>' +
      '<div class="done amber"><div class="d1">✓ ' + esc(t('fb_done1')) + '</div>' +
      '<div class="d3" style="margin-top:var(--cl-sp-2)">' + esc(t('rep_done3')) + '</div>' +
      '<button data-fbx-close>' + esc(t('done_btn')) + '</button></div>';
  }

  function needLoginHtml() {
    return '<div class="m-head"><div><div class="name">' + esc(t('nl1')) + '</div>' +
      '<div class="sub">' + esc(t('nl2')) + '</div></div><button class="close" data-fbx-close>✕</button></div>' +
      '<div class="needlogin"><div class="n1">🔒</div><div class="n2">' + esc(t('nl2')) + '</div>' +
      '<div class="oauth"><a href="/api/v1/auth/line/start">LINE</a><a href="/api/v1/auth/google/start">Google</a></div></div>';
  }

  // ===========================================================================
  // Runtime
  // ===========================================================================

  var state = { enabled: false, booted: false, member: null, memberFetched: false };
  var aggCache = new Map();   // placeId -> {at, doc}
  var aggInflight = new Map();
  var mineCache = new Map();  // placeId -> {at, rating|null}
  var mineInflight = new Map();
  var AGG_TTL_MS = 60 * 1000;
  var scanTimer = null;

  function fixtures() { return window.__FBX_FIXTURES || null; }

  function api(path, opts) {
    var fx = fixtures();
    if (fx && fx.respond) return Promise.resolve(fx.respond(path, opts || {}));
    return fetch(path, Object.assign({ credentials: 'same-origin', cache: 'no-store' }, opts || {}));
  }

  function placeDisplayName(placeId) {
    // honest label from the rendered surface when available (card title)
    var card = document.querySelector('#spots-container .card[data-place-id="' + placeId + '"] .spot-name');
    return card ? card.textContent : placeId;
  }
  function placeRegion(placeId) {
    var card = document.querySelector('#spots-container .card[data-place-id="' + placeId + '"]');
    var el = card && card.querySelector('.category-tag');
    return el ? el.textContent : '';
  }

  function fetchAgg(placeId) {
    var hit = aggCache.get(placeId);
    if (hit && Date.now() - hit.at < AGG_TTL_MS) return Promise.resolve(hit.doc);
    if (aggInflight.has(placeId)) return aggInflight.get(placeId);
    var p = api(FB_ENDPOINT + '?place_id=' + encodeURIComponent(placeId)).then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.json();
    }).then(function (doc) {
      aggCache.set(placeId, { at: Date.now(), doc: doc });
      aggInflight.delete(placeId);
      return doc;
    }).catch(function () {
      aggInflight.delete(placeId);
      return null; // a failed read never renders a chip
    });
    aggInflight.set(placeId, p);
    return p;
  }

  function invalidateAgg(placeId) { aggCache.delete(placeId); mineCache.delete(placeId); }

  function fetchMine(placeId) {
    var hit = mineCache.get(placeId);
    if (hit && Date.now() - hit.at < AGG_TTL_MS) return Promise.resolve(hit.rating);
    if (mineInflight.has(placeId)) return mineInflight.get(placeId);
    var p = api(FB_ENDPOINT + '?mine=1&place_id=' + encodeURIComponent(placeId)).then(function (res) {
      if (!res.ok) return null;
      return res.json();
    }).then(function (doc) {
      var rating = (doc && doc.rating) || null;
      mineCache.set(placeId, { at: Date.now(), rating: rating });
      mineInflight.delete(placeId);
      return rating;
    }).catch(function () {
      mineInflight.delete(placeId);
      return null;
    });
    mineInflight.set(placeId, p);
    return p;
  }

  function currentMember() {
    if (state.memberFetched && state.member !== null) return Promise.resolve(state.member);
    var fx = fixtures();
    if (fx && fx.respond) {
      return Promise.resolve(fx.respond(ME_ENDPOINT, {})).then(function (res) {
        if (!res || !res.ok) { state.memberFetched = true; return null; }
        return res.json();
      }).then(function (doc) {
        state.member = parseMember(doc);
        state.memberFetched = true;
        return state.member;
      });
    }
    return api(ME_ENDPOINT, {}).then(function (res) {
      if (!res.ok) { state.memberFetched = true; return null; }
      return res.json();
    }).then(function (doc) {
      state.member = parseMember(doc);
      state.memberFetched = true;
      return state.member;
    }).catch(function () {
      state.memberFetched = true;
      return null;
    });
  }

  // Same semantics as member-auth.js parseMember: anything without a usable
  // display name counts as signed out.
  function parseMember(doc) {
    if (!doc || typeof doc !== 'object' || Array.isArray(doc)) return null;
    var u = (doc.user != null && typeof doc.user === 'object') ? doc.user : null;
    var raw = (u && u.displayName != null) ? u.displayName :
              (doc.display_name != null ? doc.display_name :
              (doc.name != null ? doc.name : (doc.sub != null ? doc.sub : null)));
    if (typeof raw !== 'string') return null;
    var name = raw.trim();
    return name ? { displayName: name } : null;
  }

  function maskedSelf(mineRating) {
    if (mineRating && mineRating.maskedName) return mineRating.maskedName;
    var m = state.member;
    if (m && m.displayName) return m.displayName.slice(0, 2) + '**';
    return t('anon_fallback');
  }

  // ---- card chips -----------------------------------------------------------
  function scheduleScan() {
    if (scanTimer) return;
    scanTimer = setTimeout(function () { scanTimer = null; scanCards(); }, 60);
  }

  function scanCards() {
    if (!state.enabled) return;
    var cards = document.querySelectorAll('#spots-container .card[data-place-id]');
    var wanted = [];
    for (var i = 0; i < cards.length; i++) {
      var card = cards[i];
      var placeId = card.getAttribute('data-place-id');
      if (!placeId) continue;
      var actions = card.querySelector('.card-header-actions');
      if (!actions || card.querySelector('span.r-chip')) continue;
      var chip = document.createElement('span');
      chip.className = 'clfb r-chip';
      chip.setAttribute('data-fbx-chip', '');
      chip.hidden = true; // hidden until the aggregate clears the gate
      var fav = actions.querySelector('[data-fav]');
      if (fav) actions.insertBefore(chip, fav); else actions.appendChild(chip);
      wanted.push(placeId);
    }
    wanted.forEach(function (placeId) {
      fetchAgg(placeId).then(function (doc) {
        if (!doc) return; // stays hidden — fail closed
        var hit = aggCache.get(placeId);
        paintChips(placeId, doc, hit ? hit.at : Date.now());
      });
    });
  }

  function paintChips(placeId, doc) {
    var html = chipHtml(doc);
    var chips = document.querySelectorAll('#spots-container .card[data-place-id="' + placeId + '"] span.r-chip');
    for (var i = 0; i < chips.length; i++) {
      var chip = chips[i];
      if (!html) { chip.hidden = true; chip.textContent = ''; continue; }
      chip.innerHTML = html;
      chip.hidden = false;
    }
    // an open evaluation section for this place refreshes with the same data
    refreshOpenEval(placeId);
  }

  // ---- evaluation sections (forecast modal + subject panel) ------------------
  var evalBox = null; // {host, placeId, section}

  function ensureSection(host, insertBefore) {
    var section = host.querySelector('.clfb[data-fbx-eval]');
    if (!section) {
      section = document.createElement('div');
      section.className = 'clfb';
      section.setAttribute('data-fbx-eval', '');
      if (insertBefore) host.insertBefore(section, insertBefore);
      else host.appendChild(section);
    }
    return section;
  }

  function refreshOpenEval(placeId) {
    if (!evalBox || !evalBox.section || evalBox.placeId !== placeId) return;
    renderEval(evalBox.section, placeId);
  }

  function renderEval(section, placeId) {
    section.setAttribute('data-fbx-rendered', '1');
    section.hidden = false;
    evalBox = { section: section, placeId: placeId };
    section.innerHTML = '';
    var memberP = currentMember();
    var mineP = memberP ? fetchMine(placeId) : Promise.resolve(null);
    Promise.all([fetchAgg(placeId), mineP, memberP]).then(function (r) {
      var agg = r[0], mine = r[1];
      if (!evalBox || evalBox.section !== section || evalBox.placeId !== placeId) return;
      if (!agg) { section.innerHTML = ''; section.hidden = true; return; } // API failure → nothing renders
      section.innerHTML = evalHtml(agg, mine, maskedSelf(mine));
      var openers = section.querySelectorAll('[data-fbx-open]');
      for (var i = 0; i < openers.length; i++) {
        openers[i].addEventListener('click', function (e) {
          e.preventDefault();
          e.stopPropagation();
          onEvalEntry(this.getAttribute('data-fbx-open'), placeId);
        });
      }
    });
  }

  function onEvalEntry(action, placeId) {
    if (action === 'rate-del') return deleteRating(placeId);
    if (action === 'report') return openReport(placeId);
    var isEdit = action === 'rate-edit';
    if (isEdit && !(mineCache.get(placeId) || {}).rating) return;
    openRate(placeId, isEdit);
  }

  // ---- overlays --------------------------------------------------------------
  function makeOverlay(id) {
    var ov = document.getElementById(id);
    if (ov) return ov;
    ov = document.createElement('div');
    ov.id = id;
    ov.className = 'clfb-overlay';
    ov.hidden = true;
    var modal = document.createElement('div');
    modal.className = 'clfb-modal clfb';
    ov.appendChild(modal);
    document.body.appendChild(ov);
    ov.addEventListener('click', function (e) {
      if (e.target === ov) closeOverlay(ov);
    });
    return ov;
  }

  function closeOverlay(ov) {
    ov.classList.remove('open');
    ov.hidden = true;
    ov.querySelector('.clfb-modal').innerHTML = '';
    // mirror app.js syncModalScrollLock: clear the lock only when no shell
    // modal sits underneath (the rate/report flows open from inside them).
    try {
      var shellOpen = ['place-modal-overlay', 'modal-overlay'].some(function (id) {
        var el = document.getElementById(id);
        return el && el.style.display === 'flex';
      });
      document.body.style.overflow = shellOpen ? 'hidden' : '';
    } catch (e) { /* shell owns the lock */ }
  }

  function showOverlay(id, html, bind) {
    var ov = makeOverlay(id);
    ov.querySelector('.clfb-modal').innerHTML = html;
    ov.hidden = false;
    ov.classList.add('open');
    var closes = ov.querySelectorAll('[data-fbx-close]');
    for (var i = 0; i < closes.length; i++) closes[i].addEventListener('click', function () { closeOverlay(ov); });
    if (bind) bind(ov);
    return ov;
  }

  function setError(ov, sel, key) {
    var el = ov.querySelector(sel);
    if (!el) return;
    el.textContent = t(key);
    el.hidden = false;
  }

  function requireMemberThen(placeId, fn) {
    currentMember().then(function (member) {
      if (!member) { showOverlay('fbx-login-overlay', needLoginHtml()); return; }
      fn(member);
    });
  }

  function openRate(placeId, isEdit) {
    requireMemberThen(placeId, function () {
      var mineP = isEdit ? fetchMine(placeId) : Promise.resolve((mineCache.get(placeId) || {}).rating || null);
      var selfP = currentMember().then(function () { return fetchMine(placeId); });
      Promise.all([mineP, selfP]).then(function (r) {
        var mine = r[0] || r[1] || null;
        showOverlay('fbx-rate-overlay', rateHtml({
          placeName: placeDisplayName(placeId),
          region: placeRegion(placeId),
          isEdit: isEdit,
          mine: mine,
          maskedSelf: maskedSelf(mine)
        }), function (ov) { bindRate(ov, placeId, !!isEdit && !!mine); });
      });
    });
  }

  function bindRate(ov, placeId, isEdit) {
    var rateState = { L: 0, P: 0 };
    var pre = ov.querySelector('#fbx-rate-note');
    if (isEdit) {
      var mine = (mineCache.get(placeId) || {}).rating;
      if (mine) { rateState.L = mine.l; rateState.P = mine.p; }
    }
    var submit = ov.querySelector('#fbx-rate-submit');
    ov.querySelectorAll('.lev').forEach(function (b) {
      b.addEventListener('click', function () {
        rateState[b.getAttribute('data-ax')] = Number(b.getAttribute('data-v'));
        var ax = b.getAttribute('data-ax');
        ov.querySelectorAll('.lev[data-ax="' + ax + '"]').forEach(function (x) { x.classList.toggle('sel', x === b); });
        var q = ov.querySelector(ax === 'L' ? '#fbx-q-l' : '#fbx-q-p');
        if (q) q.textContent = '★' + b.getAttribute('data-v');
        if (rateState.L && rateState.P) { submit.classList.add('ready'); submit.disabled = false; }
      });
    });
    submit.addEventListener('click', function () {
      if (!rateState.L || !rateState.P) return;
      var body = {
        type: 'rating',
        placeId: placeId,
        l: rateState.L,
        p: rateState.P,
        commentText: (pre && pre.value.trim()) || null
      };
      submit.disabled = true;
      api(FB_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      }).then(function (res) {
        return res.json().then(function (doc) { return { ok: res.ok, status: res.status, doc: doc }; });
      }).then(function (r) {
        if (!r.ok) { setError(ov, '#fbx-rate-error', 'error'); submit.disabled = false; return; }
        invalidateAgg(placeId);
        mineCache.delete(placeId);
        showOverlay('fbx-rate-overlay', rateDoneHtml({
          placeName: placeDisplayName(placeId),
          region: placeRegion(placeId),
          l: rateState.L,
          p: rateState.P,
          flagged: r.status === 202 || (r.doc && r.doc.status === 'flagged')
        }));
        fetchAgg(placeId).then(function (doc) { if (doc) paintChips(placeId, doc); });
      }).catch(function () {
        setError(ov, '#fbx-rate-error', 'error');
        submit.disabled = false;
      });
    });
  }

  function deleteRating(placeId) {
    requireMemberThen(placeId, function () {
      api(FB_ENDPOINT + '?place_id=' + encodeURIComponent(placeId), { method: 'DELETE' }).then(function (res) {
        invalidateAgg(placeId);
        if (evalBox && evalBox.placeId === placeId) renderEval(evalBox.section, placeId);
        fetchAgg(placeId).then(function (doc) { if (doc) paintChips(placeId, doc); });
      }).catch(function () { /* keep the current state — a failed delete changes nothing */ });
    });
  }

  function openReport(placeId) {
    requireMemberThen(placeId, function () {
      currentMember().then(function () { return fetchMine(placeId); }).then(function (mine) {
        showOverlay('fbx-report-overlay', reportHtml({
          placeName: placeDisplayName(placeId),
          region: placeRegion(placeId),
          maskedSelf: maskedSelf(mine)
        }), function (ov) { bindReport(ov, placeId); });
      });
    });
  }

  function bindReport(ov, placeId) {
    var reportType = null;
    var desc = ov.querySelector('#fbx-report-desc');
    var submit = ov.querySelector('#fbx-report-submit');
    function refreshReady() {
      var ready = !!reportType && desc && desc.value.trim().length > 0;
      submit.classList.toggle('ready', ready);
      submit.disabled = !ready;
    }
    ov.querySelectorAll('.type').forEach(function (b) {
      b.addEventListener('click', function () {
        reportType = b.getAttribute('data-code');
        ov.querySelectorAll('.type').forEach(function (x) { x.classList.toggle('sel', x === b); });
        refreshReady();
      });
    });
    if (desc) desc.addEventListener('input', refreshReady);
    submit.addEventListener('click', function () {
      if (!reportType || !desc.value.trim()) return;
      var photo = ov.querySelector('#fbx-report-photo');
      var body = {
        type: 'report',
        placeId: placeId,
        reportCategory: reportType,
        commentText: desc.value.trim(),
        fixSuggest: (ov.querySelector('#fbx-report-fix').value || '').trim() || null,
        photoUrl: photo && photo.value.trim() ? photo.value.trim() : null
      };
      submit.disabled = true;
      api(FB_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      }).then(function (res) {
        return res.json().then(function (doc) { return { ok: res.ok, status: res.status, doc: doc }; });
      }).then(function (r) {
        if (!r.ok) { setError(ov, '#fbx-report-error', 'error'); submit.disabled = false; return; }
        showOverlay('fbx-report-overlay', reportDoneHtml({
          placeName: placeDisplayName(placeId),
          region: placeRegion(placeId),
          flagged: r.status === 202 || (r.doc && r.doc.status === 'flagged')
        }));
      }).catch(function () {
        setError(ov, '#fbx-report-error', 'error');
        submit.disabled = false;
      });
    });
  }

  function openFb() {
    requireMemberThen(null, function () {
      currentMember().then(function () { return null; }).then(function () {
        showOverlay('fbx-fb-overlay', fbHtml({ maskedSelf: maskedSelf(null) }), function (ov) { bindFb(ov); });
      });
    });
  }

  function bindFb(ov) {
    var note = ov.querySelector('#fbx-fb-note');
    var submit = ov.querySelector('#fbx-fb-submit');
    function refreshReady() {
      var ready = !!(note && note.value.trim());
      submit.classList.toggle('ready', ready);
      submit.disabled = !ready;
    }
    if (note) note.addEventListener('input', refreshReady);
    submit.addEventListener('click', function () {
      if (!note.value.trim()) return;
      var body = { type: 'comment', commentText: note.value.trim() }; // no placeId = site feedback
      submit.disabled = true;
      api(FB_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      }).then(function (res) {
        return res.json().then(function (doc) { return { ok: res.ok, status: res.status, doc: doc }; });
      }).then(function (r) {
        if (!r.ok) { setError(ov, '#fbx-fb-error', 'error'); submit.disabled = false; return; }
        showOverlay('fbx-fb-overlay', fbDoneHtml());
      }).catch(function () {
        setError(ov, '#fbx-fb-error', 'error');
        submit.disabled = false;
      });
    });
  }

  // ---- surface wiring --------------------------------------------------------
  function overlayId(placeId) {
    var mo = document.getElementById('modal-overlay');
    var po = document.getElementById('place-modal-overlay');
    var moOpen = mo && mo.style.display === 'flex';
    var poOpen = po && po.style.display === 'flex';
    if (poOpen && po.getAttribute('data-place-id') === placeId) return po;
    if (moOpen && mo.getAttribute('data-place-id') === placeId) return mo;
    if (poOpen) return po;
    if (moOpen) return mo;
    return null;
  }

  function watchOverlay(overlayEl, host, insertBefore) {
    var lastPlace = null;
    function tick() {
      var open = overlayEl.style.display === 'flex';
      var placeId = overlayEl.getAttribute('data-place-id') || '';
      if (open && placeId) {
        if (placeId !== lastPlace) {
          lastPlace = placeId;
          var stale = host.querySelector('.clfb[data-fbx-eval]');
          if (stale) stale.remove();
          var section = ensureSection(host, insertBefore ? host.querySelector(insertBefore) : null);
          section.hidden = true;
          section.removeAttribute('data-fbx-rendered');
          section.innerHTML = '';
          renderEval(section, placeId);
        }
      } else if (!open) {
        lastPlace = null;
        var section2 = host.querySelector('.clfb[data-fbx-eval]');
        if (section2) { section2.remove(); }
        evalBox = null;
      }
    }
    new MutationObserver(tick).observe(overlayEl, { attributes: true, attributeFilter: ['style', 'data-place-id'] });
    // the place panel rewrites its body wholesale on every open/language switch:
    // a wiped section re-mounts and re-renders for the still-open place.
    new MutationObserver(function () {
      var placeId = overlayEl.getAttribute('data-place-id') || '';
      if (overlayEl.style.display !== 'flex' || !placeId) return;
      var section = host.querySelector('.clfb[data-fbx-eval]');
      if (!section || section.getAttribute('data-fbx-rendered') !== '1') {
        var fresh = ensureSection(host, insertBefore ? host.querySelector(insertBefore) : null);
        if (!fresh || fresh.getAttribute('data-fbx-rendered') !== '1') {
          fresh.hidden = true;
          renderEval(fresh, placeId);
        }
      }
    }).observe(host, { childList: true });
  }

  function watchCards() {
    var host = document.getElementById('spots-container');
    if (!host) return;
    new MutationObserver(scheduleScan).observe(host, { childList: true, subtree: true });
    scheduleScan();
  }

  function applyCopy() {
    var nodes = document.querySelectorAll('[data-fbx-i18n]');
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      var v = t(el.getAttribute('data-fbx-i18n'));
      if (v) el.textContent = v;
    }
  }

  function swapFooterEntry() {
    var old = document.getElementById('guest-comment-entry');
    var footer = old && old.closest('.guest-comment-footer');
    if (!footer) return;
    var mine = footer.querySelector('#fbx-foot-entry');
    if (!mine) {
      mine = document.createElement('button');
      mine.type = 'button';
      mine.id = 'fbx-foot-entry';
      mine.className = 'clfb foot-ugc';
      mine.setAttribute('data-fbx-open-fb', '');
      mine.setAttribute('aria-haspopup', 'dialog');
      var span = document.createElement('span');
      span.setAttribute('data-fbx-i18n', 'foot_feedback');
      span.textContent = t('foot_feedback');
      mine.textContent = '💬 ';
      mine.appendChild(span);
      footer.insertBefore(mine, old);
      mine.addEventListener('click', openFb);
    }
    old.hidden = true; // CL-DESIGN-7 §6.3 W2: the retired entry collapses while the new channel runs
  }

  function boot() {
    if (state.booted) return;
    state.booted = true;
    swapFooterEntry();
    watchCards();
    var mo = document.getElementById('modal-overlay');
    if (mo) watchOverlay(mo, mo.querySelector('.modal-body'), '#modal-provenance');
    var po = document.getElementById('place-modal-overlay');
    if (po) watchOverlay(po, document.getElementById('place-modal-body'), null);
    document.addEventListener('chaselights:auth', function (e) {
      var member = (e && e.detail && e.detail.member) ? e.detail.member : null;
      state.member = member;
      state.memberFetched = true;
      // identity changed → the per-place "mine" answers are stale
      mineCache.clear();
      scheduleScan();
    });
    var langSel = document.getElementById('lang-select');
    if (langSel) langSel.addEventListener('change', function () {
      applyCopy();
      scheduleScan();
      if (evalBox && evalBox.section && evalBox.placeId) renderEval(evalBox.section, evalBox.placeId);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      ['fbx-rate-overlay', 'fbx-report-overlay', 'fbx-fb-overlay', 'fbx-login-overlay'].forEach(function (id) {
        var ov = document.getElementById(id);
        if (ov && ov.classList.contains('open')) closeOverlay(ov);
      });
    });
  }

  function init() {
    var fx = fixtures();
    if (fx && fx.config) {
      if (fx.config.enabled) { state.enabled = true; boot(); }
      return;
    }
    fetch(CFG_ENDPOINT, { credentials: 'same-origin', cache: 'no-store' }).then(function (res) {
      if (!res.ok) return null; // 404 (pre-config deploy) / 403 (off) → hidden, fail closed
      return res.json();
    }).then(function (doc) {
      if (doc && doc.enabled === true) {
        state.enabled = true;
        boot();
      }
    }).catch(function () { /* offline → hidden */ });
  }

  // test/screenshot surface (pure renderers + gate state)
  window.ChaseLightsFeedback = {
    isEnabled: function () { return state.enabled; },
    refresh: scheduleScan,
    chipHtml: chipHtml,
    evalHtml: evalHtml,
    rateHtml: rateHtml,
    rateDoneHtml: rateDoneHtml,
    reportHtml: reportHtml,
    reportDoneHtml: reportDoneHtml,
    fbHtml: fbHtml,
    fbDoneHtml: fbDoneHtml,
    needLoginHtml: needLoginHtml
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
