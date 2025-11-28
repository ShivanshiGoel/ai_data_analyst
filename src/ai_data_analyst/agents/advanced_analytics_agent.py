"""Advanced Analytics Agent - Machine Learning & Predictive Analytics."""
from crewai import Agent, Task
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class AdvancedAnalyticsAgent:
    """
    Agent for advanced analytics beyond basic KPIs:
    - Forecasting (time series prediction)
    - Clustering (customer segmentation)
    - Anomaly detection
    - Correlation analysis
    - Regression modeling
    - Cohort analysis
    - RFM analysis (for customer data)
    """
    
    def __init__(self, llm):
        if not llm:
            raise ValueError("LLM required for AdvancedAnalyticsAgent")
        
        self.agent = Agent(
            role='Senior Data Scientist & ML Engineer',
            goal='''Perform advanced analytics including forecasting, clustering, anomaly detection,
            and predictive modeling. Automatically select appropriate ML techniques based on data characteristics.''',
            backstory="""You are a PhD-level data scientist with expertise in machine learning,
            statistics, and predictive analytics. You have deployed ML models in production at
            Fortune 500 companies. You understand when to use different algorithms and can
            explain complex analyses in business terms. You are fluent in scikit-learn, statsmodels,
            and time series analysis.""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
    
    def analyze_with_llm(self, df: pd.DataFrame, schema: Dict,
                        user_request: str) -> Dict[str, Any]:
        """
        Use LLM to determine which advanced analytics to perform.
        
        Args:
            df: DataFrame to analyze
            schema: Dataset schema
            user_request: Natural language request
        
        Returns:
            Dict with analysis results
        """
        # Get data summary for LLM
        data_summary = self._create_data_summary(df, schema)
        
        task_description = f"""
Analyze this request and determine appropriate advanced analytics:

USER REQUEST: "{user_request}"

DATA SUMMARY:
{data_summary}

AVAILABLE ANALYSES:
1. Forecasting - Predict future values (requires time series data)
2. Clustering - Group similar records (customer segmentation, pattern discovery)
3. Anomaly Detection - Find outliers and unusual patterns
4. Correlation Analysis - Identify relationships between variables
5. Regression Analysis - Predict one variable from others
6. Cohort Analysis - Track groups over time
7. RFM Analysis - Customer value segmentation (Recency, Frequency, Monetary)
8. Trend Analysis - Identify growth patterns and seasonality
9. Statistical Testing - Compare groups (t-test, ANOVA)

Determine which analysis to perform and why. Consider:
- Does the data have time elements? (enables forecasting, trend analysis)
- Are there natural groupings? (enables clustering, cohort analysis)
- Are there numeric relationships to explore? (enables correlation, regression)
- Does the request mention customers? (enables RFM analysis)

Return the analysis type and parameters to use.
"""
        
        task = Task(
            description=task_description,
            agent=self.agent,
            expected_output="""JSON with:
            - analysis_type: name of analysis to perform
            - target_columns: columns to use
            - parameters: specific parameters for the analysis
            - rationale: why this analysis is appropriate"""
        )
        
        llm_response = self.agent.execute_task(task)
        
        # Parse LLM response and execute analysis
        analysis_plan = self._parse_analysis_plan(llm_response)
        results = self._execute_analysis(df, schema, analysis_plan)
        
        return results
    
    def _create_data_summary(self, df: pd.DataFrame, schema: Dict) -> str:
        """Create concise data summary for LLM."""
        summary = f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n\n"
        
        # Column types summary
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        summary += f"Numeric columns ({len(numeric_cols)}): {', '.join(numeric_cols[:5])}\n"
        summary += f"Date columns ({len(date_cols)}): {', '.join(date_cols)}\n"
        summary += f"Categorical columns ({len(categorical_cols)}): {', '.join(categorical_cols[:5])}\n\n"
        
        # Sample statistics
        if numeric_cols:
            summary += "Numeric statistics:\n"
            for col in numeric_cols[:3]:
                summary += f"  {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, mean={df[col].mean():.2f}\n"
        
        return summary
    
    def _parse_analysis_plan(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response into analysis plan."""
        import json
        
        try:
            # Extract JSON from response
            if '```json' in llm_response:
                json_start = llm_response.find('```json') + 7
                json_end = llm_response.find('```', json_start)
                json_str = llm_response[json_start:json_end].strip()
            elif '{' in llm_response:
                json_start = llm_response.find('{')
                json_end = llm_response.rfind('}') + 1
                json_str = llm_response[json_start:json_end]
            else:
                # Default plan
                return {
                    'analysis_type': 'correlation',
                    'target_columns': [],
                    'parameters': {}
                }
            
            plan = json.loads(json_str)
            return plan
        
        except:
            return {
                'analysis_type': 'correlation',
                'target_columns': [],
                'parameters': {}
            }
    
    def _execute_analysis(self, df: pd.DataFrame, schema: Dict,
                         plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the planned analysis."""
        analysis_type = plan.get('analysis_type', '').lower()
        
        if 'forecast' in analysis_type or 'predict' in analysis_type:
            return self.perform_forecasting(df, plan)
        
        elif 'cluster' in analysis_type or 'segment' in analysis_type:
            return self.perform_clustering(df, plan)
        
        elif 'anomaly' in analysis_type or 'outlier' in analysis_type:
            return self.detect_anomalies(df, plan)
        
        elif 'correlation' in analysis_type:
            return self.analyze_correlations(df, plan)
        
        elif 'regression' in analysis_type:
            return self.perform_regression(df, plan)
        
        elif 'cohort' in analysis_type:
            return self.cohort_analysis(df, plan)
        
        elif 'rfm' in analysis_type:
            return self.rfm_analysis(df, plan)
        
        else:
            return self.analyze_correlations(df, plan)
    
    # ========================================================================
    # FORECASTING
    # ========================================================================
    
    def perform_forecasting(self, df: pd.DataFrame, plan: Dict) -> Dict[str, Any]:
        """
        Time series forecasting using linear regression.
        For production: use Prophet, ARIMA, or LSTM.
        """
        target_cols = plan.get('target_columns', [])
        periods_ahead = plan.get('parameters', {}).get('periods', 30)
        
        # Find date column
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        if not date_cols and target_cols:
            date_cols = [col for col in df.columns if 'date' in col.lower()]
        
        if not date_cols or not target_cols:
            return {'error': 'Need date column and target column for forecasting'}
        
        date_col = date_cols[0]
        value_col = target_cols[0] if target_cols else df.select_dtypes(include=[np.number]).columns[0]
        
        # Prepare data
        df_sorted = df.sort_values(date_col).copy()
        df_sorted['days_from_start'] = (df_sorted[date_col] - df_sorted[date_col].min()).dt.days
        
        X = df_sorted[['days_from_start']].values
        y = df_sorted[value_col].values
        
        # Train model
        model = LinearRegression()
        model.fit(X, y)
        
        # Make predictions
        last_day = X[-1][0]
        future_days = np.array([[last_day + i] for i in range(1, periods_ahead + 1)])
        predictions = model.predict(future_days)
        
        # Create forecast dataframe
        last_date = df_sorted[date_col].max()
        future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, periods_ahead + 1)]
        
        forecast_df = pd.DataFrame({
            date_col: future_dates,
            f'Forecasted_{value_col}': predictions
        })
        
        return {
            'type': 'forecast',
            'forecast': forecast_df,
            'model_score': model.score(X, y),
            'summary': f'Forecasted {value_col} for next {periods_ahead} periods. R² = {model.score(X, y):.3f}'
        }
    
    # ========================================================================
    # CLUSTERING
    # ========================================================================
    
    def perform_clustering(self, df: pd.DataFrame, plan: Dict) -> Dict[str, Any]:
        """
        K-means clustering for segmentation.
        """
        n_clusters = plan.get('parameters', {}).get('n_clusters', 3)
        target_cols = plan.get('target_columns', [])
        
        # Get numeric columns for clustering
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if target_cols:
            numeric_cols = [col for col in numeric_cols if col in target_cols]
        
        if len(numeric_cols) < 2:
            return {'error': 'Need at least 2 numeric columns for clustering'}
        
        # Prepare data
        X = df[numeric_cols].fillna(0)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Add cluster labels to dataframe
        result_df = df.copy()
        result_df['Cluster'] = clusters
        result_df['Cluster_Label'] = result_df['Cluster'].map(
            {i: f'Segment {i+1}' for i in range(n_clusters)}
        )
        
        # Calculate cluster statistics
        cluster_stats = result_df.groupby('Cluster')[numeric_cols].mean()
        
        return {
            'type': 'clustering',
            'data': result_df,
            'cluster_centers': cluster_stats,
            'n_clusters': n_clusters,
            'summary': f'Identified {n_clusters} distinct segments in the data'
        }
    
    # ========================================================================
    # ANOMALY DETECTION
    # ========================================================================
    
    def detect_anomalies(self, df: pd.DataFrame, plan: Dict) -> Dict[str, Any]:
        """
        Detect anomalies using Isolation Forest.
        """
        target_cols = plan.get('target_columns', [])
        contamination = plan.get('parameters', {}).get('contamination', 0.1)
        
        # Get numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if target_cols:
            numeric_cols = [col for col in numeric_cols if col in target_cols]
        
        if not numeric_cols:
            return {'error': 'Need numeric columns for anomaly detection'}
        
        # Prepare data
        X = df[numeric_cols].fillna(0)
        
        # Detect anomalies
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        predictions = iso_forest.fit_predict(X)
        
        # Add anomaly labels
        result_df = df.copy()
        result_df['Is_Anomaly'] = predictions == -1
        result_df['Anomaly_Score'] = iso_forest.score_samples(X)
        
        anomalies = result_df[result_df['Is_Anomaly']]
        
        return {
            'type': 'anomaly_detection',
            'data': result_df,
            'anomalies': anomalies,
            'n_anomalies': len(anomalies),
            'summary': f'Detected {len(anomalies)} anomalous records ({len(anomalies)/len(df)*100:.1f}% of data)'
        }
    
    # ========================================================================
    # CORRELATION ANALYSIS
    # ========================================================================
    
    def analyze_correlations(self, df: pd.DataFrame, plan: Dict) -> Dict[str, Any]:
        """
        Analyze correlations between numeric variables.
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            return {'error': 'Need at least 2 numeric columns for correlation'}
        
        # Calculate correlation matrix
        corr_matrix = df[numeric_cols].corr()
        
        # Find strong correlations
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.5:  # Strong correlation threshold
                    strong_correlations.append({
                        'var1': corr_matrix.columns[i],
                        'var2': corr_matrix.columns[j],
                        'correlation': corr_value,
                        'strength': 'Strong' if abs(corr_value) > 0.7 else 'Moderate'
                    })
        
        return {
            'type': 'correlation',
            'correlation_matrix': corr_matrix,
            'strong_correlations': strong_correlations,
            'summary': f'Found {len(strong_correlations)} strong correlations among {len(numeric_cols)} variables'
        }
    
    # ========================================================================
    # REGRESSION ANALYSIS
    # ========================================================================
    
    def perform_regression(self, df: pd.DataFrame, plan: Dict) -> Dict[str, Any]:
        """
        Linear regression to predict target variable.
        """
        target_cols = plan.get('target_columns', [])
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not target_cols or len(numeric_cols) < 2:
            return {'error': 'Need target variable and predictor variables'}
        
        target = target_cols[0]
        predictors = [col for col in numeric_cols if col != target][:5]  # Limit to 5 predictors
        
        # Prepare data
        X = df[predictors].fillna(0)
        y = df[target].fillna(0)
        
        # Train model
        model = LinearRegression()
        model.fit(X, y)
        
        # Get predictions
        predictions = model.predict(X)
        
        # Calculate metrics
        r_squared = model.score(X, y)
        
        # Create results dataframe
        result_df = df.copy()
        result_df[f'Predicted_{target}'] = predictions
        result_df['Residual'] = y - predictions
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'Feature': predictors,
            'Coefficient': model.coef_
        }).sort_values('Coefficient', key=abs, ascending=False)
        
        return {
            'type': 'regression',
            'data': result_df,
            'r_squared': r_squared,
            'feature_importance': feature_importance,
            'summary': f'Regression model predicting {target} with R² = {r_squared:.3f}'
        }
    
    # ========================================================================
    # COHORT ANALYSIS
    # ========================================================================
    
    def cohort_analysis(self, df: pd.DataFrame, plan: Dict) -> Dict[str, Any]:
        """
        Cohort analysis - track groups over time.
        """
        date_col = plan.get('parameters', {}).get('date_column')
        customer_col = plan.get('parameters', {}).get('customer_column')
        value_col = plan.get('parameters', {}).get('value_column')
        
        # Auto-detect if not provided
        if not date_col:
            date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            date_col = date_cols[0] if date_cols else None
        
        if not customer_col:
            customer_col = [col for col in df.columns if 'customer' in col.lower() or 'user' in col.lower()]
            customer_col = customer_col[0] if customer_col else df.columns[0]
        
        if not value_col:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            value_col = numeric_cols[0] if numeric_cols else None
        
        if not all([date_col, customer_col, value_col]):
            return {'error': 'Need date, customer, and value columns for cohort analysis'}
        
        # Create cohort
        df_cohort = df.copy()
        df_cohort['CohortMonth'] = df_cohort[date_col].dt.to_period('M')
        
        # Get first transaction month for each customer
        df_cohort['CohortGroup'] = df_cohort.groupby(customer_col)[date_col].transform('min').dt.to_period('M')
        
        # Calculate months since first transaction
        df_cohort['CohortIndex'] = (df_cohort['CohortMonth'] - df_cohort['CohortGroup']).apply(attrgetter('n'))
        
        # Create cohort table
        cohort_table = df_cohort.groupby(['CohortGroup', 'CohortIndex'])[customer_col].nunique().reset_index()
        cohort_pivot = cohort_table.pivot(index='CohortGroup', columns='CohortIndex', values=customer_col)
        
        return {
            'type': 'cohort',
            'cohort_table': cohort_pivot,
            'summary': f'Cohort analysis tracking {df[customer_col].nunique()} customers over time'
        }
    
    # ========================================================================
    # RFM ANALYSIS
    # ========================================================================
    
    def rfm_analysis(self, df: pd.DataFrame, plan: Dict) -> Dict[str, Any]:
        """
        RFM (Recency, Frequency, Monetary) analysis for customer segmentation.
        """
        customer_col = plan.get('parameters', {}).get('customer_column')
        date_col = plan.get('parameters', {}).get('date_column')
        value_col = plan.get('parameters', {}).get('value_column')
        
        # Auto-detect columns
        if not customer_col:
            customer_candidates = [col for col in df.columns if 'customer' in col.lower() or 'user' in col.lower() or 'id' in col.lower()]
            customer_col = customer_candidates[0] if customer_candidates else df.columns[0]
        
        if not date_col:
            date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            date_col = date_cols[0] if date_cols else None
        
        if not value_col:
            value_candidates = [col for col in df.columns if 'amount' in col.lower() or 'revenue' in col.lower() or 'sales' in col.lower()]
            if not value_candidates:
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                value_candidates = numeric_cols
            value_col = value_candidates[0] if value_candidates else None
        
        if not all([customer_col, date_col, value_col]):
            return {'error': 'Need customer, date, and value columns for RFM analysis'}
        
        # Calculate RFM metrics
        reference_date = df[date_col].max()
        
        rfm = df.groupby(customer_col).agg({
            date_col: lambda x: (reference_date - x.max()).days,  # Recency
            customer_col: 'count',  # Frequency
            value_col: 'sum'  # Monetary
        }).reset_index()
        
        rfm.columns = [customer_col, 'Recency', 'Frequency', 'Monetary']
        
        # Create RFM scores (1-5)
        rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5,4,3,2,1], duplicates='drop')
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5], duplicates='drop')
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1,2,3,4,5], duplicates='drop')
        
        rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
        
        # Segment customers
        def segment_customer(row):
            if row['R_Score'] >= 4 and row['F_Score'] >= 4 and row['M_Score'] >= 4:
                return 'Champions'
            elif row['R_Score'] >= 3 and row['F_Score'] >= 3:
                return 'Loyal Customers'
            elif row['R_Score'] >= 4:
                return 'Potential Loyalists'
            elif row['M_Score'] >= 4:
                return 'Big Spenders'
            elif row['R_Score'] <= 2:
                return 'At Risk'
            else:
                return 'Needs Attention'
        
        rfm['Segment'] = rfm.apply(segment_customer, axis=1)
        
        # Segment summary
        segment_summary = rfm.groupby('Segment').agg({
            customer_col: 'count',
            'Monetary': 'sum'
        }).reset_index()
        
        return {
            'type': 'rfm',
            'rfm_data': rfm,
            'segment_summary': segment_summary,
            'summary': f'RFM analysis identified {rfm["Segment"].nunique()} customer segments'
        }


from operator import attrgetter
