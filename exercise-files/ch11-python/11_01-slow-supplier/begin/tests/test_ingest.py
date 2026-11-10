"""The tests that came with the ingestion code. They pass."""
import asyncio
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "data"))
import ingest
import supplier_server


class IngestTests(unittest.TestCase):
    def setUp(self):
        self.server, self.base = supplier_server.start()

    def tearDown(self):
        self.server.shutdown()

    def test_reads_every_feed(self):
        feeds, finished, _ = asyncio.run(ingest.ingest([self.base + "/fast-a", self.base + "/fast-b"]))
        self.assertEqual([f["supplier"] for f in feeds], ["fast-a", "fast-b"])

    def test_is_quick(self):
        _, finished, _ = asyncio.run(ingest.ingest([self.base + "/fast-a", self.base + "/fast-b"]))
        self.assertLess(max(finished.values()), 1.0)


if __name__ == "__main__":
    unittest.main()
