"""Unpack a supplier's uploaded price-list archive (fictional Hollin Garden Supplies).

Written as an AI assistant might write it, to show a common failure pattern.
"""
import tarfile
from pathlib import Path


def unpack(archive_path, supplier_dir):
    supplier_dir = Path(supplier_dir)
    supplier_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path) as tar:
        tar.extractall(supplier_dir)
    return sorted(p.name for p in supplier_dir.iterdir())
