import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Read DEEPSEEK_API_KEY from environment
API_KEY = os.getenv('DEEPSEEK_API_KEY')
print(f"API Key loaded: {API_KEY is not None}, length: {len(API_KEY) if API_KEY else 0}")

# Initialize OpenAI-compatible client for DeepSeek API
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

# Test API call
try:
    response = client.chat.completions.create(
        model="deepseek",
        messages=[
            {"role": "user", "content": "Hello"}
        ],
        max_tokens=50,
        timeout=10
    )
    print("API call successful!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"API call failed: {str(e)}")