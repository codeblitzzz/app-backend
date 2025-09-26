from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..services.analytics_service import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/specialty-experience")
async def get_specialty_experience_data(db: Session = Depends(get_db)):
    """Get specialty experience data for box plot visualization"""
    return analytics_service.get_specialty_experience_data(db)


@router.get("/providers-by-specialty")
async def get_providers_by_specialty(db: Session = Depends(get_db)):
    """Get provider categorization data by specialty for pie chart visualization"""
    return analytics_service.get_providers_by_specialty(db)


@router.get("/providers-by-state")
async def get_providers_by_state(db: Session = Depends(get_db)):
    """Get provider distribution data by state for bar chart visualization"""
    return analytics_service.get_providers_by_state(db)
