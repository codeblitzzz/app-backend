from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config.settings import settings
from .config.database import test_db_connection
from .config.logging import setup_logging, get_logger
from .routes import health, query, providers, analytics, export

# Configure logging
setup_logging()
logger = get_logger("main")

# Create FastAPI application
app = FastAPI(
    title="AI-Powered Database Query API", 
    version="1.0.0",
    description="Modular healthcare provider database API with AI-powered querying"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(query.router)
app.include_router(providers.router)
app.include_router(analytics.router)
app.include_router(export.router)

# Legacy routes for backward compatibility
from .routes.providers import get_duplicates, process_csv

# Add legacy endpoints at root level
app.add_api_route("/duplicates", get_duplicates, methods=["GET"], include_in_schema=False)
app.add_api_route("/process_csv", process_csv, methods=["POST"], include_in_schema=False)


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting AI-Powered Database Query API...")
    logger.info(f"Database URL: {settings.database_url}")
    logger.info(f"AI Model URL: {settings.sql_model_url}")
    
    # Test database connection
    if test_db_connection():
        logger.info("Database connection verified successfully")
    else:
        logger.warning("Database connection failed - check configuration")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down AI-Powered Database Query API...")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
