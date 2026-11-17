/* ============================================================
   Divine Abba — landing page behaviour
   Vanilla JS, no dependencies.
   ============================================================ */
(function () {
  "use strict";

  var SITE = window.SITE || {};

  /* ---------- contact wiring from config.js ---------- */

  function initContacts() {
    var email = SITE.email;
    if (email) {
      document.querySelectorAll("[data-email]").forEach(function (a) {
        a.href = "mailto:" + email;
      });
      document.querySelectorAll("[data-email-text]").forEach(function (el) {
        el.textContent = email;
      });
    }

    var digits = (SITE.whatsapp || "").replace(/[^\d]/g, "");
    if (digits) {
      var msg = SITE.whatsappMessage ? "?text=" + encodeURIComponent(SITE.whatsappMessage) : "";
      document.querySelectorAll("[data-wa]").forEach(function (a) {
        a.href = "https://wa.me/" + digits + msg;
      });
      document.querySelectorAll("[data-wa-text]").forEach(function (el) {
        el.textContent = SITE.whatsappDisplay || "+" + digits;
      });
    }

    if (SITE.linkedin) {
      document.querySelectorAll('a[href*="linkedin.com/in/"]').forEach(function (a) {
        a.href = SITE.linkedin;
      });
    }

    if (SITE.telegram) {
      document.querySelectorAll("[data-tg]").forEach(function (a) {
        a.href = SITE.telegram;
      });
    }
  }

  /* ---------- hero market strip ---------- */

  function initTicker() {
    var track = document.getElementById("tickerTrack");
    var items = SITE.ticker || [];
    if (!track || !items.length) return;

    var html = items
      .map(function (p) {
        return (
          '<span><b>' + p[0] + "</b><i>/</i>" + p[1] + "</span>"
        );
      })
      .join("");

    // duplicated once so the -50% translate loops seamlessly
    track.innerHTML = html + html;
  }

  /* ---------- sticky nav border ---------- */

  function initNav() {
    var nav = document.getElementById("nav");
    if (!nav) return;
    var onScroll = function () {
      nav.classList.toggle("stuck", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---------- scroll reveal ---------- */

  function initReveal() {
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var targets = document.querySelectorAll(
      ".sec .wrap > *, .card, .mini, .steps li, .discipline div, .chart, .band, .link-card"
    );
    if (reduce || !("IntersectionObserver" in window)) return;

    targets.forEach(function (el) {
      el.classList.add("reveal");
    });

    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          e.target.classList.add("in");
          io.unobserve(e.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );

    targets.forEach(function (el) {
      io.observe(el);
    });
  }

  /* ---------- current year ---------- */

  function initYear() {
    var el = document.getElementById("yr");
    if (el) el.textContent = String(new Date().getFullYear());
  }

  function boot() {
    initContacts();
    initTicker();
    initNav();
    initReveal();
    initYear();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
