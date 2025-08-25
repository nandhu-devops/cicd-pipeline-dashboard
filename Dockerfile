# Multi-stage build for CI/CD Health Dashboard
FROM python:3.11-slim AS backend

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install Python dependencies
COPY backend/requirements.docker.txt .
RUN pip install --no-cache-dir -r requirements.docker.txt

# Copy backend code
COPY backend/ ./backend/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Production stage with Nginx
FROM nginx:alpine AS production

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy frontend files
COPY frontend/ /usr/share/nginx/html/

# Copy the complete backend environment from backend stage
COPY --from=backend /app /app

# Install only curl for health checks (Python is already available from backend stage)
RUN apk add --no-cache curl

# Create startup script
RUN echo '#!/bin/sh' > /start.sh && \
    echo 'cd /app' >> /start.sh && \
    echo 'uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &' >> /start.sh && \
    echo 'nginx -g "daemon off;"' >> /start.sh && \
    chmod +x /start.sh

# Expose ports
EXPOSE 80 8000

# Start both services
CMD ["/start.sh"]
