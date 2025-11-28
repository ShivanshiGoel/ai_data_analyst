"""Planner Agent - Orchestrates workflow based on user intent using LLM."""
from crewai import Agent, Task
from typing import Dict, Any
from ai_data_analyst.models.schemas import ExecutionPlan, DatasetSchema
from ai_data_analyst.utils.llm_intent_analyzer import LLMIntentAnalyzer


class PlannerAgent:
    """
    Planner Agent uses LLM to interpret user prompts and create execution plans.
    NO hardcoded keywords - pure AI understanding.
    """
    
    def __init__(self, llm):
        self.agent = Agent(
            role='Strategic Data Analyst Planner',
            goal='Understand user intent and create optimal execution plans for data analysis tasks',
            backstory="""You are a senior data analyst with 15 years of experience. 
            You excel at understanding what users want from their data and breaking down 
            complex requests into actionable steps. You use AI to understand intent rather 
            than relying on keyword matching.""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
        self.llm = llm
        self.intent_analyzer = LLMIntentAnalyzer() if llm else None
    
    def create_execution_plan(self, user_prompt: str, schema: DatasetSchema) -> ExecutionPlan:
        """
        Analyze user prompt and schema to create execution plan using LLM.
        
        Args:
            user_prompt: Natural language request from user
            schema: Current dataset schema
        
        Returns:
            ExecutionPlan with agents and execution order
        """
        if self.intent_analyzer:
            # Use LLM-based intent analysis
            schema_dict = self._schema_to_dict(schema)
            intent_result = self.intent_analyzer.analyze_user_intent(user_prompt, schema_dict)
            
            # Extract execution plan components
            required_agents = []
            execution_order = []
            
            # Map operations to agents
            operation_map = {
                'cleaning': 'cleaning_agent',
                'data_cleaning': 'cleaning_agent',
                'analytics': 'analytics_agent',
                'analysis': 'analytics_agent',
                'aggregation': 'analytics_agent',
                'visualization': 'visualization_agent',
                'chart': 'visualization_agent',
                'formatting': 'formatting_agent',
                'dashboard': 'dashboard_agent'
            }
            
            for op in intent_result.get('required_operations', []):
                agent_name = operation_map.get(op.lower())
                if agent_name and agent_name not in execution_order:
                    execution_order.append(agent_name)
                    required_agents.append(op)
            
            # Get target columns from LLM
            target_columns = intent_result.get('target_columns', [])
            if not target_columns:
                target_columns = self.intent_analyzer.extract_column_references(user_prompt, schema_dict)
            
            # Determine output type
            intent_type = intent_result.get('intent_type', 'data_analysis')
            output_type = self._determine_output_type(intent_type)
            
            confidence = intent_result.get('confidence', 0.7)
            
        else:
            # Fallback to basic analysis if no LLM
            return self._fallback_plan(user_prompt, schema)
        
        # If no agents identified, default to analytics
        if not execution_order:
            execution_order = ['analytics_agent']
            required_agents = ['analytics']
        
        return ExecutionPlan(
            user_intent=user_prompt,
            required_agents=required_agents,
            execution_order=execution_order,
            target_columns=target_columns,
            expected_output_type=output_type,
            confidence=confidence
        )
    
    def _schema_to_dict(self, schema: DatasetSchema) -> Dict:
        """Convert DatasetSchema to dictionary for LLM."""
        return {
            'columns': [
                {
                    'name': col.name,
                    'data_type': col.data_type.value if hasattr(col.data_type, 'value') else str(col.data_type),
                    'unique_count': col.unique_count,
                    'semantic_type': col.semantic_type if hasattr(col, 'semantic_type') else None
                }
                for col in schema.columns
            ]
        }
    
    def _determine_output_type(self, intent_type: str) -> str:
        """Determine output type based on intent."""
        if intent_type == 'visualization':
            return 'chart'
        elif intent_type == 'dashboard':
            return 'dashboard'
        else:
            return 'table'
    
    def _fallback_plan(self, prompt: str, schema: DatasetSchema) -> ExecutionPlan:
        """Fallback plan when LLM is not available."""
        return ExecutionPlan(
            user_intent=prompt,
            required_agents=['analytics'],
            execution_order=['analytics_agent'],
            target_columns=[],
            expected_output_type='table',
            confidence=0.5
        )
    
    def create_task(self, description: str, expected_output: str) -> Task:
        """Create a CrewAI task for this agent."""
        return Task(
            description=description,
            agent=self.agent,
            expected_output=expected_output
        )