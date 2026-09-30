from pricepulse.domain.price import PriceRecord

from .schema import PriceInputSchema


def to_price_record(schema: PriceInputSchema) -> PriceRecord:
    """
    Convert a PriceInputSchema instance to a PriceRecord domain model.
    """
    return PriceRecord(
        event_id=schema.event_id,
        product_id=schema.product_id,
        seller_id=schema.seller_id,
        observed_date=schema.observed_date,
        version=schema.version,
        price_vnd=schema.price_vnd,
        original_price_vnd=schema.original_price_vnd,
        stock_qty=schema.stock_qty,
        updated_at=schema.updated_at,
        currency=schema.currency,
        attributes_json=schema.attributes_json,
    )
