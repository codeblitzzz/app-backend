from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..models.schemas import ProvidersResponse, DuplicatesResponse
from ..services.data_service import data_service

router = APIRouter(prefix="/providers", tags=["providers"])


@router.post("/process_csv")
async def process_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Process uploaded CSV file using preprocessing function"""
    return await data_service.process_csv_file(file, db)


@router.get("", response_model=ProvidersResponse)
async def get_providers(
    page: int = 1, 
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get paginated list of providers with specific columns"""
    providers, total, total_pages = data_service.get_providers_paginated(db, page, limit)
    
    return ProvidersResponse(
        providers=providers,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.get("/duplicates", response_model=DuplicatesResponse)
async def get_duplicates(db: Session = Depends(get_db)):
    """Get duplicate clusters with provider information"""
    clusters, total_clusters, total_duplicates = data_service.get_duplicate_clusters(db)
    
    return DuplicatesResponse(
        clusters=clusters,
        total_clusters=total_clusters,
        total_duplicates=total_duplicates
    )
