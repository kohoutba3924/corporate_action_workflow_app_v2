# src/corporate_action_workflow_app_v2/semantic/error_entry.py

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from .enums import Component, Operation, Retryability, Severity


class ErrorEntry(BaseModel):
    error_type: str
    message: str

    severity: Severity
    operation: Operation
    component: Component

    action_id: Optional[str] = None
    correlation_id: Optional[str] = None
    workflow_id: Optional[str] = None

    retryability: Retryability
    remediation: Optional[str] = None

    # Always a dict — never None
    context: Dict[str, Any] = Field(default_factory=dict)

    # Timestamp added (UTC, timezone-aware)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
