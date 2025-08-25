# CI/CD Health Dashboard Operations Makefile
# 
# Available targets:
#   dev-up      - Start development environment
#   dev-down    - Stop development environment
#   dev-logs    - View development logs
#   seed        - Seed database with sample data
#   alert-test  - Test alert system
#   fmt         - Format code (placeholder)
#   lint        - Lint code (placeholder)
#   prod-up     - Start production environment
#   prod-down   - Stop production environment
#   prod-logs   - View production logs
#   build       - Build all Docker images
#   clean       - Clean up containers and volumes
#   help        - Show this help message

# Configuration
COMPOSE_DEV = docker-compose -f compose.dev.yml
COMPOSE_PROD = docker-compose -f compose.prod.yml
API_BASE = http://localhost:8000
API_KEY = dev-write-key-change-in-production

# Default target
.DEFAULT_GOAL := help

# Development targets
.PHONY: dev-up
dev-up: ## Start development environment
	@echo "🚀 Starting development environment..."
	@mkdir -p data
	$(COMPOSE_DEV) up -d --build
	@echo "✅ Development environment started!"
	@echo "📊 Dashboard: http://localhost:5173"
	@echo "🔧 Backend API: http://localhost:8000"
	@echo "📝 API Docs: http://localhost:8000/docs"

.PHONY: dev-down
dev-down: ## Stop development environment
	@echo "🛑 Stopping development environment..."
	$(COMPOSE_DEV) down
	@echo "✅ Development environment stopped!"

.PHONY: dev-logs
dev-logs: ## View development logs
	@echo "📋 Showing development logs..."
	$(COMPOSE_DEV) logs -f

# Production targets
.PHONY: prod-up
prod-up: ## Start production environment
	@echo "🚀 Starting production environment..."
	@mkdir -p data
	$(COMPOSE_PROD) up -d --build
	@echo "✅ Production environment started!"
	@echo "📊 Dashboard: http://localhost:8080"
	@echo "🔧 Backend API: http://localhost:8000"

.PHONY: prod-down
prod-down: ## Stop production environment
	@echo "🛑 Stopping production environment..."
	$(COMPOSE_PROD) down
	@echo "✅ Production environment stopped!"

.PHONY: prod-logs
prod-logs: ## View production logs
	@echo "📋 Showing production logs..."
	$(COMPOSE_PROD) logs -f

# Build targets
.PHONY: build
build: ## Build all Docker images
	@echo "🔨 Building Docker images..."
	$(COMPOSE_PROD) build
	@echo "✅ All images built successfully!"

# Database and API targets
.PHONY: seed
seed: ## Seed database with sample data
	@echo "🌱 Seeding database with sample data..."
	@curl -X POST "$(API_BASE)/api/seed" \
		-H "Content-Type: application/json" \
		-H "X-API-KEY: $(API_KEY)" \
		-d '{}' \
		-s | jq '.' || echo "❌ Failed to seed database. Is the backend running?"

.PHONY: alert-test
alert-test: ## Test alert system
	@echo "🔔 Testing alert system..."
	@curl -X POST "$(API_BASE)/api/alert/test" \
		-H "Content-Type: application/json" \
		-H "X-API-KEY: $(API_KEY)" \
		-d '{"message": "This is a test alert from the Makefile"}' \
		-s | jq '.' || echo "❌ Failed to test alert. Is the backend running?"

# Code quality targets (placeholders)
.PHONY: fmt
fmt: ## Format code (placeholder)
	@echo "🎨 Code formatting not implemented yet"
	@echo "   Backend: Use black, isort for Python"
	@echo "   Frontend: Use prettier for JavaScript/TypeScript"

.PHONY: lint
lint: ## Lint code (placeholder)
	@echo "🔍 Code linting not implemented yet"
	@echo "   Backend: Use flake8, mypy for Python"
	@echo "   Frontend: Use ESLint for JavaScript/TypeScript"

# Utility targets
.PHONY: clean
clean: ## Clean up containers and volumes
	@echo "🧹 Cleaning up containers and volumes..."
	$(COMPOSE_DEV) down -v --remove-orphans
	$(COMPOSE_PROD) down -v --remove-orphans
	docker system prune -f
	@echo "✅ Cleanup completed!"

.PHONY: status
status: ## Show service status
	@echo "📊 Development environment status:"
	@$(COMPOSE_DEV) ps || echo "   Not running"
	@echo ""
	@echo "📊 Production environment status:"
	@$(COMPOSE_PROD) ps || echo "   Not running"

.PHONY: restart
restart: ## Restart development environment
	@echo "🔄 Restarting development environment..."
	$(COMPOSE_DEV) restart
	@echo "✅ Development environment restarted!"

.PHONY: logs-backend
logs-backend: ## View backend logs
	@echo "📋 Backend logs:"
	$(COMPOSE_DEV) logs -f backend

.PHONY: logs-frontend
logs-frontend: ## View frontend logs
	@echo "📋 Frontend logs:"
	$(COMPOSE_DEV) logs -f frontend

.PHONY: logs-worker
logs-worker: ## View worker logs
	@echo "📋 Worker logs:"
	$(COMPOSE_DEV) logs -f worker

.PHONY: shell-backend
shell-backend: ## Open shell in backend container
	@echo "🐚 Opening shell in backend container..."
	$(COMPOSE_DEV) exec backend /bin/bash

.PHONY: shell-worker
shell-worker: ## Open shell in worker container
	@echo "🐚 Opening shell in worker container..."
	$(COMPOSE_DEV) exec worker /bin/bash

# Help target
.PHONY: help
help: ## Show this help message
	@echo "CI/CD Health Dashboard Operations"
	@echo "================================="
	@echo ""
	@echo "Development:"
	@echo "  dev-up      - Start development environment"
	@echo "  dev-down    - Stop development environment"
	@echo "  dev-logs    - View development logs"
	@echo "  restart     - Restart development environment"
	@echo ""
	@echo "Production:"
	@echo "  prod-up     - Start production environment"
	@echo "  prod-down   - Stop production environment"
	@echo "  prod-logs   - View production logs"
	@echo ""
	@echo "Database & API:"
	@echo "  seed        - Seed database with sample data"
	@echo "  alert-test  - Test alert system"
	@echo ""
	@echo "Code Quality:"
	@echo "  fmt         - Format code (placeholder)"
	@echo "  lint        - Lint code (placeholder)"
	@echo ""
	@echo "Utilities:"
	@echo "  build       - Build all Docker images"
	@echo "  clean       - Clean up containers and volumes"
	@echo "  status      - Show service status"
	@echo "  logs-backend - View backend logs"
	@echo "  logs-frontend - View frontend logs"
	@echo "  logs-worker - View worker logs"
	@echo "  shell-backend - Open shell in backend container"
	@echo "  shell-worker - Open shell in worker container"
	@echo ""
	@echo "Examples:"
	@echo "  make dev-up     # Start development"
	@echo "  make seed       # Seed database"
	@echo "  make dev-logs   # View logs"
	@echo "  make clean      # Clean up everything"

# Environment file check
check-env:
	@if [ ! -f .env ]; then \
		echo "⚠️  .env file not found. Creating from example..."; \
		cp .env.example .env 2>/dev/null || echo "   No .env.example found"; \
		echo "   Please edit .env with your configuration"; \
	fi

# Pre-flight checks
dev-up: check-env
prod-up: check-env
