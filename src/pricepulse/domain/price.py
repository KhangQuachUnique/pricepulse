from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


@dataclass
class PriceRecord:
    event_id: str
    product_id: str
    seller_id: str
    observed_date: date
    version: int
    price_vnd: int
    original_price_vnd: int
    stock_qty: int
    updated_at: datetime
    currency: str
    attributes_json: dict[str, Any]
