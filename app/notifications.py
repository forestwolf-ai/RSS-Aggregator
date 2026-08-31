import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

logger = logging.getLogger(__name__)

def send_email(subject, body):
    """发送邮件通知，使用 Flask 配置"""
    if not current_app.config.get('EMAIL_ENABLED', False):
        logger.info("Email notifications disabled")
        return
    try:
        msg = MIMEMultipart()
        msg['From'] = current_app.config.get('EMAIL_FROM', '')
        msg['To'] = current_app.config.get('EMAIL_TO', '')
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        server = smtplib.SMTP(
            current_app.config.get('EMAIL_SMTP_SERVER', ''),
            current_app.config.get('EMAIL_SMTP_PORT', 587),
            timeout=10
        )
        server.starttls()
        server.login(
            current_app.config.get('EMAIL_USERNAME', ''),
            current_app.config.get('EMAIL_PASSWORD', '')
        )
        server.sendmail(
            current_app.config.get('EMAIL_FROM', ''),
            [current_app.config.get('EMAIL_TO', '')],
            msg.as_string()
        )
        server.quit()
        logger.info(f"Email sent: {subject}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
