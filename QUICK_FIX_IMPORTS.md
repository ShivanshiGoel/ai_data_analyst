# 🔧 Quick Fix - Missing Dependencies

## Problem
Getting import errors like:
- `No module named 'matplotlib'`
- `No module named 'plotly'`
- `No module named 'seaborn'`
- etc.

## ⚡ Quick Solution

### Option 1: Install All at Once (Recommended)
```bash
pip install -r requirements.txt
```

### Option 2: Use Quick Installer
```bash
python install_dependencies.py
```

### Option 3: Install Manually
```bash
# Core packages
pip install streamlit pandas numpy

# Visualization
pip install matplotlib plotly seaborn

# Excel support
pip install openpyxl

# Data science
pip install scipy

# AI/LLM
pip install langchain langchain-community langchain-google-genai google-generativeai

# CrewAI
pip install crewai

# Other
pip install pydantic python-dotenv reportlab typing-extensions
```

---

## 📋 Complete Dependency List

### Must Have (Required):
```
streamlit       - Web UI framework
pandas          - Data manipulation
numpy           - Numerical computing
matplotlib      - Plotting
plotly          - Interactive charts
openpyxl        - Excel file support
langchain-google-genai - Gemini AI integration
google-generativeai - Google AI SDK
crewai          - Multi-agent framework
python-dotenv   - Environment variables
```

### Important (Highly Recommended):
```
seaborn         - Statistical visualization
scipy           - Scientific computing
pydantic        - Data validation
langchain       - LLM framework
langchain-community - LangChain community tools
```

### Nice to Have (Optional):
```
reportlab       - PDF generation
typing-extensions - Enhanced type hints
python-dateutil - Date utilities
```

---

## 🚀 After Installation

Once dependencies are installed, run:

```bash
python -m streamlit run app_enterprise.py
```

Or:

```bash
python run_enterprise.py
```

---

## 🔍 Verify Installation

```python
# test_imports.py
try:
    import streamlit
    import pandas
    import numpy
    import matplotlib
    import plotly
    import seaborn
    import openpyxl
    import langchain_google_genai
    import crewai
    print("✅ All dependencies installed successfully!")
except ImportError as e:
    print(f"❌ Missing: {e}")
```

Run: `python -c "import streamlit, pandas, matplotlib, plotly; print('✅ Core deps OK')"`

---

## 💡 Troubleshooting

### Issue: pip not found
```bash
python -m ensurepip --upgrade
```

### Issue: Permission denied
```bash
pip install --user -r requirements.txt
```

### Issue: Old packages
```bash
pip install --upgrade -r requirements.txt
```

### Issue: Conflicting versions
```bash
# Create virtual environment
python -m venv venv
# Activate it (Windows)
venv\Scripts\activate
# Activate it (Mac/Linux)
source venv/bin/activate
# Install
pip install -r requirements.txt
```

---

## ✅ After All Dependencies Installed

You should see NO import errors when running:
```bash
python -m streamlit run app_enterprise.py
```

The app will start successfully! 🎉
