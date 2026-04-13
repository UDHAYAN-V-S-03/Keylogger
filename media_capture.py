import pyautogui
import os
from datetime import datetime
from config import HIDDEN_DIR, SCREENSHOT_FILE, LOG_FILE

def _timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def _log_event(message):
    log_path = os.path.join(HIDDEN_DIR, LOG_FILE)
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"{_timestamp()} {message}\n")

def take_screenshot():
    path = os.path.join(HIDDEN_DIR, SCREENSHOT_FILE)
    screenshot = pyautogui.screenshot()
    screenshot.save(path)
    _log_event(f"Screenshot captured -> {path}")
    return path