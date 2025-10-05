#!/usr/bin/env python3
"""
Test the full search functionality with date extraction
"""

from app.csv_service import csv_service

def test_full_search():
    # Load CSV data
    print("Loading CSV data...")
    success = csv_service.load_csv_data()
    if not success:
        print("Failed to load CSV data")
        return
    
    print("CSV data loaded successfully")
    
    # Test search queries
    test_queries = [
        "microgravity",
        "space",
        "Tempus ALS",
        "bone"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Searching for: '{query}'")
        print('='*60)
        
        results = csv_service.search(query, limit=5)
        print(f"Found {results['count']} results:")
        
        for i, result in enumerate(results['results']):
            print(f"\n{i+1}. {result['title'][:70]}...")
            print(f"   📅 Date: {result['date']}")
            print(f"   📋 Type: {result['type']}")
            print(f"   👥 Authors: {result['authors'][0][:50]}...")
            print(f"   🏷️  Tags: {', '.join(result['tags'][:3])}")
            if result['link']:
                print(f"   🔗 Link: {result['link'][:60]}...")

if __name__ == "__main__":
    test_full_search()