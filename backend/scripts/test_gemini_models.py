"""
Quick test to find working Gemini model
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"\n🔑 Using API key: {api_key[:10]}...{api_key[-4:]}")

genai.configure(api_key=api_key)

print("\n" + "="*60)
print("🧪 TESTING GEMINI MODELS")
print("="*60)

# List of models to try
models_to_try = [
    "models/gemini-1.5-flash",
    "gemini-1.5-flash", 
    "models/gemini-1.5-flash-latest",
    "gemini-1.5-flash-latest",
    "models/gemini-pro",
    "gemini-pro",
    "models/gemini-1.5-pro",
    "gemini-1.5-pro"
]

working_model = None

for model_name in models_to_try:
    print(f"\n🧪 Testing: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say hello")
        print(f"   ✅ WORKS! Response: {response.text[:50]}...")
        if not working_model:
            working_model = model_name
    except Exception as e:
        error = str(e)
        if "404" in error:
            print(f"   ❌ Not found")
        elif "permission" in error.lower():
            print(f"   ❌ Permission denied")
        else:
            print(f"   ❌ Error: {error[:100]}")

print("\n" + "="*60)
if working_model:
    print(f"✅ WORKING MODEL FOUND: {working_model}")
    print("\nUpdate your .env file:")
    print(f"LLM_MODEL={working_model}")
else:
    print("❌ No working model found!")
    print("\nTrying to list available models...")
    try:
        models = genai.list_models()
        print("\n📋 Available models:")
        for m in models:
            if 'generateContent' in getattr(m, 'supported_generation_methods', []):
                print(f"   - {m.name}")
    except Exception as e:
        print(f"   Error: {e}")

print("="*60)
