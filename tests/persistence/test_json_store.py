# tests/persistence/test_json_store.py

import json
from datetime import date
from unittest.mock import patch

from corporate_action_workflow_app_v2.models.corporate_actions import (
    CorporateAction,
)
from corporate_action_workflow_app_v2.models.metadata import (
    DividendMetadata,
    MetadataType,
)
from corporate_action_workflow_app_v2.models.statuses import (
    CorporateActionStatus,
)
from corporate_action_workflow_app_v2.persistence.json_store import JsonStore

# =========================================================
# Helpers
# =========================================================


def make_action() -> CorporateAction:
    metadata = MetadataType(
        root=DividendMetadata(
            amount=10.0,
            currency="USD",
            declaration_date=date(2024, 1, 1),
            record_date=date(2024, 1, 2),
            payable_date=date(2024, 1, 3),
        )
    )

    return CorporateAction(
        action_type="DIVIDEND",
        metadata=metadata,
    )


# =========================================================
# Initialization Tests
# =========================================================


class TestJsonStoreInitialization:

    def test_store_file_created(self, tmp_path):
        store_path = tmp_path / "actions.json"

        assert not store_path.exists()

        JsonStore(str(store_path))

        assert store_path.exists()
        assert json.loads(store_path.read_text()) == []

    def test_existing_store_preserved(self, tmp_path):
        store_path = tmp_path / "actions.json"

        original = [{"test": "value"}]
        store_path.write_text(json.dumps(original))

        JsonStore(str(store_path))

        assert json.loads(store_path.read_text()) == original


# =========================================================
# _load_raw Tests
# =========================================================


class TestLoadRaw:

    def test_load_raw_success(self, tmp_path):
        store_path = tmp_path / "actions.json"
        store_path.write_text(json.dumps([{"id": 1}]))

        store = JsonStore(str(store_path))

        ctx = store._load_raw()

        assert ctx.error is None
        assert ctx.log is not None
        assert ctx.introspection is not None
        assert ctx.payload == [{"id": 1}]

    def test_load_raw_corruption_error(self, tmp_path):
        store_path = tmp_path / "actions.json"
        store_path.write_text("{ invalid json")

        store = JsonStore(str(store_path))

        ctx = store._load_raw()

        assert ctx.error is not None
        assert ctx.error.error_type == "CorruptionError"
        assert ctx.log is None
        assert ctx.introspection is None


# =========================================================
# _save_raw Tests
# =========================================================


class TestSaveRaw:

    def test_save_raw_success(self, tmp_path):
        store_path = tmp_path / "actions.json"
        store = JsonStore(str(store_path))

        payload = [{"id": 1}]

        ctx = store._save_raw(payload)

        assert ctx.error is None
        assert ctx.log is not None
        assert ctx.introspection is not None
        assert ctx.payload == payload

        assert json.loads(store_path.read_text()) == payload

    def test_save_raw_atomic_write_error(self, tmp_path):
        store_path = tmp_path / "actions.json"
        store = JsonStore(str(store_path))

        with patch(
            "pathlib.Path.replace",
            side_effect=Exception("disk failure"),
        ):
            ctx = store._save_raw([{"id": 1}])

        assert ctx.error is not None
        assert ctx.error.error_type == "AtomicWriteError"
        assert ctx.log is None
        assert ctx.introspection is None


# =========================================================
# Public API Tests
# =========================================================


class TestPublicAPI:

    def test_save_all(self, tmp_path):
        store_path = tmp_path / "actions.json"
        store = JsonStore(str(store_path))

        action = make_action()

        ctx = store.save_all([action])

        assert ctx.error is None

        data = json.loads(store_path.read_text())
        assert len(data) == 1

    def test_load_all_returns_domain_objects(self, tmp_path):
        store_path = tmp_path / "actions.json"
        store = JsonStore(str(store_path))

        action = make_action()

        store.save_all([action])

        ctx = store.load_all()

        assert ctx.error is None

        payload = ctx.payload

        assert len(payload) == 1
        assert isinstance(payload[0], CorporateAction)

        assert ctx.log is not None
        assert ctx.log.context["actions_loaded"] == 1

    def test_append_single_action(self, tmp_path):
        store_path = tmp_path / "actions.json"
        store = JsonStore(str(store_path))

        store.append(make_action())

        ctx = store.load_all()

        assert len(ctx.payload) == 1

    def test_append_multiple_actions(self, tmp_path):
        store_path = tmp_path / "actions.json"
        store = JsonStore(str(store_path))

        store.append(make_action())
        store.append(make_action())

        ctx = store.load_all()

        assert len(ctx.payload) == 2

    def test_update_existing_action(self, tmp_path):
        store_path = tmp_path / "actions.json"
        store = JsonStore(str(store_path))

        action = make_action()

        store.save_all([action])

        action.mark_completed()

        update_ctx = store.update(action)

        assert update_ctx.error is None

        load_ctx = store.load_all()

        loaded_action = load_ctx.payload[0]

        assert loaded_action.status == CorporateActionStatus.COMPLETED

    def test_update_missing_action_returns_error(self, tmp_path):
        store_path = tmp_path / "actions.json"
        store = JsonStore(str(store_path))

        missing_action = make_action()

        ctx = store.update(missing_action)

        assert ctx.error is not None
        assert ctx.error.error_type == "ActionNotFoundError"

        assert ctx.log is None
        assert ctx.introspection is None


# =========================================================
# End-to-End Persistence Tests
# =========================================================


class TestPersistenceRoundTrip:

    def test_complete_persistence_lifecycle(self, tmp_path):
        store_path = tmp_path / "actions.json"
        store = JsonStore(str(store_path))

        action = make_action()

        save_ctx = store.save_all([action])
        assert save_ctx.error is None

        load_ctx = store.load_all()
        assert load_ctx.error is None

        loaded_action = load_ctx.payload[0]

        assert loaded_action.action_id == action.action_id

        loaded_action.mark_completed()

        update_ctx = store.update(loaded_action)
        assert update_ctx.error is None

        final_ctx = store.load_all()

        final_action = final_ctx.payload[0]

        assert final_action.action_id == action.action_id
        assert final_action.status == CorporateActionStatus.COMPLETED
        assert (
            final_action.metadata.root.metadata_type
            == action.metadata.root.metadata_type
        )
