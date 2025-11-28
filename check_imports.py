"""Check which crew is being imported in the app."""
import sys
from pathlib import Path

# Add src to path like the app does
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

print("=" * 60)
print("Checking Crew Imports")
print("=" * 60)

print("\n1. Testing simple crew import...")
try:
    from ai_data_analyst.crew_simple import SimpleDataAnalystCrew
    print("✅ SimpleDataAnalystCrew imports successfully")
except Exception as e:
    print(f"❌ SimpleDataAnalystCrew import failed: {e}")

print("\n2. Testing enterprise crew import...")
try:
    from ai_data_analyst.crew_enterprise import EnterpriseDataAnalystCrew
    print("⚠️  EnterpriseDataAnalystCrew imports (this is the broken one!)")
except Exception as e:
    print(f"✅ EnterpriseDataAnalystCrew import blocked (good!)")
    print(f"   Error: {e}")

print("\n3. Checking what app_enterprise.py would import...")
try:
    # Simulate what the app does
    from ai_data_analyst.crew_simple import SimpleDataAnalystCrew as CrewClass
    print("✅ App will use: SimpleDataAnalystCrew")
    print(f"   Location: {CrewClass.__module__}")
except Exception as e:
    print(f"❌ App import simulation failed: {e}")

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)

print("\n✅ SimpleDataAnalystCrew should be used")
print("❌ EnterpriseDataAnalystCrew should NOT be used")
print("\nIf you're still seeing crew_enterprise.py errors,")
print("it means something is still importing it.")
