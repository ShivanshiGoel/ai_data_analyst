# 🔧 Error Handling & Troubleshooting Guide

## Common Errors and Fixes

### 1. GEMINI_API_KEY not found

**Error:**
```
ValueError: GEMINI_API_KEY not found in environment variables
```

**Fix:**
```bash
# 1. Check if .env file exists
ls -la .env

# 2. Verify it contains the key
cat .env

# 3. Should show:
# GEMINI_API_KEY=AIzaSy...
# MODEL=gemini/gemini-1.5-pro

# 4. If missing, create it:
echo "GEMINI_API_KEY=your_key_here" > .env
echo "MODEL=gemini/gemini-1.5-pro" >> .env

# 5. Verify setup:
python check_env.py
```

### 2. Import Errors

**Error:**
```
ImportError: No module named 'crewai'
```

**Fix:**
```bash
pip install -r requirements.txt
# or
pip install crewai langchain-google-genai python-dotenv
```

### 3. Schema Errors

**Error:**
```
AttributeError: 'dict' object has no attribute 'columns'
```

**Fix:**
This should now be handled automatically. If you still see it:
1. Reload the file
2. Make sure you're using the latest code
3. Check that TypeInferencer.infer_schema() runs successfully

### 4. CrewAI Execution Errors

**Error:**
```
Error in CrewAI execution: ...
```

**Fix:**
1. Check error details in the expander
2. Verify API key is valid
3. Check internet connection
4. Try a simpler command first: "Show me data summary"

### 5. Data Loading Errors

**Error:**
```
Error loading file: ...
```

**Fix:**
1. Make sure file is .xlsx or .xls
2. Check file isn't corrupted
3. Try opening in Excel first to verify
4. Look at auto-cleaning report for details

---

## 🧪 Diagnostic Tools

### Check Environment
```bash
python check_env.py
```
Shows:
- ✅ .env file exists
- ✅ API key is loaded
- ✅ Gemini connection works

### Quick Test
```bash
python test_quick.py
```
Tests:
- ✅ Schema handling
- ✅ Data cleaner
- ✅ All imports

### Full Test
```bash
pip install -r requirements.txt
python test_enterprise.py
```

---

## 🔍 Debug Mode

To see more details, run with verbose output:

```python
# In app_enterprise.py, add this at top:
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📊 Error Locations

### Line 192 in app_enterprise.py
This is in `execute_ai_command()` - the crew execution line.

**Common causes:**
1. API key not loaded
2. Schema format issue
3. CrewAI initialization failed

**Check:**
```bash
python check_env.py  # Verify API key
```

### CrewAI Import Errors
**Fix:**
```bash
pip install crewai>=0.28.0
pip install crewai-tools>=0.1.0
```

### LangChain Errors
**Fix:**
```bash
pip install langchain>=0.1.6
pip install langchain-google-genai>=1.0.0
pip install google-generativeai>=0.3.0
```

---

## 🆘 Getting Help

### 1. Collect Information
```bash
# Python version
python --version

# Installed packages
pip list | grep -E "(crewai|langchain|google)"

# Check .env
cat .env

# Run diagnostics
python check_env.py > diagnostic.txt
```

### 2. Check Error Details
- Look at the error message in Streamlit
- Expand "Error Details" to see full traceback
- Note which line number failed

### 3. Common Quick Fixes

**Restart Everything:**
```bash
# Stop Streamlit (Ctrl+C)
# Reload .env
# Restart
python -m streamlit run app_enterprise.py
```

**Clear Cache:**
```bash
# In Streamlit UI
# Click "☰" menu → "Clear cache"
# Or press 'c' then 'Enter'
```

**Reinstall Dependencies:**
```bash
pip uninstall crewai langchain-google-genai
pip install crewai langchain-google-genai
```

---

## 💡 Pro Tips

### Tip 1: Test in Stages
```bash
# Test 1: Environment
python check_env.py

# Test 2: Imports
python test_quick.py

# Test 3: Load app
python -m streamlit run app_enterprise.py

# Test 4: Upload small file first
# Test 5: Try simple command
```

### Tip 2: Check Logs
Streamlit shows errors in:
1. Browser console (F12)
2. Terminal where you ran streamlit
3. Error expanders in the UI

### Tip 3: Simplify
If complex command fails:
1. Try: "Show me data"
2. Then: "Clean data"
3. Then: "Analyze data"
4. Then your complex request

---

## 🎯 Error Prevention

### Before Running:
- [ ] `.env` file exists with valid API key
- [ ] All dependencies installed
- [ ] `check_env.py` shows all green
- [ ] Excel file is valid

### When Errors Occur:
- [ ] Read error message carefully
- [ ] Check "Error Details" expander
- [ ] Run diagnostic tools
- [ ] Try simpler operation
- [ ] Check this guide

---

## 📞 Still Having Issues?

1. Run: `python check_env.py > status.txt`
2. Note the error message
3. Check line number in error
4. Look up that section in this guide
5. Try the suggested fixes

Most errors are due to:
- Missing/invalid API key (50%)
- Missing dependencies (30%)
- Data format issues (15%)
- Other (5%)

Run the diagnostic tools to identify which category!
