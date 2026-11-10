"""Run the ingestion against all three local suppliers, slow one first."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import supplier_server

module = sys.argv[1] if len(sys.argv) > 1 else "ingest"
if module != "ingest":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "answer-key"))
ingest = __import__(module)

server, base = supplier_server.start()
try:
    _, finished, beats = asyncio.run(ingest.ingest([base + "/slow", base + "/fast-a", base + "/fast-b"]))
finally:
    server.shutdown()
print("finished (seconds after start):", finished)
gaps = [round(b - a, 2) for a, b in zip(beats, beats[1:])]
print("heartbeats:", len(beats), "longest gap:", max(gaps) if gaps else None)
