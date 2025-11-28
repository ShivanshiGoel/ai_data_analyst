"""Enterprise Crew - Production-ready AI Data Analyst System."""
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import List, Dict, Any, Optional
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from .crew_tools import get_crew_tools


@CrewBase
class EnterpriseDataAnalystCrew:
    """Enterprise-grade AI Data Analyst Crew with Gemini."""
    
    # Use absolute path to config files
    agents_config = 'config/agents_enterprise.yaml'
    tasks_config = 'config/tasks_enterprise.yaml'
    
    def __init__(self):
        """Initialize with Gemini LLM and crew tools."""
        try:
            print("🔧 Initializing Gemini LLM...")
            self.llm = self._initialize_llm()
            print("✅ LLM initialized")
        except Exception as e:
            print(f"❌ Failed to initialize LLM: {e}")
            raise
        
        try:
            print("🔧 Loading crew tools...")
            self.crew_tools = get_crew_tools()  # Tools available to all agents
            print(f"✅ Loaded {len(self.crew_tools)} tools")
        except Exception as e:
            print(f"❌ Failed to load tools: {e}")
            raise
    
    def _initialize_llm(self) -> ChatGoogleGenerativeAI:
        """Initialize Gemini LLM from environment."""
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please add it to your .env file.")
        
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.1,
            google_api_key=api_key
        )
    
    @agent
    def data_planner(self) -> Agent:
        """Strategic planner agent with tools."""
        return Agent(
            role='Strategic Data Analyst Planner',
            goal='Analyze user requests and create optimal execution plans',
            backstory="""You are a senior data strategist with deep expertise in understanding 
            business requirements and translating them into actionable data analysis plans. 
            You excel at identifying the right analytical approach for any data question.""",
            llm=self.llm,
            tools=self.crew_tools,  # Give planner access to all tools
            verbose=True,
            allow_delegation=True
        )
    
    @agent
    def data_cleaner(self) -> Agent:
        """Data cleaning specialist with cleaning tools."""
        return Agent(
            role='Data Quality Engineer',
            goal='Ensure data is clean, consistent, and analysis-ready',
            backstory="""You are a meticulous data quality expert who identifies and fixes 
            data issues including missing values, duplicates, outliers, and type inconsistencies. 
            You apply industry best practices for data cleaning.""",
            llm=self.llm,
            tools=[self.crew_tools[0]],  # Data Cleaning Tool
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def data_analyst(self) -> Agent:
        """Advanced analytics specialist with analysis tools."""
        return Agent(
            role='Senior Data Analyst',
            goal='Generate deep insights through statistical analysis and KPI calculation',
            backstory="""You are an expert analyst who uncovers meaningful patterns in data. 
            You calculate relevant KPIs, perform aggregations, and provide statistical insights 
            that drive business decisions.""",
            llm=self.llm,
            tools=[self.crew_tools[1]],  # Data Analysis Tool
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def visualization_expert(self) -> Agent:
        """Data visualization specialist with visualization tools."""
        return Agent(
            role='Data Visualization Expert',
            goal='Create compelling, insightful visualizations that tell data stories',
            backstory="""You are a visualization expert who knows which chart types best 
            communicate different types of insights. You follow data visualization best 
            practices and create charts that are both beautiful and informative.""",
            llm=self.llm,
            tools=[self.crew_tools[2]],  # Visualization Tool
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def dashboard_architect(self) -> Agent:
        """Dashboard design specialist."""
        return Agent(
            role='BI Dashboard Architect',
            goal='Design comprehensive executive dashboards',
            backstory="""You are a BI expert with extensive Power BI and Tableau experience. 
            You design dashboards that tell complete data stories with optimal information 
            hierarchy and visual flow.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    @task
    def plan_analysis(self) -> Task:
        """Planning task."""
        return Task(
            description="""Analyze the user's request: {user_request}
            
            Available data schema: {schema}
            
            Create a comprehensive execution plan that includes:
            1. Understanding of user intent
            2. Required analytical operations
            3. Target columns and metrics
            4. Expected output format
            
            Be thorough and strategic in your planning.""",
            agent=self.data_planner(),
            expected_output="""A detailed execution plan with:
            - Clear interpretation of user intent
            - List of required operations
            - Identified target columns
            - Expected output type and format"""
        )
    
    @task
    def clean_data(self) -> Task:
        """Data cleaning task."""
        return Task(
            description="""Clean and prepare the dataset for analysis.
            
            Analyze data quality issues and apply appropriate fixes:
            - Handle missing values intelligently
            - Remove duplicates
            - Fix data type inconsistencies
            - Handle outliers if needed
            
            Dataset info: {schema}""",
            agent=self.data_cleaner(),
            expected_output="""Cleaned dataset with:
            - Summary of cleaning operations performed
            - Number of records affected
            - Data quality improvements made"""
        )
    
    @task
    def analyze_data(self) -> Task:
        """Analytics task."""
        return Task(
            description="""Perform comprehensive data analysis based on the plan.
            
            User request: {user_request}
            Target columns: {target_columns}
            
            Calculate relevant KPIs, perform aggregations, and generate insights.""",
            agent=self.data_analyst(),
            expected_output="""Analysis results including:
            - Key performance indicators
            - Statistical summaries
            - Aggregations and groupings
            - Notable patterns or insights"""
        )
    
    @task
    def create_visualizations(self) -> Task:
        """Visualization task."""
        return Task(
            description="""Create appropriate visualizations for the analysis.
            
            User request: {user_request}
            Analysis results: Use output from previous task
            
            Select and specify optimal chart types.""",
            agent=self.visualization_expert(),
            expected_output="""Visualization specifications including:
            - Chart types selected
            - Data mappings (x, y, color, size)
            - Chart titles and labels
            - Design rationale"""
        )
    
    @task
    def build_dashboard(self) -> Task:
        """Dashboard creation task."""
        return Task(
            description="""Compose a comprehensive dashboard.
            
            User request: {user_request}
            Available KPIs: Use from analysis task
            Available charts: Use from visualization task
            
            Design an executive-ready dashboard layout.""",
            agent=self.dashboard_architect(),
            expected_output="""Dashboard specification with:
            - Layout structure
            - KPI placement
            - Chart arrangement
            - Visual hierarchy""",
            output_file='dashboard_spec.json'
        )
    
    @crew
    def crew(self) -> Crew:
        """Assemble the enterprise crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            embedder={
                "provider": "google",
                "config": {
                    "model": "models/embedding-001",
                    "api_key": os.getenv('GEMINI_API_KEY')
                }
            }
        )
    
    def analyze_data_request(self, user_request: str, df, schema) -> Dict[str, Any]:
        """
        Execute full analysis workflow using CrewAI agents.
        
        Args:
            user_request: Natural language user request
            df: Pandas DataFrame
            schema: Dataset schema
        
        Returns:
            Analysis results with agent outputs
        """
        # Prepare inputs for the crew
        inputs = {
            'user_request': user_request,
            'schema': self._format_schema_for_crew(schema),
            'data_preview': df.head(10).to_string() if df is not None else "No data",
            'target_columns': self._suggest_columns(user_request, schema)
        }
        
        # Execute the crew - agents will collaborate
        print(f"\n🚀 CrewAI: Starting multi-agent workflow for: '{user_request}'")
        print(f"👥 Active Agents: {len(self.agents)}")
        print(f"📋 Tasks to Execute: {len(self.tasks)}")
        
        result = self.crew().kickoff(inputs=inputs)
        
        print(f"✅ CrewAI: Workflow completed successfully")
        
        return {
            'success': True,
            'result': result,
            'agents_used': [agent.role for agent in self.agents],
            'user_request': user_request
        }
    
    def _format_schema_for_crew(self, schema) -> str:
        """Format schema for crew agents."""
        if isinstance(schema, dict):
            columns = schema.get('columns', [])
            formatted = "Dataset Schema:\n"
            for col in columns:
                if isinstance(col, dict):
                    name = col.get('name', 'Unknown')
                    dtype = col.get('data_type', 'unknown')
                    unique = col.get('unique_count', 0)
                else:
                    name = getattr(col, 'name', 'Unknown')
                    dtype = getattr(col, 'data_type', 'unknown')
                    if hasattr(dtype, 'value'):
                        dtype = dtype.value
                    unique = getattr(col, 'unique_count', 0)
                formatted += f"  - {name}: {dtype} ({unique} unique)\n"
            return formatted
        
        # Handle object with columns attribute
        if hasattr(schema, 'columns'):
            formatted = "Dataset Schema:\n"
            for col in schema.columns:
                name = getattr(col, 'name', 'Unknown')
                dtype = getattr(col, 'data_type', 'unknown')
                if hasattr(dtype, 'value'):
                    dtype = dtype.value
                unique = getattr(col, 'unique_count', 0)
                formatted += f"  - {name}: {dtype} ({unique} unique)\n"
            return formatted
        
        return str(schema)
    
    def _suggest_columns(self, request: str, schema) -> List[str]:
        """Suggest relevant columns based on request."""
        # Simple keyword-based suggestion (agents will refine this)
        columns = []
        
        if isinstance(schema, dict):
            for col in schema.get('columns', [])[:5]:
                if isinstance(col, dict):
                    columns.append(col.get('name', ''))
                else:
                    columns.append(getattr(col, 'name', ''))
        elif hasattr(schema, 'columns'):
            for col in list(schema.columns)[:5]:
                columns.append(getattr(col, 'name', ''))
        
        return [c for c in columns if c]  # Remove empty strings
