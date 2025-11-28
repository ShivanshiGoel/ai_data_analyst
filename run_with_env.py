"""Run Streamlit with environment variables explicitly set."""
import os
import subprocess
import sys
from pathlib import Path

print("=" * 60)
print("Running Streamlit with Environment")
print("=" * 60)

# Set environment variables directly
print("\n1. Setting environment variables...")

os.environ['MODEL'] = 'gemini/gemini-1.5-pro'

print("✅ GEMINI_API_KEY set")
print("✅ MODEL set")

# Verify
api_key = os.getenv('GEMINI_API_KEY')
print(f"\n2. Verifying: API key length = {len(api_key)} chars")

# Run streamlit
print("\n3. Starting Streamlit...")
print("-" * 60)

app_file = Path("app_enterprise.py")
if not app_file.exists():
    print(f"❌ {app_file} not found")
    print(f"   Current directory: {Path.cwd()}")
    sys.exit(1)

# Run streamlit with inherited environment
subprocess.run([
    sys.executable,
    "-m",
    "streamlit",
    "run",
    str(app_file)
])
