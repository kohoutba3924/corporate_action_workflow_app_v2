# src/corporate_action_workflow_app_v2/models/corporate_action.py

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Set

from pydantic import BaseModel, Field, field_validator

from .metadata import (
    DividendMetadata,
    MergerMetadata,
    MetadataType,
    SplitMetadata,
)
from .statuses import CorporateActionStatus


# ---------------------------------------------------------
# Metadata factory using discriminator
# ---------------------------------------------------------
def parse_metadata(data: Dict[str, Any]) -> MetadataType:
    """
    Deserialize metadata using the discriminator field `metadata_type`.
    """
    metadata_type = data.get("metadata_type")

    if metadata_type == "DIVIDEND":
        return MetadataType(root=DividendMetadata.model_validate(data))
    elif metadata_type == "SPLIT":
        return MetadataType(root=SplitMetadata.model_validate(data))
    elif metadata_type == "MERGER":
        return MetadataType(root=MergerMetadata.model_validate(data))

    raise ValueError(
        f"Unknown metadata_type '{metadata_type}'. "
        "Expected one of: DIVIDEND, SPLIT, MERGER."
    )


class CorporateAction(BaseModel):
    """
    Core domain model for a corporate action & domain level validation.
    """

    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str
    metadata: MetadataType
    status: CorporateActionStatus = CorporateActionStatus.RECEIVED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Allowed corporate action types (domain rule)
    ALLOWED_ACTION_TYPES: ClassVar[Set[str]] = {"DIVIDEND", "MERGER", "SPLIT"}

    # ---------------------------------------------------------
    # Status transitions
    # ---------------------------------------------------------
    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    def mark_validated(self) -> None:
        self.status = CorporateActionStatus.VALIDATED
        self._touch()

    def mark_processing(self) -> None:
        self.status = CorporateActionStatus.PROCESSING
        self._touch()

    def mark_completed(self) -> None:
        self.status = CorporateActionStatus.COMPLETED
        self._touch()

    def mark_failed(self) -> None:
        self.status = CorporateActionStatus.FAILED
        self._touch()

    def mark_dead_letter(self) -> None:
        self.status = CorporateActionStatus.DEAD_LETTER
        self._touch()

    def mark_retry_pending(self) -> None:
        self.status = CorporateActionStatus.RETRY_PENDING
        self._touch()

    # ---------------------------------------------------------
    # Domain validation
    # ---------------------------------------------------------
    @field_validator("action_type")
    def validate_action_type(cls, v: str) -> str:
        if not v:
            raise ValueError("action_type is required")

        if v.upper() not in cls.ALLOWED_ACTION_TYPES:
            allowed = ", ".join(cls.ALLOWED_ACTION_TYPES)
            raise ValueError(f"Invalid action_type '{v}'. Allowed types: {allowed}")
        return v

    @field_validator("metadata", mode="after")
    def ensure_action_type_matches_metadata(cls, v, info):
        action_type = info.data.get("action_type")
        if action_type is None:
            return v

        # Normalize action_type for comparison
        action_type = action_type.upper()

        # Extract metadata_type from the root model
        metadata_type = v.root.metadata_type

        if action_type != metadata_type:
            raise ValueError(
                f"action_type '{action_type}' does not match metadata.metadata_type '{metadata_type}'"
            )

        return v

    # ---------------------------------------------------------
    # Serialization / Deserialization
    # ---------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "metadata": self.metadata.model_dump(mode="json"),
            "status": self.status.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CorporateAction":
        return cls(
            action_id=data["action_id"],
            action_type=data["action_type"],
            metadata=parse_metadata(data["metadata"]),
            status=CorporateActionStatus[data["status"]],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
