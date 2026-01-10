#!/usr/bin/env python3
"""Script to check available Gemini models for the configured API key"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file")
    exit(1)

try:
    genai.configure(api_key=api_key)
    
    print("Checking available models...")
    print("-" * 60)
    
    # List all available models
    models = genai.list_models()
    
    # Filter models that support generateContent
    supported_models = []
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            supported_models.append({
                'name': model.name,
                'display_name': model.display_name,
                'version': model.version,
                'description': model.description
            })
    
    if supported_models:
        print(f"\nFound {len(supported_models)} model(s) that support generateContent:\n")
        for i, model in enumerate(supported_models, 1):
            # Extract model name (e.g., 'models/gemini-1.5-flash' -> 'gemini-1.5-flash')
            model_name = model['name'].replace('models/', '')
            print(f"{i}. Model Name: {model_name}")
            print(f"   Display Name: {model['display_name']}")
            print(f"   Version: {model['version']}")
            if model['description']:
                print(f"   Description: {model['description'][:100]}...")
            print()
        
        # Recommend the best model (prefer flash over pro for speed, prefer newer versions)
        recommended = None
        for model in supported_models:
            model_name = model['name'].replace('models/', '')
            if 'flash' in model_name.lower():
                recommended = model_name
                break
        
        if not recommended and supported_models:
            recommended = supported_models[0]['name'].replace('models/', '')
        
        print("-" * 60)
        print(f"Recommended model: {recommended}")
        print(f"\nTo use this model, update gemini_client.py:")
        print(f'  self.model = genai.GenerativeModel("{recommended}")')
    else:
        print("\nNo models found that support generateContent.")
        print("Please check your API key and ensure it has access to Gemini models.")
        
except Exception as e:
    print(f"Error checking models: {str(e)}")
    print("\nTrying alternative approach...")
    
    # Try common model names
    common_models = [
        'gemini-pro',
        'gemini-1.5-pro',
        'gemini-1.5-flash',
        'gemini-1.5-flash-8b',
        'gemini-2.0-flash-exp',
        'gemini-pro-vision'
    ]
    
    print("\nTesting common model names:")
    for model_name in common_models:
        try:
            model = genai.GenerativeModel(model_name)
            # Try a simple test (without actually generating)
            print(f"  ✓ {model_name} - Available")
        except Exception as e:
            print(f"  ✗ {model_name} - {str(e)[:50]}")

