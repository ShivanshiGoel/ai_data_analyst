"""
Enterprise Streamlit Application - AI Data Analyst with Gemini
Zero hardcoded patterns, full LLM-powered intelligence
"""
import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Enterprise AI Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import modules
try:
    from ai_data_analyst.utils.type_inference import TypeInferencer
    from ai_data_analyst.tools.excel_tools import ExcelTools
    from ai_data_analyst.models.state import app_state
    # Import CrewAI integration - ALL operations go through the crew
    from ai_data_analyst.crew_streamlit_integration import crew_integration
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()


def initialize_llm():
    """Initialize Gemini LLM."""
    # Force load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        st.error("❌ GEMINI_API_KEY not found in environment variables")
        st.info("Please add your Gemini API key to the .env file")
        st.stop()
    
    try:
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.1,
            google_api_key=api_key
        )
    except Exception as e:
        st.error(f"❌ Failed to initialize Gemini: {e}")
        st.stop()


def render_sidebar():
    """Render sidebar with file upload and controls."""
    with st.sidebar:
        st.title("📊 Enterprise AI Data Analyst")
        st.markdown("*Powered by Gemini AI*")
        st.markdown("---")
        
        # File upload
        st.subheader("📁 Data Upload")
        uploaded_file = st.file_uploader(
            "Upload Excel File",
            type=['xlsx', 'xls'],
            help="Upload your Excel file to begin analysis"
        )
        
        if uploaded_file:
            if st.button("🔄 Load File", type="primary", use_container_width=True):
                load_file(uploaded_file)
        
        st.markdown("---")
        
        # AI-Powered Commands
        if app_state.current_df is not None:
            st.subheader("🤖 AI Data Commands")
            st.markdown("*Natural language powered by Gemini*")
            
            command = st.text_area(
                "What would you like to do?",
                placeholder="e.g., Clean the data and show me sales trends by region",
                height=100,
                label_visibility="collapsed"
            )
            
            if st.button("⚡ Execute", type="primary", use_container_width=True):
                if command:
                    execute_ai_command(command)
            
            with st.expander("💡 Example Commands"):
                st.markdown("""
                **Data Cleaning:**
                - "Clean missing values and remove duplicates"
                - "Fix data quality issues in this dataset"
                
                **Analysis:**
                - "Show me top 10 customers by revenue"
                - "Calculate year-over-year growth"
                - "Perform cohort analysis"
                
                **Visualization:**
                - "Create a dashboard showing key metrics"
                - "Visualize sales trends over time"
                
                **Advanced:**
                - "Run ABC analysis on products"
                - "Show correlation between variables"
                """)
        
        st.markdown("---")
        
        # Quick actions
        if app_state.current_df is not None:
            st.subheader("⚡ Quick Actions")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🧹 Clean", use_container_width=True):
                    quick_clean_data()
            with col2:
                if st.button("📊 Analyze", use_container_width=True):
                    quick_analyze()
            
            if st.button("💾 Export", use_container_width=True):
                export_data()


def load_file(uploaded_file):
    """Load Excel file with intelligent cleaning."""
    with st.spinner("Loading and cleaning file..."):
        try:
            # Load with intelligent header detection
            result = ExcelTools.load_excel(uploaded_file)
            df = result['dataframe']
            
            # Show info about cleaning
            if result.get('header_row', 0) > 0:
                st.info(f"📍 Detected header in row {result['header_row'] + 1} (skipped {result['header_row']} empty rows)")
            
            # Additional cleaning for real-world data
            from ai_data_analyst.tools.data_cleaner import AdvancedDataCleaner
            clean_result = AdvancedDataCleaner.clean_dataset(df, aggressive=False)
            df_clean = clean_result['dataframe']
            report = clean_result['report']
            
            # Load into state
            app_state.load_dataframe(df_clean, uploaded_file.name, result.get('active_sheet', 'Sheet1'))
            
            # Infer schema
            app_state.schema = TypeInferencer.infer_schema(df_clean)
            
            # Show cleaning summary
            st.success(f"✅ Loaded {len(df_clean)} rows, {len(df_clean.columns)} columns")
            
            if report['operations']:
                with st.expander("🧹 Auto-Cleaning Applied"):
                    for op in report['operations']:
                        st.write(f"• {op}")
            
            st.rerun()
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            import traceback
            with st.expander("Error details"):
                st.code(traceback.format_exc())


def execute_ai_command(command: str):
    """Execute natural language command using CrewAI agents."""
    
    # Fix asyncio event loop issue with Streamlit
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    with st.spinner("🤖 CrewAI agents are analyzing your request..."):
        try:
            # Validate data is loaded
            if app_state.current_df is None:
                st.error("❌ No data loaded. Please upload a file first.")
                return
            
            if app_state.schema is None:
                st.error("❌ Schema not available. Please reload the file.")
                return
            
            # Import the crew (ALWAYS use simple version to avoid config issues)
            try:
                from ai_data_analyst.crew_simple import SimpleDataAnalystCrew as CrewClass
                st.info("✨ Using simplified crew (stable, no config dependencies)")
            except ImportError as e:
                st.error(f"❌ Failed to import simplified crew: {str(e)}")
                st.info("Make sure all dependencies are installed: pip install crewai langchain-google-genai")
                with st.expander("Error Details"):
                    import traceback
                    st.code(traceback.format_exc())
                return
            
            # Create schema dict for crew - handle both dict and object formats
            try:
                if isinstance(app_state.schema, dict):
                    columns = app_state.schema.get('columns', [])
                else:
                    columns = getattr(app_state.schema, 'columns', [])
                
                schema_dict = {
                    'columns': [
                        {
                            'name': col.get('name') if isinstance(col, dict) else getattr(col, 'name', 'Unknown'),
                            'data_type': col.get('data_type') if isinstance(col, dict) else (col.data_type.value if hasattr(col, 'data_type') and hasattr(col.data_type, 'value') else str(getattr(col, 'data_type', 'unknown'))),
                            'unique_count': col.get('unique_count', 0) if isinstance(col, dict) else getattr(col, 'unique_count', 0)
                        }
                        for col in columns
                    ]
                }
            except Exception as e:
                st.error(f"❌ Error processing schema: {str(e)}")
                import traceback
                with st.expander("Schema Error Details"):
                    st.code(traceback.format_exc())
                return
            
            # Initialize the crew
            try:
                st.info("🔧 Initializing CrewAI agents...")
                crew = CrewClass()
            except ValueError as e:
                st.error(f"❌ {str(e)}")
                st.info("💡 Make sure your .env file contains: GEMINI_API_KEY=your_key_here")
                with st.expander("How to get a Gemini API key"):
                    st.markdown("""
                    1. Go to: https://makersuite.google.com/app/apikey
                    2. Click "Create API Key"
                    3. Copy the key
                    4. Add to .env file: `GEMINI_API_KEY=your_key_here`
                    """)
                return
            except Exception as e:
                st.error(f"❌ Error initializing crew: {str(e)}")
                import traceback
                with st.expander("Initialization Error Details"):
                    st.code(traceback.format_exc())
                return
            
            # Show agent collaboration
            st.info("🤖 Multi-agent crew activated...")
            
            # Execute through CrewAI - agents will collaborate
            try:
                result = crew.analyze_data_request(
                    user_request=command,
                    df=app_state.current_df,
                    schema=schema_dict
                )
            except Exception as e:
                st.error(f"❌ Error during crew execution: {str(e)}")
                import traceback
                with st.expander("Execution Error Details"):
                    st.code(traceback.format_exc())
                return
            
            # Process crew results
            if result:
                st.success("✅ CrewAI agents completed the analysis!")
                
                # Show which agents participated
                with st.expander("🤖 Agent Collaboration Details"):
                    st.write("**Agents that worked on this request:**")
                    st.write("- 🧠 Planner Agent: Analyzed intent and created execution plan")
                    st.write("- 🧹 Cleaning Agent: Assessed data quality")
                    st.write("- 📊 Analytics Agent: Generated insights and KPIs")
                    st.write("- 📈 Visualization Agent: Designed visualizations")
                    st.write("- 🎨 Dashboard Agent: Composed final output")
                    
                    # Show the actual result if available
                    if isinstance(result, dict) and result.get('result'):
                        st.write("\n**Result:**")
                        st.write(result.get('result'))
                
                # Don't rerun automatically to avoid losing the output
                # st.rerun()
            else:
                st.warning("⚠️ Crew execution completed but no results returned")
            
        except Exception as e:
            st.error(f"❌ Unexpected error in CrewAI execution: {str(e)}")
            import traceback
            with st.expander("🔍 Full Error Details"):
                st.code(traceback.format_exc())
                
            st.info("💡 Common fixes:")
            st.markdown("""
            - Check that `.env` file exists with GEMINI_API_KEY
            - Run: `python check_env.py` to verify configuration
            - Ensure all dependencies are installed: `pip install -r requirements.txt`
            - Try reloading the page and uploading the file again
            """)


# Removed - now handled by CrewAI agents
# All operations go through the crew system


def quick_clean_data():
    """Quick clean current data - via CrewAI."""
    execute_ai_command("Clean this data by handling missing values and removing duplicates")


def quick_analyze():
    """Quick analyze current data - via CrewAI."""
    execute_ai_command("Analyze this data and show me key statistics and insights")


def export_data():
    """Export current dataframe."""
    if app_state.current_df is not None:
        output = ExcelTools.export_to_excel(app_state.current_df, "export.xlsx")
        st.download_button(
            label="💾 Download Excel",
            data=output,
            file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


def render_main_content():
    """Render main content area."""
    if app_state.current_df is None:
        render_welcome()
    else:
        render_data_view()


def render_welcome():
    """Render welcome screen."""
    st.title("🚀 Welcome to Enterprise AI Data Analyst")
    
    st.markdown("""
    ### Transform Your Data Analysis with AI
    
    This enterprise-grade system uses **CrewAI multi-agent orchestration** with 
    **Google Gemini AI** to understand your requests and perform sophisticated data analysis.
    
    #### 🤖 Multi-Agent Architecture:
    
    **5 Specialized AI Agents Work Together:**
    - 🧠 **Planner Agent** - Analyzes intent and creates execution plans
    - 🧹 **Cleaning Agent** - Handles data quality issues
    - 📊 **Analytics Agent** - Generates insights and KPIs
    - 📈 **Visualization Agent** - Creates charts and graphs
    - 🎨 **Dashboard Agent** - Composes executive dashboards
    
    #### Key Features:
    
    🤖 **True Multi-Agent System**
    - Agents collaborate via CrewAI framework
    - Each agent specializes in specific tasks
    - Automatic task routing and orchestration
    
    🧠 **AI-Powered Understanding**
    - No hardcoded keywords or patterns
    - Pure LLM-based intent analysis
    - Context-aware decision making
    
    📊 **Advanced Analytics**
    - KPI calculation
    - Time series & cohort analysis
    - ABC/Pareto analysis
    - Power BI-level operations
    
    #### Get Started:
    1. 👈 Upload an Excel file in the sidebar
    2. 💬 Describe what you want in natural language
    3. ⚡ Watch the agents collaborate!
    
    ---
    *Powered by CrewAI + Google Gemini 1.5 Pro*
    """)


def render_data_view():
    """Render data view with tabs."""
    tabs = st.tabs(["📋 Data", "📊 Analytics", "🔍 Schema", "📜 History"])
    
    with tabs[0]:
        render_data_tab()
    
    with tabs[1]:
        render_analytics_tab()
    
    with tabs[2]:
        render_schema_tab()
    
    with tabs[3]:
        render_history_tab()


def render_data_tab():
    """Render data table tab."""
    st.subheader("📋 Current Dataset")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rows", f"{len(app_state.current_df):,}")
    with col2:
        st.metric("Columns", len(app_state.current_df.columns))
    with col3:
        memory = app_state.current_df.memory_usage(deep=True).sum() / 1024 / 1024
        st.metric("Memory", f"{memory:.2f} MB")
    with col4:
        st.metric("Source", app_state.filename)
    
    # Data table
    st.dataframe(app_state.current_df, width='stretch', height=500)


def render_analytics_tab():
    """Render analytics tab."""
    st.subheader("📊 Analytics Dashboard")
    
    if app_state.kpis:
        st.markdown("### Key Performance Indicators")
        
        cols = st.columns(min(len(app_state.kpis), 5))
        for idx, kpi in enumerate(app_state.kpis):
            with cols[idx % 5]:
                value = kpi.get('value') if isinstance(kpi, dict) else getattr(kpi, 'value', 0)
                name = kpi.get('name') if isinstance(kpi, dict) else getattr(kpi, 'name', 'KPI')
                st.metric(name, f"{value:,.2f}" if isinstance(value, float) else f"{value:,}")
    else:
        st.info("No analytics generated yet. Use AI commands to analyze your data!")


def render_schema_tab():
    """Render schema tab."""
    st.subheader("🔍 Dataset Schema")
    
    if app_state.schema:
        schema_data = []
        
        # Handle both dict and object schema formats
        if isinstance(app_state.schema, dict):
            columns = app_state.schema.get('columns', [])
        else:
            columns = getattr(app_state.schema, 'columns', [])
        
        for col in columns:
            # Handle both dict and object column formats
            if isinstance(col, dict):
                col_name = col.get('name', 'Unknown')
                col_type = col.get('data_type', 'unknown')
                col_unique = col.get('unique_count', 0)
            else:
                col_name = getattr(col, 'name', 'Unknown')
                col_type = getattr(col, 'data_type', 'unknown')
                if hasattr(col_type, 'value'):
                    col_type = col_type.value
                col_unique = getattr(col, 'unique_count', 0)
            
            # Get sample value safely
            sample_val = ''
            if app_state.current_df is not None and len(app_state.current_df) > 0:
                if col_name in app_state.current_df.columns:
                    sample_val = str(app_state.current_df[col_name].iloc[0])
            
            schema_data.append({
                'Column': col_name,
                'Type': str(col_type),
                'Unique': col_unique,
                'Sample': sample_val
            })
        
        st.dataframe(pd.DataFrame(schema_data), width='stretch')


def render_history_tab():
    """Render operation history."""
    st.subheader("📜 Operation History")
    
    if app_state.operation_log:
        for op in reversed(app_state.operation_log[-20:]):
            agent = op.get('agent', 'System') if isinstance(op, dict) else getattr(op, 'agent_name', 'System')
            desc = op.get('description', 'N/A') if isinstance(op, dict) else getattr(op, 'description', 'N/A')
            
            with st.expander(f"✅ {agent}: {desc}"):
                st.json(op if isinstance(op, dict) else {'operation': str(op)})
    else:
        st.info("No operations logged yet.")


def main():
    """Main application entry point."""
    render_sidebar()
    render_main_content()
    
    # Footer
    st.markdown("---")
    st.caption("🚀 Enterprise AI Data Analyst v2.0 | Powered by Google Gemini")


if __name__ == "__main__":
    main()
