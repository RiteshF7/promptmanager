from flask import Flask, render_template, request, jsonify
from prompt_manager import PromptManager
from keyboard_listener import KeyboardListener
from gemini_client import GeminiClient
import threading
import os

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
    return jsonify({"api_key": os.getenv("GEMINI_API_KEY", "")})

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

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False) 
    # use_reloader=False is important to avoid starting two listeners
