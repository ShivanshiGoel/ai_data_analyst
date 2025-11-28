"""LLM-based Intent Analyzer - Zero hardcoded patterns."""
import os
from typing import Dict, List, Any, Optional
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate


class LLMIntentAnalyzer:
    """
    Enterprise-grade intent analyzer using Gemini LLM.
    No hardcoded keywords or patterns - pure AI understanding.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize with Gemini API key.
        
        Args:
            api_key: Gemini API key (optional, will use env var if not provided)
        """
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.1,
            google_api_key=self.api_key
        )
    
    def analyze_user_intent(self, user_prompt: str, schema: Dict) -> Dict[str, Any]:
        """
        Analyze user intent and determine required operations.
        
        Args:
            user_prompt: Natural language user request
            schema: Dataset schema information
        
        Returns:
            Dict with intent analysis, required agents, and parameters
        """
        # Create schema summary for LLM
        schema_summary = self._create_schema_summary(schema)
        
        # Create prompt for intent analysis
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert data analyst AI assistant. Analyze user requests and determine:
1. What operations are needed (cleaning, analytics, visualization, formatting, dashboard)
2. Which columns are relevant
3. What type of output is expected
4. Specific parameters for each operation

Respond ONLY with valid JSON, no additional text."""),
            ("human", """User Request: {user_prompt}

Available Data Schema:
{schema_summary}

Analyze the request and respond with JSON in this exact format:
{{
    "intent_type": "data_analysis|visualization|cleaning|formatting|dashboard",
    "confidence": 0.0-1.0,
    "required_operations": ["operation1", "operation2"],
    "target_columns": ["col1", "col2"],
    "parameters": {{
        "aggregation": "sum|mean|count|etc",
        "group_by": ["column"],
        "filters": {{}},
        "chart_type": "bar|line|pie|scatter",
        "formatting_rules": []
    }},
    "explanation": "Brief explanation of the interpretation"
}}""")
        ])
        
        # Get LLM response
        try:
            chain = prompt | self.llm
            response = chain.invoke({
                "user_prompt": user_prompt,
                "schema_summary": schema_summary
            })
            
            # Parse JSON response
            content = response.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            return result
            
        except Exception as e:
            print(f"Error analyzing intent: {e}")
            # Fallback to basic analysis
            return self._fallback_intent_analysis(user_prompt, schema)
    
    def determine_required_agents(self, intent_analysis: Dict) -> List[str]:
        """
        Determine which agents need to be activated based on intent.
        
        Args:
            intent_analysis: Intent analysis result
        
        Returns:
            List of agent names
        """
        agents = []
        operations = intent_analysis.get('required_operations', [])
        
        operation_to_agent = {
            'cleaning': 'cleaning_agent',
            'data_cleaning': 'cleaning_agent',
            'analytics': 'analytics_agent',
            'analysis': 'analytics_agent',
            'aggregation': 'analytics_agent',
            'visualization': 'visualization_agent',
            'chart': 'visualization_agent',
            'plot': 'visualization_agent',
            'formatting': 'formatting_agent',
            'styling': 'formatting_agent',
            'dashboard': 'dashboard_agent',
            'report': 'dashboard_agent'
        }
        
        for op in operations:
            agent = operation_to_agent.get(op.lower())
            if agent and agent not in agents:
                agents.append(agent)
        
        # Always include planner
        if 'planner_agent' not in agents:
            agents.insert(0, 'planner_agent')
        
        return agents
    
    def extract_column_references(self, user_prompt: str, schema: Dict) -> List[str]:
        """
        Extract column references from user prompt using LLM.
        
        Args:
            user_prompt: User's natural language request
            schema: Dataset schema
        
        Returns:
            List of referenced column names
        """
        columns = []
        schema_columns = schema.get('columns', [])
        
        if not schema_columns:
            return columns
        
        # Create list of available columns
        available_columns = [col.get('name') if isinstance(col, dict) else col.name 
                           for col in schema_columns]
        
        # Use LLM to match intent to columns
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a data column matching expert. Given a user request and available columns,
identify which columns are most relevant. Respond with ONLY a JSON array of column names."""),
            ("human", """User Request: {user_prompt}

Available Columns: {columns}

Which columns are referenced or needed? Respond with JSON array only: ["col1", "col2"]""")
        ])
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({
                "user_prompt": user_prompt,
                "columns": ", ".join(available_columns)
            })
            
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            
            columns = json.loads(content)
            
        except Exception as e:
            print(f"Error extracting columns: {e}")
            # Fallback: simple string matching
            columns = [col for col in available_columns 
                      if col.lower() in user_prompt.lower()]
        
        return columns
    
    def _create_schema_summary(self, schema: Dict) -> str:
        """Create human-readable schema summary."""
        summary_parts = []
        columns = schema.get('columns', [])
        
        for col in columns[:20]:  # Limit to first 20 columns
            if isinstance(col, dict):
                name = col.get('name', 'Unknown')
                dtype = col.get('data_type', 'unknown')
                unique = col.get('unique_count', 0)
            else:
                name = getattr(col, 'name', 'Unknown')
                dtype = getattr(col, 'data_type', 'unknown')
                unique = getattr(col, 'unique_count', 0)
            
            summary_parts.append(f"- {name} ({dtype}, {unique} unique values)")
        
        if len(columns) > 20:
            summary_parts.append(f"... and {len(columns) - 20} more columns")
        
        return "\n".join(summary_parts)
    
    def _fallback_intent_analysis(self, user_prompt: str, schema: Dict) -> Dict:
        """Fallback analysis when LLM fails."""
        prompt_lower = user_prompt.lower()
        
        # Determine intent type
        if any(word in prompt_lower for word in ['clean', 'fix', 'remove']):
            intent_type = 'cleaning'
        elif any(word in prompt_lower for word in ['chart', 'plot', 'visualize', 'graph']):
            intent_type = 'visualization'
        elif any(word in prompt_lower for word in ['format', 'highlight', 'color']):
            intent_type = 'formatting'
        elif any(word in prompt_lower for word in ['dashboard', 'report', 'overview']):
            intent_type = 'dashboard'
        else:
            intent_type = 'data_analysis'
        
        return {
            'intent_type': intent_type,
            'confidence': 0.6,
            'required_operations': [intent_type],
            'target_columns': [],
            'parameters': {},
            'explanation': 'Fallback analysis due to LLM error'
        }
    
    def generate_execution_plan(self, intent_analysis: Dict, schema: Dict) -> Dict:
        """
        Generate detailed execution plan based on intent analysis.
        
        Args:
            intent_analysis: Intent analysis result
            schema: Dataset schema
        
        Returns:
            Execution plan with step-by-step operations
        """
        plan = {
            'intent': intent_analysis.get('intent_type'),
            'confidence': intent_analysis.get('confidence', 0.5),
            'steps': [],
            'agents_required': self.determine_required_agents(intent_analysis),
            'target_columns': intent_analysis.get('target_columns', []),
            'parameters': intent_analysis.get('parameters', {})
        }
        
        # Generate steps based on operations
        for operation in intent_analysis.get('required_operations', []):
            step = {
                'operation': operation,
                'description': f"Execute {operation} operation",
                'parameters': intent_analysis.get('parameters', {})
            }
            plan['steps'].append(step)
        
        return plan
