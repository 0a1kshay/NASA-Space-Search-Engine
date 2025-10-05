from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from app.db import get_db, Neo4jDatabase
from app.models import GraphResponse, Dataset, Project

router = APIRouter(
    prefix="/graph",
    tags=["graph"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=GraphResponse)
async def get_graph(
    node_type: Optional[str] = Query(None, description="Filter by node type (Publication, Dataset, Project, Author)"),
    limit: int = Query(100, description="Maximum number of nodes to return"),
    keyword: Optional[str] = Query(None, description="Filter by keyword"),
    db: Neo4jDatabase = Depends(get_db)
):
    """Get graph data for visualization with optional filters"""
    
    if db.mock_mode:
        # Return enhanced mock graph data for development
        mock_nodes = [
            {"id": "pub_001", "label": "Plant Adaptation to Microgravity", "type": "Publication"},
            {"id": "auth_001", "label": "Dr. Sarah Johnson", "type": "Author"},
            {"id": "GLDS-394", "label": "Arabidopsis Gene Expression in Space", "type": "Dataset"},
            {"id": "TB-2023-001", "label": "Molecular Mechanisms Project", "type": "Project"},
            {"id": "microgravity", "label": "microgravity", "type": "Keyword"},
            {"id": "plant_biology", "label": "plant biology", "type": "Keyword"}
        ]
        mock_edges = [
            {"source": "pub_001", "target": "auth_001", "type": "AUTHORED_BY"},
            {"source": "pub_001", "target": "GLDS-394", "type": "USES_DATASET"},
            {"source": "TB-2023-001", "target": "auth_001", "type": "LED_BY"},
            {"source": "TB-2023-001", "target": "GLDS-394", "type": "GENERATED"},
            {"source": "pub_001", "target": "microgravity", "type": "TAGGED_WITH"},
            {"source": "GLDS-394", "target": "plant_biology", "type": "TAGGED_WITH"}
        ]
        
        return GraphResponse(
            nodes=mock_nodes,
            edges=mock_edges,
            stats={
                "node_count": len(mock_nodes),
                "edge_count": len(mock_edges),
                "node_types": len(set(node["type"] for node in mock_nodes))
            },
            metadata={
                "query_filters": {
                    "node_type": node_type,
                    "keyword": keyword,
                    "limit": limit
                },
                "timestamp": "2023-10-03T12:00:00Z",
                "mode": "mock"
            }
        )
    
    try:
        with db.driver.session() as session:
            # Build dynamic query based on filters
            node_filter = ""
            if node_type:
                node_filter = f"WHERE '{node_type}' IN labels(n)"
            
            if keyword:
                if node_filter:
                    node_filter += f" AND (n.title CONTAINS '{keyword}' OR n.name CONTAINS '{keyword}' OR n.description CONTAINS '{keyword}')"
                else:
                    node_filter = f"WHERE (n.title CONTAINS '{keyword}' OR n.name CONTAINS '{keyword}' OR n.description CONTAINS '{keyword}')"
            
            # Get nodes
            nodes_query = f"""
                MATCH (n)
                {node_filter}
                RETURN id(n) as id, labels(n)[0] as type, 
                       COALESCE(n.title, n.name, n.id) as label,
                       COALESCE(n.description, '') as description
                LIMIT {min(limit, 500)}
            """
            
            nodes_result = session.run(nodes_query)
            
            nodes = []
            node_ids = set()
            for record in nodes_result:
                node_id = str(record["id"])
                nodes.append({
                    "id": node_id,
                    "label": record["label"],
                    "type": record["type"],
                    "description": record["description"][:100] + "..." if len(record["description"]) > 100 else record["description"]
                })
                node_ids.add(node_id)
            
            # Get edges for the selected nodes
            if node_ids:
                edges_query = """
                MATCH (n)-[r]->(m)
                WHERE id(n) IN $node_ids AND id(m) IN $node_ids
                RETURN id(n) as source, id(m) as target, type(r) as type
                LIMIT 1000
                """
                
                edges_result = session.run(edges_query, node_ids=list(map(int, node_ids)))
                
                edges = []
                for record in edges_result:
                    edges.append({
                        "source": str(record["source"]),
                        "target": str(record["target"]),
                        "type": record["type"]
                    })
            else:
                edges = []
            
            # Generate stats and metadata
            stats = {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "node_types": len(set(node["type"] for node in nodes))
            }
            
            metadata = {
                "query_filters": {
                    "node_type": node_type,
                    "keyword": keyword,
                    "limit": limit
                },
                "timestamp": str(db.driver.session().run("RETURN datetime() as now").single()["now"]) if not db.mock_mode else "2023-10-03T12:00:00Z"
            }
            
            return GraphResponse(nodes=nodes, edges=edges, stats=stats, metadata=metadata)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/publications", response_model=List[dict])
async def get_publications(
    limit: int = Query(50, description="Maximum number of publications to return"),
    author: Optional[str] = Query(None, description="Filter by author name"),
    keyword: Optional[str] = Query(None, description="Filter by keyword"),
    db: Neo4jDatabase = Depends(get_db)
):
    """Get publications with optional filters"""
    
    if db.mock_mode:
        return [
            {
                "id": "pub_001",
                "title": "Plant Adaptation to Microgravity",
                "authors": ["Dr. Sarah Johnson", "Dr. Michael Chen"],
                "journal": "Space Biology Research",
                "year": 2023,
                "doi": "10.1016/j.sbr.2023.001"
            }
        ]
    
    try:
        with db.driver.session() as session:
            # Build query with filters
            where_clauses = []
            if author:
                where_clauses.append("ANY(auth IN p.authors WHERE auth CONTAINS $author)")
            if keyword:
                where_clauses.append("(p.title CONTAINS $keyword OR p.abstract CONTAINS $keyword)")
            
            where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            
            query = f"""
                MATCH (p:Publication)
                {where_clause}
                RETURN p.id as id, p.title as title, p.authors as authors,
                       p.journal as journal, p.year as year, p.doi as doi,
                       p.abstract as abstract
                ORDER BY p.year DESC
                LIMIT {min(limit, 200)}
            """
            
            result = session.run(query, author=author, keyword=keyword)
            
            publications = []
            for record in result:
                publications.append({
                    "id": record["id"],
                    "title": record["title"],
                    "authors": record["authors"] or [],
                    "journal": record["journal"],
                    "year": record["year"],
                    "doi": record["doi"],
                    "abstract": record["abstract"][:200] + "..." if record["abstract"] and len(record["abstract"]) > 200 else record["abstract"]
                })
            
            return publications
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/datasets", response_model=List[Dataset])
async def get_datasets(
    limit: int = Query(50, description="Maximum number of datasets to return"),
    organism: Optional[str] = Query(None, description="Filter by organism"),
    experiment_type: Optional[str] = Query(None, description="Filter by experiment type"),
    db: Neo4jDatabase = Depends(get_db)
):
    """Get datasets with optional filters"""
    
    if db.mock_mode:
        return [
            Dataset(
                id="GLDS-394",
                title="Arabidopsis Gene Expression in Microgravity",
                description="RNA-seq analysis of Arabidopsis thaliana grown in microgravity conditions",
                organism="Arabidopsis thaliana",
                experiment_type="RNA Sequencing",
                data_source="NASA GeneLab",
                release_date="2023-01-15"
            )
        ]
    
    try:
        with db.driver.session() as session:
            # Build query with filters
            where_clauses = []
            if organism:
                where_clauses.append("d.organism CONTAINS $organism")
            if experiment_type:
                where_clauses.append("d.experiment_type CONTAINS $experiment_type")
            
            where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            
            query = f"""
                MATCH (d:Dataset)
                {where_clause}
                RETURN d.id as id, d.title as title, d.description as description,
                       d.organism as organism, d.experiment_type as experiment_type,
                       d.data_source as data_source, d.release_date as release_date
                ORDER BY d.release_date DESC
                LIMIT {min(limit, 200)}
            """
            
            result = session.run(query, organism=organism, experiment_type=experiment_type)
            
            datasets = []
            for record in result:
                datasets.append(Dataset(
                    id=record["id"],
                    title=record["title"],
                    description=record["description"],
                    organism=record["organism"],
                    experiment_type=record["experiment_type"],
                    data_source=record["data_source"],
                    release_date=record["release_date"]
                ))
            
            return datasets
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/projects", response_model=List[Project])
async def get_projects(
    limit: int = Query(50, description="Maximum number of projects to return"),
    discipline: Optional[str] = Query(None, description="Filter by discipline"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Neo4jDatabase = Depends(get_db)
):
    """Get projects with optional filters"""
    
    if db.mock_mode:
        return [
            Project(
                id="TB-2023-001",
                title="Molecular Mechanisms of Plant Adaptation to Microgravity",
                pi="Dr. Sarah Johnson",
                institution="University of California, Davis",
                discipline="Plant Biology",
                status="Active",
                funding_amount=750000
            )
        ]
    
    try:
        with db.driver.session() as session:
            # Build query with filters
            where_clauses = []
            if discipline:
                where_clauses.append("p.discipline CONTAINS $discipline")
            if status:
                where_clauses.append("p.status = $status")
            
            where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            
            query = f"""
                MATCH (p:Project)
                {where_clause}
                RETURN p.id as id, p.title as title, p.pi as pi,
                       p.pi_institution as institution, p.discipline as discipline,
                       p.status as status, p.award_amount as funding_amount,
                       p.description as description
                ORDER BY p.start_date DESC
                LIMIT {min(limit, 200)}
            """
            
            result = session.run(query, discipline=discipline, status=status)
            
            projects = []
            for record in result:
                projects.append(Project(
                    id=record["id"],
                    title=record["title"],
                    pi=record["pi"],
                    institution=record["institution"],
                    discipline=record["discipline"],
                    status=record["status"],
                    funding_amount=record["funding_amount"],
                    description=record["description"]
                ))
            
            return projects
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/search")
async def search_graph(
    query: str = Query(..., description="Search query"),
    limit: int = Query(20, description="Maximum number of results"),
    db: Neo4jDatabase = Depends(get_db)
):
    """Full-text search across all node types"""
    
    if db.mock_mode:
        return {
            "results": [
                {
                    "id": "pub_001",
                    "title": "Plant Adaptation to Microgravity",
                    "type": "Publication",
                    "relevance": 0.95
                }
            ],
            "query": query,
            "total": 1
        }
    
    try:
        with db.driver.session() as session:
            # Full-text search query
            search_query = """
                CALL db.index.fulltext.queryNodes("searchIndex", $query) YIELD node, score
                RETURN id(node) as id, labels(node)[0] as type,
                       COALESCE(node.title, node.name, node.id) as title,
                       COALESCE(node.description, node.abstract, '') as description,
                       score
                ORDER BY score DESC
                LIMIT $limit
            """
            
            try:
                result = session.run(search_query, query=query, limit=min(limit, 100))
                
                results = []
                for record in result:
                    results.append({
                        "id": str(record["id"]),
                        "title": record["title"],
                        "type": record["type"],
                        "description": record["description"][:150] + "..." if len(record["description"]) > 150 else record["description"],
                        "relevance": record["score"]
                    })
                
                return {
                    "results": results,
                    "query": query,
                    "total": len(results)
                }
                
            except Exception:
                # Fallback to simple text search if full-text index doesn't exist
                fallback_query = """
                    MATCH (n)
                    WHERE n.title CONTAINS $query OR n.name CONTAINS $query 
                       OR n.description CONTAINS $query OR n.abstract CONTAINS $query
                    RETURN id(n) as id, labels(n)[0] as type,
                           COALESCE(n.title, n.name, n.id) as title,
                           COALESCE(n.description, n.abstract, '') as description
                    LIMIT $limit
                """
                
                result = session.run(fallback_query, query=query, limit=min(limit, 100))
                
                results = []
                for record in result:
                    results.append({
                        "id": str(record["id"]),
                        "title": record["title"],
                        "type": record["type"],
                        "description": record["description"][:150] + "..." if len(record["description"]) > 150 else record["description"],
                        "relevance": 1.0
                    })
                
                return {
                    "results": results,
                    "query": query,
                    "total": len(results)
                }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.get("/node/{node_id}")
async def get_node(node_id: str, db: Neo4jDatabase = Depends(get_db)):
    """
    Retrieve detailed information about a specific node.
    
    Parameters:
        node_id (str): The ID of the node to retrieve.
        
    Returns:
        NodeDetail: Detailed information about the node.
    """
    try:
        node_data = db.get_node_details(node_id)
        if node_data is None:
            raise HTTPException(status_code=404, detail=f"Node with ID {node_id} not found")
        return node_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving node details: {str(e)}")