# CI/CD Health Dashboard - Worker

Background worker service that polls CI/CD providers and updates the dashboard via API calls.

## Features

- **GitHub Actions Polling**: Polls recent workflow runs via REST API
- **Jenkins Polling**: Queries Jenkins API for recent builds
- **Configurable Polling**: Environment-based provider enabling
- **Thundering Herd Protection**: Jitter to avoid synchronized polling
- **Robust Error Handling**: Continues operation on individual failures
- **API Integration**: Updates dashboard via webhook endpoints

## Quick Start

### Prerequisites

- Python 3.9+
- Access to CI/CD providers (GitHub, Jenkins)
- Dashboard API running

### Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**
   ```bash
   # Copy and edit the example
   cp .env.example .env
   ```

3. **Run the worker**
   ```bash
   # Option 1: Direct module execution
   python -m scheduler
   
   # Option 2: Simple entry point
   python run_scheduler.py
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_GH` | Enable GitHub Actions polling | `true` |
| `ENABLE_JENKINS` | Enable Jenkins polling | `false` |
| `WORKER_POLL_INTERVAL` | Polling interval in seconds | `60` |
| `WORKER_JITTER_SECONDS` | Jitter to avoid thundering herd | `10` |

#### GitHub Actions Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub personal access token | Yes |
| `GITHUB_REPOS` | Comma-separated owner/repo pairs | No* |
| `GITHUB_OWNER` | Default GitHub owner | No* |
| `GITHUB_REPO` | Default GitHub repository | No* |

*If `GITHUB_REPOS` is not set, falls back to `GITHUB_OWNER`/`GITHUB_REPO`

#### Jenkins Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `JENKINS_URL` | Jenkins server URL | Yes |
| `JENKINS_USERNAME` | Jenkins username | Yes |
| `JENKINS_API_TOKEN` | Jenkins API token | Yes |
| `JENKINS_JOBS` | Comma-separated job names | No* |
| `JENKINS_DEFAULT_JOB` | Default Jenkins job | No* |

*If `JENKINS_JOBS` is not set, falls back to `JENKINS_DEFAULT_JOB`

#### Dashboard API Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DASHBOARD_API_URL` | Dashboard API base URL | `http://localhost:8000` |
| `DASHBOARD_API_KEY` | Dashboard API write key | `dev-write-key-change-in-production` |

### Example Configuration

```bash
# Enable providers
ENABLE_GH=true
ENABLE_JENKINS=false

# Polling configuration
WORKER_POLL_INTERVAL=60
WORKER_JITTER_SECONDS=10

# GitHub Actions
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPOS=myorg/frontend-app,myorg/backend-api,myorg/infrastructure

# Jenkins (if enabled)
JENKINS_URL=http://jenkins.company.com
JENKINS_USERNAME=jenkins-user
JENKINS_API_TOKEN=your_api_token
JENKINS_JOBS=myapp-pipeline,database-migrations

# Dashboard API
DASHBOARD_API_URL=http://localhost:8000
DASHBOARD_API_KEY=your-secure-api-key
```

## Architecture

### Components

1. **CICDPoller**: Handles individual provider polling
2. **WorkerScheduler**: Manages polling schedule and execution
3. **HTTP Client**: Makes API calls to providers and dashboard

### Polling Flow

1. **Scheduler** triggers polling cycle every N seconds
2. **Poller** queries enabled providers for recent activity
3. **Data Processing** converts provider data to webhook format
4. **API Update** sends webhook payloads to dashboard API
5. **Error Handling** logs failures and continues operation

### Provider Integration

#### GitHub Actions
- Polls `/repos/{owner}/{repo}/actions/runs` endpoint
- Gets workflow runs from last 24 hours
- Maps to webhook payload format
- Sends via `/api/webhook/github-actions`

#### Jenkins
- Queries `/job/{job_name}/api/json` for job info
- Gets detailed build info from `/job/{job_name}/{build_number}/api/json`
- Maps to webhook payload format
- Sends via `/api/webhook/jenkins`

## Usage

### Running the Worker

```bash
# Start the worker scheduler
python run_scheduler.py

# Or run as a module
python -m scheduler
```

### Testing Individual Components

```bash
# Test poller directly
python -c "
import asyncio
from poller import CICDPoller

async def test():
    poller = CICDPoller()
    await poller.poll_all_providers()
    await poller.close()

asyncio.run(test())
"
```

### Logging

The worker logs all operations with timestamps:

```
2024-01-15 17:30:00 - __main__ - INFO - Starting CI/CD Worker Scheduler
2024-01-15 17:30:00 - __main__ - INFO - Poll interval: 60 seconds
2024-01-15 17:30:00 - __main__ - INFO - GitHub Actions enabled: true
2024-01-15 17:30:00 - __main__ - INFO - Jenkins enabled: false
2024-01-15 17:30:00 - __main__ - INFO - Added polling job with 60s interval and 5s jitter
2024-01-15 17:30:00 - __main__ - INFO - Scheduler started successfully
```

## Error Handling

### Individual Failures
- Provider API failures don't stop other providers
- Dashboard API failures are logged but don't stop polling
- Network timeouts use exponential backoff with retry

### Scheduler Failures
- Job execution errors are logged with full tracebacks
- Scheduler continues running despite individual job failures
- Graceful shutdown on SIGINT/SIGTERM

### Recovery
- Failed API calls use tenacity retry logic
- Exponential backoff prevents overwhelming failed services
- Jitter prevents synchronized failures across multiple workers

## Production Deployment

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "run_scheduler.py"]
```

### Systemd Service

```ini
[Unit]
Description=CI/CD Health Dashboard Worker
After=network.target

[Service]
Type=simple
User=cicd-worker
WorkingDirectory=/opt/cicd-worker
EnvironmentFile=/etc/cicd-worker/env
ExecStart=/usr/bin/python3 run_scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Environment File

```bash
# /etc/cicd-worker/env
ENABLE_GH=true
ENABLE_JENKINS=false
WORKER_POLL_INTERVAL=60
GITHUB_TOKEN=ghp_production_token
DASHBOARD_API_URL=https://dashboard.company.com
DASHBOARD_API_KEY=production_api_key
```

## Monitoring

### Health Checks
- Worker logs successful polling cycles
- Failed cycles are logged with error details
- Scheduler status can be monitored via logs

### Metrics
- Polling frequency and success rates
- API response times and failure counts
- Provider-specific error rates

### Alerts
- Failed polling cycles
- Dashboard API connectivity issues
- Provider authentication failures
