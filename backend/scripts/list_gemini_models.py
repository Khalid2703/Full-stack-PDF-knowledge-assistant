"""
List available Gemini models to find the correct model name
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("\n" + "="*60)
print("📋 AVAILABLE GEMINI MODELS")
print("="*60)

try:
    models = genai.list_models()
    
    print("\nAll available models:")
    for model in models:
        print(f"\n✅ {model.name}")
        print(f"   Display Name: {model.display_name}")
        print(f"   Description: {model.description}")
        if hasattr(model, 'supported_generation_methods'):
            methods = model.supported_generation_methods
            print(f"   Supports: {', '.join(methods)}")
    
    print("\n" + "="*60)
    print("RECOMMENDED MODELS FOR YOUR USE:")
    print("="*60)
    
    for model in models:
        if 'generateContent' in getattr(model, 'supported_generation_methods', []):
            print(f"✅ {model.name}")
    
except Exception as e:
    print(f"❌ Error listing models: {e}")
