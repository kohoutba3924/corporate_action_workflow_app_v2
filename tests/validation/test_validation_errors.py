# tests/validation/test_validation_errors.py

from corporate_action_workflow_app_v2.validation.validation_errors import (
    BusinessRuleValidationError,
    ValidationError,
    WorkflowValidationError,
)

# =========================================================
# ValidationError Tests
# =========================================================


class TestValidationError:

    def test_construct_validation_error(self):
        err = ValidationError("Validation failed.")

        assert str(err) == "Validation failed."

    def test_is_exception(self):
        err = ValidationError("Validation failed.")

        assert isinstance(err, Exception)


# =========================================================
# BusinessRuleValidationError Tests
# =========================================================


class TestBusinessRuleValidationError:

    def test_construct_business_rule_validation_error(self):
        err = BusinessRuleValidationError("Processor admission denied.")

        assert err.message == "Processor admission denied."
        assert str(err) == "Processor admission denied."

    def test_is_validation_error(self):
        err = BusinessRuleValidationError("Processor admission denied.")

        assert isinstance(err, ValidationError)


# =========================================================
# WorkflowValidationError Tests
# =========================================================


class TestWorkflowValidationError:

    def test_construct_workflow_validation_error(self):
        err = WorkflowValidationError(
            message="Invalid transition.",
            current_status="RECEIVED",
            target_status="PROCESSING",
        )

        assert err.message == "Invalid transition."
        assert err.current_status == "RECEIVED"
        assert err.target_status == "PROCESSING"

    def test_preserves_message(self):
        err = WorkflowValidationError(
            message="Invalid transition.",
            current_status="RECEIVED",
            target_status="PROCESSING",
        )

        assert str(err) == "Invalid transition."

    def test_is_validation_error(self):
        err = WorkflowValidationError(
            message="Invalid transition.",
            current_status="RECEIVED",
            target_status="PROCESSING",
        )

        assert isinstance(err, ValidationError)
