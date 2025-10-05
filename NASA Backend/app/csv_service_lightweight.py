"""
Lightweight CSV Data Service for NASA Space Biology Search Engine
Pure Python implementation without pandas dependency
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
    """Lightweight CSV service using pure Python"""
    
    def __init__(self):
        self.data: List[Dict[str, Any]] = []
        self.csv_path = None
        self.loaded = False
        self.date_cache = {}  # Cache for extracted dates to avoid repeated requests
        
    def load_csv_data(self, csv_path: str = None) -> bool:
        """
        Load CSV data from multiple files using pure Python
        
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
                'source': 'Taskbook Projects', 
                'required_columns': ['Title', 'Description']
            }
        ]
        
        # If specific path provided, try to load it
        if csv_path:
            try:
                data = self._load_single_file_pure_python(csv_path, 'Custom')
                if data:
                    all_data.extend(data)
                    files_loaded.append(csv_path)
                    self.csv_path = csv_path
            except Exception as e:
                logger.error(f"Failed to load specific CSV file {csv_path}: {e}")
                return False
        else:
            # Try to load all available data files
            for data_file in data_files:
                data = self._load_single_file_from_config(data_file)
                if data:
                    all_data.extend(data)
                    files_loaded.append(data_file['path'])
        
        if all_data:
            self.data = all_data
            self.loaded = True
            logger.info(f"✅ Successfully loaded {len(self.data)} records from {len(files_loaded)} files")
            logger.info(f"📁 Files loaded: {files_loaded}")
            return True
        else:
            logger.warning("❌ No CSV files could be loaded")
            return False
    
    def _load_single_file_from_config(self, data_file: Dict) -> List[Dict[str, Any]]:
        """Load a single file based on configuration"""
        # Try primary path first
        file_path = data_file['path']
        if os.path.exists(file_path):
            return self._load_single_file_pure_python(file_path, data_file['source'])
        
        # Try alternative paths
        for alt_path in data_file.get('alt_paths', []):
            if os.path.exists(alt_path):
                logger.info(f"📁 Using alternative path: {alt_path}")
                return self._load_single_file_pure_python(alt_path, data_file['source'])
        
        logger.warning(f"⚠️  File not found: {file_path} (tried {len(data_file.get('alt_paths', []))} alternatives)")
        return []
    
    def _load_single_file_pure_python(self, file_path: str, source: str) -> List[Dict[str, Any]]:
        """
        Load a single CSV file using pure Python csv module
        
        Args:
            file_path: Path to the CSV file
            source: Source identifier for the data
            
        Returns:
            List of dictionaries representing the CSV data
        """
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as csvfile:
                # Detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Clean and standardize the row
                        cleaned_row = self._standardize_columns_pure_python(row, source)
                        cleaned_row['source'] = source
                        cleaned_row['row_id'] = f"{source}_{row_num}"
                        data.append(cleaned_row)
                    except Exception as e:
                        logger.warning(f"⚠️  Error processing row {row_num} in {file_path}: {e}")
                        continue
            
            logger.info(f"✅ Loaded {len(data)} records from {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error loading CSV file {file_path}: {e}")
            return []
    
    def _standardize_columns_pure_python(self, row: Dict[str, str], source: str) -> Dict[str, Any]:
        """
        Standardize column names and data types using pure Python
        
        Args:
            row: Raw CSV row dictionary
            source: Source identifier
            
        Returns:
            Standardized row dictionary
        """
        standardized = {}
        
        # Column mappings for different sources
        column_mappings = {
            'NASA Articles': {
                'title': ['Title', 'title', 'name', 'Name'],
                'description': ['Description', 'description', 'abstract', 'Abstract', 'summary', 'Summary'],
                'link': ['Link', 'link', 'url', 'URL', 'doi', 'DOI'],
                'authors': ['Authors', 'authors', 'author', 'Author'],
                'year': ['Year', 'year', 'date', 'Date', 'published', 'Published'],
                'keywords': ['Keywords', 'keywords', 'tags', 'Tags'],
                'journal': ['Journal', 'journal', 'publication', 'Publication'],
                'type': ['Type', 'type', 'category', 'Category']
            },
            'Taskbook Projects': {
                'title': ['Title', 'title', 'project_title', 'Project Title'],
                'description': ['Description', 'description', 'objective', 'Objective'],
                'discipline': ['Discipline', 'discipline', 'field', 'Field'],
                'status': ['Status', 'status', 'state', 'State'],
                'investigator': ['Investigator', 'investigator', 'pi', 'PI']
            }
        }
        
        # Get mappings for this source
        mappings = column_mappings.get(source, column_mappings['NASA Articles'])
        
        # Standardize each field
        for standard_key, possible_keys in mappings.items():
            value = None
            for key in possible_keys:
                if key in row and row[key] and str(row[key]).strip():
                    value = str(row[key]).strip()
                    break
            
            if value:
                # Clean and process the value
                if standard_key == 'year':
                    standardized[standard_key] = self._extract_year(value)
                elif standard_key in ['keywords', 'tags']:
                    standardized[standard_key] = self._process_keywords(value)
                else:
                    standardized[standard_key] = self._clean_text(value)
        
        # Add any unmapped columns with original keys
        for key, value in row.items():
            if key not in [mapped_key for keys in mappings.values() for mapped_key in keys]:
                if value and str(value).strip():
                    standardized[key] = self._clean_text(str(value))
        
        return standardized
    
    def _clean_text(self, text: str) -> str:
        """Clean text data"""
        if not text:
            return ""
        
        # Remove extra whitespace and clean up
        cleaned = re.sub(r'\s+', ' ', str(text)).strip()
        
        # Remove common CSV artifacts
        cleaned = cleaned.replace('""', '"').replace("''", "'")
        
        return cleaned
    
    def _extract_year(self, text: str) -> Optional[int]:
        """Extract year from text"""
        if not text:
            return None
        
        # Try to find a 4-digit year
        year_match = re.search(r'\b(19|20)\d{2}\b', str(text))
        if year_match:
            try:
                return int(year_match.group())
            except ValueError:
                pass
        
        return None
    
    def _process_keywords(self, text: str) -> List[str]:
        """Process keywords/tags into a list"""
        if not text:
            return []
        
        # Split by common delimiters
        keywords = re.split(r'[,;|]', str(text))
        
        # Clean and filter
        cleaned_keywords = []
        for keyword in keywords:
            cleaned = keyword.strip().lower()
            if cleaned and len(cleaned) > 1:
                cleaned_keywords.append(cleaned)
        
        return cleaned_keywords
    
    def search(self, query: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search through loaded CSV data
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of matching records
        """
        if not self.loaded or not self.data:
            logger.error("❌ CSV data not loaded")
            return []
        
        if not query or query.strip() == "":
            # Return all data if no query
            return self.data[:limit]
        
        query_lower = query.lower().strip()
        results = []
        
        for record in self.data:
            score = self._calculate_match_score(record, query_lower)
            if score > 0:
                record_copy = record.copy()
                record_copy['search_score'] = score
                results.append(record_copy)
        
        # Sort by score (highest first) and limit
        results.sort(key=lambda x: x.get('search_score', 0), reverse=True)
        return results[:limit]
    
    def _calculate_match_score(self, record: Dict[str, Any], query: str) -> float:
        """Calculate match score for a record"""
        score = 0.0
        
        # Search in different fields with different weights
        search_fields = {
            'title': 3.0,
            'description': 2.0,
            'keywords': 2.5,
            'authors': 1.5,
            'journal': 1.0
        }
        
        for field, weight in search_fields.items():
            if field in record and record[field]:
                field_text = str(record[field]).lower()
                
                # Exact match bonus
                if query in field_text:
                    score += weight
                
                # Word matching
                query_words = query.split()
                for word in query_words:
                    if len(word) > 2 and word in field_text:
                        score += weight * 0.3
        
        return score
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded data"""
        if not self.loaded:
            return {"total_articles": 0, "loaded": False, "csv_path": None}
        
        stats = {
            "total_articles": len(self.data),
            "loaded": True,
            "csv_path": self.csv_path or "multiple_files"
        }
        
        # Add source breakdown
        sources = {}
        for record in self.data:
            source = record.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        stats['sources'] = sources
        
        # Add field coverage
        field_coverage = {}
        for record in self.data:
            for field in record.keys():
                if field not in ['source', 'row_id', 'search_score']:
                    field_coverage[field] = field_coverage.get(field, 0) + 1
        
        stats['field_coverage'] = field_coverage
        
        return stats
    
    def get_filter_counts(self) -> Dict[str, Dict[str, int]]:
        """Get counts for different filter categories"""
        if not self.loaded:
            return {}
        
        counts = {
            'type': {},
            'year': {},
            'source': {},
            'discipline': {}
        }
        
        for record in self.data:
            # Count by type
            record_type = record.get('type', 'Unknown')
            counts['type'][record_type] = counts['type'].get(record_type, 0) + 1
            
            # Count by year
            year = record.get('year')
            if year:
                year_str = str(year)
                counts['year'][year_str] = counts['year'].get(year_str, 0) + 1
            
            # Count by source
            source = record.get('source', 'Unknown')
            counts['source'][source] = counts['source'].get(source, 0) + 1
            
            # Count by discipline (if available)
            discipline = record.get('discipline')
            if discipline:
                counts['discipline'][discipline] = counts['discipline'].get(discipline, 0) + 1
        
        return counts

# Create global instance
csv_service = CSVDataService()