# Modular Backend Architecture

This backend has been refactored into a clean, modular architecture for better maintainability and deployment.

## Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Main FastAPI application
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py         # Application settings and AWS RDS config
│   │   └── database.py         # Database connection and session management
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models and schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py           # Health check endpoints
│   │   ├── query.py            # AI-powered query endpoints
│   │   ├── providers.py        # Provider and duplicate management
│   │   └── analytics.py        # Analytics and reporting endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py       # AI model integration service
│   │   ├── data_service.py     # Data processing and CSV handling
│   │   └── analytics_service.py # Analytics and reporting logic
│   └── utils/
│       └── __init__.py         # Utility functions
├── main.py                     # Legacy entry point (backward compatibility)
├── pipeline.py                 # Data processing pipeline (unchanged)
├── requirements.txt            # Updated dependencies
├── .env.example               # Environment variables template
├── Dockerfile                 # Docker configuration
└── README.md                  # This file
```

## Key Features

### 🔧 Configuration Management
- **AWS RDS Integration**: Direct connection to AWS RDS MySQL database
- **Environment Variables**: Centralized configuration through settings.py
- **Database Connection**: Optimized connection pooling and health checks

### 🛣️ Modular Routes
- **Health Checks**: `/health` endpoint for monitoring
- **AI Queries**: `/query` for natural language to SQL conversion
- **Provider Management**: `/providers` for provider data and CSV processing
- **Analytics**: `/analytics/*` for various reporting endpoints

### 🔄 Service Layer
- **AI Service**: Handles AI model interactions and SQL generation
- **Data Service**: Manages CSV processing and provider data operations
- **Analytics Service**: Provides reporting and analytics functionality

### 📊 Database Configuration
- **Host**: Configurable via `DATABASE_HOST` environment variable
- **Port**: Configurable via `DATABASE_PORT` environment variable (default: 3306)
- **Database**: Configurable via `DATABASE_NAME` environment variable (default: demo)
- **User**: Configurable via `DATABASE_USER` environment variable

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=your_password_here
DATABASE_NAME=demo

# AI Model Configuration
SQL_MODEL_URL=http://model-runner.docker.internal:12434
SQL_MODEL_NAME=hf.co/unsloth/gemma-3-270m-it-GGUF

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Data Path
DATA_PATH=/app/data
```

## Running the Application

### With Docker Compose (Recommended)
```bash
docker-compose up backend
```

### Standalone
```bash
cd backend
pip install -r requirements.txt
python3 -m app.main
```

### Testing Imports
```bash
cd backend
python3 test_imports.py
```

## API Endpoints

All existing endpoints remain unchanged:

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /query` - Natural language query
- `POST /providers/process_csv` - CSV file processing
- `GET /providers` - Get providers (paginated)
- `GET /providers/duplicates` - Get duplicate clusters
- `GET /analytics/specialty-experience` - Specialty experience data
- `GET /analytics/providers-by-specialty` - Provider specialty distribution
- `GET /analytics/providers-by-state` - Provider state distribution

## Backward Compatibility

The legacy `main.py` file in the backend root imports from the modular structure, ensuring existing Docker configurations continue to work without changes.

## Benefits

1. **Clean Architecture**: Separation of concerns with distinct layers
2. **Easy Deployment**: AWS RDS integration removes local database dependency
3. **Maintainability**: Modular structure makes code easier to understand and modify
4. **Scalability**: Services can be easily extended or replaced
5. **Testing**: Individual components can be tested in isolation
6. **Configuration**: Centralized environment management
