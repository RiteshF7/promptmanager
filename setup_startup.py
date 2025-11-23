"""
Script to add Prompt Manager to Windows startup using Task Scheduler.
Run this script once to enable automatic startup on boot.
"""
import os
import sys
import subprocess
import ctypes

def is_admin():
    """Check if the script is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_script_path():
    """Get the absolute path to the background_service.py script"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "background_service.py")

def create_startup_task():
    """Create a Windows Task Scheduler task to run on startup"""
    script_path = get_script_path()
    python_exe = sys.executable
    
    # Task name
    task_name = "PromptManagerBackgroundService"
    
    # Create the task using schtasks command
    # This will run the background service when user logs in
    command = [
        "schtasks",
        "/Create",
        "/TN", task_name,
        "/TR", f'"{python_exe}" "{script_path}"',
        "/SC", "ONLOGON",  # Run on user logon
        "/RL", "HIGHEST",  # Run with highest privileges (needed for keyboard hooks)
        "/F"  # Force creation (overwrite if exists)
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("✓ Successfully added Prompt Manager to Windows startup!")
        print(f"  Task name: {task_name}")
        print(f"  The service will start automatically when you log in.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error creating startup task: {e.stderr}")
        return False

def remove_startup_task():
    """Remove the Windows Task Scheduler task"""
    task_name = "PromptManagerBackgroundService"
    
    command = [
        "schtasks",
        "/Delete",
        "/TN", task_name,
        "/F"  # Force deletion
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("✓ Successfully removed Prompt Manager from Windows startup!")
        return True
    except subprocess.CalledProcessError as e:
        if "does not exist" in e.stderr.lower():
            print("ℹ Task does not exist (already removed or never created).")
        else:
            print(f"✗ Error removing startup task: {e.stderr}")
        return False

def check_task_exists():
    """Check if the startup task already exists"""
    task_name = "PromptManagerBackgroundService"
    
    command = [
        "schtasks",
        "/Query",
        "/TN", task_name
    ]
    
    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("Prompt Manager - Startup Configuration")
    print("=" * 50)
    
    if not is_admin():
        print("⚠ Warning: This script requires administrator privileges.")
        print("  Please run this script as Administrator for best results.")
        print("  (Right-click and select 'Run as administrator')")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Check if task already exists
    if check_task_exists():
        print("\nℹ Startup task already exists.")
        response = input("Do you want to (r)emove it or (r)ecreate it? (r/c): ")
        if response.lower() == 'r':
            remove_startup_task()
            return
        elif response.lower() == 'c':
            remove_startup_task()
            print()
    
    # Create the startup task
    print("\nSetting up automatic startup...")
    if create_startup_task():
        print("\n✓ Setup complete!")
        print("\nTo test, you can:")
        print("  1. Restart your computer, or")
        print("  2. Run 'background_service.py' manually to start the service now")
    else:
        print("\n✗ Setup failed. Please try running as Administrator.")

if __name__ == "__main__":
    main()

