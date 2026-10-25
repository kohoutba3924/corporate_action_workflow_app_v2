# tests/semantic/test_log_entry.py

import pytest
from datetime import datetime, timezone

from corporate_action_workflow_app_v2.semantic.log_entry import LogEntry
from corporate_action_workflow_app_v2.semantic.enums import (
    Severity,
    Operation,
    Component,
    Retryability,
)

# =========================================================
# Construction Tests
# =========================================================


class TestLogEntryConstruction:

    def test_construct_minimal_log_entry(self):
        entry = LogEntry(
            message="Test message",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
        )

        assert entry.message == "Test message"
        assert entry.severity == Severity.INFO
        assert entry.operation == Operation.LOAD
        assert entry.component == Component.JSON_STORE

        assert entry.retryability is None
        assert entry.action_id is None
        assert entry.correlation_id is None
        assert entry.workflow_id is None
        assert entry.remediation is None

        assert isinstance(entry.timestamp, datetime)
        assert entry.timestamp.tzinfo == timezone.utc

        assert isinstance(entry.context, dict)
        assert entry.context == {}

    def test_construct_full_log_entry(self):
        entry = LogEntry(
            message="Full entry",
            severity=Severity.ERROR,
            operation=Operation.SAVE,
            component=Component.PROCESSOR,
            retryability=Retryability.RETRYABLE,
            action_id="A1",
            correlation_id="C1",
            workflow_id="W1",
            remediation="Fix it",
            context={"foo": "bar"},
        )

        assert entry.retryability == Retryability.RETRYABLE
        assert entry.action_id == "A1"
        assert entry.correlation_id == "C1"
        assert entry.workflow_id == "W1"
        assert entry.remediation == "Fix it"
        assert entry.context == {"foo": "bar"}


# =========================================================
# Enum Enforcement Tests
# =========================================================


class TestEnumEnforcement:

    def test_invalid_severity(self):
        with pytest.raises(ValueError):
            LogEntry(
                message="Bad severity",
                severity="NOT_A_SEVERITY",
                operation=Operation.LOAD,
                component=Component.JSON_STORE,
            )

    def test_invalid_operation(self):
        with pytest.raises(ValueError):
            LogEntry(
                message="Bad operation",
                severity=Severity.INFO,
                operation="NOT_AN_OPERATION",
                component=Component.JSON_STORE,
            )

    def test_invalid_component(self):
        with pytest.raises(ValueError):
            LogEntry(
                message="Bad component",
                severity=Severity.INFO,
                operation=Operation.LOAD,
                component="NOT_A_COMPONENT",
            )

    def test_invalid_retryability(self):
        with pytest.raises(ValueError):
            LogEntry(
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
        entry = LogEntry(
            message="Timestamp test",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
        )
        assert entry.timestamp.tzinfo == timezone.utc

    def test_timestamp_auto_populates(self):
        before = datetime.now(timezone.utc)
        entry = LogEntry(
            message="Timestamp auto",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
        )
        after = datetime.now(timezone.utc)

        assert before <= entry.timestamp <= after


# =========================================================
# Context Tests
# =========================================================


class TestContextBehavior:

    def test_context_defaults_to_empty_dict(self):
        entry = LogEntry(
            message="Context test",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
        )
        assert entry.context == {}

    def test_context_accepts_arbitrary_data(self):
        entry = LogEntry(
            message="Context test",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
            context={"a": 1, "b": "two"},
        )
        assert entry.context == {"a": 1, "b": "two"}


# =========================================================
# Serialization Tests
# =========================================================


class TestSerialization:

    def test_model_dump(self):
        entry = LogEntry(
            message="Dump test",
            severity=Severity.WARNING,
            operation=Operation.VALIDATE,
            component=Component.VALIDATOR,
            context={"x": 42},
        )

        d = entry.model_dump()

        assert d["message"] == "Dump test"
        assert d["severity"] == Severity.WARNING
        assert d["operation"] == Operation.VALIDATE
        assert d["component"] == Component.VALIDATOR
        assert d["context"] == {"x": 42}
        assert isinstance(d["timestamp"], datetime)

    def test_round_trip(self):
        entry = LogEntry(
            message="Round trip",
            severity=Severity.CRITICAL,
            operation=Operation.PROCESS,
            component=Component.ORCHESTRATOR,
            context={"k": "v"},
        )

        d = entry.model_dump()
        restored = LogEntry.model_validate(d)

        assert restored.message == entry.message
        assert restored.severity == entry.severity
        assert restored.operation == entry.operation
        assert restored.component == entry.component
        assert restored.context == entry.context
        assert restored.timestamp == entry.timestamp
