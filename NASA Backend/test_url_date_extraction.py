#!/usr/bin/env python3
"""
Test script to verify URL date extraction functionality
"""

from app.csv_service import csv_service
import asyncio

async def test_url_date_extraction():
    """Test the URL date extraction functionality"""
    
    # Load CSV data
    print("Loading CSV data...")
    success = csv_service.load_csv_data()
    if not success:
        print("Failed to load CSV data")
        return
    
    print("CSV data loaded successfully")
    
    # Test URLs from the sample data
    test_urls = [
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4136787/",
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3630201/",
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11988870/"
    ]
    
    print("\nTesting URL date extraction:")
    for url in test_urls:
        print(f"\nExtracting date from: {url}")
        date = await csv_service.extract_date_from_url(url)
        print(f"Extracted date: {date}")
    
    # Test search functionality with date extraction
    print("\n" + "="*60)
    print("Testing search with date extraction:")
    
    # Search for articles that should have URLs
    results = csv_service.search('Microgravity', limit=3)
    
    print(f"Found {results['count']} results:")
    
    for i, result in enumerate(results['results']):
        print(f"\n{i+1}. {result['title'][:80]}...")
        print(f"   Date: {result['date']}")
        print(f"   Type: {result['type']}")
        print(f"   Link: {result['link'][:60]}...")

def test_sync_date_extraction():
    """Test synchronous date extraction"""
    
    # Load CSV data
    print("Loading CSV data...")
    success = csv_service.load_csv_data()
    if not success:
        print("Failed to load CSV data")
        return
    
    print("CSV data loaded successfully")
    
    test_url = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4136787/"
    print(f"\nTesting sync extraction from: {test_url}")
    
    date = csv_service.sync_extract_date_from_url(test_url)
    print(f"Extracted date: {date}")

if __name__ == "__main__":
    print("Testing URL Date Extraction Functionality")
    print("="*50)
    
    # Test synchronous extraction first
    test_sync_date_extraction()
    
    # Test async extraction
    print("\n" + "="*50)
    print("Testing Async Date Extraction:")
    asyncio.run(test_url_date_extraction())