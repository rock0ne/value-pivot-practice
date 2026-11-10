// Runs the JavaScript exercises in the browser. Your code runs only on this page; nothing is sent anywhere.
(function () {
  "use strict";
  function el(tag, attrs, kids) {
    var e = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { if (k === "text") e.textContent = attrs[k]; else if (k === "html") e.innerHTML = attrs[k]; else e.setAttribute(k, attrs[k]); });
    (kids || []).forEach(function (c) { e.appendChild(c); });
    return e;
  }

  function load(code, name) {
    // Your code is a plain script; this returns the function it defines.
    return new Function(code + "\n;return typeof " + name + " === 'function' ? " + name + " : undefined;")();
  }

  function card(ex) {
    var ta = el("textarea", { spellcheck: "false", "aria-label": "Code for exercise " + ex.id }); ta.value = ex.begin;
    ta.style.minHeight = "16em";
    var out = el("div", { class: "out", "aria-live": "polite" });
    var bRun = el("button", { class: "primary", text: "Run my tests" }), bReset = el("button", { text: "Start again" });
    var sol = el("details", {}, [el("summary", { text: "Show one possible answer" }), el("pre", { text: ex.end })]);
    var hint = el("details", {}, [el("summary", { text: "Hint" }), el("p", { html: ex.hint })]);
    bRun.onclick = function () {
      out.innerHTML = "";
      var f;
      try { f = load(ta.value, ex.fn); } catch (e) { out.appendChild(el("div", { class: "verdict bad", text: "Your code didn't run: " + e.message })); return; }
      if (!f) { out.appendChild(el("div", { class: "verdict bad", text: "Define a function called " + ex.fn + "." })); return; }
      var passed = 0, list = el("ul");
      ex.tests.forEach(function (t) {
        var ok;
        try { ok = t[1](f) === true; } catch (e) { ok = false; }
        if (ok) passed++;
        list.appendChild(el("li", { text: (ok ? "✓ " : "✗ ") + t[0] }));
      });
      var all = passed === ex.tests.length;
      out.appendChild(el("div", { class: "verdict " + (all ? "ok" : "bad"), role: "status",
        text: (all ? "All " : passed + " of ") + ex.tests.length + " tests pass" + (all ? ". Well done." : ". Not yet.") }));
      out.appendChild(list);
    };
    bReset.onclick = function () { ta.value = ex.begin; out.innerHTML = ""; };
    return el("section", { class: "card", id: "ex" + ex.id }, [
      el("div", { class: "id", text: "Exercise " + ex.id + " · Book: " + ex.book }),
      el("h2", { text: ex.title }), el("p", { html: ex.task }), ta,
      el("div", { class: "buttons" }, [bRun, bReset]), out, hint, sol]);
  }

  window.addEventListener("DOMContentLoaded", function () {
    var host = document.getElementById("exercises");
    window.EXERCISES.forEach(function (ex) { host.appendChild(card(ex)); });
  });
})();
