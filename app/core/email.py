import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_feedback_email(name: str, email: str, feedback_type: str, message: str):
    sender_email = settings.SMTP_USER
    receiver_email = settings.FEEDBACK_EMAIL_TO

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = f"New Feedback: {feedback_type}"

    body = f"""
    Name: {name}
    Email: {email}
    Type: {feedback_type}
    Message:
    {message}
    """
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("✅ Feedback email sent successfully")
    except Exception as e:
        print("❌ Failed to send feedback email:", e)
        raise e
