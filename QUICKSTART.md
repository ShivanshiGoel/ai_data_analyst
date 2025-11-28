# ⚡ Quick Start Guide

Get up and running with Enterprise AI Data Analyst in 5 minutes!

## 📋 Prerequisites

- Python 3.10 - 3.13
- Gemini API Key (free from Google)
- Excel file with data

## 🚀 Installation (3 minutes)

### Step 1: Clone/Download

```bash
# If you have the code, navigate to the directory
cd ai_data_analyst
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.py
```

Or install individually:
```bash
pip install streamlit crewai pandas openpyxl langchain-google-genai google-generativeai scipy python-dotenv
```

### Step 3: Get Gemini API Key

1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

### Step 4: Configure

Create a `.env` file in the project root:

```bash
GEMINI_API_KEY=AIzaSy...your_key_here
MODEL=gemini/gemini-1.5-pro
```

Or use command line:
```bash
echo "GEMINI_API_KEY=your_key_here" > .env
echo "MODEL=gemini/gemini-1.5-pro" >> .env
```

## ✅ Verify Installation

Run the test suite:

```bash
python test_enterprise.py
```

You should see: ✅ All tests passed!

## 🎯 First Run (2 minutes)

### Method 1: Quick Launcher (Recommended)

```bash
python run_enterprise.py
```

### Method 2: Direct Streamlit

```bash
streamlit run app_enterprise.py
```

### Method 3: CLI Mode

```bash
python src/ai_data_analyst/main_enterprise.py your_data.xlsx "analyze sales trends"
```

## 📊 Your First Analysis

1. **Upload Data**
   - Click "Browse files" in the sidebar
   - Select your Excel file
   - Click "🔄 Load File"

2. **Run Analysis**
   - In the "🤖 AI Data Commands" box, type:
   ```
   Clean the data and show me key statistics
   ```
   - Click "⚡ Execute"

3. **View Results**
   - Check the tabs: Data, Analytics, Schema, History
   - See KPIs, cleaned data, and insights

## 💡 Try These Commands

**Data Cleaning:**
```
Remove duplicates and fix missing values
```

**Analysis:**
```
Show me top 10 items by sales
```

**Advanced:**
```
Calculate month-over-month growth
```

**Visualization:**
```
Create a dashboard with sales metrics
```

## 🎨 Example Workflows

### Workflow 1: Quick Data Quality Check
```
1. Upload file
2. Type: "Clean this data"
3. Type: "Show me data quality issues"
4. Export cleaned data
```

### Workflow 2: Sales Analysis
```
1. Upload sales data
2. Type: "Show top 10 customers by revenue"
3. Type: "Calculate year-over-year growth"
4. Type: "Create a sales dashboard"
```

### Workflow 3: Trend Analysis
```
1. Upload time series data
2. Type: "Analyze trends over time"
3. Type: "Calculate moving averages"
4. Type: "Forecast next quarter"
```

## 🔧 Troubleshooting

### Issue: "GEMINI_API_KEY not found"
**Solution:** Make sure `.env` file exists in project root with your API key

### Issue: Import errors
**Solution:** 
```bash
pip install -r requirements.py --upgrade
```

### Issue: Slow responses
**Solution:** First run is slower due to model loading. Subsequent runs are faster.

### Issue: "LLM not configured"
**Solution:** Check that your Gemini API key is valid and has credits

## 📚 What's Next?

- Read [ENTERPRISE_README.md](ENTERPRISE_README.md) for full documentation
- Check [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) if upgrading
- Explore advanced operations in the app
- Try complex natural language queries

## 🎓 Learning Path

1. **Day 1:** Basic cleaning and analysis
2. **Day 2:** Advanced operations (pivot, cohorts, ABC)
3. **Day 3:** Natural language mastery
4. **Day 4:** Dashboard creation
5. **Day 5:** Production deployment

## 💬 Example Natural Language Commands

The system understands natural language. No need to memorize syntax!

**Instead of:** `df.groupby('region')['sales'].sum()`  
**Just say:** `Show me total sales by region`

**Instead of:** `df[df['sales'] > df['sales'].quantile(0.9)]`  
**Just say:** `Show me top 10% of sales`

**Instead of:** Complex pandas pivot logic  
**Just say:** `Create a pivot table of products by month`

## 🚦 System Status Check

Run this quick check:

```python
# quick_test.py
import os
print("✅ GEMINI_API_KEY:", "Found" if os.getenv('GEMINI_API_KEY') else "❌ Missing")

try:
    import streamlit
    print("✅ Streamlit: Installed")
except:
    print("❌ Streamlit: Not installed")

try:
    import crewai
    print("✅ CrewAI: Installed")
except:
    print("❌ CrewAI: Not installed")

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("✅ Gemini: Ready")
except:
    print("❌ Gemini: Not ready")
```

## 📞 Getting Help

1. Check error messages (they're detailed!)
2. Run `python test_enterprise.py`
3. Review `.env` configuration
4. Check [ENTERPRISE_README.md](ENTERPRISE_README.md)

## 🎉 Success Checklist

- [ ] Python 3.10+ installed
- [ ] Dependencies installed
- [ ] `.env` file created with API key
- [ ] Test suite passes
- [ ] App launches successfully
- [ ] Sample data loads
- [ ] AI command executes

If all checked, you're ready to analyze! 🚀

---

**Time to First Insight: < 5 minutes**  
**Complexity: Beginner-friendly**  
**Power: Enterprise-grade**
