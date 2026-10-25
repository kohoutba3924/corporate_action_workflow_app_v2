# src/corporate_action_workflow_app_v2/persistence/persistence_logger.py

from typing import Any, Dict, Optional

from corporate_action_workflow_app_v2.semantic import (
    Component,
    LogEntry,
    Operation,
    Retryability,
    Severity,
)


class PersistenceLogger:
    def log(
        self,
        message: str,
        *,
        severity: Severity,
        operation: Operation,
        component: Component,
        retryability: Optional[Retryability] = None,
        action_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        remediation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> LogEntry:

        # Ensure context is always a dict (LogEntry requires this)
        safe_context: Dict[str, Any] = context or {}

        entry = LogEntry(
            severity=severity,
            operation=operation,
            component=component,
            message=message,
            action_id=action_id,
            correlation_id=correlation_id,
            workflow_id=workflow_id,
            retryability=retryability,
            remediation=remediation,
            context=safe_context,
        )
        return entry
