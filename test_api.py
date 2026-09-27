#!/usr/bin/env python3
"""
Quick API tests for Neural Memory App (debug-test-001)
Tests core functionality: health, facts, graph, insights, search
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8080"
PROJECT_ID = "debug-test-001"

def test_health():
    """Test health endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        data = r.json()
        print(f"✅ Health: {data.get('status')} | Facts: {data.get('facts_count', 0)}")
        return r.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_facts():
    """Test facts endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/api/facts?project={PROJECT_ID}", timeout=5)
        data = r.json()
        count = data.get('count', 0)
        print(f"✅ Facts: {count} facts retrieved")
        return count >= 5
    except Exception as e:
        print(f"❌ Facts check failed: {e}")
        return False

def test_graph():
    """Test graph endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/api/graph?project={PROJECT_ID}", timeout=5)
        data = r.json()
        graph = data.get('graph', {})
        nodes = len(graph.get('nodes', []))
        edges = len(graph.get('edges', []))
        print(f"✅ Graph: {nodes} nodes, {edges} edges")
        return nodes > 0
    except Exception as e:
        print(f"❌ Graph check failed: {e}")
        return False

def test_insights():
    """Test insights endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/api/graph/insights?project={PROJECT_ID}", timeout=5)
        data = r.json()
        insights = data.get('insights', {})
        facts = insights.get('total_facts', 0)
        keywords = len(insights.get('keyword_analysis', {}))
        print(f"✅ Insights: {facts} facts, {keywords} keyword patterns")
        return facts >= 5
    except Exception as e:
        print(f"❌ Insights check failed: {e}")
        return False

def test_search():
    """Test search endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/api/search?q=memory&project={PROJECT_ID}", timeout=5)
        data = r.json()
        count = data.get('count', 0)
        print(f"✅ Search: 'memory' found {count} results")
        return True
    except Exception as e:
        print(f"❌ Search check failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Neural Memory App - Quick API Tests")
    print("=" * 50)
    
    tests = [
        ("Health", test_health),
        ("Facts", test_facts),
        ("Graph", test_graph),
        ("Insights", test_insights),
        ("Search", test_search),
    ]
    
    results = [(name, test()) for name, test in tests]
    
    print("\n" + "=" * 50)
    passed = sum(1 for _, r in results if r)
    print(f"Results: {passed}/{len(results)} tests passed")
    print("=" * 50)
    
    if passed < len(tests):
        sys.exit(1)