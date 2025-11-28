"""Pandas Tools - Core data manipulation operations."""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union


class PandasTools:
    """Enterprise-grade pandas operations for data manipulation."""
    
    @staticmethod
    def clean_missing_values(df: pd.DataFrame, strategy: str, 
                            columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Clean missing values using specified strategy.
        
        Args:
            df: Input dataframe
            strategy: 'drop', 'fill_mean', 'fill_median', 'fill_mode', 'fill_zero', 'fill_forward', 'fill_backward'
            columns: Columns to apply cleaning (None = all columns)
        
        Returns:
            Cleaned dataframe
        """
        df_result = df.copy()
        target_cols = columns if columns else df_result.columns.tolist()
        
        for col in target_cols:
            if col not in df_result.columns:
                continue
                
            if strategy == 'drop':
                df_result = df_result.dropna(subset=[col])
            elif strategy == 'fill_mean':
                if pd.api.types.is_numeric_dtype(df_result[col]):
                    df_result[col] = df_result[col].fillna(df_result[col].mean())
            elif strategy == 'fill_median':
                if pd.api.types.is_numeric_dtype(df_result[col]):
                    df_result[col] = df_result[col].fillna(df_result[col].median())
            elif strategy == 'fill_mode':
                mode_val = df_result[col].mode()
                if len(mode_val) > 0:
                    df_result[col] = df_result[col].fillna(mode_val[0])
            elif strategy == 'fill_zero':
                df_result[col] = df_result[col].fillna(0)
            elif strategy == 'fill_forward':
                df_result[col] = df_result[col].fillna(method='ffill')
            elif strategy == 'fill_backward':
                df_result[col] = df_result[col].fillna(method='bfill')
        
        return df_result
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame, 
                         subset: Optional[List[str]] = None,
                         keep: str = 'first') -> pd.DataFrame:
        """
        Remove duplicate rows.
        
        Args:
            df: Input dataframe
            subset: Columns to consider for duplicates (None = all columns)
            keep: 'first', 'last', or False (remove all duplicates)
        
        Returns:
            Deduplicated dataframe
        """
        return df.drop_duplicates(subset=subset, keep=keep)
    
    @staticmethod
    def fix_data_types(df: pd.DataFrame, 
                       type_mappings: Dict[str, str]) -> pd.DataFrame:
        """
        Fix data types for specified columns.
        
        Args:
            df: Input dataframe
            type_mappings: Dict of column -> type ('int', 'float', 'str', 'datetime')
        
        Returns:
            Dataframe with corrected types
        """
        df_result = df.copy()
        
        for col, dtype in type_mappings.items():
            if col not in df_result.columns:
                continue
            
            try:
                if dtype in ['int', 'integer']:
                    df_result[col] = pd.to_numeric(df_result[col], errors='coerce').astype('Int64')
                elif dtype in ['float', 'numeric']:
                    df_result[col] = pd.to_numeric(df_result[col], errors='coerce')
                elif dtype in ['str', 'string', 'text']:
                    df_result[col] = df_result[col].astype(str)
                elif dtype in ['datetime', 'date']:
                    df_result[col] = pd.to_datetime(df_result[col], errors='coerce')
                elif dtype == 'bool':
                    df_result[col] = df_result[col].astype(bool)
            except Exception as e:
                print(f"Warning: Could not convert {col} to {dtype}: {e}")
        
        return df_result
    
    @staticmethod
    def remove_outliers(df: pd.DataFrame, columns: List[str], 
                       method: str = 'iqr', threshold: float = 1.5) -> pd.DataFrame:
        """
        Remove outliers from numeric columns.
        
        Args:
            df: Input dataframe
            columns: Numeric columns to check for outliers
            method: 'iqr' (Interquartile Range) or 'zscore'
            threshold: Threshold for outlier detection (1.5 for IQR, 3.0 for z-score)
        
        Returns:
            Dataframe with outliers removed
        """
        df_result = df.copy()
        
        for col in columns:
            if col not in df_result.columns:
                continue
            
            if not pd.api.types.is_numeric_dtype(df_result[col]):
                continue
            
            if method == 'iqr':
                Q1 = df_result[col].quantile(0.25)
                Q3 = df_result[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                df_result = df_result[
                    (df_result[col] >= lower_bound) & (df_result[col] <= upper_bound)
                ]
            elif method == 'zscore':
                z_scores = np.abs((df_result[col] - df_result[col].mean()) / df_result[col].std())
                df_result = df_result[z_scores < threshold]
        
        return df_result
    
    @staticmethod
    def calculate_kpis(df: pd.DataFrame, schema: Any) -> List[Dict]:
        """
        Calculate key performance indicators from dataframe.
        
        Args:
            df: Input dataframe
            schema: Dataset schema
        
        Returns:
            List of KPI dictionaries
        """
        kpis = []
        
        # Basic KPIs
        kpis.append({
            'name': 'Total Records',
            'value': len(df),
            'category': 'Volume'
        })
        
        # Numeric column KPIs
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols[:3]:  # Limit to first 3
            kpis.append({
                'name': f'Total {col}',
                'value': df[col].sum(),
                'category': 'Aggregate'
            })
            kpis.append({
                'name': f'Avg {col}',
                'value': df[col].mean(),
                'category': 'Aggregate'
            })
        
        return kpis
    
    @staticmethod
    def aggregate_data(df: pd.DataFrame, group_by: List[str], 
                      agg_functions: Dict[str, Union[str, List[str]]]) -> pd.DataFrame:
        """
        Group and aggregate data.
        
        Args:
            df: Input dataframe
            group_by: Columns to group by
            agg_functions: Dict of column -> aggregation function(s)
        
        Returns:
            Aggregated dataframe
        """
        return df.groupby(group_by).agg(agg_functions).reset_index()
    
    @staticmethod
    def pivot_data(df: pd.DataFrame, index: List[str], 
                   columns: str, values: str, 
                   aggfunc: str = 'sum') -> pd.DataFrame:
        """
        Create pivot table.
        
        Args:
            df: Input dataframe
            index: Columns to use as index
            columns: Column to pivot
            values: Column to aggregate
            aggfunc: Aggregation function
        
        Returns:
            Pivoted dataframe
        """
        return df.pivot_table(
            index=index, 
            columns=columns, 
            values=values, 
            aggfunc=aggfunc
        ).reset_index()
    
    @staticmethod
    def filter_data(df: pd.DataFrame, conditions: Dict[str, Any]) -> pd.DataFrame:
        """
        Filter dataframe based on conditions.
        
        Args:
            df: Input dataframe
            conditions: Dict of column -> value or (operator, value)
        
        Returns:
            Filtered dataframe
        """
        df_result = df.copy()
        
        for col, condition in conditions.items():
            if col not in df_result.columns:
                continue
            
            if isinstance(condition, tuple):
                operator, value = condition
                if operator == '==':
                    df_result = df_result[df_result[col] == value]
                elif operator == '!=':
                    df_result = df_result[df_result[col] != value]
                elif operator == '>':
                    df_result = df_result[df_result[col] > value]
                elif operator == '<':
                    df_result = df_result[df_result[col] < value]
                elif operator == '>=':
                    df_result = df_result[df_result[col] >= value]
                elif operator == '<=':
                    df_result = df_result[df_result[col] <= value]
                elif operator == 'contains':
                    df_result = df_result[df_result[col].astype(str).str.contains(value, na=False)]
            else:
                # Direct equality
                df_result = df_result[df_result[col] == condition]
        
        return df_result
    
    @staticmethod
    def sort_data(df: pd.DataFrame, by: List[str], 
                  ascending: Union[bool, List[bool]] = True) -> pd.DataFrame:
        """
        Sort dataframe by columns.
        
        Args:
            df: Input dataframe
            by: Columns to sort by
            ascending: Sort order
        
        Returns:
            Sorted dataframe
        """
        return df.sort_values(by=by, ascending=ascending)
    
    @staticmethod
    def add_calculated_column(df: pd.DataFrame, column_name: str, 
                             expression: str) -> pd.DataFrame:
        """
        Add calculated column using pandas eval.
        
        Args:
            df: Input dataframe
            column_name: Name for new column
            expression: Pandas expression to evaluate
        
        Returns:
            Dataframe with new column
        """
        df_result = df.copy()
        try:
            df_result[column_name] = df_result.eval(expression)
        except Exception as e:
            print(f"Error evaluating expression: {e}")
        return df_result
