"""
Loading animation module for prompt enhancement.
Handles animated loading indicator with flying plane effect.
"""
import time
import threading
from pynput.keyboard import Key, Controller


class LoadingAnimation:
    """Handles animated loading indicator with ➤ character (flying plane effect)"""
    
    def __init__(self, controller=None):
        """
        Initialize the loading animation.
        
        Args:
            controller: pynput Controller instance for typing/deleting text.
                      If None, creates a new one.
        """
        self.controller = controller or Controller()
        self.animation_running = False
        self.animation_stop_event = threading.Event()
        self.animation_thread = None
        self.current_text = ""
        self.arrow = "➤"
        self.max_spaces = 10
        self.animation_delay = 0.15  # Delay between frames in seconds
    
    def start(self):
        """
        Start the animated loading indicator.
        The animation shows ➤ moving from left to right (flying plane effect).
        """
        # Reset animation control
        self.animation_stop_event.clear()
        self.animation_running = True
        self.current_text = ""
        
        # Start animation thread
        self.animation_thread = threading.Thread(target=self._animate)
        self.animation_thread.daemon = True
        self.animation_thread.start()
    
    def stop(self):
        """
        Stop the animated loading indicator.
        Waits briefly for the animation thread to finish, then deletes the animation text.
        """
        # Signal animation to stop
        self.animation_running = False
        self.animation_stop_event.set()
        
        # Wait for animation thread to finish current frame
        if self.animation_thread and self.animation_thread.is_alive():
            time.sleep(0.25)
        
        # Delete the animated text
        self._delete_animation_text()
    
    def _animate(self):
        """
        Internal method that runs the animation loop.
        Creates the flying plane effect by adding spaces before ➤.
        """
        space_count = 0
        first_frame = True
        
        while self.animation_running and not self.animation_stop_event.is_set():
            # Create the animated text: spaces + arrow
            animated_text = " " * space_count + self.arrow
            
            # Delete previous animation (except first time)
            if not first_frame:
                self._delete_text(self.current_text)
            
            # Type new animation frame
            self.controller.type(animated_text)
            self.current_text = animated_text
            first_frame = False
            
            # Increment space count for next frame (cycle through 0 to max_spaces)
            space_count = (space_count + 1) % (self.max_spaces + 1)
            
            # Wait before next frame
            time.sleep(self.animation_delay)
    
    def _delete_animation_text(self):
        """
        Delete the current animation text from the active text field.
        Handles up to the maximum possible length of animation.
        """
        max_length = self.max_spaces + len(self.arrow)
        for _ in range(max_length):
            self.controller.press(Key.backspace)
            self.controller.release(Key.backspace)
            time.sleep(0.005)  # Small delay for smooth deletion
    
    def _delete_text(self, text):
        """
        Delete a specific text string character by character.
        
        Args:
            text: The text string to delete.
        """
        for _ in range(len(text)):
            self.controller.press(Key.backspace)
            self.controller.release(Key.backspace)
            time.sleep(0.01)

