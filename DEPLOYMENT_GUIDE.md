# Deployment Guide - Modular Backend with AWS RDS

## Overview
The backend has been successfully modularized and configured to use AWS RDS instead of local MySQL. This guide covers deployment and testing.

## Quick Start

### 1. Using Docker Compose (Recommended)
```bash
# Navigate to project root
cd /home/ujjwal/Downloads/hilabs-main

# Start the services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 2. Manual Deployment
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run validation (optional)
python3 validate_backend.py

# Start the application
python3 -m app.main
```

## Configuration

### Environment Variables
The application uses the following environment variables (already configured in docker-compose.yml):

```yaml
# AWS RDS Database
DATABASE_HOST: admin.c9sumkiag01s.eu-north-1.rds.amazonaws.com
DATABASE_PORT: 3306
DATABASE_USER: bpadmin
DATABASE_PASSWORD: Qwerty1234
DATABASE_NAME: demo

# AI Model
SQL_MODEL_URL: http://model-runner.docker.internal:12434
SQL_MODEL_NAME: hf.co/unsloth/gemma-3-270m-it-gguf

# API Settings
API_HOST: 0.0.0.0
API_PORT: 8000
DEBUG: true
DATA_PATH: /app/data
```

## Testing the Deployment

### 1. Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "ai_model": "connected"
}
```

### 2. Test API Endpoints

**Root endpoint:**
```bash
curl http://localhost:8000/
```

**Query endpoint:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How many providers are there?"}'
```

**Providers endpoint:**
```bash
curl http://localhost:8000/providers?page=1&limit=5
```

**Analytics endpoints:**
```bash
curl http://localhost:8000/analytics/specialty-experience
curl http://localhost:8000/analytics/providers-by-specialty
curl http://localhost:8000/analytics/providers-by-state
```

### 3. Frontend Integration
The frontend should work without any changes since all API endpoints remain the same:
- Frontend runs on: http://localhost:3000
- Backend API: http://localhost:8000

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check AWS RDS security groups allow connections
   - Verify credentials in environment variables
   - Ensure RDS instance is running

2. **AI Model Unavailable**
   - Check if model-runner service is running
   - Verify model URL configuration
   - Check Docker network connectivity

3. **Import Errors**
   - Run validation script: `python3 validate_backend.py`
   - Check Python path and dependencies
   - Verify all required files exist

### Logs
Check application logs:
```bash
# Docker logs
docker-compose logs backend

# Or if running manually
tail -f backend.log
```

## Architecture Benefits

### Before (Monolithic)
- Single large main.py file (741 lines)
- Mixed concerns (DB, AI, routes, business logic)
- Local MySQL dependency
- Difficult to maintain and test

### After (Modular)
- Clean separation of concerns
- 10+ focused modules
- AWS RDS integration
- Easy to maintain, test, and deploy
- Backward compatible

## File Structure
```
backend/
├── app/
│   ├── config/          # Database & settings
│   ├── models/          # Data schemas
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   └── utils/           # Utilities
├── main.py             # Legacy entry point
├── pipeline.py         # Data processing
└── requirements.txt    # Dependencies
```

## Next Steps

1. **Monitor Performance**: Check database connection pooling and query performance
2. **Add Logging**: Implement structured logging for production
3. **Security**: Add authentication and rate limiting if needed
4. **Testing**: Add unit tests for individual services
5. **CI/CD**: Set up automated deployment pipeline

## Support

If you encounter any issues:
1. Run the validation script: `python3 backend/validate_backend.py`
2. Check the logs for specific error messages
3. Verify AWS RDS connectivity and credentials
4. Ensure all environment variables are properly set
