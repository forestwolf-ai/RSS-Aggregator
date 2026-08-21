import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body, config):
    """发送邮件通知，config为配置字典的notifications.email部分"""
    if not config.get('enabled'):
        return
    try:
        msg = MIMEMultipart()
        msg['From'] = config['from_addr']
        msg['To'] = config['to_addr']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['username'], config['password'])
        server.sendmail(config['from_addr'], [config['to_addr']], msg.as_string())
        server.quit()
    except Exception:
        pass