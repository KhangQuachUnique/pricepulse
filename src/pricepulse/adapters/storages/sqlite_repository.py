import json
import sqlite3
from collections.abc import Sequence
from pathlib import Path

from pricepulse.domain.price import PriceRecord
from pricepulse.ports.price_repository import (
    BatchSaveResult,
)


class SQLitePriceRepository:
    def __init__(self, db_path: Path):
        self._connection = sqlite3.connect(db_path)

    def initialize(self) -> None:
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS price_records (
                event_id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                seller_id TEXT NOT NULL,
                observed_date TEXT NOT NULL,
                version INTEGER NOT NULL,
                price_vnd INTEGER NOT NULL,
                original_price_vnd INTEGER NOT NULL,
                stock_qty INTEGER NOT NULL,
                updated_at TEXT NOT NULL,
                currency TEXT NOT NULL,
                attributes_json TEXT NOT NULL
            )
            """
        )
        self._connection.commit()

    def save_batch(
        self, records: Sequence[PriceRecord]
    ) -> BatchSaveResult:
        inserted = 0
        duplicates = 0

        try:
            self._connection.execute("BEGIN")

            for record in records:
                cursor = self._connection.execute(
                    """
                    INSERT INTO price_records (
                        event_id,
                        product_id,
                        seller_id,
                        observed_date,
                        version,
                        price_vnd,
                        original_price_vnd,
                        stock_qty,
                        updated_at,
                        currency,
                        attributes_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(event_id) DO NOTHING
                    """,
                    (
                        record.event_id,
                        record.product_id,
                        record.seller_id,
                        record.observed_date.isoformat(),
                        record.version,
                        record.price_vnd,
                        record.original_price_vnd,
                        record.stock_qty,
                        record.updated_at.isoformat(),
                        record.currency,
                        json.dumps(record.attributes_json),
                    ),
                )

                if cursor.rowcount == 0:
                    duplicates += 1
                else:
                    inserted += 1

            self._connection.commit()

        except Exception:
            self._connection.rollback()
            raise

        return BatchSaveResult(
            inserted=inserted, duplicates=duplicates
        )

    def close(self) -> None:
        self._connection.close()
