# src/corporate_action_workflow_app_v2/semantic/introspection_event.py

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from .enums import Component, Operation, Severity


class IntrospectionEvent(BaseModel):

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    operation: Operation
    component: Component
    severity: Severity

    duration_ms: Optional[int] = None
    action_id: Optional[str] = None
    correlation_id: Optional[str] = None
    workflow_id: Optional[str] = None

    # Always dicts — never None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
