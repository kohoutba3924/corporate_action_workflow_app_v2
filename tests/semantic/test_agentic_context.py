# tests/semantic/test_agentic_context.py

import pytest

from corporate_action_workflow_app_v2.semantic.agentic_context import AgenticContext
from corporate_action_workflow_app_v2.semantic.log_entry import LogEntry
from corporate_action_workflow_app_v2.semantic.error_entry import ErrorEntry
from corporate_action_workflow_app_v2.semantic.introspection_event import (
    IntrospectionEvent,
)
from corporate_action_workflow_app_v2.semantic.enums import (
    Severity,
    Operation,
    Component,
    Retryability,
)

# =========================================================
# Construction Tests
# =========================================================


class TestAgenticContextConstruction:

    def test_construct_empty_context(self):
        ctx = AgenticContext()

        assert ctx.log is None
        assert ctx.error is None
        assert ctx.introspection is None
        assert ctx.payload is None
        assert ctx.context == {}

    def test_construct_with_log(self):
        log = LogEntry(
            message="Test log",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
        )
        ctx = AgenticContext(log=log)

        assert ctx.log is log
        assert ctx.error is None
        assert ctx.introspection is None

    def test_construct_with_error(self):
        err = ErrorEntry(
            error_type="X",
            message="Something failed",
            severity=Severity.ERROR,
            operation=Operation.PROCESS,
            component=Component.PROCESSOR,
            retryability=Retryability.NOT_RETRYABLE,
        )
        ctx = AgenticContext(error=err)

        assert ctx.error is err
        assert ctx.log is None
        assert ctx.introspection is None

    def test_construct_with_introspection(self):
        intro = IntrospectionEvent(
            operation=Operation.VALIDATE,
            component=Component.VALIDATOR,
            severity=Severity.WARNING,
        )
        ctx = AgenticContext(introspection=intro)

        assert ctx.introspection is intro
        assert ctx.log is None
        assert ctx.error is None

    def test_construct_with_payload(self):
        ctx = AgenticContext(payload={"result": 42})
        assert ctx.payload == {"result": 42}


# =========================================================
# Nested Model Validation Tests
# =========================================================


class TestNestedModelValidation:

    def test_invalid_log_type(self):
        with pytest.raises(ValueError):
            AgenticContext(log="not a log entry")

    def test_invalid_error_type(self):
        with pytest.raises(ValueError):
            AgenticContext(error=123)

    def test_invalid_introspection_type(self):
        with pytest.raises(ValueError):
            AgenticContext(introspection=["not", "valid"])


# =========================================================
# Context Behavior Tests
# =========================================================


class TestContextBehavior:

    def test_context_defaults_to_empty_dict(self):
        ctx = AgenticContext()
        assert ctx.context == {}

    def test_context_accepts_arbitrary_data(self):
        ctx = AgenticContext(context={"a": 1, "b": "two"})
        assert ctx.context == {"a": 1, "b": "two"}

    def test_context_rejects_none(self):
        with pytest.raises(ValueError):
            AgenticContext(context=None)

    def test_context_rejects_non_dict(self):
        with pytest.raises(ValueError):
            AgenticContext(context="not a dict")


# =========================================================
# Helper Method Tests
# =========================================================


class TestHelperMethods:

    def test_has_error_true(self):
        err = ErrorEntry(
            error_type="X",
            message="Failure",
            severity=Severity.ERROR,
            operation=Operation.PROCESS,
            component=Component.PROCESSOR,
            retryability=Retryability.NOT_RETRYABLE,
        )
        ctx = AgenticContext(error=err)
        assert ctx.has_error() is True
        assert ctx.is_success() is False

    def test_has_error_false(self):
        ctx = AgenticContext()
        assert ctx.has_error() is False
        assert ctx.is_success() is True


# =========================================================
# Serialization Tests
# =========================================================


class TestSerialization:

    def test_model_dump(self):
        log = LogEntry(
            message="Dump test",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
        )
        ctx = AgenticContext(
            log=log,
            payload={"x": 1},
            context={"k": "v"},
        )

        d = ctx.model_dump()

        assert d["log"]["message"] == "Dump test"
        assert d["payload"] == {"x": 1}
        assert d["context"] == {"k": "v"}

    def test_round_trip(self):
        intro = IntrospectionEvent(
            operation=Operation.PROCESS,
            component=Component.ORCHESTRATOR,
            severity=Severity.CRITICAL,
            metrics={"m": 10},
            context={"c": 20},
        )

        ctx = AgenticContext(
            introspection=intro,
            payload=[1, 2, 3],
            context={"foo": "bar"},
        )

        d = ctx.model_dump()
        restored = AgenticContext.model_validate(d)

        assert restored.introspection is not None
        assert ctx.introspection is not None

        assert restored.introspection.operation == ctx.introspection.operation
        assert restored.introspection.component == ctx.introspection.component
        assert restored.introspection.severity == ctx.introspection.severity
        assert restored.introspection.metrics == ctx.introspection.metrics
        assert restored.introspection.context == ctx.introspection.context

        assert restored.payload == ctx.payload
        assert restored.context == ctx.context
