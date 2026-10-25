# src/corporate_action_workflow_app_v2/semantic/log_entry.py

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from .enums import Component, Operation, Retryability, Severity


class LogEntry(BaseModel):
    message: str
    severity: Severity
    operation: Operation
    component: Component
    retryability: Optional[Retryability] = None

    action_id: Optional[str] = None
    correlation_id: Optional[str] = None
    workflow_id: Optional[str] = None
    remediation: Optional[str] = None

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    context: Dict[str, Any] = Field(default_factory=dict)
