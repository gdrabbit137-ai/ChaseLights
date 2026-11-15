/* CL-UI-101: site-wide footer — 「資料來源與授權」 link (the commercial-
   compliance attribution hub, sources.html) + a one-line shooting-safety
   disclaimer. Self-contained widget (own trilingual pack, reads the shared
   chaselights_lang localStorage key — same convention as guest-comment.js /
   member-auth.js); never edits app.js. The footer MARKUP is static in each
   page's HTML (data-sf-i18n attributes); this script only owns the injected
   style block (the weather-map page does not load app.css, so no --cl-*
   tokens are used here — alpha-white literals like guest-comment.css) and
   the translation pass. */
(function () {
  'use strict';
  var PACK = {
    sf_sources: { 'zh-TW': '資料來源與授權', en: 'Data sources & licenses', ja: 'データソースとライセンス' },
    sf_note: { 'zh-TW': '氣象資料僅供參考，拍攝安全請自行評估。', en: 'Weather data is for reference only — assess shooting safety yourself.', ja: '気象データは参考情報です。撮影の安全はご自身でご確認ください。' }
  };
  var STYLE = [
    '.site-footer{text-align:center;padding:6px 0 18px;margin-top:10px;border-top:1px solid rgba(255,255,255,0.08)}',
    '.site-footer-link{display:inline-block;color:#9aa3ad;font-size:0.78rem;padding:5px 14px;min-height:32px;line-height:22px;text-decoration:none}',
    '.site-footer-link:hover,.site-footer-link:focus-visible{color:#d8dee5;text-decoration:underline}',
    '.site-footer-note{display:block;color:#6f7780;font-size:0.72rem;margin-top:2px}',
    '@media (max-width:390px){.site-footer{padding:4px 10px 16px}.site-footer-link{font-size:0.75rem}}'
  ].join('\n');
  function lang() {
    try { return localStorage.getItem('chaselights_lang') || 'zh-TW'; } catch (e) { return 'zh-TW'; }
  }
  function t(k) { var e = PACK[k]; return e ? (e[lang()] || e['zh-TW']) : k; }
  function ensureStyle() {
    if (document.getElementById('cl-site-footer-style')) return;
    var s = document.createElement('style');
    s.id = 'cl-site-footer-style';
    s.textContent = STYLE;
    document.head.appendChild(s);
  }
  function apply() {
    var nodes = document.querySelectorAll('[data-sf-i18n]');
    for (var i = 0; i < nodes.length; i++) {
      var v = t(nodes[i].getAttribute('data-sf-i18n'));
      if (v) nodes[i].textContent = v;
    }
  }
  function init() {
    ensureStyle();
    apply();
    // Language switchers on the host pages (index / genre-eval / reminders
    // render #lang-select): re-translate when the user changes the language.
    document.addEventListener('change', function (e) {
      if (e.target && e.target.id === 'lang-select') apply();
    });
    // Other tabs / ?lang= handoffs write the shared key — pick them up too.
    window.addEventListener('storage', function (e) {
      if (!e.key || e.key === 'chaselights_lang') apply();
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
