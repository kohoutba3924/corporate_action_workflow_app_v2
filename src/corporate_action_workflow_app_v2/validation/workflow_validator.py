# src/corporate_action_workflow_app_v2/validation/workflow_validator.py

from __future__ import annotations

from corporate_action_workflow_app_v2.models.corporate_actions import (
    CorporateAction,
)
from corporate_action_workflow_app_v2.models.statuses import (
    CorporateActionStatus,
)

from .validation_errors import (
    BusinessRuleValidationError,
    WorkflowValidationError,
)
from .validation_result import ValidationResult


class WorkflowValidator:
    """
    Enforces workflow governance policies.

    The validator does not mutate actions, perform persistence,
    or execute processing logic. It only evaluates whether
    workflow operations are permitted.
    """

    ALLOWED_TRANSITIONS = {
        (
            CorporateActionStatus.RECEIVED,
            CorporateActionStatus.VALIDATED,
        ),
        (
            CorporateActionStatus.RECEIVED,
            CorporateActionStatus.DEAD_LETTER,
        ),
        (
            CorporateActionStatus.VALIDATED,
            CorporateActionStatus.PROCESSING,
        ),
        (
            CorporateActionStatus.PROCESSING,
            CorporateActionStatus.COMPLETED,
        ),
        (
            CorporateActionStatus.PROCESSING,
            CorporateActionStatus.FAILED,
        ),
        (
            CorporateActionStatus.FAILED,
            CorporateActionStatus.RETRY_PENDING,
        ),
        (
            CorporateActionStatus.FAILED,
            CorporateActionStatus.DEAD_LETTER,
        ),
        (
            CorporateActionStatus.RETRY_PENDING,
            CorporateActionStatus.PROCESSING,
        ),
    }

    MAX_RETRIES = 3

    @staticmethod
    def validate_transition(
        current_status: CorporateActionStatus,
        target_status: CorporateActionStatus,
    ) -> ValidationResult:
        """
        Validate workflow state transitions against the
        Workflow State Transition Policy.
        """

        if (
            current_status,
            target_status,
        ) in WorkflowValidator.ALLOWED_TRANSITIONS:
            return ValidationResult(success=True)

        return ValidationResult(
            success=False,
            error=WorkflowValidationError(
                message=(
                    "Workflow transition rejected. "
                    f"Observed transition: "
                    f"{current_status.name} -> {target_status.name}. "
                    "The requested transition is not permitted by the "
                    "Workflow State Transition Policy."
                ),
                current_status=current_status.name,
                target_status=target_status.name,
            ),
        )

    @staticmethod
    def validate_readiness(
        action: CorporateAction,
    ) -> ValidationResult:
        """
        Validate Processing Readiness Policy.

        An action is considered ready for validation only
        when it exists as a valid CorporateAction and is
        currently in RECEIVED status.
        """

        if action.status == CorporateActionStatus.RECEIVED:
            return ValidationResult(success=True)

        return ValidationResult(
            success=False,
            error=BusinessRuleValidationError(
                (
                    "Processing readiness validation rejected. "
                    f"Observed status: {action.status.name}. "
                    "Expected status: RECEIVED. "
                    "Only actions in RECEIVED status may undergo "
                    "readiness validation."
                )
            ),
        )

    @staticmethod
    def validate_processor_admission(
        action: CorporateAction,
    ) -> ValidationResult:
        """
        Validate Processor Admission Policy.

        Only VALIDATED and RETRY_PENDING actions are eligible
        for processor pickup.
        """

        if action.status in {
            CorporateActionStatus.VALIDATED,
            CorporateActionStatus.RETRY_PENDING,
        }:
            return ValidationResult(success=True)

        return ValidationResult(
            success=False,
            error=BusinessRuleValidationError(
                (
                    "Processor admission denied. "
                    f"Observed status: {action.status.name}. "
                    "Expected status: VALIDATED or RETRY_PENDING. "
                    "Only actions approved for execution may be "
                    "admitted for processor pickup."
                )
            ),
        )

    @staticmethod
    def validate_retry(
        action: CorporateAction,
    ) -> ValidationResult:
        """
        Validate Retry Policy.

        Retries are only permitted for actions currently in
        FAILED status that have not exceeded the configured
        retry threshold.
        """

        if action.status != CorporateActionStatus.FAILED:
            return ValidationResult(
                success=False,
                error=BusinessRuleValidationError(
                    (
                        "Retry validation rejected. "
                        f"Observed status: {action.status.name}. "
                        "Expected status: FAILED. "
                        "Only failed actions are eligible for retry "
                        "evaluation."
                    )
                ),
            )

        if action.retry_count >= WorkflowValidator.MAX_RETRIES:
            return ValidationResult(
                success=False,
                error=BusinessRuleValidationError(
                    (
                        "Retry validation rejected. "
                        f"Observed retry count: {action.retry_count}. "
                        f"Maximum retry count: "
                        f"{WorkflowValidator.MAX_RETRIES}. "
                        "The action exceeded the Retry Policy threshold "
                        "and must transition to DEAD_LETTER."
                    )
                ),
            )

        return ValidationResult(success=True)
