# src/corporate_action_workflow_app_v2/semantic/agentic_context.py

from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from .error_entry import ErrorEntry
from .introspection_event import IntrospectionEvent
from .log_entry import LogEntry


class AgenticContext(BaseModel):
    """
    Unified semantic envelope for all agentic-aware operations.

    Every subsystem (persistence, validation, workflow, orchestration,
    agentic reasoning) returns an AgenticContext so higher layers can
    inspect:
        - what happened (log)
        - what went wrong (error)
        - how it performed (introspection)
        - what it produced (payload)
    """

    log: Optional[LogEntry] = None
    error: Optional[ErrorEntry] = None
    introspection: Optional[IntrospectionEvent] = None
    payload: Any = None

    # Optional: semantic context for future agentic enrichment
    # (kept separate from log.context to avoid mixing layers)
    context: Dict[str, Any] = Field(default_factory=dict)

    def has_error(self) -> bool:
        return self.error is not None

    def is_success(self) -> bool:
        return self.error is None
