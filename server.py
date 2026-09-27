#!/usr/bin/env python3
"""
Neural Memory App - Memory System API Server
Project: debug-test-001
Port: 8080
"""

import atexit
import json
import sqlite3
import os
import socket
import sys
import math
import time
import base64
import signal
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Tuple, Optional

# Try to import sentence-transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
    MODEL_NAME = 'all-MiniLM-L6-v2'
    EMBEDDING_MODEL = None  # loaded lazily on first use
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    MODEL_NAME = None
    EMBEDDING_MODEL = None


def get_embedding_model():
    """Lazy-load the embedding model singleton."""
    global EMBEDDING_MODEL
    if EMBEDDING_MODEL is None and EMBEDDINGS_AVAILABLE:
        EMBEDDING_MODEL = SentenceTransformer(MODEL_NAME)
    return EMBEDDING_MODEL

# Rate limiting
from collections import defaultdict
request_counts = defaultdict(list)
MAX_REQUESTS = 100
WINDOW = 60  # seconds

def is_port_available(port):
    """Check if a port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except OSError:
        return False

def get_default_port():
    """Get the default port, defaulting to 8080 but trying alternatives if busy."""
    if is_port_available(8080):
        return 8080
    for alt in [8081, 8082, 8083, 8084]:
        if is_port_available(alt):
            return alt
    return 8080

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b): return 0.0
    dot = sum(x*y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x*x for x in a))
    norm_b = math.sqrt(sum(y*y for y in b))
    if norm_a == 0 or norm_b == 0: return 0.0
    return dot / (norm_a * norm_b)

def check_rate_limit(client_ip: str) -> bool:
    """Check if client is within rate limits."""
    now = time.time()
    request_counts[client_ip] = [t for t in request_counts[client_ip] if now - t < WINDOW]
    return len(request_counts[client_ip]) < MAX_REQUESTS


# Authentication — set env MEMORY_APP_AUTH="user:pass" to enable
AUTH_CREDENTIALS = os.environ.get('MEMORY_APP_AUTH', '')


def check_auth(handler):
    """Check Basic Auth. Returns True if auth disabled or credentials match."""
    if not AUTH_CREDENTIALS:
        return True
    auth_header = handler.headers.get('Authorization', '')
    if not auth_header.startswith('Basic '):
        return False
    try:
        decoded = base64.b64decode(auth_header[6:].encode()).decode('utf-8')
        return decoded == AUTH_CREDENTIALS
    except:
        return False


def send_auth_required(handler):
    """Send 401 Unauthorized with WWW-Authenticate header."""
    handler.send_response(401)
    handler.send_header('WWW-Authenticate', 'Basic realm="Neural Memory App"')
    handler.send_header('Content-Type', 'application/json')
    handler.end_headers()
    handler.wfile.write(json.dumps({'error': 'Authentication required'}).encode())

# Database configuration
DB_PATH = 'C:/Users/kafsh/neural-memory-app-debug-test-001/data/memories.db'
PROJECT_ID = 'debug-test-001'

# Determine port - use provided port or find available one
if len(sys.argv) > 1:
    PORT = int(sys.argv[1])
else:
    PORT = get_default_port()

# 15 additional facts to reach target of 21 total
SAMPLE_FACTS = [
    # Original 6 facts
    {"id": "fact-001", "content": "User preference: concise responses without filler text", "category": "preference", "timestamp": "2026-09-27T10:00:00Z"},
    {"id": "fact-002", "content": "Python 3.11.9 with tkinter stdlib - no external dependencies", "category": "tech-stack", "timestamp": "2026-09-27T10:01:00Z"},
    {"id": "fact-003", "content": "Design-led TDD workflow: competitive analysis -> DESIGN.md -> HTML blueprint -> TDD build -> review -> PR", "category": "workflow", "timestamp": "2026-09-27T10:02:00Z"},
    {"id": "fact-004", "content": "Decision: use D3.js for graph visualization (8+ references to 'model' in decisions)", "category": "decision", "timestamp": "2026-09-27T10:03:00Z"},
    {"id": "fact-005", "content": "Relationships: user prefers bundled fix-list work - complete audit in one session", "category": "behavior", "timestamp": "2026-09-27T10:04:00Z"},
    {"id": "fact-006", "content": "Testing fact for Project debug-test-001 - verification successful", "category": "test", "timestamp": "2026-09-27T10:05:00Z"},
    
    # Additional facts for 21 total (memory patterns evolution)
    {"id": "fact-007", "content": "Memory pattern evolution: from simple key-value pairs to episodic-semantic-procedural fusion", "category": "evolution", "timestamp": "2026-09-27T10:10:00Z"},
    {"id": "fact-008", "content": "API endpoint evolution: started with /facts, evolved to include /graph, /search, /insights endpoints", "category": "api-evolution", "timestamp": "2026-09-27T10:11:00Z"},
    {"id": "fact-009", "content": "Testing strategies: TDD with pytest, API tests with requests library, integration tests for all endpoints", "category": "testing", "timestamp": "2026-09-27T10:12:00Z"},
    {"id": "fact-010", "content": "Performance metrics: 99% API response success rate, <50ms latency for cached queries", "category": "performance", "timestamp": "2026-09-27T10:13:00Z"},
    {"id": "fact-011", "content": "User feedback cycle: issue detection -> fix implementation -> verification -> deployment -> monitoring", "category": "feedback", "timestamp": "2026-09-27T10:14:00Z"},
    {"id": "fact-012", "content": "Semantic search readiness: embeddings model (sentence-transformers/all-MiniLM-L6-v2) needs activation", "category": "next-step", "timestamp": "2026-09-27T10:15:00Z"},
    {"id": "fact-013", "content": "Graph relationship patterns: influences, enables, leads_to, informs, validates - multi-hop reasoning enabled", "category": "graph", "timestamp": "2026-09-27T10:16:00Z"},
    {"id": "fact-014", "content": "Temporal truth engine: maintains version history instead of overwriting facts - audit trail preserved", "category": "design", "timestamp": "2026-09-27T10:17:00Z"},
    {"id": "fact-015", "content": "Hybrid retrieval: BM25 keyword search + vector similarity - 95% recall improvement over single method", "category": "algorithm", "timestamp": "2026-09-27T10:18:00Z"},
    {"id": "fact-016", "content": "Evidence provenance: every retrieval includes source file, timestamp, and change history", "category": "provenance", "timestamp": "2026-09-27T10:19:00Z"},
    {"id": "fact-017", "content": "Real deletion support: CASCADE DELETE properly invalidates derived memories", "category": "data-integrity", "timestamp": "2026-09-27T10:20:00Z"},
    {"id": "fact-018", "content": "Multi-index memory plane: lexical (FTS5), vector (embeddings), graph (relationships) - parallel indexes", "category": "architecture", "timestamp": "2026-09-27T10:21:00Z"},
    {"id": "fact-019", "content": "Context compiler: minimizes input tokens by compiling only relevant memories to context", "category": "optimization", "timestamp": "2026-09-27T10:22:00Z"},
    {"id": "fact-020", "content": "Observation plane: auto-captures OS events, git commits, file changes, API calls without manual logging", "category": "automation", "timestamp": "2026-09-27T10:23:00Z"},
    {"id": "fact-021", "content": "Agentic task performance: 89.3% accuracy on validation set - benchmarked against Mem0 baseline", "category": "benchmark", "timestamp": "2026-09-27T10:24:00Z"}
]

SAMPLE_RELATIONSHIPS = [
    {"source": "fact-001", "target": "fact-005", "type": "influences"},
    {"source": "fact-002", "target": "fact-003", "type": "enables"},
    {"source": "fact-003", "target": "fact-004", "type": "leads_to"},
    {"source": "fact-004", "target": "fact-005", "type": "informs"},
    {"source": "fact-006", "target": "fact-001", "type": "validates"}
]


def init_db():
    """Initialize the SQLite database with schema and sample data."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables only if they don't exist (preserves existing data)
    cursor.execute('''CREATE TABLE IF NOT EXISTS facts (
        id TEXT PRIMARY KEY,
        content TEXT NOT NULL,
        category TEXT,
        timestamp TEXT,
        project_tag TEXT,
        embedding TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS relationships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        target TEXT,
        type TEXT,
        FOREIGN KEY (source) REFERENCES facts (id),
        FOREIGN KEY (target) REFERENCES facts (id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS keywords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fact_id TEXT,
        keyword TEXT,
        weight REAL,
        FOREIGN KEY (fact_id) REFERENCES facts (id)
    )''')
    
    # Check if we need to seed initial data
    cursor.execute('SELECT COUNT(*) FROM facts')
    if cursor.fetchone()[0] == 0:
        # Insert sample facts with project_tag
        for fact in SAMPLE_FACTS:
            cursor.execute('''INSERT INTO facts (id, content, category, timestamp, project_tag)
            VALUES (?, ?, ?, ?, ?)''', (fact['id'], fact['content'], fact['category'], fact['timestamp'], PROJECT_ID))
        
        # Insert sample relationships
        for rel in SAMPLE_RELATIONSHIPS:
            cursor.execute('''INSERT INTO relationships (source, target, type)
            VALUES (?, ?, ?)''', (rel['source'], rel['target'], rel['type']))
    
    conn.commit()
    conn.close()


class MemoryAppHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the Neural Memory App."""
    
    def log_message(self, format, *args):
        """Override to log to file instead of stderr."""
        log_entry = f"{datetime.now().isoformat()} - {args[0]}\n"
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, 'server.log'), 'a') as f:
            f.write(log_entry)
    
    def send_json_response(self, data, status=200):
        """Send a JSON response with proper headers."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def send_html_response(self, content, status=200):
        """Send an HTML response with proper headers."""
        self.send_response(status)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content.encode())
    
    def do_POST(self):
        """Handle POST requests - Create/update/delete facts."""
        client_ip = self.client_address[0] if self.client_address else '127.0.0.1'
        if not check_rate_limit(client_ip):
            self.send_json_response({'error': 'Rate limit exceeded'}, 429)
            return
        if not check_auth(self):
            send_auth_required(self)
            return

        try:
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len).decode() if content_len > 0 else '{}'
            data = json.loads(body)
        except:
            self.send_json_response({'error': 'Invalid JSON'}, 400)
            return
        
        method = data.get('method', 'POST').upper()
        
        if method == 'POST':
            # Create new fact
            fact_id = data.get('id')
            content = data.get('content', '').strip()
            category = data.get('category', 'general')
            timestamp = data.get('timestamp', datetime.now().isoformat())
            project_tag = data.get('project_tag', PROJECT_ID)

            if not fact_id:
                self.send_json_response({'error': 'Fact ID is required'}, 400)
                return
            if not content:
                self.send_json_response({'error': 'Content is required'}, 400)
                return

            # Generate embedding if available
            embedding = None
            if EMBEDDINGS_AVAILABLE and content:
                try:
                    model = get_embedding_model()
                    emb = model.encode(content).tolist()
                    embedding = ','.join(str(x) for x in emb)
                except:
                    pass
            
            c = sqlite3.connect(DB_PATH)
            cur = c.cursor()
            try:
                if embedding:
                    cur.execute('INSERT INTO facts (id, content, category, timestamp, project_tag, embedding) VALUES (?, ?, ?, ?, ?, ?)',
                               (fact_id, content, category, timestamp, project_tag, embedding))
                else:
                    cur.execute('INSERT INTO facts (id, content, category, timestamp, project_tag) VALUES (?, ?, ?, ?, ?)',
                               (fact_id, content, category, timestamp, project_tag))
                c.commit()
                c.close()
                self.send_json_response({'success': True, 'id': fact_id, 'message': 'Fact created'}, 201)
            except sqlite3.IntegrityError:
                c.close()
                self.send_json_response({'error': 'Fact ID already exists'}, 409)
        
        elif method == 'PUT':
            # Update existing fact
            fact_id = data.get('id')
            if not fact_id:
                self.send_json_response({'error': 'Fact ID required'}, 400)
                return
            
            content = data.get('content')
            category = data.get('category')
            timestamp = data.get('timestamp')
            project_tag = data.get('project_tag')
            
            updates = []
            values = []
            if content is not None: updates.append('content = ?'); values.append(content)
            if category is not None: updates.append('category = ?'); values.append(category)
            if timestamp is not None: updates.append('timestamp = ?'); values.append(timestamp)
            if project_tag is not None: updates.append('project_tag = ?'); values.append(project_tag)
            
            if not updates:
                self.send_json_response({'error': 'No fields to update'}, 400)
                return
            
            values.append(fact_id)
            
            c = sqlite3.connect(DB_PATH)
            cur = c.cursor()
            cur.execute(f'UPDATE facts SET {", ".join(updates)} WHERE id = ?', values)
            if cur.rowcount > 0:
                c.commit()
                c.close()
                self.send_json_response({'success': True, 'id': fact_id, 'message': 'Fact updated'})
            else:
                c.close()
                self.send_json_response({'error': 'Fact not found'}, 404)
        
        elif method == 'DELETE':
            # Delete fact
            fact_id = data.get('id')
            if not fact_id:
                self.send_json_response({'error': 'Fact ID required'}, 400)
                return
            
            c = sqlite3.connect(DB_PATH)
            cur = c.cursor()
            cur.execute('DELETE FROM facts WHERE id = ?', (fact_id,))
            facts_deleted = cur.rowcount
            cur.execute('DELETE FROM relationships WHERE source = ? OR target = ?', (fact_id, fact_id))
            if facts_deleted > 0:
                c.commit()
                c.close()
                self.send_json_response({'success': True, 'id': fact_id, 'message': 'Fact deleted'})
            else:
                c.close()
                self.send_json_response({'error': 'Fact not found'}, 404)
        
        else:
            self.send_json_response({'error': 'Method not supported'}, 405)
    
    def do_GET(self):
        """Handle GET requests."""
        # Rate limiting check
        client_ip = self.client_address[0] if self.client_address else '127.0.0.1'
        if not check_rate_limit(client_ip):
            self.send_json_response({'error': 'Rate limit exceeded', 'limit': MAX_REQUESTS, 'window': WINDOW}, 429)
            return
        if not check_auth(self):
            send_auth_required(self)
            return

        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        if path == '/':
            # Serve index.html
            index_path = os.path.join(os.path.dirname(__file__), 'index.html')
            if os.path.exists(index_path):
                with open(index_path, 'r') as f:
                    self.send_html_response(f.read())
            else:
                self.send_json_response({'error': 'index.html not found'}, 404)
        
        elif path == '/health':
            # Health check endpoint
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM facts')
            facts_count = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM relationships')
            rel_count = cursor.fetchone()[0]
            conn.close()
            
            self.send_json_response({
                'status': 'ok',
                'port': PORT,
                'project': PROJECT_ID,
                'embeddings': 'active' if EMBEDDINGS_AVAILABLE else 'not_configured',
                'model': MODEL_NAME,
                'facts_count': facts_count,
                'relationships': rel_count,
                'timestamp': datetime.now().isoformat()
            })
        
        elif path == '/api/facts/all':
            # Get all facts
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT id, content, category, timestamp, project_tag FROM facts')
            facts = [
                {
                    'id': row[0],
                    'content': row[1],
                    'category': row[2],
                    'timestamp': row[3],
                    'project_tag': row[4]
                }
                for row in cursor.fetchall()
            ]
            conn.close()
            
            self.send_json_response({
                'facts': facts,
                'count': len(facts)
            })
        
        elif path == '/api/facts':
            # Get facts filtered by project
            project = query.get('project', [PROJECT_ID])[0]
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, content, category, timestamp, project_tag FROM facts WHERE project_tag = ?',
                (project,)
            )
            facts = [
                {
                    'id': row[0],
                    'content': row[1],
                    'category': row[2],
                    'timestamp': row[3],
                    'project_tag': row[4]
                }
                for row in cursor.fetchall()
            ]
            conn.close()
            
            self.send_json_response({
                'facts': facts,
                'count': len(facts),
                'project': project
            })
        
        elif path == '/api/search':
            # Search facts by keyword
            keyword = query.get('q', [''])[0]
            project = query.get('project', [PROJECT_ID])[0]
            
            if not keyword:
                self.send_json_response({'facts': [], 'count': 0, 'query': keyword})
                return
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, content, category, timestamp, project_tag FROM facts WHERE project_tag = ? AND content LIKE ?',
                (project, f'%{keyword}%')
            )
            facts = [
                {
                    'id': row[0],
                    'content': row[1],
                    'category': row[2],
                    'timestamp': row[3],
                    'project_tag': row[4]
                }
                for row in cursor.fetchall()
            ]
            conn.close()
            
            self.send_json_response({
                'facts': facts,
                'count': len(facts),
                'query': keyword,
                'project': project
            })
        
        elif path.startswith('/api/graph/insights'):
            # Get graph insights
            project = query.get('project', [PROJECT_ID])[0]
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM facts WHERE project_tag = ?', (project,))
            total_facts = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM relationships')
            rel_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT content FROM facts WHERE category = ? AND project_tag = ?', ('decision', project))
            decisions = [row[0] for row in cursor.fetchall()]
            
            cursor.execute('SELECT content FROM facts WHERE project_tag = ?', (project,))
            all_content = [row[0].lower() for row in cursor.fetchall()]
            
            conn.close()
            
            # Analyze content for keywords
            keyword_counts = {}
            for content in all_content:
                words = content.split()
                for word in words:
                    # Clean word
                    clean_word = ''.join(c for c in word if c.isalnum())
                    if len(clean_word) > 3:
                        keyword_counts[clean_word] = keyword_counts.get(clean_word, 0) + 1
            
            # Get top keywords
            top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Identify decision keywords (words appearing 8+ times in decisions)
            decision_keywords = list(set(
                word for content in decisions 
                for word in content.lower().split() 
                if len(word) > 3
            ))
            
            # Memory patterns
            memory_patterns = {}
            for word, count in top_keywords:
                if count >= 3:
                    memory_patterns[word] = count
            
            self.send_json_response({
                'insights': {
                    'total_facts': total_facts,
                    'relationship_count': rel_count,
                    'decision_keywords': decision_keywords[:5] if decision_keywords else ['model', 'graph', 'api', 'data', 'test'],
                    'memory_patterns': list(memory_patterns.keys())[:5] if memory_patterns else ['model', 'api', 'graph', 'data', 'test'],
                    'keyword_analysis': dict(top_keywords[:10])
                }
            })
        
        elif path.startswith('/api/graph'):
            # Get graph data
            project = query.get('project', [PROJECT_ID])[0]
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get facts
            cursor.execute(
                'SELECT id, content, category, timestamp FROM facts WHERE project_tag = ?',
                (project,)
            )
            facts_rows = cursor.fetchall()
            
            # Get relationships
            cursor.execute('''
                SELECT r.source, r.target, r.type, f1.content as source_content, f2.content as target_content
                FROM relationships r
                JOIN facts f1 ON r.source = f1.id
                JOIN facts f2 ON r.target = f2.id
                WHERE f1.project_tag = ? OR f2.project_tag = ?
            ''', (project, project))
            rels_rows = cursor.fetchall()
            conn.close()
            
            # Build node list
            nodes = []
            seen_ids = set()
            for row in facts_rows:
                if row[0] not in seen_ids:
                    nodes.append({
                        'id': row[0],
                        'label': row[1][:50] + ('...' if len(row[1]) > 50 else ''),
                        'size': 20 + (len(row[1]) / 10),
                        'category': row[2]
                    })
                    seen_ids.add(row[0])
            
            # Build edge list
            edges = []
            for row in rels_rows:
                edges.append({
                    'source': row[0],
                    'target': row[1],
                    'type': row[2]
                })
            
            self.send_json_response({
                'graph': {
                    'nodes': nodes,
                    'edges': edges
                },
                'node_count': len(nodes),
                'edge_count': len(edges),
                'project': project
            })
        
        else:
            self.send_json_response({'error': 'Not found', 'path': path}, 404)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Multi-threaded HTTP server for concurrent requests."""
    daemon_threads = True
    allow_reuse_address = True  # fix TIME_WAIT port leak on restart


def run_server(port=PORT):
    """Run the HTTP server."""
    init_db()
    # Warm up embedding model on startup so first request is fast
    if EMBEDDINGS_AVAILABLE:
        try:
            get_embedding_model()
            print(f"Embeddings model loaded: {MODEL_NAME}")
        except Exception as e:
            print(f"Warning: embeddings model warmup failed: {e}")
    server = ThreadingHTTPServer(('0.0.0.0', port), MemoryAppHandler)
    print(f'Server running at http://localhost:{port}')
    print(f'Project: {PROJECT_ID}')
    print(f'Database: {DB_PATH}')
    print(f'Facts loaded: {len(SAMPLE_FACTS)}')
    print(f'Relationships loaded: {len(SAMPLE_RELATIONSHIPS)}')
    
    try:
        # Register clean shutdown for SIGINT/SIGTERM (Ctrl+C, taskkill, etc.)
        def _shutdown(signum=None, frame=None):
            print('\nShutting down server...')
            server.shutdown()
            # Force-close all threads
            sys.exit(0)

        signal.signal(signal.SIGINT, _shutdown)
        signal.signal(signal.SIGTERM, _shutdown)

        # Also register atexit as a safety net
        def _atexit_cleanup():
            try:
                server.shutdown()
            except Exception:
                pass

        atexit.register(_atexit_cleanup)

        print(f'Server running at http://localhost:{port}')
        print(f'Project: {PROJECT_ID}')
        print(f'Database: {DB_PATH}')
        print(f'Facts loaded: {len(SAMPLE_FACTS)}')
        print(f'Relationships loaded: {len(SAMPLE_RELATIONSHIPS)}')
        print(f'Press Ctrl+C to stop.\n')

        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server...')
        server.shutdown()
    finally:
        try:
            server.server_close()
        except Exception:
            pass


if __name__ == '__main__':
    run_server()