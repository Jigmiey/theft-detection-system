import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT","587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASSWORD")
ALERT_RECIPIENT = os.getenv("ALERT_RECIPIENT")

def send_email_alert(subject:str,message:str):
    """
    Sends an email to the Loss Prevention Team.
    """
    msg = MIMEText(message)
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_RECIPIENT
    msg["Subject"] = subject
    
    with smtplib.SMTP(SMTP_SERVER,SMTP_PORT) as s:
        s.starttls()
        s.login(SMTP_USER,SMTP_PASS)
        s.send_message(msg)
    print(f"Alert sent successfully to {ALERT_RECIPIENT}")
    