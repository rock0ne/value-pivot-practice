# 11_01: The supplier that froze the shop

**Book:** Chapter 11, Scenario 1: the supplier that froze the shop.

Hollin Garden Supplies' stock service is meant to fetch every supplier's feed at the same time, with a heartbeat ticking alongside. When one supplier takes 2 seconds to answer, the fast suppliers wait for it, and the heartbeat stops. Change `fetch_feed` so the slow call no longer holds up everything else. You're done when the fast suppliers finish in under half a second and the heartbeat ticks at least 10 times.

**Files:** `begin/ingest.py` (edit this). `begin/run_demo.py` runs the three local stand-in suppliers, slow one first, and `begin/tests/` holds the tests that came with the code. The answer is in `end/`: open it only when you've finished, or you're truly stuck.

**Check your work:** from the `ch11-python` folder, run `python check.py`.

**Hint:** read every call inside each `async def`, and ask whether it awaits something or just runs. `asyncio.to_thread` is in the standard library.
