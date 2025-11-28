"""Type inference engine for automatic schema detection."""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import re


class TypeInferencer:
    """Intelligent type and semantic inference for dataframes."""

    # Semantic keyword patterns
    REVENUE_KEYWORDS = ['revenue', 'sales', 'amount', 'total', 'price', 'cost', 'value']
    QUANTITY_KEYWORDS = ['quantity', 'qty', 'count', 'number', 'units', 'volume']
    LOCATION_KEYWORDS = ['city', 'country', 'region', 'state', 'location', 'address', 'area']
    DATE_KEYWORDS = ['date', 'time', 'day', 'month', 'year', 'timestamp', 'created', 'updated']
    ID_KEYWORDS = ['id', 'key', 'code', 'identifier', 'uuid', 'guid']
    NAME_KEYWORDS = ['name', 'title', 'label', 'description', 'desc']
    CATEGORY_KEYWORDS = ['category', 'type', 'class', 'group', 'segment', 'status']

    @staticmethod
    def infer_schema(df: pd.DataFrame, sample_size: int = 1000) -> Dict[str, Any]:
        """
        Infer complete schema from dataframe.

        Args:
            df: DataFrame to analyze
            sample_size: Number of rows to sample for analysis

        Returns:
            Dictionary with schema information
        """
        columns = []

        # Sample dataframe for efficiency
        df_sample = df.head(sample_size) if len(df) > sample_size else df

        for col_name in df.columns:
            col_data = df_sample[col_name]

            # Detect data type
            data_type = TypeInferencer._detect_data_type(col_data)

            # Detect semantic type
            semantic_type = TypeInferencer._detect_semantic_type(col_name, col_data, data_type)

            # Calculate statistics
            stats = TypeInferencer._calculate_column_stats(col_data, data_type)

            # Build column schema
            column_schema = {
                'name': col_name,
                'data_type': data_type,
                'semantic_type': semantic_type,
                'nullable': stats['null_count'] > 0,
                'unique_count': stats['unique_count'],
                'null_count': stats['null_count'],
                'sample_values': stats['sample_values']
            }

            columns.append(column_schema)

        return {
            'columns': columns,
            'row_count': len(df),
            'column_count': len(df.columns)
        }

    @staticmethod
    def _detect_data_type(series: pd.Series) -> str:
        """
        Detect pandas data type.

        Args:
            series: Pandas series

        Returns:
            Data type string (numeric, categorical, datetime, text, boolean)
        """
        # Drop nulls for type detection
        series_clean = series.dropna()

        if len(series_clean) == 0:
            return 'unknown'

        # Check pandas dtype
        dtype = series.dtype

        # Numeric types
        if pd.api.types.is_numeric_dtype(dtype):
            return 'numeric'

        # Datetime types
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return 'datetime'

        # Boolean types
        if pd.api.types.is_bool_dtype(dtype):
            return 'boolean'

        # Object types - need further analysis
        if dtype == 'object':
            # Try to infer datetime
            try:
                pd.to_datetime(series_clean.head(100))
                return 'datetime'
            except:
                pass

            # Check if categorical (low cardinality)
            unique_ratio = series_clean.nunique() / len(series_clean)
            if unique_ratio < 0.05 or series_clean.nunique() < 50:
                return 'categorical'
            else:
                return 'text'

        return 'unknown'

    @staticmethod
    def _detect_semantic_type(col_name: str, series: pd.Series, data_type: str) -> str:
        """
        Detect semantic meaning of column.

        Args:
            col_name: Column name
            series: Column data
            data_type: Already detected data type

        Returns:
            Semantic type string
        """
        col_lower = col_name.lower()

        # Revenue detection
        if any(keyword in col_lower for keyword in TypeInferencer.REVENUE_KEYWORDS):
            return 'revenue'

        # Quantity detection
        if any(keyword in col_lower for keyword in TypeInferencer.QUANTITY_KEYWORDS):
            return 'quantity'

        # Location detection
        if any(keyword in col_lower for keyword in TypeInferencer.LOCATION_KEYWORDS):
            return 'location'

        # Date detection
        if any(keyword in col_lower for keyword in TypeInferencer.DATE_KEYWORDS):
            return 'date'

        # ID detection
        if any(keyword in col_lower for keyword in TypeInferencer.ID_KEYWORDS):
            return 'identifier'

        # Name detection
        if any(keyword in col_lower for keyword in TypeInferencer.NAME_KEYWORDS):
            return 'name'

        # Category detection
        if any(keyword in col_lower for keyword in TypeInferencer.CATEGORY_KEYWORDS):
            return 'category'

        # Price detection (specific for numeric)
        if data_type == 'numeric' and ('price' in col_lower or 'cost' in col_lower):
            return 'price'

        return 'unknown'

    @staticmethod
    def _calculate_column_stats(series: pd.Series, data_type: str) -> Dict[str, Any]:
        """
        Calculate column statistics.

        Args:
            series: Pandas series
            data_type: Column data type

        Returns:
            Dictionary with statistics
        """
        stats = {
            'null_count': int(series.isnull().sum()),
            'unique_count': int(series.nunique()),
            'sample_values': []
        }

        # Get sample values (non-null)
        sample = series.dropna().head(5).tolist()
        stats['sample_values'] = [str(v) for v in sample]

        return stats

    # ========================================================================
    # HELPER METHODS FOR AGENTS
    # ========================================================================

    @staticmethod
    def get_numeric_columns(schema: Dict) -> List[str]:
        """Get list of numeric column names."""
        return [col['name'] for col in schema['columns'] 
                if col['data_type'] in ['numeric', 'integer', 'float']]

    @staticmethod
    def get_categorical_columns(schema: Dict) -> List[str]:
        """Get list of categorical column names."""
        return [col['name'] for col in schema['columns'] 
                if col['data_type'] == 'categorical']

    @staticmethod
    def get_datetime_columns(schema: Dict) -> List[str]:
        """Get list of datetime column names."""
        return [col['name'] for col in schema['columns'] 
                if col['data_type'] == 'datetime']

    @staticmethod
    def get_date_columns(schema: Dict) -> List[str]:
        """Alias for get_datetime_columns."""
        return TypeInferencer.get_datetime_columns(schema)

    @staticmethod
    def get_columns_by_semantic(schema: Dict, semantic_type: str) -> List[str]:
        """
        Get columns matching semantic type.

        Args:
            schema: Dataset schema
            semantic_type: Semantic type to match (revenue, location, etc.)

        Returns:
            List of matching column names
        """
        return [col['name'] for col in schema['columns'] 
                if col['semantic_type'] == semantic_type]

    @staticmethod
    def get_column_info(schema: Dict, column_name: str) -> Optional[Dict]:
        """
        Get information about specific column.

        Args:
            schema: Dataset schema
            column_name: Column name

        Returns:
            Column schema dict or None if not found
        """
        for col in schema['columns']:
            if col['name'] == column_name:
                return col
        return None

    @staticmethod
    def is_numeric_column(schema: Dict, column_name: str) -> bool:
        """Check if column is numeric."""
        col_info = TypeInferencer.get_column_info(schema, column_name)
        return col_info and col_info['data_type'] == 'numeric' if col_info else False

    @staticmethod
    def is_categorical_column(schema: Dict, column_name: str) -> bool:
        """Check if column is categorical."""
        col_info = TypeInferencer.get_column_info(schema, column_name)
        return col_info and col_info['data_type'] == 'categorical' if col_info else False

    @staticmethod
    def get_high_cardinality_columns(schema: Dict, threshold: int = 100) -> List[str]:
        """Get columns with high cardinality (many unique values)."""
        return [col['name'] for col in schema['columns'] 
                if col['unique_count'] > threshold]

    @staticmethod
    def get_low_cardinality_columns(schema: Dict, threshold: int = 20) -> List[str]:
        """Get columns with low cardinality (few unique values)."""
        return [col['name'] for col in schema['columns'] 
                if col['unique_count'] <= threshold and col['unique_count'] > 1]

    @staticmethod
    def recommend_chart_columns(schema: Dict) -> Dict[str, List[str]]:
        """
        Recommend good column combinations for charts.

        Returns:
            Dictionary with recommendations for different chart types
        """
        recommendations = {
            'time_series': [],  # datetime x numeric
            'categorical_comparison': [],  # categorical x numeric
            'distributions': [],  # numeric only
            'correlations': []  # numeric x numeric
        }

        datetime_cols = TypeInferencer.get_datetime_columns(schema)
        numeric_cols = TypeInferencer.get_numeric_columns(schema)
        categorical_cols = TypeInferencer.get_categorical_columns(schema)

        # Time series recommendations
        if datetime_cols and numeric_cols:
            for date_col in datetime_cols[:2]:
                for num_col in numeric_cols[:3]:
                    recommendations['time_series'].append([date_col, num_col])

        # Categorical comparisons
        if categorical_cols and numeric_cols:
            for cat_col in categorical_cols[:3]:
                for num_col in numeric_cols[:3]:
                    recommendations['categorical_comparison'].append([cat_col, num_col])

        # Distributions
        recommendations['distributions'] = numeric_cols[:5]

        # Correlations
        if len(numeric_cols) >= 2:
            for i in range(min(3, len(numeric_cols))):
                for j in range(i + 1, min(3, len(numeric_cols))):
                    recommendations['correlations'].append([numeric_cols[i], numeric_cols[j]])

        return recommendations
