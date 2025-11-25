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
    return render_template('index.html')

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

@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    return jsonify(prompt_manager.get_prompts())

@app.route('/api/prompts', methods=['POST'])
def add_prompt():
    data = request.json
    shortcut = data.get('shortcut')
    text = data.get('text')
    if shortcut and text:
        try:
            prompt_manager.add_prompt(shortcut, text)
            return jsonify({"status": "success", "message": "Prompt added"}), 201
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 400
    return jsonify({"status": "error", "message": "Invalid data"}), 400

@app.route('/api/prompts/<path:shortcut>', methods=['DELETE'])
def delete_prompt(shortcut):
    prompt_manager.delete_prompt(shortcut)
    return jsonify({"status": "success", "message": "Prompt deleted"})

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False) 
    # use_reloader=False is important to avoid starting two listeners
