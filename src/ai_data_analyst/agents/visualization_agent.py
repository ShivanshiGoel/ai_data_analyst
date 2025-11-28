"""Visualization Agent - Smart chart selection and creation."""
from crewai import Agent
import pandas as pd
from typing import Dict, List


class VisualizationAgent:
    """Agent responsible for intelligent chart selection and specification."""

    def __init__(self, llm=None):
        """Initialize Visualization Agent with optional LLM."""
        self.agent = Agent(
            role='Data Visualization Specialist',
            goal='Create compelling, insightful visualizations that tell data stories',
            backstory="""You are an expert in data storytelling through visualization 
            with a background in UI/UX design. You understand which chart types best 
            communicate different data patterns. You follow Edward Tufte's principles 
            of data visualization and have created dashboards for major corporations.
            Your charts are both beautiful and informative.""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )

    def suggest_visualizations(self, df: pd.DataFrame, schema: List[Dict], 
                              user_intent: str = "", max_charts: int = 6) -> List[Dict]:
        """
        Auto-generate appropriate chart specifications based on data characteristics.

        Args:
            df: DataFrame to visualize
            schema: Column schema information
            user_intent: User's natural language request
            max_charts: Maximum number of charts to generate

        Returns:
            List of ChartSpec dictionaries
        """
        charts = []

        # Get column categories
        numeric_cols = [col['name'] for col in schema 
                       if col.get('data_type') in ['numeric', 'integer', 'float']]
        categorical_cols = [col['name'] for col in schema 
                           if col.get('data_type') == 'categorical']
        datetime_cols = [col['name'] for col in schema 
                        if col.get('data_type') == 'datetime']

        # Chart 1: Time series (if datetime available)
        if datetime_cols and numeric_cols:
            date_col = datetime_cols[0]
            value_col = numeric_cols[0]
            charts.append({
                'chart_type': 'line',
                'title': f'{value_col} Trend Over Time',
                'x_column': date_col,
                'y_column': value_col,
                'rationale': 'Line chart shows temporal trends effectively',
                'aggregation': 'mean'
            })

        # Chart 2: Categorical comparison (bar chart)
        if categorical_cols and numeric_cols:
            cat_col = categorical_cols[0]
            value_col = numeric_cols[0]

            # Check cardinality - limit to top categories if too many
            cardinality = df[cat_col].nunique()
            limit = min(cardinality, 10)

            charts.append({
                'chart_type': 'bar',
                'title': f'{value_col} by {cat_col}',
                'x_column': cat_col,
                'y_column': value_col,
                'rationale': f'Bar chart compares {value_col} across {cat_col} categories',
                'aggregation': 'sum',
                'limit': limit
            })

        # Chart 3: Distribution (histogram)
        if numeric_cols:
            value_col = numeric_cols[0]
            charts.append({
                'chart_type': 'histogram',
                'title': f'Distribution of {value_col}',
                'x_column': value_col,
                'y_column': None,
                'rationale': f'Histogram reveals {value_col} distribution pattern',
                'bins': 20
            })

        # Chart 4: Categorical split (pie chart)
        if categorical_cols:
            cat_col = categorical_cols[0]
            cardinality = df[cat_col].nunique()

            # Only use pie chart if cardinality is reasonable
            if cardinality <= 8:
                charts.append({
                    'chart_type': 'pie',
                    'title': f'{cat_col} Distribution',
                    'x_column': cat_col,
                    'y_column': None,
                    'rationale': f'Pie chart shows proportional breakdown of {cat_col}',
                    'limit': 8
                })

        # Chart 5: Correlation (scatter) if multiple numeric columns
        if len(numeric_cols) >= 2:
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]
            charts.append({
                'chart_type': 'scatter',
                'title': f'{y_col} vs {x_col}',
                'x_column': x_col,
                'y_column': y_col,
                'rationale': f'Scatter plot reveals relationship between {x_col} and {y_col}',
                'color_by': categorical_cols[0] if categorical_cols else None
            })

        # Chart 6: Multi-category comparison (grouped bar)
        if len(categorical_cols) >= 2 and numeric_cols:
            cat1 = categorical_cols[0]
            cat2 = categorical_cols[1]
            value_col = numeric_cols[0]

            # Check combined cardinality
            if df[cat1].nunique() <= 5 and df[cat2].nunique() <= 5:
                charts.append({
                    'chart_type': 'grouped_bar',
                    'title': f'{value_col} by {cat1} and {cat2}',
                    'x_column': cat1,
                    'y_column': value_col,
                    'color_by': cat2,
                    'rationale': f'Grouped bar shows {value_col} across two dimensions',
                    'aggregation': 'mean'
                })

        return charts[:max_charts]

    def create_specific_chart(self, df: pd.DataFrame, schema: List[Dict],
                             chart_type: str, x_col: str, y_col: str = None,
                             **kwargs) -> Dict:
        """
        Create a specific chart based on user requirements.

        Args:
            df: DataFrame
            schema: Column schema
            chart_type: Type of chart (bar, line, pie, etc.)
            x_col: X-axis column
            y_col: Y-axis column (optional for some chart types)
            **kwargs: Additional chart parameters

        Returns:
            ChartSpec dictionary
        """
        # Validate columns exist
        if x_col not in df.columns:
            raise ValueError(f"Column '{x_col}' not found in dataframe")

        if y_col and y_col not in df.columns:
            raise ValueError(f"Column '{y_col}' not found in dataframe")

        # Create chart specification
        chart_spec = {
            'chart_type': chart_type.lower(),
            'title': kwargs.get('title', f'{y_col or "Distribution"} by {x_col}'),
            'x_column': x_col,
            'y_column': y_col,
            'rationale': kwargs.get('rationale', f'User-requested {chart_type} chart'),
            **kwargs
        }

        return chart_spec

    def recommend_chart_type(self, x_col_type: str, y_col_type: str = None) -> str:
        """
        Recommend chart type based on column data types.

        Args:
            x_col_type: Data type of x column (numeric, categorical, datetime)
            y_col_type: Data type of y column (optional)

        Returns:
            Recommended chart type
        """
        # Single variable
        if y_col_type is None:
            if x_col_type == 'numeric':
                return 'histogram'
            elif x_col_type == 'categorical':
                return 'pie'
            elif x_col_type == 'datetime':
                return 'line'

        # Two variables
        if x_col_type == 'datetime' and y_col_type == 'numeric':
            return 'line'
        elif x_col_type == 'categorical' and y_col_type == 'numeric':
            return 'bar'
        elif x_col_type == 'numeric' and y_col_type == 'numeric':
            return 'scatter'
        elif x_col_type == 'categorical' and y_col_type == 'categorical':
            return 'heatmap'

        # Default
        return 'bar'
