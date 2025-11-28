"""Test script to verify correct Gemini model name."""
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key found: {bool(api_key)}")

# Try different model names
model_names = [
    "gemini-1.5-pro",
    "models/gemini-1.5-pro",
    "gemini-1.5-pro-latest",
    "models/gemini-1.5-pro-latest"
]

for model_name in model_names:
    print(f"\n🧪 Testing model: {model_name}")
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.1,
            google_api_key=api_key
        )
        # Try a simple invocation
        response = llm.invoke("Say 'hello' in one word")
        print(f"   ✅ SUCCESS: {response.content}")
        break
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)[:100]}")
