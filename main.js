/* ============================================================
   Divine Abba — landing page behaviour
   Vanilla JS, no dependencies.
   ============================================================ */
(function () {
  "use strict";

  var SITE = window.SITE || {};
  var mqMobile = window.matchMedia("(max-width: 940px)");

  /* ---------- contact wiring from config.js ---------- */

  function initContacts() {
    if (SITE.email) {
      document.querySelectorAll("[data-email]").forEach(function (a) {
        a.href = "mailto:" + SITE.email;
      });
      document.querySelectorAll("[data-email-text]").forEach(function (el) {
        el.textContent = SITE.email;
      });
    }

    if (SITE.linkedin) {
      document.querySelectorAll("[data-linkedin]").forEach(function (a) {
        a.href = SITE.linkedin;
      });
    }

    if (SITE.x) {
      document.querySelectorAll("[data-x]").forEach(function (a) {
        a.href = SITE.x;
      });
      // https://x.com/ad_crim1 -> "@ad_crim1"
      var xh = (SITE.x.split("/").filter(Boolean).pop() || "");
      if (xh) {
        document.querySelectorAll("[data-x-text]").forEach(function (el) {
          el.textContent = "@" + xh;
        });
      }
    }

    if (SITE.telegram) {
      document.querySelectorAll("[data-tg]").forEach(function (a) {
        a.href = SITE.telegram;
      });
      // derive a readable handle, e.g. https://t.me/adcrim -> @adcrim
      var handle = (SITE.telegram.split("/").filter(Boolean).pop() || "").replace(/^\+/, "");
      var label = handle.charAt(0) === "+" || handle.length > 24
        ? "Daily trade posts"
        : "@" + handle + " — daily trade posts";
      document.querySelectorAll("[data-tg-text]").forEach(function (el) {
        el.textContent = label;
      });
    }
  }

  /* ---------- hero market strip ---------- */

  function initTicker() {
    var track = document.getElementById("tickerTrack");
    var items = SITE.ticker || [];
    if (!track || !items.length) return;
    var html = items
      .map(function (p) { return "<span><b>" + p[0] + "</b><i>/</i>" + p[1] + "</span>"; })
      .join("");
    track.innerHTML = html + html; // duplicated for seamless loop
  }

  /* ---------- sticky nav + mobile menu ---------- */

  function initNav() {
    var nav = document.getElementById("nav");
    var burger = document.getElementById("burger");
    if (!nav) return;

    var onScroll = function () {
      nav.classList.toggle("stuck", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });

    if (!burger) return;

    function setOpen(open) {
      nav.classList.toggle("menu-open", open);
      burger.setAttribute("aria-expanded", open ? "true" : "false");
      burger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    }

    burger.addEventListener("click", function () {
      setOpen(!nav.classList.contains("menu-open"));
    });

    // close after tapping a link
    nav.querySelectorAll("nav a").forEach(function (a) {
      a.addEventListener("click", function () { setOpen(false); });
    });

    // close on Escape
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("menu-open")) {
        setOpen(false);
        burger.focus();
      }
    });

    // close when tapping outside the panel
    document.addEventListener("click", function (e) {
      if (!nav.classList.contains("menu-open")) return;
      if (nav.contains(e.target)) return;
      setOpen(false);
    });

    // reset when growing past the mobile breakpoint
    var onChange = function () { if (!mqMobile.matches) setOpen(false); };
    if (mqMobile.addEventListener) mqMobile.addEventListener("change", onChange);
    else if (mqMobile.addListener) mqMobile.addListener(onChange);
  }

  /* ---------- active section highlighting ---------- */

  function initActiveLink() {
    var links = Array.prototype.slice.call(document.querySelectorAll('.nav nav a[href^="#"]'));
    if (!links.length || !("IntersectionObserver" in window)) return;

    var map = {};
    var sections = [];
    links.forEach(function (a) {
      var id = a.getAttribute("href").slice(1);
      var el = document.getElementById(id);
      if (el) { map[id] = a; sections.push(el); }
    });

    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          links.forEach(function (l) { l.classList.remove("active"); });
          var link = map[e.target.id];
          if (link) link.classList.add("active");
        });
      },
      { rootMargin: "-45% 0px -50% 0px", threshold: 0 }
    );
    sections.forEach(function (s) { io.observe(s); });
  }

  /* ---------- scroll reveal ---------- */

  function initReveal() {
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce || !("IntersectionObserver" in window)) return;

    // Reveal the blocks that carry the page's rhythm. We deliberately do NOT
    // wrap ".sec .wrap > *" — that hid the h2 and lede of every section until a
    // scroll event fired, which looks broken on slow devices and hurts SEO.
    var targets = document.querySelectorAll(
      ".card, .steps li, .discipline div, .chart, .band, .link-card, .project, " +
      ".work-foot, .services, .stat-grid, .risk-block"
    );

    targets.forEach(function (el) { el.classList.add("reveal"); });

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

    targets.forEach(function (el) { io.observe(el); });
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
    initActiveLink();
    initReveal();
    initYear();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
