import aiosmtplib
from email.message import EmailMessage
import os
from datetime import datetime

class EmailService:
    """Send email notifications via Gmail SMTP"""
    
    @staticmethod
    async def send_feedback_notification(feedback_data: dict):
        """Send email when feedback is received"""
        
        # Get credentials from environment
        email_user = os.getenv("EMAIL_USER")
        email_password = os.getenv("EMAIL_PASSWORD")
        email_recipient = os.getenv("EMAIL_RECIPIENT", email_user)
        
        # ADD DEBUGGING
        #print(f"🔍 DEBUG - EMAIL_USER: {email_user}")
        #print(f"🔍 DEBUG - EMAIL_PASSWORD: {'*' * len(email_password) if email_password else 'NOT SET'}")
        #print(f"🔍 DEBUG - EMAIL_RECIPIENT: {email_recipient}")
        
        if not email_user or not email_password:
            print("⚠️ Email not configured. Skipping notification.")
            print("   Set EMAIL_USER and EMAIL_PASSWORD environment variables")
            return
        
        # Create email message
        message = EmailMessage()
        message["From"] = email_user
        message["To"] = email_recipient
        message["Subject"] = f"🔔 New Feedback: {feedback_data['type'].upper()}"
        
        # Email body
        body = f"""
New feedback received from StudyCore!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TYPE: {feedback_data['type'].upper()}

FROM:
  Name: {feedback_data['name']}
  Email: {feedback_data['email']}

MESSAGE:
{feedback_data['message']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Submitted: {feedback_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}

---
StudyCore Feedback System
        """
        
        message.set_content(body)
        
        try:
            print("📧 Attempting to send email...")
            
            # Send via Gmail SMTP
            await aiosmtplib.send(
                message,
                hostname="smtp.gmail.com",
                port=465,
                username=email_user,
                password=email_password,
                use_tls=True,
                timeout=30
            )
            
            print(f"✅ Email notification sent")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")
            import traceback
            traceback.print_exc()  # Show full error
            return False
