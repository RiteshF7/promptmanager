import google.generativeai as genai
import os
from dotenv import load_dotenv

class GeminiClient:
    def __init__(self):
        # Always load from .env file (override=True to get latest value)
        load_dotenv(override=True)
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        self.model_name = None
        if self.api_key:
            self.configure(self.api_key)

    def configure(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        
        # Automatically detect and use an available model
        self.model_name = self._find_available_model()
        if self.model_name:
            try:
                self.model = genai.GenerativeModel(self.model_name)
                print(f"Using Gemini model: {self.model_name}")
            except Exception as e:
                print(f"Error initializing model {self.model_name}: {str(e)}")
                self.model = None
        else:
            print("Warning: No suitable Gemini model found. Please check your API key.")
            self.model = None
    
    def _find_available_model(self):
        """Find the best available model that supports generateContent"""
        try:
            # List of preferred models in order of preference (fastest/cheapest first)
            preferred_models = [
                'gemini-2.5-flash',      # Latest stable flash (recommended)
                'gemini-2.0-flash',      # Stable flash v2.0
                'gemini-2.0-flash-001',  # Stable flash v2.0 (versioned)
                'gemini-flash-latest',   # Latest flash (alias)
                'gemini-2.5-pro',        # Latest stable pro
                'gemini-pro-latest',     # Latest pro (alias)
                'gemini-2.0-flash-lite', # Lite version (fastest/cheapest)
            ]
            
            # First, try to get the list of available models from API
            try:
                available_models = {}
                for model in genai.list_models():
                    if 'generateContent' in model.supported_generation_methods:
                        model_name = model.name.replace('models/', '')
                        available_models[model_name] = model.display_name
                
                # Try preferred models in order (exact match first)
                for preferred in preferred_models:
                    if preferred in available_models:
                        return preferred
                
                # Try partial matches (e.g., "gemini-2.5-flash" matches "gemini-2.5-flash-001")
                for preferred in preferred_models:
                    # Check if any available model starts with preferred name or contains key parts
                    preferred_parts = preferred.split('-')
                    for available in available_models.keys():
                        available_parts = available.split('-')
                        # Match if first 2-3 parts match and both contain "flash" or both contain "pro"
                        if (len(preferred_parts) >= 2 and len(available_parts) >= 2 and
                            preferred_parts[0] == available_parts[0] and  # "gemini"
                            ('flash' in preferred.lower() and 'flash' in available.lower() or
                             'pro' in preferred.lower() and 'pro' in available.lower())):
                            print(f"Using compatible model: {available} (preferred: {preferred})")
                            return available
                
                # If none of preferred found, use first available flash model
                for available in available_models.keys():
                    if 'flash' in available.lower() and 'latest' not in available.lower():
                        print(f"Using first available flash model: {available}")
                        return available
                
                # Last resort: use first available model
                if available_models:
                    first_model = list(available_models.keys())[0]
                    print(f"Using first available model: {first_model}")
                    return first_model
            except Exception as e:
                print(f"Could not list models from API: {str(e)}")
                # Fall back: try the most common model directly
                try:
                    return 'gemini-2.5-flash'
                except:
                    pass
            
            return None
            
        except Exception as e:
            print(f"Error finding available model: {str(e)}")
            return None

    def enhance_prompt(self, text):
        if not self.model:
            return "Error: Gemini API Key not configured."
        
        try:
            prompt = f"""
            You are an expert AI prompt engineer. Your task is to rewrite the following user input into a clear, detailed, and effective prompt for an AI agent (like Cursor AI) that can execute actions and modify code.
            
            User Input: "{text}"
            
            Important Guidelines:
            1. Transform the input into an INSTRUCTION for the AI agent to EXECUTE an action, not to generate or explain text.
            2. Focus on what the agent should DO, not what it should generate or describe.
            3. If the input asks for a command or code, instruct the agent to execute it, not to generate it.
            4. Add necessary context about what files to work with, what to check, or what conditions to consider.
            5. Make the instruction actionable and specific for an AI coding assistant.
            6. Keep the original intent but make it execution-oriented.
            7. Use imperative mood (e.g., "Create", "Implement", "Modify", "Add") rather than descriptive language.
            8. Do NOT ask the agent to generate commands, code, or explanations - ask it to perform actions.
            
            Examples:
            - Input: "make a git commit" → Output: "Stage all currently modified and new files, then create a git commit with an appropriate commit message based on the changes. Analyze the staged changes to determine a meaningful commit message."
            - Input: "add a button" → Output: "Add a button component to the current file. Determine the appropriate location and styling based on the existing UI patterns."
            - Input: "fix the bug" → Output: "Identify and fix the bug in the current codebase. First analyze the code to locate the issue, then implement the fix."
            
            Return ONLY the enhanced prompt text as a single paragraph, no explanations, no quotes, no markdown formatting.
            """
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error enhancing prompt: {str(e)}"
