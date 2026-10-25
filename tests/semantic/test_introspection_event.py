# tests/semantic/introspection_event.py

import pytest
from datetime import datetime, timezone

from corporate_action_workflow_app_v2.semantic.introspection_event import (
    IntrospectionEvent,
)
from corporate_action_workflow_app_v2.semantic.enums import (
    Severity,
    Operation,
    Component,
)

# =========================================================
# Construction Tests
# =========================================================


class TestIntrospectionEventConstruction:

    def test_construct_minimal_event(self):
        event = IntrospectionEvent(
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
            severity=Severity.INFO,
        )

        assert event.operation == Operation.LOAD
        assert event.component == Component.JSON_STORE
        assert event.severity == Severity.INFO

        assert event.duration_ms is None
        assert event.action_id is None
        assert event.correlation_id is None
        assert event.workflow_id is None

        assert isinstance(event.timestamp, datetime)
        assert event.timestamp.tzinfo == timezone.utc

        assert isinstance(event.metrics, dict)
        assert event.metrics == {}

        assert isinstance(event.context, dict)
        assert event.context == {}

    def test_construct_full_event(self):
        event = IntrospectionEvent(
            operation=Operation.PROCESS,
            component=Component.PROCESSOR,
            severity=Severity.WARNING,
            duration_ms=123,
            action_id="A1",
            correlation_id="C1",
            workflow_id="W1",
            metrics={"m1": 10, "m2": "ok"},
            context={"foo": "bar"},
        )

        assert event.duration_ms == 123
        assert event.action_id == "A1"
        assert event.correlation_id == "C1"
        assert event.workflow_id == "W1"
        assert event.metrics == {"m1": 10, "m2": "ok"}
        assert event.context == {"foo": "bar"}


# =========================================================
# Enum Enforcement Tests
# =========================================================


class TestEnumEnforcement:

    def test_invalid_operation(self):
        with pytest.raises(ValueError):
            IntrospectionEvent(
                operation="NOT_AN_OPERATION",
                component=Component.JSON_STORE,
                severity=Severity.INFO,
            )

    def test_invalid_component(self):
        with pytest.raises(ValueError):
            IntrospectionEvent(
                operation=Operation.LOAD,
                component="NOT_A_COMPONENT",
                severity=Severity.INFO,
            )

    def test_invalid_severity(self):
        with pytest.raises(ValueError):
            IntrospectionEvent(
                operation=Operation.LOAD,
                component=Component.JSON_STORE,
                severity="NOT_A_SEVERITY",
            )


# =========================================================
# Timestamp Tests
# =========================================================


class TestTimestampBehavior:

    def test_timestamp_is_utc(self):
        event = IntrospectionEvent(
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
            severity=Severity.INFO,
        )
        assert event.timestamp.tzinfo == timezone.utc

    def test_timestamp_auto_populates(self):
        before = datetime.now(timezone.utc)
        event = IntrospectionEvent(
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
            severity=Severity.INFO,
        )
        after = datetime.now(timezone.utc)

        assert before <= event.timestamp <= after


# =========================================================
# Metrics Tests
# =========================================================


class TestMetricsBehavior:

    def test_metrics_defaults_to_empty_dict(self):
        event = IntrospectionEvent(
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
            severity=Severity.INFO,
        )
        assert event.metrics == {}

    def test_metrics_accepts_arbitrary_data(self):
        event = IntrospectionEvent(
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
            severity=Severity.INFO,
            metrics={"a": 1, "b": "two"},
        )
        assert event.metrics == {"a": 1, "b": "two"}

    def test_metrics_rejects_none(self):
        with pytest.raises(ValueError):
            IntrospectionEvent(
                operation=Operation.LOAD,
                component=Component.JSON_STORE,
                severity=Severity.INFO,
                metrics=None,
            )

    def test_metrics_rejects_non_dict(self):
        with pytest.raises(ValueError):
            IntrospectionEvent(
                operation=Operation.LOAD,
                component=Component.JSON_STORE,
                severity=Severity.INFO,
                metrics=["not", "a", "dict"],
            )


# =========================================================
# Context Tests
# =========================================================


class TestContextBehavior:

    def test_context_defaults_to_empty_dict(self):
        event = IntrospectionEvent(
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
            severity=Severity.INFO,
        )
        assert event.context == {}

    def test_context_accepts_arbitrary_data(self):
        event = IntrospectionEvent(
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
            severity=Severity.INFO,
            context={"x": 42},
        )
        assert event.context == {"x": 42}

    def test_context_rejects_none(self):
        with pytest.raises(ValueError):
            IntrospectionEvent(
                operation=Operation.LOAD,
                component=Component.JSON_STORE,
                severity=Severity.INFO,
                context=None,
            )

    def test_context_rejects_non_dict(self):
        with pytest.raises(ValueError):
            IntrospectionEvent(
                operation=Operation.LOAD,
                component=Component.JSON_STORE,
                severity=Severity.INFO,
                context="not a dict",
            )


# =========================================================
# Serialization Tests
# =========================================================


class TestSerialization:

    def test_model_dump(self):
        event = IntrospectionEvent(
            operation=Operation.VALIDATE,
            component=Component.VALIDATOR,
            severity=Severity.CRITICAL,
            metrics={"m": 1},
            context={"c": 2},
        )

        d = event.model_dump()

        assert d["operation"] == Operation.VALIDATE
        assert d["component"] == Component.VALIDATOR
        assert d["severity"] == Severity.CRITICAL
        assert d["metrics"] == {"m": 1}
        assert d["context"] == {"c": 2}
        assert isinstance(d["timestamp"], datetime)

    def test_round_trip(self):
        event = IntrospectionEvent(
            operation=Operation.PROCESS,
            component=Component.ORCHESTRATOR,
            severity=Severity.WARNING,
            duration_ms=250,
            metrics={"k": "v"},
            context={"foo": "bar"},
        )

        d = event.model_dump()
        restored = IntrospectionEvent.model_validate(d)

        assert restored.operation == event.operation
        assert restored.component == event.component
        assert restored.severity == event.severity
        assert restored.duration_ms == event.duration_ms
        assert restored.metrics == event.metrics
        assert restored.context == event.context
        assert restored.timestamp == event.timestamp
