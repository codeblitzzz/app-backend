from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..config.database import get_db
from ..models.schemas import HealthResponse
from ..services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["health"])


@router.get("/")
async def root():
    return {"message": "AI-Powered Database Query API", "docs": "/docs"}


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Test AI model connection
    ai_status = ai_service.check_health()
    
    return HealthResponse(
        status="healthy" if db_status == "connected" and ai_status == "connected" else "degraded",
        database=db_status,
        ai_model=ai_status
    )
