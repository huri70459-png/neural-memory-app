#!/usr/bin/env python3
"""
Comprehensive test suite for Neural Memory App (debug-test-001)
Covers: health, CRUD (create/update/delete), search, graph, insights,
rate limiting, CORS, error handling, embeddings column verification.

Uses urllib (stdlib) — no external dependencies.
"""
import urllib.request
import urllib.error
import json
import sys
import os
import time
import base64
import subprocess
import socket
import sqlite3

PROJECT_DIR = "C:/Users/kafsh/neural-memory-app-debug-test-001"
PORT = None  # assigned at runtime
DB_PATH = None


def pick_port():
    for p in range(9100, 9200):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.bind(("localhost", p))
            s.close()
            return p
        except OSError:
            s.close()
    raise RuntimeError("No free port")


def api(method, path, data=None, auth=None):
    url = f"http://localhost:{PORT}{path}"
    req = urllib.request.Request(url, method=method)
    if data is not None:
        req.data = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")
    if auth:
        cred = base64.b64encode(auth.encode()).decode()
        req.add_header("Authorization", f"Basic {cred}")
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        body = resp.read()
        return resp.status, json.loads(body)
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"error": raw.decode("utf-8", "replace")[:200]}
    except Exception as e:
        return None, {"error": str(e)[:200]}


passed = 0
failed = 0


def check(label, ok):
    global passed, failed
    symbol = "PASS" if ok else "FAIL"
    print(f"  [{symbol}] {label}")
    if ok:
        passed += 1
    else:
        failed += 1
    return ok


def wait_for_server(timeout=25):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            s, d = api("GET", "/health")
            if s == 200:
                return d
        except Exception:
            pass
        time.sleep(1)
    return None


# ---------- Test helpers (each returns bool) ----------

def T_health(d):
    print("\n--- Test 1: Health ---")
    check("status == 'ok'", d.get("status") == "ok")
    check("project == 'debug-test-001'", d.get("project") == "debug-test-001")
    check("facts_count is int", isinstance(d.get("facts_count"), int))
    check("facts_count >= 0", d.get("facts_count", -1) >= 0)
    check("relationships is int", isinstance(d.get("relationships"), int))
    check("embeddings == 'active'", d.get("embeddings") == "active")
    check("model == 'all-MiniLM-L6-v2'", d.get("model") == "all-MiniLM-L6-v2")
    check("port is int", isinstance(d.get("port"), int))
    return True


def T_all_facts():
    print("\n--- Test 2: GET /api/facts/all ---")
    s, d = api("GET", "/api/facts/all")
    check("200", s == 200)
    check("has 'facts'", "facts" in d)
    check("has 'count'", "count" in d)
    check("count == len(facts)", len(d.get("facts", [])) == d.get("count", -1))
    check("count >= 21", d.get("count", 0) >= 21)
    if d.get("facts"):
        f = d["facts"][0]
        check("fact has id", "id" in f)
        check("fact has content", "content" in f)
        check("fact has category", "category" in f)
        check("fact has timestamp", "timestamp" in f)
    return True


def T_project_filter():
    print("\n--- Test 3: GET /api/facts?project=... ---")
    s, d = api("GET", "/api/facts?project=debug-test-001")
    check("200", s == 200)
    check("has facts", "facts" in d)
    check("project correct", d.get("project") == "debug-test-001")
    # nonexistent project
    s2, d2 = api("GET", "/api/facts?project=no-such-project-xyz")
    check("unknown project 200", s2 == 200)
    check("unknown project count=0", d2.get("count", 0) == 0)
    return True


def T_create():
    print("\n--- Test 4: CREATE (POST) ---")
    fid = f"fact-{int(time.time()*1000)}"

    s, d = api("POST", "/api/facts", {
        "method": "POST", "id": fid,
        "content": "Created by comprehensive test suite",
        "category": "testing",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    })
    check("create -> 201", s == 201)
    check("success=True", d.get("success") is True)
    check("id matches", d.get("id") == fid)

    # verify present
    s, d = api("GET", "/api/facts?project=debug-test-001")
    rows = [r for r in d.get("facts", []) if r.get("id") == fid]
    check("fact in list", len(rows) == 1)
    if rows:
        check("content correct", rows[0]["content"] == "Created by comprehensive test suite")
        check("category correct", rows[0]["category"] == "testing")

    # duplicate
    s, d = api("POST", "/api/facts", {
        "method": "POST", "id": fid, "content": "dup", "category": "x",
    })
    check("duplicate -> 409", s == 409)

    # missing id
    s, d = api("POST", "/api/facts", {"method": "POST", "content": "x"})
    check("missing id -> 400", s == 400)

    # missing content
    s, d = api("POST", "/api/facts", {"method": "POST", "id": "no-content"})
    check("missing content -> 400", s == 400)
    return True


def T_update():
    print("\n--- Test 5: UPDATE (PUT) ---")
    fid = f"upd-{int(time.time()*1000)}"
    api("POST", "/api/facts", {
        "method": "POST", "id": fid,
        "content": "original", "category": "pre",
    })

    s, d = api("POST", "/api/facts", {
        "method": "PUT", "id": fid, "content": "updated",
    })
    check("update content -> 200", s == 200)
    check("success=True", d.get("success") is True)

    s, d = api("GET", "/api/facts?project=debug-test-001")
    row = [r for r in d["facts"] if r["id"] == fid][0]
    check("content updated", row["content"] == "updated")
    check("category preserved", row["category"] == "pre")

    s, d = api("POST", "/api/facts", {
        "method": "PUT", "id": fid, "category": "post",
    })
    check("update category -> 200", s == 200)
    s, d = api("GET", "/api/facts?project=debug-test-001")
    row = [r for r in d["facts"] if r["id"] == fid][0]
    check("category updated", row["category"] == "post")
    check("content still there", row["content"] == "updated")

    s, d = api("POST", "/api/facts", {
        "method": "PUT", "id": "ghost-xyz", "content": "x",
    })
    check("update ghost -> 404", s == 404)
    return True


def T_delete():
    print("\n--- Test 6: DELETE ---")
    fid = f"del-{int(time.time()*1000)}"
    api("POST", "/api/facts", {
        "method": "POST", "id": fid,
        "content": "will delete", "category": "tmp",
    })

    s, d = api("POST", "/api/facts", {"method": "DELETE", "id": fid})
    check("delete -> 200", s == 200)
    check("success=True", d.get("success") is True)

    s, d = api("GET", "/api/facts?project=debug-test-001")
    rows = [r for r in d.get("facts", []) if r.get("id") == fid]
    check("fact gone", len(rows) == 0)

    s, d = api("POST", "/api/facts", {"method": "DELETE", "id": "ghost-xyz"})
    check("delete ghost -> 404", s == 404)

    s, d = api("POST", "/api/facts", {"method": "DELETE"})
    check("delete missing id -> 400", s == 400)
    return True


def T_search():
    print("\n--- Test 7: SEARCH ---")
    s, d = api("GET", "/api/search?q=memory&project=debug-test-001")
    check("search -> 200", s == 200)
    check("has facts", "facts" in d)
    check("has count", "count" in d)
    check("query echoed", d.get("query") == "memory")
    check("finds results", d.get("count", 0) > 0)

    s, d = api("GET", "/api/search?q=zzz-nonexistent-zzz&project=debug-test-001")
    check("unknown term count=0", d.get("count", 0) == 0)

    s, d = api("GET", "/api/search?q=&project=debug-test-001")
    check("empty query count=0", d.get("count", 0) == 0)
    return True


def T_semantic_search():
    print("\n--- Test 7b: SEMANTIC SEARCH ---")
    # Semantic search should return results even when keyword doesn't match
    # e.g. "neural memory system" should find facts about memory via embedding similarity
    s, d = api("GET", "/api/search?q=neural+memory+system&project=debug-test-001&semantic=true")
    check("semantic search -> 200", s == 200)
    check("has results", "results" in d)
    check("results is list", isinstance(d.get("results"), list))
    # Should find at least 1 fact via embedding similarity
    check("semantic finds results", d.get("count", 0) > 0)
    if d.get("results"):
        r = d["results"][0]
        check("result has id", "id" in r)
        check("result has content", "content" in r)
        check("result has score", "score" in r)
        check("score is float", isinstance(r.get("score"), (int, float)))
        check("score > 0", r.get("score", 0) > 0)
        check("score <= 1", r.get("score", 2) <= 1)
    return True


def T_relationships_crud():
    print("\n--- Test 7c: RELATIONSHIP MANAGEMENT ---")
    # Create a relationship via POST method LINK
    source_id = f"link-src-{int(time.time() * 1000)}"
    target_id = f"link-tgt-{int(time.time() * 1000)}"

    # First create two test facts
    s, d = api("POST", "/api/facts", {
        "method": "POST", "id": source_id,
        "content": "Source fact for relationship testing", "category": "test"
    })
    check("create source -> 201", s == 201)

    s, d = api("POST", "/api/facts", {
        "method": "POST", "id": target_id,
        "content": "Target fact for relationship testing", "category": "test"
    })
    check("create target -> 201", s == 201)

    # Now create a relationship via LINK method
    s, d = api("POST", "/api/facts", {
        "method": "LINK", "source": source_id, "target": target_id, "type": "relates_to"
    })
    check("link -> 201", s == 201)
    check("link success", d.get("success") is True)

    # Verify relationship appears in graph
    s, d = api("GET", "/api/graph?project=debug-test-001")
    check("graph -> 200", s == 200)
    edges = d.get("graph", {}).get("edges", [])
    link_edge = [e for e in edges if e.get("source") == source_id and e.get("target") == target_id]
    check("link edge in graph", len(link_edge) == 1)

    # Delete the source fact should cascade-delete the relationship
    s, d = api("POST", "/api/facts", {
        "method": "DELETE", "id": source_id
    })
    check("delete source -> 200", s == 200)

    # Verify edge is gone after cascade
    s, d = api("GET", "/api/graph?project=debug-test-001")
    edges = d.get("graph", {}).get("edges", [])
    link_edge = [e for e in edges if e.get("source") == source_id]
    check("edge cascade-deleted", len(link_edge) == 0)

    # Clean up target
    api("POST", "/api/facts", {"method": "DELETE", "id": target_id})
    return True


def T_graph():
    print("\n--- Test 8: GRAPH ---")
    s, d = api("GET", "/api/graph?project=debug-test-001")
    check("200", s == 200)
    g = d.get("graph", {})
    check("has nodes", "nodes" in g)
    check("has edges", "edges" in g)
    check("node_count > 0", d.get("node_count", 0) > 0)
    check("node_count matches", len(g.get("nodes", [])) == d.get("node_count", -1))
    check("edge_count matches", len(g.get("edges", [])) == d.get("edge_count", -1))
    if g.get("nodes"):
        n = g["nodes"][0]
        check("node has id", "id" in n)
        check("node has label", "label" in n)
        check("node has size", "size" in n)
        check("node has category", "category" in n)
    if g.get("edges"):
        e = g["edges"][0]
        check("edge has source", "source" in e)
        check("edge has target", "target" in e)
        check("edge has type", "type" in e)
    return True


def T_insights():
    print("\n--- Test 9: INSIGHTS ---")
    s, d = api("GET", "/api/graph/insights?project=debug-test-001")
    check("200", s == 200)
    ins = d.get("insights", {})
    check("total_facts int", isinstance(ins.get("total_facts"), int))
    check("relationship_count int", isinstance(ins.get("relationship_count"), int))
    check("decision_keywords list", isinstance(ins.get("decision_keywords"), list))
    check("memory_patterns list", isinstance(ins.get("memory_patterns"), list))
    check("keyword_analysis dict", isinstance(ins.get("keyword_analysis"), dict))
    return True


def T_rate_limit():
    print("\n--- Test 10: RATE LIMIT ---")
    ok = 0
    for _ in range(5):
        s, _ = api("GET", "/health")
        if s == 200:
            ok += 1
    check(f"{ok}/5 fast requests pass", ok == 5)
    return True


def T_cors():
    print("\n--- Test 11: CORS ---")
    try:
        req = urllib.request.Request(
            f"http://localhost:{PORT}/health", method="OPTIONS"
        )
        resp = urllib.request.urlopen(req, timeout=5)
        check("OPTIONS 200", resp.status == 200)
        h = resp.headers
        check("ACAO header", "Access-Control-Allow-Origin" in h)
        check("ACAM header", "Access-Control-Allow-Methods" in h)
    except Exception as e:
        check(f"OPTIONS failed: {e}", False)
    return True


def T_errors():
    print("\n--- Test 12: ERROR HANDLING ---")
    s, d = api("POST", "/api/facts", {"method": "PATCH", "id": "x"})
    check("PATCH -> 405", s == 405)
    s, d = api("GET", "/api/does-not-exist")
    check("bad path -> 404", s == 404)
    return True


def T_embedding_column():
    print("\n--- Test 13: EMBEDDING COLUMN ---")
    fid = f"emb-{int(time.time()*1000)}"
    s, d = api("POST", "/api/facts", {
        "method": "POST", "id": fid,
        "content": "Verify embedding stored in database",
        "category": "embedding-check",
    })
    check("create -> 201", s == 201)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT embedding FROM facts WHERE id = ?", (fid,))
    row = cur.fetchone()
    conn.close()
    emb = row[0] if row else None
    check("embedding column not null", emb is not None)
    if emb:
        vec = [float(v) for v in emb.split(",")]
        check("dim == 384", len(vec) == 384)
        check("has non-trivial values", any(abs(v) > 0.01 for v in vec))
    return True


def run_all():
    global passed, failed, PORT, DB_PATH
    print("=" * 60)
    print("  Neural Memory App — Comprehensive Test Suite")
    print("=" * 60)

    PORT = pick_port()
    DB_PATH = os.path.join(PROJECT_DIR, "data", "memories.db")

    # clean slate
    try:
        os.remove(DB_PATH)
    except FileNotFoundError:
        pass

    print(f"\n  Starting server on port {PORT} ...")
    proc = subprocess.Popen(
        [sys.executable, "server.py", str(PORT)],
        cwd=PROJECT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    d = wait_for_server()
    if d is None:
        print("  FAILED to start server")
        proc.terminate()
        sys.exit(1)

    print(f"  Server ready — facts={d.get('facts_count')}, embeddings={d.get('embeddings')}")

    try:
        T_health(d)
        T_all_facts()
        T_project_filter()
        T_create()
        T_update()
        T_delete()
        T_search()
        T_semantic_search()
        T_relationships_crud()
        T_graph()
        T_insights()
        T_rate_limit()
        T_cors()
        T_errors()
        T_embedding_column()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    total = passed + failed
    print(f"\n{'='*60}")
    print(f"  RESULTS: {passed}/{total} passed, {failed} failed")
    print(f"{'='*60}")
    return failed == 0


if __name__ == "__main__":
    ok = run_all()
    sys.exit(0 if ok else 1)
