from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..config.database import get_db
from ..models.schemas import QueryRequest, QueryResponse
from ..services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def query_database(request: QueryRequest, db: Session = Depends(get_db)):
    """Generate SQL query from natural language and execute it"""
    try:
        # Generate SQL query using AI model
        sql_query = ai_service.generate_sql_query(request.question)
        
        if not sql_query:
            return QueryResponse(
                question=request.question,
                sql_query="",
                results=[],
                success=False,
                error="Failed to generate SQL query"
            )
        
        logger.info(f"Generated SQL: {sql_query}")
        
        # Execute the query
        try:
            result = db.execute(text(sql_query))
            rows = result.fetchall()
            
            # Convert to list of dictionaries
            columns = result.keys()
            results = [dict(zip(columns, row)) for row in rows]
            
            return QueryResponse(
                question=request.question,
                sql_query=sql_query,
                results=results,
                success=True
            )
            
        except Exception as db_error:
            logger.error(f"Database execution error: {str(db_error)}")
            return QueryResponse(
                question=request.question,
                sql_query=sql_query,
                results=[],
                success=False,
                error=f"Database error: {str(db_error)}"
            )
    
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        return QueryResponse(
            question=request.question,
            sql_query="",
            results=[],
            success=False,
            error=str(e)
        )
