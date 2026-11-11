(function () {
  var grid = document.getElementById('dir-grid');
  if (!grid) return;
  var cards = [].slice.call(grid.querySelectorAll('.dir-city'));
  var tabs = [].slice.call(document.querySelectorAll('.dir-tab'));
  var input = document.getElementById('dir-q');
  var empty = document.getElementById('dir-empty');
  var filter = 'all';

  function apply() {
    var q = (input.value || '').trim().toLowerCase();
    var shown = 0;
    cards.forEach(function (c) {
      var ok = (filter === 'all' || c.getAttribute('data-group') === filter) &&
               (!q || c.getAttribute('data-search').indexOf(q) !== -1);
      c.hidden = !ok;
      if (ok) shown++;
    });
    empty.hidden = shown !== 0;
  }

  tabs.forEach(function (t) {
    t.addEventListener('click', function () {
      filter = t.getAttribute('data-filter');
      tabs.forEach(function (x) { x.classList.toggle('is-active', x === t); });
      apply();
    });
  });
  input.addEventListener('input', apply);
})();
