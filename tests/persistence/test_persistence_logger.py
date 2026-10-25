# tests/persistence/test_persistence_logger.py

from corporate_action_workflow_app_v2.persistence.persistence_logger import (
    PersistenceLogger,
)
from corporate_action_workflow_app_v2.semantic.enums import (
    Component,
    Operation,
    Retryability,
    Severity,
)
from corporate_action_workflow_app_v2.semantic.log_entry import LogEntry

# =========================================================
# PersistenceLogger Tests
# =========================================================

"""
This suite intentionally tests only the adapter responsibilities of PersistenceLogger (normalization and propagation). 
It avoids re-testing enum validation, timestamp implementation details, serialization, and round-trip behavior because 
those are already covered by the LogEntry semantic test suite.
"""


class TestPersistenceLogger:

    def test_log_returns_log_entry(self):
        logger = PersistenceLogger()

        entry = logger.log(
            "Test message",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
        )

        assert isinstance(entry, LogEntry)

    def test_message_propagates(self):
        logger = PersistenceLogger()

        entry = logger.log(
            "Persistence message",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
        )

        assert entry.message == "Persistence message"

    def test_core_fields_propagate(self):
        logger = PersistenceLogger()

        entry = logger.log(
            "Core field test",
            severity=Severity.WARNING,
            operation=Operation.SAVE,
            component=Component.PROCESSOR,
        )

        assert entry.severity == Severity.WARNING
        assert entry.operation == Operation.SAVE
        assert entry.component == Component.PROCESSOR

    def test_context_defaults_to_empty_dict(self):
        logger = PersistenceLogger()

        entry = logger.log(
            "Context normalization",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
            context=None,
        )

        assert entry.context == {}

    def test_context_propagates(self):
        logger = PersistenceLogger()

        context = {
            "filepath": "store.json",
            "records": 42,
        }

        entry = logger.log(
            "Context propagation",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
            context=context,
        )

        assert entry.context == context

    def test_action_id_propagates(self):
        logger = PersistenceLogger()

        entry = logger.log(
            "Action id test",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
            action_id="ACTION-123",
        )

        assert entry.action_id == "ACTION-123"

    def test_correlation_id_propagates(self):
        logger = PersistenceLogger()

        entry = logger.log(
            "Correlation id test",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
            correlation_id="CORR-123",
        )

        assert entry.correlation_id == "CORR-123"

    def test_workflow_id_propagates(self):
        logger = PersistenceLogger()

        entry = logger.log(
            "Workflow id test",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
            workflow_id="WF-123",
        )

        assert entry.workflow_id == "WF-123"

    def test_retryability_propagates(self):
        logger = PersistenceLogger()

        entry = logger.log(
            "Retryability test",
            severity=Severity.WARNING,
            operation=Operation.SAVE,
            component=Component.JSON_STORE,
            retryability=Retryability.RETRYABLE,
        )

        assert entry.retryability == Retryability.RETRYABLE

    def test_remediation_propagates(self):
        logger = PersistenceLogger()

        entry = logger.log(
            "Remediation test",
            severity=Severity.ERROR,
            operation=Operation.SAVE,
            component=Component.JSON_STORE,
            remediation="Retry operation.",
        )

        assert entry.remediation == "Retry operation."

    def test_timestamp_present(self):
        logger = PersistenceLogger()

        entry = logger.log(
            "Timestamp test",
            severity=Severity.INFO,
            operation=Operation.LOAD,
            component=Component.JSON_STORE,
        )

        assert entry.timestamp is not None
