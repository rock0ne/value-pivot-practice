"""Shared helper for the exercise checkers: runs named checks and writes results.html.

Each chapter's check.py builds a list of exercises, each with a list of (description, function) checks.
A check function takes the folder being checked (begin or end) and returns True, or a short string
explaining what went wrong. Standard library only.
"""
import html, sys, traceback
from datetime import datetime
from pathlib import Path


def run(chapter_title, exercises, chapter_dir):
    """exercises: list of dicts with id, title, book, folder (exercise folder), checks [(desc, fn)]."""
    which = "end" if "--end" in sys.argv else "begin"
    total = passed = 0
    blocks = []
    for ex in exercises:
        d = Path(chapter_dir) / ex["folder"] / which
        rows, ok_all = [], True
        for desc, fn in ex["checks"]:
            try:
                r = fn(d)
            except Exception as e:  # a crash in your code is a failed check, with the reason shown
                r = f"{type(e).__name__}: {e}"
                if "--debug" in sys.argv:
                    traceback.print_exc()
            ok = r is True
            ok_all &= ok
            total += 1; passed += ok
            rows.append((ok, desc, "" if ok else str(r)))
        print(f"\n{ex['id']} {ex['title']}: {'PASS' if ok_all else 'NOT YET'}")
        for ok, desc, why in rows:
            print(f"  {'PASS' if ok else 'FAIL'}  {desc}" + (f"\n        {why}" if why else ""))
        items = "".join(f'<li>{"&#10003;" if ok else "&#10007;"} {html.escape(desc)}'
                        + (f'<br><span class="muted">{html.escape(why)}</span>' if why else "") + "</li>" for ok, desc, why in rows)
        blocks.append(f'<section class="card"><div class="id">Exercise {ex["id"]} &middot; Book: {html.escape(ex["book"])}</div>'
                      f'<h2>{html.escape(ex["title"])}</h2><div class="verdict {"ok" if ok_all else "bad"}">'
                      f'{"All checks pass." if ok_all else "Not yet."}</div><ul>{items}</ul>'
                      f'<p class="muted">Folder checked: <code>{html.escape(ex["folder"])}/{which}</code></p></section>')
    print(f"\n{passed} of {total} checks pass ({which} folders).")
    page = (f'<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{html.escape(chapter_title)} results</title><link rel="stylesheet" href="../shared/style.css"></head><body><main>'
            f'<p class="muted"><a href="../index.html">Value Pivot exercise files</a></p><h1>{html.escape(chapter_title)}: your results</h1>'
            f'<p>{passed} of {total} checks pass, on the <code>{which}</code> folders. Checked {datetime.now():%d %B %Y at %H:%M}. '
            f'Run <code>python check.py</code> again after each change.</p>{"".join(blocks)}</main></body></html>')
    out = Path(chapter_dir) / "results.html"
    out.write_text(page, encoding="utf-8")
    print(f"Results page: {out}")
    return 0 if passed == total else 1
