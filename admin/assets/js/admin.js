(function () {
  'use strict';

  /* ---------- Per-store mock data (header switcher) ---------- */
  var STORES = {
    fur:   { name: 'LUXEFUR',     visitors: '84,291', orders: '2,487', revenue: '$1.62M', cvr: '2.95%',
             rev: [42, 55, 48, 63, 70, 66, 78, 84, 80, 92] },
    pet:   { name: 'PAWMAISON',   visitors: '51,038', orders: '3,142', revenue: '$486K',  cvr: '3.42%',
             rev: [30, 38, 44, 41, 52, 58, 55, 63, 69, 74] },
    sport: { name: 'CUPID SPORT', visitors: '127,654', orders: '8,930', revenue: '$392K', cvr: '4.10%',
             rev: [48, 52, 60, 58, 67, 72, 70, 81, 88, 95] }
  };
  var WEEKS = ['W1','W2','W3','W4','W5','W6','W7','W8','W9','W10'];

  /* ---------- Section switching ---------- */
  var navItems = document.querySelectorAll('.nav-item');
  var pages = document.querySelectorAll('.page');

  function showPage(target) {
    pages.forEach(function (p) { p.classList.toggle('is-active', p.id === 'page-' + target); });
    navItems.forEach(function (n) { n.classList.toggle('is-active', n.dataset.target === target); });
    closeSidebar();
    var content = document.querySelector('.content');
    if (content) content.scrollIntoView({ block: 'start' });
  }

  // Any element with data-target switches pages (sidebar + "View All" + jumps)
  document.querySelectorAll('[data-target]').forEach(function (el) {
    el.addEventListener('click', function () { showPage(el.dataset.target); });
  });

  /* ---------- Store switcher ---------- */
  var storeSelect = document.getElementById('storeSelect');
  var ctxStore = document.getElementById('ctxStore');

  function renderChart(values) {
    var chart = document.getElementById('revChart');
    if (!chart) return;
    var max = Math.max.apply(null, values);
    chart.innerHTML = values.map(function (v, i) {
      var h = Math.round((v / max) * 100);
      return '<div class="chart-col" title="' + WEEKS[i] + ': ' + v + 'k">' +
             '<div class="chart-bar" style="height:' + h + '%"></div>' +
             '<span class="chart-x">' + WEEKS[i] + '</span></div>';
    }).join('');
  }

  function paint(name, kpis, rev) {
    if (ctxStore) ctxStore.textContent = name;
    Object.keys(kpis).forEach(function (k) {
      var el = document.querySelector('[data-kpi="' + k + '"]');
      if (el) el.textContent = kpis[k];
    });
    renderChart(rev);
  }

  function applyStore(key) {
    var s = STORES[key];
    if (!s) return;
    // Optimistic paint from local mock, then hydrate from the backend data API.
    paint(s.name, { visitors: s.visitors, orders: s.orders, revenue: s.revenue, cvr: s.cvr }, s.rev);
    var base = window.SHOPAGENT_API || '';
    fetch(base + '/api/dashboard?store=' + key, { credentials: 'same-origin' })
      .then(function (r) { if (!r.ok) throw 0; return r.json(); })
      .then(function (d) {
        if (storeSelect && storeSelect.value !== key) return; // stale response
        paint(d.store.name, d.kpis, d.revenue_series);
      })
      .catch(function () { /* backend offline — keep mock values */ });
  }

  if (storeSelect) {
    storeSelect.addEventListener('change', function () { applyStore(storeSelect.value); });
  }

  // "查看数据" on a store tile → switch store + jump to dashboard
  document.querySelectorAll('[data-store-jump]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var key = btn.dataset.storeJump;
      if (storeSelect) storeSelect.value = key;
      applyStore(key);
      showPage('dashboard');
    });
  });

  /* ---------- Mobile sidebar ---------- */
  var sidebar = document.getElementById('sidebar');
  var menuBtn = document.getElementById('menuBtn');
  var backdrop = document.getElementById('sidebarBackdrop');

  function closeSidebar() { if (sidebar) sidebar.classList.remove('is-open'); }
  if (menuBtn) menuBtn.addEventListener('click', function () { sidebar.classList.toggle('is-open'); });
  if (backdrop) backdrop.addEventListener('click', closeSidebar);

  /* ---------- Floating Copilot ---------- */
  var copilot = document.getElementById('copilot');
  var copilotFab = document.getElementById('copilotFab');
  var copilotClose = document.getElementById('copilotClose');

  if (copilotFab) copilotFab.addEventListener('click', function () { copilot.classList.toggle('is-open'); });
  if (copilotClose) copilotClose.addEventListener('click', function () { copilot.classList.remove('is-open'); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && copilot) copilot.classList.remove('is-open'); });
  // Copilot send/stream is handled by the shared client (/shared/chat.js),
  // which calls the backend /api/chat and falls back to a canned message offline.

  /* ---------- Init ---------- */
  applyStore('fur');
})();
