"""Unpack the tampered archive into sandbox/uploads/acme and report where files went."""
import shutil
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_archives

module = sys.argv[2] if len(sys.argv) > 2 else "unpack"
if module != "unpack":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "answer-key"))
unpack = __import__(module)

sandbox = Path(sys.argv[1]).resolve()
shutil.rmtree(sandbox, ignore_errors=True)
good, bad = make_archives.build(sandbox)
dest = sandbox / "uploads" / "acme"
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    try:
        unpack.unpack(bad, dest)
        outcome = "extracted"
    except Exception as exc:
        outcome = f"refused: {type(exc).__name__}"
print("python", sys.version.split()[0])
print("outcome:", outcome)
print("escaped file exists:", (sandbox / "escaped.txt").exists())
print("warnings:", sorted({type(w.message).__name__ for w in caught}))
