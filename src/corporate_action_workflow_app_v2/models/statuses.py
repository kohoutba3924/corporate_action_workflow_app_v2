# src/corporate_action_workflow_app_v2/models/statuses.py

from enum import Enum


class CorporateActionStatus(Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DEAD_LETTER = "DEAD_LETTER"
    RETRY_PENDING = "RETRY_PENDING"
