#!/usr/bin/env python3
"""
Test script to verify CSV service is loading real article data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.csv_service import CSVDataService

def test_csv_loading():
    print("🧪 Testing CSV Service with Real Data...")
    
    # Create service instance
    csv_service = CSVDataService()
    
    # Test loading
    print("📁 Loading CSV data...")
    success = csv_service.load_csv_data()
    
    if not success:
        print("❌ Failed to load CSV data")
        return
    
    print(f"✅ Successfully loaded CSV data")
    
    # Get stats
    stats = csv_service.get_stats()
    print(f"📊 Statistics:")
    print(f"  - Total articles: {stats['total_articles']}")
    print(f"  - Research papers: {stats.get('research_papers', 'N/A')}")
    print(f"  - OSDR data: {stats.get('osdr_data', 'N/A')}")
    print(f"  - TaskBook projects: {stats.get('taskbook_projects', 'N/A')}")
    print(f"  - Sources: {stats.get('sources', [])}")
    
    # Test search
    print("\n🔍 Testing search functionality...")
    
    # Test with microgravity
    results = csv_service.search("microgravity", limit=3)
    print(f"Search 'microgravity': Found {results['count']} results")
    
    if results['results']:
        first_result = results['results'][0]
        print(f"  First result: {first_result['title'][:80]}...")
        print(f"  Link: {first_result['link']}")
        print(f"  Type: {first_result['type']}")
        print(f"  Tags: {first_result['tags']}")
    
    # Test with space
    results = csv_service.search("space", limit=2)
    print(f"\nSearch 'space': Found {results['count']} results")
    
    # Test with plant
    results = csv_service.search("plant", limit=2)
    print(f"Search 'plant': Found {results['count']} results")

if __name__ == "__main__":
    test_csv_loading()