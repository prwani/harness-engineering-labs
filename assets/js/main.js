(function () {
  var body = document.body;
  var toggle = document.getElementById('sidebar-toggle');
  var scrim = document.getElementById('sidebar-scrim');
  var STORAGE_KEY = 'harness-labs-sidebar-collapsed';

  function setCollapsed(collapsed, persist) {
    body.classList.toggle('sidebar-collapsed', collapsed);
    if (toggle) {
      toggle.setAttribute('aria-expanded', String(!collapsed));
    }
    if (persist) {
      try {
        localStorage.setItem(STORAGE_KEY, collapsed ? '1' : '0');
      } catch (e) {
        /* localStorage unavailable (e.g. privacy mode); ignore */
      }
    }
  }

  var stored = null;
  try {
    stored = localStorage.getItem(STORAGE_KEY);
  } catch (e) {
    stored = null;
  }

  if (stored === '1') {
    setCollapsed(true, false);
  } else if (stored === '0') {
    setCollapsed(false, false);
  } else if (window.innerWidth < 900) {
    // No saved preference yet: default to collapsed on small screens.
    setCollapsed(true, false);
  }

  if (toggle) {
    toggle.addEventListener('click', function () {
      setCollapsed(!body.classList.contains('sidebar-collapsed'), true);
    });
  }

  if (scrim) {
    scrim.addEventListener('click', function () {
      setCollapsed(true, true);
    });
  }

  // Collapse automatically after following a nav link on narrow screens.
  document.querySelectorAll('.sidebar-nav a').forEach(function (link) {
    link.addEventListener('click', function () {
      if (window.innerWidth < 900) {
        setCollapsed(true, true);
      }
    });
  });
})();
