# 🚀 CI/CD Health Dashboard - Complete Setup Guide

## 📋 Prerequisites

- Python 3.11+ installed
- Git repository with GitHub Actions enabled
- Docker (optional, for containerized deployment)

## 🔧 Step-by-Step Setup

### 1. Environment Configuration ✅
```bash
# Run the configuration script (already done)
./setup_config.sh
```

**Generated Secrets:**
- `WRITE_KEY`: `6edea10ca953ae30c13cf44efb3b7f6a`
- `SECRET_KEY`: `784488fb089ac79f293355ed8003ba13179fdfddaa670b0f5b3f135d911d28f3`

### 2. Start the Dashboard Backend
```bash
# Activate virtual environment
source .venv/bin/activate

# Start the backend server
python run_server.py
```

**Expected Output:**
```
🚀 Starting CI/CD Health Dashboard...
Creating database tables...
✅ Database tables created successfully
📋 Tables created: ['alert_history', 'alerts', 'builds', 'metrics', 'providers', 'settings']
✅ Database initialized
INFO: Application startup complete.
```

### 3. Expose Dashboard to Internet (ngrok)
```bash
# In a new terminal window
ngrok http 8000
```

**Copy the HTTPS URL** (e.g., `https://abcd-1234.ngrok-free.app`)

### 4. Configure GitHub Repository Secrets

Go to your GitHub repository:
1. **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**

**Required Secrets:**

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `DASHBOARD_WEBHOOK_URL` | `https://your-ngrok-url/api/webhook/github-actions` | Public dashboard URL |
| `DASHBOARD_WRITE_KEY` | `6edea10ca953ae30c13cf44efb3b7f6a` | Authentication token |

### 5. Test the Setup

#### Test Backend Health
```bash
curl http://localhost:8000/health
```

#### Test API Endpoints
```bash
# Metrics summary
curl http://localhost:8000/api/metrics/summary

# Builds list
curl http://localhost:8000/api/builds

# Test webhook (replace with your actual WRITE_KEY)
curl -X POST http://localhost:8000/api/webhook/github-actions \
  -H "Authorization: Bearer 6edea10ca953ae30c13cf44efb3b7f6a" \
  -H "Content-Type: application/json" \
  -d '{"test": "webhook"}'
```

### 6. Trigger GitHub Actions

Make a commit and push to trigger the workflow:
```bash
git add .
git commit -m "test: trigger CI/CD pipeline"
git push
```

**Expected Result:** Dashboard shows new build data in real-time.

## 🌐 Access Points

- **Frontend Dashboard**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Public Webhook URL**: https://your-ngrok-url/api/webhook/github-actions

## 🔍 Troubleshooting

### Dashboard Not Loading
```bash
# Check backend status
curl http://localhost:8000/health

# Check logs
tail -f logs/dashboard.log

# Restart backend
pkill -f 'run_server.py'
python run_server.py
```

### Webhook Not Working
1. Verify `DASHBOARD_WRITE_KEY` matches in both GitHub and `.env`
2. Check ngrok URL is accessible
3. Verify webhook endpoint: `/api/webhook/github-actions`
4. Check backend logs for errors

### Database Issues
```bash
# Reinitialize database
python init_db.py

# Check database file
ls -la data.db
```

## 📊 Monitoring Dashboard Features

- **Real-time Metrics**: Success/failure rates, build times
- **Build History**: Complete pipeline execution history
- **Auto-refresh**: Updates every 30 seconds
- **Filtering**: By status, branch, time period
- **GitHub Actions Integration**: Real-time webhook monitoring

## 🚢 Production Deployment

### Docker Deployment
```bash
# Build and run with Docker
./deploy.sh

# Or use Docker Compose
docker-compose up -d
```

### Environment Variables
- Set `DEBUG=false` for production
- Configure production database (PostgreSQL)
- Set up proper SSL certificates

## 🔐 Security Notes

- **Never commit** `.env` file to git
- **Rotate secrets** regularly in production
- **Use HTTPS** for all webhook communications
- **Implement rate limiting** for production use
- **Monitor access logs** for suspicious activity

## 📚 Additional Resources

- [README.md](README.md) - Project overview
- [DOCKER_SETUP.md](DOCKER_SETUP.md) - Docker configuration
- [tech_design_document.md](tech_design_document.md) - Technical architecture
- [requirement_analysis_document.md](requirement_analysis_document.md) - Requirements analysis

## 🆘 Support

If you encounter issues:
1. Check the logs: `tail -f logs/dashboard.log`
2. Verify all environment variables are set
3. Ensure GitHub secrets are configured correctly
4. Check network connectivity and firewall settings

---

**🎉 Your CI/CD Health Dashboard is now ready to monitor GitHub Actions pipelines in real-time!**
