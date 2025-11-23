import customtkinter as ctk
from prompt_manager import PromptManager
from keyboard_listener import KeyboardListener
from service_manager import (
    check_background_service_running,
    check_startup_enabled,
    enable_startup,
    disable_startup,
    start_background_service,
    stop_background_service
)
import threading
import sys

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class PromptApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Prompt Manager")
        self.geometry("800x600")

        self.prompt_manager = PromptManager()
        self.listener = KeyboardListener(self.prompt_manager)
        
        # Start listener automatically
        self.listener.start()

        # Layout configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Sidebar (List of prompts)
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(1, weight=1)  # Make scrollable frame expandable

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Shortcuts", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.scrollable_frame = ctk.CTkScrollableFrame(self.sidebar_frame, label_text="Saved Prompts")
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(1, weight=1)

        # Right Main Area (Add/Edit)
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.main_label = ctk.CTkLabel(self.main_frame, text="Add New Prompt", font=ctk.CTkFont(size=20, weight="bold"))
        self.main_label.pack(pady=10, anchor="w")

        self.shortcut_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Shortcut (e.g., /hi)")
        self.shortcut_entry.pack(pady=10, fill="x")

        self.text_entry = ctk.CTkTextbox(self.main_frame, height=200)
        self.text_entry.pack(pady=10, fill="x")
        self.text_entry.insert("0.0", "Enter expansion text here...")

        self.add_button = ctk.CTkButton(self.main_frame, text="Save Prompt", command=self.add_prompt_event)
        self.add_button.pack(pady=10, anchor="e")

        self.status_label = ctk.CTkLabel(self.main_frame, text="Listener Running", text_color="green")
        self.status_label.pack(side="bottom", anchor="w")

        # Settings section for background service and startup
        self.setup_settings_section()

        self.refresh_list()
        # Update status periodically
        self.update_status()

    def refresh_list(self):
        # Clear existing buttons
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        prompts = self.prompt_manager.get_prompts()
        for shortcut, text in prompts.items():
            btn = ctk.CTkButton(self.scrollable_frame, text=shortcut, 
                                command=lambda s=shortcut, t=text: self.load_prompt_into_form(s, t),
                                fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"))
            btn.pack(pady=2, fill="x")
            
            # Add a small delete button next to it? 
            # For simplicity in this version, we'll just have the list items load into the form
            # and maybe add a delete button in the main form if a shortcut exists.

    def load_prompt_into_form(self, shortcut, text):
        self.shortcut_entry.delete(0, "end")
        self.shortcut_entry.insert(0, shortcut)
        self.text_entry.delete("0.0", "end")
        self.text_entry.insert("0.0", text)
        self.main_label.configure(text="Edit Prompt")
        
        # Add delete button dynamically if it doesn't exist
        if not hasattr(self, 'delete_button'):
            self.delete_button = ctk.CTkButton(self.main_frame, text="Delete", fg_color="red", hover_color="darkred", command=self.delete_prompt_event)
            self.delete_button.pack(pady=10, anchor="e", before=self.add_button)

    def add_prompt_event(self):
        shortcut = self.shortcut_entry.get()
        text = self.text_entry.get("0.0", "end-1c") # Get text without trailing newline
        
        if shortcut and text:
            self.prompt_manager.add_prompt(shortcut, text)
            self.refresh_list()
            self.clear_form()

    def delete_prompt_event(self):
        shortcut = self.shortcut_entry.get()
        if shortcut:
            self.prompt_manager.delete_prompt(shortcut)
            self.refresh_list()
            self.clear_form()

    def clear_form(self):
        self.shortcut_entry.delete(0, "end")
        self.text_entry.delete("0.0", "end")
        self.main_label.configure(text="Add New Prompt")
        if hasattr(self, 'delete_button'):
            self.delete_button.destroy()
            del self.delete_button

    def setup_settings_section(self):
        """Setup the settings section with background service and startup controls"""
        # Settings frame in sidebar
        self.settings_frame = ctk.CTkFrame(self.sidebar_frame)
        self.settings_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        settings_label = ctk.CTkLabel(self.settings_frame, text="Settings", font=ctk.CTkFont(size=16, weight="bold"))
        settings_label.pack(pady=(10, 5))
        
        # Background Service Section
        bg_service_label = ctk.CTkLabel(self.settings_frame, text="Background Service", font=ctk.CTkFont(size=12, weight="bold"))
        bg_service_label.pack(pady=(5, 2))
        
        self.bg_service_status = ctk.CTkLabel(self.settings_frame, text="Checking...", font=ctk.CTkFont(size=10))
        self.bg_service_status.pack(pady=2)
        
        self.bg_service_button = ctk.CTkButton(
            self.settings_frame,
            text="Start Background Service",
            command=self.toggle_background_service,
            width=150,
            height=30
        )
        self.bg_service_button.pack(pady=5)
        
        # Startup Section
        startup_label = ctk.CTkLabel(self.settings_frame, text="Start on Boot", font=ctk.CTkFont(size=12, weight="bold"))
        startup_label.pack(pady=(10, 2))
        
        self.startup_status = ctk.CTkLabel(self.settings_frame, text="Checking...", font=ctk.CTkFont(size=10))
        self.startup_status.pack(pady=2)
        
        self.startup_button = ctk.CTkButton(
            self.settings_frame,
            text="Enable Startup",
            command=self.toggle_startup,
            width=150,
            height=30
        )
        self.startup_button.pack(pady=5)

    def update_status(self):
        """Update the status of background service and startup"""
        # Check background service
        bg_running = check_background_service_running()
        if bg_running:
            self.bg_service_status.configure(text="Running", text_color="green")
            self.bg_service_button.configure(text="Stop Background Service")
        else:
            self.bg_service_status.configure(text="Stopped", text_color="red")
            self.bg_service_button.configure(text="Start Background Service")
        
        # Check startup
        startup_enabled = check_startup_enabled()
        if startup_enabled:
            self.startup_status.configure(text="Enabled", text_color="green")
            self.startup_button.configure(text="Disable Startup")
        else:
            self.startup_status.configure(text="Disabled", text_color="gray")
            self.startup_button.configure(text="Enable Startup")
        
        # Schedule next update in 3 seconds
        self.after(3000, self.update_status)

    def toggle_background_service(self):
        """Toggle background service on/off"""
        is_running = check_background_service_running()
        
        if is_running:
            # Stop the service
            success, message = stop_background_service()
            if success:
                self.bg_service_status.configure(text="Stopped", text_color="red")
                self.bg_service_button.configure(text="Start Background Service")
            else:
                # Show error message
                self.show_message("Error", message)
        else:
            # Start the service
            success, message = start_background_service()
            if success:
                self.bg_service_status.configure(text="Starting...", text_color="orange")
                # Update status after a short delay
                self.after(2000, self.update_status)
            else:
                # Show error message
                self.show_message("Error", message)

    def toggle_startup(self):
        """Toggle startup on boot"""
        is_enabled = check_startup_enabled()
        
        if is_enabled:
            # Disable startup
            success, message = disable_startup()
            if success:
                self.startup_status.configure(text="Disabled", text_color="gray")
                self.startup_button.configure(text="Enable Startup")
                self.show_message("Success", "Startup on boot has been disabled.")
            else:
                self.show_message("Error", message)
        else:
            # Enable startup
            success, message = enable_startup()
            if success:
                self.startup_status.configure(text="Enabled", text_color="green")
                self.startup_button.configure(text="Disable Startup")
                self.show_message("Success", "Startup on boot has been enabled. The service will start automatically when you log in.")
            else:
                self.show_message("Error", message + "\n\nNote: You may need to run as Administrator to enable startup.")

    def show_message(self, title, message):
        """Show a message dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x150")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        label = ctk.CTkLabel(dialog, text=message, wraplength=350)
        label.pack(pady=20, padx=20)
        
        button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy)
        button.pack(pady=10)

    def on_closing(self):
        self.listener.stop()
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = PromptApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
