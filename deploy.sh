#!/bin/bash

# HiLabs Backend Deployment Script
# This script pulls latest code and redeploys the application

set -e  # Exit on any error

echo "🚀 Starting HiLabs Backend Deployment..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository. Please run this script from the project root."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create one from .env.example"
    echo "Run: cp .env.example .env"
    echo "Then edit .env with your actual database credentials"
    exit 1
fi

# Pull latest code from git
echo "📥 Pulling latest code from repository..."
git pull origin main || {
    echo "⚠️  Git pull failed. Continuing with current code..."
}

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down || {
    echo "⚠️  No containers to stop, continuing..."
}

# Remove old images to ensure fresh build
echo "🧹 Cleaning up old Docker images..."
docker-compose build --no-cache

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check if backend is healthy (try both port 80 and 8000)
echo "🔍 Checking backend health..."
HEALTH_CHECK_PASSED=false

# Try port 80 first (production)
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy on port 80!"
    HEALTH_CHECK_PASSED=true
    BACKEND_URL="http://$(curl -s http://checkip.amazonaws.com)/"
# Try port 8000 (development)
elif curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy on port 8000!"
    HEALTH_CHECK_PASSED=true
    BACKEND_URL="http://$(curl -s http://checkip.amazonaws.com):8000/"
else
    echo "❌ Backend health check failed on both ports!"
    echo "📋 Container logs:"
    docker-compose logs backend
    echo "📊 Container status:"
    docker-compose ps
    exit 1
fi

# Show running containers
echo "📊 Current container status:"
docker-compose ps

if [ "$HEALTH_CHECK_PASSED" = true ]; then
    echo "🎉 Deployment completed successfully!"
    echo "🌐 Backend is available at: $BACKEND_URL"
    echo "📚 API Documentation: ${BACKEND_URL}docs"
    echo "🔍 Health Check: ${BACKEND_URL}health"
fi
