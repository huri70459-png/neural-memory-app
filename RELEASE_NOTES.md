## Neural Memory App — Alpha Release

### What's included
- **REST API server** (`server.py`): Full CRUD (POST/PUT/DELETE), keyword search, D3-compatible graph endpoint, /graph/insights analytics, rate limiting (100 req/min), CORS, basic auth hook
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (384-dim vectors stored per fact)
- **Interactive UI** (`index.html`): D3.js v7 force-directed knowledge graph with legend, node-click detail modal, search highlighting, CRUD fact manager
- **21 seeded facts** across 11 categories with 5 relationships

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server health + stats |
| `/api/facts/all` | GET | All facts |
| `/api/facts?project=X` | GET | Filter by project |
| `/api/facts` | POST | Create/update/delete (via `method` field) |
| `/api/search?q=X&project=X` | GET | Keyword search |
| `/api/graph?project=X` | GET | Graph data (nodes + edges) |
| `/api/graph/insights?project=X` | GET | Analytics insights |

### Running
```
python server.py [port]
# Default: 8080, or auto-select
# Open http://localhost:8080
```

### Test suite
```
python test_api.py  # 80 tests, stdlib-only
```

### Auth
Set `MEMORY_APP_AUTH=user:pass` env var to enable basic auth.
