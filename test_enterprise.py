"""
Test Suite for Enterprise AI Data Analyst
Run this to verify everything is working correctly
"""
import pandas as pd
import os
from pathlib import Path
import sys

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def test_imports():
    """Test that all imports work."""
    print("🧪 Test 1: Checking imports...")
    try:
        from ai_data_analyst import (
            EnterpriseDataAnalystCrew,
            TypeInferencer,
            LLMIntentAnalyzer
        )
        from ai_data_analyst.tools.pandas_tools import PandasTools
        from ai_data_analyst.tools.advanced_operations import AdvancedOperations
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_gemini_config():
    """Test Gemini API configuration."""
    print("\n🧪 Test 2: Checking Gemini configuration...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        print("   Add it to your .env file")
        return False
    
    if len(api_key) < 20:
        print("❌ GEMINI_API_KEY seems invalid (too short)")
        return False
    
    print(f"✅ GEMINI_API_KEY found (length: {len(api_key)})")
    return True


def test_llm_initialization():
    """Test LLM initialization."""
    print("\n🧪 Test 3: Testing LLM initialization...")
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ Cannot test LLM without API key")
            return False
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.1,
            google_api_key=api_key
        )
        print("✅ LLM initialized successfully")
        return True
    except Exception as e:
        print(f"❌ LLM initialization failed: {e}")
        return False


def test_type_inference():
    """Test type inference."""
    print("\n🧪 Test 4: Testing type inference...")
    try:
        from ai_data_analyst.utils.type_inference import TypeInferencer
        
        # Create sample data
        df = pd.DataFrame({
            'product': ['A', 'B', 'C', 'D', 'E'],
            'sales': [100, 200, 150, 300, 250],
            'date': pd.date_range('2024-01-01', periods=5),
            'category': ['X', 'Y', 'X', 'Y', 'X']
        })
        
        schema = TypeInferencer.infer_schema(df)
        
        if len(schema.columns) == 4:
            print(f"✅ Type inference working ({len(schema.columns)} columns detected)")
            return True
        else:
            print(f"❌ Type inference error: expected 4 columns, got {len(schema.columns)}")
            return False
    except Exception as e:
        print(f"❌ Type inference failed: {e}")
        return False


def test_pandas_tools():
    """Test pandas tools."""
    print("\n🧪 Test 5: Testing pandas tools...")
    try:
        from ai_data_analyst.tools.pandas_tools import PandasTools
        
        df = pd.DataFrame({
            'value': [1, 2, None, 4, 5],
            'category': ['A', 'B', 'A', 'B', 'A']
        })
        
        # Test cleaning
        df_clean = PandasTools.clean_missing_values(df, 'fill_mean', ['value'])
        
        if df_clean['value'].isnull().sum() == 0:
            print("✅ Pandas tools working (missing values handled)")
            return True
        else:
            print("❌ Pandas tools failed to clean data")
            return False
    except Exception as e:
        print(f"❌ Pandas tools failed: {e}")
        return False


def test_advanced_operations():
    """Test advanced operations."""
    print("\n🧪 Test 6: Testing advanced operations...")
    try:
        from ai_data_analyst.tools.advanced_operations import AdvancedOperations
        
        df = pd.DataFrame({
            'product': ['A', 'B', 'A', 'B', 'A'] * 3,
            'sales': [100, 200, 150, 300, 250] * 3,
            'date': pd.date_range('2024-01-01', periods=15)
        })
        
        # Test time series
        ts_result = AdvancedOperations.time_series_analysis(df, 'date', 'sales', freq='D')
        
        if 'trend_slope' in ts_result:
            print("✅ Advanced operations working (time series analysis)")
            return True
        else:
            print("❌ Advanced operations returned unexpected result")
            return False
    except Exception as e:
        print(f"❌ Advanced operations failed: {e}")
        return False


def test_cleaning_agent():
    """Test cleaning agent."""
    print("\n🧪 Test 7: Testing cleaning agent...")
    try:
        from ai_data_analyst.agents.cleaning_agent import CleaningAgent
        from ai_data_analyst.utils.type_inference import TypeInferencer
        
        df = pd.DataFrame({
            'value': [1, 2, None, 4, 5, 5],  # Has null and duplicate
            'category': ['A', 'B', 'A', 'B', 'A', 'A']
        })
        
        schema = TypeInferencer.infer_schema(df)
        
        # Note: CleaningAgent needs LLM, so we test without it
        cleaner = CleaningAgent(llm=None)
        
        print("✅ Cleaning agent initialized (full test needs LLM)")
        return True
    except Exception as e:
        print(f"❌ Cleaning agent failed: {e}")
        return False


def test_intent_analyzer():
    """Test intent analyzer."""
    print("\n🧪 Test 8: Testing LLM intent analyzer...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️  Skipping (requires GEMINI_API_KEY)")
        return True
    
    try:
        from ai_data_analyst.utils.llm_intent_analyzer import LLMIntentAnalyzer
        
        analyzer = LLMIntentAnalyzer()
        
        schema = {
            'columns': [
                {'name': 'sales', 'data_type': 'numeric', 'unique_count': 100},
                {'name': 'product', 'data_type': 'categorical', 'unique_count': 10}
            ]
        }
        
        # Simple test - don't actually call LLM in test
        print("✅ Intent analyzer initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Intent analyzer failed: {e}")
        return False


def test_crew_creation():
    """Test crew creation."""
    print("\n🧪 Test 9: Testing crew creation...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️  Skipping (requires GEMINI_API_KEY)")
        return True
    
    try:
        from ai_data_analyst.crew_enterprise import EnterpriseDataAnalystCrew
        
        crew = EnterpriseDataAnalystCrew()
        
        print("✅ Enterprise crew created successfully")
        return True
    except Exception as e:
        print(f"❌ Crew creation failed: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("=" * 80)
    print("🚀 Enterprise AI Data Analyst - Test Suite")
    print("=" * 80)
    
    tests = [
        test_imports,
        test_gemini_config,
        test_llm_initialization,
        test_type_inference,
        test_pandas_tools,
        test_advanced_operations,
        test_cleaning_agent,
        test_intent_analyzer,
        test_crew_creation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 80)
    print("📊 Test Results")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
    elif passed >= total * 0.7:
        print("\n⚠️  Most tests passed. Some features may need configuration.")
    else:
        print("\n❌ Multiple tests failed. Check configuration and dependencies.")
    
    print("\n" + "=" * 80)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
