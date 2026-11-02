/* ============================================================
   case.js · 演示页渐进增强
   ------------------------------------------------------------
   各页 demo 由内联脚本渲染，这里不改它们的逻辑，只做三件事：
   1) 给「标签组」补 ARIA tabs 语义 + 左右方向键切换
   2) 给可展开的工具卡补 button 语义 + Enter/Space
   3) 给日志容器补 aria-live，让读屏能听到运行过程
   用 MutationObserver 跟随 demo 重渲染，reset 后语义不丢。
   ============================================================ */
(function () {
  'use strict';
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  var TAB_ATTRS = ['data-t', 'data-m', 'data-s', 'data-mode', 'data-idx', 'data-k'];

  function tabKey(el) {
    for (var i = 0; i < TAB_ATTRS.length; i++) {
      if (el.hasAttribute(TAB_ATTRS[i])) return TAB_ATTRS[i];
    }
    return null;
  }

  function upgradeTabs(root) {
    var all = $$('.chips .chip', root);
    var groups = {};
    all.forEach(function (el) {
      var key = tabKey(el);
      if (!key) return;
      (groups[key] = groups[key] || []).push(el);
    });
    Object.keys(groups).forEach(function (key) {
      var tabs = groups[key];
      var list = tabs[0].parentElement;
      if (!list || list.getAttribute('role') === 'tablist') return;
      list.setAttribute('role', 'tablist');
      if (!list.getAttribute('aria-label')) list.setAttribute('aria-label', '演示视图');
      tabs.forEach(function (t, i) {
        var on = t.classList.contains('on');
        t.setAttribute('role', 'tab');
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        t.addEventListener('keydown', function (e) {
          if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight' && e.key !== 'Home' && e.key !== 'End') return;
          e.preventDefault();
          var next = i;
          if (e.key === 'ArrowRight') next = (i + 1) % tabs.length;
          if (e.key === 'ArrowLeft') next = (i + tabs.length - 1) % tabs.length;
          if (e.key === 'Home') next = 0;
          if (e.key === 'End') next = tabs.length - 1;
          tabs[next].focus();
          tabs[next].click();
        });
      });
      // 选中态变化时同步 aria-selected / tabindex
      var sync = function () {
        tabs.forEach(function (t) {
          var on = t.classList.contains('on');
          t.setAttribute('aria-selected', String(on));
          t.tabIndex = on ? 0 : -1;
        });
      };
      tabs.forEach(function (t) { t.addEventListener('click', sync); t.addEventListener('keydown', sync); });
    });
  }

  function upgradePanels(root) {
    var panes = $$('[data-pane]', root);
    panes.forEach(function (p, i) {
      p.setAttribute('role', 'tabpanel');
      var tabs = $$('[role="tab"]', root);
      if (tabs[i] && !p.hasAttribute('aria-labelledby')) {
        if (!tabs[i].id) tabs[i].id = 'case-tab-' + i;
        p.setAttribute('aria-labelledby', tabs[i].id);
      }
    });
  }

  function upgradeTools(root) {
    $$('[data-tool], [data-row]', root).forEach(function (el) {
      if (el.tagName === 'BUTTON') return;
      if (!el.hasAttribute('role')) el.setAttribute('role', 'button');
      el.tabIndex = 0;
      el.addEventListener('keydown', function (e) {
        if (e.key !== 'Enter' && e.key !== ' ') return;
        e.preventDefault();
        el.click();
      });
    });
  }

  function upgradeLive(root) {
    $$('[data-line], [data-out], [data-flow], [data-log], [data-trace], [data-feed], [data-fout], [data-o0], [data-o1], [data-o2]', root).forEach(function (el) {
      if (!el.hasAttribute('aria-live')) el.setAttribute('aria-live', 'polite');
    });
    // 逐行追加的日志：只给最外层容器加播报，避免每行都念一遍
    $$('.demo-log', root).forEach(function (el) {
      var host = el.parentElement;
      if (!host || host.closest('[aria-live]')) return;
      var siblings = host.querySelectorAll(':scope > .demo-log');
      if (siblings.length > 1) host.setAttribute('aria-live', 'polite');
      else if (!el.hasAttribute('aria-live')) el.setAttribute('aria-live', 'polite');
    });
  }

  function upgrade(root) {
    if (!root) return;
    upgradeTabs(root);
    upgradePanels(root);
    upgradeTools(root);
    upgradeLive(root);
  }

  function boot() {
    upgrade(document);
    var stage = document.getElementById('stage');
    if (!stage || !window.MutationObserver) return;
    var scheduled = false;
    new MutationObserver(function () {
      if (scheduled) return;
      scheduled = true;
      window.requestAnimationFrame(function () {
        scheduled = false;
        upgrade(stage);
      });
    }).observe(stage, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();


/* 返回目录：优先浏览器后退——用户从首页点进来时，后退能原样回到刚才的滚动位置；
   直接打开案例页（referrer 非本站）或历史为空时，退回普通跳转 ../ 不变。 */
(function wireBackToHome() {
  'use strict';
  var back = document.querySelector('.case-nav-bar a[href="../"]');
  if (!back) return;
  back.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    if (history.length < 2) return;
    var same = false;
    try {
      same = !!document.referrer && new URL(document.referrer).origin === location.origin;
    } catch (_) {}
    if (!same) return;
    e.preventDefault();
    history.back();
  });
})();
