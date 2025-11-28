# 🔧 Installation Guide

## Quick Installation (Automated)

### One-Command Install
```bash
python install_and_verify.py
```

This will:
1. ✅ Install all dependencies
2. ✅ Verify installation
3. ✅ Check configuration
4. ✅ Run tests
5. ✅ Provide next steps

## Manual Installation

### Prerequisites
- Python 3.10 - 3.13
- pip (Python package manager)
- Internet connection

### Step 1: Install Core Dependencies

```bash
pip install streamlit pandas numpy openpyxl
```

### Step 2: Install AI & LangChain

```bash
pip install crewai[tools]==1.5.0
pip install langchain==0.1.6
pip install langchain-google-genai
pip install google-generativeai
```

### Step 3: Install Data Science Libraries

```bash
pip install matplotlib plotly seaborn scipy
```

### Step 4: Install Additional Tools

```bash
pip install pydantic python-dotenv reportlab
```

### Step 5: Verify Installation

```bash
python test_enterprise.py
```

## Alternative: Using requirements.py

```bash
pip install -r requirements.py
```

## Configuration

### 1. Get Gemini API Key

Visit: https://makersuite.google.com/app/apikey

Click "Create API Key" and copy the key.

### 2. Create .env File

Create a file named `.env` in the project root:

```bash
GEMINI_API_KEY=your_api_key_here
MODEL=gemini/gemini-1.5-pro
```

Or use command line:
```bash
echo "GEMINI_API_KEY=AIzaSy..." > .env
echo "MODEL=gemini/gemini-1.5-pro" >> .env
```

### 3. Verify Configuration

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅ API Key Found' if os.getenv('GEMINI_API_KEY') else '❌ API Key Missing')"
```

## Platform-Specific Instructions

### Windows

```bash
# Using PowerShell
python -m pip install -r requirements.py

# Create .env file
New-Item -Path .env -ItemType File
Add-Content -Path .env -Value "GEMINI_API_KEY=your_key"
Add-Content -Path .env -Value "MODEL=gemini/gemini-1.5-pro"
```

### macOS / Linux

```bash
# Install dependencies
pip3 install -r requirements.py

# Create .env file
cat > .env << EOF
GEMINI_API_KEY=your_key
MODEL=gemini/gemini-1.5-pro
EOF
```

## Troubleshooting

### Issue: pip not found
```bash
# Windows
python -m ensurepip --upgrade

# macOS
python3 -m ensurepip --upgrade

# Linux
sudo apt install python3-pip
```

### Issue: Permission denied
```bash
# Use user installation
pip install --user -r requirements.py
```

### Issue: SSL certificate errors
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.py
```

### Issue: Conflicting dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.py
```

### Issue: CrewAI installation fails
```bash
# Try without tools extra
pip install crewai==0.28.0

# Or install from GitHub
pip install git+https://github.com/joaomdmoura/crewAI.git
```

### Issue: LangChain Google GenAI not found
```bash
pip install --upgrade langchain-google-genai google-generativeai
```

## Verification Checklist

After installation, verify:

- [ ] All packages installed: `python test_enterprise.py`
- [ ] `.env` file exists with API key
- [ ] Can import packages:
  ```python
  python -c "import streamlit, crewai, pandas, langchain_google_genai; print('✅ All imports OK')"
  ```
- [ ] Gemini API key is valid
- [ ] Can launch app: `streamlit run app_enterprise.py`

## Dependency List

### Core Framework
- `streamlit` - Web interface
- `crewai` - Agent orchestration
- `pandas` - Data manipulation
- `numpy` - Numerical computing

### AI & LLM
- `langchain` - LLM framework
- `langchain-google-genai` - Gemini integration
- `google-generativeai` - Google AI SDK

### Data Science
- `scipy` - Statistical analysis
- `matplotlib` - Plotting
- `plotly` - Interactive charts
- `seaborn` - Statistical visualization

### Data Formats
- `openpyxl` - Excel files
- `xlrd` - Old Excel format

### Utilities
- `pydantic` - Data validation
- `python-dotenv` - Environment variables
- `reportlab` - PDF generation

## Minimal Installation (Testing Only)

For quick testing without all features:

```bash
pip install streamlit pandas numpy openpyxl langchain-google-genai google-generativeai python-dotenv
```

This provides basic functionality without visualization and advanced analytics.

## Virtual Environment (Recommended)

### Create Virtual Environment

```bash
# Create
python -m venv ai_analyst_env

# Activate (Windows)
ai_analyst_env\Scripts\activate

# Activate (macOS/Linux)
source ai_analyst_env/bin/activate

# Install dependencies
pip install -r requirements.py
```

### Deactivate

```bash
deactivate
```

## Docker Installation (Advanced)

Coming soon - Docker container with all dependencies pre-installed.

## Uninstallation

To remove the system:

```bash
# Uninstall packages
pip uninstall -y streamlit crewai pandas numpy openpyxl langchain langchain-google-genai google-generativeai

# Remove files
rm -rf src/ app_enterprise.py run_enterprise.py .env
```

## Update Installation

To update to latest versions:

```bash
pip install --upgrade -r requirements.py
```

## Support

If installation fails:
1. Check Python version: `python --version` (should be 3.10-3.13)
2. Check pip version: `pip --version`
3. Try virtual environment (see above)
4. Check error messages carefully
5. Verify internet connection

## Post-Installation

After successful installation:
1. Read QUICKSTART.md
2. Run `python test_enterprise.py`
3. Launch app: `python run_enterprise.py`
4. Try sample commands from sample_commands.md
