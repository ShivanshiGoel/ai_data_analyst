"""Formatting Agent - Conditional formatting logic."""
from crewai import Agent
from typing import Dict, List


class FormattingAgent:
    """Agent responsible for applying visual formatting to data."""

    def __init__(self, llm=None):
        """Initialize Formatting Agent with optional LLM."""
        self.agent = Agent(
            role='UI/UX Formatting Specialist',
            goal='Apply visual formatting to enhance data readability and highlight key insights',
            backstory="""You are an expert in conditional formatting and visual design 
            with a keen eye for making data scannable and actionable. You understand 
            color theory, accessibility, and best practices for data presentation.
            Your formatting makes key insights jump off the page.""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )

    def create_formatting_plan(self, user_intent: str, schema: List[Dict],
                              target_columns: List[str] = None) -> Dict:
        """
        Create formatting plan based on user intent and data schema.

        Args:
            user_intent: Natural language formatting request
            schema: Column schema information
            target_columns: Specific columns to format

        Returns:
            FormattingPlan dictionary with rules
        """
        rules = []
        intent_lower = user_intent.lower()

        # Determine target columns if not specified
        if not target_columns:
            numeric_cols = [col['name'] for col in schema 
                           if col.get('data_type') in ['numeric', 'integer', 'float']]
            target_columns = numeric_cols[:3]  # Default to first 3 numeric columns

        # Parse intent for formatting keywords
        if 'highlight' in intent_lower:
            # Highlight maximum values
            if any(word in intent_lower for word in ['max', 'highest', 'top', 'maximum']):
                rules.append({
                    'rule_type': 'highlight_max',
                    'target_columns': target_columns,
                    'color': 'green',
                    'description': 'Highlight maximum values in green'
                })

            # Highlight minimum values
            if any(word in intent_lower for word in ['min', 'lowest', 'bottom', 'minimum']):
                rules.append({
                    'rule_type': 'highlight_min',
                    'target_columns': target_columns,
                    'color': 'red',
                    'description': 'Highlight minimum values in red'
                })

        # Color scale formatting
        if any(word in intent_lower for word in ['scale', 'gradient', 'color']):
            rules.append({
                'rule_type': 'color_scale',
                'target_columns': target_columns,
                'colors': ['#ff4444', '#ffaa00', '#44ff44'],  # Red -> Yellow -> Green
                'description': 'Apply color gradient based on values'
            })

        # Threshold-based formatting
        if 'threshold' in intent_lower or 'above' in intent_lower or 'below' in intent_lower:
            # Extract threshold value if possible (simplified - can be enhanced)
            rules.append({
                'rule_type': 'threshold',
                'target_columns': target_columns,
                'threshold': 'mean',  # Can be 'mean', 'median', or numeric value
                'above_color': 'green',
                'below_color': 'red',
                'description': 'Color values above/below threshold'
            })

        # Default formatting if no specific intent detected
        if not rules:
            rules.append({
                'rule_type': 'highlight_extremes',
                'target_columns': target_columns,
                'max_color': 'green',
                'min_color': 'red',
                'description': 'Highlight both maximum and minimum values'
            })

        return {
            'rules': rules,
            'applies_to': 'table',
            'success': True
        }

    def apply_formatting_to_dataframe(self, df, formatting_plan: Dict):
        """
        Apply formatting rules to pandas DataFrame for display.
        Note: Returns styling functions for Streamlit dataframe.style

        Args:
            df: DataFrame to format
            formatting_plan: Formatting plan with rules

        Returns:
            Styled DataFrame or styling functions
        """
        # This would integrate with Streamlit's dataframe.style
        # For now, return the formatting plan for app.py to apply
        return formatting_plan
