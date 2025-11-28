#!/usr/bin/env python
"""Enterprise Main Entry Point - Production-ready AI Data Analyst."""
import sys
import os
import pandas as pd
from pathlib import Path
from datetime import datetime
import warnings

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_data_analyst.crew_enterprise import EnterpriseDataAnalystCrew
from ai_data_analyst.utils.type_inference import TypeInferencer

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run_analysis(excel_file: str, user_request: str):
    """
    Run enterprise data analysis.
    
    Args:
        excel_file: Path to Excel file
        user_request: Natural language analysis request
    """
    print(f"\n{'='*80}")
    print(f"🚀 Enterprise AI Data Analyst")
    print(f"{'='*80}\n")
    
    # Load data
    print(f"📁 Loading data from: {excel_file}")
    df = pd.read_excel(excel_file)
    print(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns\n")
    
    # Infer schema
    print("🔍 Analyzing schema...")
    schema = TypeInferencer.infer_schema(df)
    print(f"✅ Schema analyzed: {len(schema.columns)} columns typed\n")
    
    # Initialize crew
    print("🤖 Initializing AI agents...")
    crew = EnterpriseDataAnalystCrew()
    print("✅ Agents ready\n")
    
    # Execute analysis
    print(f"💡 User Request: {user_request}\n")
    print("⚙️ Executing analysis workflow...\n")
    
    result = crew.analyze_data_request(user_request, df, schema)
    
    print(f"\n{'='*80}")
    print("✅ Analysis Complete!")
    print(f"{'='*80}\n")
    
    return result


def run_demo():
    """Run demo with sample data."""
    print("\n🎯 Running Enterprise Demo\n")
    
    # Check for demo data
    demo_files = [
        "sample_data.xlsx",
        "data.xlsx",
        "test.xlsx"
    ]
    
    excel_file = None
    for file in demo_files:
        if Path(file).exists():
            excel_file = file
            break
    
    if not excel_file:
        print("❌ No demo data file found. Please provide an Excel file.")
        print("Expected files: sample_data.xlsx, data.xlsx, or test.xlsx")
        return
    
    # Demo requests
    demo_requests = [
        "Clean the data and show me key statistics",
        "Create a dashboard with sales performance metrics",
        "Analyze trends over time and visualize them",
    ]
    
    user_request = demo_requests[0]
    result = run_analysis(excel_file, user_request)
    
    print("\n📊 Results:")
    print(result)


def run():
    """Main entry point for CLI."""
    if len(sys.argv) > 2:
        excel_file = sys.argv[1]
        user_request = sys.argv[2]
        run_analysis(excel_file, user_request)
    else:
        run_demo()


def train():
    """Train the crew."""
    print("🎓 Training mode - Enterprise AI Data Analyst")
    
    if len(sys.argv) < 3:
        print("Usage: train <n_iterations> <filename>")
        return
    
    n_iterations = int(sys.argv[1])
    filename = sys.argv[2]
    
    crew = EnterpriseDataAnalystCrew()
    
    inputs = {
        'user_request': 'Analyze sales data and create insights',
        'schema': 'Sample schema',
        'target_columns': []
    }
    
    try:
        crew.crew().train(n_iterations=n_iterations, filename=filename, inputs=inputs)
        print(f"✅ Training complete. Results saved to {filename}")
    except Exception as e:
        print(f"❌ Training failed: {e}")


def test():
    """Test the crew."""
    print("🧪 Test mode - Enterprise AI Data Analyst")
    
    if len(sys.argv) < 3:
        print("Usage: test <n_iterations> <eval_llm>")
        return
    
    n_iterations = int(sys.argv[1])
    eval_llm = sys.argv[2]
    
    crew = EnterpriseDataAnalystCrew()
    
    inputs = {
        'user_request': 'Test analysis request',
        'schema': 'Test schema',
        'target_columns': []
    }
    
    try:
        crew.crew().test(n_iterations=n_iterations, eval_llm=eval_llm, inputs=inputs)
        print("✅ Testing complete")
    except Exception as e:
        print(f"❌ Testing failed: {e}")


if __name__ == "__main__":
    run()
