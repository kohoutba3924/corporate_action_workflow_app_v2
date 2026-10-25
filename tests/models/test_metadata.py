import pytest
from datetime import date

from corporate_action_workflow_app_v2.models.metadata import (
    DividendMetadata,
    SplitMetadata,
    MergerMetadata,
    MetadataType,
)

# =========================================================
# DividendMetadata Tests
# =========================================================


class TestDividendMetadata:

    def test_valid_dividend_metadata(self):
        dm = DividendMetadata(
            amount=10.5,
            currency="USD",
            declaration_date=date(2024, 1, 1),
            record_date=date(2024, 1, 2),
            payable_date=date(2024, 1, 3),
            dividend_type="CASH",
            tax_withholding_rate=0.15,
        )
        assert dm.metadata_type == "DIVIDEND"
        assert dm.amount == 10.5

    # ----- amount -----

    def test_amount_must_be_positive(self):
        with pytest.raises(ValueError):
            DividendMetadata(
                amount=-1,
                currency="USD",
                declaration_date=date(2024, 1, 1),
                record_date=date(2024, 1, 2),
                payable_date=date(2024, 1, 3),
            )

    def test_amount_cannot_be_zero(self):
        with pytest.raises(ValueError):
            DividendMetadata(
                amount=0,
                currency="USD",
                declaration_date=date(2024, 1, 1),
                record_date=date(2024, 1, 2),
                payable_date=date(2024, 1, 3),
            )

    def test_amount_rejects_non_numeric(self):
        with pytest.raises(Exception):
            DividendMetadata(
                amount="abc",
                currency="USD",
                declaration_date=date(2024, 1, 1),
                record_date=date(2024, 1, 2),
                payable_date=date(2024, 1, 3),
            )

    # ----- currency -----

    def test_currency_must_be_exactly_three_characters(self):
        with pytest.raises(ValueError):
            DividendMetadata(
                amount=10,
                currency="US",
                declaration_date=date(2024, 1, 1),
                record_date=date(2024, 1, 2),
                payable_date=date(2024, 1, 3),
            )
        with pytest.raises(ValueError):
            DividendMetadata(
                amount=10,
                currency="USDD",
                declaration_date=date(2024, 1, 1),
                record_date=date(2024, 1, 2),
                payable_date=date(2024, 1, 3),
            )

    # ----- date invariants -----

    def test_record_date_must_be_after_or_equal_declaration_date(self):
        with pytest.raises(ValueError):
            DividendMetadata(
                amount=10,
                currency="USD",
                declaration_date=date(2024, 1, 2),
                record_date=date(2024, 1, 1),
                payable_date=date(2024, 1, 3),
            )

    def test_payable_date_must_be_after_or_equal_record_date(self):
        with pytest.raises(ValueError):
            DividendMetadata(
                amount=10,
                currency="USD",
                declaration_date=date(2024, 1, 1),
                record_date=date(2024, 1, 2),
                payable_date=date(2024, 1, 1),
            )

    # ----- tax_withholding_rate -----

    def test_tax_withholding_rate_must_be_between_0_and_1(self):
        with pytest.raises(ValueError):
            DividendMetadata(
                amount=10,
                currency="USD",
                declaration_date=date(2024, 1, 1),
                record_date=date(2024, 1, 2),
                payable_date=date(2024, 1, 3),
                tax_withholding_rate=-0.1,
            )
        with pytest.raises(ValueError):
            DividendMetadata(
                amount=10,
                currency="USD",
                declaration_date=date(2024, 1, 1),
                record_date=date(2024, 1, 2),
                payable_date=date(2024, 1, 3),
                tax_withholding_rate=1.1,
            )

    # ----- serialization -----

    def test_dividend_metadata_round_trip(self):
        dm = DividendMetadata(
            amount=10.5,
            currency="USD",
            declaration_date=date(2024, 1, 1),
            record_date=date(2024, 1, 2),
            payable_date=date(2024, 1, 3),
            dividend_type="CASH",
        )
        dumped = dm.model_dump()
        restored = DividendMetadata.model_validate(dumped)
        assert restored == dm


# =========================================================
# SplitMetadata Tests
# =========================================================


class TestSplitMetadata:

    def test_valid_split_metadata(self):
        sm = SplitMetadata(
            split_ratio="2:1",
            effective_date=date(2024, 1, 2),
            announcement_date=date(2024, 1, 1),
            fractional_shares_policy="ROUND_UP",
        )
        assert sm.metadata_type == "SPLIT"

    # ----- split_ratio -----

    def test_split_ratio_requires_colon(self):
        with pytest.raises(ValueError):
            SplitMetadata(
                split_ratio="21",
                effective_date=date(2024, 1, 2),
                announcement_date=date(2024, 1, 1),
                fractional_shares_policy="ROUND_UP",
            )

    def test_split_ratio_requires_two_integers(self):
        with pytest.raises(ValueError):
            SplitMetadata(
                split_ratio="A:B",
                effective_date=date(2024, 1, 2),
                announcement_date=date(2024, 1, 1),
                fractional_shares_policy="ROUND_UP",
            )

    def test_split_ratio_denominator_cannot_be_zero(self):
        with pytest.raises(ValueError):
            SplitMetadata(
                split_ratio="2:0",
                effective_date=date(2024, 1, 2),
                announcement_date=date(2024, 1, 1),
                fractional_shares_policy="ROUND_UP",
            )

    # ----- date invariants -----

    def test_effective_date_must_be_after_or_equal_announcement_date(self):
        with pytest.raises(ValueError):
            SplitMetadata(
                split_ratio="2:1",
                effective_date=date(2024, 1, 1),
                announcement_date=date(2024, 1, 2),
                fractional_shares_policy="ROUND_UP",
            )

    # ----- fractional_shares_policy -----

    def test_fractional_shares_policy_literal(self):
        with pytest.raises(ValueError):
            SplitMetadata(
                split_ratio="2:1",
                effective_date=date(2024, 1, 2),
                announcement_date=date(2024, 1, 1),
                fractional_shares_policy="INVALID",
            )

    # ----- serialization -----

    def test_split_metadata_round_trip(self):
        sm = SplitMetadata(
            split_ratio="2:1",
            effective_date=date(2024, 1, 2),
            announcement_date=date(2024, 1, 1),
            fractional_shares_policy="ROUND_UP",
        )
        dumped = sm.model_dump()
        restored = SplitMetadata.model_validate(dumped)
        assert restored == sm


# =========================================================
# MergerMetadata Tests
# =========================================================


class TestMergerMetadata:

    def test_valid_merger_metadata(self):
        mm = MergerMetadata(
            acquiring_company="A",
            acquired_company="B",
            merger_type="ABSORPTION",
            effective_date=date(2024, 1, 2),
            announcement_date=date(2024, 1, 1),
            exchange_ratio=1.5,
        )
        assert mm.metadata_type == "MERGER"

    # ----- merger_type -----

    def test_merger_type_literal(self):
        with pytest.raises(ValueError):
            MergerMetadata(
                acquiring_company="A",
                acquired_company="B",
                merger_type="INVALID",
                effective_date=date(2024, 1, 2),
                announcement_date=date(2024, 1, 1),
                exchange_ratio=1.5,
            )

    # ----- date invariants -----

    def test_effective_date_must_be_after_or_equal_announcement_date(self):
        with pytest.raises(ValueError):
            MergerMetadata(
                acquiring_company="A",
                acquired_company="B",
                merger_type="ABSORPTION",
                effective_date=date(2024, 1, 1),
                announcement_date=date(2024, 1, 2),
                exchange_ratio=1.5,
            )

    # ----- consideration invariants -----

    def test_at_least_one_consideration_required(self):
        with pytest.raises(ValueError):
            MergerMetadata(
                acquiring_company="A",
                acquired_company="B",
                merger_type="ABSORPTION",
                effective_date=date(2024, 1, 2),
                announcement_date=date(2024, 1, 1),
                exchange_ratio=None,
                cash_component=None,
                stock_component=None,
            )

    def test_exchange_ratio_must_be_positive_if_provided(self):
        with pytest.raises(ValueError):
            MergerMetadata(
                acquiring_company="A",
                acquired_company="B",
                merger_type="ABSORPTION",
                effective_date=date(2024, 1, 2),
                announcement_date=date(2024, 1, 1),
                exchange_ratio=-1,
            )

    # ----- serialization -----

    def test_merger_metadata_round_trip(self):
        mm = MergerMetadata(
            acquiring_company="A",
            acquired_company="B",
            merger_type="ABSORPTION",
            effective_date=date(2024, 1, 2),
            announcement_date=date(2024, 1, 1),
            exchange_ratio=1.5,
        )
        dumped = mm.model_dump()
        restored = MergerMetadata.model_validate(dumped)
        assert restored == mm


# =========================================================
# MetadataType Union Tests
# =========================================================


class TestMetadataTypeUnion:

    def test_union_routing_dividend(self):
        data = {
            "metadata_type": "DIVIDEND",
            "amount": 10,
            "currency": "USD",
            "declaration_date": "2024-01-01",
            "record_date": "2024-01-02",
            "payable_date": "2024-01-03",
        }
        obj = MetadataType.model_validate(data).root
        assert isinstance(obj, DividendMetadata)

    def test_union_routing_split(self):
        data = {
            "metadata_type": "SPLIT",
            "split_ratio": "2:1",
            "effective_date": "2024-01-02",
            "announcement_date": "2024-01-01",
            "fractional_shares_policy": "ROUND_UP",
        }
        obj = MetadataType.model_validate(data).root
        assert isinstance(obj, SplitMetadata)

    def test_union_routing_merger(self):
        data = {
            "metadata_type": "MERGER",
            "acquiring_company": "A",
            "acquired_company": "B",
            "merger_type": "ABSORPTION",
            "effective_date": "2024-01-02",
            "announcement_date": "2024-01-01",
            "exchange_ratio": 1.5,
        }
        obj = MetadataType.model_validate(data).root
        assert isinstance(obj, MergerMetadata)

    def test_invalid_metadata_type(self):
        data = {"metadata_type": "UNKNOWN"}
        with pytest.raises(Exception):
            MetadataType.model_validate(data)

    def test_union_round_trip(self):
        dm = DividendMetadata(
            amount=10,
            currency="USD",
            declaration_date=date(2024, 1, 1),
            record_date=date(2024, 1, 2),
            payable_date=date(2024, 1, 3),
        )
        dumped = dm.model_dump()
        restored = MetadataType.model_validate(dumped).root
        assert isinstance(restored, DividendMetadata)
        assert restored == dm
