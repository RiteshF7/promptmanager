import json
import os
import threading

class PromptManager:
    def __init__(self, filepath="prompts.json"):
        self.filepath = filepath
        self.prompts = {}
        self.lock = threading.Lock()
        self.load_prompts()

    def load_prompts(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    self.prompts = json.load(f)
            except json.JSONDecodeError:
                self.prompts = {}
        else:
            self.prompts = {}

    def save_prompts(self):
        with self.lock:
            with open(self.filepath, 'w') as f:
                json.dump(self.prompts, f, indent=4)

    def add_prompt(self, shortcut, text):
        if ' ' in shortcut:
            raise ValueError("Shortcuts cannot contain spaces")
        with self.lock:
            self.prompts[shortcut] = text
        self.save_prompts()

    def delete_prompt(self, shortcut):
        with self.lock:
            if shortcut in self.prompts:
                del self.prompts[shortcut]
        self.save_prompts()

    def get_prompts(self):
        with self.lock:
            return self.prompts.copy()

    def get_prompt(self, shortcut):
        with self.lock:
            return self.prompts.get(shortcut)
