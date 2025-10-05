"""
CSV Data Service for NASA Space Biology Search Engine
Handles loading and searching CSV data from sample_600_articles.csv
"""

import pandas as pd
import os
import re
import asyncio
import aiohttp
from typing import List, Dict, Optional
import logging
from datetime import datetime
from urllib.parse import urlparse
import json

logger = logging.getLogger(__name__)

class CSVDataService:
    """Service to load and search CSV data"""
    
    def __init__(self):
        self.data = None
        self.csv_path = None
        self.loaded = False
        self.date_cache = {}  # Cache for extracted dates to avoid repeated requests
        
    def load_csv_data(self, csv_path: str = None) -> bool:
        """
        Load CSV data from multiple files
        
        Args:
            csv_path: Primary CSV file path. If None, loads all available data files.
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        all_data = []
        files_loaded = []
        
        # Define all possible data files
        data_files = [
            {
                'path': "data/sample_600_articles.csv",
                'alt_paths': ["../data/sample_600_articles.csv", "sample_600_articles.csv", 
                            r"c:\Users\aksha\Downloads\sample_600_articles.csv"],
                'source': 'NASA Articles',
                'required_columns': ['Title', 'Link', 'Description']
            },
            {
                'path': "data/taskbook_projects.csv",
                'alt_paths': ["../data/taskbook_projects.csv", "taskbook_projects.csv"],
                'source': 'Task Book Projects',
                'required_columns': ['title', 'principal_investigator', 'abstract', 'url']
            }
        ]
        
        # If specific CSV path provided, load only that file
        if csv_path and os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                self.data = df
                self.csv_path = csv_path
                self.loaded = True
                logger.info(f"Successfully loaded single CSV: {csv_path}")
                return True
            except Exception as e:
                logger.error(f"Error loading {csv_path}: {e}")
                return False
        
        # Load all available data files
        for data_file in data_files:
            df = self._load_single_file(data_file)
            if df is not None:
                all_data.append(df)
                files_loaded.append(data_file['source'])
        
        if not all_data:
            logger.error("No CSV files could be loaded")
            return False
            
        try:
            # Combine all dataframes
            self.data = pd.concat(all_data, ignore_index=True, sort=False)
            self.csv_path = f"Multiple files: {', '.join(files_loaded)}"
            self.loaded = True
            
            logger.info(f"Successfully loaded {len(files_loaded)} CSV files:")
            for source in files_loaded:
                logger.info(f"  - {source}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error combining CSV data: {e}")
            return False
    
    def _load_single_file(self, data_file: Dict) -> Optional[pd.DataFrame]:
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
            # Load CSV with pandas
            df = pd.read_csv(file_path)
            
            # Standardize column names based on file type
            df = self._standardize_columns(df, data_file['source'])
            
            # Clean up data
            df = df.fillna('')  # Replace NaN with empty strings
            
            logger.info(f"Successfully loaded {len(df)} rows from {data_file['source']}: {file_path}")
            logger.info(f"Columns: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading {data_file['source']} from {file_path}: {e}")
            return None
    
    def _standardize_columns(self, df: pd.DataFrame, source: str) -> pd.DataFrame:
        """Standardize column names for different data sources"""
        
        # Add source column to track where data came from
        df['source'] = source
        
        if source == 'NASA Articles':
            # Handle CSV with Title, Link columns only
            # Ensure all required columns exist
            if 'Description' not in df.columns:
                # Create description from title for search purposes
                df['Description'] = df['Title']
            if 'Link' not in df.columns:
                df['Link'] = ''
                
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
            
            # Rename columns
            df = df.rename(columns=column_mapping)
            
            # Ensure all required columns exist
            for col in ['Title', 'Description', 'Link']:
                if col not in df.columns:
                    df[col] = ''
            
            # Combine additional info into description
            if 'Author' in df.columns and 'Category' in df.columns:
                df['Description'] = df.apply(lambda row: 
                    f"PI: {row.get('Author', '')} | {row.get('Category', '')} | {row.get('Description', '')}", 
                    axis=1)
        
        return df
    
    async def extract_date_from_url(self, url: str) -> str:
        """Extract publication date from URL metadata"""
        if not url or url in self.date_cache:
            return self.date_cache.get(url, "N/A")
        
        try:
            # Handle different URL types
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
        """Extract date from NCBI PMC articles using API approach"""
        try:
            # Extract PMC ID from URL
            pmc_match = re.search(r'PMC(\d+)', url)
            if not pmc_match:
                return "N/A"
            
            pmc_id = pmc_match.group(1)
            logger.info(f"Extracting date for PMC{pmc_id}")
            
            # Try NCBI E-utilities API to get publication metadata
            api_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pmc&id={pmc_id}&retmode=json"
            
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Parse the API response
                        if 'result' in data and pmc_id in data['result']:
                            article_data = data['result'][pmc_id]
                            
                            # Look for publication date fields
                            date_fields = ['pubdate', 'epubdate', 'printpubdate', 'history']
                            
                            for field in date_fields:
                                if field in article_data and article_data[field]:
                                    date_str = str(article_data[field])
                                    year_match = re.search(r'(20\d{2})', date_str)
                                    if year_match:
                                        year = int(year_match.group(1))
                                        if 2000 <= year <= 2024:
                                            logger.info(f"Found API date {year} for PMC{pmc_id}")
                                            return str(year)
            
            # Fallback: Use estimated publication year based on PMC assignment patterns
            # PMC IDs are generally assigned chronologically
            pmc_num = int(pmc_id)
            
            # Rough estimates based on PMC ID ranges (these are approximate)
            if pmc_num >= 10000000:  # Very high numbers, recent articles
                estimated_year = "2023"
            elif pmc_num >= 8000000:
                estimated_year = "2021"
            elif pmc_num >= 6000000:
                estimated_year = "2019"
            elif pmc_num >= 4000000:
                estimated_year = "2016"
            elif pmc_num >= 2000000:
                estimated_year = "2012"
            elif pmc_num >= 1000000:
                estimated_year = "2008"
            else:
                estimated_year = "2005"
            
            logger.info(f"Using estimated date {estimated_year} for PMC{pmc_id} based on ID range")
            return estimated_year
                        
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
                        
                        # Look for fiscal year patterns
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
                        
                        # Look for meta tags and common date patterns
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
                        
                        # Fallback to any reasonable year
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
            # Try to use existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, we can't use run_until_complete
                # Return cached result if available, otherwise return N/A
                return self.date_cache.get(url, "N/A")
            else:
                return loop.run_until_complete(self.extract_date_from_url(url))
        except RuntimeError:
            # No event loop, create new one
            return asyncio.run(self.extract_date_from_url(url))
        except Exception as e:
            logger.warning(f"Error in sync date extraction: {e}")
            return "N/A"
    
    def search(self, query: str, limit: int = 10) -> Dict:
        """
        Search for articles matching the query
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            Dict with count and normalized results for frontend cards
        """
        if not self.loaded or self.data is None:
            logger.warning("CSV data not loaded, attempting to load...")
            if not self.load_csv_data():
                return {"count": 0, "results": []}
        
        if not query or query.strip() == '':
            # Return empty results for empty query (as requested)
            return {"count": 0, "results": []}
        
        try:
            # Case-insensitive search in Title and Link columns
            query_lower = query.lower().strip()
            
            # Create boolean masks for searching
            title_mask = self.data['Title'].str.lower().str.contains(query_lower, na=False, regex=False)
            
            # Also search in links for domain-specific searches
            link_mask = self.data['Link'].str.lower().str.contains(query_lower, na=False, regex=False)
            
            # If Description column exists, search in it too
            if 'Description' in self.data.columns:
                desc_mask = self.data['Description'].str.lower().str.contains(query_lower, na=False, regex=False)
                combined_mask = title_mask | desc_mask | link_mask
            else:
                combined_mask = title_mask | link_mask
            
            # Filter data
            filtered_data = self.data[combined_mask]
            
            # Limit results
            limited_data = filtered_data.head(limit)
            
            # Convert to normalized format for frontend cards
            results = []
            for _, row in limited_data.iterrows():
                title = row.get("Title", "")
                link = row.get("Link", "")
                
                # Get publication date from the data or extract from URL
                publication_date = "N/A"
                if 'Date' in row and row['Date'] and str(row['Date']).strip() and str(row['Date']).strip() != 'nan':
                    # Handle fiscal year format (e.g., "FY 2025")
                    date_value = str(row['Date']).strip()
                    if date_value.startswith('FY '):
                        publication_date = date_value.replace('FY ', '')
                    else:
                        publication_date = date_value
                elif link and link.strip():
                    # Try to extract date from URL if no date in CSV
                    publication_date = self.sync_extract_date_from_url(link.strip())
                
                # Get source information
                source_info = row.get('source', 'NASA Research')
                
                # Create a meaningful abstract from available data
                abstract = row.get('Description', f"NASA research article: {title}")
                if not abstract or abstract == title:
                    abstract = f"NASA research article: {title}"
                    if "microgravity" in title.lower():
                        abstract += " - Study focuses on microgravity effects and space biology research."
                    elif "space" in title.lower():
                        abstract += " - Research conducted in space environment conditions."
                    else:
                        abstract += " - Important findings for space exploration and astronaut health."
                
                # Determine research type based on content and source
                research_type = "Research Papers"
                if source_info == "Task Book Projects":
                    research_type = "Task Book Grants"
                elif "OSDR" in title or "data" in title.lower():
                    research_type = "OSDR Data"
                elif "task" in title.lower() or "project" in title.lower():
                    research_type = "Task Book Grants"
                
                # Get author information
                authors = ["NASA Space Biology Database"]
                if 'Author' in row and row['Author'] and str(row['Author']).strip():
                    author_info = str(row['Author']).strip()
                    if author_info and author_info != 'nan':
                        authors = [author_info]
                
                # Generate relevant tags based on title content and available data
                tags = ["Space Biology"]
                title_lower = title.lower()
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
                
                # Add tags from CSV data if available
                if 'Tags' in row and row['Tags'] and str(row['Tags']).strip():
                    csv_tags = str(row['Tags']).strip()
                    if csv_tags and csv_tags != 'nan' and csv_tags != 'Not specified':
                        tags.extend([tag.strip() for tag in csv_tags.split(',') if tag.strip()])
                
                results.append({
                    "title": title,
                    "abstract": abstract,
                    "link": link,
                    "type": research_type,
                    "authors": authors,
                    "date": publication_date,
                    "tags": list(set(tags))  # Remove duplicates
                })
            
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
        if not self.loaded or self.data is None:
            return {"loaded": False, "total_articles": 0}
        
        # Count articles by type based on content analysis
        research_papers = 0
        osdr_data = 0
        taskbook_projects = 0
        
        if self.data is not None:
            for _, row in self.data.iterrows():
                title = str(row.get("Title", "")).lower()
                if "osdr" in title or "data" in title:
                    osdr_data += 1
                elif "task" in title or "project" in title:
                    taskbook_projects += 1
                else:
                    research_papers += 1
        
        return {
            "loaded": True,
            "total_articles": len(self.data),
            "research_papers": research_papers,
            "osdr_data": osdr_data,
            "taskbook_projects": taskbook_projects,
            "sources": ["NASA Articles CSV"],
            "columns": list(self.data.columns),
            "csv_path": self.csv_path
        }

# Global instance
csv_service = CSVDataService()

def get_csv_service() -> CSVDataService:
    """Dependency injection for FastAPI"""
    return csv_service