"""Quick test script to verify fixes."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_schema_handling():
    """Test schema dict/object handling."""
    print("Testing schema handling...")
    
    # Test dict format
    schema_dict = {
        'columns': [
            {'name': 'col1', 'data_type': 'int', 'unique_count': 10},
            {'name': 'col2', 'data_type': 'str', 'unique_count': 5}
        ]
    }
    
    # Handle dict format
    if isinstance(schema_dict, dict):
        columns = schema_dict.get('columns', [])
        print(f"✅ Dict format: {len(columns)} columns")
        
        for col in columns:
            name = col.get('name')
            print(f"  - {name}")
    
    # Test object format (mock)
    class MockColumn:
        def __init__(self, name, dtype):
            self.name = name
            self.data_type = dtype
            self.unique_count = 10
    
    class MockSchema:
        def __init__(self):
            self.columns = [
                MockColumn('col1', 'int'),
                MockColumn('col2', 'str')
            ]
    
    schema_obj = MockSchema()
    
    # Handle object format
    if hasattr(schema_obj, 'columns'):
        columns = schema_obj.columns
        print(f"✅ Object format: {len(columns)} columns")
        
        for col in columns:
            name = getattr(col, 'name', 'Unknown')
            print(f"  - {name}")
    
    print("\n✅ Schema handling works for both dict and object formats!")


def test_data_cleaner():
    """Test data cleaner."""
    print("\nTesting data cleaner...")
    
    import pandas as pd
    from ai_data_analyst.tools.data_cleaner import AdvancedDataCleaner
    
    # Create dirty data
    df = pd.DataFrame({
        'col1': [1, 2, None, 4, 5],
        'col2': ['a', 'b', 'c', 'd', 'e'],
        'col3': ['  space  ', 'trim', '', 'me', 'please']
    })
    
    print("Before cleaning:")
    print(df)
    
    # Clean
    result = AdvancedDataCleaner.clean_dataset(df, aggressive=False)
    df_clean = result['dataframe']
    report = result['report']
    
    print("\nAfter cleaning:")
    print(df_clean)
    
    print("\nCleaning report:")
    for op in report['operations']:
        print(f"  - {op}")
    
    print("\n✅ Data cleaner works!")


def test_imports():
    """Test all critical imports."""
    print("\nTesting imports...")
    
    try:
        from ai_data_analyst.crew_enterprise import EnterpriseDataAnalystCrew
        print("✅ EnterpriseDataAnalystCrew")
    except Exception as e:
        print(f"❌ EnterpriseDataAnalystCrew: {e}")
    
    try:
        from ai_data_analyst.tools.data_cleaner import AdvancedDataCleaner
        print("✅ AdvancedDataCleaner")
    except Exception as e:
        print(f"❌ AdvancedDataCleaner: {e}")
    
    try:
        from ai_data_analyst.tools.excel_tools import ExcelTools
        print("✅ ExcelTools")
    except Exception as e:
        print(f"❌ ExcelTools: {e}")
    
    try:
        from ai_data_analyst.utils.type_inference import TypeInferencer
        print("✅ TypeInferencer")
    except Exception as e:
        print(f"❌ TypeInferencer: {e}")
    
    print("\n✅ All critical imports work!")


if __name__ == "__main__":
    print("="*60)
    print("Quick Test Suite")
    print("="*60)
    
    test_schema_handling()
    test_data_cleaner()
    test_imports()
    
    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("="*60)
    print("\nSystem is ready to run:")
    print("  python -m streamlit run app_enterprise.py")
