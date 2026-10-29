# tests/validation/test_workflow_validator.py

from datetime import date

from corporate_action_workflow_app_v2.models.corporate_actions import (
    CorporateAction,
)
from corporate_action_workflow_app_v2.models.metadata import (
    DividendMetadata,
    MetadataType,
)
from corporate_action_workflow_app_v2.models.statuses import (
    CorporateActionStatus,
)
from corporate_action_workflow_app_v2.validation.validation_errors import (
    BusinessRuleValidationError,
    WorkflowValidationError,
)
from corporate_action_workflow_app_v2.validation.workflow_validator import (
    WorkflowValidator,
)

# =========================================================
# Helpers
# =========================================================


def make_action() -> CorporateAction:
    metadata = MetadataType(
        root=DividendMetadata(
            amount=10.0,
            currency="USD",
            declaration_date=date(2024, 1, 1),
            record_date=date(2024, 1, 2),
            payable_date=date(2024, 1, 3),
        )
    )

    return CorporateAction(
        action_type="DIVIDEND",
        metadata=metadata,
    )


# =========================================================
# Transition Validation Tests
# =========================================================


class TestValidateTransition:

    def test_received_to_validated_allowed(self):
        result = WorkflowValidator.validate_transition(
            CorporateActionStatus.RECEIVED,
            CorporateActionStatus.VALIDATED,
        )

        assert result.success is True

    def test_received_to_dead_letter_allowed(self):
        result = WorkflowValidator.validate_transition(
            CorporateActionStatus.RECEIVED,
            CorporateActionStatus.DEAD_LETTER,
        )

        assert result.success is True

    def test_validated_to_processing_allowed(self):
        result = WorkflowValidator.validate_transition(
            CorporateActionStatus.VALIDATED,
            CorporateActionStatus.PROCESSING,
        )

        assert result.success is True

    def test_processing_to_completed_allowed(self):
        result = WorkflowValidator.validate_transition(
            CorporateActionStatus.PROCESSING,
            CorporateActionStatus.COMPLETED,
        )

        assert result.success is True

    def test_processing_to_failed_allowed(self):
        result = WorkflowValidator.validate_transition(
            CorporateActionStatus.PROCESSING,
            CorporateActionStatus.FAILED,
        )

        assert result.success is True

    def test_failed_to_retry_pending_allowed(self):
        result = WorkflowValidator.validate_transition(
            CorporateActionStatus.FAILED,
            CorporateActionStatus.RETRY_PENDING,
        )

        assert result.success is True

    def test_failed_to_dead_letter_allowed(self):
        result = WorkflowValidator.validate_transition(
            CorporateActionStatus.FAILED,
            CorporateActionStatus.DEAD_LETTER,
        )

        assert result.success is True

    def test_retry_pending_to_processing_allowed(self):
        result = WorkflowValidator.validate_transition(
            CorporateActionStatus.RETRY_PENDING,
            CorporateActionStatus.PROCESSING,
        )

        assert result.success is True

    def test_invalid_transition_rejected(self):
        result = WorkflowValidator.validate_transition(
            CorporateActionStatus.RECEIVED,
            CorporateActionStatus.PROCESSING,
        )

        assert result.failed()

        assert isinstance(
            result.error,
            WorkflowValidationError,
        )

        assert "RECEIVED" in result.error.message
        assert "PROCESSING" in result.error.message

    def test_terminal_state_transition_rejected(self):
        result = WorkflowValidator.validate_transition(
            CorporateActionStatus.COMPLETED,
            CorporateActionStatus.PROCESSING,
        )

        assert result.failed()

        assert isinstance(
            result.error,
            WorkflowValidationError,
        )


# =========================================================
# Readiness Validation Tests
# =========================================================


class TestValidateReadiness:

    def test_received_action_is_ready(self):
        action = make_action()

        result = WorkflowValidator.validate_readiness(action)

        assert result.success is True

    def test_validated_action_rejected(self):
        action = make_action()
        action.mark_validated()

        result = WorkflowValidator.validate_readiness(action)

        assert result.failed()

        assert isinstance(
            result.error,
            BusinessRuleValidationError,
        )

    def test_completed_action_rejected(self):
        action = make_action()
        action.mark_completed()

        result = WorkflowValidator.validate_readiness(action)

        assert result.failed()

        assert isinstance(
            result.error,
            BusinessRuleValidationError,
        )


# =========================================================
# Processor Admission Tests
# =========================================================


class TestValidateProcessorAdmission:

    def test_validated_action_admitted(self):
        action = make_action()
        action.mark_validated()

        result = WorkflowValidator.validate_processor_admission(action)

        assert result.success is True

    def test_retry_pending_action_admitted(self):
        action = make_action()
        action.mark_retry_pending()

        result = WorkflowValidator.validate_processor_admission(action)

        assert result.success is True

    def test_received_action_denied(self):
        action = make_action()

        result = WorkflowValidator.validate_processor_admission(action)

        assert result.failed()

        assert isinstance(
            result.error,
            BusinessRuleValidationError,
        )

    def test_dead_letter_action_denied(self):
        action = make_action()
        action.mark_dead_letter()

        result = WorkflowValidator.validate_processor_admission(action)

        assert result.failed()

        assert isinstance(
            result.error,
            BusinessRuleValidationError,
        )

    def test_completed_action_denied(self):
        action = make_action()
        action.mark_completed()

        result = WorkflowValidator.validate_processor_admission(action)

        assert result.failed()

        assert isinstance(
            result.error,
            BusinessRuleValidationError,
        )


# =========================================================
# Retry Validation Tests
# =========================================================


class TestValidateRetry:

    def test_failed_retry_count_zero_allowed(self):
        action = make_action()
        action.mark_failed()
        action.retry_count = 0

        result = WorkflowValidator.validate_retry(action)

        assert result.success is True

    def test_failed_retry_count_one_allowed(self):
        action = make_action()
        action.mark_failed()
        action.retry_count = 1

        result = WorkflowValidator.validate_retry(action)

        assert result.success is True

    def test_failed_retry_count_two_allowed(self):
        action = make_action()
        action.mark_failed()
        action.retry_count = 2

        result = WorkflowValidator.validate_retry(action)

        assert result.success is True

    def test_failed_retry_count_three_rejected(self):
        action = make_action()
        action.mark_failed()
        action.retry_count = 3

        result = WorkflowValidator.validate_retry(action)

        assert result.failed()

        assert isinstance(
            result.error,
            BusinessRuleValidationError,
        )

        assert "retry count" in result.error.message.lower()
        assert "DEAD_LETTER" in result.error.message

    def test_failed_retry_count_greater_than_three_rejected(self):
        action = make_action()
        action.mark_failed()
        action.retry_count = 4

        result = WorkflowValidator.validate_retry(action)

        assert result.failed()

        assert isinstance(
            result.error,
            BusinessRuleValidationError,
        )

    def test_non_failed_status_rejected(self):
        action = make_action()
        action.mark_validated()

        result = WorkflowValidator.validate_retry(action)

        assert result.failed()

        assert isinstance(
            result.error,
            BusinessRuleValidationError,
        )
