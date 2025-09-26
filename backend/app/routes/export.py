from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.provider import Provider
import csv
import io
from typing import List

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/providers/csv")
async def export_providers_csv(db: Session = Depends(get_db)):
    """Export all providers to CSV format"""
    try:
        # Query all providers
        providers = db.query(Provider).all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Provider ID', 'NPI', 'Full Name', 'Primary Specialty', 
            'License Number', 'License State', 'Years Experience',
            'Created At', 'Updated At'
        ])
        
        # Write data rows
        for provider in providers:
            writer.writerow([
                provider.provider_id,
                provider.npi,
                provider.full_name,
                provider.primary_specialty,
                provider.license_number,
                provider.license_state,
                provider.years_experience,
                provider.created_at,
                provider.updated_at
            ])
        
        # Prepare response
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename=providers_export.csv'}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/providers/csv/filtered")
async def export_filtered_providers_csv(
    specialty: str = None,
    state: str = None,
    db: Session = Depends(get_db)
):
    """Export filtered providers to CSV format"""
    try:
        # Build query with filters
        query = db.query(Provider)
        
        if specialty:
            query = query.filter(Provider.primary_specialty.ilike(f"%{specialty}%"))
        if state:
            query = query.filter(Provider.license_state == state)
            
        providers = query.all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Provider ID', 'NPI', 'Full Name', 'Primary Specialty', 
            'License Number', 'License State', 'Years Experience'
        ])
        
        # Write data rows
        for provider in providers:
            writer.writerow([
                provider.provider_id,
                provider.npi,
                provider.full_name,
                provider.primary_specialty,
                provider.license_number,
                provider.license_state,
                provider.years_experience
            ])
        
        # Prepare response
        output.seek(0)
        filename = f"providers_export_{'_'.join(filter(None, [specialty, state]))}.csv"
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
