#!/usr/bin/env python3
"""
Simple test to manually extract date from one URL
"""

import asyncio
import aiohttp
import re

async def simple_test():
    url = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4136787/"
    
    print(f"Testing URL: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get(url) as response:
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    html = await response.text()
                    print(f"HTML length: {len(html)}")
                    
                    # Look for years in the content
                    year_matches = re.findall(r'\b(20\d{2})\b', html)
                    print(f"Found years: {set(year_matches)}")
                    
                    # Look for specific publication patterns
                    patterns = [
                        r'Published[:\s]*(\d{4})',
                        r'Publication date[:\s]*(\d{4})',
                        r'(\d{4})\s*[;,]\s*\d+',
                        r'epub\s+(\d{4})',
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, html, re.IGNORECASE)
                        if matches:
                            print(f"Pattern '{pattern}' found: {matches}")
                    
                    # Check title for clues
                    title_match = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
                    if title_match:
                        print(f"Title: {title_match.group(1)}")
                        
                else:
                    print(f"Failed to fetch page: {response.status}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(simple_test())