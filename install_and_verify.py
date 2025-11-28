"""
Complete installation and verification script for Enterprise AI Data Analyst
"""
import subprocess
import sys
import os
from pathlib import Path


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def install_dependencies():
    """Install all required dependencies."""
    print_section("📦 Installing Dependencies")
    
    requirements = [
        "streamlit==1.31.0",
        "crewai[tools]==1.5.0",
        "pandas==2.2.0",
        "numpy==1.26.3",
        "openpyxl==3.1.2",
        "pydantic==2.6.0",
        "matplotlib==3.8.2",
        "plotly==5.18.0",
        "seaborn==0.13.2",
        "scipy>=1.11.0",
        "reportlab==4.1.0",
        "langchain==0.1.6",
        "langchain-community==0.0.20",
        "langchain-google-genai>=1.0.0",
        "google-generativeai>=0.3.0",
        "python-dotenv>=1.0.0",
    ]
    
    print("Installing packages (this may take a few minutes)...\n")
    
    for package in requirements:
        print(f"Installing {package}...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            print(f"  ✅ {package}")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  {package} - trying without constraints...")
            # Try without version constraint
            base_package = package.split('==')[0].split('>=')[0]
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "-q", base_package],
                    stdout=subprocess.DEVNULL
                )
                print(f"  ✅ {base_package} (latest version)")
            except:
                print(f"  ❌ {base_package} failed")
    
    print("\n✅ Dependencies installation complete!")


def verify_installation():
    """Verify installation."""
    print_section("🔍 Verifying Installation")
    
    checks = {
        "Streamlit": "streamlit",
        "CrewAI": "crewai",
        "Pandas": "pandas",
        "NumPy": "numpy",
        "OpenPyXL": "openpyxl",
        "LangChain": "langchain",
        "Gemini LangChain": "langchain_google_genai",
        "Google Generative AI": "google.generativeai",
        "Plotly": "plotly",
        "Matplotlib": "matplotlib",
        "SciPy": "scipy",
    }
    
    all_ok = True
    for name, module in checks.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - NOT INSTALLED")
            all_ok = False
    
    return all_ok


def check_env_config():
    """Check environment configuration."""
    print_section("⚙️  Checking Configuration")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("Creating .env file...")
        
        api_key = input("\nEnter your GEMINI_API_KEY (or press Enter to skip): ").strip()
        if api_key:
            with open(".env", "w") as f:
                f.write(f"GEMINI_API_KEY={api_key}\n")
                f.write("MODEL=gemini/gemini-1.5-pro\n")
            print("✅ .env file created")
        else:
            print("⚠️  Skipped - you'll need to create .env manually")
            return False
    
    # Load .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass
    
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"✅ GEMINI_API_KEY found (length: {len(api_key)})")
        return True
    else:
        print("❌ GEMINI_API_KEY not found in .env")
        print("\nTo fix:")
        print("1. Get API key from: https://makersuite.google.com/app/apikey")
        print("2. Add to .env file: GEMINI_API_KEY=your_key_here")
        return False


def run_tests():
    """Run test suite."""
    print_section("🧪 Running Tests")
    
    print("Running test suite...\n")
    result = subprocess.run(
        [sys.executable, "test_enterprise.py"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode == 0


def main():
    """Main installation flow."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║            🚀 Enterprise AI Data Analyst - Installation Script               ║
║                                                                              ║
║                        Complete Setup & Verification                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    print("This script will:")
    print("  1. Install all required dependencies")
    print("  2. Verify installation")
    print("  3. Check configuration")
    print("  4. Run tests")
    print("  5. Provide next steps")
    
    input("\nPress Enter to continue...")
    
    # Step 1: Install dependencies
    install_dependencies()
    
    # Step 2: Verify installation
    if not verify_installation():
        print("\n❌ Some packages failed to install.")
        print("Try running: pip install -r requirements.py")
        return
    
    # Step 3: Check configuration
    config_ok = check_env_config()
    
    # Step 4: Run tests
    if config_ok:
        tests_ok = run_tests()
    else:
        print("\n⚠️  Skipping tests (configuration incomplete)")
        tests_ok = False
    
    # Final summary
    print_section("📋 Installation Summary")
    
    if tests_ok:
        print("✅ Installation SUCCESSFUL!")
        print("✅ All tests passed!")
        print("✅ System is ready to use!")
        
        print("\n" + "=" * 80)
        print("🎯 Next Steps:")
        print("=" * 80)
        print("\n1. Launch the application:")
        print("   python run_enterprise.py")
        print("\n2. Or use Streamlit directly:")
        print("   streamlit run app_enterprise.py")
        print("\n3. Try sample commands from sample_commands.md")
        print("\n4. Read QUICKSTART.md for detailed guide")
        
    else:
        print("⚠️  Installation complete but tests failed")
        print("\nLikely issues:")
        if not config_ok:
            print("  - GEMINI_API_KEY not configured")
            print("    Get key from: https://makersuite.google.com/app/apikey")
            print("    Add to .env file")
        
        print("\nManual verification:")
        print("  1. Check .env file exists with GEMINI_API_KEY")
        print("  2. Run: python test_enterprise.py")
        print("  3. Check error messages")
    
    print("\n" + "=" * 80)
    print("📚 Documentation:")
    print("=" * 80)
    print("  - QUICKSTART.md - 5-minute getting started guide")
    print("  - ENTERPRISE_README.md - Complete documentation")
    print("  - sample_commands.md - Command examples")
    print("  - MIGRATION_GUIDE.md - Upgrade guide")
    
    print("\n✨ Thank you for using Enterprise AI Data Analyst!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
