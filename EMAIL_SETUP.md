# 📧 **Email Setup Guide for CI/CD Dashboard**

## 🔐 **GitHub Secrets Configuration (Recommended)**

Instead of hardcoding email credentials, store them securely in GitHub Secrets:

### **Required GitHub Secrets:**

1. **`SMTP_USERNAME`**
   - Value: Your Gmail address (e.g., `renugavelmurugan09@gmail.com`)

2. **`SMTP_PASSWORD`**
   - Value: Your Gmail App Password (NOT your regular password)

3. **`ALERT_DEFAULT_RECIPIENT`**
   - Value: Default email for alerts (e.g., `renugavelmurugan09@gmail.com`)

4. **`ALERT_TEST_RECIPIENT`**
   - Value: Email for test alerts (e.g., `renugavelmurugan09@gmail.com`)

### **How to Add GitHub Secrets:**

1. Go to: `https://github.com/velu-vm/cicd-health-dashboard/settings/secrets/actions`
2. Click "New repository secret"
3. Add each secret with the exact names above

## 🚀 **Local Development Setup**

For local development, create a `.env` file:

```bash
# Email Configuration
ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=renugavelmurugan09@gmail.com
SMTP_PASSWORD=YOUR_APP_PASSWORD_HERE
SMTP_FROM_EMAIL=renugavelmurugan09@gmail.com
SMTP_FROM_NAME=CI/CD Dashboard

# Alert Recipients
ALERT_DEFAULT_RECIPIENT=renugavelmurugan09@gmail.com
ALERT_TEST_RECIPIENT=renugavelmurugan09@gmail.com
```

## 🔑 **Gmail App Password Setup**

### **Step 1: Enable 2-Factor Authentication**
1. Go to [Google Account Settings](https://myaccount.google.com/security)
2. Enable "2-Step Verification"

### **Step 2: Generate App Password**
1. Go to [Google Account Security](https://myaccount.google.com/apppasswords)
2. Select "Mail" and "Other (Custom name)"
3. Name: "CI/CD Dashboard"
4. Click "Generate"
5. Copy the 16-character password

### **Step 3: Update Configuration**
- Replace `YOUR_APP_PASSWORD_HERE` with the generated password
- **Never use your regular Gmail password**

## 🧪 **Test Email Notifications**

### **Test with Backend Running:**
```bash
curl -X POST http://localhost:8000/api/alert/test \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer d447e5b2466828ddda9eed4da0597577" \
  -d '{"message": "Test email notification", "severity": "info"}'
```

### **Expected Response:**
```json
{
  "success": true,
  "message": "Alert test completed successfully to renugavelmurugan09@gmail.com"
}
```

## 🔍 **Troubleshooting**

### **Email Not Sending?**
1. ✅ Check if `ALERTS_ENABLED=true`
2. ✅ Verify Gmail app password is correct
3. ✅ Ensure 2FA is enabled on Gmail
4. ✅ Check backend logs for SMTP errors

### **Common Errors:**
- **535 Authentication Failed**: Wrong app password
- **Connection Refused**: Check SMTP port (465 for SSL, 587 for TLS)
- **SSL/TLS Error**: Verify port and SSL settings

## 🚨 **Security Best Practices**

1. **Never commit credentials** to your repository
2. **Use GitHub Secrets** for production deployments
3. **Use App Passwords** instead of regular passwords
4. **Rotate app passwords** regularly
5. **Monitor email usage** in Gmail

## 📋 **Environment Variables Reference**

| Variable | Description | Example |
|----------|-------------|---------|
| `SMTP_USERNAME` | Gmail address | `renugavelmurugan09@gmail.com` |
| `SMTP_PASSWORD` | Gmail app password | `abcd efgh ijkl mnop` |
| `ALERT_DEFAULT_RECIPIENT` | Default alert email | `renugavelmurugan09@gmail.com` |
| `ALERT_TEST_RECIPIENT` | Test alert email | `renugavelmurugan09@gmail.com` |

---

**🎉 Your email notifications are now properly configured with environment variables and GitHub secrets!**
