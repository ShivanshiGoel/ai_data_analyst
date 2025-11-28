"""Analytics Agent - KPI and statistical analysis."""
from crewai import Agent, Task
import pandas as pd
from typing import Dict, List
from datetime import datetime

# Note: Import these from your models/schemas.py and tools modules
# from models.schemas import AnalyticsResult, KPI
# from tools.pandas_tools import PandasTools
# from utils.type_inference import TypeInferencer


class AnalyticsAgent:
    """Agent responsible for extracting insights and calculating KPIs."""

    def __init__(self, llm=None):
        """Initialize Analytics Agent with optional LLM."""
        self.agent = Agent(
            role='Senior Business Analyst',
            goal='Extract meaningful insights and KPIs from data to drive business decisions',
            backstory="""You are an expert analyst with 15+ years in business intelligence. 
            You have worked with Fortune 500 companies, transforming raw data into actionable insights.
            Your specialty is identifying key performance indicators that matter to stakeholders.
            You understand both technical metrics and business context.""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )

    def generate_analytics(self, df: pd.DataFrame, schema: List[Dict], 
                          target_columns: List[str] = None) -> Dict:
        """
        Generate comprehensive analytics including KPIs and insights.

        Args:
            df: DataFrame to analyze
            schema: Column schema information
            target_columns: Specific columns to focus on

        Returns:
            Dictionary with kpis, insights, and statistical summary
        """
        try:
            # Calculate KPIs
            kpis = self._calculate_kpis(df, schema)

            # Generate insights
            insights = self._generate_insights(df, schema)

            # Statistical summary
            stats = self._generate_statistical_summary(df, schema)

            return {
                'kpis': kpis,
                'insights': insights,
                'statistical_summary': stats,
                'success': True
            }
        except Exception as e:
            return {
                'kpis': [],
                'insights': [f"Error generating analytics: {str(e)}"],
                'statistical_summary': {},
                'success': False
            }

    def _calculate_kpis(self, df: pd.DataFrame, schema: List[Dict]) -> List[Dict]:
        """Calculate key performance indicators based on data types."""
        kpis = []

        # Get numeric columns
        numeric_cols = [col['name'] for col in schema 
                       if col.get('data_type') in ['numeric', 'integer', 'float']]

        # Get categorical columns
        categorical_cols = [col['name'] for col in schema 
                           if col.get('data_type') == 'categorical']

        # Get datetime columns
        datetime_cols = [col['name'] for col in schema 
                        if col.get('data_type') == 'datetime']

        # KPI 1: Record count
        kpis.append({
            'name': 'Total Records',
            'value': len(df),
            'format': 'number',
            'icon': '📊',
            'change': None
        })

        # KPI 2-4: Numeric aggregations
        for col in numeric_cols[:3]:
            col_sum = df[col].sum()
            col_mean = df[col].mean()

            # Check semantic type for better naming
            semantic_type = next((c.get('semantic_type') for c in schema 
                                if c['name'] == col), None)

            if semantic_type == 'revenue' or 'revenue' in col.lower():
                kpis.append({
                    'name': f'Total {col}',
                    'value': col_sum,
                    'format': 'currency',
                    'icon': '💰',
                    'change': None
                })
                kpis.append({
                    'name': f'Average {col}',
                    'value': col_mean,
                    'format': 'currency',
                    'icon': '📈',
                    'change': None
                })
            elif semantic_type == 'quantity' or 'quantity' in col.lower():
                kpis.append({
                    'name': f'Total {col}',
                    'value': col_sum,
                    'format': 'number',
                    'icon': '📦',
                    'change': None
                })
            else:
                kpis.append({
                    'name': f'Sum {col}',
                    'value': col_sum,
                    'format': 'decimal',
                    'icon': '🔢',
                    'change': None
                })

        # KPI: Unique categories
        for col in categorical_cols[:2]:
            unique_count = df[col].nunique()
            kpis.append({
                'name': f'Unique {col}',
                'value': unique_count,
                'format': 'number',
                'icon': '🏷️',
                'change': None
            })

        # KPI: Date range
        if datetime_cols:
            date_col = datetime_cols[0]
            date_range = (df[date_col].max() - df[date_col].min()).days
            kpis.append({
                'name': 'Date Range (Days)',
                'value': date_range,
                'format': 'number',
                'icon': '📅',
                'change': None
            })

        return kpis[:6]  # Limit to 6 KPIs for dashboard

    def _generate_insights(self, df: pd.DataFrame, schema: List[Dict]) -> List[str]:
        """Generate natural language insights from data."""
        insights = []

        # Insight 1: Data volume
        insights.append(
            f"Dataset contains {len(df):,} records across {len(df.columns)} dimensions"
        )

        # Insight 2: Data quality
        null_count = df.isnull().sum().sum()
        null_pct = (null_count / (len(df) * len(df.columns))) * 100
        if null_pct > 0:
            insights.append(
                f"Data quality: {null_pct:.1f}% missing values detected across dataset"
            )
        else:
            insights.append("Data quality: No missing values detected - excellent data quality")

        # Insight 3: Numeric extremes
        numeric_cols = [col['name'] for col in schema 
                       if col.get('data_type') in ['numeric', 'integer', 'float']]
        if numeric_cols:
            top_col = numeric_cols[0]
            max_val = df[top_col].max()
            min_val = df[top_col].min()
            insights.append(
                f"{top_col} ranges from {min_val:,.2f} to {max_val:,.2f}"
            )

        # Insight 4: Categorical distribution
        categorical_cols = [col['name'] for col in schema 
                           if col.get('data_type') == 'categorical']
        if categorical_cols:
            cat_col = categorical_cols[0]
            top_category = df[cat_col].value_counts().index[0]
            top_count = df[cat_col].value_counts().iloc[0]
            pct = (top_count / len(df)) * 100
            insights.append(
                f"Most common {cat_col}: '{top_category}' appears in {pct:.1f}% of records"
            )

        # Insight 5: Time trends (if datetime present)
        datetime_cols = [col['name'] for col in schema 
                        if col.get('data_type') == 'datetime']
        if datetime_cols and numeric_cols:
            date_col = datetime_cols[0]
            value_col = numeric_cols[0]

            # Check if trending up or down
            df_sorted = df.sort_values(date_col)
            first_half = df_sorted[value_col].iloc[:len(df)//2].mean()
            second_half = df_sorted[value_col].iloc[len(df)//2:].mean()

            if second_half > first_half * 1.1:
                insights.append(
                    f"Positive trend: {value_col} increased by {((second_half/first_half - 1) * 100):.1f}% over time period"
                )
            elif second_half < first_half * 0.9:
                insights.append(
                    f"Declining trend: {value_col} decreased by {((1 - second_half/first_half) * 100):.1f}% over time period"
                )
            else:
                insights.append(f"{value_col} shows stable performance over time period")

        return insights[:5]  # Limit to 5 insights

    def _generate_statistical_summary(self, df: pd.DataFrame, 
                                      schema: List[Dict]) -> Dict:
        """Generate statistical summary for numeric columns."""
        numeric_cols = [col['name'] for col in schema 
                       if col.get('data_type') in ['numeric', 'integer', 'float']]

        if not numeric_cols:
            return {}

        stats = df[numeric_cols].describe().to_dict()
        return stats
