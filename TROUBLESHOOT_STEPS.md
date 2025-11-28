# 🔍 Troubleshooting Steps - Line by Line

## Current Error
```
self.llm = self._initialize_llm()
```

This means the LLM initialization is failing in the simplified crew.

---

## 🧪 Debug Steps (Run These In Order)

### Step 1: Test Environment Only
```bash
python check_env.py
```

**Look for:**
- ✅ .env file exists
- ✅ GEMINI_API_KEY loaded
- If ❌, create .env file with your API key

### Step 2: Test Gemini LLM Only
```bash
python test_gemini_only.py
```

**This tests:**
- ✅ API key loads
- ✅ langchain-google-genai imports
- ✅ ChatGoogleGenerativeAI initializes
- ✅ Can invoke Gemini

**If this fails, the problem is:**
- Missing or invalid API key
- Missing dependencies
- Network issues

### Step 3: Test Simple Crew
```bash
python test_simple_crew.py
```

**This tests:**
- ✅ Crew imports
- ✅ Crew initializes
- ✅ Agents created

**If Step 2 passes but Step 3 fails:**
- Issue is in crew initialization
- Check agent creation code

### Step 4: Run App
```bash
python -m streamlit run app_enterprise.py
```

---

## 🔧 Common Fixes

### Fix 1: API Key Not Loading
```bash
# Check .env exists
cat .env

# Should show:
# GEMINI_API_KEY=AIzaSyB_Mo954YQfmRs8Ptjsik4cvfJXhoDopwk
# MODEL=gemini/gemini-1.5-pro

# If not, create it:
echo "GEMINI_API_KEY=AIzaSyB_Mo954YQfmRs8Ptjsik4cvfJXhoDopwk" > .env
echo "MODEL=gemini/gemini-1.5-pro" >> .env
```

### Fix 2: Missing Dependencies
```bash
pip install python-dotenv langchain-google-genai google-generativeai
```

### Fix 3: Import Error
```bash
pip install crewai --upgrade
pip install langchain langchain-google-genai --upgrade
```

### Fix 4: Invalid API Key
- Go to https://makersuite.google.com/app/apikey
- Create new API key
- Update .env file

---

## 📊 Decision Tree

```
Run: python test_gemini_only.py
│
├─ ❌ Fails at "Loading .env"
│   └─> Install: pip install python-dotenv
│
├─ ❌ Fails at "API key not found"
│   └─> Create .env file with GEMINI_API_KEY
│
├─ ❌ Fails at "Import"
│   └─> Install: pip install langchain-google-genai
│
├─ ❌ Fails at "LLM initialization"
│   └─> Check API key is valid
│
└─ ✅ All pass
    └─> Run: python test_simple_crew.py
        │
        ├─ ❌ Fails
        │   └─> Share error output
        │
        └─ ✅ Pass
            └─> Run app: python -m streamlit run app_enterprise.py
```

---

## 💡 What Each Test Does

### test_gemini_only.py
- **Purpose:** Test ONLY Gemini LLM
- **Why:** Isolate if problem is with API key/LLM
- **Fast:** Takes 5 seconds
- **Critical:** Must pass before moving forward

### test_simple_crew.py
- **Purpose:** Test full crew with agents
- **Why:** Test if crew initialization works
- **Slower:** Takes 10-15 seconds
- **Important:** Shows if agents can be created

### test_crew_init.py
- **Purpose:** Test step-by-step initialization
- **Why:** Shows exactly which step fails
- **Comprehensive:** Tests everything
- **Detailed:** Shows progress at each step

---

## 🎯 Quick Diagnosis

**Run this ONE command:**
```bash
python test_gemini_only.py && echo "LLM OK" && python test_simple_crew.py && echo "CREW OK"
```

**If you see:**
- `✅ LLM OK` → Gemini works
- `✅ CREW OK` → Everything works, run the app!

**If you see:**
- `❌` followed by error → That's where the problem is

---

## 📞 Share This Info

If still not working, run and share output:

```bash
python test_gemini_only.py > diagnosis.txt 2>&1
cat diagnosis.txt
```

This will show exactly what's failing!

---

## ✅ Expected Success Output

```bash
$ python test_gemini_only.py

Testing Gemini LLM Only
========================

1. Loading .env file...
✅ 

2. Checking API key...
✅ GEMINI_API_KEY found
   Length: 39 characters
   Preview: AIzaSyB_Mo...opwk

3. Importing langchain_google_genai...
✅ Import successful

4. Initializing Gemini LLM...
✅ LLM initialized successfully

5. Testing LLM invoke...
✅ LLM invoke successful
   Response: Hello

✅ Gemini LLM is working correctly!
```

Then:

```bash
$ python test_simple_crew.py

Testing SimpleDataAnalystCrew
==============================

1. Loading environment...
✅ API key found (39 chars)

2. Importing SimpleDataAnalystCrew...
✅ Import successful

3. Creating crew instance...
🔧 Initializing Gemini LLM...
✅ LLM initialized
🔧 Creating agents...
✅ Created 3 agents
✅ Crew created successfully!

✅ SimpleDataAnalystCrew is working!
```

If you see this, the app will work!

---

## 🚀 Next Steps

1. Run: `python test_gemini_only.py`
2. If passes, run: `python test_simple_crew.py`  
3. If passes, run: `python -m streamlit run app_enterprise.py`
4. If any fail, share the error output!
