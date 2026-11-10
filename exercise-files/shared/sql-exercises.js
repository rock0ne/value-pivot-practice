// Runs the SQL exercises in the browser with the pinned copy of sql.js. Nothing is sent anywhere.
(function () {
  "use strict";
  var SQL, base, $ = function (s, el) { return (el || document).querySelector(s); };

  function el(tag, attrs, kids) {
    var e = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { if (k === "text") e.textContent = attrs[k]; else if (k === "html") e.innerHTML = attrs[k]; else e.setAttribute(k, attrs[k]); });
    (kids || []).forEach(function (c) { e.appendChild(c); });
    return e;
  }

  function freshDb() { return new SQL.Database(base); }

  function buildBase() {
    var d = new SQL.Database(), C = window.CLINIC;
    d.exec(C.schema);
    d.exec("BEGIN");
    var s = d.prepare("INSERT INTO clients VALUES (?,?,?)");
    C.clients.forEach(function (r) { s.run(r); }); s.free();
    s = d.prepare("INSERT INTO bookings VALUES (?,?,?,?,?,?,?,?)");
    C.bookings.forEach(function (r) { s.run(r); }); s.free();
    d.exec("COMMIT");
    base = d.export(); d.close();
  }

  function norm(v) { return v === null ? "NULL" : String(v); }
  function key(row) { return row.map(norm).join("␟"); }

  function table(res, limit) {
    if (!res) return el("p", { class: "muted", text: "The statement ran. It returned no rows." });
    var t = el("table"), h = el("tr");
    res.columns.forEach(function (c) { h.appendChild(el("th", { text: c })); });
    t.appendChild(h);
    res.values.slice(0, limit).forEach(function (r) {
      var tr = el("tr"); r.forEach(function (v) { tr.appendChild(el("td", { text: norm(v) })); }); t.appendChild(tr);
    });
    var wrap = el("div", {}, [el("p", { class: "muted", text: res.values.length + " row" + (res.values.length === 1 ? "" : "s") + (res.values.length > limit ? ", showing the first " + limit : "") }), t]);
    return wrap;
  }

  function verdict(ok, text) { return el("div", { class: "verdict " + (ok ? "ok" : "bad"), role: "status", text: text }); }

  function run(sql) {
    var d = freshDb();
    try { var r = d.exec(sql); return { res: r.length ? r[r.length - 1] : null }; }
    catch (e) { return { err: e.message }; }
    finally { d.close(); }
  }

  function checkRows(ex, sql) {
    var r = run(sql);
    if (r.err) return [false, "Your SQL didn't run: " + r.err];
    var got = r.res ? r.res.values : [], want = ex.expected;
    if (got.length && want.length && got[0].length !== want[0].length)
      return [false, "Not yet. Your query returns " + got[0].length + " columns; this exercise asks for " + want[0].length + "."];
    var g = got.map(key).sort(), w = want.map(key).sort();
    if (g.length !== w.length) return [false, "Not yet. Your query returns " + g.length + " rows; the right answer has " + w.length + "."];
    for (var i = 0; i < g.length; i++) if (g[i] !== w[i]) return [false, "Not yet. The number of rows is right, but at least one row's values differ. Compare a few rows with the data."];
    return [true, "Correct. Your result matches, row for row (" + w.length + " row" + (w.length === 1 ? "" : "s") + ")."];
  }

  function checkGuard(sql) {
    var d = new SQL.Database(), lines = [], all = true;
    try {
      d.exec(window.CLINIC.schema);
      d.exec(sql);
    } catch (e) { d.close(); return [false, "Your SQL didn't run on the empty table: " + e.message]; }
    window.GUARD.forEach(function (g) {
      var accepted = true;
      try { d.run("INSERT INTO bookings (therapist,start,client_ref,service,price_pence,status,created_at) VALUES (?,?,NULL,'Follow-up',4800,?,'2027-01-05 09:00:00')", g.row); }
      catch (e) { accepted = false; }
      var right = accepted === g.accept; all = all && right;
      lines.push((right ? "✓ " : "✗ ") + g.what + ": " + (accepted ? "accepted" : "refused") + (right ? "" : " (it should have been " + (g.accept ? "accepted" : "refused") + ")"));
    });
    d.close();
    return [all, (all ? "Correct. The database itself now keeps the rule.\n" : "Not yet.\n") + lines.join("\n")];
  }

  function card(ex) {
    var ta = el("textarea", { spellcheck: "false", "aria-label": "SQL for exercise " + ex.id }); ta.value = ex.begin;
    var out = el("div", { class: "out", "aria-live": "polite" });
    var bRun = el("button", { class: "primary", text: "Run" }), bCheck = el("button", { text: "Check my answer" }), bReset = el("button", { text: "Start again" });
    var sol = el("details", {}, [el("summary", { text: "Show one possible answer" }), el("pre", { text: ex.end })]);
    var hint = el("details", {}, [el("summary", { text: "Hint" }), el("p", { html: ex.hint })]);
    bRun.onclick = function () { out.innerHTML = ""; var r = run(ta.value); out.appendChild(r.err ? verdict(false, "Error: " + r.err) : table(r.res, 50)); };
    bCheck.onclick = function () {
      out.innerHTML = "";
      var v = ex.check === "guard" ? checkGuard(ta.value) : checkRows(ex, ta.value);
      var p = verdict(v[0], ""); p.style.whiteSpace = "pre-wrap"; p.textContent = v[1]; out.appendChild(p);
    };
    bReset.onclick = function () { ta.value = ex.begin; out.innerHTML = ""; };
    return el("section", { class: "card", id: "ex" + ex.id }, [
      el("div", { class: "id", text: "Exercise " + ex.id + " · Book: " + ex.book }),
      el("h2", { text: ex.title }), el("p", { html: ex.task }), ta,
      el("div", { class: "buttons" }, [bRun, bCheck, bReset]), out, hint, sol]);
  }

  window.addEventListener("DOMContentLoaded", function () {
    var status = $("#status");
    initSqlJs().then(function (S) {
      SQL = S; buildBase();
      var host = $("#exercises");
      window.EXERCISES.forEach(function (ex) { host.appendChild(card(ex)); });
      status.textContent = "Ready. The database is loaded in your browser: " + window.CLINIC.clients.length + " clients and " + window.CLINIC.bookings.length + " bookings. Every Run starts from a fresh copy, so you can't break anything.";
    }).catch(function (e) { status.textContent = "The SQL engine didn't load: " + e.message; });
  });
})();
