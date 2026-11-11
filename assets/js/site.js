/* Small progressive enhancements. Every page works without this file. */
(function () {
  'use strict';

  /* ---------- 1. Job list filter (pages with a job table) ---------- */
  function setupFilter() {
    var main = document.getElementById('main');
    if (!main || !main.classList.contains('wide')) return;
    var tables = Array.prototype.slice.call(main.querySelectorAll('table')).filter(function (t) {
      var head = t.querySelector('thead');
      return head && /company/i.test(head.textContent) && /role/i.test(head.textContent);
    });
    if (!tables.length) return;

    // Rows are indexed on first use, not at page load, so long lists stay fast to open.
    var rows = null, total = 0;
    tables.forEach(function (t) { total += t.querySelectorAll('tbody tr').length; });
    function index() {
      if (rows) return;
      rows = [];
      tables.forEach(function (t) {
      var heads = Array.prototype.map.call(t.querySelectorAll('thead th'), function (th) { return th.textContent.trim().toLowerCase(); });
      var tagCol = heads.indexOf('tags');
      Array.prototype.forEach.call(t.querySelectorAll('tbody tr'), function (tr) {
        var cells = tr.children;
        var tags = tagCol >= 0 && cells[tagCol] ? cells[tagCol].textContent.toLowerCase() : '';
        var text = '';
        for (var i = 0; i < cells.length; i++) if (i !== tagCol) text += ' ' + cells[i].textContent;
        rows.push({ el: tr, text: text.toLowerCase(), tags: tags, show: true });
      });
      });
    }

    var bar = document.createElement('form');
    bar.className = 'filter-bar';
    bar.setAttribute('role', 'search');
    bar.setAttribute('aria-label', 'Filter jobs');
    bar.innerHTML =
      '<div class="filter-field">' +
        '<label for="job-q">Filter jobs</label>' +
        '<input id="job-q" type="search" autocomplete="off" spellcheck="false" placeholder="Company, role or city (e.g. Texas, embedded, Google)">' +
      '</div>' +
      '<div class="filter-toggles">' +
        '<label class="toggle"><input type="checkbox" id="job-open"> Hide citizens-only, clearance, ITAR and gov roles</label>' +
        '<label class="toggle"><input type="checkbox" id="job-remote"> Remote only</label>' +
        '<label class="toggle"><input type="checkbox" id="job-term"> Co-op, fall, spring or part-time only</label>' +
      '</div>' +
      '<p class="filter-status" id="job-count" role="status" aria-live="polite"></p>';
    var slot = document.getElementById('job-filter');
    if (slot) slot.appendChild(bar); else tables[0].parentNode.insertBefore(bar, tables[0]);

    var q = bar.querySelector('#job-q'), open = bar.querySelector('#job-open'),
        remote = bar.querySelector('#job-remote'), term = bar.querySelector('#job-term'),
        count = bar.querySelector('#job-count');

    // Restore from the URL so a filtered list can be shared (?q=texas&remote=1).
    var params = new URLSearchParams(location.search);
    q.value = params.get('q') || '';
    open.checked = params.get('open') === '1';
    remote.checked = params.get('remote') === '1';
    term.checked = params.get('term') === '1';

    var RESTRICTED = /citizens|clearance|secret|ts\/sci|public trust|itar|\bgov\b/;
    var TERMS = /co-op|fall|spring|part-time/;
    var timer = null;

    function apply() {
      index();
      var words = q.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
      var shown = 0;
      // Decide every row first, then write once per row (no layout reads in between).
      for (var i = 0; i < rows.length; i++) {
        var r = rows[i], ok = true;
        for (var w = 0; ok && w < words.length; w++) if (r.text.indexOf(words[w]) === -1 && r.tags.indexOf(words[w]) === -1) ok = false;
        if (ok && open.checked && RESTRICTED.test(r.tags)) ok = false;
        if (ok && remote.checked && r.tags.indexOf('remote') === -1 && r.text.indexOf('remote') === -1) ok = false;
        if (ok && term.checked && !TERMS.test(r.tags)) ok = false;
        r.next = ok;
        if (ok) shown++;
      }
      // Write only rows whose visibility changed (one batch of writes, no reads).
      for (var j = 0; j < rows.length; j++) {
        if (rows[j].next !== rows[j].show) { rows[j].show = rows[j].next; rows[j].el.hidden = !rows[j].show; }
      }
      var filtered = words.length || open.checked || remote.checked || term.checked;
      count.textContent = filtered ? 'Showing ' + shown + ' of ' + total + ' jobs' : total + ' jobs';

      var p = new URLSearchParams();
      if (q.value.trim()) p.set('q', q.value.trim());
      if (open.checked) p.set('open', '1');
      if (remote.checked) p.set('remote', '1');
      if (term.checked) p.set('term', '1');
      var qs = p.toString();
      try { history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash); } catch (e) { /* file:// or sandboxed */ }
    }
    function later() { clearTimeout(timer); timer = setTimeout(apply, 150); }

    q.addEventListener('input', later);
    [open, remote, term].forEach(function (c) { c.addEventListener('change', apply); });
    bar.addEventListener('submit', function (e) { e.preventDefault(); apply(); });
    q.addEventListener('keydown', function (e) { if (e.key === 'Escape' && q.value) { q.value = ''; apply(); } });
    // Only filter at load when the URL asks for it; otherwise just show the count.
    if (q.value || open.checked || remote.checked || term.checked) apply();
    else count.textContent = total + ' jobs';
    q.addEventListener('focus', function () {
      if ('requestIdleCallback' in window) requestIdleCallback(index); else setTimeout(index, 0);
    }, { once: true });
  }

  /* ---------- 2. Copy buttons on message templates in the guides ---------- */
  function setupCopy() {
    if (!navigator.clipboard || location.pathname.indexOf('/guides/') === -1) return;
    var quotes = document.querySelectorAll('#main blockquote');
    Array.prototype.forEach.call(quotes, function (bq) {
      var text = bq.innerText.trim();
      if (text.length < 60 || !/\[[^\]]+\]/.test(text)) return; // only fill-in-the-blank templates
      var wrap = document.createElement('div');
      wrap.className = 'copy-row';
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'copy-btn';
      btn.textContent = 'Copy template';
      var status = document.createElement('span');
      status.className = 'copy-status';
      status.setAttribute('role', 'status');
      btn.addEventListener('click', function () {
        navigator.clipboard.writeText(text).then(function () {
          status.textContent = 'Copied. Replace the [brackets] before you send it.';
        }, function () {
          status.textContent = 'Copy failed. Select the text and copy it instead.';
        });
      });
      wrap.appendChild(btn);
      wrap.appendChild(status);
      bq.parentNode.insertBefore(wrap, bq.nextSibling);
    });
  }

  /* ---------- 3. Wide guide tables: reachable by keyboard when they scroll sideways ---------- */
  function setupScrollTables() {
    if (location.pathname.indexOf('/guides/') === -1) return; // job tables have links, so they're already reachable
    var tables = document.querySelectorAll('#main table');
    // Read all widths first, then write (no interleaved layout reads and writes).
    var wide = Array.prototype.filter.call(tables, function (t) { return t.scrollWidth > t.clientWidth + 1; });
    wide.forEach(function (t) {
      if (t.querySelector('a, button, input')) return;
      var h = t.previousElementSibling;
      while (h && !/^H[2-4]$/.test(h.tagName)) h = h.previousElementSibling;
      t.setAttribute('tabindex', '0');
      t.setAttribute('role', 'region');
      t.setAttribute('aria-label', (h ? h.textContent.trim() + ' ' : '') + 'table (scrolls sideways)');
    });
  }

  function init() { setupFilter(); setupCopy(); setupScrollTables(); }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
