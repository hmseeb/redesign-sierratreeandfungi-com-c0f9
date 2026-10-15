/* Sierra Tree & Fungi — site behaviour
   - mobile navigation + mega-menu toggles
   - LeadrVision form handling (fetch with graceful no-JS fallback)
   - ?submitted=1 confirmation
*/
(function () {
  'use strict';

  var ENDPOINT = 'https://vision.leadrai.com/api/forms/246b1deb67270022258874839c48348b';

  /* ----------------------------- navigation ----------------------------- */
  var nav = document.getElementById('primary-nav');
  var navToggle = document.querySelector('.nav-toggle');

  if (nav && navToggle) {
    navToggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      navToggle.querySelector('.nav-toggle-label').textContent = open ? 'Close' : 'Menu';
      document.documentElement.style.overflow = open ? 'hidden' : '';
    });
  }

  Array.prototype.forEach.call(document.querySelectorAll('button.navtop'), function (btn) {
    var panel = document.getElementById(btn.getAttribute('aria-controls'));
    if (!panel) return;
    btn.addEventListener('click', function (event) {
      event.preventDefault();
      var open = panel.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') return;
    Array.prototype.forEach.call(document.querySelectorAll('.mega.is-open'), function (panel) {
      panel.classList.remove('is-open');
      var btn = document.querySelector('[aria-controls="' + panel.id + '"]');
      if (btn) btn.setAttribute('aria-expanded', 'false');
    });
    if (nav && nav.classList.contains('is-open') && navToggle) navToggle.click();
  });

  /* ------------------------------- forms -------------------------------- */
  var pageUrl = window.location.href;
  Array.prototype.forEach.call(document.querySelectorAll('input[name="_page"]'), function (input) {
    input.value = pageUrl;
  });

  function showThanks(shell) {
    if (!shell) return;
    shell.classList.add('is-sent');
    var box = shell.querySelector('.form-success');
    if (box) box.setAttribute('tabindex', '-1');
  }

  var submitted = /[?&]submitted=1(&|$)/.test(window.location.search);
  if (submitted) {
    var shells = document.querySelectorAll('.form-shell');
    Array.prototype.forEach.call(shells, function (shell) { showThanks(shell); });
    if (shells.length) {
      var first = shells[0].querySelector('.form-success');
      if (first) {
        window.setTimeout(function () {
          first.scrollIntoView({ block: 'center', behavior: 'smooth' });
          first.focus({ preventScroll: true });
        }, 120);
      }
    }
  }

  Array.prototype.forEach.call(document.querySelectorAll('form.leadr-form'), function (form) {
    form.addEventListener('submit', function (event) {
      if (!window.fetch) return; // no-JS / old browser: plain POST happens
      event.preventDefault();

      var shell = form.closest('.form-shell');
      var status = form.querySelector('.form-status');
      var button = form.querySelector('button[type="submit"]');
      var pageField = form.querySelector('input[name="_page"]');
      if (pageField) pageField.value = window.location.href;

      var payload = {};
      var data = new FormData(form);
      data.forEach(function (value, key) {
        if (typeof value !== 'string') return;
        if (payload[key]) { payload[key] = payload[key] + ', ' + value; }
        else { payload[key] = value; }
      });
      payload._page = window.location.href;

      if (status) { status.textContent = 'Sending…'; status.setAttribute('data-state', 'busy'); }
      if (button) { button.disabled = true; }

      window.fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(payload)
      }).then(function (response) {
        return response.json().catch(function () { return { ok: response.ok }; });
      }).then(function (result) {
        if (result && result.ok) {
          if (status) { status.textContent = ''; status.removeAttribute('data-state'); }
          form.reset();
          if (pageField) pageField.value = window.location.href;
          showThanks(shell);
          var box = shell && shell.querySelector('.form-success');
          if (box) box.focus({ preventScroll: true });
        } else {
          throw new Error('Submission rejected');
        }
      }).catch(function () {
        if (status) {
          status.textContent = 'Sorry, that did not go through. Please call or text (530) 391-6100.';
          status.setAttribute('data-state', 'error');
        }
      }).then(function () {
        if (button) button.disabled = false;
      });
    });
  });

  /* --------------------------- current year ----------------------------- */
  Array.prototype.forEach.call(document.querySelectorAll('[data-year]'), function (el) {
    el.textContent = String(new Date().getFullYear());
  });
})();
