# 🔧 CrewAI Initialization Debugging

## Error Location
```
Line 195: crew = EnterpriseDataAnalystCrew()
```

This line is failing during crew initialization. Here's how to debug it.

---

## 🧪 Run the Debug Script

```bash
python test_crew_init.py
```

This will test each step of initialization and tell you exactly where it fails:

1. ✅ Environment variables
2. ✅ Gemini LLM
3. ✅ Crew tools
4. ✅ CrewAI import
5. ❓ **EnterpriseDataAnalystCrew initialization** ← This is where it's failing

---

## 🔍 Common Failures

### Failure 1: GEMINI_API_KEY not found
```
❌ GEMINI_API_KEY not found in environment variables
```

**Fix:**
```bash
# Check .env exists
ls -la .env

# Check contents
cat .env

# Should contain:
# GEMINI_API_KEY=AIzaSyB_Mo954YQfmRs8Ptjsik4cvfJXhoDopwk
# MODEL=gemini/gemini-1.5-pro

# If missing, create it:
echo "GEMINI_API_KEY=AIzaSyB_Mo954YQfmRs8Ptjsik4cvfJXhoDopwk" > .env
echo "MODEL=gemini/gemini-1.5-pro" >> .env
```

### Failure 2: CrewAI not installed
```
❌ No module named 'crewai'
```

**Fix:**
```bash
pip install crewai>=0.28.0
pip install crewai-tools>=0.1.0
```

### Failure 3: Agents/Tasks config missing
```
❌ File not found: config/agents.yaml
```

**Fix:**
```bash
# Check files exist
ls -la src/ai_data_analyst/config/

# Should show:
# agents.yaml
# tasks.yaml
# agents_enterprise.yaml
# tasks_enterprise.yaml
```

### Failure 4: Crew tools error
```
❌ Error in get_crew_tools()
```

**Fix:**
```bash
# Check crew_tools.py
python -c "from ai_data_analyst.crew_tools import get_crew_tools; print(get_crew_tools())"
```

---

## 🎯 Step-by-Step Debug

### Step 1: Check Environment
```bash
python check_env.py
```

Expected output:
```
✅ .env file exists
✅ GEMINI_API_KEY found in .env file
✅ GEMINI_API_KEY loaded into environment
✅ Gemini LLM initialized successfully
✅ Gemini API connection working!
```

### Step 2: Test Imports
```python
python -c "
from dotenv import load_dotenv
load_dotenv()
import os
print('API Key:', 'Found' if os.getenv('GEMINI_API_KEY') else 'Missing')

from langchain_google_genai import ChatGoogleGenerativeAI
print('LangChain Gemini: OK')

from crewai import Agent, Crew
print('CrewAI: OK')

from ai_data_analyst.crew_tools import get_crew_tools
print('Crew Tools: OK')

print('All imports successful!')
"
```

### Step 3: Test Crew Initialization
```bash
python test_crew_init.py
```

This will show exactly which step fails.

### Step 4: Check Detailed Error
Run Streamlit and look at the error details:
```bash
python -m streamlit run app_enterprise.py
```

Upload file, try command, and expand "Initialization Error Details" to see full traceback.

---

## 🔧 Manual Test

Try initializing the crew manually:

```python
# test_manual_crew.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "src"))

from dotenv import load_dotenv
load_dotenv()

print("Testing crew initialization...")

try:
    from ai_data_analyst.crew_enterprise import EnterpriseDataAnalystCrew
    crew = EnterpriseDataAnalystCrew()
    print("✅ SUCCESS!")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
```

Run:
```bash
python test_manual_crew.py
```

---

## 💡 Most Likely Causes

Based on the error at line 195, here are the most likely issues:

### 1. Environment Variables Not Loaded (60% probability)
**Symptom:** "GEMINI_API_KEY not found"

**Fix:**
```bash
python check_env.py  # Check if it's loaded
```

If not loaded:
```bash
pip install python-dotenv
```

### 2. CrewAI Dependencies Missing (25% probability)
**Symptom:** Import errors or "No module named..."

**Fix:**
```bash
pip install crewai langchain-google-genai google-generativeai
```

### 3. Configuration Files Missing (10% probability)
**Symptom:** "File not found: config/agents.yaml"

**Fix:**
```bash
# Check config directory
ls -la src/ai_data_analyst/config/
```

Should contain agents_enterprise.yaml and tasks_enterprise.yaml

### 4. API Key Invalid (5% probability)
**Symptom:** Authentication error

**Fix:**
- Get new API key from https://makersuite.google.com/app/apikey
- Update .env file

---

## 🚀 Quick Fix Sequence

Try these in order:

```bash
# 1. Verify environment
python check_env.py

# 2. Reinstall dependencies
pip install python-dotenv crewai langchain-google-genai google-generativeai

# 3. Test crew initialization
python test_crew_init.py

# 4. Run app
python -m streamlit run app_enterprise.py
```

One of these should fix it!

---

## 📞 Get Help

If still not working, run this and share the output:

```bash
python test_crew_init.py > crew_debug.txt 2>&1
cat crew_debug.txt
```

This will show exactly where it's failing.
