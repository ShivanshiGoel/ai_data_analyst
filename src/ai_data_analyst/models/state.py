"""Application state management with undo/redo capability."""
import pandas as pd
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
from copy import deepcopy


class StateSnapshot:
    """Immutable snapshot of application state for undo/redo."""

    def __init__(self, df: pd.DataFrame, metadata: Dict[str, Any], description: str):
        """
        Create state snapshot.

        Args:
            df: DataFrame to snapshot (will be deep copied)
            metadata: Additional state metadata (KPIs, charts, etc.)
            description: Description of what changed
        """
        self.snapshot_id = str(uuid.uuid4())[:8]
        self.timestamp = datetime.now()
        self.dataframe = df.copy() if df is not None else None
        self.metadata = deepcopy(metadata)
        self.description = description


class ApplicationState:
    """Central application state manager with undo/redo."""

    def __init__(self, max_history: int = 50):
        """
        Initialize application state.

        Args:
            max_history: Maximum number of undo levels to maintain
        """
        # Current state
        self.current_df: Optional[pd.DataFrame] = None
        self.schema: Optional[Dict] = None
        self.filename: Optional[str] = None
        self.active_sheet: Optional[str] = None

        # Derived data
        self.kpis: List[Dict] = []
        self.charts: List[Dict] = []
        self.formatting_rules: List[Dict] = []

        # History management
        self.history_stack: List[StateSnapshot] = []
        self.redo_stack: List[StateSnapshot] = []
        self.max_history = max_history

        # Operation tracking
        self.operation_log: List[Dict] = []
        self.agent_messages: List[Dict] = []

        # Statistics
        self.total_operations = 0
        self.load_time: Optional[datetime] = None

    # ========================================================================
    # CORE DATA OPERATIONS
    # ========================================================================

    def load_dataframe(self, df: pd.DataFrame, filename: str, 
                       sheet_name: str = "Sheet1", schema: Dict = None):
        """
        Load initial dataframe.

        Args:
            df: DataFrame to load
            filename: Source filename
            sheet_name: Sheet name
            schema: Optional pre-computed schema
        """
        self.current_df = df.copy()
        self.filename = filename
        self.active_sheet = sheet_name
        self.schema = schema
        self.load_time = datetime.now()

        # Clear derived data
        self.kpis = []
        self.charts = []
        self.formatting_rules = []

        # Reset history
        self.history_stack = []
        self.redo_stack = []

        # Log operation
        self._log_operation(
            "LOAD",
            f"Loaded {filename} ({len(df)} rows, {len(df.columns)} columns)",
            success=True
        )

    def update_dataframe(self, df: pd.DataFrame, operation: str, 
                        agent_name: str = "System", save_snapshot: bool = True):
        """
        Update current dataframe with undo capability.

        Args:
            df: New dataframe
            operation: Description of operation
            agent_name: Agent performing update
            save_snapshot: Whether to save snapshot for undo
        """
        if save_snapshot and self.current_df is not None:
            self._save_snapshot(operation)

        self.current_df = df.copy()

        # Clear redo stack on new operation
        self.redo_stack = []

        # Log operation
        self._log_operation("TRANSFORM", operation, agent_name=agent_name, success=True)

    # ========================================================================
    # UNDO/REDO OPERATIONS
    # ========================================================================

    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return len(self.history_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return len(self.redo_stack) > 0

    def undo(self) -> bool:
        """
        Undo last operation.

        Returns:
            True if undo succeeded, False otherwise
        """
        if not self.can_undo():
            return False

        # Save current state to redo stack
        current_snapshot = StateSnapshot(
            self.current_df,
            self._get_metadata(),
            "Current state before undo"
        )
        self.redo_stack.append(current_snapshot)

        # Restore previous state
        previous = self.history_stack.pop()
        self.current_df = previous.dataframe.copy() if previous.dataframe is not None else None
        self._restore_metadata(previous.metadata)

        # Log operation
        self._log_operation("UNDO", f"Undid: {previous.description}", success=True)

        return True

    def redo(self) -> bool:
        """
        Redo last undone operation.

        Returns:
            True if redo succeeded, False otherwise
        """
        if not self.can_redo():
            return False

        # Save current state to history
        current_snapshot = StateSnapshot(
            self.current_df,
            self._get_metadata(),
            "Current state before redo"
        )
        self.history_stack.append(current_snapshot)

        # Restore redo state
        next_state = self.redo_stack.pop()
        self.current_df = next_state.dataframe.copy() if next_state.dataframe is not None else None
        self._restore_metadata(next_state.metadata)

        # Log operation
        self._log_operation("REDO", f"Redid: {next_state.description}", success=True)

        return True

    def _save_snapshot(self, description: str):
        """Save current state as snapshot."""
        snapshot = StateSnapshot(
            self.current_df,
            self._get_metadata(),
            description
        )
        self.history_stack.append(snapshot)

        # Prune old snapshots if exceeding max
        if len(self.history_stack) > self.max_history:
            self.history_stack.pop(0)

    def _get_metadata(self) -> Dict[str, Any]:
        """Get current metadata for snapshot."""
        return {
            'kpis': deepcopy(self.kpis),
            'charts': deepcopy(self.charts),
            'formatting_rules': deepcopy(self.formatting_rules),
            'schema': deepcopy(self.schema) if self.schema else None
        }

    def _restore_metadata(self, metadata: Dict[str, Any]):
        """Restore metadata from snapshot."""
        self.kpis = deepcopy(metadata.get('kpis', []))
        self.charts = deepcopy(metadata.get('charts', []))
        self.formatting_rules = deepcopy(metadata.get('formatting_rules', []))
        if 'schema' in metadata and metadata['schema']:
            self.schema = deepcopy(metadata['schema'])

    # ========================================================================
    # DERIVED DATA MANAGEMENT
    # ========================================================================

    def set_kpis(self, kpis: List[Dict]):
        """Set KPIs."""
        self.kpis = kpis
        self._log_operation("ANALYTICS", f"Generated {len(kpis)} KPIs", success=True)

    def add_chart(self, chart: Dict):
        """Add chart specification."""
        self.charts.append(chart)

    def clear_charts(self):
        """Clear all charts."""
        self.charts = []

    def set_formatting_rules(self, rules: List[Dict]):
        """Set formatting rules."""
        self.formatting_rules = rules

    # ========================================================================
    # OPERATION LOGGING
    # ========================================================================

    def _log_operation(self, operation_type: str, description: str,
                      agent_name: str = "System", success: bool = True,
                      error_message: str = None):
        """Log an operation."""
        operation = {
            'id': str(uuid.uuid4())[:8],
            'type': operation_type,
            'agent': agent_name,
            'description': description,
            'timestamp': datetime.now(),
            'success': success,
            'error': error_message
        }
        self.operation_log.append(operation)
        self.total_operations += 1

    def log_agent_message(self, from_agent: str, to_agent: str,
                         message: str, metadata: Dict = None):
        """
        Log agent-to-agent communication.

        Args:
            from_agent: Sender agent
            to_agent: Receiver agent
            message: Message content
            metadata: Additional metadata
        """
        comm = {
            'id': str(uuid.uuid4())[:8],
            'from': from_agent,
            'to': to_agent,
            'message': message,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        }
        self.agent_messages.append(comm)

    def get_recent_operations(self, limit: int = 10) -> List[Dict]:
        """Get recent operations."""
        return self.operation_log[-limit:] if self.operation_log else []

    def get_recent_messages(self, limit: int = 10) -> List[Dict]:
        """Get recent agent messages."""
        return self.agent_messages[-limit:] if self.agent_messages else []

    # ========================================================================
    # STATE INSPECTION
    # ========================================================================

    def get_state_summary(self) -> Dict[str, Any]:
        """Get summary of current state."""
        return {
            'has_data': self.current_df is not None,
            'rows': len(self.current_df) if self.current_df is not None else 0,
            'columns': len(self.current_df.columns) if self.current_df is not None else 0,
            'filename': self.filename,
            'kpi_count': len(self.kpis),
            'chart_count': len(self.charts),
            'can_undo': self.can_undo(),
            'can_redo': self.can_redo(),
            'history_depth': len(self.history_stack),
            'total_operations': self.total_operations,
            'load_time': self.load_time
        }

    def reset(self):
        """Reset all state."""
        self.__init__(max_history=self.max_history)


# ========================================================================
# GLOBAL STATE INSTANCE
# ========================================================================

# Global singleton instance
app_state = ApplicationState()
