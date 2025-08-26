# 🚀 CI/CD Health Dashboard

## 🚀 Features

- **Real-time Pipeline Monitoring**: Track success/failure rates, build times, and status
- **Comprehensive Metrics**: Success rate, failure rate, average build time, last build status
- **Alert System**: Slack and email notifications for pipeline failures
- **Modern UI**: Responsive dashboard with real-time updates
- **Multi-Provider Support**: GitHub Actions, Jenkins, and extensible for other tools

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **SQLite**: Lightweight database for development (configurable for production)
- **Async Support**: Full async/await support for high performance

### Frontend (Vanilla JavaScript)
- **Pure JavaScript**: No framework dependencies, lightweight and fast
- **Responsive Design**: Mobile-first approach with CSS Grid and Flexbox
- **Real-time Updates**: WebSocket-like polling for live data
- **Modern UI**: Clean, professional interface with status indicators

### Database Schema
- **Providers**: CI/CD tool configurations
- **Builds**: Pipeline execution records
- **Alerts**: Notification history and settings
- **Metrics**: Aggregated performance data

## 🛠️ Tech Stack

- **Backend**: Python 3.8+, FastAPI, SQLAlchemy, SQLite
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Alerting**: Slack webhooks, SMTP email
- **Deployment**: Docker containerization

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- pip or uv package manager
- Modern web browser

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cicd-health-dashboard
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize database**
   ```bash
   cd backend
   python init_db.py
   ```

5. **Start the backend**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Open the frontend**
   - Navigate to `frontend/` directory
   - Open `index.html` in your browser
   - Or serve with a simple HTTP server: `python -m http.server 8080`

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite:///./data.db

# Frontend Origin (for CORS)
FRONTEND_ORIGIN=http://localhost:8080

# Alert Configuration
SLACK_WEBHOOK_URL=your_slack_webhook_url
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Security
WRITE_KEY=your_secret_write_key
```

### Alert Setup
1. **Slack**: Create a webhook in your Slack workspace
2. **Email**: Configure SMTP settings for your email provider

## 📊 API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `GET /api/metrics/summary` - Dashboard metrics
- `GET /api/builds` - List of builds
- `GET /api/builds/{build_id}` - Build details
- `POST /api/webhook/github-actions` - GitHub webhook receiver
- `POST /api/webhook/jenkins` - Jenkins webhook receiver

### Alert Endpoints
- `POST /api/alert/test` - Test alert delivery
- `GET /api/alerts` - Alert history
- `POST /api/alerts/configure` - Configure alert settings

## 🎨 Frontend Components

### Dashboard Layout
- **Header**: Title and refresh button
- **Summary Cards**: Key metrics display
- **Builds Table**: Recent pipeline executions
- **Status Indicators**: Color-coded build statuses
- **Responsive Design**: Mobile and desktop optimized

### Real-time Features
- **Auto-refresh**: Configurable polling intervals
- **Live Updates**: Real-time status changes
- **Error Handling**: Graceful failure states
- **Loading States**: User feedback during operations

## 🚢 Deployment

### Docker
```bash
# Build the image
docker build -t cicd-dashboard .

# Run the container
docker run -p 8000:8000 -p 8080:8080 cicd-dashboard
```

### Production Considerations
- Use PostgreSQL instead of SQLite
- Configure proper CORS origins
- Set up reverse proxy (nginx)
- Enable HTTPS
- Configure monitoring and logging

## 🔍 Monitoring & Observability

### Built-in Metrics
- Request/response times
- Database query performance
- Error rates and types
- Alert delivery success rates

### Health Checks
- Database connectivity
- External service availability
- Alert service status
- Overall system health
