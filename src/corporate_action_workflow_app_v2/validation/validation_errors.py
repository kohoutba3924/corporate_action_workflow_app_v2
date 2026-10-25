# src/corporate_action_workflow_app_v2/validation/validation_errors.py


class DomainError(Exception):
    """
    Base class for all domain-level validation errors.
    These errors represent semantic issues, not structural ones.
    """

    pass


class MetadataValidationError(DomainError):
    """
    Raised when metadata is structurally valid (Pydantic) but semantically invalid.
    Example: dividend_type is valid literal but violates a business rule.
    """

    def __init__(self, field: str, message: str, action_type: str):
        super().__init__(message)
        self.field = field
        self.message = message
        self.action_type = action_type


class BusinessRuleValidationError(DomainError):
    """
    Raised when a corporate action violates a business rule.
    Example: split ratio is valid but violates a corporate policy.
    """

    def __init__(self, message: str, action_type: str):
        super().__init__(message)
        self.message = message
        self.action_type = action_type


class WorkflowValidationError(DomainError):
    """
    Raised when a corporate action cannot proceed in the workflow.
    Example: attempting to process an action that is still in RECEIVED status.
    """

    def __init__(self, message: str, current_status: str):
        super().__init__(message)
        self.message = message
        self.current_status = current_status
