# CI/CD Health Dashboard - Technical Design Document

## 🏗️ System Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CI/CD Tools   │    │   Dashboard     │    │   Alerting      │
│                 │    │   Backend       │    │   Services      │
│ • GitHub Actions│◄──►│ • FastAPI       │◄──►│ • Email (SMTP)  │
│ • Jenkins       │    │ • SQLAlchemy    │    │ • Slack Webhook │
│ • GitLab CI     │    │ • SQLite/PostgreSQL│ │ • Webhooks      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Frontend      │
                       │ • HTML5/CSS3    │
                       │ • Vanilla JS    │
                       │ • Responsive    │
                       └─────────────────┘
```

### Component Architecture
1. **Backend API Layer**: FastAPI application with async support
2. **Data Layer**: SQLAlchemy ORM with database abstraction
3. **Integration Layer**: Webhook handlers and provider adapters
4. **Alerting Layer**: Multi-channel notification system
5. **Frontend Layer**: Static HTML with JavaScript for interactivity

## 🗄️ Database Design

### Entity Relationship Diagram
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Provider   │    │    Build    │    │    Alert    │
│             │    │             │    │             │
│ • id (PK)   │◄───│ • provider_id│   │ • id (PK)   │
│ • name      │    │ • external_id│   │ • type      │
│ • kind      │    │ • status    │    │ • config    │
│ • config    │    │ • branch    │    │ • is_active │
│ • is_active │    │ • duration  │    └─────────────┘
└─────────────┘    │ • started_at│
                   │ • finished_at│
                   └─────────────┘
```

### Database Schema

#### Providers Table
```sql
CREATE TABLE providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    kind VARCHAR(50) NOT NULL,
    config_json JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Builds Table
```sql
CREATE TABLE builds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id VARCHAR(255) NOT NULL,
    provider_id INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,
    branch VARCHAR(100),
    commit_sha VARCHAR(100),
    triggered_by VARCHAR(255),
    url TEXT,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    duration_seconds FLOAT,
    raw_payload JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES providers(id),
    INDEX idx_builds_status (status),
    INDEX idx_builds_started (started_at),
    INDEX idx_builds_provider (provider_id)
);
```

#### Alerts Table
```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    config_json JSON NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Alert History Table
```sql
CREATE TABLE alert_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id INTEGER NOT NULL,
    build_id INTEGER,
    message TEXT NOT NULL,
    severity VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alert_id) REFERENCES alerts(id),
    FOREIGN KEY (build_id) REFERENCES builds(id)
);
```

## 🔌 API Design

### RESTful Endpoints

#### Core Endpoints
```
GET    /health                    # Health check
GET    /api/metrics/summary      # Dashboard metrics
GET    /api/builds               # List builds with pagination
GET    /api/builds/{id}          # Get specific build
POST   /api/webhook/github-actions # GitHub webhook
POST   /api/webhook/jenkins      # Jenkins webhook
POST   /api/alert/test           # Test alert delivery
POST   /api/seed                 # Seed database with sample data
```

#### API Response Models

##### Metrics Summary
```json
{
    "window_days": 7,
    "success_rate": 0.85,
    "failure_rate": 0.15,
    "avg_build_time_seconds": 180.5,
    "last_build_status": "success",
    "last_updated": "2024-01-15T10:30:00Z"
}
```

##### Build List Response
```json
{
    "builds": [
        {
            "id": 1,
            "external_id": "123456789",
            "status": "success",
            "branch": "main",
            "commit_sha": "abc123def456",
            "triggered_by": "john_doe",
            "url": "https://github.com/repo/actions/runs/123456789",
            "started_at": "2024-01-15T10:00:00Z",
            "finished_at": "2024-01-15T10:03:00Z",
            "duration_seconds": 180,
            "provider_name": "GitHub Actions",
            "provider_kind": "github_actions"
        }
    ],
    "total": 100,
    "limit": 50,
    "offset": 0,
    "has_more": true
}
```

### Webhook Integration

#### GitHub Actions Webhook
```json
{
    "workflow_run": {
        "id": 123456789,
        "name": "CI Pipeline",
        "status": "completed",
        "conclusion": "success",
        "run_started_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:03:00Z",
        "head_branch": "main",
        "head_commit": {
            "id": "abc123def456",
            "message": "feat: add new feature"
        },
        "triggering_actor": {
            "login": "john_doe"
        },
        "html_url": "https://github.com/repo/actions/runs/123456789"
    },
    "workflow": {
        "name": "CI Pipeline"
    },
    "repository": {
        "full_name": "owner/repo"
    },
    "sender": {
        "login": "john_doe"
    }
}
```

#### Jenkins Webhook
```json
{
    "name": "Build Pipeline",
    "url": "http://jenkins.example.com/job/Build%20Pipeline/",
    "build": {
        "number": 123,
        "status": "SUCCESS",
        "branch": "main",
        "commit": "abc123def456",
        "user": "jenkins_user",
        "url": "http://jenkins.example.com/job/Build%20Pipeline/123/"
    },
    "timestamp": 1705312800000
}
```

## 🎨 Frontend Architecture

### Component Structure
```
Dashboard
├── Header
│   ├── Title
│   └── Refresh Button
├── Summary Cards
│   ├── Success Rate
│   ├── Failure Rate
│   ├── Average Build Time
│   └── Last Build Status
├── Builds Table
│   ├── Status Column
│   ├── Build ID Column
│   ├── Branch Column
│   ├── Duration Column
│   ├── Started Column
│   └── Actions Column
└── Error States
    ├── Loading State
    ├── Error State
    └── Empty State
```

### JavaScript Architecture
```javascript
// Main dashboard controller
class DashboardController {
    constructor() {
        this.apiBase = 'http://localhost:8000';
        this.currentData = null;
        this.autoRefreshInterval = null;
    }
    
    async loadDashboard() {
        // Load metrics and builds
    }
    
    updateMetrics(metrics) {
        // Update summary cards
    }
    
    updateBuildsTable(builds) {
        // Update builds table
    }
    
    startAutoRefresh() {
        // Start auto-refresh timer
    }
}

// API service layer
class ApiService {
    async fetchMetrics() {
        // Fetch metrics from API
    }
    
    async fetchBuilds() {
        // Fetch builds from API
    }
    
    async testAlert(alertData) {
        // Test alert delivery
    }
}
```

### CSS Architecture
```css
/* Base styles and reset */
/* Layout components (header, cards, table) */
/* Status indicators and badges */
/* Responsive design breakpoints */
/* Animation and transitions */
/* Utility classes */
```

## 🔔 Alert System Design

### Alert Flow
```
Build Event → Alert Trigger → Alert Service → Channel Selection → Delivery
     │              │              │              │              │
     ▼              ▼              ▼              ▼              ▼
Webhook      Rule Evaluation   Alert Creation   Email/Slack   Success/Failure
Received     (Failure, Time)   (Message, Data)  Selection     Logging
```

### Alert Configuration
```json
{
    "email": {
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "alerts@company.com",
        "password": "app_password",
        "from_email": "alerts@company.com",
        "from_name": "CI/CD Dashboard"
    },
    "slack": {
        "webhook_url": "https://hooks.slack.com/services/...",
        "channel": "#alerts",
        "username": "CI/CD Bot"
    }
}
```

### Alert Rules
```python
class AlertRule:
    def __init__(self, condition, severity, channels):
        self.condition = condition      # Build status == "failed"
        self.severity = severity        # "error", "warning", "info"
        self.channels = channels        # ["email", "slack"]
    
    def evaluate(self, build):
        # Evaluate if alert should be triggered
        pass
```

## 🚀 Deployment Architecture

### Docker Containerization
```dockerfile
# Multi-stage build
FROM python:3.11-slim as backend
# Backend dependencies and code

FROM nginx:alpine as frontend
# Frontend static files

FROM python:3.11-slim as production
# Combined production image
```

### Production Deployment
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Web Server    │    │   Application   │
│   (nginx)       │◄──►│   (nginx)       │◄──►│   (FastAPI)     │
│                 │    │                 │    │                 │
│ • SSL/TLS       │    │ • Static Files  │    │ • API Endpoints │
│ • Rate Limiting │    │ • API Proxy     │    │ • Database      │
│ • Health Checks │    │ • Caching       │    │ • Background    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Environment Configuration
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# Server
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Frontend
FRONTEND_ORIGIN=https://dashboard.company.com

# Security
SECRET_KEY=your-secret-key
WRITE_KEY=your-write-key

# Alerts
ALERTS_ENABLED=true
SLACK_WEBHOOK_URL=your_slack_webhook
SMTP_HOST=smtp.company.com
SMTP_USERNAME=alerts@company.com
SMTP_PASSWORD=your_password
```

## 📊 Performance Considerations

### Database Optimization
- **Indexing**: Strategic indexes on frequently queried columns
- **Query Optimization**: Efficient SQL queries with proper joins
- **Connection Pooling**: Database connection management
- **Caching**: Redis integration for frequently accessed data

### API Performance
- **Async Processing**: Non-blocking I/O operations
- **Response Caching**: HTTP response caching headers
- **Compression**: Gzip compression for API responses
- **Pagination**: Efficient data pagination for large datasets

### Frontend Performance
- **Asset Optimization**: Minified CSS and JavaScript
- **Image Optimization**: Compressed and optimized images
- **Lazy Loading**: Deferred loading of non-critical resources
- **Caching**: Browser caching for static assets

## 🔒 Security Design

### Authentication & Authorization
```python
# API key verification
async def verify_write_key(request: Request):
    api_key = request.headers.get("X-API-KEY")
    if not api_key or api_key != settings.WRITE_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return True
```

### Input Validation
```python
# Pydantic models for request validation
class GitHubWebhookPayload(BaseModel):
    workflow_run: Dict[str, Any]
    workflow: Dict[str, Any]
    repository: Dict[str, Any]
    sender: Dict[str, Any]
```

### CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

## 📈 Monitoring & Observability

### Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "ok": True,
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "database": "connected",
        "alerts": "active"
    }
```

### Metrics Collection
- **Request/Response Times**: API performance monitoring
- **Error Rates**: Failure tracking and alerting
- **Database Performance**: Query execution times
- **System Resources**: CPU, memory, and disk usage

### Logging Strategy
```python
import logging

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Build processed", extra={
    "build_id": build.id,
    "status": build.status,
    "provider": build.provider.name
})
```

## 🧪 Testing Strategy

### Backend Testing
```python
# Unit tests
def test_metrics_calculation():
    # Test metrics calculation logic
    
# Integration tests
async def test_webhook_processing():
    # Test webhook endpoint
    
# Performance tests
async def test_concurrent_requests():
    # Test system under load
```

### Frontend Testing
- **Cross-browser Testing**: Chrome, Firefox, Safari, Edge
- **Mobile Testing**: Responsive design validation
- **User Acceptance Testing**: End-to-end workflow testing
- **Performance Testing**: Load time and responsiveness

## 🔄 CI/CD Integration

### Build Pipeline
```yaml
# GitHub Actions workflow
name: CI/CD Dashboard Build
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest tests/
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker image
        run: docker build -t cicd-dashboard .
```

### Deployment Pipeline
```yaml
# Deployment workflow
name: Deploy Dashboard
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Deployment commands
```

---

*This technical design document provides the architectural foundation for implementing the CI/CD Health Dashboard with modern best practices and scalable design patterns.*
