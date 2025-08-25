#!/bin/bash

# CI/CD Health Dashboard Configuration Setup Script
set -e

echo "🚀 Setting up CI/CD Health Dashboard Configuration..."

# Create necessary directories
mkdir -p data logs

# Generate random secrets
SECRET_KEY=$(openssl rand -hex 32)
WRITE_KEY=$(openssl rand -hex 16)
GITHUB_SECRET=$(openssl rand -hex 16)

echo "🔐 Generated Security Keys:"
echo "SECRET_KEY: $SECRET_KEY"
echo "WRITE_KEY: $WRITE_KEY"
echo "GITHUB_SECRET: $GITHUB_SECRET"
echo ""

# Create .env file
cat > .env << EOF
# CI/CD Health Dashboard Environment Configuration

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./data.db
DEBUG=true

# Server Configuration
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=["http://localhost:8080", "http://localhost:3000", "http://127.0.0.1:8080"]

# Security Configuration
SECRET_KEY=$SECRET_KEY
WRITE_KEY=$WRITE_KEY

# Alert Configuration
ALERTS_ENABLED=false
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=gopalakrishnan.kuppan@gmail.com
SMTP_FROM_NAME=CI/CD Dashboard

# GitHub Actions Configuration
GITHUB_WEBHOOK_SECRET=$GITHUB_SECRET

# Monitoring Configuration
METRICS_ENABLED=true
HEALTH_CHECK_INTERVAL=30

# Rate Limiting
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/dashboard.log
EOF

echo "✅ Created .env file with generated secrets"
echo ""

# Create GitHub secrets configuration file
cat > github-secrets.md << EOF
# GitHub Repository Secrets Configuration

## Required Secrets for GitHub Actions

Add these secrets in your GitHub repository:
Settings → Secrets and variables → Actions → New repository secret

### 1. DASHBOARD_WEBHOOK_URL
- **Value**: https://your-public-url/api/webhook/github-actions
- **Description**: Public URL where your dashboard backend is accessible
- **Note**: Use ngrok or cloudflared to expose localhost:8000

### 2. DASHBOARD_WRITE_KEY
- **Value**: $WRITE_KEY
- **Description**: Authentication token for webhook requests
- **Note**: Must match WRITE_KEY in your dashboard .env file

## How to Set Up:

1. Install ngrok: \`brew install ngrok\` (macOS) or download from ngrok.com
2. Expose your dashboard: \`ngrok http 8000\`
3. Copy the https URL (e.g., https://abcd-1234.ngrok-free.app)
4. Add the secrets in GitHub with the full webhook URL
5. Test with a commit/push to trigger the workflow

## Current Configuration:
- WRITE_KEY: $WRITE_KEY
- SECRET_KEY: $SECRET_KEY
- GitHub Secret: $GITHUB_SECRET
EOF

echo "✅ Created GitHub secrets configuration guide"
echo ""

# Create quick start script
cat > quick-start.sh << 'EOF'
#!/bin/bash

# Quick Start Script for CI/CD Dashboard
echo "🚀 Quick Start for CI/CD Dashboard"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Run setup_config.sh first."
    exit 1
fi

# Load environment variables
source .env

echo "📋 Current Configuration:"
echo "WRITE_KEY: $WRITE_KEY"
echo "DATABASE_URL: $DATABASE_URL"
echo ""

echo "🔧 Starting Dashboard..."
echo "1. Start the backend: python run_server.py"
echo "2. In another terminal, expose with ngrok: ngrok http 8000"
echo "3. Copy the https URL and add to GitHub secrets"
echo "4. Test with a git push"
echo ""

echo "📚 Useful Commands:"
echo "- View logs: tail -f logs/dashboard.log"
echo "- Test API: curl http://localhost:8000/health"
echo "- Open frontend: open http://localhost:8080"
echo "- Stop server: pkill -f 'run_server.py'"
EOF

chmod +x quick-start.sh

echo "✅ Created quick-start.sh script"
echo ""

# Create ngrok setup script
cat > setup-ngrok.sh << 'EOF'
#!/bin/bash

# Setup ngrok for exposing local dashboard
echo "🌐 Setting up ngrok for public access..."

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not found. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install ngrok
    else
        echo "Please install ngrok from https://ngrok.com/download"
        exit 1
    fi
fi

echo "✅ ngrok is installed"
echo ""
echo "🚀 To expose your dashboard:"
echo "1. Start your dashboard: python run_server.py"
echo "2. In another terminal: ngrok http 8000"
echo "3. Copy the https URL (e.g., https://abcd-1234.ngrok-free.app)"
echo "4. Use this URL in GitHub secrets: DASHBOARD_WEBHOOK_URL"
echo ""

echo "📋 Example ngrok command:"
echo "ngrok http 8000 --log=stdout"
EOF

chmod +x setup-ngrok.sh

echo "✅ Created setup-ngrok.sh script"
echo ""

echo "🎉 Configuration setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Review the generated .env file"
echo "2. Read github-secrets.md for GitHub setup"
echo "3. Run: ./quick-start.sh for quick start guide"
echo "4. Run: ./setup-ngrok.sh for ngrok setup"
echo ""
echo "🔐 Important: Keep your secrets secure and never commit .env to git!"
echo "📚 Check README.md for detailed setup instructions"
