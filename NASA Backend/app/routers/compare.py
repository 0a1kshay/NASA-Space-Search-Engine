from fastapi import APIRouter, Depends, HTTPException

from app.db import get_db, Neo4jDatabase
from app.models import CompareRequest, ComparisonResponse

router = APIRouter(
    prefix="/compare",
    tags=["compare"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=ComparisonResponse)
async def compare_publications(request: CompareRequest, db: Neo4jDatabase = Depends(get_db)):
    """
    Compare two publications to find similarities and differences.
    
    Parameters:
        request (CompareRequest): IDs of the publications to compare.
        
    Returns:
        ComparisonResponse: Comparison results with common and unique elements.
    """
    try:
        pub_id1 = request.publication_id1
        pub_id2 = request.publication_id2
        
        comparison = db.compare_publications(pub_id1, pub_id2)
        
        if comparison is None:
            raise HTTPException(status_code=404, detail="One or both publications not found")
            
        return comparison
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing publications: {str(e)}")