from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PublicationBase(BaseModel):
    """Base model for Publication data"""
    title: str
    authors: List[str]
    year: int
    url: Optional[str] = None
    abstract: Optional[str] = None


class PublicationCreate(PublicationBase):
    """Model for Publication creation"""
    organisms: Optional[List[str]] = []
    assays: Optional[List[str]] = []
    phenotypes: Optional[List[str]] = []
    missions: Optional[List[str]] = []


class Publication(PublicationBase):
    """Model for Publication response"""
    id: str
    organisms: List[str] = []
    assays: List[str] = []
    phenotypes: List[str] = []
    missions: List[str] = []


class Node(BaseModel):
    """Model for graph node"""
    id: str
    label: str
    type: str


class Edge(BaseModel):
    """Model for graph edge"""
    source: str
    target: str
    label: str


class Graph(BaseModel):
    """Model for full graph response"""
    nodes: List[Node]
    edges: List[Edge]


class NodeDetail(BaseModel):
    """Model for node detail response"""
    type: str
    details: Dict[str, Any]


class SummarizeRequest(BaseModel):
    """Model for summarization request"""
    text: str
    max_length: Optional[int] = 150


class SummaryResponse(BaseModel):
    """Model for summarization response"""
    summary: str


class CompareRequest(BaseModel):
    """Model for comparison request"""
    publication_id1: str
    publication_id2: str


class ComparisonResponse(BaseModel):
    """Model for comparison response"""
    publication1: Dict[str, Any]
    publication2: Dict[str, Any]
    common: Dict[str, List[str]]


# NASA Dataset Models
class DatasetBase(BaseModel):
    """Base model for NASA Dataset"""
    id: str
    title: str
    organism: Optional[str] = None
    assay_type: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None


class DatasetCreate(DatasetBase):
    """Model for Dataset creation"""
    pass


class Dataset(DatasetBase):
    """Model for Dataset response"""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ProjectBase(BaseModel):
    """Base model for NASA Project"""
    id: str
    title: str
    pi: Optional[str] = None  # Principal Investigator
    funding_program: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Model for Project creation"""
    pass


class Project(ProjectBase):
    """Model for Project response"""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AuthorBase(BaseModel):
    """Base model for Author"""
    name: str
    affiliation: Optional[str] = None
    email: Optional[str] = None
    orcid: Optional[str] = None


class AuthorCreate(AuthorBase):
    """Model for Author creation"""
    pass


class Author(AuthorBase):
    """Model for Author response"""
    id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class GraphResponse(BaseModel):
    """Enhanced model for graph response with NASA data"""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    stats: Dict[str, int]
    metadata: Dict[str, Any]


class IngestionRequest(BaseModel):
    """Model for data ingestion request"""
    data_type: str  # 'publications', 'datasets', 'projects'
    source_file: Optional[str] = None
    source_url: Optional[str] = None
    batch_size: Optional[int] = 100


class IngestionResponse(BaseModel):
    """Model for data ingestion response"""
    status: str
    message: str
    processed_count: int
    error_count: int
    errors: List[str] = []