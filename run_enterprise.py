"""
Quick launcher for Enterprise AI Data Analyst
"""
import subprocess
import sys
from pathlib import Path

def main():
    """Launch the enterprise Streamlit app."""
    app_file = Path(__file__).parent / "app_enterprise.py"
    
    print("🚀 Launching Enterprise AI Data Analyst...")
    print("=" * 80)
    print("Using Gemini AI for intelligent data analysis")
    print("=" * 80)
    
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_file),
        "--theme.primaryColor=#1E88E5",
        "--theme.backgroundColor=#FFFFFF",
        "--theme.secondaryBackgroundColor=#F5F5F5",
        "--theme.textColor=#262730",
        "--theme.font=sans serif"
    ])

if __name__ == "__main__":
    main()
