from pynput import keyboard
from pynput.keyboard import Key, Controller
import time
import threading
import json
from loading_animation import LoadingAnimation
try:
    from urllib.request import urlopen, Request
    from urllib.error import URLError
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

class KeyboardListener:
    def __init__(self, prompt_manager, gemini_client=None):
        self.prompt_manager = prompt_manager
        self.gemini_client = gemini_client
        self.buffer = ""
        self.controller = Controller()
        self.listener = None
        self.running = False
        self.loading_animation = LoadingAnimation(self.controller)

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
            
            # Limit buffer size to prevent memory issues - increased for enhancement
            if len(self.buffer) > 500:
                self.buffer = self.buffer[-500:]
            
            # Check for matches
            self.check_for_matches()
            
        except Exception as e:
            print(f"Error in on_press: {e}")

    def check_for_matches(self):
        # Check for enhancement trigger
        if self.buffer.endswith("````"):
            self.handle_enhancement()
            return

        prompts = self.prompt_manager.get_prompts()
        for shortcut, prompt_data in prompts.items():
            # Handle both old format (string) and new format (object)
            if isinstance(prompt_data, dict):
                prepend = prompt_data.get('prepend', '')
                postpend = prompt_data.get('postpend', '')
                # Build the full trigger shortcut: prepend + shortcut + postpend
                full_trigger = prepend + shortcut + postpend
                text = prompt_data.get('text', '')
                replacement = text  # Replacement is just the text, not prepend/postpend
            else:
                # Old format - just use the shortcut as-is
                full_trigger = shortcut
                replacement = prompt_data
            
            # Check if buffer ends with the full trigger shortcut
            if self.buffer.endswith(full_trigger):
                # Track usage (non-blocking)
                self.track_usage(shortcut)
                
                # Clear buffer BEFORE replacement to ensure clean state
                self.buffer = ""
                # Replace the full trigger with only the text (no prepend/postpend)
                self.replace_text(full_trigger, replacement)
                break
    
    def track_usage(self, shortcut):
        """Track prompt usage by calling the API endpoint"""
        if not HAS_URLLIB:
            return
        try:
            data = json.dumps({'shortcut': shortcut}).encode('utf-8')
            req = Request('http://localhost:5000/api/prompts/track-usage', 
                         data=data,
                         headers={'Content-Type': 'application/json'})
            urlopen(req, timeout=0.1)
        except:
            # Silently fail - this is non-critical
            pass

    def handle_enhancement(self):
        if not self.gemini_client:
            return

        # Extract the text before ````
        # We assume the user typed the prompt and then ```` immediately
        # We'll take the last 500 chars (minus the trigger) as context, 
        # but practically we want to find the start of the sentence or just take everything in buffer.
        # For simplicity, we'll take the whole buffer minus the trigger.
        
        trigger = "````"
        text_to_enhance = self.buffer[:-len(trigger)].strip()
        
        if not text_to_enhance:
            return

        # Clear buffer to prevent further processing
        self.buffer = ""
        
        # Visual feedback: delete the trigger
        self.delete_text(trigger)
        
        # Delete the original text
        self.delete_text(text_to_enhance)
        
        # Start the animated loading indicator
        self.loading_animation.start()
        
        # Run enhancement in a separate thread to avoid blocking
        def enhance_and_replace():
            try:
                # Get the enhanced text
                enhanced_text = self.gemini_client.enhance_prompt(text_to_enhance)
                
                # Stop animation
                self.loading_animation.stop()
                
                # Type the enhanced text, replacing newlines with spaces to prevent auto-sending
                self.controller.type(enhanced_text.replace('\n', ' '))
            except Exception as e:
                # Stop animation on error
                self.loading_animation.stop()
                
                # Show error message
                error_msg = f"Error: {str(e)}"
                self.controller.type(error_msg)
        
        # Start the enhancement in a separate thread
        thread = threading.Thread(target=enhance_and_replace)
        thread.daemon = True
        thread.start()

    def delete_text(self, text):
        for _ in range(len(text)):
            self.controller.press(Key.backspace)
            self.controller.release(Key.backspace)
            time.sleep(0.01)

    def replace_text(self, text_to_delete, replacement):
        # Delete the full trigger (prepend + shortcut + postpend)
        # Make sure we delete exactly what was typed, nothing more, nothing less
        self.delete_text(text_to_delete)
        # Insert only the replacement text (no prepend/postpend)
        # Strip trailing newlines/whitespace to prevent auto-enter
        self.controller.type(replacement.rstrip())

    def start(self):
        self.running = True
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def stop(self):
        self.running = False
        if self.listener:
            self.listener.stop()
