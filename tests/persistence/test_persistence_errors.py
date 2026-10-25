# tests/persistence/test_persistence_errors.py

from corporate_action_workflow_app_v2.persistence.persistence_errors import (
    ActionNotFoundError,
    AtomicWriteError,
    CorruptionError,
    PersistenceError,
)
from corporate_action_workflow_app_v2.semantic.enums import (
    Component,
    Operation,
    Retryability,
    Severity,
)

# =========================================================
# PersistenceError Tests
# =========================================================


class TestPersistenceError:

    def test_construct_persistence_error(self):
        err = PersistenceError(
            "Base persistence error",
            operation=Operation.SAVE,
            retryability=Retryability.RETRYABLE,
        )

        assert str(err) == "Base persistence error"

        entry = err.entry

        assert entry.error_type == "PersistenceError"
        assert entry.message == "Base persistence error"
        assert entry.operation == Operation.SAVE
        assert entry.retryability == Retryability.RETRYABLE
        assert entry.severity == Severity.ERROR
        assert entry.component == Component.JSON_STORE

    def test_context_defaults_to_empty_dict(self):
        err = PersistenceError(
            "Context test",
            operation=Operation.SAVE,
            retryability=Retryability.RETRYABLE,
            context=None,
        )

        assert err.entry.context == {}

    def test_metadata_fields_propagate(self):
        err = PersistenceError(
            "Metadata propagation",
            operation=Operation.SAVE,
            retryability=Retryability.RETRYABLE,
            action_id="A1",
            correlation_id="C1",
            workflow_id="W1",
        )

        entry = err.entry

        assert entry.action_id == "A1"
        assert entry.correlation_id == "C1"
        assert entry.workflow_id == "W1"

    def test_is_exception(self):
        err = PersistenceError(
            "Exception test",
            operation=Operation.SAVE,
            retryability=Retryability.RETRYABLE,
        )

        assert isinstance(err, Exception)


# =========================================================
# CorruptionError Tests
# =========================================================


class TestCorruptionError:

    def test_default_values(self):
        err = CorruptionError()

        entry = err.entry

        assert entry.error_type == "CorruptionError"
        assert entry.operation == Operation.CORRUPTION
        assert entry.retryability == Retryability.NOT_RETRYABLE
        assert entry.severity == Severity.ERROR
        assert entry.component == Component.JSON_STORE

    def test_default_remediation(self):
        err = CorruptionError()

        assert (
            err.entry.remediation == "Restore from backup or regenerate the JSON store."
        )

    def test_custom_message(self):
        err = CorruptionError("Custom corruption message")

        assert err.entry.message == "Custom corruption message"

    def test_is_exception(self):
        err = CorruptionError()

        assert isinstance(err, Exception)


# =========================================================
# AtomicWriteError Tests
# =========================================================


class TestAtomicWriteError:

    def test_default_values(self):
        err = AtomicWriteError()

        entry = err.entry

        assert entry.error_type == "AtomicWriteError"
        assert entry.operation == Operation.SAVE
        assert entry.retryability == Retryability.RETRYABLE
        assert entry.severity == Severity.ERROR
        assert entry.component == Component.JSON_STORE

    def test_default_remediation(self):
        err = AtomicWriteError()

        assert (
            err.entry.remediation
            == "Retry the write operation after verifying file lock availability."
        )

    def test_custom_message(self):
        err = AtomicWriteError("Custom atomic write message")

        assert err.entry.message == "Custom atomic write message"

    def test_is_exception(self):
        err = AtomicWriteError()

        assert isinstance(err, Exception)


# =========================================================
# ActionNotFoundError Tests
# =========================================================


class TestActionNotFoundError:

    def test_default_values(self):
        err = ActionNotFoundError()

        entry = err.entry

        assert entry.error_type == "ActionNotFoundError"
        assert entry.operation == Operation.SAVE
        assert entry.retryability == Retryability.NOT_RETRYABLE
        assert entry.severity == Severity.ERROR
        assert entry.component == Component.JSON_STORE

    def test_default_remediation(self):
        err = ActionNotFoundError()

        assert (
            err.entry.remediation
            == "Verify the action exists in persistence before attempting an update."
        )

    def test_custom_message(self):
        err = ActionNotFoundError("Custom action missing message")

        assert err.entry.message == "Custom action missing message"

    def test_action_id_propagates(self):
        err = ActionNotFoundError(action_id="ACTION-123")

        assert err.entry.action_id == "ACTION-123"

    def test_is_exception(self):
        err = ActionNotFoundError()

        assert isinstance(err, Exception)
