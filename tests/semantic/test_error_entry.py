# tests/semantic/test_error_entry.py

import pytest
from datetime import datetime, timezone

from corporate_action_workflow_app_v2.semantic.error_entry import ErrorEntry
from corporate_action_workflow_app_v2.semantic.enums import (
    Severity,
    Operation,
    Component,
    Retryability,
)

# =========================================================
# Construction Tests
# =========================================================


class TestErrorEntryConstruction:

    def test_construct_minimal_error_entry(self):
        entry = ErrorEntry(
            error_type="ValidationError",
            message="Something went wrong",
            severity=Severity.ERROR,
            operation=Operation.VALIDATE,
            component=Component.VALIDATOR,
            retryability=Retryability.NOT_RETRYABLE,
        )

        assert entry.error_type == "ValidationError"
        assert entry.message == "Something went wrong"

        assert entry.severity == Severity.ERROR
        assert entry.operation == Operation.VALIDATE
        assert entry.component == Component.VALIDATOR
        assert entry.retryability == Retryability.NOT_RETRYABLE

        assert entry.action_id is None
        assert entry.correlation_id is None
        assert entry.workflow_id is None
        assert entry.remediation is None

        assert isinstance(entry.timestamp, datetime)
        assert entry.timestamp.tzinfo == timezone.utc

        assert isinstance(entry.context, dict)
        assert entry.context == {}

    def test_construct_full_error_entry(self):
        entry = ErrorEntry(
            error_type="ProcessingError",
            message="Failed to process",
            severity=Severity.CRITICAL,
            operation=Operation.PROCESS,
            component=Component.PROCESSOR,
            retryability=Retryability.RETRYABLE,
            action_id="A1",
            correlation_id="C1",
            workflow_id="W1",
            remediation="Restart workflow",
            context={"foo": "bar"},
        )

        assert entry.retryability == Retryability.RETRYABLE
        assert entry.action_id == "A1"
        assert entry.correlation_id == "C1"
        assert entry.workflow_id == "W1"
        assert entry.remediation == "Restart workflow"
        assert entry.context == {"foo": "bar"}


# =========================================================
# Enum Enforcement Tests
# =========================================================


class TestEnumEnforcement:

    def test_invalid_severity(self):
        with pytest.raises(ValueError):
            ErrorEntry(
                error_type="X",
                message="Bad severity",
                severity="NOT_A_SEVERITY",
                operation=Operation.LOAD,
                component=Component.JSON_STORE,
                retryability=Retryability.RETRYABLE,
            )

    def test_invalid_operation(self):
        with pytest.raises(ValueError):
            ErrorEntry(
                error_type="X",
                message="Bad operation",
                severity=Severity.INFO,
                operation="NOT_AN_OPERATION",
                component=Component.JSON_STORE,
                retryability=Retryability.RETRYABLE,
            )

    def test_invalid_component(self):
        with pytest.raises(ValueError):
            ErrorEntry(
                error_type="X",
                message="Bad component",
                severity=Severity.INFO,
                operation=Operation.LOAD,
                component="NOT_A_COMPONENT",
                retryability=Retryability.RETRYABLE,
            )

    def test_invalid_retryability(self):
        with pytest.raises(ValueError):
            ErrorEntry(
                error_type="X",
                message="Bad retryability",
                severity=Severity.INFO,
                operation=Operation.LOAD,
                component=Component.JSON_STORE,
                retryability="NOT_RETRYABLE_VALUE",
            )


# =========================================================
# Timestamp Tests
# =========================================================


class TestTimestampBehavior:

    def test_timestamp_is_utc(self):
        entry = ErrorEntry(
            error_type="X",
            message="Timestamp test",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
            retryability=Retryability.RETRYABLE,
        )
        assert entry.timestamp.tzinfo == timezone.utc

    def test_timestamp_auto_populates(self):
        before = datetime.now(timezone.utc)
        entry = ErrorEntry(
            error_type="X",
            message="Timestamp auto",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
            retryability=Retryability.RETRYABLE,
        )
        after = datetime.now(timezone.utc)

        assert before <= entry.timestamp <= after


# =========================================================
# Context Tests
# =========================================================


class TestContextBehavior:

    def test_context_defaults_to_empty_dict(self):
        entry = ErrorEntry(
            error_type="X",
            message="Context test",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
            retryability=Retryability.RETRYABLE,
        )
        assert entry.context == {}

    def test_context_accepts_arbitrary_data(self):
        entry = ErrorEntry(
            error_type="X",
            message="Context test",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
            retryability=Retryability.RETRYABLE,
            context={"a": 1, "b": "two"},
        )
        assert entry.context == {"a": 1, "b": "two"}

    def test_context_rejects_none(self):
        with pytest.raises(ValueError):
            ErrorEntry(
                error_type="X",
                message="Bad context",
                severity=Severity.INFO,
                operation=Operation.LOAD,
                component=Component.JSON_STORE,
                retryability=Retryability.RETRYABLE,
                context=None,
            )


# =========================================================
# Serialization Tests
# =========================================================


class TestSerialization:

    def test_model_dump(self):
        entry = ErrorEntry(
            error_type="DumpError",
            message="Dump test",
            severity=Severity.WARNING,
            operation=Operation.VALIDATE,
            component=Component.VALIDATOR,
            retryability=Retryability.NOT_RETRYABLE,
            context={"x": 42},
        )

        d = entry.model_dump()

        assert d["error_type"] == "DumpError"
        assert d["message"] == "Dump test"
        assert d["severity"] == Severity.WARNING
        assert d["operation"] == Operation.VALIDATE
        assert d["component"] == Component.VALIDATOR
        assert d["retryability"] == Retryability.NOT_RETRYABLE
        assert d["context"] == {"x": 42}
        assert isinstance(d["timestamp"], datetime)

    def test_round_trip(self):
        entry = ErrorEntry(
            error_type="RoundTripError",
            message="Round trip",
            severity=Severity.CRITICAL,
            operation=Operation.PROCESS,
            component=Component.ORCHESTRATOR,
            retryability=Retryability.RETRYABLE,
            context={"k": "v"},
        )

        d = entry.model_dump()
        restored = ErrorEntry.model_validate(d)

        assert restored.error_type == entry.error_type
        assert restored.message == entry.message
        assert restored.severity == entry.severity
        assert restored.operation == entry.operation
        assert restored.component == entry.component
        assert restored.retryability == entry.retryability
        assert restored.context == entry.context
        assert restored.timestamp == entry.timestamp
