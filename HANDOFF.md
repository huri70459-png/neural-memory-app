# Handoff — Neural Memory App (debug-test-001) — 2026-09-27 19:11 IST

## Project
- **Path:** `C:/Users/kafsh/neural-memory-app-debug-test-001`
- **Server:** `server.py` — ThreadingHTTPServer, health + facts + graph + insights, embeddings `all-MiniLM-L6-v2` (384-dim, active)
- **UI:** `index.html` — D3 graph + CRUD form (Create/Update/Delete) + search highlighting + legend + node-click modal
- **Tests:** `test_api.py` — 80/80 passing (health, CRUD, search, graph, insights, rate-limit, CORS, errors, embeddings)
- **Release:** `v1.0.0-alpha` at https://github.com/huri70459-png/neural-memory-app/releases/tag/v1.0.0-alpha (pushed `da63eb3`)

## Current Live State
- Running on **http://localhost:8080** — `health: ok, facts=21, embeddings=active` — verified live (curl + DB read).
- **PID 38892** single server after cleanup (orphans killed). DB `data/memories.db` accessible, no lock.

## Fixes Since Last Handoff (this session)
1. **Port leak / stale instances:** `restart.py` used `wmic` (removed Win11 24H2) → no kills, stacked servers. Fixed to `Get-CimInstance Win32_Process + Get-NetTCPConnection` via powershell, kills only `*server.py*`, ignores PID 0 (TIME_WAIT). Also added `ThreadingHTTPServer.allow_reuse_address = True` and `SIGTERM`/`atexit` + `server_close()` in `server.py`.
2. **Stale app state:** Added `restart.py` step 2 — remove `data/memories.db` on restart so old facts don't persist. Verified DB releases clean after stop/test suite.
3. **UI connection refused (`localhost:8082`):** `index.html` hardcoded `API_BASE = 'http://localhost:8082'` + `port-status 8082` mismatched server 8080. Patched to `window.location.origin` and `window.location.port || '8080'` — requires **Ctrl+F5** hard refresh in browser.

## Uncommitted Changes (needs commit)
- `M server.py` — allow_reuse_address, signal/atexit handlers
- `M index.html` — dynamic API_BASE
- `?? restart.py` — new (replaces deleted `restart.sh`)
- `D restart.sh`, `?? RELEASE_NOTES.md`, `?? quick_test.py`, `?? demo_harness.py`

## How To Run (resume here)
```bash
cd C:/Users/kafsh/neural-memory-app-debug-test-001
python restart.py           # or python restart.py 8080 — kills stale, clears DB, starts, waits for /health
# open http://localhost:8080 then Ctrl+F5
python test_api.py          # 80/80 expected, DB auto-released
# stop:
powershell -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object {\$_.CommandLine -like '*server.py*'} | ForEach-Object { taskkill /F /PID \$_.ProcessId }"
```
Alt: `python server.py` (with `allow_reuse_address` it restarts clean if prev stopped cleanly).

## Verified Live Checks (re-run on resume)
```bash
curl -s http://localhost:8080/health
curl -s -X POST http://localhost:8080/api/facts -H "Content-Type: application/json" -d '{"method":"POST","id":"debug-001","content":"test","category":"test"}'
curl -s "http://localhost:8080/api/search?q=debug&project=debug-test-001"
powershell -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object {\$_.CommandLine -like '*server.py*'} | Select-Object ProcessId"
```

## Next Steps / TODO (from MEMORY)
- `git add server.py index.html restart.py && git commit && git push` — then `gh release edit v1.0.0-alpha --notes-file RELEASE_NOTES.md` if updating release.
- Wire basic auth: set `MEMORY_APP_AUTH=***` env and test 401/200.
- Add semantic search endpoint (embedding cosine, not just LIKE) — embeddings already computed.
- Clean up `quick_test.py` if throwaway.
- Regression: confirm no `Failed to fetch` after Ctrl+F5; confirm single PID after repeated `restart.py` cycles.

## Known Issues / Warnings
- Browser cache: after pulling, must hard-refresh or `Failed to fetch` persists.
- `restart.py` previously printed `Killed PID 0` — now filtered, but keep eye on powershell output.
- HuggingFace `all-MiniLM-L6-v2` first load downloads ~80MB; ensure offline cache or pre-install.
