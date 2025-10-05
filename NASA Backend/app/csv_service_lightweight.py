"""
Lightweight CSV Data Service for NASA Space Biology Search Engine
No pandas dependency - uses pure Python for Vercel compatibility
"""

import csv
import os
import re
import asyncio
import aiohttp
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime
from urllib.parse import urlparse
import json

logger = logging.getLogger(__name__)

class CSVDataService:
    """Lightweight service to load and search CSV data without pandas"""
    
    def __init__(self):
        self.data = []
        self.csv_path = None
        self.loaded = False
        self.date_cache = {}
        
    def load_csv_data(self, csv_path: str = None) -> bool:
        """Load CSV data from multiple files using pure Python"""
        all_data = []
        files_loaded = []
        
        data_files = [
            {
                'path': "NASA Backend/data/sample_600_articles.csv",
                'alt_paths': ["data/sample_600_articles.csv", "../data/sample_600_articles.csv", 
                            "sample_600_articles.csv"],
                'source': 'NASA Articles',
                'required_columns': ['Title', 'Link', 'Description']
            },
            {
                'path': "NASA Backend/data/taskbook_projects.csv", 
                'alt_paths': ["data/taskbook_projects.csv", "../data/taskbook_projects.csv",
                            "taskbook_projects.csv"],
                'source': 'Task Book Projects',
                'required_columns': ['title', 'principal_investigator', 'abstract', 'url']
            }
        ]
        
        # If specific CSV path provided, load only that file
        if csv_path and os.path.exists(csv_path):
            try:
                data = self._load_single_file_path(csv_path)
                if data:
                    self.data = data
                    self.csv_path = csv_path
                    self.loaded = True
                    logger.info(f"Successfully loaded single CSV: {csv_path}")
                    return True
            except Exception as e:
                logger.error(f"Error loading {csv_path}: {e}")
                return False
        
        # Load all available data files
        for data_file in data_files:
            data = self._load_single_file(data_file)
            if data:
                all_data.extend(data)
                files_loaded.append(data_file['source'])
        
        if not all_data:
            logger.error("No CSV files could be loaded")
            return False
            
        try:
            self.data = all_data
            self.csv_path = f"Multiple files: {', '.join(files_loaded)}"
            self.loaded = True
            
            logger.info(f"Successfully loaded {len(files_loaded)} CSV files:")
            for source in files_loaded:
                logger.info(f"  - {source}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error combining CSV data: {e}")
            return False
    
    def _load_single_file_path(self, file_path: str) -> List[Dict[str, Any]]:
        """Load a single CSV file by path"""
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Clean up row data
                    cleaned_row = {k: v.strip() if v else '' for k, v in row.items()}
                    data.append(cleaned_row)
            
            logger.info(f"Successfully loaded {len(data)} rows from {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return []
    
    def _load_single_file(self, data_file: Dict) -> Optional[List[Dict[str, Any]]]:
        """Load a single CSV file with standardization"""
        file_path = None
        
        # Find the file
        for path in [data_file['path']] + data_file['alt_paths']:
            if os.path.exists(path):
                file_path = path
                break
        
        if not file_path:
            logger.warning(f"File not found for {data_file['source']}: tried {data_file['path']}")
            return None
            
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Clean up row data
                    cleaned_row = {k: v.strip() if v else '' for k, v in row.items()}
                    # Standardize columns
                    standardized_row = self._standardize_row(cleaned_row, data_file['source'])
                    data.append(standardized_row)
            
            logger.info(f"Successfully loaded {len(data)} rows from {data_file['source']}: {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading {data_file['source']} from {file_path}: {e}")
            return None
    
    def _standardize_row(self, row: Dict[str, str], source: str) -> Dict[str, str]:
        """Standardize row data for different sources"""
        standardized = dict(row)
        standardized['source'] = source
        
        if source == 'NASA Articles':
            # Ensure required fields exist
            if 'Description' not in standardized:
                standardized['Description'] = standardized.get('Title', '')
            if 'Link' not in standardized:
                standardized['Link'] = ''
                
        elif source == 'Task Book Projects':
            # Map Task Book columns to standard format
            column_mapping = {
                'title': 'Title',
                'abstract': 'Description', 
                'url': 'Link',
                'principal_investigator': 'Author',
                'fiscal_year': 'Date',
                'research_area': 'Category',
                'keywords': 'Tags'
            }
            
            # Create new standardized row
            new_row = {}
            for old_key, new_key in column_mapping.items():
                if old_key in standardized:
                    new_row[new_key] = standardized[old_key]
            
            # Keep other fields
            for key, value in standardized.items():
                if key not in column_mapping:
                    new_row[key] = value
            
            standardized = new_row
            
            # Ensure required fields exist
            for field in ['Title', 'Description', 'Link']:
                if field not in standardized:
                    standardized[field] = ''
            
            # Combine additional info into description
            author = standardized.get('Author', '')
            category = standardized.get('Category', '')
            description = standardized.get('Description', '')
            
            if author or category:
                parts = []
                if author:
                    parts.append(f"PI: {author}")
                if category:
                    parts.append(category)
                if description:
                    parts.append(description)
                standardized['Description'] = " | ".join(parts)
        
        return standardized
    
    async def extract_date_from_url(self, url: str) -> str:
        """Extract publication date from URL metadata"""
        if not url or url in self.date_cache:
            return self.date_cache.get(url, "N/A")
        
        try:
            if "ncbi.nlm.nih.gov/pmc/articles" in url:
                date = await self._extract_ncbi_date(url)
            elif "taskbook.nasaprs.com" in url:
                date = await self._extract_taskbook_date(url)
            else:
                date = await self._extract_generic_date(url)
            
            self.date_cache[url] = date
            return date
            
        except Exception as e:
            logger.warning(f"Error extracting date from {url}: {e}")
            self.date_cache[url] = "N/A"
            return "N/A"
    
    async def _extract_ncbi_date(self, url: str) -> str:
        """Extract date from NCBI PMC articles"""
        try:
            pmc_match = re.search(r'PMC(\d+)', url)
            if not pmc_match:
                return "N/A"
            
            pmc_id = pmc_match.group(1)
            api_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pmc&id={pmc_id}&retmode=json"
            
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'result' in data and pmc_id in data['result']:
                            article_data = data['result'][pmc_id]
                            
                            date_fields = ['pubdate', 'epubdate', 'printpubdate', 'history']
                            
                            for field in date_fields:
                                if field in article_data and article_data[field]:
                                    date_str = str(article_data[field])
                                    year_match = re.search(r'(20\d{2})', date_str)
                                    if year_match:
                                        year = int(year_match.group(1))
                                        if 2000 <= year <= 2024:
                                            return str(year)
            
            # Fallback: estimate based on PMC ID
            pmc_num = int(pmc_id)
            
            if pmc_num >= 10000000:
                return "2023"
            elif pmc_num >= 8000000:
                return "2021"
            elif pmc_num >= 6000000:
                return "2019"
            elif pmc_num >= 4000000:
                return "2016"
            elif pmc_num >= 2000000:
                return "2012"
            elif pmc_num >= 1000000:
                return "2008"
            else:
                return "2005"
                        
        except Exception as e:
            logger.warning(f"Error extracting NCBI date from {url}: {e}")
        
        return "N/A"
    
    async def _extract_taskbook_date(self, url: str) -> str:
        """Extract date from NASA Task Book URLs"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        fy_patterns = [
                            r'FY\s*(\d{4})',
                            r'Fiscal Year[:\s]*(\d{4})',
                            r'FY(\d{4})',
                            r'(\d{4})\s*fiscal\s*year'
                        ]
                        
                        for pattern in fy_patterns:
                            match = re.search(pattern, html, re.IGNORECASE)
                            if match:
                                return match.group(1)
                                
        except Exception as e:
            logger.warning(f"Error extracting Task Book date: {e}")
        
        return "N/A"
    
    async def _extract_generic_date(self, url: str) -> str:
        """Extract date from generic URLs"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        meta_patterns = [
                            r'<meta[^>]*name="publication_date"[^>]*content="([^"]*)"',
                            r'<meta[^>]*property="article:published_time"[^>]*content="([^"]*)"',
                            r'<meta[^>]*name="date"[^>]*content="([^"]*)"',
                        ]
                        
                        for pattern in meta_patterns:
                            match = re.search(pattern, html, re.IGNORECASE)
                            if match:
                                date_str = match.group(1)
                                year_match = re.search(r'\d{4}', date_str)
                                if year_match:
                                    return year_match.group(0)
                        
                        year_matches = re.findall(r'\b(20\d{2})\b', html)
                        if year_matches:
                            years = [int(y) for y in year_matches if 2000 <= int(y) <= 2024]
                            if years:
                                return str(min(years))
                                
        except Exception as e:
            logger.warning(f"Error extracting generic date: {e}")
        
        return "N/A"
    
    def sync_extract_date_from_url(self, url: str) -> str:
        """Synchronous wrapper for date extraction"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return self.date_cache.get(url, "N/A")
            else:
                return loop.run_until_complete(self.extract_date_from_url(url))
        except RuntimeError:
            return asyncio.run(self.extract_date_from_url(url))
        except Exception as e:
            logger.warning(f"Error in sync date extraction: {e}")
            return "N/A"
    
    def search(self, query: str, limit: int = 10) -> Dict:
        """Search for articles matching the query"""
        if not self.loaded:
            logger.warning("CSV data not loaded, attempting to load...")
            if not self.load_csv_data():
                return {"count": 0, "results": []}
        
        if not query or query.strip() == '':
            return {"count": 0, "results": []}
        
        try:
            query_lower = query.lower().strip()
            results = []
            
            for row in self.data:
                # Search in title, description, and link
                title = row.get('Title', '').lower()
                description = row.get('Description', '').lower()
                link = row.get('Link', '').lower()
                
                if (query_lower in title or 
                    query_lower in description or 
                    query_lower in link):
                    
                    # Convert to normalized format
                    title_original = row.get('Title', '')
                    link_original = row.get('Link', '')
                    
                    # Get publication date
                    publication_date = "N/A"
                    if 'Date' in row and row['Date'] and str(row['Date']).strip():
                        date_value = str(row['Date']).strip()
                        if date_value.startswith('FY '):
                            publication_date = date_value.replace('FY ', '')
                        else:
                            publication_date = date_value
                    elif link_original and link_original.strip():
                        publication_date = self.sync_extract_date_from_url(link_original.strip())
                    
                    # Get source information
                    source_info = row.get('source', 'NASA Research')
                    
                    # Create abstract
                    abstract = row.get('Description', f"NASA research article: {title_original}")
                    if not abstract or abstract == title_original:
                        abstract = f"NASA research article: {title_original}"
                        if "microgravity" in title_original.lower():
                            abstract += " - Study focuses on microgravity effects and space biology research."
                        elif "space" in title_original.lower():
                            abstract += " - Research conducted in space environment conditions."
                        else:
                            abstract += " - Important findings for space exploration and astronaut health."
                    
                    # Determine research type
                    research_type = "Research Papers"
                    if source_info == "Task Book Projects":
                        research_type = "Task Book Grants"
                    elif "OSDR" in title_original or "data" in title_original.lower():
                        research_type = "OSDR Data"
                    elif "task" in title_original.lower() or "project" in title_original.lower():
                        research_type = "Task Book Grants"
                    
                    # Get authors
                    authors = ["NASA Space Biology Database"]
                    if 'Author' in row and row['Author'] and str(row['Author']).strip():
                        author_info = str(row['Author']).strip()
                        if author_info and author_info != 'nan':
                            authors = [author_info]
                    
                    # Generate tags
                    tags = ["Space Biology"]
                    title_lower = title_original.lower()
                    
                    if 'Category' in row and row['Category']:
                        category = str(row['Category']).strip()
                        if category and category != 'nan':
                            tags.append(category)
                    
                    if "microgravity" in title_lower:
                        tags.append("Microgravity")
                    if "plant" in title_lower or "arabidopsis" in title_lower:
                        tags.append("Plant Biology")
                    if "bone" in title_lower or "skeletal" in title_lower:
                        tags.append("Bone Research")
                    if "cell" in title_lower:
                        tags.append("Cell Biology")
                    if "radiation" in title_lower:
                        tags.append("Space Radiation")
                    if "muscle" in title_lower:
                        tags.append("Muscle Research")
                    if "iss" in title_lower:
                        tags.append("ISS Research")
                    if "technology" in title_lower:
                        tags.append("Technology Development")
                    
                    if 'Tags' in row and row['Tags'] and str(row['Tags']).strip():
                        csv_tags = str(row['Tags']).strip()
                        if csv_tags and csv_tags != 'nan' and csv_tags != 'Not specified':
                            tags.extend([tag.strip() for tag in csv_tags.split(',') if tag.strip()])
                    
                    results.append({
                        "title": title_original,
                        "abstract": abstract,
                        "link": link_original,
                        "type": research_type,
                        "authors": authors,
                        "date": publication_date,
                        "tags": list(set(tags))
                    })
                    
                    if len(results) >= limit:
                        break
            
            logger.info(f"Search for '{query}' returned {len(results)} results")
            
            return {
                "count": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error searching data: {e}")
            return {"count": 0, "results": []}
    
    def get_stats(self) -> Dict:
        """Get statistics about the loaded data"""
        if not self.loaded:
            return {"loaded": False, "total_articles": 0}
        
        # Count articles by type
        research_papers = 0
        osdr_data = 0
        taskbook_projects = 0
        
        for row in self.data:
            title = str(row.get("Title", "")).lower()
            if "osdr" in title or "data" in title:
                osdr_data += 1
            elif "task" in title or "project" in title:
                taskbook_projects += 1
            else:
                research_papers += 1
        
        # Get unique columns
        columns = set()
        for row in self.data:
            columns.update(row.keys())
        
        return {
            "loaded": True,
            "total_articles": len(self.data),
            "research_papers": research_papers,
            "osdr_data": osdr_data,
            "taskbook_projects": taskbook_projects,
            "sources": ["NASA Articles CSV"],
            "columns": list(columns),
            "csv_path": self.csv_path
        }

# Global instance
csv_service = CSVDataService()

def get_csv_service() -> CSVDataService:
    """Dependency injection for FastAPI"""
    return csv_service