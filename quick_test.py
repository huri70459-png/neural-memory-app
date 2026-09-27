#!/usr/bin/env python3
"""Quick inline test runner for Neural Memory App."""
import urllib.request, urllib.error, json, sys, time, socket, subprocess, sqlite3, os

PROJECT_DIR = os.getcwd()
PORT = None

def pick_port():
    for p in range(9150, 9200):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.bind(('localhost', p))
            s.close()
            return p
        except OSError:
            s.close()
    raise RuntimeError('No free port')

def api(method, path, data=None):
    url = f'http://localhost:{PORT}{path}'
    req = urllib.request.Request(url, method=method)
    if data is not None:
        req.data = json.dumps(data).encode()
        req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except:
            return e.code, {'error': raw.decode('utf-8', 'replace')[:200]}
    except Exception as e:
        return None, {'error': str(e)[:200]}

passed = 0
failed = 0

def chk(label, ok):
    global passed, failed
    s = 'PASS' if ok else 'FAIL'
    print(f'  [{s}] {label}')
    if ok:
        passed += 1
    else:
        failed += 1
    return ok

PORT = pick_port()
DB_PATH = os.path.join(PROJECT_DIR, 'data', 'memories.db')

# Remove old DB
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

print(f'Starting server on port {PORT}...')
proc = subprocess.Popen(
    [sys.executable, 'server.py', str(PORT)],
    cwd=PROJECT_DIR,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

# Wait for server
for _ in range(20):
    try:
        s, d = api('GET', '/health', timeout=2)
        if s == 200:
            print(f'Server ready: facts={d.get("facts_count")}, embeddings={d.get("embeddings")}')
            break
    except:
        time.sleep(1)
else:
    print('Server failed to start')
    proc.terminate()
    sys.exit(1)

try:
    # Test 1: Health
    print('\n--- Test 1: Health ---')
    s, d = api('GET', '/health')
    chk('200', s == 200)
    chk('status=ok', d.get('status') == 'ok')
    chk('project correct', d.get('project') == 'debug-test-001')
    chk('embeddings active', d.get('embeddings') == 'active')
    chk('model correct', d.get('model') == 'all-MiniLM-L6-v2')
    chk('facts >= 21', d.get('facts_count', 0) >= 21)
    chk('has relationships', isinstance(d.get('relationships'), int))

    # Test 2: All facts
    print('\n--- Test 2: GET /api/facts/all ---')
    s, d = api('GET', '/api/facts/all')
    chk('200', s == 200)
    chk('has facts', 'facts' in d)
    chk('has count', 'count' in d)
    chk('count match', len(d.get('facts', [])) == d.get('count', -1))
    chk('count >= 21', d.get('count', 0) >= 21)
    if d.get('facts'):
        f = d['facts'][0]
        chk('fact has id', 'id' in f)
        chk('fact has content', 'content' in f)
        chk('fact has category', 'category' in f)
        chk('fact has timestamp', 'timestamp' in f)

    # Test 3: Project filter
    print('\n--- Test 3: Project filter ---')
    s, d = api('GET', '/api/facts?project=debug-test-001')
    chk('200', s == 200)
    chk('correct project', d.get('project') == 'debug-test-001')
    chk('has facts', 'facts' in d)
    s, d = api('GET', '/api/facts?project=nonexistent')
    chk('unknown -> 0', d.get('count', 0) == 0)

    # Test 4: Create
    print('\n--- Test 4: Create ---')
    fid = f'crud-{int(time.time()*1000)}'
    s, d = api('POST', '/api/facts', {
        'method': 'POST', 'id': fid,
        'content': 'Created by test suite',
        'category': 'testing',
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ')
    })
    chk('Create -> 201', s == 201)
    chk('success=True', d.get('success') is True)
    chk('id matches', d.get('id') == fid)
    s, d = api('GET', '/api/facts?project=debug-test-001')
    rows = [r for r in d.get('facts', []) if r.get('id') == fid]
    chk('In list', len(rows) == 1)
    if rows:
        chk('Content correct', rows[0]['content'] == 'Created by test suite')
        chk('Category correct', rows[0]['category'] == 'testing')
    s, d = api('POST', '/api/facts', {'method': 'POST', 'id': fid, 'content': 'dup', 'category': 'x'})
    chk('Duplicate -> 409', s == 409)
    s, d = api('POST', '/api/facts', {'method': 'POST', 'content': 'no-id'})
    chk('Missing ID -> 400', s == 400)

    # Test 5: Update
    print('\n--- Test 5: Update ---')
    fid2 = f'upd-{int(time.time()*1000)}'
    api('POST', '/api/facts', {'method': 'POST', 'id': fid2, 'content': 'original', 'category': 'pre'})
    s, d = api('POST', '/api/facts', {'method': 'PUT', 'id': fid2, 'content': 'updated'})
    chk('Update -> 200', s == 200)
    chk('success=True', d.get('success') is True)
    s, d = api('GET', '/api/facts?project=debug-test-001')
    row = [r for r in d['facts'] if r['id'] == fid2][0]
    chk('Content updated', row['content'] == 'updated')
    chk('Category preserved', row['category'] == 'pre')
    s, d = api('POST', '/api/facts', {'method': 'PUT', 'id': fid2, 'category': 'post'})
    chk('Category update -> 200', s == 200)
    s, d = api('GET', '/api/facts?project=debug-test-001')
    row = [r for r in d['facts'] if r['id'] == fid2][0]
    chk('Category updated', row['category'] == 'post')
    chk('Content preserved', row['content'] == 'updated')
    s, d = api('POST', '/api/facts', {'method': 'PUT', 'id': 'ghost-xyz', 'content': 'x'})
    chk('Ghost update -> 404', s == 404)

    # Test 6: Delete
    print('\n--- Test 6: Delete ---')
    fid3 = f'del-{int(time.time()*1000)}'
    api('POST', '/api/facts', {'method': 'POST', 'id': fid3, 'content': 'to delete', 'category': 'tmp'})
    s, d = api('POST', '/api/facts', {'method': 'DELETE', 'id': fid3})
    chk('Delete -> 200', s == 200)
    chk('success=True', d.get('success') is True)
    s, d = api('GET', '/api/facts?project=debug-test-001')
    rows = [r for r in d.get('facts', []) if r.get('id') == fid3]
    chk('Gone from list', len(rows) == 0)
    s, d = api('POST', '/api/facts', {'method': 'DELETE', 'id': 'ghost-xyz'})
    chk('Ghost delete -> 404', s == 404)
    s, d = api('POST', '/api/facts', {'method': 'DELETE'})
    chk('Missing id delete -> 400', s == 400)

    # Test 7: Search
    print('\n--- Test 7: Search ---')
    s, d = api('GET', '/api/search?q=memory&project=debug-test-001')
    chk('Search 200', s == 200)
    chk('Has facts', 'facts' in d)
    chk('Has count', 'count' in d)
    chk('Query echoed', d.get('query') == 'memory')
    chk('Finds results', d.get('count', 0) > 0)
    s, d = api('GET', '/api/search?q=zzz-nonexistent-zzz&project=debug-test-001')
    chk('Unknown -> 0', d.get('count', 0) == 0)

    # Test 8: Graph
    print('\n--- Test 8: Graph ---')
    s, d = api('GET', '/api/graph?project=debug-test-001')
    chk('Graph 200', s == 200)
    g = d.get('graph', {})
    chk('Has nodes', 'nodes' in g)
    chk('Has edges', 'edges' in g)
    chk('Node count >0', d.get('node_count', 0) > 0)
    chk('Node count match', len(g.get('nodes', [])) == d.get('node_count', -1))
    if g.get('nodes'):
        n = g['nodes'][0]
        chk('Node id', 'id' in n)
        chk('Node label', 'label' in n)
        chk('Node category', 'category' in n)
    if g.get('edges'):
        e = g['edges'][0]
        chk('Edge source', 'source' in e)
        chk('Edge target', 'target' in e)
        chk('Edge type', 'type' in e)
    chk('Edge count match', len(g.get('edges', [])) == d.get('edge_count', -1))

    # Test 9: Insights
    print('\n--- Test 9: Insights ---')
    s, d = api('GET', '/api/graph/insights?project=debug-test-001')
    chk('Insights 200', s == 200)
    ins = d.get('insights', {})
    chk('total_facts int', isinstance(ins.get('total_facts'), int))
    chk('rel count int', isinstance(ins.get('relationship_count'), int))
    chk('decision_keywords list', isinstance(ins.get('decision_keywords'), list))
    chk('memory_patterns list', isinstance(ins.get('memory_patterns'), list))
    chk('keyword_analysis dict', isinstance(ins.get('keyword_analysis'), dict))

    # Test 10: Rate limit
    print('\n--- Test 10: Rate limit ---')
    ok_count = 0
    for _ in range(5):
        s, _ = api('GET', '/health')
        if s == 200:
            ok_count += 1
    chk(f'{ok_count}/5 pass', ok_count == 5)

    # Test 11: CORS
    print('\n--- Test 11: CORS ---')
    try:
        req = urllib.request.Request(f'http://localhost:{PORT}/health', method='OPTIONS')
        resp = urllib.request.urlopen(req, timeout=5)
        chk('OPTIONS 200', resp.status == 200)
        chk('ACAO header', 'Access-Control-Allow-Origin' in resp.headers)
    except Exception as e:
        chk(f'OPTIONS failed: {e}', False)

    # Test 12: Errors
    print('\n--- Test 12: Error handling ---')
    s, d = api('POST', '/api/facts', {'method': 'PATCH', 'id': 'x'})
    chk('PATCH -> 405', s == 405)
    s, d = api('GET', '/api/does-not-exist')
    chk('Bad path -> 404', s == 404)

    # Test 13: Embedding column
    print('\n--- Test 13: Embedding column ---')
    fid4 = f'emb-{int(time.time()*1000)}'
    s, d = api('POST', '/api/facts', {
        'method': 'POST', 'id': fid4,
        'content': 'Embedding verification',
        'category': 'emb-test'
    })
    chk('Create -> 201', s == 201)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT embedding FROM facts WHERE id=?', (fid4,))
    row = cur.fetchone()
    conn.close()
    emb = row[0] if row else None
    chk('Embedding not null', emb is not None)
    if emb:
        vec = [float(v) for v in emb.split(',')]
        chk('dim == 384', len(vec) == 384)
        chk('Non-trivial values', any(abs(v) > 0.01 for v in vec))

finally:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except:
        proc.kill()

total = passed + failed
print(f'\n{"="*55}')
print(f'  RESULTS: {passed}/{total} passed, {failed} failed')
print(f'{"="*55}')
sys.exit(0 if failed == 0 else 1)
