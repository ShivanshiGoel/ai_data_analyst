"""Advanced Excel Operations - Enterprise-grade capabilities."""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta


class AdvancedOperations:
    """
    Advanced data operations matching Power BI capabilities.
    Handles complex transformations, calculations, and analytics.
    """
    
    @staticmethod
    def create_pivot_table(df: pd.DataFrame, 
                          index: Union[str, List[str]],
                          columns: Optional[str] = None,
                          values: Optional[Union[str, List[str]]] = None,
                          aggfunc: Union[str, Dict] = 'sum',
                          fill_value: Any = None) -> pd.DataFrame:
        """
        Create advanced pivot table with multiple aggregations.
        
        Args:
            df: Input dataframe
            index: Row index columns
            columns: Column pivot column
            values: Values to aggregate
            aggfunc: Aggregation function(s)
            fill_value: Value to replace NaN
        
        Returns:
            Pivoted dataframe
        """
        if values is None:
            # Auto-detect numeric columns
            values = df.select_dtypes(include=[np.number]).columns.tolist()
        
        pivot = pd.pivot_table(
            df,
            index=index,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
            fill_value=fill_value
        )
        
        return pivot.reset_index()
    
    @staticmethod
    def time_series_analysis(df: pd.DataFrame,
                            date_column: str,
                            value_column: str,
                            freq: str = 'D') -> Dict[str, Any]:
        """
        Perform time series analysis.
        
        Args:
            df: Input dataframe
            date_column: Column containing dates
            value_column: Column with values to analyze
            freq: Frequency for resampling ('D', 'W', 'M', 'Q', 'Y')
        
        Returns:
            Dict with time series insights
        """
        df_ts = df.copy()
        df_ts[date_column] = pd.to_datetime(df_ts[date_column])
        df_ts = df_ts.set_index(date_column)
        
        # Resample to frequency
        resampled = df_ts[value_column].resample(freq).sum()
        
        # Calculate trend
        from scipy import stats
        x = np.arange(len(resampled))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, resampled.values)
        
        # Calculate moving averages
        ma_7 = resampled.rolling(window=7, min_periods=1).mean()
        ma_30 = resampled.rolling(window=30, min_periods=1).mean()
        
        # Seasonality detection (basic)
        seasonality = resampled.values.std() / resampled.values.mean() if resampled.values.mean() != 0 else 0
        
        return {
            'resampled_data': resampled,
            'trend_slope': slope,
            'trend_direction': 'upward' if slope > 0 else 'downward',
            'r_squared': r_value ** 2,
            'moving_average_7': ma_7,
            'moving_average_30': ma_30,
            'seasonality_coefficient': seasonality,
            'total_sum': resampled.sum(),
            'average': resampled.mean(),
            'volatility': resampled.std()
        }
    
    @staticmethod
    def calculate_growth_metrics(df: pd.DataFrame,
                                 date_column: str,
                                 value_column: str,
                                 period: str = 'M') -> pd.DataFrame:
        """
        Calculate growth metrics (MoM, YoY, etc.).
        
        Args:
            df: Input dataframe
            date_column: Date column
            value_column: Value column
            period: Period for comparison ('D', 'M', 'Q', 'Y')
        
        Returns:
            Dataframe with growth metrics
        """
        df_growth = df.copy()
        df_growth[date_column] = pd.to_datetime(df_growth[date_column])
        df_growth = df_growth.sort_values(date_column)
        
        # Group by period
        df_grouped = df_growth.groupby(pd.Grouper(key=date_column, freq=period))[value_column].sum().reset_index()
        
        # Calculate period-over-period growth
        df_grouped['previous_period'] = df_grouped[value_column].shift(1)
        df_grouped['growth_absolute'] = df_grouped[value_column] - df_grouped['previous_period']
        df_grouped['growth_percentage'] = ((df_grouped[value_column] - df_grouped['previous_period']) / 
                                          df_grouped['previous_period'] * 100)
        
        # Calculate year-over-year if applicable
        periods_per_year = {'D': 365, 'M': 12, 'Q': 4, 'Y': 1}
        if period in periods_per_year:
            shift_periods = periods_per_year[period]
            df_grouped['value_year_ago'] = df_grouped[value_column].shift(shift_periods)
            df_grouped['yoy_growth'] = ((df_grouped[value_column] - df_grouped['value_year_ago']) /
                                       df_grouped['value_year_ago'] * 100)
        
        return df_grouped
    
    @staticmethod
    def segment_analysis(df: pd.DataFrame,
                        segment_column: str,
                        metric_columns: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Perform comprehensive segment analysis.
        
        Args:
            df: Input dataframe
            segment_column: Column to segment by
            metric_columns: Metrics to analyze per segment
        
        Returns:
            Dict with various segment analyses
        """
        results = {}
        
        # Basic aggregation by segment
        agg_dict = {col: ['sum', 'mean', 'count', 'std'] for col in metric_columns}
        results['summary'] = df.groupby(segment_column).agg(agg_dict)
        
        # Percentage contribution
        totals = df[metric_columns].sum()
        segment_sums = df.groupby(segment_column)[metric_columns].sum()
        results['contribution_pct'] = (segment_sums / totals * 100)
        
        # Ranking
        results['ranking'] = segment_sums.rank(ascending=False, method='dense')
        
        # Segment size
        results['segment_size'] = df.groupby(segment_column).size()
        
        return results
    
    @staticmethod
    def cohort_analysis(df: pd.DataFrame,
                       customer_column: str,
                       date_column: str,
                       value_column: str) -> pd.DataFrame:
        """
        Perform cohort analysis.
        
        Args:
            df: Input dataframe
            customer_column: Customer identifier column
            date_column: Date column
            value_column: Value to analyze
        
        Returns:
            Cohort analysis table
        """
        df_cohort = df.copy()
        df_cohort[date_column] = pd.to_datetime(df_cohort[date_column])
        
        # Get first purchase date for each customer
        df_cohort['cohort'] = df_cohort.groupby(customer_column)[date_column].transform('min')
        df_cohort['cohort_period'] = df_cohort['cohort'].dt.to_period('M')
        
        # Calculate period number
        df_cohort['period_number'] = ((df_cohort[date_column].dt.to_period('M') - 
                                      df_cohort['cohort_period']).apply(lambda x: x.n))
        
        # Create cohort table
        cohort_data = df_cohort.groupby(['cohort_period', 'period_number'])[value_column].sum().reset_index()
        cohort_table = cohort_data.pivot(index='cohort_period', columns='period_number', values=value_column)
        
        return cohort_table
    
    @staticmethod
    def abc_analysis(df: pd.DataFrame,
                    item_column: str,
                    value_column: str) -> pd.DataFrame:
        """
        Perform ABC analysis (Pareto analysis).
        
        Args:
            df: Input dataframe
            item_column: Item identifier column
            value_column: Value column for analysis
        
        Returns:
            Dataframe with ABC classification
        """
        # Aggregate by item
        abc_df = df.groupby(item_column)[value_column].sum().reset_index()
        abc_df = abc_df.sort_values(value_column, ascending=False)
        
        # Calculate cumulative percentage
        abc_df['total'] = abc_df[value_column].sum()
        abc_df['percentage'] = (abc_df[value_column] / abc_df['total'] * 100)
        abc_df['cumulative_percentage'] = abc_df['percentage'].cumsum()
        
        # Classify into ABC categories
        def classify(cum_pct):
            if cum_pct <= 80:
                return 'A'
            elif cum_pct <= 95:
                return 'B'
            else:
                return 'C'
        
        abc_df['category'] = abc_df['cumulative_percentage'].apply(classify)
        
        return abc_df
    
    @staticmethod
    def correlation_analysis(df: pd.DataFrame,
                            columns: Optional[List[str]] = None,
                            method: str = 'pearson') -> pd.DataFrame:
        """
        Calculate correlation matrix.
        
        Args:
            df: Input dataframe
            columns: Columns to include (None = all numeric)
            method: Correlation method ('pearson', 'spearman', 'kendall')
        
        Returns:
            Correlation matrix
        """
        if columns:
            df_corr = df[columns]
        else:
            df_corr = df.select_dtypes(include=[np.number])
        
        return df_corr.corr(method=method)
    
    @staticmethod
    def rank_and_filter(df: pd.DataFrame,
                       rank_column: str,
                       top_n: Optional[int] = None,
                       bottom_n: Optional[int] = None,
                       ascending: bool = False) -> pd.DataFrame:
        """
        Rank and filter top/bottom N records.
        
        Args:
            df: Input dataframe
            rank_column: Column to rank by
            top_n: Number of top records
            bottom_n: Number of bottom records
            ascending: Ranking order
        
        Returns:
            Filtered dataframe
        """
        df_ranked = df.sort_values(rank_column, ascending=ascending)
        
        if top_n:
            return df_ranked.head(top_n)
        elif bottom_n:
            return df_ranked.tail(bottom_n)
        else:
            return df_ranked
    
    @staticmethod
    def running_totals(df: pd.DataFrame,
                      value_column: str,
                      group_by: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Calculate running/cumulative totals.
        
        Args:
            df: Input dataframe
            value_column: Column to calculate running total
            group_by: Columns to group by
        
        Returns:
            Dataframe with running totals
        """
        df_result = df.copy()
        
        if group_by:
            df_result['running_total'] = df_result.groupby(group_by)[value_column].cumsum()
        else:
            df_result['running_total'] = df_result[value_column].cumsum()
        
        return df_result
    
    @staticmethod
    def window_functions(df: pd.DataFrame,
                        value_column: str,
                        window_size: int = 7,
                        functions: List[str] = ['mean', 'sum', 'std']) -> pd.DataFrame:
        """
        Apply rolling window functions.
        
        Args:
            df: Input dataframe
            value_column: Column to apply functions
            window_size: Size of rolling window
            functions: List of functions to apply
        
        Returns:
            Dataframe with window calculations
        """
        df_result = df.copy()
        
        for func in functions:
            col_name = f'{value_column}_{func}_{window_size}'
            df_result[col_name] = df_result[value_column].rolling(
                window=window_size, 
                min_periods=1
            ).agg(func)
        
        return df_result
    
    @staticmethod
    def percentile_analysis(df: pd.DataFrame,
                          value_column: str,
                          percentiles: List[float] = [0.25, 0.5, 0.75, 0.9, 0.95]) -> Dict[str, float]:
        """
        Calculate percentile distributions.
        
        Args:
            df: Input dataframe
            value_column: Column to analyze
            percentiles: List of percentiles to calculate
        
        Returns:
            Dict of percentile values
        """
        results = {}
        for p in percentiles:
            results[f'p{int(p*100)}'] = df[value_column].quantile(p)
        
        return results
    
    @staticmethod
    def create_calculated_columns(df: pd.DataFrame,
                                 calculations: Dict[str, str]) -> pd.DataFrame:
        """
        Create multiple calculated columns using expressions.
        
        Args:
            df: Input dataframe
            calculations: Dict of {new_column_name: expression}
        
        Returns:
            Dataframe with new columns
        """
        df_result = df.copy()
        
        for col_name, expression in calculations.items():
            try:
                df_result[col_name] = df_result.eval(expression)
            except Exception as e:
                print(f"Warning: Could not create column '{col_name}': {e}")
        
        return df_result
