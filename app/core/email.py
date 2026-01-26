import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FEEDBACK_EMAIL_TO = os.getenv("FEEDBACK_EMAIL_TO")


def send_feedback_email(feedback):
    subject = f"📩 New Feedback: {feedback.type.capitalize()}"

    body = f"""
New feedback received:

Name: {feedback.name}
Email: {feedback.email}
Type: {feedback.type}

Message:
{feedback.message}

Submitted at: {feedback.created_at}
User ID: {feedback.user_id or 'Anonymous'}
"""

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = FEEDBACK_EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
