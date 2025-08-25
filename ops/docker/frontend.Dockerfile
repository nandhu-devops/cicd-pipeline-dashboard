# Build stage
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY frontend/ .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy custom nginx configuration
COPY ops/docker/nginx.conf /etc/nginx/nginx.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create non-root user
RUN adduser -D -H -u 1000 -s /bin/bash www-data

# Change ownership of nginx directories
RUN chown -R www-data:www-data /var/cache/nginx \
    && chown -R www-data:www-data /var/log/nginx \
    && chown -R www-data:www-data /etc/nginx/conf.d \
    && touch /var/run/nginx.pid \
    && chown -R www-data:www-data /var/run/nginx.pid

# Switch to non-root user
USER www-data

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
