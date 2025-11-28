"""
Quick dependency installer for Enterprise AI Data Analyst
"""
import subprocess
import sys


def install_dependencies():
    """Install all required dependencies."""
    print("=" * 80)
    print("  📦 Installing Enterprise AI Data Analyst Dependencies")
    print("=" * 80)
    print()
    
    # Core dependencies in order
    dependencies = [
        # Core first
        "streamlit",
        "pandas",
        "numpy",
        
        # Excel
        "openpyxl",
        
        # Visualization
        "matplotlib",
        "plotly",
        "seaborn",
        
        # Analysis
        "scipy",
        
        # Data validation
        "pydantic",
        "python-dateutil",
        
        # Environment
        "python-dotenv",
        
        # LangChain
        "langchain",
        "langchain-community",
        "langchain-google-genai",
        "google-generativeai",
        
        # CrewAI
        "crewai",
        
        # Other
        "reportlab",
        "typing-extensions",
    ]
    
    for package in dependencies:
        print(f"Installing {package}...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            print(f"  ✅ {package}")
        except subprocess.CalledProcessError:
            print(f"  ⚠️  {package} - trying again...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package]
                )
                print(f"  ✅ {package}")
            except:
                print(f"  ❌ {package} - FAILED")
    
    print()
    print("=" * 80)
    print("  ✅ Installation Complete!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Run: python -m streamlit run app_enterprise.py")
    print("  2. Or: python run_enterprise.py")
    print()


if __name__ == "__main__":
    install_dependencies()
