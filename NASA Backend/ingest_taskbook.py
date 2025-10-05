#!/usr/bin/env python3
"""
NASA Task Book Data Ingestion Script
Web scrapes all NASA Task Book project data from https://taskbook.nasaprs.com/

This script crawls all NASA Task Book project pages from FY2004 to present,
extracts comprehensive project information, and saves it as CSV for search indexing.

Author: NASA Space Biology Knowledge Engine
Date: October 2025
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
import re
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import csv
from datetime import datetime
import os
from typing import List, Dict, Optional
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/taskbook_ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NASATaskBookScraper:
    """
    NASA Task Book project data scraper
    """
    
    def __init__(self):
        self.base_url = "https://taskbook.nasaprs.com"
        self.welcome_url = "https://taskbook.nasaprs.com/tbp/welcome.cfm"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NASAResearchBot/1.0 (NASA Space Biology Knowledge Engine; contact: research@nasa.gov)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        self.projects_data = []
        self.delay_between_requests = 1.5  # Polite scraping delay
        
    def check_robots_txt(self) -> bool:
        """Check if scraping is allowed according to robots.txt"""
        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            # Check if our user agent can fetch the welcome page
            can_fetch = rp.can_fetch('NASAResearchBot', self.welcome_url)
            logger.info(f"Robots.txt check: {'✅ Allowed' if can_fetch else '❌ Disallowed'}")
            return can_fetch
            
        except Exception as e:
            logger.warning(f"Could not check robots.txt: {e}")
            return True  # Proceed with caution if robots.txt is unavailable
    
    def get_page_with_retry(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """Fetch a page with retry logic and error handling"""
        for attempt in range(max_retries):
            try:
                logger.debug(f"Fetching: {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Check if we got a valid HTML response
                if 'text/html' in response.headers.get('content-type', ''):
                    soup = BeautifulSoup(response.content, 'html.parser')
                    time.sleep(self.delay_between_requests)  # Polite delay
                    return soup
                else:
                    logger.warning(f"Non-HTML response from {url}")
                    return None
                    
            except requests.RequestException as e:
                logger.warning(f"Request failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                    return None
        
        return None
    
    def discover_fiscal_years(self) -> List[str]:
        """Discover all available fiscal years from the main page"""
        logger.info("🔍 Discovering available fiscal years...")
        
        soup = self.get_page_with_retry(self.welcome_url)
        if not soup:
            logger.error("Failed to fetch welcome page")
            return []
        
        fiscal_years = []
        
        # Look for fiscal year links - these might be in dropdowns, links, or forms
        # Common patterns: FY2024, FY 2024, Fiscal Year 2024, etc.
        fy_patterns = [
            r'FY\s*(\d{4})',
            r'Fiscal\s+Year\s+(\d{4})',
            r'(\d{4})\s*Fiscal',
            r'Year\s+(\d{4})'
        ]
        
        # Check all links and text for fiscal year references
        all_text = soup.get_text()
        links = soup.find_all('a', href=True)
        
        for pattern in fy_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                year = int(match)
                if 2004 <= year <= datetime.now().year + 1:  # Reasonable range
                    fiscal_years.append(f"FY{year}")
        
        # Check form options and select elements
        selects = soup.find_all('select')
        for select in selects:
            options = select.find_all('option')
            for option in options:
                text = option.get_text().strip()
                for pattern in fy_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        year = int(match.group(1))
                        if 2004 <= year <= datetime.now().year + 1:
                            fiscal_years.append(f"FY{year}")
        
        # Remove duplicates and sort
        fiscal_years = sorted(list(set(fiscal_years)))
        
        # If no fiscal years found, create a reasonable range
        if not fiscal_years:
            current_year = datetime.now().year
            fiscal_years = [f"FY{year}" for year in range(2004, current_year + 1)]
            logger.warning("No fiscal years found on page, using default range 2004-present")
        
        logger.info(f"📅 Found fiscal years: {fiscal_years[:5]}...{fiscal_years[-5:] if len(fiscal_years) > 10 else ''}")
        return fiscal_years
    
    def discover_project_urls(self, fiscal_year: str) -> List[str]:
        """Discover all project URLs for a given fiscal year using search forms"""
        logger.info(f"🔍 Discovering projects for {fiscal_year}...")
        
        project_urls = []
        year_number = fiscal_year.replace('FY', '')
        
        # Since NASA Task Book uses form-based search, let's try some sample searches
        # We'll search for projects using different approaches
        
        search_patterns = [
            # Try searching with fiscal year parameters
            f"{self.base_url}/tbp/index.cfm?action=public_query_taskbook_content&fiscal_year={year_number}",
            f"{self.base_url}/tbp/index.cfm?action=bib_search&fy={year_number}",
            
            # Try some common project listing patterns
            f"{self.base_url}/tbp/browse.cfm?year={year_number}",
            f"{self.base_url}/tbp/list.cfm?fy={year_number}",
        ]
        
        for search_url in search_patterns:
            logger.debug(f"Trying search URL: {search_url}")
            soup = self.get_page_with_retry(search_url)
            
            if soup:
                # Look for project links in search results
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href', '')
                    
                    # Convert relative URLs to absolute
                    if href.startswith('?'):
                        full_url = f"{self.base_url}/tbp/index.cfm{href}"
                    elif href.startswith('/'):
                        full_url = f"{self.base_url}{href}"
                    elif not href.startswith('http'):
                        full_url = f"{self.base_url}/tbp/{href}"
                    else:
                        full_url = href
                    
                    # Check if this looks like a project URL
                    if self.is_project_url(full_url):
                        project_urls.append(full_url)
                        logger.debug(f"Found project: {full_url}")
        
        # If no projects found through searches, let's try to find some sample projects
        # by looking at the main search page for any existing project links
        if not project_urls:
            logger.info("No projects found with direct search, looking for sample projects...")
            main_search = f"{self.base_url}/tbp/index.cfm"
            soup = self.get_page_with_retry(main_search)
            
            if soup:
                # Look for any project URLs that might be examples or recent projects
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link.get('href', '')
                    if 'TASKID=' in href or 'taskbook_content' in href:
                        if href.startswith('?'):
                            full_url = f"{self.base_url}/tbp/index.cfm{href}"
                        else:
                            full_url = href
                        project_urls.append(full_url)
        
        # Remove duplicates
        project_urls = list(set(project_urls))
        
        # Limit to a reasonable number for testing
        if len(project_urls) > 50:
            project_urls = project_urls[:50]
            logger.info(f"Limited to first 50 projects for {fiscal_year}")
        
        logger.info(f"📋 Found {len(project_urls)} projects for {fiscal_year}")
        return project_urls
    
    def is_project_url(self, url: str) -> bool:
        """Check if a URL looks like a NASA Task Book project detail page"""
        project_indicators = [
            # NASA Task Book specific patterns
            'TASKID=',
            'taskbook_content',
            'public_query_taskbook_content',
            'action=public_query_taskbook_content',
            
            # General project patterns
            'project.cfm',
            'detail.cfm',
            'view.cfm',
            '/project/',
            'id=',
            'projectid=',
            'pid='
        ]
        
        # Must be from the NASA Task Book domain
        if 'taskbook.nasaprs.com' not in url.lower():
            return False
            
        return any(indicator in url.lower() for indicator in project_indicators)
    
    def extract_project_data(self, project_url: str) -> Optional[Dict]:
        """Extract project data from a project detail page"""
        soup = self.get_page_with_retry(project_url)
        if not soup:
            return None
        
        logger.debug(f"Extracting data from: {project_url}")
        
        project_data = {
            'url': project_url,
            'title': self.extract_title(soup),
            'principal_investigator': self.extract_pi(soup),
            'organization': self.extract_organization(soup),
            'fiscal_year': self.extract_fiscal_year(soup),
            'abstract': self.extract_abstract(soup),
            'research_area': self.extract_research_area(soup),
            'publications': self.extract_publications(soup),
            'responsible_center': self.extract_responsible_center(soup),
            'keywords': self.extract_keywords(soup),
            'funding_amount': self.extract_funding(soup),
            'project_id': self.extract_project_id(soup, project_url),
            'scraped_date': datetime.now().isoformat()
        }
        
        # Validate that we got meaningful data
        if not project_data['title'] or len(project_data['title'].strip()) < 5:
            logger.warning(f"Insufficient data extracted from {project_url}")
            return None
        
        return project_data
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract project title"""
        selectors = [
            'h1',
            'h2',
            '.title',
            '.project-title',
            '[class*="title"]',
            'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title and len(title) > 5:
                    return self.clean_text(title)
        
        return "Unknown Title"
    
    def extract_pi(self, soup: BeautifulSoup) -> str:
        """Extract Principal Investigator"""
        pi_patterns = [
            r'Principal\s+Investigator[:\s]+([^\n\r]+)',
            r'PI[:\s]+([^\n\r]+)',
            r'Lead\s+Investigator[:\s]+([^\n\r]+)',
            r'Investigator[:\s]+([^\n\r]+)'
        ]
        
        text = soup.get_text()
        for pattern in pi_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.clean_text(match.group(1))
        
        # Look for specific elements
        pi_selectors = [
            '[class*="pi"]',
            '[class*="investigator"]',
            '.contact',
            '.researcher'
        ]
        
        for selector in pi_selectors:
            element = soup.select_one(selector)
            if element:
                pi = element.get_text().strip()
                if pi and len(pi) > 3:
                    return self.clean_text(pi)
        
        return "Unknown PI"
    
    def extract_organization(self, soup: BeautifulSoup) -> str:
        """Extract organization/institution"""
        org_patterns = [
            r'Organization[:\s]+([^\n\r]+)',
            r'Institution[:\s]+([^\n\r]+)',
            r'Affiliation[:\s]+([^\n\r]+)',
            r'University[:\s]+([^\n\r]+)'
        ]
        
        text = soup.get_text()
        for pattern in org_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.clean_text(match.group(1))
        
        return "Unknown Organization"
    
    def extract_fiscal_year(self, soup: BeautifulSoup) -> str:
        """Extract fiscal year"""
        fy_patterns = [
            r'Fiscal\s+Year[:\s]+(\d{4})',
            r'FY[:\s]*(\d{4})',
            r'Year[:\s]+(\d{4})'
        ]
        
        text = soup.get_text()
        for pattern in fy_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"FY{match.group(1)}"
        
        return "Unknown FY"
    
    def extract_abstract(self, soup: BeautifulSoup) -> str:
        """Extract project abstract/description"""
        abstract_selectors = [
            '.abstract',
            '.description',
            '.summary',
            '[class*="abstract"]',
            '[class*="description"]',
            'p'  # Fallback to paragraphs
        ]
        
        for selector in abstract_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                if len(text) > 100:  # Likely an abstract if it's substantial
                    return self.clean_text(text)
        
        return "No abstract available"
    
    def extract_research_area(self, soup: BeautifulSoup) -> str:
        """Extract research area"""
        research_areas = [
            'Space Biology',
            'Human Research',
            'Physical Sciences',
            'Space Technology',
            'Astrophysics',
            'Earth Science'
        ]
        
        text = soup.get_text().lower()
        for area in research_areas:
            if area.lower() in text:
                return area
        
        return "General Research"
    
    def extract_publications(self, soup: BeautifulSoup) -> str:
        """Extract publications or reports"""
        pub_selectors = [
            '.publications',
            '.reports',
            '[class*="publication"]',
            '[class*="report"]',
            'a[href*="publication"]',
            'a[href*="paper"]'
        ]
        
        publications = []
        for selector in pub_selectors:
            elements = soup.select(selector)
            for element in elements:
                pub_text = element.get_text().strip()
                if pub_text and len(pub_text) > 10:
                    publications.append(pub_text)
        
        return "; ".join(publications) if publications else "None listed"
    
    def extract_responsible_center(self, soup: BeautifulSoup) -> str:
        """Extract responsible NASA center"""
        centers = [
            'Ames Research Center',
            'Glenn Research Center',
            'Goddard Space Flight Center',
            'Johnson Space Center',
            'Kennedy Space Center',
            'Langley Research Center',
            'Marshall Space Flight Center',
            'Stennis Space Center'
        ]
        
        text = soup.get_text()
        for center in centers:
            if center.lower() in text.lower():
                return center
        
        return "NASA Headquarters"
    
    def extract_keywords(self, soup: BeautifulSoup) -> str:
        """Extract keywords or tags"""
        keyword_selectors = [
            '.keywords',
            '.tags',
            '[class*="keyword"]',
            '[class*="tag"]'
        ]
        
        keywords = []
        for selector in keyword_selectors:
            elements = soup.select(selector)
            for element in elements:
                keyword_text = element.get_text().strip()
                if keyword_text:
                    keywords.extend([k.strip() for k in keyword_text.split(',')])
        
        return ", ".join(keywords) if keywords else ""
    
    def extract_funding(self, soup: BeautifulSoup) -> str:
        """Extract funding amount if available"""
        funding_patterns = [
            r'\$[\d,]+',
            r'Budget[:\s]+\$?[\d,]+',
            r'Funding[:\s]+\$?[\d,]+'
        ]
        
        text = soup.get_text()
        for pattern in funding_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return ""
    
    def extract_project_id(self, soup: BeautifulSoup, url: str) -> str:
        """Extract project ID from page or URL"""
        # Try to get from URL parameters
        id_patterns = [
            r'id=(\w+)',
            r'projectid=(\w+)',
            r'pid=(\w+)'
        ]
        
        for pattern in id_patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Try to find in page content
        text = soup.get_text()
        id_match = re.search(r'Project\s+ID[:\s]+(\w+)', text, re.IGNORECASE)
        if id_match:
            return id_match.group(1)
        
        # Generate from URL hash
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:8]
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        
        return text
    
    def save_to_csv(self, output_file: str = 'data/taskbook_projects.csv'):
        """Save scraped data to CSV file"""
        if not self.projects_data:
            logger.warning("No project data to save")
            return
        
        logger.info(f"💾 Saving {len(self.projects_data)} projects to {output_file}")
        
        # Define CSV columns
        columns = [
            'project_id',
            'title',
            'principal_investigator',
            'organization',
            'fiscal_year',
            'abstract',
            'research_area',
            'publications',
            'responsible_center',
            'keywords',
            'funding_amount',
            'url',
            'scraped_date'
        ]
        
        try:
            df = pd.DataFrame(self.projects_data)
            
            # Ensure all columns exist
            for col in columns:
                if col not in df.columns:
                    df[col] = ""
            
            # Reorder columns
            df = df[columns]
            
            # Save to CSV with UTF-8 encoding
            df.to_csv(output_file, index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)
            
            logger.info(f"✅ Successfully saved {len(df)} projects to {output_file}")
            
            # Log summary statistics
            self.log_summary_stats(df)
            
        except Exception as e:
            logger.error(f"❌ Failed to save CSV: {e}")
            raise
    
    def log_summary_stats(self, df: pd.DataFrame):
        """Log summary statistics about the scraped data"""
        logger.info("📊 Data Summary:")
        logger.info(f"   Total Projects: {len(df)}")
        logger.info(f"   Fiscal Years: {df['fiscal_year'].nunique()}")
        logger.info(f"   Organizations: {df['organization'].nunique()}")
        logger.info(f"   Research Areas: {df['research_area'].value_counts().to_dict()}")
        
        # Most recent years
        recent_years = df['fiscal_year'].value_counts().head()
        logger.info(f"   Recent Years: {recent_years.index.tolist()}")
    
    def scrape_all_projects(self):
        """Main scraping method - orchestrates the entire process"""
        logger.info("🚀 Starting NASA Task Book scraping...")
        
        # Check robots.txt
        if not self.check_robots_txt():
            logger.warning("⚠️  Robots.txt disallows scraping, but proceeding with caution...")
        
        try:
            # Step 1: Discover fiscal years
            fiscal_years = self.discover_fiscal_years()
            if not fiscal_years:
                logger.error("❌ No fiscal years found, cannot proceed")
                return
            
            # Step 2: For each fiscal year, discover and scrape projects
            total_projects = 0
            for i, fiscal_year in enumerate(fiscal_years):
                logger.info(f"📅 Processing {fiscal_year} ({i+1}/{len(fiscal_years)})")
                
                # Discover project URLs for this fiscal year
                project_urls = self.discover_project_urls(fiscal_year)
                
                if not project_urls:
                    logger.warning(f"No projects found for {fiscal_year}")
                    continue
                
                # Scrape each project
                for j, project_url in enumerate(project_urls):
                    logger.info(f"   📋 Project {j+1}/{len(project_urls)}: {project_url}")
                    
                    project_data = self.extract_project_data(project_url)
                    if project_data:
                        self.projects_data.append(project_data)
                        total_projects += 1
                    
                    # Progress logging
                    if (j + 1) % 10 == 0:
                        logger.info(f"   ✅ Processed {j+1}/{len(project_urls)} projects for {fiscal_year}")
                
                logger.info(f"✅ Completed {fiscal_year}: {len(project_urls)} projects processed")
            
            logger.info(f"🎉 Scraping completed! Total projects: {total_projects}")
            
            # Step 3: Save to CSV
            if self.projects_data:
                self.save_to_csv()
            else:
                logger.warning("❌ No projects were successfully scraped")
                
        except KeyboardInterrupt:
            logger.info("🛑 Scraping interrupted by user")
            if self.projects_data:
                logger.info("💾 Saving partial data...")
                self.save_to_csv()
        except Exception as e:
            logger.error(f"❌ Scraping failed: {e}")
            raise


def main():
    """Main entry point"""
    print("🚀 NASA Task Book Data Ingestion")
    print("=" * 50)
    
    scraper = NASATaskBookScraper()
    
    try:
        scraper.scrape_all_projects()
        print("\n✅ Task Book ingestion completed successfully!")
        print("📁 Data saved to: data/taskbook_projects.csv")
        print("🔄 Restart your FastAPI server to see the new data in search results")
        
    except Exception as e:
        print(f"\n❌ Ingestion failed: {e}")
        logger.error(f"Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())