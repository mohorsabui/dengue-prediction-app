import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv('DEEPSEEK_API_KEY')
print(f"API Key loaded: {API_KEY[:20]}..." if API_KEY else "NO API KEY FOUND")

# Test different configurations
configs = [
    ("https://api.deepseek.com", "Config 1: Without /v1"),
    ("https://api.deepseek.com/v1", "Config 2: With /v1"),
]

for base_url, description in configs:
    print(f"\n{description}")
    print(f"Testing with: {base_url}")
    
    try:
        client = OpenAI(api_key=API_KEY, base_url=base_url)
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "Hello, say 'working'"}
            ],
            max_tokens=20
        )
        
        print(f"✅ SUCCESS! Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}")
        print(f"   Message: {str(e)}")
