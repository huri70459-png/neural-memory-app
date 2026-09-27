# Neural Memory App (debug-test-001)

A local SQLite-based neural memory system with graph visualization and semantic search.

## Quick Start

```bash
# Start the server
python server.py [port]

# Default port: 8080 (auto-detects next available if busy)
# Example: python server.py 8081
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server health check |
| `/api/facts` | GET | Get all facts |
| `/api/facts/all` | GET | Get all facts (alternative) |
| `/api/facts?project=xxx` | GET | Get facts by project |
| `/api/search?q=xxx` | GET | Search facts by keyword |
| `/api/graph` | GET | Get graph data for D3.js visualization |
| `/api/graph/insights` | GET | Get insights and statistics |
| `/api/facts` | POST | Create new fact (JSON body with id, content, etc.) |
| `/api/facts` | PUT | Update existing fact (JSON body) |
| `/api/facts` | DELETE | Delete fact (JSON body)

## Feature Status

- ✅ **Embeddings**: sentence-transformers integration ready (embedding column in schema)
- ✅ **D3.js Graph**: Force-directed graph visualization with zoom/pan support
- ✅ **Semantic Search**: Hybrid keyword + vector similarity search implemented
- ✅ **CRUD Operations**: POST/PUT/DELETE for facts, automatic embedding generation
- ✅ **Rate Limiting**: 100 requests per 60 seconds per IP
- ✅ **CORS**: Headers on all responses
- ✅ **Port Auto-Detection**: Auto-selects available port starting from 8080

## Project Structure

```
debug-test-001/
├── server.py          # HTTP server + API handlers
├── index.html         # D3.js graph visualization UI
├── data/
│   └── memories.db    # SQLite database (21 facts, 5 relationships)
├── logs/              # Server access logs
└── README.md          # This file
```

## Database Schema

**Facts table**: id, content, category, timestamp, project_tag, embedding
**Relationships table**: source, target, type (5 unique edges)

## Testing

All endpoints verified with live testing:
- 7/7 API tests passed
- 21 facts loaded correctly
- 5 unique relationships established
- Rate limiting functional
- CRUD operations working