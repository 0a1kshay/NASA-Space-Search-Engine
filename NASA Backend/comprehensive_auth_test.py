#!/usr/bin/env python3
"""
Comprehensive Authentication Test for NASA Backend
Tests all scenarios and provides detailed feedback
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "i31G2AKUI24gGq2oaw8w8sYGryZEjMArrJEjffcT"

def test_scenario(name, url, headers=None, expected_status=200):
    """Test a specific scenario and return results"""
    print(f"\n🧪 Test: {name}")
    print(f"   URL: {url}")
    if headers:
        print(f"   Headers: {headers}")
    
    try:
        response = requests.get(url, headers=headers or {})
        success = response.status_code == expected_status
        status_icon = "✅" if success else "❌"
        
        print(f"   {status_icon} Status: {response.status_code} (expected {expected_status})")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'results' in data:
                    print(f"   📊 Results: {len(data['results'])} articles found")
                    if data['results']:
                        print(f"   📖 Sample: {data['results'][0].get('title', 'N/A')[:50]}...")
                elif 'message' in data:
                    print(f"   💬 Message: {data['message']}")
            except:
                print(f"   📄 Response: {response.text[:100]}...")
        elif response.status_code == 401:
            try:
                error_data = response.json()
                print(f"   🔒 Error: {error_data.get('detail', {}).get('error', 'Authentication failed')}")
            except:
                print(f"   🔒 Error: Unauthorized")
        else:
            print(f"   ⚠️  Response: {response.text[:100]}...")
            
        return success, response.status_code
        
    except Exception as e:
        print(f"   💥 Exception: {e}")
        return False, 0

def main():
    print("🚀 NASA Backend Authentication & API Tests")
    print("=" * 60)
    
    results = []
    
    # Test 1: Health check (no auth required)
    success, status = test_scenario(
        "Health Check (No Auth Required)",
        f"{BASE_URL}/health",
        expected_status=200
    )
    results.append(("Health Check", success))
    
    # Test 2: Search without API key (should fail with 401)
    success, status = test_scenario(
        "Search Without API Key (Should Fail)",
        f"{BASE_URL}/api/search/?query=microgravity&limit=2",
        expected_status=401
    )
    results.append(("Search No Auth", success))
    
    # Test 3: Search with correct API key (should work)
    success, status = test_scenario(
        "Search With Correct API Key (Should Work)",
        f"{BASE_URL}/api/search/?query=microgravity&limit=2",
        headers={"x-api-key": API_KEY},
        expected_status=200
    )
    results.append(("Search With Auth", success))
    
    # Test 4: Search with wrong API key (should fail)
    success, status = test_scenario(
        "Search With Wrong API Key (Should Fail)",
        f"{BASE_URL}/api/search/?query=microgravity&limit=2",
        headers={"x-api-key": "wrong-key-12345"},
        expected_status=401
    )
    results.append(("Search Wrong Auth", success))
    
    # Test 5: Graph endpoint (no auth required)
    success, status = test_scenario(
        "Graph Endpoint (No Auth Required)",
        f"{BASE_URL}/api/graph/",
        expected_status=200
    )
    results.append(("Graph No Auth", success))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    for test_name, success in results:
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}")
    
    print(f"\n🎯 Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Your API authentication is working perfectly!")
        print("\n🚀 Your Frontend Should Work With These Settings:")
        print(f"   • API Key: {API_KEY}")
        print("   • Header: x-api-key")
        print("   • Protected Endpoints: /api/search/*")
        print("   • Unprotected Endpoints: /health, /api/graph/*")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()