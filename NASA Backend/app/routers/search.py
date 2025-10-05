from fastapi import APIRouter, Depends, HTTPException, Query, Header
from typing import List, Optional
import json
import logging
import asyncio

from app.db import get_db, Neo4jDatabase
from app.models import Publication
from app.csv_service import get_csv_service, CSVDataService
from app.services.nasa_api_service import get_nasa_api_service, NASAAPIService

logger = logging.getLogger(__name__)

# API Key constant
VALID_API_KEY = "i31G2AKUI24gGq2oaw8w8sYGryZEjMArrJEjffcT"

def verify_api_key(x_api_key: str = Header(None, alias="x-api-key")):
    """
    Dependency to verify API key for search endpoints
    """
    if x_api_key != VALID_API_KEY:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid or missing API key"}
        )
    return True

router = APIRouter(
    prefix="/search",
    tags=["search"],
    responses={404: {"description": "Not found"}},
)


@router.get("/csv", response_model=dict)
async def search_csv_articles(
    query: Optional[str] = Query(None, description="Search query for articles"),
    limit: int = Query(10, description="Maximum number of results (default: 10)"),
    csv_service: CSVDataService = Depends(get_csv_service),
    _: bool = Depends(verify_api_key)
):
    """
    Search articles from CSV data
    
    Parameters:
        query (str, optional): Search term to find in Title and Description
        limit (int): Maximum number of results to return (default: 10)
        
    Returns:
        dict: JSON response with count and results
        
    Example response:
        {
            "count": 3,
            "results": [
                {"Title": "Effects of Microgravity on Plant Cell Wall Formation", "Link": "https://osdr.nasa.gov/..."}
            ]
        }
    """
    try:
        if query is None or query.strip() == '':
            # Return empty results for empty query
            return {"count": 0, "results": []}
        
        # Search the CSV data
        search_results = csv_service.search(query=query, limit=limit)
        
        return search_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching CSV data: {str(e)}")


@router.get("/csv/stats")
async def get_csv_stats(csv_service: CSVDataService = Depends(get_csv_service)):
    """Get statistics about the loaded CSV data"""
    return csv_service.get_stats()


@router.get("/nasa/test")
async def test_nasa_apis(nasa_service: NASAAPIService = Depends(get_nasa_api_service)):
    """Test connectivity to all NASA Open Science APIs"""
    try:
        test_results = await nasa_service.test_apis()
        return {
            "status": "completed",
            "apis": test_results,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"NASA API test error: {e}")
        raise HTTPException(status_code=500, detail=f"NASA API test failed: {str(e)}")


@router.get("/nasa/search")
async def search_nasa_only(
    query: str = Query(..., description="Search query for NASA APIs only"),
    limit: int = Query(20, description="Maximum number of results"),
    nasa_service: NASAAPIService = Depends(get_nasa_api_service),
    _: bool = Depends(verify_api_key)
):
    """Search only NASA Open Science APIs (no local data)"""
    try:
        nasa_data = await nasa_service.fetch_nasa_data(query, limit)
        
        # Format results for frontend compatibility
        all_results = []
        for source_key, results in nasa_data.items():
            if source_key in ["osdr_studies", "osdr_biodata", "ntrs_publications", "nslsl_experiments"]:
                all_results.extend(results)
        
        return {
            "count": len(all_results),
            "results": all_results,
            "nasa_sources": nasa_data.get("sources_queried", []),
            "errors": nasa_data.get("errors", [])
        }
        
    except Exception as e:
        logger.error(f"NASA-only search error: {e}")
        raise HTTPException(status_code=500, detail=f"NASA search failed: {str(e)}")


@router.get("/", response_model=dict)
async def search_articles(
    query: Optional[str] = Query(None, description="Search query for articles"),
    limit: int = Query(10, description="Maximum number of results (default: 10)"),
    include_nasa_apis: bool = Query(True, description="Include NASA Open Science APIs in search"),
    csv_service: CSVDataService = Depends(get_csv_service),
    nasa_service: NASAAPIService = Depends(get_nasa_api_service),
    _: bool = Depends(verify_api_key)
):
    """
    Search NASA articles from CSV data - returns normalized JSON for frontend cards
    
    Parameters:
        query (str, optional): Search term to find in Title and Description
        limit (int): Maximum number of results to return (default: 10)
        
    Returns:
        dict: JSON response with count and results formatted for frontend cards
        
    Example response:
        {
            "count": 2,
            "results": [
                {
                    "title": "Effects of Microgravity on Plant Cell Wall Formation",
                    "abstract": "Study description...",
                    "link": "https://www.ncbi.nlm.nih.gov/...",
                    "type": "Research Papers",
                    "authors": ["NASA Space Biology Database"],
                    "date": "N/A",
                    "tags": ["Space Biology", "Microgravity"]
                }
            ]
        }
    """
    try:
        # Check if CSV data is loaded
        if not csv_service.loaded:
            logger.warning("CSV data not loaded, attempting to load...")
            if not csv_service.load_csv_data():
                return {"count": 0, "results": [], "message": "CSV not loaded"}
        
        # Search local CSV data
        local_results = csv_service.search(query=query or "", limit=limit)
        
        # If NASA APIs are disabled, return only local results
        if not include_nasa_apis or not query or not query.strip():
            return local_results
        
        # Fetch data from NASA APIs
        try:
            nasa_data = await nasa_service.fetch_nasa_data(query, limit//2)  # Split limit between local and NASA
            
            # Merge NASA API results with local results
            unified_results = nasa_service.get_unified_results(
                nasa_data, 
                local_results.get("results", []), 
                max_results=limit
            )
            
            return unified_results
            
        except Exception as nasa_error:
            logger.error(f"NASA API error: {nasa_error}")
            # Fallback to local results if NASA APIs fail
            local_results["nasa_api_error"] = str(nasa_error)
            return local_results
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching articles: {str(e)}")