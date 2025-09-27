#!/bin/bash

# HiLabs Backend Deployment Script
# This script pulls latest code and redeploys the application

set -e  # Exit on any error

echo "🚀 Starting HiLabs Backend Deployment..."

# Pull latest code from git
echo "📥 Pulling latest code from repository..."
git pull origin main

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Remove old images to ensure fresh build
echo "🧹 Cleaning up old Docker images..."
docker-compose build --no-cache

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check if backend is healthy
echo "🔍 Checking backend health..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy!"
else
    echo "❌ Backend health check failed!"
    docker-compose logs backend
    exit 1
fi

# Show running containers
echo "📊 Current container status:"
docker-compose ps

echo "🎉 Deployment completed successfully!"
echo "🌐 Backend is available at: http://$(curl -s http://checkip.amazonaws.com)/"
echo "📚 API Documentation: http://$(curl -s http://checkip.amazonaws.com)/docs"
