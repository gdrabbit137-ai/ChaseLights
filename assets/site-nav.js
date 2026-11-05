/* CL-UI-28: shared site-nav behavior — the 更多工具 collapsed menu.
   One file, included by all four pages; the nav DOM is static per page
   (active state is baked into the HTML), so this script only owns the menu. */
(function () {
  'use strict';
  function initSiteNav() {
    const more = document.querySelector('[data-nav-more]');
    if (!more) return;
    const btn = more.querySelector('.site-nav-more-btn');
    const menu = more.querySelector('.site-nav-menu');
    if (!btn || !menu) return;
    function close() {
      menu.hidden = true;
      btn.setAttribute('aria-expanded', 'false');
    }
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      const open = menu.hidden;
      menu.hidden = !open;
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('click', function (e) {
      if (!more.contains(e.target)) close();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') close();
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSiteNav);
  } else {
    initSiteNav();
  }
})();
