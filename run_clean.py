"""Run Streamlit with warnings suppressed."""
import os
import subprocess
import sys
import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")
os.environ['PYTHONWARNINGS'] = 'ignore'

# Set environment
os.environ['GEMINI_API_KEY'] = 'AIzaSyB_Mo954YQfmRs8Ptjsik4cvfJXhoDopwk'
os.environ['MODEL'] = 'gemini/gemini-1.5-pro'

print("=" * 60)
print("🚀 Starting App (Clean - No Warnings)")
print("=" * 60)
print("\n✅ Environment set")
print("✅ Warnings suppressed")
print("\n🌐 Opening browser...\n")

# Run streamlit
subprocess.run([
    sys.executable,
    "-m",
    "streamlit",
    "run",
    "app_enterprise.py",
    "--logger.level=error"  # Only show errors
])
