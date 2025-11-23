from flask import Flask, render_template, request, jsonify
from prompt_manager import PromptManager
from keyboard_listener import KeyboardListener
import threading
import os

app = Flask(__name__)
prompt_manager = PromptManager()
listener = KeyboardListener(prompt_manager)

# Start listener in a separate thread to avoid blocking Flask
# Note: pynput listener is already threaded, but we start it here.
listener.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    return jsonify(prompt_manager.get_prompts())

@app.route('/api/prompts', methods=['POST'])
def add_prompt():
    data = request.json
    shortcut = data.get('shortcut')
    text = data.get('text')
    if shortcut and text:
        prompt_manager.add_prompt(shortcut, text)
        return jsonify({"status": "success", "message": "Prompt added"}), 201
    return jsonify({"status": "error", "message": "Invalid data"}), 400

@app.route('/api/prompts/<path:shortcut>', methods=['DELETE'])
def delete_prompt(shortcut):
    prompt_manager.delete_prompt(shortcut)
    return jsonify({"status": "success", "message": "Prompt deleted"})

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False) 
    # use_reloader=False is important to avoid starting two listeners
