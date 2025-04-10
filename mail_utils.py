import os
import smtplib
import logging
from email.mime.text import MIMEText

def send_email(recipient, subject, body):
    """
    发送邮件通知。默认配置使用 QQ 邮箱：
      - SMTP_HOST: smtp.qq.com
      - SMTP_PORT: 465（使用 SSL 连接）
      - SMTP_USER: your@qq.com
      - SMTP_PASS: your_authorization_code （授权码）
      - SENDER_EMAIL: 默认为 SMTP_USER
    可通过环境变量覆盖默认设置。
    """
    smtp_host = os.environ.get("SMTP_HOST", "smtp.qq.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 465))
    smtp_user = os.environ.get("SMTP_USER", "your@qq.com")
    smtp_pass = os.environ.get("SMTP_PASS", "your_authorization_code")
    sender = os.environ.get("SENDER_EMAIL", smtp_user)

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    try:
        logging.debug(f"连接邮件服务器: {smtp_host}:{smtp_port}")
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=20)
            server.starttls()
        logging.debug("登录邮件服务器...")
        server.login(smtp_user, smtp_pass)
        logging.debug("发送邮件...")
        server.sendmail(sender, [recipient], msg.as_string())
        server.quit()
        logging.info(f"邮件发送成功，已通知 {recipient}")
    except Exception as e:
        logging.error(f"邮件发送失败: {e}")
