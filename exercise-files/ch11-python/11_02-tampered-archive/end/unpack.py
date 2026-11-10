"""The fix: say which extraction filter you want, instead of relying on the default.

filter="data" refuses members that would land outside the folder, absolute
paths, links that point outside, and device files. It is in Python 3.12 and later,
and in security releases of some earlier versions.
"""
import tarfile
from pathlib import Path


def unpack(archive_path, supplier_dir):
    supplier_dir = Path(supplier_dir)
    supplier_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path) as tar:
        tar.extractall(supplier_dir, filter="data")
    return sorted(p.name for p in supplier_dir.iterdir())
