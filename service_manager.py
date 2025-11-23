"""
Helper module for managing background service and startup configuration.
"""
import subprocess
import sys
import os

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

def check_background_service_running():
    """Check if the background service is currently running"""
    if PSUTIL_AVAILABLE:
        try:
            script_name = "background_service.py"
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and script_name in ' '.join(cmdline):
                        # Check if it's a Python process running our script
                        if 'python' in proc.info['name'].lower() or any('python' in str(c).lower() for c in cmdline):
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except Exception:
            pass
    
    # Fallback method using tasklist on Windows
    if sys.platform == 'win32':
        try:
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
                capture_output=True, text=True, check=False
            )
            # Check if background_service.py is in the command line
            # This is a simpler check but less reliable
            return 'background_service.py' in result.stdout
        except:
            return False
    return False

def check_startup_enabled():
    """Check if startup task is enabled in Task Scheduler"""
    task_name = "PromptManagerBackgroundService"
    command = ["schtasks", "/Query", "/TN", task_name]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        # Check if task is enabled (not disabled)
        return "Ready" in result.stdout or "Running" in result.stdout
    except subprocess.CalledProcessError:
        return False

def enable_startup():
    """Enable startup on boot"""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "background_service.py")
    python_exe = sys.executable
    task_name = "PromptManagerBackgroundService"
    
    command = [
        "schtasks",
        "/Create",
        "/TN", task_name,
        "/TR", f'"{python_exe}" "{script_path}"',
        "/SC", "ONLOGON",
        "/RL", "HIGHEST",
        "/F"
    ]
    
    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
        return True, "Startup enabled successfully"
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e.stderr}"

def disable_startup():
    """Disable startup on boot"""
    task_name = "PromptManagerBackgroundService"
    command = ["schtasks", "/Delete", "/TN", task_name, "/F"]
    
    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
        return True, "Startup disabled successfully"
    except subprocess.CalledProcessError as e:
        if "does not exist" in str(e.stderr).lower():
            return True, "Startup was not enabled"
        return False, f"Error: {e.stderr}"

def start_background_service():
    """Start the background service"""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "background_service.py")
    python_exe = sys.executable
    
    try:
        # Start in a new process, detached from console
        if sys.platform == 'win32':
            subprocess.Popen(
                [python_exe, script_path],
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
            )
        else:
            subprocess.Popen([python_exe, script_path], start_new_session=True)
        return True, "Background service started"
    except Exception as e:
        return False, f"Error starting service: {str(e)}"

def stop_background_service():
    """Stop the background service"""
    if not PSUTIL_AVAILABLE:
        return False, "psutil is required to stop the background service. Please install it with: pip install psutil"
    
    try:
        script_name = "background_service.py"
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and script_name in ' '.join(cmdline):
                    if 'python' in proc.info['name'].lower() or any('python' in str(c).lower() for c in cmdline):
                        proc.terminate()
                        # Wait a bit for graceful shutdown
                        try:
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            proc.kill()
                        return True, "Background service stopped"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False, "Background service not found"
    except Exception as e:
        return False, f"Error stopping service: {str(e)}"

