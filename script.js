/* =========================================================
   ACA Certification Hub — state search / filter
   Vanilla JS, no dependencies. Progressive enhancement:
   all cards exist in HTML; this only filters the view.
   ========================================================= */
(function () {
  'use strict';

  // Footer year
  var yearEl = document.getElementById('year');
  if (yearEl) { yearEl.textContent = new Date().getFullYear(); }

  var input = document.getElementById('state-search');
  var grid = document.getElementById('state-grid');
  if (!input || !grid) { return; }

  var cards = Array.prototype.slice.call(grid.querySelectorAll('.state-card'));
  var countEl = document.getElementById('search-count');
  var noResults = document.getElementById('no-results');
  var noResultsTerm = document.getElementById('no-results-term');
  var clearBtn = document.getElementById('search-clear');
  var total = cards.length;

  // Build a lowercase search index for each card
  cards.forEach(function (card) {
    var name = (card.getAttribute('data-name') || '').toLowerCase();
    var abbr = (card.getAttribute('data-abbr') || '').toLowerCase();
    var alt = (card.getAttribute('data-alt') || '').toLowerCase();
    var market = (card.querySelector('.state-market') || {}).textContent || '';
    card._searchName = name;
    card._searchAbbr = abbr;
    card._searchText = (name + ' ' + abbr + ' ' + alt + ' ' + market.toLowerCase()).trim();
  });

  function setCount(shown, term) {
    if (!countEl) { return; }
    if (!term) {
      countEl.textContent = 'Showing all ' + total + ' state-based jurisdictions.';
    } else if (shown === 0) {
      countEl.textContent = 'No matches for "' + term + '".';
    } else {
      countEl.textContent = 'Showing ' + shown + ' of ' + total + ' jurisdictions.';
    }
  }

  function filter() {
    var raw = input.value.trim();
    var q = raw.toLowerCase();
    var shown = 0;

    cards.forEach(function (card) {
      var match;
      if (!q) {
        match = true;
      } else if (q.length <= 2) {
        // short query: match abbreviation exactly/prefix, or name start
        match = card._searchAbbr === q ||
                card._searchAbbr.indexOf(q) === 0 ||
                card._searchName.indexOf(q) === 0;
      } else {
        match = card._searchText.indexOf(q) !== -1;
      }
      card.classList.toggle('is-hidden', !match);
      if (match) { shown++; }
    });

    if (noResults) {
      var none = q && shown === 0;
      noResults.hidden = !none;
      if (none && noResultsTerm) { noResultsTerm.textContent = raw; }
    }
    if (clearBtn) { clearBtn.hidden = !raw; }
    setCount(shown, raw);
  }

  var t;
  input.addEventListener('input', function () {
    clearTimeout(t);
    t = setTimeout(filter, 80);
  });

  // Enter with a single visible match: focus its first link for fast keyboard flow
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') {
      var visible = cards.filter(function (c) { return !c.classList.contains('is-hidden'); });
      if (visible.length === 1) {
        var link = visible[0].querySelector('.state-links a');
        if (link) { e.preventDefault(); link.focus(); }
      }
    }
  });

  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      input.value = '';
      filter();
      input.focus();
    });
  }

  // Initialize
  setCount(total, '');
})();
