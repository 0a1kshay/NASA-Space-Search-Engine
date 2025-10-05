"""
Debug script to examine NASA Task Book HTML structure
"""

import requests
from bs4 import BeautifulSoup
import time

def debug_nasa_taskbook():
    """Debug NASA Task Book structure"""
    
    url = 'https://taskbook.nasaprs.com/tbp/index.cfm'
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    try:
        print(f"Fetching: {url}")
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("\n=== FORMS ON PAGE ===")
        forms = soup.find_all('form')
        for i, form in enumerate(forms):
            print(f"\nForm {i+1}:")
            print(f"  Action: {form.get('action', 'None')}")
            print(f"  Method: {form.get('method', 'None')}")
            
            # Look for input fields
            inputs = form.find_all(['input', 'select', 'textarea'])
            for inp in inputs:
                name = inp.get('name', 'unnamed')
                inp_type = inp.get('type', inp.name)
                print(f"    {inp_type}: {name}")
                
                if inp.name == 'select':
                    options = inp.find_all('option')
                    print(f"      Options: {[opt.get('value', opt.get_text()[:20]) for opt in options[:5]]}")
        
        print("\n=== SAMPLE LINKS ===")
        links = soup.find_all('a', href=True)
        for link in links[:15]:
            href = link.get('href')
            text = link.get_text().strip()[:50]
            print(f"  {text} -> {href}")
        
        print("\n=== SEARCH FOR PROJECT PATTERNS ===")
        page_text = soup.get_text()
        
        # Look for common patterns
        patterns = [
            'TASKID',
            'project',
            'investigation',
            'research',
            'Task Book'
        ]
        
        for pattern in patterns:
            count = page_text.lower().count(pattern.lower())
            print(f"  '{pattern}': found {count} times")
        
        # Look for any forms with search functionality
        print("\n=== FORM DETAILS ===")
        for form in forms:
            print(f"\nForm action: {form.get('action')}")
            print("Form HTML snippet:")
            print(str(form)[:500] + "..." if len(str(form)) > 500 else str(form))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_nasa_taskbook()