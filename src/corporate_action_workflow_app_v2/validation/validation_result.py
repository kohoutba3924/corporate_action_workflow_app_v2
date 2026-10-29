# src/corporate_action_workflow_app_v2/validation/validation_result.py

from __future__ import annotations

from typing import Optional


class ValidationResult:
    """
    Standard validation response.

    Validation modules return ValidationResult instances
    rather than raising exceptions for expected policy decisions.
    """

    def __init__(
        self,
        success: bool,
        error: Optional[Exception] = None,
    ):
        self.success = success
        self.error = error

    def failed(self) -> bool:
        return not self.success
