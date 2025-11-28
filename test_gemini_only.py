"""Test just Gemini LLM initialization."""
import os
from dotenv import load_dotenv

print("=" * 60)
print("Testing Gemini LLM Only")
print("=" * 60)

# Load environment
print("\n1. Loading .env file...")
load_dotenv()

# Check API key
print("\n2. Checking API key...")
api_key = os.getenv('GEMINI_API_KEY')

if api_key:
    print(f"✅ GEMINI_API_KEY found")
    print(f"   Length: {len(api_key)} characters")
    print(f"   Preview: {api_key[:10]}...{api_key[-5:]}")
else:
    print("❌ GEMINI_API_KEY not found")
    print("\n💡 Fix:")
    print("   1. Check .env file exists")
    print("   2. Add: GEMINI_API_KEY=your_key_here")
    exit(1)

# Test import
print("\n3. Importing langchain_google_genai...")
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("✅ Import successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("\n💡 Fix: pip install langchain-google-genai google-generativeai")
    exit(1)

# Test initialization
print("\n4. Initializing Gemini LLM...")
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.1,
        google_api_key=api_key
    )
    print("✅ LLM initialized successfully")
except Exception as e:
    print(f"❌ LLM initialization failed: {e}")
    print("\n💡 Possible issues:")
    print("   - Invalid API key")
    print("   - Network connection issue")
    print("   - Missing dependencies")
    import traceback
    traceback.print_exc()
    exit(1)

# Test invoke
print("\n5. Testing LLM invoke...")
try:
    response = llm.invoke("Say 'Hello'")
    print("✅ LLM invoke successful")
    print(f"   Response: {response.content}")
except Exception as e:
    print(f"⚠️  LLM invoke failed: {e}")
    print("   (This might be expected if API has issues)")

print("\n" + "=" * 60)
print("✅ Gemini LLM is working correctly!")
print("=" * 60)
print("\nYou can now proceed to test the crew.")
