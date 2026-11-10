"""Stock-feed ingestion for Hollin Garden Supplies (fictional).

Written as an AI assistant might write it, to show a common failure pattern.
It is not the output of any particular AI.

Fetches every supplier's feed "concurrently" with asyncio, and keeps a
heartbeat running so the shop's dashboard knows the service is alive.
"""
import asyncio
import json
import time
import urllib.request


async def fetch_feed(url):
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read())


async def heartbeat(stop, beats):
    while not stop.is_set():
        beats.append(time.perf_counter())
        await asyncio.sleep(0.1)


async def ingest(urls):
    """Return (feeds, finish_times, heartbeat_times)."""
    start = time.perf_counter()
    finished = {}
    beats = []
    stop = asyncio.Event()
    hb = asyncio.create_task(heartbeat(stop, beats))
    await asyncio.sleep(0)

    async def one(url):
        feed = await fetch_feed(url)
        finished[url.rsplit("/", 1)[-1]] = round(time.perf_counter() - start, 2)
        return feed

    feeds = await asyncio.gather(*(one(u) for u in urls))
    stop.set()
    await hb
    return feeds, finished, [round(b - start, 2) for b in beats]
