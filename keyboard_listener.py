from pynput import keyboard
from pynput.keyboard import Key, Controller
import time
import threading

class KeyboardListener:
    def __init__(self, prompt_manager):
        self.prompt_manager = prompt_manager
        self.buffer = ""
        self.controller = Controller()
        self.listener = None
        self.running = False

    def on_press(self, key):
        try:
            if hasattr(key, 'char') and key.char:
                self.buffer += key.char
            elif key == Key.space:
                self.buffer += " "
            elif key == Key.enter:
                self.buffer = "" # Reset on enter usually
            elif key == Key.backspace:
                self.buffer = self.buffer[:-1]
            
            # Check for matches
            self.check_for_matches()
            
        except Exception as e:
            print(f"Error in on_press: {e}")

    def check_for_matches(self):
        prompts = self.prompt_manager.get_prompts()
        for shortcut, replacement in prompts.items():
            if self.buffer.endswith(shortcut):
                self.replace_text(shortcut, replacement)
                self.buffer = "" # Reset buffer after replacement
                break

    def replace_text(self, shortcut, replacement):
        # Delete the shortcut
        for _ in range(len(shortcut)):
            self.controller.press(Key.backspace)
            self.controller.release(Key.backspace)
            time.sleep(0.01) # Small delay for stability
        
        # Type the replacement
        self.controller.type(replacement)

    def start(self):
        self.running = True
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def stop(self):
        self.running = False
        if self.listener:
            self.listener.stop()
