"""CrewAI orchestration and management."""
from crewai import Crew, Task, Process
from typing import Dict, List, Optional
import os


class CrewManager:
    """Manages CrewAI agent orchestration."""

    def __init__(self, api_key: str = None):
        """
        Initialize CrewManager with agents.

        Args:
            api_key: Gemini API key (optional - can use environment variable)
        """
        # Set API key if provided
        if api_key:
            os.environ['GEMINI_API_KEY'] = api_key

        # Initialize Gemini LLM
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-pro",
                temperature=0.1,
                google_api_key=api_key or os.getenv('GEMINI_API_KEY')
            ) if (api_key or os.getenv('GEMINI_API_KEY')) else None
        except Exception as e:
            self.llm = None
            print(f"⚠️ LLM not configured - agents will run in simplified mode: {e}")

        # Import and initialize agents
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all agent instances."""
        # Import agent classes
        from ai_data_analyst.agents.planner_agent import PlannerAgent
        from ai_data_analyst.agents.cleaning_agent import CleaningAgent
        from ai_data_analyst.agents.analytics_agent import AnalyticsAgent
        from ai_data_analyst.agents.visualization_agent import VisualizationAgent
        from ai_data_analyst.agents.formatting_agent import FormattingAgent
        from ai_data_analyst.agents.dashboard_agent import DashboardAgent

        # Create agent instances
        self.planner = PlannerAgent(self.llm)
        self.cleaning = CleaningAgent(self.llm)
        self.analytics = AnalyticsAgent(self.llm)
        self.visualization = VisualizationAgent(self.llm)
        self.formatting = FormattingAgent(self.llm)
        self.dashboard = DashboardAgent(self.llm)

        print("✅ All agents initialized successfully")

    def execute_plan(self, user_prompt: str, df, schema, app_state) -> Dict:
        """
        Execute a complete workflow based on user prompt.

        Args:
            user_prompt: Natural language user request
            df: Current dataframe
            schema: Column schema
            app_state: Application state instance

        Returns:
            Execution result dictionary
        """
        try:
            # Step 1: Create execution plan
            plan = self.planner.create_execution_plan(user_prompt, schema)

            # Log A2A communication
            app_state.log_agent_message(
                'System', 'PlannerAgent',
                'Created execution plan',
                {'prompt': user_prompt, 'agents': plan['execution_order']}
            )

            # Step 2: Execute agents in order
            results = {}
            for agent_name in plan['execution_order']:
                agent_result = self._execute_agent(
                    agent_name, plan, df, schema, app_state
                )
                results[agent_name] = agent_result

            return {
                'success': True,
                'plan': plan,
                'results': results
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _execute_agent(self, agent_name: str, plan: Dict, df, schema, app_state) -> Dict:
        """
        Execute specific agent based on plan.

        Args:
            agent_name: Name of agent to execute
            plan: Execution plan
            df: Dataframe
            schema: Column schema
            app_state: Application state

        Returns:
            Agent execution result
        """
        try:
            if agent_name == 'cleaning_agent':
                result = self.cleaning.analyze_and_clean(df, schema)
                app_state.log_agent_message(
                    'CleaningAgent', 'System',
                    'Completed data cleaning',
                    {'actions': len(result.get('cleaning_plan', {}).get('actions', []))}
                )
                return result

            elif agent_name == 'analytics_agent':
                result = self.analytics.generate_analytics(
                    df, schema, plan.get('target_columns', [])
                )
                if result.get('kpis'):
                    app_state.set_kpis(result['kpis'])
                app_state.log_agent_message(
                    'AnalyticsAgent', 'System',
                    'Generated analytics',
                    {'kpi_count': len(result.get('kpis', []))}
                )
                return result

            elif agent_name == 'visualization_agent':
                charts = self.visualization.suggest_visualizations(
                    df, schema, plan.get('user_intent', '')
                )
                for chart in charts:
                    app_state.add_chart(chart)
                app_state.log_agent_message(
                    'VisualizationAgent', 'System',
                    'Created visualizations',
                    {'chart_count': len(charts)}
                )
                return {'charts': charts}

            elif agent_name == 'formatting_agent':
                result = self.formatting.create_formatting_plan(
                    plan.get('user_intent', ''),
                    schema,
                    plan.get('target_columns', [])
                )
                app_state.log_agent_message(
                    'FormattingAgent', 'System',
                    'Applied formatting',
                    {'rules': len(result.get('rules', []))}
                )
                return result

            elif agent_name == 'dashboard_agent':
                dashboard = self.dashboard.compose_dashboard(
                    app_state.kpis,
                    app_state.charts,
                    plan.get('user_intent', 'Dashboard')
                )
                app_state.log_agent_message(
                    'DashboardAgent', 'System',
                    'Composed dashboard',
                    {'sections': len(dashboard.get('sections', []))}
                )
                return dashboard

            else:
                return {'success': False, 'error': f'Unknown agent: {agent_name}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}
