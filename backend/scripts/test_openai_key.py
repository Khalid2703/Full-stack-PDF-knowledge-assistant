"""
Quick script to test OpenAI API key validity
Run this to verify if a new key from your senior works
"""

import os
from openai import OpenAI

def test_openai_key(api_key):
    """Test if OpenAI API key is valid"""
    print("\n" + "="*60)
    print("🔑 OPENAI API KEY TESTER")
    print("="*60)
    
    if not api_key:
        print("❌ No API key provided")
        return False
    
    # Mask the key for display
    if len(api_key) > 20:
        masked = api_key[:10] + "..." + api_key[-8:]
    else:
        masked = "***"
    
    print(f"Testing key: {masked}")
    print()
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Test 1: List models
        print("📋 Test 1: Listing models...")
        models = client.models.list()
        print("✅ Can access models list")
        
        # Test 2: Simple generation
        print("\n💬 Test 2: Test generation...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Say 'Hello, API key is valid!'"}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ Generation successful!")
        print(f"📝 Response: {result}")
        
        # Test 3: Check usage
        print("\n📊 Test 3: Checking key info...")
        print(f"✅ Model used: {response.model}")
        print(f"✅ Tokens used: {response.usage.total_tokens}")
        
        print("\n" + "="*60)
        print("🎉 API KEY IS VALID!")
        print("="*60)
        print("\nYou can use this key in your .env file:")
        print(f"OPENAI_API_KEY={api_key}")
        print("="*60)
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ API KEY TEST FAILED")
        print(f"Error: {error_msg}")
        
        if "401" in error_msg or "invalid" in error_msg.lower():
            print("\n💡 This key is INVALID. Possible reasons:")
            print("   1. Key was revoked or deleted")
            print("   2. Key has expired")
            print("   3. Copy-paste error (extra/missing characters)")
            print("   4. Wrong key type (needs chat completion access)")
        
        elif "429" in error_msg or "quota" in error_msg.lower():
            print("\n💡 Key is VALID but quota exceeded")
            print("   The key works, just out of credits/quota")
        
        else:
            print("\n💡 Unexpected error. Check:")
            print("   1. Internet connection")
            print("   2. OpenAI service status")
            print("   3. Key permissions")
        
        print("\n" + "="*60)
        return False


if __name__ == "__main__":
    import sys
    
    print("\n🔧 OpenAI API Key Tester")
    print("=" * 60)
    
    # Try from command line argument
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        print("Using key from command line argument")
    else:
        # Try from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            print("Using key from OPENAI_API_KEY environment variable")
        else:
            # Ask for input
            print("\nNo key provided. You can:")
            print("1. Run: python test_openai_key.py YOUR_API_KEY")
            print("2. Set environment: $env:OPENAI_API_KEY='YOUR_KEY'")
            print("3. Enter key now:")
            api_key = input("\nEnter OpenAI API key: ").strip()
    
    if api_key:
        test_openai_key(api_key)
    else:
        print("\n❌ No API key provided!")
        print("Exiting...")
