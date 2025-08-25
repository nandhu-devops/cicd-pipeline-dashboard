# CI/CD Health Dashboard - Backend

FastAPI backend service for the CI/CD Health Dashboard with SQLite support and comprehensive GitHub Actions monitoring.

## Features

- **Real-time Monitoring**: GitHub Actions webhook processing
- **Metrics Dashboard**: Success rates, build times, and pipeline health
- **Email Alert System**: Automatic alerts for failed builds with debouncing
- **SQLite First**: Local development with SQLite, production-ready for PostgreSQL
- **API Security**: Write operations protected with API keys
- **Comprehensive Testing**: Full test coverage for all endpoints

## Quick Start

### Prerequisites

- Python 3.9+
- SQLite (included with Python)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cicd-health-dashboard/backend
   ```

2. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -e .
   ```

3. **Configure environment variables**
   ```bash
   # Copy and edit the example
   cp .env.example .env
   ```

4. **Initialize database**
   ```bash
   python init_db.py
   ```

5. **Run the application**
   ```bash
   # Development
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Or directly
   python -m app.main
   ```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite+aiosqlite:///./data.db` |
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |
| `DEBUG` | Enable debug mode | `false` |
| `ALERTS_ENABLED` | Enable/disable email alerts | `true` |
| `SMTP_HOST` | SMTP server hostname | Required |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USERNAME` | SMTP username/email | Required |
| `SMTP_PASSWORD` | SMTP password or app password | Required |

## API Endpoints

### Public Endpoints
- `GET /health` - Health check
- `GET /api/metrics/summary` - Dashboard metrics
- `GET /api/builds` - List builds with pagination
- `GET /api/builds/{id}` - Build details
- `POST /api/webhook/github-actions` - GitHub Actions webhook

### Protected Endpoints (Require X-API-KEY header)
- `POST /api/alert/test` - Test email alert delivery
- `POST /api/seed` - Seed database with sample data

### Default API Key
For development, the default API key is: `dev-write-key-change-in-production`

## Database Schema

### Core Tables
- **providers**: GitHub Actions repository configuration
- **builds**: Workflow run information with status tracking
- **alerts**: Alert history and delivery status (prevents duplicate alerts)
- **settings**: Application configuration and API keys

### Indexes
- `idx_builds_status_started`: Performance for status queries
- `idx_builds_provider_finished`: Provider-specific queries
- `idx_builds_external_id`: External ID lookups

## Webhook Integration

### GitHub Actions
Accepts `workflow_run` events and automatically:
- Creates/updates providers for repositories
- Tracks workflow runs with detailed metadata
- Calculates build duration from start/end times
- Stores raw payload for debugging and analysis
- Supports all workflow statuses: success, failed, running, queued
- **Triggers automatic email alerts for failed builds**

### Webhook Payload Parsing
The system includes a comprehensive parser that extracts:
- **Build Information**: ID, status, duration, branch, commit SHA
- **Timing Data**: Start time, end time, duration in seconds
- **Repository Details**: Owner, repository name, workflow name
- **Trigger Information**: Event type, actor, pull request details
- **Metadata**: Run number, workflow ID, conclusion status

## Alert System

### Automatic Build Failure Alerts
- **Trigger**: Any newly stored build with status 'failed' and finished_at set
- **Debouncing**: Prevents duplicate alerts for the same build ID & channel
- **Email Format**: Professional email with build details and failure information
- **Non-blocking**: Alert failures don't crash the webhook processing pipeline

### Email Configuration
Email alerts require the following environment variables:
- `ALERTS_ENABLED`: Set to 'true' or 'false' to enable/disable alerts
- `SMTP_HOST`: SMTP server hostname
- `SMTP_PORT`: SMTP server port (typically 587 for TLS)
- `SMTP_USERNAME`: SMTP username/email
- `SMTP_PASSWORD`: SMTP password or app password

### Alert Content
**Subject**: `[CI/CD] Build FAILED: {provider} #{external_id}`

**Body**:
```
Build FAILED

Provider: github-myorg/frontend-app
Build ID: #123456790
Branch: feature/new-component
Duration: 120 seconds
URL: https://github.com/myorg/frontend-app/actions/runs/123456790

This is an automated alert from the CI/CD Health Dashboard.
```

### SMTP Configuration Examples

#### Gmail
```bash
ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=alerts@company.com
SMTP_PASSWORD=your-app-password  # Use App Password, not regular password
```

#### Outlook/Office 365
```bash
ALERTS_ENABLED=true
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=alerts@company.com
SMTP_PASSWORD=your-password
```

#### Custom SMTP Server
```bash
ALERTS_ENABLED=true
SMTP_HOST=mail.company.com
SMTP_PORT=587
SMTP_USERNAME=alerts@company.com
SMTP_PASSWORD=your-password
```

## Development

### Running Tests
```bash
pytest
```

### Database Initialization
```bash
python init_db.py
```

### Code Formatting
```bash
black .
isort .
```

### Type Checking
```bash
mypy .
```

## Production Deployment

### Database Migration
The application is designed to work with both SQLite and PostgreSQL:

```python
# Development (SQLite)
DATABASE_URL=sqlite+aiosqlite:///./data.db

# Production (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
```

### Environment Configuration
```bash
# Production settings
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/cicd_dashboard
DEBUG=false
API_WRITE_KEY=your-secure-production-key
ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=alerts@company.com
SMTP_PASSWORD=app_password
```

## Architecture

The backend follows a clean, async-first architecture focused on GitHub Actions:

- **Models**: SQLAlchemy ORM with proper relationships
- **Schemas**: Pydantic validation and serialization
- **Dependencies**: FastAPI dependency injection
- **Alerts**: Non-blocking email notification system with debouncing
- **Webhooks**: Real-time GitHub Actions integration with automatic alerting
- **Providers**: GitHub Actions-specific data parsing and normalization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request
