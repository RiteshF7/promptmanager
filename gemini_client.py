import google.generativeai as genai
import os
from dotenv import load_dotenv

class GeminiClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        if self.api_key:
            self.configure(self.api_key)

    def configure(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def enhance_prompt(self, text):
        if not self.model:
            return "Error: Gemini API Key not configured."
        
        try:
            prompt = f"""
            You are an expert AI prompt engineer. Your task is to rewrite the following user input into a clear, detailed, and effective prompt for an AI agent.
            
            User Input: "{text}"
            
            Rules:
            1. Keep the intent exactly the same.
            2. Add necessary context or structure if missing.
            3. Make it concise but comprehensive.
            4. Return ONLY the enhanced prompt text, no explanations or quotes.
            5. Do not use line breaks or newlines; keep it as a single paragraph.
            """
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error enhancing prompt: {str(e)}"
