"""AI Data Analyst - Enterprise-grade data analysis system."""

__version__ = "2.0.0"
__author__ = "Enterprise AI Team"

# Make imports easier
from .crew_enterprise import EnterpriseDataAnalystCrew
from .models.schemas import (
    DatasetSchema,
    ColumnSchema,
    ExecutionPlan,
    CleaningPlan,
    KPI
)
from .utils.type_inference import TypeInferencer
from .utils.llm_intent_analyzer import LLMIntentAnalyzer

__all__ = [
    'EnterpriseDataAnalystCrew',
    'DatasetSchema',
    'ColumnSchema',
    'ExecutionPlan',
    'CleaningPlan',
    'KPI',
    'TypeInferencer',
    'LLMIntentAnalyzer'
]
