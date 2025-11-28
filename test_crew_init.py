"""Test CrewAI initialization step by step."""
import sys
from pathlib import Path
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 60)
print("Testing CrewAI Initialization")
print("=" * 60)

# Step 1: Load environment
print("\n1️⃣ Loading environment variables...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"✅ GEMINI_API_KEY loaded ({len(api_key)} chars)")
    else:
        print("❌ GEMINI_API_KEY not found")
        print("\n💡 Fix: Create .env file with:")
        print("   GEMINI_API_KEY=your_key_here")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error loading environment: {e}")
    sys.exit(1)

# Step 2: Test Gemini LLM
print("\n2️⃣ Testing Gemini LLM initialization...")
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.1,
        google_api_key=api_key
    )
    print("✅ Gemini LLM initialized")
except Exception as e:
    print(f"❌ Gemini LLM failed: {e}")
    print("\n💡 Fix: Install langchain-google-genai")
    print("   pip install langchain-google-genai google-generativeai")
    sys.exit(1)

# Step 3: Test crew tools
print("\n3️⃣ Testing crew tools...")
try:
    from ai_data_analyst.crew_tools import get_crew_tools
    tools = get_crew_tools()
    print(f"✅ Loaded {len(tools)} crew tools")
    for i, tool in enumerate(tools, 1):
        print(f"   {i}. {tool.name}")
except Exception as e:
    print(f"❌ Crew tools failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Test CrewAI import
print("\n4️⃣ Testing CrewAI import...")
try:
    from crewai import Agent, Crew, Process, Task
    from crewai.project import CrewBase, agent, crew, task
    print("✅ CrewAI imported successfully")
except Exception as e:
    print(f"❌ CrewAI import failed: {e}")
    print("\n💡 Fix: Install crewai")
    print("   pip install crewai>=0.28.0")
    sys.exit(1)

# Step 5: Test EnterpriseDataAnalystCrew initialization
print("\n5️⃣ Testing EnterpriseDataAnalystCrew initialization...")
try:
    from ai_data_analyst.crew_enterprise import EnterpriseDataAnalystCrew
    print("   - Import successful")
    
    print("   - Creating instance...")
    crew_instance = EnterpriseDataAnalystCrew()
    print("✅ EnterpriseDataAnalystCrew initialized!")
    
    # Check agents
    if hasattr(crew_instance, 'agents'):
        print(f"   - Agents: {len(crew_instance.agents)}")
    
    # Check tasks
    if hasattr(crew_instance, 'tasks'):
        print(f"   - Tasks: {len(crew_instance.tasks)}")
    
except Exception as e:
    print(f"❌ EnterpriseDataAnalystCrew failed: {e}")
    print("\n📋 Full error:")
    import traceback
    traceback.print_exc()
    
    print("\n💡 Possible fixes:")
    print("   1. Check .env file has valid GEMINI_API_KEY")
    print("   2. Install all dependencies: pip install -r requirements.txt")
    print("   3. Check that agents.yaml and tasks.yaml exist")
    print("   4. Verify crew_tools.py is working")
    sys.exit(1)

# Success!
print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\n🎉 CrewAI is working correctly!")
print("   You can now run: python -m streamlit run app_enterprise.py")
print()
