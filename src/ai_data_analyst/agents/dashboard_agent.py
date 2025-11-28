"""Dashboard Agent - Compose complete dashboards."""
from crewai import Agent
from typing import Dict, List
from datetime import datetime


class DashboardAgent:
    """Agent responsible for composing complete dashboard layouts."""

    def __init__(self, llm=None):
        """Initialize Dashboard Agent with optional LLM."""
        self.agent = Agent(
            role='Dashboard Architect',
            goal='Design comprehensive, executive-ready dashboards that tell complete data stories',
            backstory="""You are an expert in BI dashboard design with extensive 
            Power BI and Tableau experience. You understand information hierarchy, 
            visual flow, and how executives consume data. Your dashboards are 
            praised for being both comprehensive and easy to understand.""",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )

    def compose_dashboard(self, kpis: List[Dict], charts: List[Dict], 
                         title: str = "Business Intelligence Dashboard") -> Dict:
        """
        Compose complete dashboard from KPIs and charts.

        Args:
            kpis: List of KPI dictionaries
            charts: List of ChartSpec dictionaries
            title: Dashboard title

        Returns:
            DashboardSpec dictionary with complete layout
        """
        sections = []

        # Section 1: KPI Row (top of dashboard)
        for idx, kpi in enumerate(kpis[:6]):  # Limit to 6 KPIs
            sections.append({
                'section_id': f'kpi_{idx}',
                'title': kpi['name'],
                'content_type': 'kpi',
                'content': kpi,
                'layout_position': {
                    'row': 0,
                    'col': idx,
                    'width': 1,
                    'height': 1
                },
                'priority': 'high'  # KPIs are high priority
            })

        # Section 2+: Chart Grid (below KPIs)
        for idx, chart in enumerate(charts[:6]):  # Limit to 6 charts
            row = (idx // 2) + 1  # 2 charts per row, start from row 1
            col = idx % 2

            sections.append({
                'section_id': f'chart_{idx}',
                'title': chart['title'],
                'content_type': 'chart',
                'content': chart,
                'layout_position': {
                    'row': row,
                    'col': col,
                    'width': 1,
                    'height': 2
                },
                'priority': 'medium'
            })

        dashboard_spec = {
            'title': title,
            'description': f'Auto-generated dashboard with {len(kpis)} KPIs and {len(charts)} visualizations',
            'sections': sections,
            'layout': 'grid',
            'created_at': datetime.now().isoformat(),
            'metadata': {
                'kpi_count': len(kpis),
                'chart_count': len(charts),
                'total_sections': len(sections)
            }
        }

        return dashboard_spec

    def optimize_layout(self, dashboard_spec: Dict) -> Dict:
        """
        Optimize dashboard layout for readability and flow.

        Args:
            dashboard_spec: Dashboard specification

        Returns:
            Optimized dashboard specification
        """
        # Sort sections by priority
        sections = dashboard_spec['sections']

        # Ensure KPIs are at top
        kpi_sections = [s for s in sections if s['content_type'] == 'kpi']
        chart_sections = [s for s in sections if s['content_type'] == 'chart']

        # Recalculate positions
        for idx, section in enumerate(kpi_sections):
            section['layout_position']['row'] = 0
            section['layout_position']['col'] = idx

        for idx, section in enumerate(chart_sections):
            section['layout_position']['row'] = (idx // 2) + 1
            section['layout_position']['col'] = idx % 2

        dashboard_spec['sections'] = kpi_sections + chart_sections
        return dashboard_spec
