"""Quick script to check environment variables."""
import os
from pathlib import Path

print("=" * 60)
print("Environment Variable Check")
print("=" * 60)

# Check if .env file exists
env_file = Path(".env")
if env_file.exists():
    print("✅ .env file exists")
    print(f"   Location: {env_file.absolute()}")
    print(f"   Size: {env_file.stat().st_size} bytes")
    
    # Read and display (masked)
    with open(env_file, 'r') as f:
        content = f.read()
        if 'GEMINI_API_KEY' in content:
            print("✅ GEMINI_API_KEY found in .env file")
        else:
            print("❌ GEMINI_API_KEY NOT found in .env file")
else:
    print("❌ .env file NOT found")
    print("   Expected location:", env_file.absolute())

print("\n" + "=" * 60)
print("Checking Environment Variables")
print("=" * 60)

# Try loading with python-dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ python-dotenv loaded")
except ImportError:
    print("❌ python-dotenv not installed")
    print("   Install: pip install python-dotenv")

# Check if key is in environment
api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    print(f"✅ GEMINI_API_KEY loaded into environment")
    print(f"   Key length: {len(api_key)} characters")
    print(f"   Key preview: {api_key[:10]}...{api_key[-5:]}")
else:
    print("❌ GEMINI_API_KEY NOT in environment")
    print("\nTo fix:")
    print("1. Create .env file in project root")
    print("2. Add: GEMINI_API_KEY=your_key_here")
    print("3. Or run: echo 'GEMINI_API_KEY=your_key' > .env")

print("\n" + "=" * 60)
print("Testing Gemini Connection")
print("=" * 60)

if api_key:
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.1,
            google_api_key=api_key
        )
        print("✅ Gemini LLM initialized successfully")
        
        # Try a simple test
        try:
            response = llm.invoke("Say 'test successful'")
            print("✅ Gemini API connection working!")
            print(f"   Response: {response.content}")
        except Exception as e:
            print(f"⚠️  Gemini initialized but API call failed: {e}")
            
    except Exception as e:
        print(f"❌ Gemini initialization failed: {e}")
else:
    print("⚠️  Skipping Gemini test (no API key)")

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)

if env_file.exists() and api_key:
    print("✅ Everything is configured correctly!")
    print("   You can run: python -m streamlit run app_enterprise.py")
else:
    print("❌ Configuration needed:")
    if not env_file.exists():
        print("   1. Create .env file")
    if not api_key:
        print("   2. Add GEMINI_API_KEY to .env")

print("=" * 60)
