"""
Background service for Prompt Manager that runs continuously
with a system tray icon for easy management.
"""
import sys
import os
import threading
from prompt_manager import PromptManager
from keyboard_listener import KeyboardListener
import pystray
from PIL import Image, ImageDraw
import subprocess

class BackgroundService:
    def __init__(self):
        self.prompt_manager = PromptManager()
        self.listener = KeyboardListener(self.prompt_manager)
        self.running = False
        self.icon = None
        
    def create_icon_image(self):
        """Create a simple icon image for the system tray"""
        # Create a 64x64 image with a simple icon
        image = Image.new('RGB', (64, 64), color='white')
        draw = ImageDraw.Draw(image)
        # Draw a simple keyboard icon representation
        draw.rectangle([10, 20, 54, 44], outline='black', width=2)
        draw.text((20, 25), "PM", fill='black')
        return image
    
    def start_listener(self):
        """Start the keyboard listener"""
        if not self.running:
            self.listener.start()
            self.running = True
            print("Keyboard listener started")
    
    def stop_listener(self):
        """Stop the keyboard listener"""
        if self.running:
            self.listener.stop()
            self.running = False
            print("Keyboard listener stopped")
    
    def open_gui(self, icon=None, item=None):
        """Open the GUI application"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        gui_script = os.path.join(script_dir, "gui.py")
        subprocess.Popen([sys.executable, gui_script], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0)
    
    def on_quit(self, icon=None, item=None):
        """Handle quit action"""
        self.stop_listener()
        if self.icon:
            self.icon.stop()
        sys.exit(0)
    
    def setup_menu(self):
        """Setup the system tray menu"""
        menu = pystray.Menu(
            pystray.MenuItem("Open GUI", self.open_gui, default=True),
            pystray.MenuItem("Start Listener", self.start_listener, 
                           enabled=lambda item: not self.running),
            pystray.MenuItem("Stop Listener", self.stop_listener,
                           enabled=lambda item: self.running),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.on_quit)
        )
        return menu
    
    def run(self):
        """Run the background service"""
        # Start the listener automatically
        self.start_listener()
        
        # Create and run the system tray icon
        image = self.create_icon_image()
        menu = self.setup_menu()
        
        self.icon = pystray.Icon("PromptManager", image, "Prompt Manager", menu)
        
        # Run the icon (this blocks until stopped)
        self.icon.run()

if __name__ == "__main__":
    service = BackgroundService()
    try:
        service.run()
    except KeyboardInterrupt:
        service.stop_listener()
        sys.exit(0)

