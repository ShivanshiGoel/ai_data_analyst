"""
CrewAI Integration for Streamlit - Full Agent-Based Workflow
This module provides CrewAI-powered operations for the Streamlit app.
"""
from typing import Dict, Any
import pandas as pd
from .crew_simple import SimpleDataAnalystCrew  # Use simple crew instead!
from .models.state import app_state


class CrewAIStreamlitIntegration:
    """
    Integration layer between Streamlit and CrewAI.
    All operations go through CrewAI agents - no direct function calls.
    """
    
    def __init__(self):
        """Initialize the crew integration."""
        self.crew = None
    
    def _get_crew(self):
        """Lazy load the crew."""
        if self.crew is None:
            self.crew = SimpleDataAnalystCrew()  # Use simple crew!
        return self.crew
    
    def execute_command(self, command: str, df: pd.DataFrame, schema) -> Dict[str, Any]:
        """
        Execute user command through CrewAI agents.
        
        This is the ONLY entry point for all operations.
        Everything goes through the multi-agent crew.
        
        Args:
            command: Natural language user command
            df: Current dataframe
            schema: Dataset schema
        
        Returns:
            Dict with results from crew execution
        """
        crew = self._get_crew()
        
        # Execute through CrewAI - agents collaborate
        result = crew.analyze_data_request(
            user_request=command,
            df=df,
            schema=schema
        )
        
        return result
    
    def quick_clean(self, df: pd.DataFrame, schema) -> Dict[str, Any]:
        """
        Quick clean operation through CrewAI.
        Delegates to cleaning agent via crew.
        """
        return self.execute_command(
            "Clean this dataset by handling missing values, removing duplicates, and fixing data types",
            df,
            schema
        )
    
    def quick_analyze(self, df: pd.DataFrame, schema) -> Dict[str, Any]:
        """
        Quick analysis operation through CrewAI.
        Delegates to analytics agent via crew.
        """
        return self.execute_command(
            "Analyze this dataset and provide key statistics, insights, and KPIs",
            df,
            schema
        )
    
    def create_dashboard(self, df: pd.DataFrame, schema) -> Dict[str, Any]:
        """
        Create dashboard through CrewAI.
        Delegates to dashboard agent via crew.
        """
        return self.execute_command(
            "Create a comprehensive executive dashboard with KPIs and visualizations",
            df,
            schema
        )
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get status of all agents in the crew.
        
        Returns:
            Dict with agent information
        """
        if self.crew is None:
            return {
                'initialized': False,
                'agents': []
            }
        
        crew = self._get_crew()
        return {
            'initialized': True,
            'agent_count': len(crew.agents) if hasattr(crew, 'agents') else 0,
            'agents': [
                {
                    'role': agent.role if hasattr(agent, 'role') else 'Unknown',
                    'goal': agent.goal if hasattr(agent, 'goal') else 'Unknown'
                }
                for agent in (crew.agents if hasattr(crew, 'agents') else [])
            ]
        }


# Global instance for Streamlit
crew_integration = CrewAIStreamlitIntegration()
