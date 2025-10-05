"""
Simple test script to find a few NASA Task Book projects
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_nasa_taskbook():
    """Test NASA Task Book access and find some sample projects"""
    
    # Base URLs to test
    test_urls = [
        'https://taskbook.nasaprs.com/tbp/index.cfm',
        'https://taskbook.nasaprs.com/tbp/index.cfm?action=public_query_taskbook_content',
        'https://taskbook.nasaprs.com/tbp/maps_metrics.cfm',
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    project_urls = []
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for project-related links
            links = soup.find_all('a', href=True)
            print(f"Found {len(links)} links on page")
            
            for link in links[:20]:  # Check first 20 links
                href = link.get('href', '')
                text = link.get_text().strip()
                
                # Look for task book project patterns
                if 'TASKID=' in href or 'taskbook_content' in href:
                    full_url = urljoin(url, href)
                    project_urls.append(full_url)
                    print(f"Found project: {text[:50]}... -> {full_url}")
                    
        except Exception as e:
            print(f"Error accessing {url}: {e}")
        
        time.sleep(1)  # Be polite
    
    print(f"\nTotal project URLs found: {len(project_urls)}")
    
    # Test accessing one project
    if project_urls:
        test_project = project_urls[0]
        print(f"\nTesting project access: {test_project}")
        
        try:
            response = session.get(test_project, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract some basic info
            title = soup.find('title')
            if title:
                print(f"Page title: {title.get_text().strip()}")
            
            # Look for common project fields
            text = soup.get_text()
            
            # Look for patterns
            patterns = {
                'Principal Investigator': r'Principal\s+Investigator[:\s]+([^\n\r]+)',
                'Fiscal Year': r'Fiscal\s+Year[:\s]+([^\n\r]+)',
                'Abstract': r'Abstract[:\s]+([^\n\r]{50,200})',
            }
            
            for field, pattern in patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    print(f"{field}: {match.group(1).strip()}")
                    
        except Exception as e:
            print(f"Error accessing project: {e}")
    
    return project_urls

if __name__ == "__main__":
    print("Testing NASA Task Book access...")
    project_urls = test_nasa_taskbook()
    
    print(f"\nFound {len(project_urls)} project URLs")
    for i, url in enumerate(project_urls[:5], 1):
        print(f"{i}. {url}")