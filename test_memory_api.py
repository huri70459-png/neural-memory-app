#!/usr/bin/env python3
"""
Test suite for Neural Memory App (debug-test-001)
Comprehensive API endpoint testing
"""

import requests
import json
import time
import subprocess
import sys
import os

BASE_URL = "http://localhost:8080"
PROJECT_ID = "debug-test-001"


def wait_for_server(max_retries=10, delay=0.5):
    """Wait for server to be ready."""
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            time.sleep(delay)
    return False


def test_health_endpoint():
    """Test 1: Health check endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert data.get('status') == 'ok', f"Expected status 'ok', got {data.get('status')}"
        assert data.get('project') == PROJECT_ID, f"Expected project '{PROJECT_ID}'"
        
        # Verify facts count
        facts_count = data.get('facts_count', 0)
        print(f"\nFacts count: {facts_count}")
        
        print("\n✓ Health endpoint test PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Health endpoint test FAILED: {e}")
        return False


def test_all_facts_endpoint():
    """Test 2: Get all facts endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Get All Facts Endpoint (GET /api/facts/all)")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/facts/all")
        data = response.json()
        
        print(f"Status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert 'facts' in data, "Missing 'facts' key in response"
        assert 'count' in data, "Missing 'count' key in response"
        
        facts = data['facts']
        count = data['count']
        
        print(f"Facts returned: {count}")
        
        if count > 0:
            print(f"\nFirst fact: {json.dumps(facts[0], indent=2)}")
            
        assert count >= 5, f"Expected at least 5 facts, got {count}"
        
        print("\n✓ All facts endpoint test PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ All facts endpoint test FAILED: {e}")
        return False


def test_project_facts_endpoint():
    """Test 3: Get facts filtered by project"""
    print("\n" + "="*60)
    print("TEST 3: Project Facts Endpoint (GET /api/facts?project=...)")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/facts?project={PROJECT_ID}")
        data = response.json()
        
        print(f"Status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert 'facts' in data, "Missing 'facts' key"
        assert data.get('project') == PROJECT_ID, f"Expected project '{PROJECT_ID}'"
        
        facts = data['facts']
        count = data['count']
        
        print(f"Project: {PROJECT_ID}")
        print(f"Facts returned: {count}")
        
        if count > 0:
            print(f"\nSample facts:")
            for i, fact in enumerate(facts[:3]):
                print(f"  {i+1}. {fact.get('content', 'N/A')[:60]}...")
        
        print("\n✓ Project facts endpoint test PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Project facts endpoint test FAILED: {e}")
        return False


def test_search_endpoint():
    """Test 4: Search facts by keyword"""
    print("\n" + "="*60)
    print("TEST 4: Search Endpoint (GET /api/search?q=...)")
    print("="*60)
    
    try:
        # Test search for "preference"
        response = requests.get(f"{BASE_URL}/api/search?q=preference&project={PROJECT_ID}")
        data = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Query: preference")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert 'facts' in data, "Missing 'facts' key"
        
        facts = data['facts']
        count = data['count']
        
        print(f"Results found: {count}")
        
        if count > 0:
            print(f"\nMatch: {facts[0].get('content', 'N/A')[:60]}...")
        
        # Test search for "python"
        response2 = requests.get(f"{BASE_URL}/api/search?q=python&project={PROJECT_ID}")
        data2 = response2.json()
        
        print(f"\nQuery: python")
        print(f"Results found: {data2.get('count', 0)}")
        
        print("\n✓ Search endpoint test PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Search endpoint test FAILED: {e}")
        return False


def test_graph_endpoint():
    """Test 5: Get graph data"""
    print("\n" + "="*60)
    print("TEST 5: Graph Endpoint (GET /api/graph)")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/graph?project={PROJECT_ID}")
        data = response.json()
        
        print(f"Status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert 'graph' in data, "Missing 'graph' key"
        
        graph = data['graph']
        nodes = graph.get('nodes', [])
        edges = graph.get('edges', [])
        
        print(f"Nodes: {len(nodes)}")
        print(f"Edges: {len(edges)}")
        
        if len(nodes) > 0:
            print(f"\nFirst node: {json.dumps(nodes[0], indent=2)}")
        if len(edges) > 0:
            print(f"First edge: {json.dumps(edges[0], indent=2)}")
        
        print(f"\nNode count: {data.get('node_count', 0)}")
        print(f"Edge count: {data.get('edge_count', 0)}")
        print(f"Project: {data.get('project', 'N/A')}")
        
        print("\n✓ Graph endpoint test PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Graph endpoint test FAILED: {e}")
        return False


def test_graph_insights_endpoint():
    """Test 6: Get graph insights"""
    print("\n" + "="*60)
    print("TEST 6: Graph Insights Endpoint (GET /api/graph/insights)")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/graph/insights?project={PROJECT_ID}")
        data = response.json()
        
        print(f"Status: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert 'insights' in data, "Missing 'insights' key"
        
        insights = data['insights']
        
        print(f"Insights returned: {len(insights)} keys")
        print(f"\nKeys: {list(insights.keys())}")
        
        if 'total_facts' in insights:
            print(f"Total facts: {insights['total_facts']}")
        if 'relationship_count' in insights:
            print(f"Relationship count: {insights['relationship_count']}")
        if 'decision_keywords' in insights:
            print(f"Decision keywords: {insights['decision_keywords']}")
        if 'memory_patterns' in insights:
            print(f"Memory patterns: {insights['memory_patterns']}")
        
        # Verify insights contain expected data
        assert insights.get('total_facts', 0) >= 5, "Too few facts in insights"
        
        print("\n✓ Graph insights endpoint test PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ Graph insights endpoint test FAILED: {e}")
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*60)
    print("NEURAL MEMORY APP - COMPREHENSIVE API TEST SUITE")
    print("="*60)
    print(f"Project: {PROJECT_ID}")
    print(f"Base URL: {BASE_URL}")
    print(f"Port: 8080")
    
    # Wait for server
    print("\nWaiting for server...")
    if not wait_for_server():
        print("✗ Server not responding - is it started?")
        return False
    
    print("✓ Server is running\n")
    
    # Run tests
    results = []
    results.append(("Health Check", test_health_endpoint()))
    results.append(("All Facts", test_all_facts_endpoint()))
    results.append(("Project Facts", test_project_facts_endpoint()))
    results.append(("Search", test_search_endpoint()))
    results.append(("Graph", test_graph_endpoint()))
    results.append(("Graph Insights", test_graph_insights_endpoint()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {name}: {status}")
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == '__main__':
    # Check if server is running
    print("Starting test suite...")
    
    # First check if we can reach the server
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=3)
        if response.status_code == 200:
            print(f"Server is already running at {BASE_URL}")
    except:
        print(f"Server not running at {BASE_URL}")
        print("Please start the server first: python server.py")
        sys.exit(1)
    
    success = run_all_tests()
    sys.exit(0 if success else 1)