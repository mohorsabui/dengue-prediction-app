import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv('GEMINI_API_KEY')
print(f"API Key loaded: {API_KEY[:30]}..." if API_KEY else "NO API KEY FOUND")

try:
    genai.configure(api_key=API_KEY)
    print("✅ Gemini configured successfully")
    
    # List available models
    print("\nAvailable models:")
    for model in genai.list_models():
        print(f"  - {model.name}")
    
    # Test a simple request
    print("\nTesting generate_content()...")
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content("Say 'hello'")
    print(f"✅ SUCCESS: {response.text}")
    
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}")
    print(f"   Message: {str(e)}")
    
    if "429" in str(e):
        print("\n⚠️  QUOTA EXCEEDED - Solutions:")
        print("   1. Go to Google Cloud Console")
        print("   2. Enable billing for your project")
        print("   3. Check Generative Language API quotas")
        print("   4. Wait a bit and try again")
    elif "403" in str(e) or "PERMISSION" in str(e):
        print("\n⚠️  PERMISSION ERROR - Solutions:")
        print("   1. Enable Generative Language API in GCP")
        print("   2. Create a new API key")
        print("   3. Verify API key has correct permissions")
