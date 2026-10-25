# src/corporate_action_workflow_app_v2/models/metadata.py

from datetime import date
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, RootModel, field_validator


# ---------------------------------------------------------
# Dividend Metadata
# ---------------------------------------------------------
class DividendMetadata(BaseModel):
    metadata_type: Literal["DIVIDEND"] = "DIVIDEND"

    amount: float = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    declaration_date: date
    record_date: date
    payable_date: date
    dividend_type: Literal["CASH", "STOCK"] = "CASH"
    tax_withholding_rate: float | None = Field(default=None, ge=0, le=1)

    @field_validator("record_date", mode="after")
    def record_date_after_declaration(cls, v, info):
        decl = info.data.get("declaration_date")
        if decl and v < decl:
            raise ValueError("record_date must be >= declaration_date")
        return v

    @field_validator("payable_date", mode="after")
    def payable_date_after_record(cls, v, info):
        rec = info.data.get("record_date")
        if rec and v < rec:
            raise ValueError("payable_date must be >= record_date")
        return v


# ---------------------------------------------------------
# Split Metadata
# ---------------------------------------------------------
class SplitMetadata(BaseModel):
    metadata_type: Literal["SPLIT"] = "SPLIT"

    split_ratio: str
    announcement_date: date
    effective_date: date
    fractional_shares_policy: Literal["ROUND_UP", "ROUND_DOWN", "CASH_IN_LIEU"]

    @field_validator("split_ratio")
    def validate_ratio(cls, v):
        if ":" not in v:
            raise ValueError("split_ratio must be in 'A:B' format")
        try:
            num, den = v.split(":")
            num = int(num)
            den = int(den)
            if den == 0:
                raise ValueError("split_ratio denominator cannot be zero")
        except Exception:
            raise ValueError("split_ratio must contain two integers, e.g. '2:1'")
        return v

    @field_validator("effective_date", mode="after")
    def effective_after_announcement(cls, v, info):
        ann = info.data.get("announcement_date")
        if ann and v < ann:
            raise ValueError("effective_date must be >= announcement_date")
        return v


# ---------------------------------------------------------
# Merger Metadata
# ---------------------------------------------------------
class MergerMetadata(BaseModel):
    metadata_type: Literal["MERGER"] = "MERGER"

    acquiring_company: str
    acquired_company: str
    merger_type: Literal["ABSORPTION", "CONSOLIDATION"]
    announcement_date: date
    effective_date: date
    exchange_ratio: float | None = Field(default=None, gt=0)
    cash_component: float | None = Field(default=None, ge=0)
    stock_component: float | None = Field(default=None, ge=0)

    @field_validator("effective_date", mode="after")
    def effective_after_announcement(cls, v, info):
        ann = info.data.get("announcement_date")
        if ann and v < ann:
            raise ValueError("effective_date must be >= announcement_date")
        return v

    @field_validator("exchange_ratio", mode="before")
    def validate_consideration(cls, v, info):
        cash = info.data.get("cash_component")
        stock = info.data.get("stock_component")

        if v is None and cash is None and stock is None:
            raise ValueError(
                "At least one of exchange_ratio, cash_component, or stock_component must be provided"
            )
        return v


# ---------------------------------------------------------
# Discriminated Union Type for Metadata (Correct Pydantic v2)
# ---------------------------------------------------------

MetadataUnion = Annotated[
    Union[DividendMetadata, SplitMetadata, MergerMetadata],
    Field(discriminator="metadata_type"),
]


class MetadataType(RootModel[MetadataUnion]):
    pass
