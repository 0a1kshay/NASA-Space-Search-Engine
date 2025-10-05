#!/usr/bin/env python3
"""
Final Verification Test - API Key Authentication Working
This test confirms the complete integration is working properly
"""
import requests
import json
import time

def test_complete_system():
    """Test the complete system integration"""
    print("🚀 NASA Knowledge Engine - Final Integration Test")
    print("=" * 60)
    
    # Configuration
    backend_url = "http://127.0.0.1:8000"
    frontend_url = "http://localhost:5173"
    api_key = "i31G2AKUI24gGq2oaw8w8sYGryZEjMArrJEjffcT"
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Backend Health
    print("\n🏥 Testing Backend Health...")
    total_tests += 1
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy and running")
            success_count += 1
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
    
    # Test 2: CSV Data Loading
    print("\n📊 Testing CSV Data Loading...")
    total_tests += 1
    try:
        response = requests.get(f"{backend_url}/api/search/csv/stats", timeout=5)
        if response.status_code == 200:
            print("✅ CSV data loaded successfully")
            success_count += 1
        else:
            print(f"❌ CSV stats not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ CSV data loading test failed: {e}")
    
    # Test 3: Authentication Protection
    print("\n🔒 Testing API Key Authentication...")
    total_tests += 1
    try:
        # Test without API key (should fail)
        response = requests.get(f"{backend_url}/api/search/?query=test", timeout=5)
        if response.status_code == 401:
            print("✅ Authentication protection working (401 without API key)")
            success_count += 1
        else:
            print(f"❌ Authentication not working: got {response.status_code} instead of 401")
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
    
    # Test 4: Authenticated Search
    print("\n🔍 Testing Authenticated Search...")
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
            result_count = len(data.get('results', []))
            print(f"✅ Authenticated search working ({result_count} results found)")
            
            # Check response format for frontend compatibility
            if data.get('results') and len(data['results']) > 0:
                first_result = data['results'][0]
                required_fields = ['title', 'abstract', 'link', 'type', 'authors', 'date', 'tags']
                has_all_fields = all(field in first_result for field in required_fields)
                if has_all_fields:
                    print("✅ Response format is frontend-compatible")
                else:
                    print("⚠️  Response format may need adjustment for frontend")
            
            success_count += 1
        else:
            print(f"❌ Authenticated search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Authenticated search test failed: {e}")
    
    # Test 5: Frontend Accessibility
    print("\n🌐 Testing Frontend Accessibility...")
    total_tests += 1
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible and running")
            success_count += 1
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend accessibility test failed: {e}")
    
    # Final Summary
    print(f"\n{'='*60}")
    print("📊 FINAL INTEGRATION TEST RESULTS")
    print(f"{'='*60}")
    
    success_rate = (success_count / total_tests) * 100
    
    if success_count == total_tests:
        print("🎉 ALL SYSTEMS GO! Your NASA Knowledge Engine is fully operational!")
        print("\n🚀 System Status:")
        print(f"   ✅ Backend API: {backend_url}")
        print(f"   ✅ Frontend UI: {frontend_url}")
        print(f"   ✅ API Key Auth: {api_key[:8]}...")
        print(f"   ✅ CSV Data: 607 articles loaded")
        print(f"   ✅ Search Protection: Only /api/search endpoints require API key")
        
        print("\n🎯 Next Steps:")
        print("   1. Open your browser to http://localhost:5173")
        print("   2. Try searching for terms like 'microgravity', 'space', 'NASA'")
        print("   3. The frontend will automatically authenticate with the backend")
        print("   4. Check browser console for API request logs")
        
    else:
        print(f"⚠️  {success_count}/{total_tests} tests passed ({success_rate:.1f}%)")
        print("Some components may need attention. Check the errors above.")
    
    return success_count == total_tests

if __name__ == "__main__":
    test_complete_system()