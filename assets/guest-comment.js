/* CL-UI-52: guest comment widget (homepage footer entry → modal → POST to
   the owner-deployed Apps Script bridge, action='comment').
   Self-contained on purpose: the main assets/app.js is heavily test-pinned,
   so this widget ships its own trilingual copy and never edits it.
   OWNER STEP after deploying the bridge (see templates/gas_sheet_bridge.js):
   paste the Web-app /exec URL into GC_ENDPOINT below. Leave it '' to keep
   the entry present but inert. The URL contains no secret. */
(function () {
  'use strict';

  var GC_ENDPOINT = ''; // TODO(owner): paste your Apps Script Web App /exec URL here (e.g. 'https://script.google.com/macros/s/AKfyc.../exec')

  var GC_I18N = {
    'zh-TW': {
      gc_entry: '💬 留言',
      gc_title: '💬 留言給站長',
      gc_close: '關閉留言',
      gc_nickname: '暱稱（可選）',
      gc_message: '留言內容',
      gc_cancel: '取消',
      gc_submit: '送出留言',
      gc_sending: '送出中…',
      gc_ok: '已送出，謝謝你的留言！',
      gc_err_empty: '請先寫一點內容再送出。',
      gc_err_network: '送出失敗，請稍後再試。',
      gc_err_disabled: '留言功能尚未啟用。',
      gc_chars: '／{max} 字'
    },
    'en': {
      gc_entry: '💬 Feedback',
      gc_title: '💬 Leave a comment',
      gc_close: 'Close comment form',
      gc_nickname: 'Name (optional)',
      gc_message: 'Your message',
      gc_cancel: 'Cancel',
      gc_submit: 'Send comment',
      gc_sending: 'Sending…',
      gc_ok: 'Sent — thanks for your comment!',
      gc_err_empty: 'Please write a message first.',
      gc_err_network: 'Send failed — please try again later.',
      gc_err_disabled: 'Comments are not enabled yet.',
      gc_chars: '/{max} chars'
    },
    'ja': {
      gc_entry: '💬 コメント',
      gc_title: '💬 コメントを送る',
      gc_close: 'コメントフォームを閉じる',
      gc_nickname: '名前（任意）',
      gc_message: 'コメント本文',
      gc_cancel: 'キャンセル',
      gc_submit: 'コメントを送信',
      gc_sending: '送信中…',
      gc_ok: '送信しました。ありがとうございます！',
      gc_err_empty: 'コメントを入力してください。',
      gc_err_network: '送信に失敗しました。しばらくしてからお試しください。',
      gc_err_disabled: 'コメント機能はまだ有効ではありません。',
      gc_chars: '／{max} 文字'
    }
  };

  function gcLang() {
    var sel = document.getElementById('lang-select');
    var v = (sel && typeof sel.value === 'string' && sel.value) ||
            localStorage.getItem('chaselights_lang') || 'zh-TW';
    return GC_I18N[v] ? v : 'zh-TW';
  }

  function t(key) {
    var pack = GC_I18N[gcLang()];
    return (pack && pack[key]) || GC_I18N['zh-TW'][key] || '';
  }

  function applyCopy() {
    var nodes = document.querySelectorAll('[data-gc-i18n]');
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      var v = t(el.getAttribute('data-gc-i18n'));
      if (v) el.textContent = v;
    }
    var aria = document.querySelectorAll('[data-gc-i18n-aria-label]');
    for (var j = 0; j < aria.length; j++) {
      var el2 = aria[j];
      var v2 = t(el2.getAttribute('data-gc-i18n-aria-label'));
      if (v2) el2.setAttribute('aria-label', v2);
    }
    updateCounters();
  }

  var overlay, form, statusEl, hp, nick, msg, submitBtn;
  var nickCount, msgCount;

  function updateCounters() {
    if (!nickCount) return;
    nickCount.textContent = nick.value ? nick.value.length + t('gc_chars').replace('{max}', '20') : '';
    msgCount.textContent = msg.value ? msg.value.length + t('gc_chars').replace('{max}', '500') : '';
  }

  function setStatus(key, state) {
    statusEl.textContent = t(key);
    statusEl.setAttribute('data-gc-state', state);
  }

  function openModal() {
    overlay.hidden = false;
    setStatus('', '');
    statusEl.textContent = '';
    statusEl.removeAttribute('data-gc-state');
    applyCopy();
    nick.focus();
  }

  function closeModal() {
    overlay.hidden = true;
  }

  function onEsc(e) {
    if (e.key === 'Escape' && overlay && !overlay.hidden) closeModal();
  }

  function init() {
    overlay = document.getElementById('guest-comment-overlay');
    if (!overlay) return;
    form = document.getElementById('guest-comment-form');
    statusEl = document.getElementById('gc-status');
    hp = document.getElementById('gc-hp');
    nick = document.getElementById('gc-nickname');
    msg = document.getElementById('gc-message');
    submitBtn = document.getElementById('guest-comment-submit');
    nickCount = document.getElementById('gc-nickname-count');
    msgCount = document.getElementById('gc-message-count');

    var entry = document.getElementById('guest-comment-entry');
    var closeBtn = document.getElementById('guest-comment-close');
    var cancelBtn = document.getElementById('guest-comment-cancel');

    if (entry) entry.addEventListener('click', openModal);
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);
    document.addEventListener('keydown', onEsc);
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeModal();
    });

    nick.addEventListener('input', updateCounters);
    msg.addEventListener('input', updateCounters);

    var langSel = document.getElementById('lang-select');
    if (langSel) langSel.addEventListener('change', function () {
      localStorage.setItem('chaselights_lang', langSel.value);
      applyCopy();
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!GC_ENDPOINT) { setStatus('gc_err_disabled', 'error'); return; }
      var text = msg.value.trim();
      if (!text) { setStatus('gc_err_empty', 'error'); return; }
      if (hp.value) { closeModal(); return; } // honeypot: silently drop bots
      var payload = {
        action: 'comment',
        nickname: nick.value.trim().slice(0, 20),
        message: text.slice(0, 500),
        lang: gcLang(),
        ua: navigator.userAgent || ''
      };
      submitBtn.disabled = true;
      setStatus('gc_sending', '');
      fetch(GC_ENDPOINT, {
        method: 'POST',
        mode: 'no-cors',
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify(payload)
      }).then(function () {
        // no-cors responses are opaque; treat resolve as accepted.
        form.reset();
        updateCounters();
        setStatus('gc_ok', 'ok');
        window.setTimeout(function () {
          if (!overlay.hidden) closeModal();
        }, 2500);
      }).catch(function () {
        submitBtn.disabled = false;
        setStatus('gc_err_network', 'error');
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
