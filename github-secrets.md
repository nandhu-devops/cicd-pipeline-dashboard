# GitHub Repository Secrets Configuration

## Required Secrets for GitHub Actions

Add these secrets in your GitHub repository:
Settings → Secrets and variables → Actions → New repository secret

### 1. DASHBOARD_WEBHOOK_URL
- **Value**: https://your-public-url/api/webhook/github-actions
- **Description**: Public URL where your dashboard backend is accessible
- **Note**: Use ngrok or cloudflared to expose localhost:8000

### 2. DASHBOARD_WRITE_KEY
- **Value**: d447e5b2466828ddda9eed4da0597577
- **Description**: Authentication token for webhook requests
- **Note**: Must match WRITE_KEY in your dashboard .env file

## How to Set Up:

1. Install ngrok: `brew install ngrok` (macOS) or download from ngrok.com
2. Expose your dashboard: `ngrok http 8000`
3. Copy the https URL (e.g., https://abcd-1234.ngrok-free.app)
4. Add the secrets in GitHub with the full webhook URL
5. Test with a commit/push to trigger the workflow

## Current Configuration:
- WRITE_KEY: d447e5b2466828ddda9eed4da0597577
- SECRET_KEY: 2e6b09416dd5e87d2bd26390ff79f67f337ea48dac8f19897cf51ef0fe259037
- GitHub Secret: 2812824dd4f8d2102dff7369235c3814
