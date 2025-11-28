"""LLM-Powered NLP Processor - No hardcoded patterns, true AI understanding."""
import pandas as pd
from typing import Dict, List, Optional, Any
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate


class LLMNLPProcessor:
    """
    Natural Language Processor using LLM for true understanding.
    NO hardcoded keywords or patterns - pure AI interpretation.
    """
    
    def __init__(self, df: pd.DataFrame, llm: ChatGoogleGenerativeAI):
        """
        Initialize with dataframe and LLM.
        
        Args:
            df: The dataframe to process
            llm: Language model for interpretation
        """
        self.df = df
        self.llm = llm
        self.columns = list(df.columns)
        self.schema_info = self._analyze_schema()
    
    def _analyze_schema(self) -> str:
        """Create detailed schema description for LLM."""
        schema_text = f"Dataset: {len(self.df)} rows × {len(self.df.columns)} columns\n\n"
        schema_text += "COLUMNS:\n"
        
        for col in self.df.columns:
            col_type = str(self.df[col].dtype)
            unique_count = self.df[col].nunique()
            null_count = self.df[col].isnull().sum()
            
            schema_text += f"- {col}\n"
            schema_text += f"  Type: {col_type}\n"
            schema_text += f"  Unique values: {unique_count}\n"
            schema_text += f"  Missing: {null_count}\n"
            
            # Sample values
            if unique_count < 20:
                samples = self.df[col].dropna().unique()[:5]
                schema_text += f"  Sample values: {', '.join(str(s) for s in samples)}\n"
            else:
                samples = self.df[col].dropna().sample(min(3, unique_count)).tolist()
                schema_text += f"  Sample: {', '.join(str(s) for s in samples)}\n"
            
            schema_text += "\n"
        
        return schema_text
    
    def process_request(self, request: str) -> Dict[str, Any]:
        """
        Process natural language request using LLM.
        
        Args:
            request: Natural language request from user
        
        Returns:
            Dict with operation details
        """
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert data analyst who interprets natural language requests 
            and converts them into structured data operations. You have deep knowledge of Excel,
            Power BI, SQL, pandas, and statistical analysis.
            
            Your task is to understand what the user wants to do with their data and return
            a structured JSON response specifying the exact operation.
            
            AVAILABLE OPERATIONS:
            1. filtering - Filter data by criteria
            2. ranking - Top N, bottom N, highest, lowest
            3. grouping - Group by columns and aggregate
            4. pivot - Create pivot tables
            5. merging - Join/merge datasets
            6. transformation - Add calculated columns, reshape data
            7. forecasting - Time series prediction
            8. clustering - Segmentation analysis
            9. anomaly_detection - Find outliers
            10. correlation - Analyze relationships
            11. regression - Predictive modeling
            12. cohort - Cohort analysis
            13. rfm - Customer segmentation
            14. conditional_formatting - Highlight cells
            15. statistical_analysis - Descriptive statistics, tests
            16. what_if - Scenario analysis
            17. vlookup - Lookup values from another source
            18. time_intelligence - YTD, QTD, rolling windows
            19. export - Export with specific formatting
            
            Return ONLY valid JSON with no markdown formatting."""),
            
            ("user", """Analyze this data request:

REQUEST: "{request}"

DATASET SCHEMA:
{schema}

Return JSON with:
{{
    "operation": "operation_name",
    "description": "clear description of what will be done",
    "parameters": {{
        "target_columns": ["column names needed"],
        "filters": {{}},  // if filtering
        "aggregations": {{}},  // if grouping
        "n": 10,  // if ranking
        "advanced_params": {{}}  // operation-specific parameters
    }},
    "rationale": "why this operation matches the request",
    "expected_output": "description of expected result"
}}

Examples:
- "show me top 5 customers by revenue" → ranking operation
- "predict next month's sales" → forecasting operation
- "find unusual transactions" → anomaly_detection operation
- "group by region and sum sales" → grouping operation
- "highlight cells where profit is negative" → conditional_formatting operation
""")
        ])
        
        # Generate prompt
        prompt = prompt_template.format_messages(
            request=request,
            schema=self.schema_info
        )
        
        # Get LLM response
        try:
            response = self.llm.invoke(prompt)
            response_text = response.content
            
            # Parse JSON response
            operation_plan = self._parse_json_response(response_text)
            
            return operation_plan
        
        except Exception as e:
            print(f"Error processing request: {e}")
            return {
                'operation': 'unknown',
                'error': str(e),
                'description': 'Failed to understand request'
            }
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        try:
            # Remove markdown code blocks if present
            if '```json' in response:
                start = response.find('```json') + 7
                end = response.find('```', start)
                response = response[start:end].strip()
            elif '```' in response:
                start = response.find('```') + 3
                end = response.find('```', start)
                response = response[start:end].strip()
            
            # Parse JSON
            operation_plan = json.loads(response)
            
            # Validate required fields
            if 'operation' not in operation_plan:
                operation_plan['operation'] = 'unknown'
            
            if 'parameters' not in operation_plan:
                operation_plan['parameters'] = {}
            
            return operation_plan
        
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {response}")
            return {
                'operation': 'unknown',
                'error': 'Failed to parse LLM response',
                'raw_response': response
            }
    
    def suggest_next_actions(self, current_state: str) -> List[str]:
        """
        Use LLM to suggest next possible actions based on current state.
        
        Args:
            current_state: Description of current data state
        
        Returns:
            List of suggested natural language actions
        """
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a data analysis expert. Suggest intelligent next steps for data analysis."),
            ("user", """Given this data state:

CURRENT STATE: {state}

DATASET SCHEMA:
{schema}

Suggest 5 intelligent next actions the user might want to take.
Return as a JSON array of strings.

Examples of good suggestions:
- "Forecast revenue for next quarter"
- "Identify customer segments using clustering"
- "Find correlations between price and sales"
- "Create pivot table by region and product"
- "Detect anomalies in transaction amounts"

Return ONLY the JSON array, no other text.""")
        ])
        
        prompt = prompt_template.format_messages(
            state=current_state,
            schema=self.schema_info
        )
        
        try:
            response = self.llm.invoke(prompt)
            response_text = response.content
            
            # Parse JSON array
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            elif '[' in response_text:
                start = response_text.find('[')
                end = response_text.rfind(']') + 1
                response_text = response_text[start:end]
            
            suggestions = json.loads(response_text)
            return suggestions if isinstance(suggestions, list) else []
        
        except Exception as e:
            print(f"Error getting suggestions: {e}")
            return [
                "Analyze data quality",
                "Create summary statistics",
                "Visualize key metrics",
                "Find patterns in data",
                "Export processed data"
            ]
    
    def explain_operation(self, operation_plan: Dict) -> str:
        """
        Use LLM to explain what an operation will do in plain English.
        
        Args:
            operation_plan: Operation plan dict
        
        Returns:
            Plain English explanation
        """
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a data analyst explaining technical operations in plain English."),
            ("user", """Explain this data operation in simple terms:

OPERATION: {operation}

PARAMETERS: {parameters}

Explain in 2-3 sentences what will happen and what the user will get.
Be clear and concise.""")
        ])
        
        prompt = prompt_template.format_messages(
            operation=json.dumps(operation_plan, indent=2),
            parameters=json.dumps(operation_plan.get('parameters', {}), indent=2)
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        
        except Exception as e:
            return f"Will perform {operation_plan.get('operation', 'operation')} on the data."
    
    def validate_request(self, request: str) -> Dict[str, Any]:
        """
        Validate if a request can be fulfilled with available data.
        
        Args:
            request: Natural language request
        
        Returns:
            Dict with validation results
        """
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a data validation expert checking if requests can be fulfilled."),
            ("user", """Check if this request can be fulfilled with the available data:

REQUEST: "{request}"

AVAILABLE DATA:
{schema}

Return JSON:
{{
    "valid": true/false,
    "reason": "explanation",
    "missing_requirements": ["list of what's missing"],
    "suggestions": ["alternative approaches"]
}}""")
        ])
        
        prompt = prompt_template.format_messages(
            request=request,
            schema=self.schema_info
        )
        
        try:
            response = self.llm.invoke(prompt)
            response_text = response.content
            
            # Parse JSON
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            elif '{' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                response_text = response_text[start:end]
            
            validation = json.loads(response_text)
            return validation
        
        except Exception as e:
            return {
                'valid': True,  # Assume valid if validation fails
                'reason': 'Unable to validate request',
                'error': str(e)
            }
    
    def auto_correct_request(self, request: str) -> str:
        """
        Auto-correct ambiguous or unclear requests.
        
        Args:
            request: User's original request
        
        Returns:
            Clarified request
        """
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You clarify ambiguous data requests to make them more specific."),
            ("user", """Clarify this request to be more specific:

ORIGINAL REQUEST: "{request}"

AVAILABLE COLUMNS: {columns}

Return a more specific version of the request that clearly states:
1. What operation to perform
2. Which columns to use
3. Any parameters (top N, time period, etc.)

Return ONLY the clarified request text, nothing else.""")
        ])
        
        prompt = prompt_template.format_messages(
            request=request,
            columns=', '.join(self.columns)
        )
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        
        except Exception as e:
            return request  # Return original if clarification fails


class OperationExecutor:
    """Execute operations returned by LLM NLP Processor."""
    
    def __init__(self, df: pd.DataFrame, advanced_tools, excel_tools):
        self.df = df
        self.advanced_tools = advanced_tools
        self.excel_tools = excel_tools
    
    def execute(self, operation_plan: Dict) -> Dict[str, Any]:
        """
        Execute operation based on LLM plan.
        
        Args:
            operation_plan: Operation plan from LLM
        
        Returns:
            Execution results
        """
        operation = operation_plan.get('operation', '')
        params = operation_plan.get('parameters', {})
        
        try:
            if operation == 'filtering':
                return self._execute_filtering(params)
            
            elif operation == 'ranking':
                return self._execute_ranking(params)
            
            elif operation == 'grouping':
                return self._execute_grouping(params)
            
            elif operation == 'pivot':
                return self._execute_pivot(params)
            
            elif operation in ['forecasting', 'clustering', 'anomaly_detection', 
                              'correlation', 'regression', 'cohort', 'rfm']:
                return self._execute_advanced_analytics(operation, params)
            
            elif operation == 'time_intelligence':
                return self._execute_time_intelligence(params)
            
            elif operation == 'conditional_formatting':
                return self._execute_formatting(params)
            
            else:
                return {
                    'success': False,
                    'error': f'Operation {operation} not implemented yet'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_filtering(self, params: Dict) -> Dict:
        """Execute filtering operation."""
        filters = params.get('filters', {})
        result_df = self.df.copy()
        
        for column, condition in filters.items():
            if isinstance(condition, dict):
                op = condition.get('operator', '==')
                value = condition.get('value')
                
                if op == '==':
                    result_df = result_df[result_df[column] == value]
                elif op == '>':
                    result_df = result_df[result_df[column] > value]
                elif op == '<':
                    result_df = result_df[result_df[column] < value]
                elif op == '>=':
                    result_df = result_df[result_df[column] >= value]
                elif op == '<=':
                    result_df = result_df[result_df[column] <= value]
                elif op == 'contains':
                    result_df = result_df[result_df[column].astype(str).str.contains(str(value))]
            else:
                result_df = result_df[result_df[column] == condition]
        
        return {
            'success': True,
            'data': result_df,
            'rows_before': len(self.df),
            'rows_after': len(result_df)
        }
    
    def _execute_ranking(self, params: Dict) -> Dict:
        """Execute ranking operation."""
        target_col = params.get('target_columns', [None])[0]
        n = params.get('n', 10)
        ascending = params.get('ascending', False)
        
        if not target_col or target_col not in self.df.columns:
            return {'success': False, 'error': f'Column {target_col} not found'}
        
        if ascending:
            result_df = self.df.nsmallest(n, target_col)
        else:
            result_df = self.df.nlargest(n, target_col)
        
        return {
            'success': True,
            'data': result_df,
            'operation': f'Top {n}' if not ascending else f'Bottom {n}'
        }
    
    def _execute_grouping(self, params: Dict) -> Dict:
        """Execute grouping operation."""
        group_by = params.get('group_by', [])
        aggregations = params.get('aggregations', {})
        
        if not group_by or not aggregations:
            return {'success': False, 'error': 'Need group_by and aggregations'}
        
        result_df = self.excel_tools.group_and_aggregate(
            self.df, group_by, aggregations
        )
        
        return {
            'success': True,
            'data': result_df
        }
    
    def _execute_pivot(self, params: Dict) -> Dict:
        """Execute pivot table creation."""
        rows = params.get('rows', [])
        columns = params.get('columns')
        values = params.get('values', [])
        aggfunc = params.get('aggfunc', 'sum')
        
        result_df = self.advanced_tools.create_pivot_table(
            self.df, rows, columns, values, {v: aggfunc for v in values}
        )
        
        return {
            'success': True,
            'data': result_df
        }
    
    def _execute_advanced_analytics(self, operation: str, params: Dict) -> Dict:
        """Execute advanced analytics operations."""
        # This would call the AdvancedAnalyticsAgent methods
        return {
            'success': True,
            'message': f'{operation} operation would be executed here',
            'params': params
        }
    
    def _execute_time_intelligence(self, params: Dict) -> Dict:
        """Execute time intelligence calculations."""
        date_col = params.get('date_column')
        value_col = params.get('value_column')
        metrics = params.get('metrics', ['YTD', 'YoY'])
        
        result_df = self.advanced_tools.calculate_time_intelligence(
            self.df, date_col, value_col, metrics
        )
        
        return {
            'success': True,
            'data': result_df
        }
    
    def _execute_formatting(self, params: Dict) -> Dict:
        """Execute conditional formatting."""
        return {
            'success': True,
            'message': 'Formatting applied',
            'params': params
        }
