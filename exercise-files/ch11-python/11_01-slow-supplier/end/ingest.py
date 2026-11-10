"""The fix: run the blocking call in a worker thread, so the event loop stays free.

An async HTTP client would also work; this keeps to the standard library.
"""
import asyncio
import json
import time
import urllib.request


def _fetch_blocking(url):
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read())


async def fetch_feed(url):
    return await asyncio.to_thread(_fetch_blocking, url)


async def heartbeat(stop, beats):
    while not stop.is_set():
        beats.append(time.perf_counter())
        await asyncio.sleep(0.1)


async def ingest(urls):
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
