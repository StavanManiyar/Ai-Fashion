#!/bin/bash

echo "🚀 Starting AI Fashion Microservices Architecture..."

# Create shared directories
mkdir -p shared/domain/entities
mkdir -p shared/domain/services
mkdir -p shared/utils

# Stop any existing services
echo "🛑 Stopping existing services..."
docker-compose -f docker-compose.microservices.yml down

# Build and start all services
echo "🔧 Building and starting services..."
docker-compose -f docker-compose.microservices.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

echo "Image Processing Service:"
curl -f http://localhost:8001/health || echo "❌ Image Processing Service not ready"

echo "Color Matching Service:"
curl -f http://localhost:8002/health || echo "❌ Color Matching Service not ready"

echo "Product Service:"
curl -f http://localhost:8003/health || echo "❌ Product Service not ready"

echo "Gateway:"
curl -f http://localhost:8080/api/image/health || echo "❌ Gateway not ready"

# Show logs
echo "📋 Service logs:"
docker-compose -f docker-compose.microservices.yml logs --tail=50

echo "✅ Microservices architecture started successfully!"
echo "🌐 API Gateway available at: http://localhost:8080"
echo "🖼️  Image Processing Service: http://localhost:8001"
echo "🎨 Color Matching Service: http://localhost:8002"
echo "🛍️  Product Service: http://localhost:8003"
echo "📊 Redis: redis://localhost:6379"
