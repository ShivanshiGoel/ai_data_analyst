"""Monitoring and logging callbacks for CrewAI."""
from datetime import datetime
from typing import Dict, Any


class MonitoringCallback:
    """Callback for monitoring agent execution."""

    def __init__(self, log_file: str = None):
        """
        Initialize monitoring callback.

        Args:
            log_file: Optional file path for logging
        """
        self.log_file = log_file
        self.start_times = {}

    def on_agent_start(self, agent_name: str, task_name: str):
        """Called when agent starts execution."""
        timestamp = datetime.now()
        self.start_times[agent_name] = timestamp

        log_message = f"[{timestamp}] 🚀 Agent {agent_name} started task: {task_name}"
        print(log_message)

        if self.log_file:
            self._write_to_file(log_message)

    def on_agent_end(self, agent_name: str, result: Dict):
        """Called when agent completes execution."""
        timestamp = datetime.now()

        # Calculate duration
        if agent_name in self.start_times:
            duration = (timestamp - self.start_times[agent_name]).total_seconds()
            duration_str = f" (took {duration:.2f}s)"
        else:
            duration_str = ""

        success = result.get('success', True)
        status = "✅" if success else "❌"

        log_message = f"[{timestamp}] {status} Agent {agent_name} completed{duration_str}"
        print(log_message)

        if self.log_file:
            self._write_to_file(log_message)

    def on_tool_start(self, tool_name: str, inputs: Dict):
        """Called when tool execution starts."""
        timestamp = datetime.now()
        log_message = f"[{timestamp}] 🔧 Tool {tool_name} called"
        print(log_message)

        if self.log_file:
            self._write_to_file(log_message)

    def on_tool_end(self, tool_name: str, output: Any):
        """Called when tool execution completes."""
        timestamp = datetime.now()
        log_message = f"[{timestamp}] ✓ Tool {tool_name} completed"
        print(log_message)

        if self.log_file:
            self._write_to_file(log_message)

    def on_error(self, error: Exception, context: str = ""):
        """Called when an error occurs."""
        timestamp = datetime.now()
        log_message = f"[{timestamp}] ❌ ERROR in {context}: {str(error)}"
        print(log_message)

        if self.log_file:
            self._write_to_file(log_message)

    def _write_to_file(self, message: str):
        """Write log message to file."""
        try:
            with open(self.log_file, 'a') as f:
                f.write(message + '\n')
        except Exception as e:
            print(f"Failed to write to log file: {e}")


class PerformanceMonitor:
    """Monitor system performance metrics."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics = {
            'agent_calls': {},
            'tool_calls': {},
            'total_duration': 0,
            'errors': []
        }

    def record_agent_call(self, agent_name: str, duration: float, success: bool):
        """Record agent execution metrics."""
        if agent_name not in self.metrics['agent_calls']:
            self.metrics['agent_calls'][agent_name] = {
                'count': 0,
                'total_duration': 0,
                'success_count': 0,
                'failure_count': 0
            }

        self.metrics['agent_calls'][agent_name]['count'] += 1
        self.metrics['agent_calls'][agent_name]['total_duration'] += duration

        if success:
            self.metrics['agent_calls'][agent_name]['success_count'] += 1
        else:
            self.metrics['agent_calls'][agent_name]['failure_count'] += 1

    def record_tool_call(self, tool_name: str, duration: float):
        """Record tool execution metrics."""
        if tool_name not in self.metrics['tool_calls']:
            self.metrics['tool_calls'][tool_name] = {
                'count': 0,
                'total_duration': 0
            }

        self.metrics['tool_calls'][tool_name]['count'] += 1
        self.metrics['tool_calls'][tool_name]['total_duration'] += duration

    def get_summary(self) -> Dict:
        """Get performance summary."""
        return {
            'total_agent_calls': sum(
                m['count'] for m in self.metrics['agent_calls'].values()
            ),
            'total_tool_calls': sum(
                m['count'] for m in self.metrics['tool_calls'].values()
            ),
            'agent_metrics': self.metrics['agent_calls'],
            'tool_metrics': self.metrics['tool_calls'],
            'error_count': len(self.metrics['errors'])
        }
