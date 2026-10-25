# src/corporate_action_workflow_app_v2/semantic/enums.py

from enum import Enum


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Operation(str, Enum):
    LOAD = "LOAD"
    SAVE = "SAVE"
    VALIDATE = "VALIDATE"
    PROCESS = "PROCESS"
    RETRY = "RETRY"
    LOCK = "LOCK"
    CORRUPTION = "CORRUPTION"
    WORKFLOW = "WORKFLOW"


class Component(str, Enum):
    JSON_STORE = "JSON_STORE"
    VALIDATOR = "VALIDATOR"
    PROCESSOR = "PROCESSOR"
    ORCHESTRATOR = "ORCHESTRATOR"
    METADATA = "METADATA"
    CORPORATE_ACTION = "CORPORATE_ACTION"


class Retryability(str, Enum):
    RETRYABLE = "RETRYABLE"
    NOT_RETRYABLE = "NOT_RETRYABLE"
