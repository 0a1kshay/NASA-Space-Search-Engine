from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from typing import List, Optional
import json
import csv
import io
import uuid

from app.db import get_db, Neo4jDatabase
from app.models import PublicationCreate, Publication

router = APIRouter(
    prefix="/ingest",
    tags=["ingest"],
    responses={404: {"description": "Not found"}},
)


@router.post("/json", response_model=List[str])
async def ingest_json_data(
    publications: List[PublicationCreate],
    db: Neo4jDatabase = Depends(get_db)
):
    """
    Ingest multiple publications in JSON format.
    
    Parameters:
        publications (List[PublicationCreate]): List of publication data objects.
        
    Returns:
        List[str]: List of created publication IDs.
    """
    try:
        publication_ids = []
        
        for pub_data in publications:
            # Generate UUID for the publication if not provided
            pub_dict = pub_data.model_dump()
            pub_dict["id"] = str(uuid.uuid4())
            
            # Create publication in database
            pub_id = db.create_publication(pub_dict)
            publication_ids.append(pub_id)
        
        return publication_ids
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting publications: {str(e)}")


@router.post("/csv", response_model=List[str])
async def ingest_csv_data(
    file: UploadFile = File(...),
    db: Neo4jDatabase = Depends(get_db)
):
    """
    Ingest publications from a CSV file.
    
    Parameters:
        file (UploadFile): CSV file with publication data.
        
    Returns:
        List[str]: List of created publication IDs.
    """
    try:
        # Read CSV file
        content = await file.read()
        csv_file = io.StringIO(content.decode('utf-8'))
        csv_reader = csv.DictReader(csv_file)
        
        publication_ids = []
        
        for row in csv_reader:
            # Convert CSV row to publication data
            pub_data = {
                "id": str(uuid.uuid4()),
                "title": row.get("title", ""),
                "authors": row.get("authors", "").split(";"),  # Assuming authors are separated by semicolons
                "year": int(row.get("year", 0)),
                "url": row.get("url", ""),
                "abstract": row.get("abstract", ""),
                "organisms": row.get("organisms", "").split(";") if row.get("organisms") else [],
                "assays": row.get("assays", "").split(";") if row.get("assays") else [],
                "phenotypes": row.get("phenotypes", "").split(";") if row.get("phenotypes") else [],
                "missions": row.get("missions", "").split(";") if row.get("missions") else []
            }
            
            # Create publication in database
            pub_id = db.create_publication(pub_data)
            publication_ids.append(pub_id)
        
        return publication_ids
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting CSV data: {str(e)}")