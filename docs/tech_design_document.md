# CI/CD Health Dashboard - Technical Design Document

## 1. High-Level Architecture

### System Components
- **Frontend**: React SPA with Tailwind CSS
- **API Gateway**: FastAPI with async support
- **Database**: SQLite (dev) → PostgreSQL (prod)
- **Worker**: Background polling service
- **Alert Engine**: Notification routing & delivery
- **Webhook Handler**: GitHub Actions integration
- **Cache**: Redis for performance optimization

### Data Flow
```mermaid
sequenceDiagram
    participant GH as GitHub Actions
    participant CF as Cloudflared Tunnel
    participant API as FastAPI Backend
    participant DB as SQLite Database
    participant SMTP as SMTP Server
    participant EMAIL as Email Recipients
    participant DASH as Dashboard Frontend

    Note over GH,EMAIL: Real CI/CD Pipeline Flow
    GH->>CF: Webhook: Workflow completed
    CF->>API: Forward webhook request
    API->>API: Authenticate request (Bearer token)
    API->>DB: Store build data
    
    alt Build Failed
        API->>SMTP: Send failure alert
        SMTP->>EMAIL: Deliver notification
    end
    
    DASH->>API: Request dashboard data
    API->>DB: Query build history
    DB->>API: Return results
    API->>DASH: JSON response with metrics
```

### Container Architecture
```mermaid
graph TB
    subgraph "External Services"
        GH[GitHub Actions<br/>Workflow Runs]
        GMAIL[Gmail SMTP<br/>gopalakrishnan.kuppan@gmail.com]
    end
    
    subgraph "Public Tunnel"
        CF[Cloudflared Tunnel<br/>hash-classroom-polls-itself.trycloudflare.com]
    end
    
    subgraph "Local Development"
        API[FastAPI Backend<br/>localhost:8000]
        DB[(SQLite Database<br/>data.db)]
        FRONTEND[Frontend Dashboard<br/>HTML/CSS/JS]
    end
    
    subgraph "Security"
        AUTH[Bearer Token Auth<br/>c1b4813cac3d12687...]
        SECRETS[Encrypted Secrets<br/>OpenSSL + secret_manager.py]
    end
    
    GH -->|Webhook POST| CF
    CF -->|Forward| API
    API -->|Store builds| DB
    API -->|Query data| DB
    API -->|Send alerts| GMAIL
    FRONTEND -->|API calls| API
    API -->|Authenticate| AUTH
    API -->|Decrypt secrets| SECRETS
```

## 2. API Design

### Base Configuration
- **Base URL**: `/api/v1`
- **Authentication**: Bearer token (JWT)
- **Rate Limiting**: 1000 req/min per user
- **Response Format**: JSON with consistent structure

### API Endpoints

#### GET /api/metrics/summary
**Purpose**: Dashboard overview metrics

**Response**:
```json
{
  "total_pipelines": 15,
  "active_pipelines": 12,
  "failed_pipelines": 2,
  "success_rate": 0.87,
  "avg_build_time": 180,
  "last_24h_runs": 45,
  "alerts": {
    "critical": 1,
    "warning": 3,
    "info": 0
  }
}
```

#### GET /api/builds?limit=20&provider=github-actions
**Purpose**: List recent workflow runs

**Query Parameters**:
- `limit`: Number of results (default: 20, max: 100)
- `provider`: CI provider filter
- `status`: Status filter (success, failed, running)
- `branch`: Branch filter
- `since`: ISO timestamp for filtering

**Response**:
```json
{
  "builds": [
    {
      "id": 123,
      "pipeline_name": "Frontend CI",
      "run_number": 42,
      "status": "success",
      "conclusion": "success",
      "start_time": "2025-08-25T10:30:00Z",
      "duration": 180,
      "commit_hash": "abc123",
      "commit_message": "feat: add dashboard",
      "author": "john.doe",
      "run_url": "https://github.com/...",
      "created_at": "2025-08-25T10:30:00Z"
    }
  ],
  "pagination": {
    "total": 156,
    "page": 1,
    "per_page": 20,
    "has_next": true
  }
}
```

#### GET /api/builds/{id}
**Purpose**: Detailed build information

**Response**:
```json
{
  "id": 123,
  "pipeline": {
    "id": 1,
    "name": "Frontend CI",
    "repository": "myorg/frontend",
    "branch": "main"
  },
  "run_number": 42,
  "status": "success",
  "conclusion": "success",
  "start_time": "2025-08-25T10:30:00Z",
  "end_time": "2025-08-25T10:33:00Z",
  "duration": 180,
  "commit_hash": "abc123",
  "commit_message": "feat: add dashboard",
  "author": "john.doe",
  "run_url": "https://github.com/...",
  "workflow_name": "CI Pipeline",
  "trigger": "push",
  "metadata": {
    "actor": "john.doe",
    "head_branch": "main",
    "base_branch": "main"
  },
  "jobs": [
    {
      "name": "Build",
      "status": "completed",
      "conclusion": "success",
      "duration": 120
    }
  ]
}
```

#### POST /api/webhook/github-actions
**Purpose**: GitHub Actions webhook endpoint

**Headers**:
- `X-GitHub-Event`: workflow_run
- `X-GitHub-Delivery`: Unique delivery ID
- `X-Hub-Signature-256`: HMAC signature

**Request Body**: GitHub webhook payload
**Response**: `{"status": "processed"}`

**Security**: Webhook signature verification required

#### POST /api/webhook/jenkins
**Purpose**: Jenkins webhook endpoint (future)

**Headers**:
- `X-Jenkins-Signature`: Jenkins signature
- `Content-Type`: application/json

**Request Body**: Jenkins webhook payload
**Response**: `{"status": "processed"}`

#### POST /api/alert/test
**Purpose**: Test alert delivery

**Request Body**:
```json
{
  "channel": "slack",
  "message": "Test alert message",
  "severity": "info"
}
```

**Response**: `{"status": "sent", "message_id": "msg_123"}`

#### POST /api/seed
**Purpose**: Seed database with sample data

**Headers**:
- `X-Seed-Key`: Required write key

**Request Body**:
```json
{
  "pipelines": [
    {
      "name": "Sample Pipeline",
      "repository": "org/repo",
      "owner": "org"
    }
  ]
}
```

**Response**: `{"status": "seeded", "count": 1}`

### Error Handling

**Standard Error Response**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "limit",
      "issue": "Value must be between 1 and 100"
    }
  },
  "timestamp": "2025-08-25T10:30:00Z",
  "request_id": "req_abc123"
}
```

**HTTP Status Codes**:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `429`: Rate Limited
- `500`: Internal Server Error

## 3. Database Schema

### SQLite-First Design

```sql
-- Core tables
CREATE TABLE pipelines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    repository TEXT NOT NULL,
    owner TEXT NOT NULL,
    branch TEXT DEFAULT 'main',
    workflow_file TEXT,
    provider TEXT DEFAULT 'github_actions',
    status TEXT DEFAULT 'unknown',
    last_run_number INTEGER,
    last_run_url TEXT,
    last_run_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workflow_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_id INTEGER NOT NULL,
    run_number INTEGER NOT NULL,
    run_id TEXT NOT NULL,
    status TEXT NOT NULL,
    conclusion TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration INTEGER,
    commit_hash TEXT,
    commit_message TEXT,
    author TEXT,
    run_url TEXT,
    workflow_name TEXT,
    trigger TEXT,
    metadata TEXT, -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pipeline_id) REFERENCES pipelines(id)
);

CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_id INTEGER,
    type TEXT NOT NULL,
    message TEXT NOT NULL,
    severity TEXT DEFAULT 'medium',
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (pipeline_id) REFERENCES pipelines(id)
);

CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_pipelines_repository ON pipelines(repository);
CREATE INDEX idx_workflow_runs_pipeline ON workflow_runs(pipeline_id);
CREATE INDEX idx_workflow_runs_status ON workflow_runs(status);
CREATE INDEX idx_workflow_runs_created ON workflow_runs(created_at);
CREATE INDEX idx_alerts_pipeline ON alerts(pipeline_id);
CREATE INDEX idx_alerts_active ON alerts(is_active, severity);

-- Triggers for updated_at
CREATE TRIGGER update_pipelines_timestamp 
    AFTER UPDATE ON pipelines
    BEGIN
        UPDATE pipelines SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;
```

## 4. Alerting Logic

### Alert Conditions
- **Pipeline Failure**: Workflow run fails
- **Slow Build**: Duration > threshold (configurable)
- **Pipeline Down**: No successful runs in 24h
- **High Failure Rate**: >20% failure rate in 24h

### Deduplication
- **Window**: 5 minutes for same pipeline + condition
- **Key**: `{pipeline_id}:{alert_type}:{hash(message)}`
- **Storage**: Redis with TTL

### Notification Channels

#### Slack
```python
async def send_slack_alert(alert: Alert, pipeline: Pipeline):
    webhook_url = settings.get("slack_webhook_url")
    message = {
        "text": f"🚨 {alert.type.upper()}: {pipeline.name}",
        "attachments": [{
            "fields": [
                {"title": "Pipeline", "value": pipeline.name, "short": True},
                {"title": "Repository", "value": pipeline.repository, "short": True},
                {"title": "Message", "value": alert.message, "short": False}
            ],
            "color": get_severity_color(alert.severity)
        }]
    }
    await http_client.post(webhook_url, json=message)
```

#### Email
```python
async def send_email_alert(alert: Alert, pipeline: Pipeline):
    smtp_config = {
        "host": settings.get("smtp_host"),
        "port": settings.get("smtp_port"),
        "username": settings.get("smtp_username"),
        "password": settings.get("smtp_password")
    }
    
    subject = f"[{alert.severity.upper()}] {alert.type}: {pipeline.name}"
    body = f"""
    Pipeline: {pipeline.name}
    Repository: {pipeline.repository}
    Message: {alert.message}
    Time: {alert.created_at}
    """
    
    await send_email(smtp_config, subject, body)
```

## 5. UI Layout Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│ Dashboard - CI/CD Health Overview                    [User] [⚙️] │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ Total       │ │ Success     │ │ Failed      │ │ Avg Build   │ │
│ │ Pipelines   │ │ Rate        │ │ Pipelines  │ │ Time        │ │
│ │    15       │ │    87%      │ │     2      │ │   3m 0s     │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Pipeline Status Chart (Last 7 Days)                        │ │
│ │ ████████████████████████████████████████████████████████████ │ │
│ │ Success: ████ Failed: ██ Running: ██                       │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ Latest Workflow Runs                    [View All] [Refresh]   │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Pipeline    │ Status │ Duration │ Commit    │ Author │ Time │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ Frontend CI │ ✅     │ 3m 0s   │ abc123    │ John   │ 1h   │ │
│ │ Backend API │ ✅     │ 1m 30s  │ def456    │ Jane   │ 30m  │ │
│ │ Mobile App  │ 🔄     │ --      │ ghi789    │ Bob    │ 15m  │ │
│ │ Infra       │ ❌     │ 10m     │ jkl012    │ Alice  │ 2h   │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ Active Alerts                                                    │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 🚨 Infrastructure pipeline failed (2h ago) [Acknowledge]   │ │
│ │ ⚠️ Mobile app pipeline slow (15m running) [Acknowledge]   │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

[Log Viewer Drawer - Right Side]
┌─────────────────────────────────────────────────────────────────┐
│ Workflow Run Logs - Frontend CI #42                            │
├─────────────────────────────────────────────────────────────────┤
│ 2025-08-25 10:30:00 INFO  Starting workflow                   │
│ 2025-08-25 10:30:05 INFO  Checking out code                  │
│ 2025-08-25 10:30:10 INFO  Installing dependencies            │
│ 2025-08-25 10:31:00 INFO  Running tests                      │
│ 2025-08-25 10:32:00 INFO  Building application              │
│ 2025-08-25 10:33:00 INFO  Workflow completed successfully   │
└─────────────────────────────────────────────────────────────────┘
```

## 6. Deployment

### Docker Compose - Development

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: ops/docker/backend.Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./dev.db
      - DEBUG=true
    volumes:
      - ./backend:/app
      - ./dev.db:/app/dev.db
    depends_on:
      - redis

  frontend:
    build:
      context: ./frontend
      dockerfile: ops/docker/frontend.Dockerfile
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules

  worker:
    build:
      context: .
      dockerfile: ops/docker/worker.Dockerfile
    environment:
      - DATABASE_URL=sqlite:///./dev.db
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./worker:/app
      - ./dev.db:/app/dev.db
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### Docker Compose - Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: ops/docker/backend.Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - DEBUG=false
    depends_on:
      - postgres
      - redis
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  frontend:
    build:
      context: ./frontend
      dockerfile: ops/docker/frontend.Dockerfile
    ports:
      - "80:80"
    environment:
      - VITE_API_BASE_URL=${API_BASE_URL}

  worker:
    build:
      context: .
      dockerfile: ops/docker/worker.Dockerfile
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - postgres
      - redis
    deploy:
      replicas: 3

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          memory: 1G

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    deploy:
      resources:
        limits:
          memory: 256M

volumes:
  postgres_data:
  redis_data:
```

### Environment Variables

```bash
# .env.production
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/cicd_dashboard
REDIS_URL=redis://redis:6379
API_BASE_URL=https://api.example.com
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxx
GITHUB_WEBHOOK_SECRET=webhook_secret_here
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=alerts@company.com
SMTP_PASSWORD=app_password_here
```

### Scale Knobs

- **Backend**: 2-10 replicas based on load
- **Worker**: 3-8 replicas based on pipeline count
- **Database**: Connection pooling (20-100 connections)
- **Redis**: 1-3 replicas with persistence
- **Frontend**: CDN + load balancer for high traffic

## 7. Security, Hardening & Compliance

### Request Hardening
- **Body size guard**: Requests larger than ~1 MB are rejected with HTTP 413. Configurable via `MAX_BODY_BYTES` (default 1,048,576 bytes).
- **CORS**: Only the configured frontend origin is allowed. Set `FRONTEND_ORIGIN` (default `http://localhost:5173`). `allow_credentials`, `allow_methods`, and `allow_headers` are enabled for app needs.
- **Naive rate limiting**: 60 requests/minute per client IP using an in-memory sliding window. Exceeding the limit returns HTTP 429. Suitable for single-instance deployments; for multi-instance production, replace with a shared store (e.g., Redis) or a gateway-level limiter.

### Authentication & Authorization
- **Write endpoints**: `POST /api/webhook/github-actions`, `POST /api/seed`, and `POST /api/alert/test` enforce `X-API-KEY` when `Settings.api_write_key` is configured. If the key is not set (demo mode), these endpoints allow requests without a key, aiding local demos.
- **Header name**: `X-API-KEY`
- **Storage**: The write key is stored in the `settings` table (`id=1`) under `api_write_key`.

### Secrets Handling & Logging
- **Log redaction**: Sensitive tokens/keys must never be logged in full. When logging, only the last 4 characters are retained (e.g., `***abcd`).
- **Environment variables**: SMTP credentials are read from env (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`). Avoid printing these values; mask if required for diagnostics.

### Transport & Deployment
- **TLS**: Terminate TLS at the ingress/reverse-proxy (e.g., Nginx). Ensure `BACKEND_URL` uses `https://` in production.
- **Containers**: Run as non-root, minimal base images, health checks in Dockerfiles.

### Abuse & DoS Considerations
- **Body-limit rejection** reduces memory pressure from oversized payloads.
- **Rate limiter** mitigates burst traffic at the app-level. For stronger protection, deploy a WAF/reverse-proxy limiter.

### Data Protection
- **PII**: The system stores CI metadata only. No passwords or personal data beyond usernames/emails in commits.
- **Backups**: Ensure volume-mounted SQLite file is backed up in production environments (or use PostgreSQL).

### Operational Notes
- **Scaling the limiter**: Replace the in-memory limiter with Redis or gateway-limits when horizontally scaling.
- **Webhook security**: Optionally add HMAC verification for GitHub webhook payloads in future iterations.
- **Configuration**: Key environment variables – `FRONTEND_ORIGIN`, `MAX_BODY_BYTES`, SMTP vars, and the database URL.
