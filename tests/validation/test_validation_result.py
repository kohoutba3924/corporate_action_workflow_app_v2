# tests/validation/test_validation_result.py

from corporate_action_workflow_app_v2.validation.validation_result import (
    ValidationResult,
)


class TestValidationResult:

    def test_construct_success_result(self):
        result = ValidationResult(success=True)

        assert result.success is True
        assert result.error is None

    def test_success_result_not_failed(self):
        result = ValidationResult(success=True)

        assert result.failed() is False

    def test_construct_failed_result(self):
        error = ValueError("validation failed")

        result = ValidationResult(
            success=False,
            error=error,
        )

        assert result.success is False
        assert result.error is error

    def test_failed_result_returns_true(self):
        result = ValidationResult(success=False)

        assert result.failed() is True

    def test_preserves_error_instance(self):
        error = RuntimeError("workflow violation")

        result = ValidationResult(
            success=False,
            error=error,
        )

        assert result.error is error
