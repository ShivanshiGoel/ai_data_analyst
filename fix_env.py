"""Fix and verify .env file."""
import os
from pathlib import Path

print("=" * 60)
print("Environment Variable Fix")
print("=" * 60)

# Check current directory
print(f"\nCurrent directory: {Path.cwd()}")

# Check if .env exists
env_path = Path(".env")
print(f"\nChecking for .env at: {env_path.absolute()}")

if env_path.exists():
    print("✅ .env file exists")
    
    # Read and show content (safely)
    with open(env_path, 'r') as f:
        content = f.read()
    
    print("\nCurrent .env content:")
    print("-" * 40)
    for line in content.split('\n'):
        if line.strip():
            if 'API_KEY' in line:
                # Mask the key
                parts = line.split('=')
                if len(parts) == 2:
                    key_name = parts[0]
                    key_value = parts[1]
                    print(f"{key_name}={key_value[:10]}...{key_value[-5:]}")
            else:
                print(line)
    print("-" * 40)
    
else:
    print("❌ .env file NOT found!")
    print("\n Creating .env file...")
    
    # Create .env with the API key
    
    
    with open(".env", "w") as f:
        f.write(f"GEMINI_API_KEY={api_key}\n")
        f.write("MODEL=gemini/gemini-1.5-pro\n")
    
    print("✅ Created .env file")

# Now test loading
print("\n" + "=" * 60)
print("Testing Environment Loading")
print("=" * 60)

print("\n1. Testing python-dotenv...")
try:
    from dotenv import load_dotenv
    print("✅ python-dotenv imported")
except ImportError:
    print("❌ python-dotenv not installed")
    print("   Install: pip install python-dotenv")
    exit(1)

print("\n2. Loading .env file...")
result = load_dotenv()
print(f"   load_dotenv() returned: {result}")

print("\n3. Checking environment variable...")
api_key = os.getenv('GEMINI_API_KEY')

if api_key:
    print(f"✅ GEMINI_API_KEY loaded!")
    print(f"   Length: {len(api_key)} characters")
    print(f"   Preview: {api_key[:10]}...{api_key[-5:]}")
else:
    print("❌ GEMINI_API_KEY still not in environment")
    print("\nTrying alternative method...")
    
    # Try loading with explicit path
    env_path = Path(".env").absolute()
    result = load_dotenv(env_path)
    print(f"   load_dotenv('{env_path}') returned: {result}")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"✅ GEMINI_API_KEY loaded with explicit path!")
        print(f"   Length: {len(api_key)} characters")
    else:
        print("❌ Still not loaded")
        print("\nManual check - reading .env directly:")
        with open(".env", 'r') as f:
            for line in f:
                if line.startswith('GEMINI_API_KEY'):
                    print(f"   Found in file: {line.strip()}")
        
        print("\n💡 The file exists but python-dotenv isn't loading it.")
        print("   Try running the app from the project root directory.")

print("\n" + "=" * 60)
print("Solution")
print("=" * 60)

if api_key:
    print("\n✅ Environment is working!")
    print("\nYou can now run:")
    print("   python -m streamlit run app_enterprise.py")
else:
    print("\n⚠️  Environment variable not loading")
    print("\nManual fix:")
    print("   1. Close all terminals")
    print("   2. Open new terminal")
    print("   3. cd to project directory")
    print("   4. Run: python -m streamlit run app_enterprise.py")
    print("\nOr set manually:")
    print("   Windows: set GEMINI_API_KEY=AIzaSyB_Mo954YQfmRs8Ptjsik4cvfJXhoDopwk")
    print("   Linux/Mac: export GEMINI_API_KEY=AIzaSyB_Mo954YQfmRs8Ptjsik4cvfJXhoDopwk")
