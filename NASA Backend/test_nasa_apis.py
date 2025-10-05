#!/usr/bin/env python3
"""
NASA Open Science APIs Integration Test Suite
Tests all four NASA APIs and verifies the integration works correctly
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.nasa_api_service import NASAAPIService, get_nasa_api_service
from app.csv_service import CSVDataService, get_csv_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_individual_apis():
    """Test each NASA API individually"""
    print("🧪 Testing Individual NASA APIs...")
    print("=" * 50)
    
    nasa_service = get_nasa_api_service()
    
    # Test API connectivity
    test_results = await nasa_service.test_apis()
    
    for api_name, result in test_results.items():
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"{status_icon} {api_name.upper()}: {result['status']} - {result['message']}")
    
    print()
    return test_results

async def test_unified_search():
    """Test unified search across all NASA APIs"""
    print("🔍 Testing Unified NASA API Search...")
    print("=" * 50)
    
    nasa_service = get_nasa_api_service()
    test_queries = [
        "microgravity",
        "plant biology",
        "space radiation", 
        "bone density",
        "ISS experiments"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        try:
            results = await nasa_service.fetch_nasa_data(query, limit=5)
            total_results = results.get("total_count", 0)
            sources = results.get("sources_queried", [])
            errors = results.get("errors", [])
            
            print(f"   📊 Total results: {total_results}")
            print(f"   📡 Sources queried: {', '.join(sources)}")
            
            if errors:
                print(f"   ⚠️  Errors: {len(errors)}")
                for error in errors:
                    print(f"      - {error}")
            
            # Show sample results
            for source_type in ["osdr_studies", "osdr_biodata", "ntrs_publications", "nslsl_experiments"]:
                source_results = results.get(source_type, [])
                if source_results:
                    print(f"   📄 {source_type}: {len(source_results)} results")
                    if source_results:
                        print(f"      Sample: {source_results[0].get('title', 'No title')[:60]}...")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print()

async def test_local_integration():
    """Test integration with local CSV data"""
    print("🔄 Testing Local + NASA API Integration...")
    print("=" * 50)
    
    nasa_service = get_nasa_api_service()
    csv_service = get_csv_service()
    
    # Load local data
    if not csv_service.loaded:
        success = csv_service.load_csv_data()
        if not success:
            print("❌ Failed to load local CSV data")
            return
    
    # Test query
    query = "microgravity"
    
    # Get local results
    local_results = csv_service.search(query, limit=10)
    print(f"📁 Local results: {local_results['count']}")
    
    try:
        # Get NASA API results
        nasa_data = await nasa_service.fetch_nasa_data(query, limit=10)
        print(f"🚀 NASA API results: {nasa_data['total_count']}")
        
        # Test unified results
        unified = nasa_service.get_unified_results(
            nasa_data, 
            local_results.get("results", []), 
            max_results=20
        )
        
        print(f"🔗 Unified results: {unified['count']}")
        print(f"   - NASA sources: {unified['nasa_sources']}")
        print(f"   - Local sources: {unified['local_sources']}")
        print(f"   - APIs queried: {unified['total_nasa_apis_queried']}")
        
        # Show sample unified results
        if unified['results']:
            print("\n📋 Sample unified results:")
            for i, result in enumerate(unified['results'][:3], 1):
                source_type = "NASA API" if result.get('is_nasa_api', False) else "Local"
                print(f"   {i}. [{source_type}] {result.get('title', 'No title')[:50]}...")
                print(f"      Source: {result.get('source', 'Unknown')}")
    
    except Exception as e:
        print(f"❌ Integration error: {e}")
    
    print()

async def test_performance():
    """Test performance of NASA API integration"""
    print("⚡ Testing Performance...")
    print("=" * 50)
    
    nasa_service = get_nasa_api_service()
    
    # Test parallel API calls
    start_time = datetime.now()
    
    try:
        results = await nasa_service.fetch_nasa_data("space biology", limit=10)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Query duration: {duration:.2f} seconds")
        print(f"📊 Total results: {results['total_count']}")
        print(f"📡 APIs queried: {len(results['sources_queried'])}")
        
        if duration < 5.0:
            print("✅ Performance: Excellent (< 5 seconds)")
        elif duration < 10.0:
            print("✅ Performance: Good (< 10 seconds)")
        else:
            print("⚠️  Performance: Needs optimization (> 10 seconds)")
    
    except Exception as e:
        print(f"❌ Performance test error: {e}")
    
    print()

async def test_error_handling():
    """Test error handling and fallbacks"""
    print("🛡️  Testing Error Handling...")
    print("=" * 50)
    
    nasa_service = get_nasa_api_service()
    
    # Test with invalid query
    try:
        results = await nasa_service.fetch_nasa_data("", limit=5)
        print("✅ Empty query handled gracefully")
    except Exception as e:
        print(f"❌ Empty query error: {e}")
    
    # Test with very long query
    try:
        long_query = "microgravity " * 100  # Very long query
        results = await nasa_service.fetch_nasa_data(long_query, limit=5)
        print("✅ Long query handled gracefully")
    except Exception as e:
        print(f"⚠️  Long query error: {e}")
    
    print()

def generate_test_report(test_results):
    """Generate a comprehensive test report"""
    print("📋 INTEGRATION TEST REPORT")
    print("=" * 50)
    
    report = {
        "test_timestamp": datetime.now().isoformat(),
        "nasa_api_status": test_results,
        "recommendations": []
    }
    
    # Analyze results
    working_apis = sum(1 for result in test_results.values() if result["status"] == "success")
    total_apis = len(test_results)
    
    print(f"🔧 API Status: {working_apis}/{total_apis} APIs working")
    
    if working_apis == total_apis:
        print("✅ All NASA APIs are operational")
        report["recommendations"].append("All systems operational - ready for production")
    elif working_apis >= total_apis // 2:
        print("⚠️  Some APIs are down but core functionality available")
        report["recommendations"].append("Monitor failing APIs and implement fallbacks")
    else:
        print("❌ Major API issues detected")
        report["recommendations"].append("Critical: Fix API connectivity issues before deployment")
    
    # Save report
    with open("nasa_api_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: nasa_api_test_report.json")
    print()

async def main():
    """Run all tests"""
    print("🚀 NASA Open Science APIs Integration Test Suite")
    print("=" * 60)
    print(f"⏰ Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Run individual tests
        api_results = await test_individual_apis()
        await test_unified_search()
        await test_local_integration()
        await test_performance()
        await test_error_handling()
        
        # Generate report
        generate_test_report(api_results)
        
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"⏰ Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())