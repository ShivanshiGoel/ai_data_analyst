"""Test script to verify new Gemini model."""
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

# Test with the stable Gemini 2.5 Pro
print("🧪 Testing model: gemini-2.5-pro")
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0.1,
        google_api_key=api_key
    )
    # Try a simple invocation
    response = llm.invoke("Say 'hello' in one word")
    print(f"✅ SUCCESS: {response.content}")
except Exception as e:
    print(f"❌ FAILED: {str(e)}")
