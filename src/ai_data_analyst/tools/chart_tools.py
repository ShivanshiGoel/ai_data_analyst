"""Tools for chart generation using matplotlib and plotly."""
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Optional
import seaborn as sns
from ai_data_analyst.models.schemas import ChartSpec, ChartType


class ChartTools:
    """Chart generation and visualization tools."""
    
    @staticmethod
    def create_chart(df: pd.DataFrame, spec: ChartSpec, use_plotly: bool = True):
        """
        Create chart based on specification.
        
        Args:
            df: Input dataframe
            spec: Chart specification
            use_plotly: Use plotly (True) or matplotlib (False)
        
        Returns:
            Plotly figure or matplotlib figure
        """
        if use_plotly:
            return ChartTools._create_plotly_chart(df, spec)
        else:
            return ChartTools._create_matplotlib_chart(df, spec)
    
    @staticmethod
    def _create_plotly_chart(df: pd.DataFrame, spec: ChartSpec):
        """Create Plotly chart."""
        chart_type = spec.chart_type
        
        if chart_type == ChartType.BAR:
            fig = px.bar(df, x=spec.x_column, y=spec.y_column, 
                        color=spec.color_column, title=spec.title)
        
        elif chart_type == ChartType.LINE:
            fig = px.line(df, x=spec.x_column, y=spec.y_column, 
                         color=spec.color_column, title=spec.title)
        
        elif chart_type == ChartType.PIE:
            fig = px.pie(df, names=spec.x_column, values=spec.y_column, 
                        title=spec.title)
        
        elif chart_type == ChartType.SCATTER:
            fig = px.scatter(df, x=spec.x_column, y=spec.y_column, 
                           color=spec.color_column, title=spec.title)
        
        elif chart_type == ChartType.HISTOGRAM:
            fig = px.histogram(df, x=spec.x_column, title=spec.title)
        
        elif chart_type == ChartType.BOX:
            fig = px.box(df, x=spec.x_column, y=spec.y_column, title=spec.title)
        
        elif chart_type == ChartType.HEATMAP:
            # Prepare correlation matrix or pivot
            if spec.parameters.get('correlation', False):
                numeric_df = df.select_dtypes(include=['number'])
                corr_matrix = numeric_df.corr()
                fig = px.imshow(corr_matrix, title=spec.title, 
                              labels=dict(color="Correlation"))
            else:
                fig = go.Figure(data=go.Heatmap(
                    z=df[spec.y_column].values,
                    x=df[spec.x_column].values,
                    y=df.index
                ))
                fig.update_layout(title=spec.title)
        
        else:
            # Default to bar chart
            fig = px.bar(df, x=spec.x_column, y=spec.y_column, title=spec.title)
        
        fig.update_layout(
            template="plotly_white",
            height=500,
            font=dict(size=12)
        )
        
        return fig
    
    @staticmethod
    def _create_matplotlib_chart(df: pd.DataFrame, spec: ChartSpec):
        """Create Matplotlib chart."""
        fig, ax = plt.subplots(figsize=(10, 6))
        chart_type = spec.chart_type
        
        if chart_type == ChartType.BAR:
            df.plot(kind='bar', x=spec.x_column, y=spec.y_column, ax=ax)
        
        elif chart_type == ChartType.LINE:
            df.plot(kind='line', x=spec.x_column, y=spec.y_column, ax=ax)
        
        elif chart_type == ChartType.PIE:
            df.set_index(spec.x_column)[spec.y_column].plot(kind='pie', ax=ax, autopct='%1.1f%%')
        
        elif chart_type == ChartType.SCATTER:
            ax.scatter(df[spec.x_column], df[spec.y_column])
        
        elif chart_type == ChartType.HISTOGRAM:
            df[spec.x_column].plot(kind='hist', ax=ax, bins=20)
        
        elif chart_type == ChartType.HEATMAP:
            numeric_df = df.select_dtypes(include=['number'])
            sns.heatmap(numeric_df.corr(), annot=True, ax=ax, cmap='coolwarm')
        
        ax.set_title(spec.title)
        plt.tight_layout()
        return fig
    
    @staticmethod
    def prepare_data_for_chart(df: pd.DataFrame, spec: ChartSpec) -> pd.DataFrame:
        """
        Prepare and aggregate data for charting.
        
        Returns:
            Processed dataframe ready for charting
        """
        df_chart = df.copy()
        
        # Apply aggregation if specified
        if spec.aggregation and spec.x_column and spec.y_column:
            agg_func = spec.aggregation
            
            if agg_func in ['sum', 'mean', 'count', 'min', 'max']:
                df_chart = df_chart.groupby(spec.x_column)[spec.y_column].agg(agg_func).reset_index()
        
        # Sort for better visualization
        if spec.x_column in df_chart.columns:
            df_chart = df_chart.sort_values(spec.x_column)
        
        # Limit rows for readability
        max_rows = spec.parameters.get('max_rows', 50)
        if len(df_chart) > max_rows:
            df_chart = df_chart.head(max_rows)
        
        return df_chart
    
    @staticmethod
    def suggest_chart_type(x_col_type: str, y_col_type: str, 
                          row_count: int) -> ChartType:
        """
        Suggest appropriate chart type based on data characteristics.
        
        Args:
            x_col_type: Type of x column ('categorical', 'numeric', 'datetime')
            y_col_type: Type of y column
            row_count: Number of rows
        
        Returns:
            Suggested ChartType
        """
        if x_col_type == 'datetime' and y_col_type == 'numeric':
            return ChartType.LINE
        
        elif x_col_type == 'categorical' and y_col_type == 'numeric':
            if row_count <= 10:
                return ChartType.PIE
            else:
                return ChartType.BAR
        
        elif x_col_type == 'numeric' and y_col_type == 'numeric':
            return ChartType.SCATTER
        
        elif x_col_type == 'categorical' and y_col_type is None:
            return ChartType.HISTOGRAM
        
        else:
            return ChartType.BAR  # Default
    
    @staticmethod
    def create_dashboard_charts(df: pd.DataFrame, schema, 
                               max_charts: int = 4) -> list:
        """
        Auto-generate multiple charts for dashboard.
        
        Returns:
            List of ChartSpec objects
        """
        from ai_data_analyst.utils.type_inference import TypeInferencer
        
        charts = []
        numeric_cols = TypeInferencer.get_numeric_columns(schema)
        categorical_cols = TypeInferencer.get_categorical_columns(schema)
        date_cols = TypeInferencer.get_date_columns(schema)
        
        # Chart 1: Top categories by main metric
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            
            charts.append(ChartSpec(
                chart_type=ChartType.BAR,
                title=f"{num_col} by {cat_col}",
                x_column=cat_col,
                y_column=num_col,
                aggregation='sum',
                rationale=f"Shows total {num_col} across different {cat_col}"
            ))
        
        # Chart 2: Time series if date column exists
        if len(date_cols) > 0 and len(numeric_cols) > 0:
            date_col = date_cols[0]
            num_col = numeric_cols[0]
            
            charts.append(ChartSpec(
                chart_type=ChartType.LINE,
                title=f"{num_col} Trend Over Time",
                x_column=date_col,
                y_column=num_col,
                aggregation='sum',
                rationale=f"Shows how {num_col} changes over time"
            ))
        
        # Chart 3: Distribution of main metric
        if len(numeric_cols) > 0:
            num_col = numeric_cols[0]
            
            charts.append(ChartSpec(
                chart_type=ChartType.HISTOGRAM,
                title=f"Distribution of {num_col}",
                x_column=num_col,
                rationale=f"Shows the distribution pattern of {num_col}"
            ))
        
        # Chart 4: Pie chart for categorical distribution
        if len(categorical_cols) > 0:
            cat_col = categorical_cols[0]
            
            charts.append(ChartSpec(
                chart_type=ChartType.PIE,
                title=f"Distribution by {cat_col}",
                x_column=cat_col,
                y_column=None,
                aggregation='count',
                rationale=f"Shows proportion of records in each {cat_col}"
            ))
        
        return charts[:max_charts]