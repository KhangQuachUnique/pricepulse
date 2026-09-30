from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class PriceInputSchema(BaseModel):
    event_id: str = Field(
        min_length=1,
        description="Unique identifier for the price event",
    )
    product_id: str = Field(
        min_length=1, description="Unique identifier for the product"
    )
    seller_id: str = Field(
        min_length=1, description="Unique identifier for the seller"
    )
    observed_date: date = Field(
        description="Date when the price was observed"
    )
    version: int = Field(
        ge=1, description="Version of the price record"
    )
    price_vnd: int = Field(
        ge=0, description="Price in Vietnamese Dong"
    )
    original_price_vnd: int = Field(
        ge=0, description="Original price in Vietnamese Dong"
    )
    stock_qty: int = Field(
        ge=0, description="Quantity of stock available"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the record was last updated"
    )
    currency: str = Field(
        ..., description="Currency code (e.g., VND)"
    )
    attributes_json: dict[str, Any] = Field(
        ..., description="Additional attributes in JSON format"
    )
