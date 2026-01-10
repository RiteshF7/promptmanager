from flask import Flask, render_template, request, jsonify
from prompt_manager import PromptManager
from keyboard_listener import KeyboardListener
from gemini_client import GeminiClient
import threading
import os
import sys
from dotenv import load_dotenv

# Load .env file at startup
load_dotenv()

# Determine template and static folders
# When installed from wheel, data files are in site-packages/promptmanager-1.0.0.data/data/
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

# Check if running from installed package (wheel)
try:
    import pkg_resources
    # Try to find data directory from installed package
    dist = pkg_resources.get_distribution('promptmanager')
    if dist:
        # Get the data directory from the installed package
        data_dir = os.path.join(dist.location, 'promptmanager-1.0.0.data', 'data')
        installed_template_dir = os.path.join(data_dir, 'templates')
        installed_static_dir = os.path.join(data_dir, 'static')
        if os.path.exists(installed_template_dir):
            template_dir = installed_template_dir
            static_dir = installed_static_dir
except:
    # Running from development - use default paths
    pass

# Create Flask app with appropriate template/static folders
if os.path.exists(template_dir) and os.path.exists(static_dir):
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
else:
    # Fallback to default Flask behavior (looks in templates/ and static/ relative to app.py)
    app = Flask(__name__)

prompt_manager = PromptManager()
gemini_client = GeminiClient()
listener = KeyboardListener(prompt_manager, gemini_client)

# Start listener in a separate thread to avoid blocking Flask
# Note: pynput listener is already threaded, but we start it here.
listener.start()

@app.route('/')
def index():
    return render_template('add.html')

@app.route('/existing')
def existing_prompts_page():
    return render_template('existing.html')

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/api/settings', methods=['GET'])
def get_settings():
    # Always reload from .env file to get the latest value
    load_dotenv(override=True)  # override=True ensures we read fresh from .env
    api_key = os.getenv("GEMINI_API_KEY", "")
    return jsonify({"api_key": api_key})

@app.route('/api/settings', methods=['POST'])
def save_settings():
    data = request.json
    api_key = data.get('api_key')
    if api_key:
        # Update .env file
        with open('.env', 'w') as f:
            f.write(f"GEMINI_API_KEY={api_key}")
        
        # Update current process environment and client
        os.environ["GEMINI_API_KEY"] = api_key
        gemini_client.configure(api_key)
        
        return jsonify({"status": "success", "message": "Settings saved"})
    return jsonify({"status": "error", "message": "Invalid API Key"}), 400

@app.route('/api/prompts/defaults', methods=['GET'])
def get_default_prompts():
    """Get default prompts from prompts.json file"""
    return jsonify(prompt_manager.get_prompts())

@app.route('/api/prompts/sync', methods=['POST'])
def sync_prompts():
    """Sync prompts from browser to server for keyboard listener"""
    try:
        if not request.json:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        
        prompts = request.json.get('prompts', {})
        if not isinstance(prompts, dict):
            return jsonify({"status": "error", "message": "Invalid prompts format"}), 400
        
        # Update the prompt manager with synced prompts
        # Clear existing and add all synced prompts
        with prompt_manager.lock:
            prompt_manager.prompts = prompts.copy()
        prompt_manager.save_prompts()
        
        return jsonify({"status": "success", "message": "Prompts synced successfully"})
    except Exception as e:
        import traceback
        print(f"Error syncing prompts: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": f"Failed to sync prompts: {str(e)}"}), 500

@app.route('/api/prompts/track-usage', methods=['POST'])
def track_usage():
    """Track prompt usage for recently used feature"""
    try:
        if not request.json:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        
        shortcut = request.json.get('shortcut')
        if not shortcut:
            return jsonify({"status": "error", "message": "Shortcut not provided"}), 400
        
        # This endpoint is called by the keyboard listener when a shortcut is used
        # The frontend will handle storing it in localStorage
        return jsonify({"status": "success", "message": "Usage tracked"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to track usage: {str(e)}"}), 500

@app.route('/api/keyboard/status', methods=['GET'])
def keyboard_status():
    """Check keyboard listener status"""
    try:
        # Check if listener is running
        is_running = False
        if listener.running and listener.listener is not None:
            try:
                # pynput listener has a running property
                is_running = getattr(listener.listener, 'running', False)
            except:
                # Fallback: if listener exists and running flag is True, assume it's running
                is_running = listener.running
        
        # Detect session type
        session_type = os.environ.get('XDG_SESSION_TYPE', 'unknown')
        is_wayland = session_type == 'wayland'
        
        status = "running" if is_running else "stopped"
        
        return jsonify({
            "status": status,
            "running": is_running,
            "session_type": session_type,
            "is_wayland": is_wayland,
            "message": "Keyboard listener is running" if is_running else "Keyboard listener is not running"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "running": False,
            "session_type": os.environ.get('XDG_SESSION_TYPE', 'unknown'),
            "is_wayland": os.environ.get('XDG_SESSION_TYPE') == 'wayland',
            "message": f"Error checking status: {str(e)}"
        }), 500

def main():
    """Entry point for the application"""
    app.run(debug=True, port=5000, use_reloader=False) 
    # use_reloader=False is important to avoid starting two listeners

if __name__ == '__main__':
    main()
