"""
Main Streamlit Application for AI Data Analyst System
Enterprise-grade, production-ready implementation with NLP
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Try to import from ai_data_analyst package with better error handling
try:
    from ai_data_analyst.models.state import app_state
    from ai_data_analyst.models.schemas import Operation, OperationType, KPI
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please make sure all __init__.py files use relative imports (with dots)")
    st.stop()

try:
    from ai_data_analyst.tools.chart_tools import ChartTools
except ImportError:
    # Fallback chart tools
    class ChartTools:
        @staticmethod
        def create_dashboard_charts(df, schema, max_charts=4):
            return []

try:
    from ai_data_analyst.utils.type_inference import TypeInferencer
except ImportError:
    # Fallback type inference
    class TypeInferencer:
        @staticmethod
        def infer_schema(df):
            schema = {'columns': []}
            for col in df.columns:
                schema['columns'].append({
                    'name': col,
                    'data_type': 'numeric' if pd.api.types.is_numeric_dtype(df[col]) else 'categorical',
                    'unique_count': df[col].nunique()
                })
            return schema

# Import Excel NLP Processor
try:
    from ai_data_analyst.utils.excel_nlp_processor import ExcelNLPProcessor
except ImportError:
    # Fallback NLP processor
    class ExcelNLPProcessor:
        def __init__(self, df):
            self.df = df
        def process_request(self, request):
            return {'operation': 'unknown'}

# Import Excel Tools
try:
    from ai_data_analyst.tools.excel_tools import ExcelTools
except ImportError:
    # Fallback Excel tools
    import io
    class ExcelTools:
        @staticmethod
        def load_excel(file):
            # Intelligent header detection
            df_peek = pd.read_excel(file, nrows=3)
            unnamed_cols = [col for col in df_peek.columns if 'Unnamed' in str(col)]
            file.seek(0)

            if len(unnamed_cols) > len(df_peek.columns) * 0.3:
                df = pd.read_excel(file, header=1)
            else:
                df = pd.read_excel(file, header=0)

            df.columns = [col if 'Unnamed' not in str(col) else f'Column_{i}' 
                         for i, col in enumerate(df.columns)]

            return {'dataframe': df, 'active_sheet': 'Sheet1'}

        @staticmethod
        def export_to_excel(df, filename):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            output.seek(0)
            return output

        @staticmethod
        def filter_by_criteria(df, criteria):
            result = df.copy()
            for col, condition in criteria.items():
                if col not in result.columns:
                    continue
                if isinstance(condition, tuple):
                    op, val = condition
                    if op in ['highest', 'top']:
                        result = result.nlargest(val, col)
                    elif op in ['lowest', 'bottom']:
                        result = result.nsmallest(val, col)
            return result

        @staticmethod
        def create_summary_table(df, group_by, aggregate):
            return df.groupby(group_by).agg(aggregate).reset_index()

try:
    from ai_data_analyst.tools.pandas_tools import PandasTools
except ImportError:
    # Fallback pandas tools
    class PandasTools:
        @staticmethod
        def clean_missing_values(df, strategy='drop'):
            if strategy == 'drop':
                return df.dropna()
            return df

        @staticmethod
        def remove_duplicates(df):
            return df.drop_duplicates()

        @staticmethod
        def calculate_kpis(df, schema):
            kpis = []
            kpis.append({
                'name': 'Total Records',
                'value': len(df),
                'format': 'number',
                'icon': '📊',
                'change': None
            })

            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                col = numeric_cols[0]
                kpis.append({
                    'name': f'Total {col}',
                    'value': float(df[col].sum()),
                    'format': 'number',
                    'icon': '💰',
                    'change': None
                })

            return kpis

# Page configuration
st.set_page_config(
    page_title="AI Data Analyst Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.processing = False

def execute_nl_excel_command(prompt: str):
    """Execute natural language Excel command."""
    with st.spinner(f"⚡ Processing: {prompt}"):
        try:
            processor = ExcelNLPProcessor(app_state.current_df)
            operation = processor.process_request(prompt)

            if operation['operation'] == 'ranking':
                # Handle top N
                rank_type = operation['type']
                n = operation['n']
                col = operation['column']

                if rank_type in ['top', 'highest']:
                    result = app_state.current_df.nlargest(n, col)
                else:
                    result = app_state.current_df.nsmallest(n, col)

                app_state.update_dataframe(result, f"Filtered: Top {n} by {col}", "NLProcessor")
                st.success(f"✅ Showing {rank_type} {n} by {col}")
                st.rerun()

            elif operation['operation'] == 'conditional_formatting':
                # Apply formatting
                rules = operation['rules']
                output = ExcelTools.apply_conditional_formatting(
                    app_state.current_df, 
                    rules
                )
                st.download_button(
                    "📥 Download Formatted Excel",
                    output.getvalue(),
                    f"formatted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.success("✅ Formatting applied! Click download button above.")

            elif operation['operation'] == 'grouping':
                # Handle grouping
                result = ExcelTools.create_summary_table(
                    app_state.current_df,
                    operation['group_by'],
                    operation['aggregate']
                )
                app_state.update_dataframe(result, f"Grouped by {operation['group_by']}", "NLProcessor")
                st.success("✅ Grouped and aggregated")
                st.rerun()

            elif operation['operation'] == 'filtering':
                # Handle filtering
                result = ExcelTools.filter_by_criteria(
                    app_state.current_df,
                    operation['criteria']
                )
                app_state.update_dataframe(result, f"Filtered with criteria", "NLProcessor")
                st.success(f"✅ Filtered: {len(result)} rows")
                st.rerun()

            else:
                st.warning("❓ Command not recognized. Try:")
                st.info("""
                - "Show top 10 by Order Year"
                - "Highlight highest Order Priority in red"
                - "Group by City and count orders"
                - "Filter for Ghaziabad only"
                """)

        except Exception as e:
            st.error(f"Error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

def render_sidebar():
    """Render sidebar with controls."""
    with st.sidebar:
        st.title("📊 AI Data Analyst")
        st.markdown("---")

        # File upload
        st.subheader("📁 Data Upload")
        uploaded_file = st.file_uploader(
            "Upload Excel File", 
            type=['xlsx', 'xls'],
            help="Upload your Excel file to begin analysis"
        )

        if uploaded_file:
            if st.button("🔄 Load File", type="primary"):
                with st.spinner("Loading Excel file..."):
                    try:
                        result = ExcelTools.load_excel(uploaded_file)
                        df = result['dataframe']

                        # Load into state
                        app_state.load_dataframe(
                            df, 
                            uploaded_file.name, 
                            result['active_sheet']
                        )

                        # Infer schema
                        app_state.schema = TypeInferencer.infer_schema(df)

                        st.success(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error loading file: {str(e)}")

        st.markdown("---")

        # Natural Language Commands
        if app_state.current_df is not None:
            st.subheader("🤖 Advanced Excel Commands")

            nl_command = st.text_input(
                "Natural Language Command",
                placeholder="e.g., 'Top 10 by revenue'",
                label_visibility="collapsed"
            )

            if st.button("⚡ Execute Command", type="primary", use_container_width=True):
                if nl_command:
                    execute_nl_excel_command(nl_command)

            # Show examples
            with st.expander("💡 Command Examples"):
                st.markdown("""
                **Ranking:**
                - Top 5 by Order Priority
                - Highest Customer Type values

                **Formatting:**
                - Highlight maximum in red
                - Color minimum yellow

                **Grouping:**
                - Group by City and count
                - Sum by Customer Type

                **Filtering:**
                - Show all from Delhi
                - Filter University only
                """)

            st.markdown("---")

        # Quick Actions
        if app_state.current_df is not None:
            st.subheader("⚡ Quick Actions")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("🧹 Clean", use_container_width=True):
                    execute_cleaning()

            with col2:
                if st.button("📈 Analyze", use_container_width=True):
                    execute_analytics()

            if st.button("📊 Generate Dashboard", type="primary", use_container_width=True):
                execute_dashboard_generation()

            st.markdown("---")

            # Undo/Redo
            st.subheader("↩️ History")
            undo_col, redo_col = st.columns(2)

            with undo_col:
                if st.button("⬅️ Undo", disabled=not app_state.can_undo(), use_container_width=True):
                    if app_state.undo():
                        st.success("Undone")
                        st.rerun()

            with redo_col:
                if st.button("➡️ Redo", disabled=not app_state.can_redo(), use_container_width=True):
                    if app_state.redo():
                        st.success("Redone")
                        st.rerun()

            st.markdown("---")

            # Export
            st.subheader("💾 Export")
            if st.button("📥 Download Excel", use_container_width=True):
                output = ExcelTools.export_to_excel(
                    app_state.current_df,
                    f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                )
                st.download_button(
                    label="Download",
                    data=output.getvalue(),
                    file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

def execute_cleaning():
    """Execute data cleaning."""
    with st.spinner("🧹 Cleaning data..."):
        try:
            tools = PandasTools()
            df = app_state.current_df

            # Apply basic cleaning
            df_clean = tools.clean_missing_values(df, 'drop')
            df_clean = tools.remove_duplicates(df_clean)

            # Update state
            app_state.update_dataframe(
                df_clean, 
                "Applied data cleaning: removed nulls and duplicates",
                "CleaningAgent"
            )

            st.success(f"✅ Cleaned data: {len(df)} → {len(df_clean)} rows")
            st.rerun()

        except Exception as e:
            st.error(f"Cleaning failed: {str(e)}")

def execute_analytics():
    """Execute analytics and KPI generation."""
    with st.spinner("📈 Analyzing data..."):
        try:
            df = app_state.current_df
            schema = app_state.schema

            # Calculate KPIs
            tools = PandasTools()
            kpi_data = tools.calculate_kpis(df, schema)

            # Convert to KPI objects
            kpis = [kpi_data] if not isinstance(kpi_data, list) else kpi_data
            app_state.set_kpis(kpis)

            st.success(f"✅ Generated {len(kpis)} KPIs")
            st.rerun()

        except Exception as e:
            st.error(f"Analytics failed: {str(e)}")

def execute_dashboard_generation():
    """Generate complete dashboard."""
    with st.spinner("📊 Generating dashboard..."):
        try:
            df = app_state.current_df
            schema = app_state.schema

            # Generate charts
            charts = ChartTools.create_dashboard_charts(df, schema, max_charts=4)
            app_state.clear_charts()
            for chart in charts:
                app_state.add_chart(chart)

            # Generate KPIs
            tools = PandasTools()
            kpi_data = tools.calculate_kpis(df, schema)
            kpis = [kpi_data] if not isinstance(kpi_data, list) else kpi_data
            app_state.set_kpis(kpis)

            st.success(f"✅ Dashboard generated with {len(charts)} charts")
            st.rerun()

        except Exception as e:
            st.error(f"Dashboard generation failed: {str(e)}")

def render_main_content():
    """Render main content area."""
    if app_state.current_df is None:
        st.info("👈 Upload an Excel file to begin")
        st.markdown("""
        ### Welcome to AI Data Analyst Pro

        This enterprise-grade AI system can:
        - 🧹 **Clean** your data automatically
        - 📊 **Analyze** and generate KPIs
        - 📈 **Visualize** with intelligent charts
        - 🎨 **Format** with conditional styling
        - 📋 **Create** comprehensive dashboards
        - 🤖 **Natural Language** Excel commands

        **Get started** by uploading an Excel file in the sidebar.
        """)
        return

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Working View", "📊 Dashboard", "📜 Audit Log", "🔍 Schema"])

    with tab1:
        render_working_view()

    with tab2:
        render_dashboard_view()

    with tab3:
        render_audit_log()

    with tab4:
        render_schema_view()

def render_working_view():
    """Render main working table view."""
    st.subheader("📋 Working Data Sheet")

    # KPI Cards
    if app_state.kpis:
        st.markdown("### 📊 Key Performance Indicators")
        kpi_cols = st.columns(min(len(app_state.kpis), 4))
        for idx, kpi in enumerate(app_state.kpis[:4]):
            with kpi_cols[idx]:
                value = kpi.get('value') if isinstance(kpi, dict) else getattr(kpi, 'value', 0)
                name = kpi.get('name') if isinstance(kpi, dict) else getattr(kpi, 'name', 'KPI')
                st.metric(
                    label=name,
                    value=f"{value:,.0f}" if isinstance(value, (int, float)) else value
                )

    # Main data table
    st.markdown("### 📄 Data Table")
    st.dataframe(app_state.current_df, use_container_width=True, height=500)

    # Data info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", len(app_state.current_df))
    with col2:
        st.metric("Columns", len(app_state.current_df.columns))
    with col3:
        memory_mb = app_state.current_df.memory_usage(deep=True).sum() / 1024 / 1024
        st.metric("Memory", f"{memory_mb:.2f} MB")

def render_dashboard_view():
    """Render dashboard with charts."""
    st.subheader("📊 Analytics Dashboard")

    if not app_state.charts and not app_state.kpis:
        st.info("No dashboard generated yet. Click 'Generate Dashboard' in the sidebar.")
        return

    # KPIs at top
    if app_state.kpis:
        st.markdown("### Key Metrics")
        kpi_cols = st.columns(min(len(app_state.kpis), 5))
        for idx, kpi in enumerate(app_state.kpis):
            with kpi_cols[idx % 5]:
                value = kpi.get('value') if isinstance(kpi, dict) else getattr(kpi, 'value', 0)
                name = kpi.get('name') if isinstance(kpi, dict) else getattr(kpi, 'name', 'KPI')
                st.metric(name, f"{value:,.0f}" if isinstance(value, (int, float)) else value)

    # Charts
    if app_state.charts:
        st.markdown("### Visualizations")

        chart_cols = st.columns(2)
        for idx, chart_spec in enumerate(app_state.charts):
            with chart_cols[idx % 2]:
                try:
                    # Simple chart rendering
                    title = chart_spec.get('title', 'Chart') if isinstance(chart_spec, dict) else getattr(chart_spec, 'title', 'Chart')
                    chart_type = chart_spec.get('chart_type', 'N/A') if isinstance(chart_spec, dict) else getattr(chart_spec, 'chart_type', 'N/A')
                    st.write(f"**{title}**")
                    st.info(f"Chart type: {chart_type}")
                except Exception as e:
                    st.error(f"Error rendering chart: {str(e)}")

def render_audit_log():
    """Render operation audit log."""
    st.subheader("📜 Operation Audit Log")

    if not app_state.operation_log:
        st.info("No operations logged yet.")
        return

    # Display operations
    for op in reversed(app_state.operation_log[-20:]):
        success = op.get('success', True) if isinstance(op, dict) else getattr(op, 'success', True)
        agent = op.get('agent', 'System') if isinstance(op, dict) else getattr(op, 'agent_name', 'System')
        desc = op.get('description', 'N/A') if isinstance(op, dict) else getattr(op, 'description', 'N/A')

        with st.expander(f"{'✅' if success else '❌'} {agent}: {desc}", expanded=False):
            st.write("Operation logged")

def render_schema_view():
    """Render schema information."""
    st.subheader("🔍 Dataset Schema")

    if not app_state.schema:
        st.info("No schema available.")
        return

    schema_data = []
    columns = app_state.schema.get('columns', []) if isinstance(app_state.schema, dict) else getattr(app_state.schema, 'columns', [])

    for col in columns:
        if isinstance(col, dict):
            schema_data.append({
                'Column': col.get('name', 'N/A'),
                'Data Type': col.get('data_type', 'N/A'),
                'Unique Values': col.get('unique_count', 'N/A')
            })
        else:
            schema_data.append({
                'Column': getattr(col, 'name', 'N/A'),
                'Data Type': getattr(col, 'data_type', 'N/A'),
                'Unique Values': getattr(col, 'unique_count', 'N/A')
            })

    schema_df = pd.DataFrame(schema_data)
    st.dataframe(schema_df, use_container_width=True)

def main():
    """Main application entry point."""
    render_sidebar()
    render_main_content()

    # Footer
    st.markdown("---")
    st.caption("AI Data Analyst Pro v1.0 | Enterprise-Grade Data Analysis System with NLP")

if __name__ == "__main__":
    main()