"""Simple Crew - Without @CrewBase decorator to avoid config issues."""
from crewai import Agent, Crew, Process, Task
from typing import List, Dict, Any
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv


class SimpleDataAnalystCrew:
    """Simple working crew without config file dependencies."""
    
    def __init__(self):
        """Initialize with Gemini LLM."""
        try:
            load_dotenv()
            
            print("🔧 Initializing Gemini LLM...")
            api_key = os.getenv('GEMINI_API_KEY')
            
            if not api_key:
                print("❌ GEMINI_API_KEY not found in environment")
                raise ValueError("GEMINI_API_KEY not found in environment variables. Please add it to your .env file.")
            
            print(f"   API key found ({len(api_key)} chars)")
            
            # Fix for Streamlit asyncio event loop issue
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # Create new event loop if none exists
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-pro",
                temperature=0.1,
                google_api_key=api_key
            )
            print("✅ LLM initialized")
            
        except Exception as e:
            print(f"❌ LLM initialization failed: {e}")
            raise
        
        # Initialize agents
        try:
            self._create_agents()
        except Exception as e:
            print(f"❌ Agent creation failed: {e}")
            raise
        
        # Initialize tasks
        try:
            self._create_tasks()
        except Exception as e:
            print(f"❌ Task creation failed: {e}")
            raise
    
    def _create_agents(self):
        """Create all agents."""
        print("🔧 Creating agents...")
        
        self.planner = Agent(
            role='Strategic Data Analyst Planner',
            goal='Analyze user requests and create optimal execution plans',
            backstory="""You are a senior data strategist with deep expertise in understanding 
            business requirements and translating them into actionable data analysis plans.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=True
        )
        
        self.cleaner = Agent(
            role='Data Quality Engineer',
            goal='Ensure data is clean, consistent, and analysis-ready',
            backstory="""You are a meticulous data quality expert who identifies and fixes 
            data issues including missing values, duplicates, outliers, and type inconsistencies.""",
            llm=self.llm,
            verbose=True
        )
        
        self.analyst = Agent(
            role='Senior Data Analyst',
            goal='Generate deep insights through statistical analysis and KPI calculation',
            backstory="""You are an expert analyst who uncovers meaningful patterns in data. 
            You calculate relevant KPIs, perform aggregations, and provide statistical insights.""",
            llm=self.llm,
            verbose=True
        )
        
        print("✅ Created 3 agents")
    
    def _create_tasks(self):
        """Create tasks for agents."""
        self.tasks = []
        
        # Planning task
        plan_task = Task(
            description="""Analyze the user's data analysis request and create a plan.
            
            User Request: {user_request}
            Dataset Schema: {schema}
            
            Create a plan that identifies:
            1. What the user wants to achieve
            2. Which analytical operations are needed
            3. Which columns should be analyzed
            4. What output format is expected""",
            agent=self.planner,
            expected_output="An execution plan with clear steps and target columns"
        )
        
        # Analysis task
        analysis_task = Task(
            description="""Analyze the dataset based on the user's request.
            
            User Request: {user_request}
            Data Preview: {data_preview}
            
            Perform the requested analysis and provide insights.""",
            agent=self.analyst,
            expected_output="Analysis results with insights and findings"
        )
        
        self.tasks = [plan_task, analysis_task]
    
    def analyze_data_request(self, user_request: str, df, schema) -> Dict[str, Any]:
        """
        Execute analysis workflow.
        
        Args:
            user_request: Natural language user request
            df: Pandas DataFrame
            schema: Dataset schema
        
        Returns:
            Analysis results
        """
        print(f"\n🚀 Starting analysis for: '{user_request}'")
        
        # Format schema
        if isinstance(schema, dict):
            columns = schema.get('columns', [])
            schema_str = "Dataset Columns:\n"
            for col in columns[:10]:  # First 10 columns
                if isinstance(col, dict):
                    name = col.get('name', 'Unknown')
                    dtype = col.get('data_type', 'unknown')
                else:
                    name = getattr(col, 'name', 'Unknown')
                    dtype = getattr(col, 'data_type', 'unknown')
                schema_str += f"  - {name} ({dtype})\n"
        else:
            schema_str = str(schema)[:500]  # Limit size
        
        # Prepare inputs
        inputs = {
            'user_request': user_request,
            'schema': schema_str,
            'data_preview': df.head(5).to_string() if df is not None else "No data"
        }
        
        # Create crew
        crew = Crew(
            agents=[self.planner, self.analyst],
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
        
        print("👥 Executing with 2 agents...")
        
        # Execute
        try:
            result = crew.kickoff(inputs=inputs)
            print("✅ Analysis completed!")
            
            return {
                'success': True,
                'result': result,
                'agents_used': ['Planner', 'Analyst'],
                'user_request': user_request
            }
        except Exception as e:
            print(f"❌ Crew execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'user_request': user_request
            }
