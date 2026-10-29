# src/corporate_action_workflow_app_v2/validation/validation_errors.py


class ValidationError(Exception):
    """
    Base class for validation-layer governance failures.

    Domain model validation is handled by the domain models
    themselves. These exceptions represent workflow and policy
    validation failures.
    """

    pass


class BusinessRuleValidationError(ValidationError):
    """
    Raised when an action violates an approved workflow policy
    or business rule.

    Examples:

    - Processor admission denied
    - Retry threshold exceeded
    - Readiness validation failure
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class WorkflowValidationError(ValidationError):
    """
    Raised when an invalid workflow state transition is attempted.

    Examples:

    - RECEIVED -> PROCESSING
    - COMPLETED -> PROCESSING
    - DEAD_LETTER -> VALIDATED
    """

    def __init__(
        self,
        message: str,
        current_status: str,
        target_status: str,
    ):
        super().__init__(message)

        self.message = message
        self.current_status = current_status
        self.target_status = target_status
