from pydantic import BaseModel
from typing import List, Optional


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    sql_query: str
    results: List[dict]
    success: bool
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    database: str
    ai_model: str


class Provider(BaseModel):
    provider_id: Optional[str] = None
    npi: Optional[int] = None
    full_name: Optional[str] = None
    primary_specialty: Optional[str] = None
    license_number: Optional[str] = None
    license_state: Optional[str] = None


class ProvidersResponse(BaseModel):
    providers: List[Provider]
    total: int
    page: int
    limit: int
    total_pages: int


class Duplicate(BaseModel):
    i1: Optional[int] = None
    i2: Optional[int] = None
    provider_id_1: Optional[str] = None
    provider_id_2: Optional[str] = None
    name_1: Optional[str] = None
    name_2: Optional[str] = None
    score: Optional[float] = None
    name_score: Optional[float] = None
    npi_match: Optional[bool] = None
    addr_score: Optional[float] = None
    phone_match: Optional[bool] = None
    license_score: Optional[float] = None


class ClusterInfo(BaseModel):
    cluster_id: str
    members: List[int]
    representative: int
    providers: List[Provider]
    duplicates: List[Duplicate]


class DuplicatesResponse(BaseModel):
    clusters: List[ClusterInfo]
    total_clusters: int
    total_duplicates: int
