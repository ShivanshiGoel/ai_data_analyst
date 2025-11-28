"""Test the updated application."""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("🧪 Testing updated application with Gemini 2.5 Pro\n")

# Test 1: Load environment
print("1️⃣ Testing environment loading...")
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
model = os.getenv('MODEL')
print(f"   ✅ API Key: {'Found' if api_key else 'Missing'}")
print(f"   ✅ Model: {model}\n")

# Test 2: Initialize simple crew
print("2️⃣ Testing Simple Crew initialization...")
try:
    from ai_data_analyst.crew_simple import SimpleDataAnalystCrew
    crew = SimpleDataAnalystCrew()
    print(f"   ✅ Crew initialized successfully\n")
except Exception as e:
    print(f"   ❌ Failed: {e}\n")
    sys.exit(1)

# Test 3: Test LLM directly
print("3️⃣ Testing LLM invocation...")
try:
    response = crew.llm.invoke("Say 'test successful' in 2 words")
    print(f"   ✅ LLM Response: {response.content}\n")
except Exception as e:
    print(f"   ❌ Failed: {e}\n")
    sys.exit(1)

print("🎉 All tests passed! Your application is ready to use with Gemini 2.5 Pro")
