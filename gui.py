import customtkinter as ctk
from prompt_manager import PromptManager
from keyboard_listener import KeyboardListener
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
        self.sidebar_frame.grid_rowconfigure(2, weight=1)

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

        self.refresh_list()

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

    def on_closing(self):
        self.listener.stop()
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = PromptApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
