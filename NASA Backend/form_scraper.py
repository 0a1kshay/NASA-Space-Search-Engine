"""
Functional NASA Task Book scraper using the search form
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import logging
from typing import List, Dict, Optional
import csv
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NASATaskBookFormScraper:
    """Scraper that uses the NASA Task Book search form to find projects"""
    
    def __init__(self):
        self.base_url = 'https://taskbook.nasaprs.com'
        self.search_url = 'https://taskbook.nasaprs.com/tbp/index.cfm'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.projects_data = []
        self.delay = 1.5
        
    def get_search_form_data(self) -> Dict:
        """Get the search form and extract form data"""
        try:
            response = self.session.get(self.search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            form = soup.find('form', {'name': 'list'})
            
            if not form:
                logger.error("Could not find search form")
                return {}
            
            # Build form data dictionary
            form_data = {}
            
            # Get all input fields
            inputs = form.find_all(['input', 'select'])
            for inp in inputs:
                name = inp.get('name')
                if not name:
                    continue
                    
                if inp.name == 'input':
                    inp_type = inp.get('type', 'text')
                    if inp_type == 'hidden':
                        form_data[name] = inp.get('value', '')
                    elif inp_type in ['text', 'email']:
                        form_data[name] = ''  # Will be filled by search parameters
                    elif inp_type == 'checkbox':
                        # Don't add checkboxes to form data unless we want to check them
                        pass
                elif inp.name == 'select':
                    # For select elements, we might want to use specific values
                    pass
            
            return form_data
            
        except Exception as e:
            logger.error(f"Error getting form data: {e}")
            return {}
    
    def search_projects_by_year(self, year: str) -> List[str]:
        """Search for projects in a specific year using the form"""
        logger.info(f"Searching for projects in {year}")
        
        # Get base form data
        form_data = self.get_search_form_data()
        if not form_data:
            return []
        
        # Set search parameters
        form_data.update({
            'StartSearch': 'Start Search',
            'year': year,  # Set the fiscal year
            'division': ['Human Research', 'Space Biology', 'Physical Sciences'],  # All divisions
            'action': 'public_query_taskbook_content'
        })
        
        project_urls = []
        
        try:
            logger.info(f"Submitting search form for {year}")
            response = self.session.post(self.search_url, data=form_data, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for project links in the results
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                if 'TASKID=' in href or 'taskbook_content' in href:
                    # Convert relative to absolute URL
                    if href.startswith('?'):
                        full_url = f"{self.search_url}{href}"
                    elif href.startswith('/'):
                        full_url = f"{self.base_url}{href}"
                    elif href.startswith('index.cfm'):
                        full_url = f"{self.base_url}/tbp/{href}"
                    elif not href.startswith('http'):
                        full_url = f"{self.base_url}/tbp/{href}"
                    else:
                        full_url = href
                    
                    project_urls.append(full_url)
            
            logger.info(f"Found {len(project_urls)} projects for {year}")
            
        except Exception as e:
            logger.error(f"Error searching for {year}: {e}")
        
        time.sleep(self.delay)
        return list(set(project_urls))  # Remove duplicates
    
    def extract_project_data(self, project_url: str) -> Optional[Dict]:
        """Extract data from a project page"""
        try:
            response = self.session.get(project_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            
            # Extract project data
            project_data = {
                'url': project_url,
                'title': self.extract_title(soup),
                'principal_investigator': self.extract_field(text, ['Principal Investigator', 'PI']),
                'organization': self.extract_field(text, ['Organization', 'Institution', 'Affiliation']),
                'fiscal_year': self.extract_field(text, ['Fiscal Year', 'FY']),
                'abstract': self.extract_abstract(soup),
                'research_area': self.extract_field(text, ['Research Area', 'Division', 'Program']),
                'keywords': self.extract_field(text, ['Keywords', 'Key Words']),
                'project_id': self.extract_project_id(project_url),
                'scraped_date': pd.Timestamp.now().isoformat()
            }
            
            # Validate we got meaningful data
            if not project_data['title'] or len(project_data['title'].strip()) < 5:
                logger.warning(f"Insufficient data from {project_url}")
                return None
            
            return project_data
            
        except Exception as e:
            logger.error(f"Error extracting data from {project_url}: {e}")
            return None
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract project title"""
        # Try multiple approaches
        title_selectors = ['h1', 'h2', '.title', 'title']
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title and len(title) > 5 and 'NASA Task Book' not in title:
                    return self.clean_text(title)
        
        return "Unknown Title"
    
    def extract_field(self, text: str, field_names: List[str]) -> str:
        """Extract a field value using various patterns"""
        for field_name in field_names:
            patterns = [
                rf'{field_name}[:\s]+([^\n\r]+)',
                rf'{field_name}[:\s]*([^\n\r]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return self.clean_text(match.group(1))
        
        return "Not specified"
    
    def extract_abstract(self, soup: BeautifulSoup) -> str:
        """Extract project abstract"""
        # Look for abstract-like content
        abstract_indicators = ['.abstract', '.summary', '.description', 'p']
        
        for indicator in abstract_indicators:
            elements = soup.select(indicator)
            for element in elements:
                text = element.get_text().strip()
                if len(text) > 100:  # Likely an abstract
                    return self.clean_text(text)
        
        return "No abstract available"
    
    def extract_project_id(self, url: str) -> str:
        """Extract project ID from URL"""
        match = re.search(r'TASKID=(\w+)', url)
        if match:
            return match.group(1)
        
        # Generate ID from URL hash
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:8]
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        
        return text
    
    def scrape_recent_years(self, num_years: int = 3):
        """Scrape projects from the most recent years"""
        logger.info(f"Starting NASA Task Book scraping for last {num_years} years")
        
        # Get recent years
        current_year = pd.Timestamp.now().year
        years = [str(year) for year in range(current_year - num_years + 1, current_year + 1)]
        
        total_projects = 0
        
        for year in years:
            logger.info(f"Processing year {year}")
            
            # Search for projects in this year
            project_urls = self.search_projects_by_year(year)
            
            if not project_urls:
                logger.warning(f"No projects found for {year}")
                continue
            
            # Limit projects per year for testing
            project_urls = project_urls[:10]  # Limit to 10 projects per year
            
            # Extract data from each project
            for i, project_url in enumerate(project_urls):
                logger.info(f"  Processing project {i+1}/{len(project_urls)}: {project_url}")
                
                project_data = self.extract_project_data(project_url)
                if project_data:
                    self.projects_data.append(project_data)
                    total_projects += 1
                
                time.sleep(self.delay)
        
        logger.info(f"Scraping completed! Total projects: {total_projects}")
        
        # Save data
        if self.projects_data:
            self.save_to_csv()
        else:
            logger.warning("No projects were scraped")
    
    def save_to_csv(self, output_file: str = 'data/taskbook_projects.csv'):
        """Save scraped data to CSV"""
        logger.info(f"Saving {len(self.projects_data)} projects to {output_file}")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Create DataFrame
        df = pd.DataFrame(self.projects_data)
        
        # Define column order
        columns = [
            'project_id', 'title', 'principal_investigator', 'organization',
            'fiscal_year', 'abstract', 'research_area', 'keywords', 'url', 'scraped_date'
        ]
        
        # Ensure all columns exist
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        
        # Reorder columns
        df = df[columns]
        
        # Save to CSV
        df.to_csv(output_file, index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)
        
        logger.info(f"Successfully saved {len(df)} projects to {output_file}")
        
        # Log summary
        logger.info(f"Sample data:")
        for i, row in df.head(3).iterrows():
            logger.info(f"  {i+1}. {row['title'][:50]}...")

def main():
    """Main entry point"""
    print("NASA Task Book Form-Based Scraper")
    print("=" * 40)
    
    scraper = NASATaskBookFormScraper()
    
    try:
        # Scrape recent years (limited for testing)
        scraper.scrape_recent_years(num_years=2)
        
        print(f"\nScraping completed!")
        print(f"Found {len(scraper.projects_data)} projects")
        print("Data saved to: data/taskbook_projects.csv")
        
    except Exception as e:
        print(f"Scraping failed: {e}")
        logger.error(f"Fatal error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())