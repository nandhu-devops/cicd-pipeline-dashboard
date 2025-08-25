# 🐳 Docker Setup Guide for CI/CD Pipeline

## 🎯 **Overview**

Your CI/CD pipeline now includes Docker image building and pushing to Docker Hub. This guide will help you set up the required secrets and configuration.

## 🔐 **Required GitHub Secrets**

You need to add these secrets to your GitHub repository:

### 1. **DOCKERUSERNAME**
- **What**: Your Docker Hub username
- **Where**: Go to [GitHub Repository Settings](https://github.com/velu-vm/cicd-health-dashboard/settings/secrets/actions) → Secrets and variables → Actions
- **Example**: `velmurugan` (if your Docker Hub username is velmurugan)

### 2. **DOCKERPASSWORD**
- **What**: Your Docker Hub access token (NOT your login password)
- **How to get it**:
  1. Go to [Docker Hub](https://hub.docker.com/settings/security)
  2. Click "New Access Token"
  3. Name it "CI/CD Dashboard"
  4. Copy the generated token

### 3. **Update Your .env File**
Replace `Arvish@09` with the actual app password:

```bash
# Current setting (needs to be updated)
SMTP_PASSWORD=Arvish@09

# Should become (example)
SMTP_PASSWORD=abcd efgh ijkl mnop
```

## 🔧 **Manual Update Command**
```bash
sed 's/SMTP_PASSWORD=Arvish@09/SMTP_PASSWORD=YOUR_ACTUAL_APP_PASSWORD/' .env > .env.new && mv .env.new .env
```

## 📋 **Current Email Configuration**
```env
ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=renugavelmurugan09@gmail.com
SMTP_PASSWORD=Arvish@09  # ⚠️ UPDATE THIS with App Password!
SMTP_FROM_EMAIL=renugavelmurugan09@gmail.com
SMTP_FROM_NAME=CI/CD Dashboard - renugavelmurugan09@gmail.com
```

## 🧪 **Test Email Notifications**

Once you've updated the app password, test the email functionality:

```bash
# Test alert endpoint
curl -X POST http://localhost:8000/api/alert/test \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer d447e5b2466828ddda9eed4da0597577" \
  -d '{"message": "Test email notification from CI/CD Dashboard"}'
```

## 📬 **What You'll Receive**

- **Build Failure Alerts**: When any CI/CD pipeline fails
- **Test Notifications**: When you manually test the alert system
- **Pipeline Status Updates**: Important pipeline events

## 🚨 **Troubleshooting**

### **Email Not Sending?**
1. Check if `ALERTS_ENABLED=true`
2. Verify Gmail app password is correct
3. Ensure 2FA is enabled on Gmail
4. Check backend logs for SMTP errors

### **Gmail Security Issues?**
- Gmail blocks regular passwords for SMTP - use App Passwords instead
- Check Gmail spam folder for test emails
- Verify sender email matches your Gmail account

## 🔄 **Restart Required**

After updating the `.env` file, restart your backend server:

```bash
# Stop current server
pkill -f "python run_server.py"

# Start with new config
python run_server.py &
```

## ✅ **Next Steps**

1. **Generate Gmail App Password** (see step 2 above)
2. **Update SMTP_PASSWORD** in `.env` file with the app password
3. **Restart backend server**
4. **Test email notifications**
5. **Trigger a failed build** to see failure alerts

---

**🎉 Your dashboard will now send real-time email notifications for all CI/CD pipeline failures!**

## 🚀 **CI/CD Pipeline Flow**

### **Test Job** ✅
- Runs simple tests (no app dependencies)
- Ensures code quality

### **Build Job** 🐳
- Builds Docker image from Dockerfile
- Pushes to Docker Hub with tags:
  - `latest` - Most recent build
  - `{commit-sha}` - Specific commit build

### **Deploy Job** 🚀
- Deploys the built Docker image
- Sends notifications to dashboard

## 📋 **Docker Image Details**

### **Image Name**:
```
{your-docker-username}/cicd-dashboard:latest
{your-docker-username}/cicd-dashboard:{commit-sha}
```

### **What's Included**:
- **Backend**: FastAPI application with all dependencies
- **Frontend**: Static HTML/CSS/JS files
- **Nginx**: Reverse proxy and static file server
- **Database**: SQLite (can be mounted as volume)

## 🚨 **Troubleshooting Docker Authentication**

### **Error: "401 Unauthorized" when pushing to Docker Hub**

This error means the Docker credentials are either:
1. **Not configured** in GitHub secrets
2. **Incorrect values** in the secrets
3. **Expired or invalid** Docker Hub access token

### **Step-by-Step Fix:**

#### **Step 1: Verify Docker Hub Account**
1. Go to [Docker Hub](https://hub.docker.com)
2. Sign in with your account
3. Note your exact username (case-sensitive)

#### **Step 2: Generate New Access Token**
1. Go to [Docker Hub Security Settings](https://hub.docker.com/settings/security)
2. Click "New Access Token"
3. **Name**: `CI/CD Dashboard`
4. **Permissions**: 
   - ✅ `Read & Write` for repositories
   - ✅ `Read` for organizations (if applicable)
5. Click "Generate"
6. **Copy the token immediately** (you won't see it again!)

#### **Step 3: Update GitHub Secrets**
1. Go to: `https://github.com/velu-vm/cicd-health-dashboard/settings/secrets/actions`
2. **Delete existing secrets** (if any):
   - Delete `DOCKERUSER` (if exists)
   - Delete `DOCKERPASS` (if exists)
3. **Add new secrets**:
   - **Name**: `DOCKERUSER`
   - **Value**: Your exact Docker Hub username
4. **Add another**:
   - **Name**: `DOCKERPASS`
   - **Value**: The access token you just generated

#### **Step 4: Test the Setup**
1. Push any change to `main` branch
2. Watch GitHub Actions tab
3. Verify Docker build and push succeeds

### **Common Issues & Solutions:**

#### **Issue 1: "Username not found"**
- **Cause**: Username is incorrect or doesn't exist
- **Solution**: Double-check your Docker Hub username (case-sensitive)

#### **Issue 2: "Access denied"**
- **Cause**: Access token is invalid or expired
- **Solution**: Generate a new access token

#### **Issue 3: "Repository not found"**
- **Cause**: Repository doesn't exist or wrong username
- **Solution**: Verify the repository name and username

#### **Issue 4: "Token expired"**
- **Cause**: Access token has expired
- **Solution**: Generate a new access token

### **Verification Commands:**

#### **Test Docker Hub Login Locally:**
```bash
# Test with your credentials
docker login -u YOUR_USERNAME -p YOUR_ACCESS_TOKEN

# Should show: "Login Succeeded"
# Then logout
docker logout
```

#### **Check Repository Access:**
```bash
# Verify you can see your repositories
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "https://hub.docker.com/v2/repositories/YOUR_USERNAME/"
```

### **Security Best Practices:**

1. **Never commit credentials** to your repository
2. **Use access tokens** instead of passwords
3. **Set appropriate permissions** (Read & Write only)
4. **Rotate tokens regularly** (every 90 days)
5. **Monitor token usage** in Docker Hub

---

## 🔧 **Setup Steps**

### **Step 1: Create Docker Hub Account**
1. Go to [Docker Hub](https://hub.docker.com)
2. Sign up or sign in
3. Note your username

### **Step 2: Generate Access Token**
1. Go to [Docker Hub Security Settings](https://hub.docker.com/settings/security)
2. Click "New Access Token"
3. Name: "CI/CD Dashboard"
4. Copy the token (you won't see it again!)

### **Step 3: Add GitHub Secrets**
1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add:
   - **Name**: `DOCKERUSER`
   - **Value**: Your Docker Hub username
5. Add another:
   - **Name**: `DOCKERPASS`
   - **Value**: Your Docker Hub access token

### **Step 4: Test the Pipeline**
1. Push any change to `main` branch
2. Watch GitHub Actions tab
3. Verify Docker image is built and pushed

## 📊 **Expected Results**

### **Successful Build**:
```
✅ Test Job: 13 tests passed
✅ Build Job: Docker image built and pushed
✅ Deploy Job: Deployment completed
```

### **Docker Hub**:
- New image: `{username}/cicd-dashboard:latest`
- Tagged image: `{username}/cicd-dashboard:{sha}`

## 🧪 **Testing Locally**

### **Pull and Run**:
```bash
# Pull the built image
docker pull {your-username}/cicd-dashboard:latest

# Run locally
docker run -d \
  --name cicd-dashboard \
  -p 8080:80 \
  -p 8000:8000 \
  {your-username}/cicd-dashboard:latest
```

### **Access Points**:
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🚨 **Troubleshooting**

### **Build Fails**:
1. Check Docker Hub credentials
2. Verify secrets are set correctly
3. Check Dockerfile syntax

### **Push Fails**:
1. Verify Docker Hub access token
2. Check repository permissions
3. Ensure Docker Hub account is active

### **Deploy Fails**:
1. Check if Docker image was built
2. Verify deployment script
3. Check target environment

## 🔄 **Next Steps**

1. **Set up Docker Hub secrets** (see Step 3 above)
2. **Push to main branch** to trigger pipeline
3. **Monitor GitHub Actions** for build progress
4. **Verify Docker Hub** for new images
5. **Test deployment** with built images

## 📚 **Resources**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Hub Documentation](https://docs.docker.com/docker-hub/)
- [Docker Build Action](https://github.com/docker/build-push-action)

---

**🎉 Once configured, every push to main will automatically build and push a new Docker image!**
