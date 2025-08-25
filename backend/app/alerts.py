import os
import json
import aiohttp
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from typing import Optional
import time

# Import secret manager with fallback
try:
    from .secret_manager import get_secret_or_env
except ImportError:
    print("⚠️ Secret manager not available, falling back to environment variables")
    def get_secret_or_env(secret_name: str, env_var: str, default: str = None):
        return os.getenv(env_var, default)

# Load environment variables
load_dotenv()

class AlertService:
    """Service for sending alerts via multiple channels"""
    
    def __init__(self):
        self.alerts_enabled = os.getenv("ALERTS_ENABLED", "true").lower() == "true"
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.slack_channel = os.getenv("SLACK_CHANNEL", "#general")
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = get_secret_or_env("smtp_password", "SMTP_PASSWORD")
        self.smtp_from_email = os.getenv("SMTP_FROM_EMAIL", "gopalakrishnan.kuppan@gmail.com")
        self.smtp_from_name = os.getenv("SMTP_FROM_NAME", "CI/CD Dashboard")
        
        # Debug output
        print(f"🔍 AlertService initialized with:")
        print(f"   SMTP_HOST: {self.smtp_host}")
        print(f"   SMTP_PORT: {self.smtp_port}")
        print(f"   SMTP_USERNAME: {self.smtp_username}")
        print(f"   SMTP_PASSWORD: {'[SET]' if self.smtp_password else '[NOT SET]'}")
        print(f"   ALERTS_ENABLED: {self.alerts_enabled}")
    
    async def send_alert(
        self,
        message: str,
        severity: str = "info",
        alert_type: str = "email",
        **kwargs
    ) -> bool:
        """Send alert via specified channel"""
        if not self.alerts_enabled:
            print("⚠️  Alerts are disabled")
            return False
        
        try:
            if alert_type == "email":
                return await self._send_email_alert(message, severity, **kwargs)
            elif alert_type == "slack":
                return await self._send_slack_alert(message, severity, **kwargs)
            else:
                print(f"⚠️  Unknown alert type: {alert_type}")
                return False
        except Exception as e:
            print(f"❌ Failed to send {alert_type} alert: {e}")
            return False
    
    async def send_build_failure_alert(self, build, provider_name: str) -> bool:
        """Send specific alert for build failures"""
        print(f"🔍 send_build_failure_alert called for build {build.external_id}")
        print(f"🔍 Build status: {build.status}")
        print(f"🔍 Provider: {provider_name}")
        
        message = f"🚨 Build #{build.external_id} failed on {provider_name}\n"
        message += f"Branch: {build.branch}\n"
        message += f"Triggered by: {build.triggered_by}\n"
        message += f"Duration: {build.duration_seconds}s\n"
        message += f"URL: {build.url}"
        
        print(f"📝 Alert message: {message}")
        
        result = await self.send_alert(
            message=message,
            severity="error",
            alert_type="email"
        )
        
        print(f"📧 send_alert result: {result}")
        return result
    
    async def _send_slack_alert(self, message: str, severity: str, **kwargs) -> bool:
        """Send alert to Slack"""
        if not self.slack_webhook_url:
            print("⚠️  Slack webhook URL not configured")
            return False
        
        try:
            # Prepare Slack message
            color_map = {
                "info": "#36a64f",
                "warning": "#ffcc00",
                "error": "#ff0000",
                "critical": "#8b0000"
            }
            
            slack_payload = {
                "channel": self.slack_channel,
                "attachments": [
                    {
                        "color": color_map.get(severity, "#36a64f"),
                        "title": f"CI/CD Dashboard Alert - {severity.upper()}",
                        "text": message,
                        "footer": "CI/CD Health Dashboard",
                        "ts": int(time.time())
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.slack_webhook_url,
                    json=slack_payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        print(f"✅ Slack alert sent successfully")
                        return True
                    else:
                        print(f"❌ Slack alert failed with status: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ Failed to send Slack alert: {e}")
            return False
    
    async def _send_email_alert(self, message: str, severity: str, **kwargs) -> bool:
        """Send alert via email"""
        print(f"🔍 _send_email_alert called with kwargs: {kwargs}")
        print(f"🔍 SMTP config - host: {self.smtp_host}, username: {self.smtp_username}, password: {'[SET]' if self.smtp_password else '[NOT SET]'}")
        
        if not all([self.smtp_host, self.smtp_username, self.smtp_password]):
            print("⚠️  SMTP configuration incomplete")
            return False
        
        try:
            # Get recipient from kwargs or use environment variable
            recipient = kwargs.get("recipients") or os.getenv("ALERT_DEFAULT_RECIPIENT", "gopalakrishnan.kuppan@gmail.com")
            print(f"🔍 Using recipient: {recipient}")
            print(f"🔍 ALERT_DEFAULT_RECIPIENT env var: {os.getenv('ALERT_DEFAULT_RECIPIENT')}")
            
            # Prepare email
            msg = MIMEMultipart()
            msg["From"] = f"{self.smtp_from_name} <{self.smtp_from_email}>"
            msg["To"] = recipient
            msg["Subject"] = f"CI/CD Dashboard Alert - {severity.upper()}"
            
            # Email body
            body = f"""
            CI/CD Health Dashboard Alert
            
            Severity: {severity.upper()}
            Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
            
            Message:
            {message}
            
            ---
            This is an automated alert from the CI/CD Health Dashboard.
            """
            
            msg.attach(MIMEText(body, "plain"))
            
            # Send email
            if self.smtp_port == 465:
                # Use SSL for port 465
                await aiosmtplib.send(
                    msg,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    username=self.smtp_username,
                    password=self.smtp_password,
                    start_tls=False,
                    use_tls=False
                )
            else:
                # Use TLS for port 587
                await aiosmtplib.send(
                    msg,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    username=self.smtp_username,
                    password=self.smtp_password,
                    start_tls=True,
                    use_tls=False
                )
            
            print(f"✅ Email alert sent successfully to {recipient}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email alert: {e}")
            return False

# Create global instance
alert_service = AlertService()
