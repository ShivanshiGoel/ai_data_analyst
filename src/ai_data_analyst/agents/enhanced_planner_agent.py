"""Enhanced Planner Agent - Uses LLM for true intelligent planning."""
from crewai import Agent, Task
from typing import Dict, Any, List
from ai_data_analyst.models.schemas import ExecutionPlan, DatasetSchema
import json


class EnhancedPlannerAgent:
    """
    Planner Agent that uses LLM to understand complex natural language requests
    and create detailed execution plans without hardcoded patterns.
    """
    
    def __init__(self, llm):
        if not llm:
            raise ValueError("LLM is required for EnhancedPlannerAgent")
        
        self.agent = Agent(
            role='Strategic AI Data Analyst & Orchestrator',
            goal='''Understand ANY natural language data request and create optimal execution plans. 
            Analyze data schemas deeply to select appropriate columns, operations, and visualizations.
            Handle complex requests like "create cohort analysis", "forecast next quarter", "detect anomalies".''',
            backstory="""You are a world-class data scientist and business analyst with 20 years of experience.
            You have mastered Excel, Power BI, Tableau, Python, SQL, and advanced analytics.
            You can interpret vague business requests and translate them into precise data operations.
            You understand statistical methods, machine learning, time series analysis, and BI best practices.
            You NEVER assume column names - you always analyze the schema first and match semantically.
            You can handle requests ranging from simple filtering to complex predictive analytics.""",
            llm=llm,
            verbose=True,
            allow_delegation=True
        )
    
    def create_execution_plan(self, user_prompt: str, schema: DatasetSchema) -> ExecutionPlan:
        """
        Use LLM to interpret user request and create detailed execution plan.
        
        Args:
            user_prompt: Natural language request from user
            schema: Current dataset schema
        
        Returns:
            ExecutionPlan with agents, columns, and detailed steps
        """
        # Prepare schema information for LLM
        schema_info = self._format_schema_for_llm(schema)
        
        # Create planning task
        task_description = f"""
Analyze this data request and create a detailed execution plan:

USER REQUEST: "{user_prompt}"

AVAILABLE DATA SCHEMA:
{schema_info}

AVAILABLE AGENTS:
1. cleaning_agent - Data quality, missing values, duplicates, outliers, type fixing
2. transformation_agent - Pivot tables, grouping, aggregations, merging, reshaping
3. analytics_agent - Statistical analysis, KPIs, correlations, distributions
4. advanced_analytics_agent - Forecasting, clustering, anomaly detection, regression
5. visualization_agent - Charts, graphs, dashboards, interactive visualizations
6. formatting_agent - Conditional formatting, styling, highlighting
7. export_agent - Excel export with formulas, Power BI export, reports

YOUR TASK:
1. Understand what the user wants to achieve
2. Analyze which columns in the schema are relevant (NEVER assume column names)
3. Determine which agents are needed and in what order
4. Specify the exact operations to perform
5. Identify target columns by matching semantic meaning
6. Consider data quality issues that might affect the analysis
7. Think about appropriate visualizations for the result

Return your analysis as a detailed execution plan.
"""
        
        task = Task(
            description=task_description,
            agent=self.agent,
            expected_output="""A detailed JSON execution plan with:
            - user_intent: Clear description of what user wants
            - required_agents: List of agent names needed
            - execution_order: Ordered list of execution steps
            - target_columns: Specific column names from schema
            - operations: Detailed operations for each agent
            - rationale: Why this plan will achieve the goal
            - expected_output_type: table/chart/dashboard/report
            - confidence: 0-1 score of plan confidence"""
        )
        
        # Execute task and get LLM response
        result = self.agent.execute_task(task)
        
        # Parse LLM response into ExecutionPlan
        plan = self._parse_llm_response(result, user_prompt, schema)
        
        return plan
    
    def _format_schema_for_llm(self, schema: DatasetSchema) -> str:
        """Format schema information for LLM understanding."""
        schema_text = f"Dataset: {schema.row_count} rows, {schema.column_count} columns\n\n"
        schema_text += "COLUMNS:\n"
        
        for col in schema.columns:
            schema_text += f"- {col.name}\n"
            schema_text += f"  Type: {col.data_type}\n"
            schema_text += f"  Semantic: {col.semantic_type}\n"
            schema_text += f"  Unique values: {col.unique_count}\n"
            schema_text += f"  Null count: {col.null_count}\n"
            if col.sample_values:
                schema_text += f"  Sample: {', '.join(str(v) for v in col.sample_values[:3])}\n"
            schema_text += "\n"
        
        return schema_text
    
    def _parse_llm_response(self, llm_output: str, user_prompt: str, 
                           schema: DatasetSchema) -> ExecutionPlan:
        """Parse LLM output into structured ExecutionPlan."""
        try:
            # Try to extract JSON from LLM response
            if '```json' in llm_output:
                json_start = llm_output.find('```json') + 7
                json_end = llm_output.find('```', json_start)
                json_str = llm_output[json_start:json_end].strip()
            elif '{' in llm_output:
                json_start = llm_output.find('{')
                json_end = llm_output.rfind('}') + 1
                json_str = llm_output[json_start:json_end]
            else:
                json_str = llm_output
            
            plan_data = json.loads(json_str)
            
            return ExecutionPlan(
                user_intent=plan_data.get('user_intent', user_prompt),
                required_agents=plan_data.get('required_agents', []),
                execution_order=plan_data.get('execution_order', []),
                target_columns=plan_data.get('target_columns', []),
                rationale=plan_data.get('rationale', 'Generated by LLM'),
                estimated_steps=len(plan_data.get('execution_order', []))
            )
        
        except Exception as e:
            # Fallback: use simple heuristics if LLM parsing fails
            return self._fallback_plan(user_prompt, schema)
    
    def _fallback_plan(self, user_prompt: str, schema: DatasetSchema) -> ExecutionPlan:
        """Create basic plan if LLM parsing fails."""
        prompt_lower = user_prompt.lower()
        
        required_agents = []
        execution_order = []
        target_columns = []
        
        # Basic keyword matching as absolute fallback
        if any(word in prompt_lower for word in ['clean', 'fix', 'quality']):
            required_agents.append('cleaning')
            execution_order.append('cleaning_agent')
        
        if any(word in prompt_lower for word in ['analyze', 'kpi', 'metric', 'summary']):
            required_agents.append('analytics')
            execution_order.append('analytics_agent')
        
        if any(word in prompt_lower for word in ['chart', 'graph', 'plot', 'visual']):
            required_agents.append('visualization')
            execution_order.append('visualization_agent')
        
        if any(word in prompt_lower for word in ['forecast', 'predict', 'trend']):
            required_agents.append('advanced_analytics')
            execution_order.append('advanced_analytics_agent')
        
        # Default to analytics if nothing matched
        if not required_agents:
            required_agents = ['analytics']
            execution_order = ['analytics_agent']
        
        # Try to extract column names from prompt
        for col in schema.columns:
            if col.name.lower() in prompt_lower:
                target_columns.append(col.name)
        
        return ExecutionPlan(
            user_intent=user_prompt,
            required_agents=required_agents,
            execution_order=execution_order,
            target_columns=target_columns,
            rationale="Fallback plan - LLM parsing failed",
            estimated_steps=len(execution_order)
        )
    
    def validate_plan(self, plan: ExecutionPlan, schema: DatasetSchema) -> Dict[str, Any]:
        """
        Use LLM to validate if the plan makes sense given the data.
        
        Returns:
            Dict with validation results and suggestions
        """
        validation_task = f"""
Review this execution plan for data quality and feasibility:

PLAN:
- Intent: {plan.user_intent}
- Agents: {', '.join(plan.required_agents)}
- Target Columns: {', '.join(plan.target_columns)}

SCHEMA:
{self._format_schema_for_llm(schema)}

Check:
1. Do target columns exist in the schema?
2. Are the column types appropriate for the operations?
3. Is there enough data quality (check null counts)?
4. Are the agents in the right order?
5. Any missing steps or agents?

Return validation result and suggestions.
"""
        
        task = Task(
            description=validation_task,
            agent=self.agent,
            expected_output="Validation results with pass/fail and improvement suggestions"
        )
        
        result = self.agent.execute_task(task)
        
        return {
            'valid': 'valid' in result.lower() or 'pass' in result.lower(),
            'feedback': result,
            'suggestions': []
        }
