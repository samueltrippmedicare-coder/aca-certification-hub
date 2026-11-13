(function () {
  'use strict';
  const menu = document.querySelector('.contents-menu');
  if (!menu) return;
  const compact = window.matchMedia('(max-width: 980px)');
  function setMenuForViewport() { menu.open = !compact.matches; }
  setMenuForViewport();
  compact.addEventListener('change', setMenuForViewport);
  menu.addEventListener('toggle', function () {
    if (!compact.matches && !menu.open) menu.open = true;
  });
  menu.querySelectorAll('nav a').forEach(function (link) {
    link.addEventListener('click', function () {
      if (compact.matches) menu.open = false;
    });
  });
})();
