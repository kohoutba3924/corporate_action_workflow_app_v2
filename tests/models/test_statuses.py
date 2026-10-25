# tests/models/test_statuses.py

import pytest

from corporate_action_workflow_app_v2.models.statuses import CorporateActionStatus


def test_status_enum_members_exist():
    """Ensure all expected status members are present."""
    expected = {
        "RECEIVED",
        "VALIDATED",
        "PROCESSING",
        "COMPLETED",
        "FAILED",
        "DEAD_LETTER",
        "RETRY_PENDING",
    }
    actual = {status.name for status in CorporateActionStatus}
    assert actual == expected


def test_status_enum_values_match_names():
    """Ensure each enum value matches its name (string identity)."""
    for status in CorporateActionStatus:
        assert status.value == status.name


def test_status_lookup_by_name():
    """Ensure enum lookup by name works (used in persistence)."""
    assert CorporateActionStatus["RECEIVED"] is CorporateActionStatus.RECEIVED
    assert CorporateActionStatus["FAILED"] is CorporateActionStatus.FAILED


def test_status_round_trip_serialization():
    """Ensure name/value round-trip works (critical for persistence)."""
    for status in CorporateActionStatus:
        serialized = status.name
        deserialized = CorporateActionStatus[serialized]
        assert deserialized is status
