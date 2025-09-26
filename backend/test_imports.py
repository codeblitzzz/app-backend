#!/usr/bin/env python3
"""
Test script to validate the modular backend structure
"""

def test_imports():
    """Test that all modules can be imported successfully"""
    try:
        # Test config imports
        from app.config.settings import settings
        from app.config.database import get_db, test_db_connection
        print("✓ Config modules imported successfully")
        
        # Test model imports
        from app.models.schemas import QueryRequest, QueryResponse, Provider
        print("✓ Model schemas imported successfully")
        
        # Test service imports
        from app.services.ai_service import ai_service
        from app.services.data_service import data_service
        from app.services.analytics_service import analytics_service
        print("✓ Service modules imported successfully")
        
        # Test route imports
        from app.routes import health, query, providers, analytics
        print("✓ Route modules imported successfully")
        
        # Test main app import
        from app.main import app
        print("✓ Main application imported successfully")
        
        print("\n🎉 All modular components imported successfully!")
        print(f"Database URL: {settings.database_url}")
        print(f"API Host: {settings.api_host}:{settings.api_port}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        return False

if __name__ == "__main__":
    test_imports()
