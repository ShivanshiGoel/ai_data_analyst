"""Cleaning Agent - Handles data quality operations."""
from crewai import Agent, Task
import pandas as pd
from typing import Dict, Any, List, Tuple
from ai_data_analyst.models.schemas import CleaningPlan, CleaningAction, DatasetSchema
from ai_data_analyst.utils.type_inference import TypeInferencer

# Import PandasTools
try:
    from ai_data_analyst.tools.pandas_tools import PandasTools
except ImportError:
    # Fallback if not available
    class PandasTools:
        @staticmethod
        def clean_missing_values(df, strategy, columns):
            return df
        @staticmethod
        def remove_duplicates(df, subset=None):
            return df.drop_duplicates(subset=subset)
        @staticmethod
        def fix_data_types(df, type_mappings):
            return df
        @staticmethod
        def remove_outliers(df, columns, method, threshold):
            return df


class CleaningAgent:
    """
    Cleaning Agent analyzes data quality issues and applies cleaning operations.
    """
    
    def __init__(self, llm):
        self.agent = Agent(
            role='Data Quality Specialist',
            goal='Identify and fix data quality issues to ensure clean, analysis-ready datasets',
            backstory="""You are a meticulous data engineer with expertise in data cleaning.
            You automatically detect missing values, duplicates, type inconsistencies, and outliers.
            You make smart decisions about cleaning strategies based on data characteristics.""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
        self.tools = PandasTools()
    
    def analyze_and_clean(self, df: pd.DataFrame, schema: DatasetSchema, 
                         user_intent: str = "") -> Tuple[pd.DataFrame, CleaningPlan]:
        """
        Analyze data quality and apply appropriate cleaning.
        
        Args:
            df: Input dataframe
            schema: Dataset schema
            user_intent: Optional user-specified cleaning intent
        
        Returns:
            Tuple of (cleaned_df, cleaning_plan)
        """
        actions = []
        df_clean = df.copy()
        
        # 1. Check for missing values
        null_counts = df_clean.isnull().sum()
        cols_with_nulls = null_counts[null_counts > 0].index.tolist()
        
        if cols_with_nulls:
            # Decide strategy based on column type
            for col in cols_with_nulls:
                col_schema = next((c for c in schema.columns if c.name == col), None)
                if not col_schema:
                    continue
                
                null_pct = (df_clean[col].isnull().sum() / len(df_clean)) * 100
                
                if null_pct > 50:
                    # High null percentage - consider dropping column
                    strategy = 'drop_column'
                    reason = f"{col} has {null_pct:.1f}% missing values"
                elif col_schema.data_type.value == 'numeric':
                    strategy = 'fill_median'
                    reason = f"Fill numeric column {col} missing values with median"
                elif col_schema.data_type.value == 'categorical':
                    strategy = 'fill_mode'
                    reason = f"Fill categorical column {col} with most frequent value"
                else:
                    strategy = 'drop_rows'
                    reason = f"Drop rows with missing {col}"
                
                actions.append(CleaningAction(
                    action_type='fill_nulls',
                    target_columns=[col],
                    parameters={'strategy': strategy},
                    reason=reason
                ))
                
                # Apply cleaning
                if strategy == 'drop_column':
                    df_clean = df_clean.drop(columns=[col])
                elif strategy == 'drop_rows':
                    df_clean = self.tools.clean_missing_values(df_clean, 'drop', [col])
                elif strategy == 'fill_median':
                    df_clean = self.tools.clean_missing_values(df_clean, 'fill_median', [col])
                elif strategy == 'fill_mode':
                    df_clean = self.tools.clean_missing_values(df_clean, 'fill_mode', [col])
        
        # 2. Check for duplicates
        duplicate_count = df_clean.duplicated().sum()
        if duplicate_count > 0:
            actions.append(CleaningAction(
                action_type='remove_duplicates',
                target_columns=[],
                parameters={},
                reason=f"Found {duplicate_count} duplicate rows"
            ))
            df_clean = self.tools.remove_duplicates(df_clean)
        
        # 3. Fix data types if needed
        type_fixes = {}
        for col_schema in schema.columns:
            col = col_schema.name
            if col not in df_clean.columns:
                continue
            
            # Try to infer and fix numeric columns stored as strings
            if col_schema.data_type.value == 'text' and df_clean[col].dtype == 'object':
                # Check if it's actually numeric
                try:
                    pd.to_numeric(df_clean[col].dropna(), errors='raise')
                    type_fixes[col] = 'float'
                except:
                    pass
        
        if type_fixes:
            actions.append(CleaningAction(
                action_type='fix_types',
                target_columns=list(type_fixes.keys()),
                parameters={'type_mappings': type_fixes},
                reason="Fix incorrectly typed columns"
            ))
            df_clean = self.tools.fix_data_types(df_clean, type_fixes)
        
        # 4. Check for outliers in numeric columns (if requested)
        if 'outlier' in user_intent.lower():
            numeric_cols = TypeInferencer.get_numeric_columns(schema)
            if numeric_cols:
                actions.append(CleaningAction(
                    action_type='outlier_removal',
                    target_columns=numeric_cols,
                    parameters={'method': 'iqr', 'threshold': 1.5},
                    reason="Remove statistical outliers using IQR method"
                ))
                df_clean = self.tools.remove_outliers(df_clean, numeric_cols, 'iqr', 1.5)
        
        # Create cleaning plan summary
        impact_summary = f"Cleaned {len(df) - len(df_clean)} rows, "
        impact_summary += f"processed {len(cols_with_nulls)} columns with missing data"
        
        cleaning_plan = CleaningPlan(
            actions=actions,
            estimated_impact=impact_summary
        )
        
        return df_clean, cleaning_plan
    
    def apply_specific_cleaning(self, df: pd.DataFrame, 
                               action: CleaningAction) -> pd.DataFrame:
        """
        Apply a specific cleaning action.
        
        Args:
            df: Input dataframe
            action: Cleaning action to apply
        
        Returns:
            Cleaned dataframe
        """
        df_result = df.copy()
        
        if action.action_type == 'drop_nulls':
            df_result = self.tools.clean_missing_values(
                df_result, 'drop', action.target_columns
            )
        
        elif action.action_type == 'fill_nulls':
            strategy = action.parameters.get('strategy', 'fill_mean')
            df_result = self.tools.clean_missing_values(
                df_result, strategy, action.target_columns
            )
        
        elif action.action_type == 'remove_duplicates':
            df_result = self.tools.remove_duplicates(
                df_result, action.target_columns if action.target_columns else None
            )
        
        elif action.action_type == 'fix_types':
            type_mappings = action.parameters.get('type_mappings', {})
            df_result = self.tools.fix_data_types(df_result, type_mappings)
        
        elif action.action_type == 'outlier_removal':
            method = action.parameters.get('method', 'iqr')
            threshold = action.parameters.get('threshold', 1.5)
            df_result = self.tools.remove_outliers(
                df_result, action.target_columns, method, threshold
            )
        
        return df_result
    
    def create_task(self, description: str, expected_output: str) -> Task:
        """Create a CrewAI task for this agent."""
        return Task(
            description=description,
            agent=self.agent,
            expected_output=expected_output
        )