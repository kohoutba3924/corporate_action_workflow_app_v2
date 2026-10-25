# src/corporate_action_workflow_app_v2/persistence/persistence_errors.py

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from corporate_action_workflow_app_v2.semantic import (
    Component,
    ErrorEntry,
    Operation,
    Retryability,
    Severity,
)


class PersistenceError(Exception):
    """
    Base class for persistence-related errors.
    Produce structured semantic ErrorEntry objects.
    """

    def __init__(
        self,
        message: str,
        *,
        operation: Operation,
        retryability: Retryability,
        action_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        remediation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)

        safe_context: Dict[str, Any] = context or {}

        self.entry = ErrorEntry(
            error_type=self.__class__.__name__,
            message=message,
            severity=Severity.ERROR,
            operation=operation,
            component=Component.JSON_STORE,
            action_id=action_id,
            correlation_id=correlation_id,
            workflow_id=workflow_id,
            retryability=retryability,
            remediation=remediation,
            context=safe_context,
            timestamp=datetime.now(timezone.utc),
        )


class CorruptionError(PersistenceError):
    """
    Raised when JSON data is corrupted or unreadable.
    """

    def __init__(
        self,
        message: str = "JSON data is corrupted or unreadable.",
        *,
        action_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message,
            operation=Operation.CORRUPTION,
            retryability=Retryability.NOT_RETRYABLE,
            action_id=action_id,
            correlation_id=correlation_id,
            workflow_id=workflow_id,
            remediation="Restore from backup or regenerate the JSON store.",
            context=context,
        )


class AtomicWriteError(PersistenceError):
    """
    Raised when an atomic write or backup operation fails.
    """

    def __init__(
        self,
        message: str = "Atomic write operation failed.",
        *,
        action_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message,
            operation=Operation.SAVE,
            retryability=Retryability.RETRYABLE,
            action_id=action_id,
            correlation_id=correlation_id,
            workflow_id=workflow_id,
            remediation="Retry the write operation after verifying file lock availability.",
            context=context,
        )


class ActionNotFoundError(PersistenceError):
    """
    Raised when an update is requested for a CorporateAction
    that does not exist in the persistence store.
    """

    def __init__(
        self,
        message: str = "CorporateAction was not found in the persistence store.",
        *,
        action_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message,
            operation=Operation.SAVE,
            retryability=Retryability.NOT_RETRYABLE,
            action_id=action_id,
            correlation_id=correlation_id,
            workflow_id=workflow_id,
            remediation=(
                "Verify the action exists in persistence before attempting an update."
            ),
            context=context,
        )
