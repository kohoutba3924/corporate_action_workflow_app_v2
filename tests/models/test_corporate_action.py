import pytest
from datetime import datetime, timezone, date

from corporate_action_workflow_app_v2.models.corporate_actions import (
    CorporateAction,
    parse_metadata,
)
from corporate_action_workflow_app_v2.models.metadata import (
    DividendMetadata,
    SplitMetadata,
    MergerMetadata,
    MetadataType,
)
from corporate_action_workflow_app_v2.models.statuses import CorporateActionStatus

# =========================================================
# Construction Tests
# =========================================================


class TestCorporateActionConstruction:

    def test_construct_dividend_action(self):
        md = MetadataType(
            root=DividendMetadata(
                amount=10,
                currency="USD",
                declaration_date=date(2024, 1, 1),
                record_date=date(2024, 1, 2),
                payable_date=date(2024, 1, 3),
            )
        )
        ca = CorporateAction(action_type="DIVIDEND", metadata=md)
        assert ca.action_type == "DIVIDEND"
        assert isinstance(ca.metadata, MetadataType)
        assert isinstance(ca.metadata.root, DividendMetadata)
        assert ca.status == CorporateActionStatus.RECEIVED
        assert isinstance(ca.action_id, str)
        assert isinstance(ca.created_at, datetime)
        assert isinstance(ca.updated_at, datetime)

    def test_construct_split_action(self):
        md = MetadataType(
            root=SplitMetadata(
                split_ratio="2:1",
                announcement_date=date(2024, 1, 1),
                effective_date=date(2024, 1, 2),
                fractional_shares_policy="ROUND_UP",
            )
        )
        ca = CorporateAction(action_type="SPLIT", metadata=md)
        assert isinstance(ca.metadata.root, SplitMetadata)

    def test_construct_merger_action(self):
        md = MetadataType(
            root=MergerMetadata(
                acquiring_company="A",
                acquired_company="B",
                merger_type="ABSORPTION",
                announcement_date=date(2024, 1, 1),
                effective_date=date(2024, 1, 2),
                exchange_ratio=1.5,
            )
        )
        ca = CorporateAction(action_type="MERGER", metadata=md)
        assert isinstance(ca.metadata.root, MergerMetadata)


# =========================================================
# Action Type Validation
# =========================================================


class TestActionTypeValidation:

    def test_valid_action_types(self):
        # DIVIDEND
        md_div = MetadataType(
            root=DividendMetadata(
                amount=10,
                currency="USD",
                declaration_date=date(2024, 1, 1),
                record_date=date(2024, 1, 2),
                payable_date=date(2024, 1, 3),
            )
        )
        ca = CorporateAction(action_type="DIVIDEND", metadata=md_div)
        assert ca.action_type == "DIVIDEND"

        # MERGER
        md_merger = MetadataType(
            root=MergerMetadata(
                acquiring_company="A",
                acquired_company="B",
                merger_type="ABSORPTION",
                announcement_date=date(2024, 1, 1),
                effective_date=date(2024, 1, 2),
                exchange_ratio=1.5,
            )
        )
        ca = CorporateAction(action_type="MERGER", metadata=md_merger)
        assert ca.action_type == "MERGER"

        # SPLIT
        md_split = MetadataType(
            root=SplitMetadata(
                split_ratio="2:1",
                announcement_date=date(2024, 1, 1),
                effective_date=date(2024, 1, 2),
                fractional_shares_policy="ROUND_UP",
            )
        )
        ca = CorporateAction(action_type="SPLIT", metadata=md_split)
        assert ca.action_type == "SPLIT"

    def test_lowercase_action_type_is_normalized(self):
        md = MetadataType(
            root=DividendMetadata(
                amount=10,
                currency="USD",
                declaration_date=date(2024, 1, 1),
                record_date=date(2024, 1, 2),
                payable_date=date(2024, 1, 3),
            )
        )
        ca = CorporateAction(action_type="dividend", metadata=md)
        assert ca.action_type == "dividend"

    def test_invalid_action_type(self):
        md = MetadataType(
            root=DividendMetadata(
                amount=10,
                currency="USD",
                declaration_date=date(2024, 1, 1),
                record_date=date(2024, 1, 2),
                payable_date=date(2024, 1, 3),
            )
        )
        with pytest.raises(ValueError):
            CorporateAction(action_type="BONUS", metadata=md)

    def test_missing_action_type(self):
        md = MetadataType(
            root=DividendMetadata(
                amount=10,
                currency="USD",
                declaration_date=date(2024, 1, 1),
                record_date=date(2024, 1, 2),
                payable_date=date(2024, 1, 3),
            )
        )
        with pytest.raises(ValueError):
            CorporateAction(action_type="", metadata=md)


# =========================================================
# Metadata Integration Tests
# =========================================================


class TestMetadataIntegration:

    def test_metadata_root_correct_type(self):
        md = MetadataType(
            root=DividendMetadata(
                amount=10,
                currency="USD",
                declaration_date=date(2024, 1, 1),
                record_date=date(2024, 1, 2),
                payable_date=date(2024, 1, 3),
            )
        )
        ca = CorporateAction(action_type="DIVIDEND", metadata=md)
        assert isinstance(ca.metadata.root, DividendMetadata)


# =========================================================
# Action Type ↔ Metadata Type Alignment Tests
# =========================================================


class TestActionTypeMetadataAlignment:

    def test_matching_action_type_and_metadata_type_passes(self):
        md = MetadataType(
            root=DividendMetadata(
                amount=10,
                currency="USD",
                declaration_date=date(2024, 1, 1),
                record_date=date(2024, 1, 2),
                payable_date=date(2024, 1, 3),
            )
        )
        ca = CorporateAction(action_type="DIVIDEND", metadata=md)
        assert isinstance(ca, CorporateAction)

    def test_mismatched_action_type_and_metadata_type_raises(self):
        # Dividend metadata but MERGER action_type
        md = MetadataType(
            root=DividendMetadata(
                amount=10,
                currency="USD",
                declaration_date=date(2024, 1, 1),
                record_date=date(2024, 1, 2),
                payable_date=date(2024, 1, 3),
            )
        )
        with pytest.raises(ValueError):
            CorporateAction(action_type="MERGER", metadata=md)

    def test_mismatched_split_metadata_raises(self):
        md = MetadataType(
            root=SplitMetadata(
                split_ratio="2:1",
                announcement_date=date(2024, 1, 1),
                effective_date=date(2024, 1, 2),
                fractional_shares_policy="ROUND_UP",
            )
        )
        with pytest.raises(ValueError):
            CorporateAction(action_type="DIVIDEND", metadata=md)

    def test_mismatched_merger_metadata_raises(self):
        md = MetadataType(
            root=MergerMetadata(
                acquiring_company="A",
                acquired_company="B",
                merger_type="ABSORPTION",
                announcement_date=date(2024, 1, 1),
                effective_date=date(2024, 1, 2),
                exchange_ratio=1.5,
            )
        )
        with pytest.raises(ValueError):
            CorporateAction(action_type="SPLIT", metadata=md)


# =========================================================
# parse_metadata() Tests
# =========================================================


class TestParseMetadata:

    def test_parse_dividend(self):
        data = {
            "metadata_type": "DIVIDEND",
            "amount": 10,
            "currency": "USD",
            "declaration_date": "2024-01-01",
            "record_date": "2024-01-02",
            "payable_date": "2024-01-03",
        }
        md = parse_metadata(data)
        assert isinstance(md.root, DividendMetadata)

    def test_parse_split(self):
        data = {
            "metadata_type": "SPLIT",
            "split_ratio": "2:1",
            "announcement_date": "2024-01-01",
            "effective_date": "2024-01-02",
            "fractional_shares_policy": "ROUND_UP",
        }
        md = parse_metadata(data)
        assert isinstance(md.root, SplitMetadata)

    def test_parse_merger(self):
        data = {
            "metadata_type": "MERGER",
            "acquiring_company": "A",
            "acquired_company": "B",
            "merger_type": "ABSORPTION",
            "announcement_date": "2024-01-01",
            "effective_date": "2024-01-02",
            "exchange_ratio": 1.5,
        }
        md = parse_metadata(data)
        assert isinstance(md.root, MergerMetadata)

    def test_parse_invalid_metadata_type(self):
        with pytest.raises(ValueError):
            parse_metadata({"metadata_type": "UNKNOWN"})


# =========================================================
# Serialization Tests
# =========================================================


class TestSerialization:

    def test_to_dict_round_trip(self):
        md = MetadataType(
            root=DividendMetadata(
                amount=10,
                currency="USD",
                declaration_date=date(2024, 1, 1),
                record_date=date(2024, 1, 2),
                payable_date=date(2024, 1, 3),
            )
        )
        ca = CorporateAction(action_type="DIVIDEND", metadata=md)
        d = ca.to_dict()

        restored = CorporateAction.from_dict(d)

        assert restored.action_id == ca.action_id
        assert restored.action_type == ca.action_type
        assert isinstance(restored.metadata.root, DividendMetadata)
        assert restored.status == ca.status
        assert restored.created_at == ca.created_at
        assert restored.updated_at == ca.updated_at


# =========================================================
# Status Transition Tests
# =========================================================


class TestStatusTransitions:

    def _make_action(self):
        md = MetadataType(
            root=DividendMetadata(
                amount=10,
                currency="USD",
                declaration_date=date(2024, 1, 1),
                record_date=date(2024, 1, 2),
                payable_date=date(2024, 1, 3),
            )
        )
        return CorporateAction(action_type="DIVIDEND", metadata=md)

    def test_mark_validated(self):
        ca = self._make_action()
        old = ca.updated_at
        ca.mark_validated()
        assert ca.status == CorporateActionStatus.VALIDATED
        assert ca.updated_at > old

    def test_mark_processing(self):
        ca = self._make_action()
        old = ca.updated_at
        ca.mark_processing()
        assert ca.status == CorporateActionStatus.PROCESSING
        assert ca.updated_at > old

    def test_mark_completed(self):
        ca = self._make_action()
        old = ca.updated_at
        ca.mark_completed()
        assert ca.status == CorporateActionStatus.COMPLETED
        assert ca.updated_at > old

    def test_mark_failed(self):
        ca = self._make_action()
        old = ca.updated_at
        ca.mark_failed()
        assert ca.status == CorporateActionStatus.FAILED
        assert ca.updated_at > old

    def test_mark_dead_letter(self):
        ca = self._make_action()
        old = ca.updated_at
        ca.mark_dead_letter()
        assert ca.status == CorporateActionStatus.DEAD_LETTER
        assert ca.updated_at > old

    def test_mark_retry_pending(self):
        ca = self._make_action()
        old = ca.updated_at
        ca.mark_retry_pending()
        assert ca.status == CorporateActionStatus.RETRY_PENDING
        assert ca.updated_at > old
