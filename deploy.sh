#!/bin/bash

# CI/CD Dashboard Deployment Script
set -e

echo "🚀 Deploying CI/CD Health Dashboard..."

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t cicd-dashboard:latest .

# Stop and remove existing container if running
echo "🛑 Stopping existing container..."
docker stop cicd-dashboard 2>/dev/null || true
docker rm cicd-dashboard 2>/dev/null || true

# Create data and logs directories
mkdir -p data logs

# Run the container
echo "🚀 Starting new container..."
docker run -d \
  --name cicd-dashboard \
  --restart unless-stopped \
  -p 8080:80 \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e WRITE_KEY=${WRITE_KEY:-your-secret-key-here} \
  -e DEBUG=false \
  -e ALERTS_ENABLED=true \
  cicd-dashboard:latest

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 10

# Check health
echo "🏥 Checking container health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Dashboard is healthy!"
    echo "🌐 Frontend: http://localhost:8080"
    echo "🔌 Backend API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
else
    echo "❌ Dashboard health check failed"
    echo "📋 Container logs:"
    docker logs cicd-dashboard
    exit 1
fi

echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Configure GitHub Actions with webhook URL: http://localhost:8000/api/webhook/github-actions"
echo "2. Set DASHBOARD_WRITE_KEY secret in GitHub repository"
echo "3. Open dashboard at: http://localhost:8080"
echo ""
echo "🔧 To view logs: docker logs -f cicd-dashboard"
echo "🛑 To stop: docker stop cicd-dashboard"
