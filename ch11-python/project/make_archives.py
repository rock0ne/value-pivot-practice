"""Build two test archives in a sandbox folder: a normal one, and one with a
member named ../../escaped.txt. Everything stays inside the sandbox."""
import io
import sys
import tarfile
from pathlib import Path


def add(tar, name, text):
    data = text.encode()
    info = tarfile.TarInfo(name)
    info.size = len(data)
    tar.addfile(info, io.BytesIO(data))


def build(sandbox):
    sandbox = Path(sandbox)
    sandbox.mkdir(parents=True, exist_ok=True)
    good = sandbox / "acme-prices.tar.gz"
    bad = sandbox / "acme-prices-tampered.tar.gz"
    with tarfile.open(good, "w:gz") as tar:
        add(tar, "prices.csv", "sku,price\nHG-001,4.99\n")
    with tarfile.open(bad, "w:gz") as tar:
        add(tar, "prices.csv", "sku,price\nHG-001,4.99\n")
        add(tar, "../../escaped.txt", "this file landed outside the supplier folder\n")
    return good, bad


if __name__ == "__main__":
    print(build(sys.argv[1]))
