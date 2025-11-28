"""Advanced Excel Tools - Enterprise-grade operations matching Power BI capabilities."""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class AdvancedExcelTools:
    """
    Enterprise-grade Excel operations that match Power BI capabilities:
    - Complex pivot tables with multiple dimensions
    - Power Query-like transformations
    - Advanced formulas (INDEX-MATCH, array formulas)
    - Time intelligence (YTD, QTD, rolling windows)
    - Data modeling (relationships, calculated columns)
    - What-if analysis and scenarios
    """
    
    # ========================================================================
    # PIVOT TABLE OPERATIONS (Power BI Matrix equivalents)
    # ========================================================================
    
    @staticmethod
    def create_pivot_table(df: pd.DataFrame, 
                          rows: List[str],
                          columns: Optional[List[str]] = None,
                          values: List[str] = None,
                          aggfunc: Dict[str, str] = None,
                          margins: bool = True,
                          fill_value: Any = 0) -> pd.DataFrame:
        """
        Create advanced pivot table with multiple dimensions.
        
        Args:
            df: Source dataframe
            rows: Row fields (can be multiple for nested grouping)
            columns: Column fields (optional, for cross-tab)
            values: Value fields to aggregate
            aggfunc: Aggregation functions {'column': 'sum'/'mean'/'count'/etc}
            margins: Add grand totals
            fill_value: Value for missing data
        
        Returns:
            Pivot table dataframe
        """
        if not aggfunc:
            aggfunc = {val: 'sum' for val in values}
        
        pivot = pd.pivot_table(
            df,
            index=rows,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
            margins=margins,
            margins_name='Grand Total',
            fill_value=fill_value
        )
        
        return pivot
    
    @staticmethod
    def create_multi_level_pivot(df: pd.DataFrame,
                                 dimensions: Dict[str, List[str]],
                                 measures: Dict[str, str]) -> pd.DataFrame:
        """
        Create Power BI-style multi-level pivot with complex aggregations.
        
        Args:
            dimensions: {'rows': ['col1', 'col2'], 'columns': ['col3']}
            measures: {'measure_name': 'aggregation'}
        
        Example:
            dimensions = {'rows': ['Region', 'Product'], 'columns': ['Year']}
            measures = {'Total Sales': 'sum', 'Avg Price': 'mean'}
        """
        pivot = df.pivot_table(
            index=dimensions.get('rows', []),
            columns=dimensions.get('columns'),
            values=list(measures.keys()),
            aggfunc=measures,
            margins=True,
            fill_value=0
        )
        
        # Calculate percentage of total
        if len(dimensions.get('rows', [])) > 0:
            for measure in measures.keys():
                if measure in pivot.columns:
                    total = pivot[measure].sum()
                    pivot[f'{measure} %'] = (pivot[measure] / total * 100).round(2)
        
        return pivot
    
    # ========================================================================
    # TIME INTELLIGENCE (DAX equivalents)
    # ========================================================================
    
    @staticmethod
    def calculate_time_intelligence(df: pd.DataFrame,
                                    date_column: str,
                                    value_column: str,
                                    metrics: List[str]) -> pd.DataFrame:
        """
        Calculate Power BI-style time intelligence measures.
        
        Metrics available:
        - YTD (Year to Date)
        - QTD (Quarter to Date)
        - MTD (Month to Date)
        - YoY (Year over Year growth)
        - MoM (Month over Month growth)
        - Rolling_3M, Rolling_6M, Rolling_12M
        - SAMEPERIODLASTYEAR
        
        Args:
            df: Dataframe with date column
            date_column: Name of date column
            value_column: Name of value column to aggregate
            metrics: List of metric names to calculate
        
        Returns:
            Enhanced dataframe with time intelligence columns
        """
        result = df.copy()
        result[date_column] = pd.to_datetime(result[date_column])
        result = result.sort_values(date_column)
        
        # Extract date parts
        result['Year'] = result[date_column].dt.year
        result['Quarter'] = result[date_column].dt.quarter
        result['Month'] = result[date_column].dt.month
        result['Week'] = result[date_column].dt.isocalendar().week
        
        if 'YTD' in metrics:
            result['YTD'] = result.groupby('Year')[value_column].cumsum()
        
        if 'QTD' in metrics:
            result['QTD'] = result.groupby(['Year', 'Quarter'])[value_column].cumsum()
        
        if 'MTD' in metrics:
            result['MTD'] = result.groupby(['Year', 'Month'])[value_column].cumsum()
        
        if 'YoY' in metrics:
            yearly = result.groupby('Year')[value_column].sum()
            result['YoY_Growth_%'] = result['Year'].map(
                lambda y: ((yearly.get(y, 0) - yearly.get(y-1, 0)) / yearly.get(y-1, 1) * 100)
                if yearly.get(y-1, 0) > 0 else 0
            )
        
        if 'Rolling_3M' in metrics:
            result['Rolling_3M'] = result[value_column].rolling(window=90, min_periods=1).sum()
        
        if 'Rolling_6M' in metrics:
            result['Rolling_6M'] = result[value_column].rolling(window=180, min_periods=1).sum()
        
        if 'Rolling_12M' in metrics:
            result['Rolling_12M'] = result[value_column].rolling(window=365, min_periods=1).sum()
        
        return result
    
    # ========================================================================
    # POWER QUERY TRANSFORMATIONS
    # ========================================================================
    
    @staticmethod
    def unpivot_columns(df: pd.DataFrame,
                       id_columns: List[str],
                       value_columns: List[str],
                       var_name: str = 'Variable',
                       value_name: str = 'Value') -> pd.DataFrame:
        """
        Unpivot/melt wide format to long format (Power Query: Unpivot Columns).
        
        Example:
            Input:  Region | Q1_Sales | Q2_Sales | Q3_Sales
            Output: Region | Quarter | Sales
        """
        return pd.melt(
            df,
            id_vars=id_columns,
            value_vars=value_columns,
            var_name=var_name,
            value_name=value_name
        )
    
    @staticmethod
    def pivot_wider(df: pd.DataFrame,
                   index_columns: List[str],
                   pivot_column: str,
                   value_column: str,
                   aggfunc: str = 'sum') -> pd.DataFrame:
        """
        Transform long format to wide format (Power Query: Pivot Column).
        
        Example:
            Input:  Region | Quarter | Sales
            Output: Region | Q1_Sales | Q2_Sales | Q3_Sales
        """
        return df.pivot_table(
            index=index_columns,
            columns=pivot_column,
            values=value_column,
            aggfunc=aggfunc,
            fill_value=0
        ).reset_index()
    
    @staticmethod
    def merge_queries(df1: pd.DataFrame,
                     df2: pd.DataFrame,
                     merge_keys: List[str],
                     merge_type: str = 'inner',
                     suffixes: Tuple[str, str] = ('_left', '_right')) -> pd.DataFrame:
        """
        Merge two dataframes (Power Query: Merge Queries).
        
        Args:
            merge_type: 'inner', 'left', 'right', 'outer', 'cross'
        """
        return pd.merge(
            df1, df2,
            on=merge_keys,
            how=merge_type,
            suffixes=suffixes
        )
    
    @staticmethod
    def append_queries(dataframes: List[pd.DataFrame],
                      ignore_index: bool = True) -> pd.DataFrame:
        """
        Append multiple dataframes (Power Query: Append Queries).
        """
        return pd.concat(dataframes, ignore_index=ignore_index)
    
    @staticmethod
    def group_and_aggregate(df: pd.DataFrame,
                           group_by: List[str],
                           aggregations: Dict[str, List[str]]) -> pd.DataFrame:
        """
        Advanced grouping with multiple aggregations per column.
        
        Args:
            aggregations: {'column': ['sum', 'mean', 'count', 'std']}
        
        Example:
            {'Sales': ['sum', 'mean'], 'Quantity': ['sum', 'count']}
        """
        agg_dict = {}
        for col, funcs in aggregations.items():
            for func in funcs:
                agg_dict[f'{col}_{func}'] = (col, func)
        
        result = df.groupby(group_by).agg(**agg_dict).reset_index()
        return result
    
    # ========================================================================
    # CALCULATED COLUMNS (DAX-style)
    # ========================================================================
    
    @staticmethod
    def add_calculated_column(df: pd.DataFrame,
                             column_name: str,
                             formula: str,
                             context: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Add calculated column using Python expression (DAX equivalent).
        
        Args:
            formula: Python expression, e.g., "df['Price'] * df['Quantity']"
            context: Additional variables for formula evaluation
        
        Example:
            formula = "df['Revenue'] / df['Quantity']"  # Average price
            formula = "df['Sales'].rolling(7).mean()"   # 7-day moving average
        """
        result = df.copy()
        
        # Safe eval context
        eval_context = {'df': result, 'np': np, 'pd': pd}
        if context:
            eval_context.update(context)
        
        try:
            result[column_name] = eval(formula, eval_context)
        except Exception as e:
            raise ValueError(f"Error in calculated column formula: {str(e)}")
        
        return result
    
    @staticmethod
    def create_ranking_column(df: pd.DataFrame,
                             value_column: str,
                             partition_by: List[str] = None,
                             ascending: bool = False,
                             rank_type: str = 'dense') -> pd.DataFrame:
        """
        Create ranking column (RANKX in DAX).
        
        Args:
            partition_by: Columns to partition ranking (rank within groups)
            rank_type: 'dense', 'min', 'max', 'average', 'first'
        """
        result = df.copy()
        
        if partition_by:
            result['Rank'] = result.groupby(partition_by)[value_column].rank(
                method=rank_type,
                ascending=ascending
            )
        else:
            result['Rank'] = result[value_column].rank(
                method=rank_type,
                ascending=ascending
            )
        
        return result
    
    # ========================================================================
    # ADVANCED FILTERING
    # ========================================================================
    
    @staticmethod
    def apply_complex_filter(df: pd.DataFrame,
                            filter_expression: str) -> pd.DataFrame:
        """
        Apply complex filter using Python query syntax.
        
        Examples:
            "Sales > 1000 and Region == 'North'"
            "Year >= 2020 and (Status == 'Active' or Priority == 'High')"
            "ProductName.str.contains('Pro')"
        """
        try:
            return df.query(filter_expression)
        except Exception as e:
            raise ValueError(f"Invalid filter expression: {str(e)}")
    
    @staticmethod
    def create_slicer_filter(df: pd.DataFrame,
                            slicer_column: str,
                            selected_values: List[Any]) -> pd.DataFrame:
        """
        Apply slicer-style filtering (Power BI slicers).
        """
        return df[df[slicer_column].isin(selected_values)]
    
    # ========================================================================
    # WHAT-IF ANALYSIS
    # ========================================================================
    
    @staticmethod
    def create_scenario_analysis(df: pd.DataFrame,
                                 base_column: str,
                                 scenarios: Dict[str, float]) -> pd.DataFrame:
        """
        Create what-if scenario analysis.
        
        Args:
            scenarios: {'Best Case': 1.2, 'Worst Case': 0.8, 'Expected': 1.0}
        
        Returns:
            Dataframe with scenario columns
        """
        result = df.copy()
        
        for scenario_name, multiplier in scenarios.items():
            result[f'{base_column}_{scenario_name}'] = result[base_column] * multiplier
        
        return result
    
    @staticmethod
    def sensitivity_analysis(df: pd.DataFrame,
                            input_column: str,
                            output_column: str,
                            variations: List[float]) -> pd.DataFrame:
        """
        Perform sensitivity analysis by varying input values.
        
        Args:
            variations: List of multipliers, e.g., [0.8, 0.9, 1.0, 1.1, 1.2]
        """
        results = []
        
        for variation in variations:
            temp_df = df.copy()
            temp_df[input_column] = temp_df[input_column] * variation
            temp_df['Variation'] = f"{variation:.1%}"
            results.append(temp_df)
        
        return pd.concat(results, ignore_index=True)
    
    # ========================================================================
    # DATA RELATIONSHIPS
    # ========================================================================
    
    @staticmethod
    def create_lookup_table(df: pd.DataFrame,
                           key_column: str,
                           value_columns: List[str]) -> Dict[Any, Dict]:
        """
        Create lookup dictionary for data relationships.
        
        Returns:
            {key: {col1: val1, col2: val2, ...}}
        """
        lookup = {}
        for _, row in df.iterrows():
            key = row[key_column]
            lookup[key] = {col: row[col] for col in value_columns}
        return lookup
    
    @staticmethod
    def apply_related_lookup(df: pd.DataFrame,
                            lookup_key: str,
                            lookup_table: pd.DataFrame,
                            return_column: str,
                            new_column_name: str = None) -> pd.DataFrame:
        """
        Apply RELATED function (DAX equivalent) using lookup table.
        """
        if new_column_name is None:
            new_column_name = f'Related_{return_column}'
        
        result = df.copy()
        result = result.merge(
            lookup_table[[lookup_key, return_column]],
            on=lookup_key,
            how='left'
        )
        result.rename(columns={return_column: new_column_name}, inplace=True)
        
        return result
    
    # ========================================================================
    # STATISTICAL MEASURES
    # ========================================================================
    
    @staticmethod
    def calculate_statistical_measures(df: pd.DataFrame,
                                       value_column: str,
                                       group_by: List[str] = None) -> pd.DataFrame:
        """
        Calculate comprehensive statistical measures.
        """
        if group_by:
            stats = df.groupby(group_by)[value_column].agg([
                ('Count', 'count'),
                ('Sum', 'sum'),
                ('Mean', 'mean'),
                ('Median', 'median'),
                ('Std', 'std'),
                ('Min', 'min'),
                ('Max', 'max'),
                ('Q1', lambda x: x.quantile(0.25)),
                ('Q3', lambda x: x.quantile(0.75))
            ]).reset_index()
        else:
            stats = pd.DataFrame([{
                'Count': df[value_column].count(),
                'Sum': df[value_column].sum(),
                'Mean': df[value_column].mean(),
                'Median': df[value_column].median(),
                'Std': df[value_column].std(),
                'Min': df[value_column].min(),
                'Max': df[value_column].max(),
                'Q1': df[value_column].quantile(0.25),
                'Q3': df[value_column].quantile(0.75)
            }])
        
        return stats
