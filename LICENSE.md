# Neural Memory App - Alpha Version

A local SQLite-based neural memory system with graph visualization and semantic search capabilities.

## Version
**Alpha 1.0.0** - Initial release with core features

## Features
- ✅ Embeddings integration (sentence-transformers)
- ✅ D3.js force-directed graph visualization
- ✅ Semantic search (keyword + vector similarity)
- ✅ CRUD operations for facts
- ✅ API rate limiting (100 req/60s)
- ✅ CORS support
- ✅ Auto port detection

## Quick Start
```bash
python server.py [port]
# Default: auto-detect from 8080
```

## API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server health check |
| `/api/facts` | GET/POST/PUT/DELETE | Manage facts |
| `/api/search?q=xxx&vector=true` | GET | Semantic search |
| `/api/graph` | GET | Graph data for D3.js |
| `/api/graph/insights` | GET | Insights and statistics |

## License
MIT