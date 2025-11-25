import unittest
from unittest.mock import MagicMock
import json
import os
import tempfile
import threading
import time
from app import app
from keyboard_listener import KeyboardListener
from pynput.keyboard import Key

class TestPromptEnhancement(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # Mock Gemini Client
        self.mock_gemini = MagicMock()
        self.mock_gemini.enhance_prompt.return_value = "Enhanced Prompt"
        
        # Mock Prompt Manager
        self.mock_pm = MagicMock()
        self.mock_pm.get_prompts.return_value = {}
        
        # Initialize Listener with mocks
        self.listener = KeyboardListener(self.mock_pm, self.mock_gemini)
        self.listener.controller = MagicMock() # Mock controller to prevent actual typing

    def test_settings_api(self):
        # Test Save
        response = self.app.post('/api/settings', json={'api_key': 'test_key'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(os.environ.get('GEMINI_API_KEY'), 'test_key')
        
        # Test Get
        response = self.app.get('/api/settings')
        data = json.loads(response.data)
        self.assertEqual(data['api_key'], 'test_key')

    def test_enhancement_trigger(self):
        # Simulate typing "test //enhance"
        self.listener.buffer = "test //enhance"
        
        # Trigger check
        self.listener.check_for_matches()
        
        # Verify Gemini was called
        self.mock_gemini.enhance_prompt.assert_called_with("test")
        
        # Verify Controller typed replacement
        # We expect delete_text called twice (trigger + original) and type called once
        self.assertTrue(self.listener.controller.type.called)
        self.listener.controller.type.assert_called_with("Enhanced Prompt")

    def test_buffer_limit(self):
        # Fill buffer over limit
        self.listener.buffer = "a" * 600
        
        # Simulate a key press to trigger limit check
        class MockKey:
            char = 'b'
        self.listener.on_press(MockKey())
        
        # Buffer should be capped at 500
        self.assertEqual(len(self.listener.buffer), 500)
        self.assertTrue(self.listener.buffer.endswith('b'))

if __name__ == '__main__':
    unittest.main()
