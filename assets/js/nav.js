(function () {
  var nav = document.querySelector('.mm-nav');
  if (!nav) return;
  var toggle = nav.querySelector('.mm-toggle');
  var buttons = nav.querySelectorAll('.mm-btn');
  var closeTimer;

  function hoverMode() { return window.matchMedia('(min-width: 901px) and (hover: hover)').matches; }

  function closeAll(except) {
    buttons.forEach(function (b) {
      if (b !== except) {
        b.setAttribute('aria-expanded', 'false');
        b.parentNode.classList.remove('is-open', 'by-click');
      }
    });
  }

  buttons.forEach(function (btn) {
    var item = btn.parentNode;
    btn.addEventListener('click', function () {
      // On desktop a hover has already opened the panel; a click should keep it open, not toggle it shut.
      var open = (hoverMode() && !item.classList.contains('by-click')) || btn.getAttribute('aria-expanded') !== 'true';
      item.classList.toggle('by-click', open);
      closeAll(btn);
      btn.setAttribute('aria-expanded', open);
      item.classList.toggle('is-open', open);
    });
    // Desktop hover (fine pointers only) with a short delay so the pointer can cross into the panel.
    item.addEventListener('mouseenter', function () {
      if (!hoverMode()) return;
      clearTimeout(closeTimer);
      closeAll(btn);
      btn.setAttribute('aria-expanded', 'true');
      item.classList.add('is-open');
    });
    item.addEventListener('mouseleave', function () {
      if (!hoverMode()) return;
      closeTimer = setTimeout(function () { closeAll(); }, 150);
    });
  });

  toggle.addEventListener('click', function () {
    var open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', open);
    nav.classList.toggle('is-open', open);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { closeAll(); }
  });
  document.addEventListener('click', function (e) {
    if (!nav.contains(e.target)) { closeAll(); }
  });
})();
