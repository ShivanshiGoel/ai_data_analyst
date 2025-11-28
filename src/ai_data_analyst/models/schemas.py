"""Pydantic schemas for data validation and structured outputs."""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class DataType(str, Enum):
    """Column data types."""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    TEXT = "text"
    BOOLEAN = "boolean"
    UNKNOWN = "unknown"


class SemanticType(str, Enum):
    """Semantic meanings of columns."""
    REVENUE = "revenue"
    QUANTITY = "quantity"
    LOCATION = "location"
    DATE = "date"
    IDENTIFIER = "identifier"
    PRICE = "price"
    NAME = "name"
    DESCRIPTION = "description"
    CATEGORY = "category"
    UNKNOWN = "unknown"


class OperationType(str, Enum):
    """Types of operations performed."""
    LOAD = "LOAD"
    CLEAN = "CLEAN"
    TRANSFORM = "TRANSFORM"
    ANALYTICS = "ANALYTICS"
    VISUALIZATION = "VISUALIZATION"
    EXPORT = "EXPORT"
    UNDO = "UNDO"
    REDO = "REDO"


class ChartType(str, Enum):
    """Supported chart types."""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"
    BOX = "box"
    GROUPED_BAR = "grouped_bar"


# ============================================================================
# SCHEMA MODELS
# ============================================================================

class ColumnSchema(BaseModel):
    """Schema information for a single column."""
    name: str = Field(..., description="Column name")
    data_type: DataType = Field(..., description="Detected data type")
    semantic_type: SemanticType = Field(default=SemanticType.UNKNOWN, description="Semantic meaning")
    nullable: bool = Field(default=False, description="Can contain null values")
    unique_count: int = Field(default=0, description="Number of unique values")
    null_count: int = Field(default=0, description="Number of null values")
    sample_values: List[Any] = Field(default_factory=list, description="Sample values")

    class Config:
        use_enum_values = True


class DatasetSchema(BaseModel):
    """Complete dataset schema."""
    columns: List[ColumnSchema] = Field(..., description="Column schemas")
    row_count: int = Field(..., description="Number of rows")
    column_count: int = Field(..., description="Number of columns")
    created_at: datetime = Field(default_factory=datetime.now, description="When schema was created")

    class Config:
        arbitrary_types_allowed = True


# ============================================================================
# OPERATION TRACKING
# ============================================================================

class Operation(BaseModel):
    """Record of an operation performed."""
    operation_id: str = Field(..., description="Unique operation ID")
    operation_type: OperationType = Field(..., description="Type of operation")
    agent_name: str = Field(default="System", description="Agent that performed operation")
    timestamp: datetime = Field(default_factory=datetime.now, description="When operation occurred")
    description: str = Field(..., description="Human-readable description")
    success: bool = Field(default=True, description="Whether operation succeeded")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        use_enum_values = True


# ============================================================================
# AGENT COMMUNICATION
# ============================================================================

class ExecutionPlan(BaseModel):
    """Plan created by PlannerAgent."""
    user_intent: str = Field(..., description="Original user request")
    required_agents: List[str] = Field(..., description="Agents needed for execution")
    execution_order: List[str] = Field(..., description="Order to execute agents")
    target_columns: List[str] = Field(default_factory=list, description="Columns to focus on")
    rationale: str = Field(..., description="Why this plan was chosen")
    estimated_steps: int = Field(default=1, description="Estimated number of steps")


class CleaningAction(BaseModel):
    """Individual cleaning action."""
    action_type: str = Field(..., description="Type of cleaning action")
    target_columns: List[str] = Field(default_factory=list, description="Columns affected")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    rationale: str = Field(..., description="Why this action is needed")


class CleaningPlan(BaseModel):
    """Plan for data cleaning operations."""
    actions: List[CleaningAction] = Field(..., description="Cleaning actions to perform")
    estimated_impact: str = Field(..., description="Expected impact description")
    warnings: List[str] = Field(default_factory=list, description="Potential warnings")


# ============================================================================
# ANALYTICS MODELS
# ============================================================================

class KPI(BaseModel):
    """Key Performance Indicator."""
    name: str = Field(..., description="KPI name")
    value: float = Field(..., description="KPI value")
    format: str = Field(default="number", description="Display format (number, currency, percentage)")
    icon: str = Field(default="📊", description="Display icon")
    change: Optional[float] = Field(None, description="Change from previous period")
    description: Optional[str] = Field(None, description="KPI description")


class AnalyticsResult(BaseModel):
    """Result of analytics operations."""
    kpis: List[KPI] = Field(..., description="Calculated KPIs")
    insights: List[str] = Field(..., description="Generated insights")
    statistical_summary: Dict[str, Any] = Field(default_factory=dict, description="Statistical summary")
    recommendations: List[str] = Field(default_factory=list, description="Recommended actions")


# ============================================================================
# VISUALIZATION MODELS
# ============================================================================

class ChartSpec(BaseModel):
    """Specification for a chart."""
    chart_type: str = Field(..., description="Type of chart")
    title: str = Field(..., description="Chart title")
    x_column: str = Field(..., description="X-axis column")
    y_column: Optional[str] = Field(None, description="Y-axis column")
    color_by: Optional[str] = Field(None, description="Column to color by")
    aggregation: Optional[str] = Field(None, description="Aggregation method (sum, mean, count)")
    rationale: str = Field(..., description="Why this chart type was chosen")
    limit: Optional[int] = Field(None, description="Limit number of data points")
    bins: Optional[int] = Field(None, description="Number of bins for histograms")

    class Config:
        use_enum_values = True


# ============================================================================
# FORMATTING MODELS
# ============================================================================

class FormattingRule(BaseModel):
    """Conditional formatting rule."""
    rule_type: str = Field(..., description="Type of formatting rule")
    target_columns: List[str] = Field(..., description="Columns to format")
    color: Optional[str] = Field(None, description="Color to apply")
    colors: Optional[List[str]] = Field(None, description="Color scale")
    threshold: Optional[Any] = Field(None, description="Threshold value")
    above_color: Optional[str] = Field(None, description="Color for values above threshold")
    below_color: Optional[str] = Field(None, description="Color for values below threshold")
    description: str = Field(..., description="Rule description")


class FormattingPlan(BaseModel):
    """Plan for formatting operations."""
    rules: List[FormattingRule] = Field(..., description="Formatting rules")
    applies_to: str = Field(default="table", description="What to format (table, chart)")
    success: bool = Field(default=True, description="Whether plan creation succeeded")


# ============================================================================
# DASHBOARD MODELS
# ============================================================================

class DashboardSection(BaseModel):
    """Section of a dashboard."""
    section_id: str = Field(..., description="Unique section ID")
    title: str = Field(..., description="Section title")
    content_type: str = Field(..., description="Type of content (kpi, chart, table)")
    content: Any = Field(..., description="Section content")
    layout_position: Dict[str, int] = Field(..., description="Position in layout")
    priority: str = Field(default="medium", description="Display priority")

    class Config:
        arbitrary_types_allowed = True


class DashboardSpec(BaseModel):
    """Complete dashboard specification."""
    title: str = Field(..., description="Dashboard title")
    description: str = Field(..., description="Dashboard description")
    sections: List[DashboardSection] = Field(..., description="Dashboard sections")
    layout: str = Field(default="grid", description="Layout type")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# ============================================================================
# STATE SNAPSHOT
# ============================================================================

class StateSnapshot(BaseModel):
    """Immutable snapshot of application state."""
    snapshot_id: str = Field(..., description="Unique snapshot ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="When snapshot was created")
    description: str = Field(..., description="What changed")
    # Note: DataFrame stored separately, not in Pydantic model
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Snapshot metadata")

    class Config:
        arbitrary_types_allowed = True


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_operation(
    operation_type: OperationType,
    description: str,
    agent_name: str = "System",
    success: bool = True,
    error_message: Optional[str] = None,
    **metadata
) -> Operation:
    """Helper to create Operation instances."""
    import uuid
    return Operation(
        operation_id=str(uuid.uuid4())[:8],
        operation_type=operation_type,
        agent_name=agent_name,
        description=description,
        success=success,
        error_message=error_message,
        metadata=metadata
    )
