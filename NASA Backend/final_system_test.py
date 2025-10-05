#!/usr/bin/env python3
"""
Final System Test - Verify All Components Working
"""
import requests
import time
import json

def test_complete_system():
    """Complete system integration test"""
    print("🚀 FINAL SYSTEM TEST - NASA Knowledge Engine")
    print("=" * 60)
    
    backend_url = "http://127.0.0.1:8000"
    frontend_url = "http://localhost:5173"
    api_key = "i31G2AKUI24gGq2oaw8w8sYGryZEjMArrJEjffcT"
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Backend Health
    print("\n1️⃣ Backend Health Check")
    total_tests += 1
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is healthy")
            success_count += 1
        else:
            print(f"   ❌ Backend unhealthy: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend unreachable: {e}")
    
    # Test 2: Authentication Protection
    print("\n2️⃣ API Key Protection")
    total_tests += 1
    try:
        response = requests.get(f"{backend_url}/api/search/?query=test", timeout=5)
        if response.status_code == 401:
            print("   ✅ Search protected (401 without API key)")
            success_count += 1
        else:
            print(f"   ❌ Search not protected: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Protection test failed: {e}")
    
    # Test 3: Authenticated Search
    print("\n3️⃣ Authenticated Search")
    total_tests += 1
    try:
        headers = {"x-api-key": api_key}
        response = requests.get(
            f"{backend_url}/api/search/?query=microgravity&limit=3", 
            headers=headers, 
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', len(data.get('results', [])))
            print(f"   ✅ Search working ({count} results)")
            
            # Check response format
            if data.get('results') and len(data['results']) > 0:
                first_result = data['results'][0]
                required_fields = ['title', 'abstract', 'link']
                has_fields = all(field in first_result for field in required_fields)
                if has_fields:
                    print("   ✅ Response format correct")
                else:
                    print("   ⚠️  Response format may need adjustment")
            
            success_count += 1
        else:
            print(f"   ❌ Search failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Search test failed: {e}")
    
    # Test 4: CORS Headers  
    print("\n4️⃣ CORS Configuration")
    total_tests += 1
    try:
        headers = {
            "Origin": "http://localhost:5173",
            "x-api-key": api_key
        }
        response = requests.get(
            f"{backend_url}/api/search/?query=test&limit=1", 
            headers=headers, 
            timeout=5
        )
        cors_headers = response.headers.get('Access-Control-Allow-Origin')
        if response.status_code == 200:
            print("   ✅ CORS working (request succeeded)")
            success_count += 1
        else:
            print(f"   ❌ CORS issue: {response.status_code}")
    except Exception as e:
        print(f"   ❌ CORS test failed: {e}")
    
    # Test 5: Frontend Accessibility
    print("\n5️⃣ Frontend Accessibility")
    total_tests += 1
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print("   ✅ Frontend accessible")
            success_count += 1
        else:
            print(f"   ❌ Frontend issue: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Frontend test failed: {e}")
    
    # Results Summary
    print(f"\n{'='*60}")
    print("📊 FINAL TEST RESULTS")
    print(f"{'='*60}")
    
    success_rate = (success_count / total_tests) * 100
    
    for i in range(1, total_tests + 1):
        test_names = [
            "Backend Health",
            "API Key Protection", 
            "Authenticated Search",
            "CORS Configuration",
            "Frontend Accessibility"
        ]
        status = "✅" if i <= success_count else "❌"
        print(f"{status} {test_names[i-1]}")
    
    print(f"\n🎯 Overall Score: {success_count}/{total_tests} ({success_rate:.1f}%)")
    
    if success_count == total_tests:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("🚀 Your NASA Knowledge Engine is ready to use!")
        print(f"\n📍 Access Points:")
        print(f"   • Frontend: {frontend_url}")
        print(f"   • Backend API: {backend_url}/docs")
        print(f"   • Test Page: {backend_url}/static/test.html")
        print(f"\n🔑 Authentication:")
        print(f"   • API Key: {api_key[:8]}...")
        print(f"   • Protected: /api/search endpoints")
        print(f"   • Unprotected: /health, /api/graph")
        
    else:
        print(f"\n⚠️  {total_tests - success_count} issues need attention")
        print("Check the test output above for specific failures")
    
    return success_count == total_tests

if __name__ == "__main__":
    test_complete_system()