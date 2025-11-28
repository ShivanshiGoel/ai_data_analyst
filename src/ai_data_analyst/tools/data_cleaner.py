"""Advanced Data Cleaner - Handles Real-World Dirty Datasets."""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import re


class AdvancedDataCleaner:
    """
    Enterprise-grade data cleaner for real-world messy datasets.
    Handles:
    - Headers in wrong rows
    - Empty rows/columns
    - Inconsistent data types
    - Merged cells
    - Special characters
    - Duplicate columns
    - Mixed formatting
    """
    
    @staticmethod
    def clean_dataset(df: pd.DataFrame, aggressive: bool = False) -> Dict[str, Any]:
        """
        Comprehensive cleaning of dirty dataset.
        
        Args:
            df: Input dataframe
            aggressive: If True, applies more aggressive cleaning
        
        Returns:
            Dict with cleaned dataframe and cleaning report
        """
        cleaning_report = {
            'operations': [],
            'rows_removed': 0,
            'columns_removed': 0,
            'cells_fixed': 0
        }
        
        original_rows = len(df)
        original_cols = len(df.columns)
        
        # Step 1: Remove completely empty rows
        df_clean = df.dropna(how='all')
        rows_removed = original_rows - len(df_clean)
        if rows_removed > 0:
            cleaning_report['operations'].append(f"Removed {rows_removed} completely empty rows")
            cleaning_report['rows_removed'] += rows_removed
        
        # Step 2: Remove completely empty columns
        df_clean = df_clean.dropna(axis=1, how='all')
        cols_removed = original_cols - len(df_clean.columns)
        if cols_removed > 0:
            cleaning_report['operations'].append(f"Removed {cols_removed} completely empty columns")
            cleaning_report['columns_removed'] += cols_removed
        
        # Step 3: Fix column names
        df_clean.columns = [AdvancedDataCleaner._clean_column_name(col) for col in df_clean.columns]
        cleaning_report['operations'].append("Cleaned column names")
        
        # Step 4: Remove duplicate columns
        df_clean = AdvancedDataCleaner._fix_duplicate_columns(df_clean)
        
        # Step 5: Clean string data
        df_clean, cells_fixed = AdvancedDataCleaner._clean_string_columns(df_clean)
        cleaning_report['cells_fixed'] += cells_fixed
        if cells_fixed > 0:
            cleaning_report['operations'].append(f"Fixed {cells_fixed} cells with string issues")
        
        # Step 6: Fix data types
        df_clean = AdvancedDataCleaner._infer_and_fix_types(df_clean)
        cleaning_report['operations'].append("Inferred and fixed data types")
        
        # Step 7: Handle missing values intelligently
        if aggressive:
            df_clean, missing_fixed = AdvancedDataCleaner._handle_missing_values(df_clean)
            if missing_fixed > 0:
                cleaning_report['operations'].append(f"Handled {missing_fixed} missing values")
                cleaning_report['cells_fixed'] += missing_fixed
        
        # Step 8: Remove duplicate rows
        before_dup = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        dups_removed = before_dup - len(df_clean)
        if dups_removed > 0:
            cleaning_report['operations'].append(f"Removed {dups_removed} duplicate rows")
            cleaning_report['rows_removed'] += dups_removed
        
        # Step 9: Reset index
        df_clean = df_clean.reset_index(drop=True)
        
        cleaning_report['final_shape'] = df_clean.shape
        cleaning_report['success'] = True
        
        return {
            'dataframe': df_clean,
            'report': cleaning_report
        }
    
    @staticmethod
    def _clean_column_name(col_name: Any) -> str:
        """Clean a single column name."""
        # Convert to string
        col_str = str(col_name).strip()
        
        # Handle Unnamed columns
        if 'unnamed' in col_str.lower():
            match = re.search(r'\d+', col_str)
            num = match.group() if match else 'X'
            return f'Column_{num}'
        
        # Remove problematic characters
        col_str = col_str.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        # Replace multiple spaces
        col_str = re.sub(r'\s+', ' ', col_str)
        
        # Remove leading/trailing special chars
        col_str = re.sub(r'^[^\w]+|[^\w]+$', '', col_str)
        
        return col_str if col_str else 'Column'
    
    @staticmethod
    def _fix_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Fix duplicate column names by adding suffix."""
        cols = pd.Series(df.columns)
        
        duplicates = cols[cols.duplicated()].unique()
        
        for dup in duplicates:
            indices = cols[cols == dup].index.tolist()
            for i, idx in enumerate(indices):
                if i > 0:  # Keep first occurrence as is
                    cols.iloc[idx] = f'{dup}_{i}'
        
        df.columns = cols
        return df
    
    @staticmethod
    def _clean_string_columns(df: pd.DataFrame) -> tuple:
        """Clean string columns - remove extra whitespace, etc."""
        cells_fixed = 0
        df_clean = df.copy()
        
        for col in df_clean.columns:
            if df_clean[col].dtype == 'object':
                # Remove leading/trailing whitespace
                before = df_clean[col].isna().sum()
                df_clean[col] = df_clean[col].apply(
                    lambda x: x.strip() if isinstance(x, str) else x
                )
                after = df_clean[col].isna().sum()
                
                # Replace empty strings with NaN
                df_clean[col] = df_clean[col].replace('', np.nan)
                
                cells_fixed += (before - after)
        
        return df_clean, cells_fixed
    
    @staticmethod
    def _infer_and_fix_types(df: pd.DataFrame) -> pd.DataFrame:
        """Intelligently infer and fix data types."""
        df_clean = df.copy()
        
        for col in df_clean.columns:
            # Skip if already numeric
            if pd.api.types.is_numeric_dtype(df_clean[col]):
                continue
            
            # Try to convert to numeric
            try:
                # Remove common non-numeric characters
                if df_clean[col].dtype == 'object':
                    test_series = df_clean[col].astype(str).str.replace(',', '')
                    test_series = test_series.str.replace('$', '')
                    test_series = test_series.str.replace('%', '')
                    test_series = test_series.str.strip()
                    
                    # Try conversion
                    converted = pd.to_numeric(test_series, errors='coerce')
                    
                    # If most values converted successfully, use it
                    if converted.notna().sum() > len(converted) * 0.7:
                        df_clean[col] = converted
                        continue
            except:
                pass
            
            # Try to convert to datetime
            try:
                if df_clean[col].dtype == 'object':
                    # Suppress warnings for format inference
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        converted = pd.to_datetime(df_clean[col], errors='coerce')
                    
                    # If most values converted successfully, use it
                    if converted.notna().sum() > len(converted) * 0.7:
                        df_clean[col] = converted
                        continue
            except:
                pass
        
        return df_clean
    
    @staticmethod
    def _handle_missing_values(df: pd.DataFrame) -> tuple:
        """Intelligently handle missing values."""
        df_clean = df.copy()
        missing_fixed = 0
        
        for col in df_clean.columns:
            missing_count = df_clean[col].isna().sum()
            
            if missing_count == 0:
                continue
            
            # For numeric columns, fill with median
            if pd.api.types.is_numeric_dtype(df_clean[col]):
                median_val = df_clean[col].median()
                df_clean[col] = df_clean[col].fillna(median_val)
                missing_fixed += missing_count
            
            # For categorical columns with few categories, fill with mode
            elif df_clean[col].dtype == 'object':
                if df_clean[col].nunique() < 10:
                    mode_val = df_clean[col].mode()
                    if len(mode_val) > 0:
                        df_clean[col] = df_clean[col].fillna(mode_val[0])
                        missing_fixed += missing_count
        
        return df_clean, missing_fixed
    
    @staticmethod
    def detect_and_fix_headers(df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect if headers are in the wrong row and fix.
        
        Args:
            df: Input dataframe
        
        Returns:
            Dataframe with correct headers
        """
        # Check if first row looks more like a header than current columns
        if len(df) > 0:
            first_row = df.iloc[0]
            
            # Count string values in first row
            first_row_strings = sum(1 for val in first_row if isinstance(val, str))
            
            # Count string values in current column names
            col_strings = sum(1 for col in df.columns if isinstance(col, str) and not col.startswith('Unnamed'))
            
            # If first row has more strings and current columns don't look good, use first row as header
            if first_row_strings > len(first_row) * 0.7 and col_strings < len(df.columns) * 0.5:
                new_cols = first_row.tolist()
                df = df[1:].reset_index(drop=True)
                df.columns = new_cols
        
        return df
