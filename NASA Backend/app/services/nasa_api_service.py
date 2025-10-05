"""
NASA Open Science APIs Integration Service
Fetches and normalizes data from multiple NASA APIs
"""

import httpx
import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import json
import os
from urllib.parse import urlencode, quote
import hashlib

logger = logging.getLogger(__name__)

class NASAAPIService:
    """Service to integrate multiple NASA Open Science APIs"""
    
    def __init__(self):
        # API Base URLs from environment (updated to current working endpoints as of 2025)
        self.osdr_main_url = os.getenv("NASA_OSDR_MAIN_API_URL", "https://osdr.nasa.gov/bio/repo/search")
        self.osdr_biodata_url = os.getenv("NASA_OSDR_BIODATA_API_URL", "https://data.nasa.gov/api/3/action/package_search")
        self.ntrs_url = os.getenv("NASA_NTRS_API_URL", "https://ntrs.nasa.gov/api/search")
        self.nslsl_url = os.getenv("NASA_NSLSL_API_URL", "https://public.ksc.nasa.gov/nslsl/api/search")  # NSLSL API endpoint
        
        # HTTP client configuration
        self.timeout = httpx.Timeout(30.0)
        self.rate_limit_delay = 0.5  # seconds between requests
        
        # Simple memory cache
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache TTL
        
    async def fetch_nasa_data(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """
        Unified function to fetch data from all NASA APIs
        
        Args:
            query: Search query string
            limit: Maximum results per API source
            
        Returns:
            Normalized results from all NASA APIs
        """
        logger.info(f"Fetching NASA data for query: '{query}' with limit: {limit}")
        
        # Check cache first
        cache_key = self._get_cache_key(query, limit)
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            if datetime.now() - cached_result['timestamp'] < timedelta(seconds=self.cache_ttl):
                logger.info("Returning cached NASA API results")
                return cached_result['data']
        
        results = {
            "osdr_studies": [],
            "osdr_biodata": [],
            "ntrs_publications": [],
            "nslsl_experiments": [],
            "total_count": 0,
            "sources_queried": [],
            "errors": []
        }
        
        # Create async HTTP client
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Fetch from all APIs in parallel
            tasks = [
                self._fetch_osdr_main(client, query, limit),
                self._fetch_osdr_biodata(client, query, limit),
                self._fetch_ntrs(client, query, limit),
                self._fetch_nslsl(client, query, limit)
            ]
            
            # Execute all requests with proper error handling
            api_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(api_results):
                api_name = ["OSDR Main", "OSDR BioData", "NTRS", "NSLSL"][i]
                
                if isinstance(result, Exception):
                    error_msg = f"{api_name} API error: {str(result)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
                else:
                    results["sources_queried"].append(api_name)
                    if i == 0:  # OSDR Main
                        results["osdr_studies"] = result
                    elif i == 1:  # OSDR BioData
                        results["osdr_biodata"] = result
                    elif i == 2:  # NTRS
                        results["ntrs_publications"] = result
                    elif i == 3:  # NSLSL
                        results["nslsl_experiments"] = result
        
        # Calculate total count
        results["total_count"] = (
            len(results["osdr_studies"]) + 
            len(results["osdr_biodata"]) + 
            len(results["ntrs_publications"]) + 
            len(results["nslsl_experiments"])
        )
        
        # Cache results
        self.cache[cache_key] = {
            'data': results,
            'timestamp': datetime.now()
        }
        
        logger.info(f"NASA API fetch complete: {results['total_count']} total results from {len(results['sources_queried'])} sources")
        return results
    
    async def _fetch_osdr_main(self, client: httpx.AsyncClient, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fetch data from NASA OSDR Main API"""
        try:
            # OSDR search endpoint
            url = self.osdr_main_url
            params = {
                "q": query,
                "data_source": "cgene,alsda,esa",
                "data_type": "study",
                "size": min(limit, 50),
                "from": 0
            }
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            # Handle OSDR response structure
            studies = data.get("studies", data.get("results", []))
            
            normalized_results = []
            for study in studies:
                normalized_results.append(self._normalize_osdr_study(study))
            
            await asyncio.sleep(self.rate_limit_delay)
            return normalized_results
            
        except Exception as e:
            logger.error(f"OSDR Main API error: {e}")
            raise
    
    async def _fetch_osdr_biodata(self, client: httpx.AsyncClient, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fetch data from NASA Open Data Portal using CKAN API"""
        try:
            # NASA Open Data Portal CKAN API endpoint
            url = self.osdr_biodata_url
            params = {
                "q": f"tags:osdr OR tags:biodata OR {query}",
                "rows": min(limit, 100),
                "sort": "metadata_modified desc"
            }
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            datasets = data.get("result", {}).get("results", [])
            
            normalized_results = []
            for dataset in datasets:
                normalized_results.append(self._normalize_osdr_biodata(dataset))
            
            await asyncio.sleep(self.rate_limit_delay)
            return normalized_results
            
        except Exception as e:
            logger.error(f"OSDR BioData API error: {e}")
            raise
    
    async def _fetch_ntrs(self, client: httpx.AsyncClient, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fetch data from NASA Technical Reports Server (NTRS) API"""
        try:
            # NTRS search API endpoint
            url = self.ntrs_url
            params = {
                "q": query,
                "size": min(limit, 100),
                "highlight": "true",
                "sort": "_score desc, publication_date desc"
            }
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            publications = data.get("results", data.get("hits", {}).get("hits", []))
            
            normalized_results = []
            for pub in publications:
                # Handle both direct results and Elasticsearch hits format
                pub_data = pub.get("_source", pub)
                normalized_results.append(self._normalize_ntrs_publication(pub_data))
            
            await asyncio.sleep(self.rate_limit_delay)
            return normalized_results
            
        except Exception as e:
            logger.error(f"NTRS API error: {e}")
            raise
    
    async def _fetch_nslsl(self, client: httpx.AsyncClient, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fetch data from NASA Space Life Sciences Library (NSLSL)"""
        try:
            # NSLSL search endpoint
            url = self.nslsl_url
            params = {
                "q": query,
                "format": "json",
                "limit": min(limit, 50),
                "category": "space-life-sciences"
            }
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            experiments = data.get("results", data.get("documents", []))
            
            normalized_results = []
            for exp in experiments:
                normalized_results.append(self._normalize_nslsl_experiment(exp))
            
            await asyncio.sleep(self.rate_limit_delay)
            return normalized_results
            
        except Exception as e:
            logger.error(f"NSLSL API error: {e}")
            raise
    
    def _normalize_osdr_study(self, study_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize OSDR study data to standard format"""
        study_id = study_data.get("accession", study_data.get("id", study_data.get("study_id", "")))
        return {
            "id": study_id,
            "title": study_data.get("title", study_data.get("name", "")),
            "abstract": study_data.get("description", study_data.get("study_description", study_data.get("summary", ""))),
            "authors": self._ensure_list(study_data.get("principal_investigator", study_data.get("pi", []))),
            "date": study_data.get("date_created", study_data.get("submission_date", study_data.get("date", ""))),
            "keywords": self._ensure_list(study_data.get("factors", study_data.get("keywords", []))),
            "link": f"https://osdr.nasa.gov/bio/repo/data/studies/{study_id}" if study_id else "#",
            "source": "NASA OSDR",
            "type": "OSDR Data",
            "organism": self._ensure_list(study_data.get("organism", [])),
            "mission": study_data.get("mission", study_data.get("flight_program", "")),
            "experiment_type": study_data.get("assay_technology", study_data.get("type", "")),
            "doi": study_data.get("doi", ""),
            "relevance_score": 0.8  # Default relevance for OSDR
        }
    
    def _normalize_osdr_biodata(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize NASA Open Data Portal CKAN data to standard format"""
        dataset_id = dataset.get("id", dataset.get("name", ""))
        tags = [tag.get("display_name", tag.get("name", "")) if isinstance(tag, dict) else str(tag) for tag in dataset.get("tags", [])]
        return {
            "id": dataset_id,
            "title": dataset.get("title", dataset.get("name", "")),
            "abstract": dataset.get("notes", dataset.get("description", "")),
            "authors": self._ensure_list([dataset.get("author", dataset.get("maintainer", ""))]),
            "date": dataset.get("metadata_modified", dataset.get("metadata_created", "")),
            "keywords": self._ensure_list(tags),
            "link": f"https://data.nasa.gov/dataset/{dataset.get('name', dataset_id)}" if dataset_id else "#",
            "source": "NASA Open Data Portal",
            "type": "NASA Dataset",
            "organism": "",  # Not typically available in CKAN metadata
            "mission": "",   # Not typically available in CKAN metadata
            "experiment_type": dataset.get("type", ""),
            "data_type": ", ".join([res.get("format", "") for res in dataset.get("resources", [])]),
            "relevance_score": 0.85  # Good relevance for open data
        }
    
    def _normalize_ntrs_publication(self, publication: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize NTRS v1 publication to standard format"""
        pub_id = publication.get("id", publication.get("ntrs_id", publication.get("recordId", "")))
        return {
            "id": pub_id,
            "title": publication.get("title", publication.get("documentTitle", "")),
            "abstract": publication.get("abstract", publication.get("description", publication.get("summary", ""))),
            "authors": self._ensure_list(publication.get("authors", publication.get("creator", []))),
            "date": publication.get("publication_date", publication.get("publicationDate", publication.get("date", ""))),
            "keywords": self._ensure_list(publication.get("keywords", publication.get("subject_terms", publication.get("subjectTerms", [])))),
            "link": f"https://ntrs.nasa.gov/citations/{pub_id}" if pub_id else "#",
            "source": "NASA NTRS",
            "type": "Research Papers",
            "publication_type": publication.get("document_type", publication.get("documentType", "")),
            "center": publication.get("center", publication.get("publishingCenter", "")),
            "program": publication.get("program", publication.get("researchProgram", "")),
            "doi": publication.get("doi", ""),
            "relevance_score": 0.85  # High relevance for technical reports
        }
    
    def _normalize_nslsl_experiment(self, experiment: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize NSLSL experiment (now from NTRS) to standard format"""
        exp_id = experiment.get("experiment_id", experiment.get("id", experiment.get("recordId", "")))
        return {
            "id": exp_id,
            "title": experiment.get("title", experiment.get("experiment_name", experiment.get("documentTitle", ""))),
            "abstract": experiment.get("description", experiment.get("objective", experiment.get("abstract", ""))),
            "authors": self._ensure_list([experiment.get("principal_investigator", experiment.get("creator", ""))]),
            "date": experiment.get("start_date", experiment.get("date", experiment.get("publicationDate", ""))),
            "keywords": self._ensure_list(experiment.get("research_areas", experiment.get("subjectTerms", []))),
            "link": f"https://ntrs.nasa.gov/citations/{exp_id}" if exp_id else "#",
            "source": "NASA NSLSL (via NTRS)",
            "type": "Space Life Sciences",
            "facility": experiment.get("facility", experiment.get("center", "")),
            "mission": experiment.get("mission", experiment.get("program", "")),
            "status": experiment.get("status", ""),
            "duration": experiment.get("duration", ""),
            "relevance_score": 0.9  # High relevance for life sciences
        }
    
    def _ensure_list(self, value) -> List[str]:
        """Ensure a value is a list of strings"""
        if value is None:
            return []
        if isinstance(value, str):
            return [value] if value else []
        if isinstance(value, list):
            return [str(item) for item in value if item]
        return [str(value)] if value else []
    
    def get_unified_results(self, nasa_data: Dict[str, Any], local_results: List[Dict[str, Any]], 
                          max_results: int = 50) -> Dict[str, Any]:
        """
        Merge NASA API results with local CSV results
        
        Args:
            nasa_data: Results from NASA APIs
            local_results: Results from local CSV
            max_results: Maximum total results to return
            
        Returns:
            Unified and ranked results
        """
        unified_results = []
        
        # Add NASA results with source identification
        for source_key, results in nasa_data.items():
            if source_key in ["osdr_studies", "osdr_biodata", "ntrs_publications", "nslsl_experiments"]:
                for result in results:
                    unified_results.append({
                        **result,
                        "is_nasa_api": True,
                        "search_source": result.get("source", "NASA API")
                    })
        
        # Add local results
        for result in local_results:
            unified_results.append({
                **result,
                "is_nasa_api": False,
                "search_source": "Local Database",
                "relevance_score": 0.7  # Default for local
            })
        
        # Remove duplicates based on title similarity
        unified_results = self._deduplicate_results(unified_results)
        
        # Sort by relevance score and date
        unified_results.sort(key=lambda x: (
            x.get("relevance_score", 0.5),
            self._parse_date(x.get("date", ""))
        ), reverse=True)
        
        # Limit results
        unified_results = unified_results[:max_results]
        
        return {
            "count": len(unified_results),
            "results": unified_results,
            "nasa_sources": len([r for r in unified_results if r.get("is_nasa_api", False)]),
            "local_sources": len([r for r in unified_results if not r.get("is_nasa_api", False)]),
            "total_nasa_apis_queried": len(nasa_data.get("sources_queried", [])),
            "api_errors": nasa_data.get("errors", [])
        }
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on title similarity"""
        seen_titles = set()
        unique_results = []
        
        for result in results:
            title = result.get("title", "").lower().strip()
            title_hash = hashlib.md5(title.encode()).hexdigest()[:16]
            
            if title_hash not in seen_titles and len(title) > 10:  # Skip very short titles
                seen_titles.add(title_hash)
                unique_results.append(result)
        
        return unique_results
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse various date formats"""
        if not date_str:
            return datetime.min
        
        try:
            # Try common formats
            for fmt in ["%Y-%m-%d", "%Y", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    return datetime.strptime(str(date_str)[:len(fmt)], fmt)
                except ValueError:
                    continue
            return datetime.min
        except:
            return datetime.min
    
    def _get_cache_key(self, query: str, limit: int) -> str:
        """Generate cache key for query"""
        return hashlib.md5(f"{query}_{limit}".encode()).hexdigest()
    
    async def test_apis(self) -> Dict[str, Any]:
        """Test all NASA APIs for connectivity"""
        test_results = {
            "osdr_main": {"status": "unknown", "message": ""},
            "osdr_biodata": {"status": "unknown", "message": ""},
            "ntrs": {"status": "unknown", "message": ""},
            "nslsl": {"status": "unknown", "message": ""}
        }
        
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            # Test each API with current working endpoints
            apis = [
                ("osdr_main", f"{self.osdr_main_url}?q=microgravity&data_source=cgene,alsda,esa&data_type=study&size=1"),
                ("osdr_biodata", f"{self.osdr_biodata_url}?q=osdr&rows=1"),
                ("ntrs", f"{self.ntrs_url}?q=microgravity&size=1"),
                ("nslsl", f"{self.nslsl_url}?q=microgravity&format=json&limit=1")
            ]
            
            for api_name, url in apis:
                try:
                    response = await client.get(url)
                    if response.status_code == 200:
                        test_results[api_name] = {"status": "success", "message": "API accessible"}
                    else:
                        test_results[api_name] = {"status": "error", "message": f"HTTP {response.status_code}"}
                except Exception as e:
                    test_results[api_name] = {"status": "error", "message": str(e)}
        
        return test_results

# Global service instance
nasa_api_service = NASAAPIService()

def get_nasa_api_service() -> NASAAPIService:
    """Dependency injection for FastAPI"""
    return nasa_api_service