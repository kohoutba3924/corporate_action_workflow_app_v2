# src/corporate_action_workflow_app_v2/validation/domain_validator.py

from __future__ import annotations

from typing import Any, Optional

from pydantic import ValidationError as PydanticValidationError

from .validation_errors import (
    MetadataValidationError,
)


class ValidationResult:
    """
    Represents the outcome of validating a corporate action.
    Phase 1: structural + basic semantic error mapping.
    Phase 2+: workflow rules, business rules, agentic remediation.
    """

    def __init__(
        self,
        success: bool,
        error: Optional[Exception] = None,
        field: Optional[str] = None,
        action_type: Optional[str] = None,
    ):
        self.success = success
        self.error = error
        self.field = field
        self.action_type = action_type

    def failed(self) -> bool:
        return not self.success


class DomainValidator:
    """
    Phase 1 validator:
    - catches Pydantic structural errors
    - maps them into domain-level semantic errors
    - prepares ValidationResult objects

    Phase 2 will extend this with:
    - business rule validation
    - workflow validation
    - agentic remediation hints
    """

    @staticmethod
    def validate_metadata(action_type: str, metadata_model: Any) -> ValidationResult:
        """
        Validate metadata using Pydantic.
        Convert Pydantic errors into MetadataValidationError.
        """

        try:
            # If metadata_model is already a validated Pydantic model,
            # this does nothing. If it's raw input, Pydantic will validate it.
            metadata_model = (
                metadata_model
                if hasattr(metadata_model, "model_dump")
                else metadata_model()
            )
            return ValidationResult(success=True)

        except PydanticValidationError as e:
            # Extract the first error for Phase 1
            first = e.errors()[0]

            loc = first.get("loc", ["unknown"])
            field = ".".join(str(part) for part in loc)
            message = first.get("msg", "Invalid metadata")

            return ValidationResult(
                success=False,
                error=MetadataValidationError(
                    field=field,
                    message=message,
                    action_type=action_type,
                ),
                field=field,
                action_type=action_type,
            )

    @staticmethod
    def validate_business_rules(action: Any) -> ValidationResult:
        """
        Placeholder for Phase 2 business rule validation.
        Phase 1: always succeeds.
        """
        return ValidationResult(success=True)

    @staticmethod
    def validate_workflow(action: Any) -> ValidationResult:
        """
        Placeholder for Phase 2 workflow validation.
        Phase 1: always succeeds.
        """
        return ValidationResult(success=True)
