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
      // Use a clear label for invite links instead of showing the invite token.
      var slug = (SITE.telegram.split("/").filter(Boolean).pop() || "");
      var handle = slug.replace(/^\+/, "");
      var label = slug.charAt(0) === "+"
        ? "Private Telegram invite"
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
      ".hero-copy > *, .market-visual, .sec > .wrap > .kicker, .sec > .wrap > h2, " +
      ".sec > .wrap > .sub, .sec > .wrap > .markets-intro, .card, .steps li, " +
      ".discipline div, .chart, .band, .band-list li, .link-card, .project, " +
      ".work-foot, .services, .service, .stat-grid, .risk-block, .prose > *, " +
      ".chip-row, .foot-in > *"
    );

    targets.forEach(function (el) {
      el.classList.add("reveal");
      var group = el.closest(".sec") || document.body;
      var count = Number(group.getAttribute("data-reveal-count") || 0);
      el.style.setProperty("--reveal-delay", Math.min(count, 5) * 55 + "ms");
      group.setAttribute("data-reveal-count", String(count + 1));
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

    targets.forEach(function (el) { io.observe(el); });
  }

  /* ---------- interactive equity curve ---------- */

  function initEquityChart() {
    var chart = document.querySelector("[data-equity-chart]");
    if (!chart || !window.fetch || !window.DOMParser) return;
    var image = chart.querySelector("img");
    var crosshair = chart.querySelector(".equity-crosshair");
    var marker = chart.querySelector(".equity-marker");
    var tooltip = chart.querySelector(".equity-tooltip");
    var points = [];
    var axes = [];
    var selected = 0;

    function setPoint(index) {
      if (!points.length) return;
      selected = Math.max(0, Math.min(points.length - 1, index));
      var point = points[selected];
      var value = axes.length > 1
        ? axes[0].value + (point[1] - axes[0].y) *
          (axes[axes.length - 1].value - axes[0].value) /
          (axes[axes.length - 1].y - axes[0].y)
        : 0;
      var label = "$" + Math.round(value).toLocaleString("en-US");
      var pointLabel = selected === 0 ? "Starting point" : "Trade " + selected;
      crosshair.setAttribute("x1", point[0]);
      crosshair.setAttribute("x2", point[0]);
      marker.setAttribute("cx", point[0]);
      marker.setAttribute("cy", point[1]);
      chart.setAttribute("aria-valuenow", String(selected));
      chart.setAttribute("aria-valuetext", pointLabel + ", " + label);
      tooltip.textContent = pointLabel + " · " + label;
      var xPercent = Math.max(12, Math.min(88, point[0] / 10));
      var yPercent = point[1] / 4.2;
      tooltip.style.left = xPercent + "%";
      if (yPercent < 30) {
        tooltip.style.top = Math.min(76, yPercent + 17) + "%";
        tooltip.style.transform = "translate(-50%,0)";
      } else {
        tooltip.style.top = Math.max(14, yPercent - 4) + "%";
        tooltip.style.transform = "translate(-50%,-100%)";
      }
      chart.classList.add("has-point");
    }

    function indexFromPointer(event) {
      var rect = chart.getBoundingClientRect();
      var x = ((event.clientX - rect.left) / rect.width) * 1000;
      var index = Math.round(((x - 8) / 984) * (points.length - 1));
      setPoint(index);
    }

    fetch(image.currentSrc || image.src, { credentials: "same-origin" })
      .then(function (response) { if (!response.ok) throw new Error("Chart unavailable"); return response.text(); })
      .then(function (source) {
        var doc = new DOMParser().parseFromString(source, "image/svg+xml");
        var path = doc.querySelector('path[fill="none"]');
        if (!path) return;
        var matches = path.getAttribute("d").matchAll(/[ML]\s*([\d.]+),([\d.]+)/g);
        points = Array.from(matches).map(function (match) {
          return [Number(match[1]), Number(match[2])];
        });
        Array.prototype.forEach.call(doc.querySelectorAll("text.ax"), function (label) {
          var value = Number(label.textContent.replace(/,/g, ""));
          var y = Number(label.getAttribute("y")) + 6;
          if (isFinite(value) && isFinite(y)) axes.push({ y: y, value: value });
        });
        axes.sort(function (a, b) { return a.y - b.y; });
        if (points.length < 2 || axes.length < 2) return;
        chart.setAttribute("aria-valuemax", String(points.length - 1));
      })
      .catch(function () { /* The static chart remains available if parsing fails. */ });

    chart.addEventListener("pointermove", function (event) {
      if (event.pointerType === "touch") return;
      indexFromPointer(event);
    });
    chart.addEventListener("pointerleave", function () {
      if (document.activeElement !== chart) chart.classList.remove("has-point");
    });
    chart.addEventListener("focus", function () {
      if (points.length) setPoint(selected);
    });
    chart.addEventListener("blur", function () { chart.classList.remove("has-point"); });
    chart.addEventListener("keydown", function (event) {
      if (!points.length) return;
      if (event.key === "ArrowRight" || event.key === "ArrowLeft" || event.key === "Home" || event.key === "End") {
        event.preventDefault();
        if (event.key === "ArrowRight") setPoint(selected + 1);
        else if (event.key === "ArrowLeft") setPoint(selected - 1);
        else if (event.key === "Home") setPoint(0);
        else setPoint(points.length - 1);
      }
    });
  }

  /* ---------- illustrative market replay ---------- */

  function initMarketReplay() {
    var replay = document.querySelector("[data-market-replay]");
    if (!replay) return;
    var chart = replay.querySelector("[data-replay-chart]");
    var playButton = replay.querySelector("[data-replay-play]");
    var pauseButton = replay.querySelector("[data-replay-pause]");
    var replayButton = replay.querySelector("[data-replay-again]");
    var status = replay.querySelector("[data-replay-status]");
    var replayMarker = chart.querySelector(".market-level-label");
    var observer = null;
    var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var hasPlayed = false;

    function setControls(playing, paused) {
      playButton.disabled = playing && !paused;
      playButton.querySelector("span").textContent = paused ? "Resume" : "Play replay";
      pauseButton.disabled = !playing || paused;
      replayButton.disabled = playing && !paused;
    }

    function startReplay(restart) {
      if (reduced) {
        status.textContent = "Static preview · reduced-motion setting";
        return;
      }
      if (observer) observer.disconnect();
      if (!restart && replay.classList.contains("is-playing") && replay.classList.contains("is-paused")) {
        replay.classList.remove("is-paused");
        status.textContent = "Replay resumed · Illustrative, not live data";
        setControls(true, false);
        return;
      }
      if (!restart && hasPlayed && replay.classList.contains("is-complete")) {
        restart = true;
      }
      if (restart || !hasPlayed) {
        replay.classList.remove("is-playing", "is-paused", "is-complete");
        chart.classList.remove("is-playing", "is-paused", "is-complete");
        chart.classList.add("replay-ready");
        void chart.offsetWidth;
        hasPlayed = true;
      }
      replay.classList.add("is-playing");
      chart.classList.add("is-playing");
      status.textContent = "Playing illustrative replay · Not live data";
      setControls(true, false);
    }

    function pauseReplay() {
      if (!replay.classList.contains("is-playing") || replay.classList.contains("is-complete")) return;
      replay.classList.add("is-paused");
      chart.classList.add("is-paused");
      status.textContent = "Replay paused";
      setControls(true, true);
    }

    function finishReplay() {
      replay.classList.remove("is-playing", "is-paused");
      replay.classList.add("is-complete");
      chart.classList.remove("is-playing", "is-paused");
      chart.classList.add("is-complete");
      status.textContent = "Replay complete · Select Replay to watch again";
      setControls(false, false);
    }

    playButton.addEventListener("click", function () { startReplay(false); });
    pauseButton.addEventListener("click", pauseReplay);
    replayButton.addEventListener("click", function () { startReplay(true); });
    replayMarker.addEventListener("animationend", function (event) {
      if (event.animationName !== "label-show") return;
      if (replay.classList.contains("is-paused")) return;
      finishReplay();
    });

    if (reduced) {
      replay.classList.add("is-complete");
      status.textContent = "Static preview · reduced-motion setting";
      playButton.disabled = true;
      pauseButton.disabled = true;
      replayButton.disabled = true;
      return;
    }

    chart.classList.add("replay-ready");
    setControls(false, false);
    if (!("IntersectionObserver" in window)) {
      startReplay(false);
      return;
    }
    observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting || hasPlayed) return;
        startReplay(false);
        observer.disconnect();
      });
    }, { threshold: 0.3 });
    observer.observe(replay);
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
    initEquityChart();
    initMarketReplay();
    initYear();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
