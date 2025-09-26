#!/usr/bin/env python3
"""
Comprehensive validation script for the modular backend
"""
import sys
import os
import traceback

def validate_structure():
    """Validate the directory structure"""
    print("🔍 Validating directory structure...")
    
    required_dirs = [
        "app",
        "app/config",
        "app/models", 
        "app/routes",
        "app/services",
        "app/utils"
    ]
    
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/config/__init__.py",
        "app/config/settings.py",
        "app/config/database.py",
        "app/models/__init__.py",
        "app/models/schemas.py",
        "app/routes/__init__.py",
        "app/routes/health.py",
        "app/routes/query.py", 
        "app/routes/providers.py",
        "app/routes/analytics.py",
        "app/services/__init__.py",
        "app/services/ai_service.py",
        "app/services/data_service.py",
        "app/services/analytics_service.py",
        "app/utils/__init__.py"
    ]
    
    missing_dirs = []
    missing_files = []
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ Directory structure is valid")
    return True

def validate_imports():
    """Validate that all modules can be imported"""
    print("\n🔍 Validating module imports...")
    
    import_tests = [
        ("Config Settings", "from app.config.settings import settings"),
        ("Database Config", "from app.config.database import get_db, test_db_connection"),
        ("Schemas", "from app.models.schemas import QueryRequest, QueryResponse, Provider"),
        ("AI Service", "from app.services.ai_service import ai_service"),
        ("Data Service", "from app.services.data_service import data_service"),
        ("Analytics Service", "from app.services.analytics_service import analytics_service"),
        ("Health Routes", "from app.routes import health"),
        ("Query Routes", "from app.routes import query"),
        ("Provider Routes", "from app.routes import providers"),
        ("Analytics Routes", "from app.routes import analytics"),
        ("Main App", "from app.main import app")
    ]
    
    failed_imports = []
    
    for name, import_stmt in import_tests:
        try:
            exec(import_stmt)
            print(f"✅ {name}")
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
            failed_imports.append((name, str(e)))
    
    if failed_imports:
        print(f"\n❌ Failed imports: {len(failed_imports)}")
        for name, error in failed_imports:
            print(f"  - {name}: {error}")
        return False
    
    print("✅ All imports successful")
    return True

def validate_configuration():
    """Validate configuration settings"""
    print("\n🔍 Validating configuration...")
    
    try:
        from app.config.settings import settings
        
        # Check database configuration
        required_vars = ["DATABASE_HOST", "DATABASE_USER", "DATABASE_PASSWORD", "DATABASE_NAME"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            print("Please set these variables in your .env file")
            return False
        
        print(f"✅ Database configuration: {settings.database_host}:{settings.database_port}/{settings.database_name}")
        print(f"✅ API configuration: {settings.api_host}:{settings.api_port}")
        print(f"✅ AI Model URL: {settings.sql_model_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {str(e)}")
        return False

def validate_fastapi_app():
    """Validate FastAPI application setup"""
    print("\n🔍 Validating FastAPI application...")
    
    try:
        from app.main import app
        
        # Check if app is FastAPI instance
        from fastapi import FastAPI
        if not isinstance(app, FastAPI):
            print("❌ App is not a FastAPI instance")
            return False
        
        # Check routes
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health", "/query", "/providers", "/providers/duplicates", "/analytics/specialty-experience", "/analytics/providers-by-specialty", "/analytics/providers-by-state"]
        
        missing_routes = []
        for expected_route in expected_routes:
            if not any(expected_route in route for route in routes):
                missing_routes.append(expected_route)
        
        if missing_routes:
            print(f"❌ Missing routes: {missing_routes}")
            return False
        
        print(f"✅ FastAPI app created with {len(routes)} routes")
        return True
        
    except Exception as e:
        print(f"❌ FastAPI validation failed: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run all validation tests"""
    print("🚀 Starting Backend Validation\n")
    
    # Change to backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    tests = [
        ("Directory Structure", validate_structure),
        ("Module Imports", validate_imports),
        ("Configuration", validate_configuration),
        ("FastAPI Application", validate_fastapi_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\n❌ {test_name} validation failed")
        except Exception as e:
            print(f"\n❌ {test_name} validation error: {str(e)}")
            traceback.print_exc()
    
    print(f"\n📊 Validation Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All validations passed! Backend is ready for deployment.")
        return True
    else:
        print("⚠️  Some validations failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
