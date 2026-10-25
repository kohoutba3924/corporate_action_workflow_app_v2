# src/corporate_action_workflow_app_v2/persistence/json_store.py

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from corporate_action_workflow_app_v2.models.corporate_actions import CorporateAction
from corporate_action_workflow_app_v2.persistence.persistence_errors import (
    ActionNotFoundError,
    AtomicWriteError,
    CorruptionError,
)
from corporate_action_workflow_app_v2.persistence.persistence_logger import (
    PersistenceLogger,
)
from corporate_action_workflow_app_v2.semantic import (
    AgenticContext,
    Component,
    IntrospectionEvent,
    Operation,
    Retryability,
    Severity,
)


class JsonStore:
    """
    Agentic-ready persistence store that emits structured semantic logs,
    errors, and introspection events. This module does NOT write logs to
    any sink. Higher layers decide where semantic signals go.
    """

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.logger = PersistenceLogger()

        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        if not self.filepath.exists():
            self.filepath.write_text("[]")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_raw(self) -> AgenticContext:
        start = time.perf_counter()

        try:
            with self.filepath.open("r") as f:
                raw = json.load(f)

            log = self.logger.log(
                "Loaded JSON store successfully.",
                severity=Severity.INFO,
                operation=Operation.LOAD,
                component=Component.JSON_STORE,
                retryability=Retryability.NOT_RETRYABLE,
                context={"filepath": str(self.filepath)},
            )

            introspection = IntrospectionEvent(
                operation=Operation.LOAD,
                component=Component.JSON_STORE,
                severity=Severity.INFO,
                duration_ms=int((time.perf_counter() - start) * 1000),
                context={"filepath": str(self.filepath)},
            )

            return AgenticContext(
                log=log,
                introspection=introspection,
                error=None,
                payload=raw,
            )

        except json.JSONDecodeError as exc:
            error = CorruptionError(
                context={"filepath": str(self.filepath), "exception": str(exc)}
            ).entry

            return AgenticContext(
                log=None,
                introspection=None,
                error=error,
            )

    def _save_raw(self, data: List[Dict[str, Any]]) -> AgenticContext:
        start = time.perf_counter()

        try:
            temp_path = self.filepath.with_suffix(".tmp")

            with temp_path.open("w") as f:
                json.dump(data, f, indent=2)

            temp_path.replace(self.filepath)

            log = self.logger.log(
                "Saved JSON store successfully.",
                severity=Severity.INFO,
                operation=Operation.SAVE,
                component=Component.JSON_STORE,
                retryability=Retryability.NOT_RETRYABLE,
                context={"filepath": str(self.filepath)},
            )

            introspection = IntrospectionEvent(
                operation=Operation.SAVE,
                component=Component.JSON_STORE,
                severity=Severity.INFO,
                duration_ms=int((time.perf_counter() - start) * 1000),
                context={"filepath": str(self.filepath)},
            )

            return AgenticContext(
                log=log,
                introspection=introspection,
                error=None,
                payload=data,
            )

        except Exception as exc:
            error = AtomicWriteError(
                context={"filepath": str(self.filepath), "exception": str(exc)}
            ).entry

            return AgenticContext(
                log=None,
                introspection=None,
                error=error,
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_all(self) -> AgenticContext:
        ctx = self._load_raw()

        if ctx.error:
            return ctx

        raw = ctx.payload
        actions = [CorporateAction.from_dict(item) for item in raw]

        # Add domain objects to context for agentic reasoning
        if ctx.log is not None:
            if ctx.log.context is None:
                ctx.log.context = {}

            ctx.log.context["actions_loaded"] = len(actions)

        # Replace raw payload with deserialized domain objects
        ctx.payload = actions

        return ctx

    def save_all(self, actions: List[CorporateAction]) -> AgenticContext:
        raw = [a.to_dict() for a in actions]
        return self._save_raw(raw)

    def append(self, action: CorporateAction) -> AgenticContext:
        load_ctx = self._load_raw()

        if load_ctx.error:
            return load_ctx

        raw = load_ctx.payload
        raw.append(action.to_dict())

        return self._save_raw(raw)

    def update(self, action: CorporateAction) -> AgenticContext:
        load_ctx = self._load_raw()

        if load_ctx.error:
            return load_ctx

        raw = load_ctx.payload
        found = False

        for idx, item in enumerate(raw):
            if item.get("action_id") == action.action_id:
                raw[idx] = action.to_dict()
                found = True
                break

        if not found:
            error = ActionNotFoundError(
                action_id=action.action_id,
                context={
                    "filepath": str(self.filepath),
                    "action_id": action.action_id,
                },
            ).entry

            return AgenticContext(
                log=None,
                introspection=None,
                error=error,
            )

        return self._save_raw(raw)
