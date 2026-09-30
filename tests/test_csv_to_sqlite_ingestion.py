import csv
import json
import sqlite3
from pathlib import Path

from pricepulse.adapters.csv.reader import CSVPriceSource
from pricepulse.adapters.storages.sqlite_repository import (
    SQLitePriceRepository,
)
from pricepulse.application.ingestion.models import RunStatus
from pricepulse.application.ingestion.session import IngestionSession


def write_test_csv(path: Path) -> None:
    fieldnames = [
        "event_id",
        "product_id",
        "seller_id",
        "observed_date",
        "version",
        "price_vnd",
        "original_price_vnd",
        "stock_qty",
        "updated_at",
        "currency",
        "attributes_json",
    ]

    rows = [
        {
            "event_id": "event-1",
            "product_id": "product-1",
            "seller_id": "seller-1",
            "observed_date": "2026-09-30",
            "version": "1",
            "price_vnd": "100000",
            "original_price_vnd": "120000",
            "stock_qty": "10",
            "updated_at": "2026-09-30T10:00:00",
            "currency": "VND",
            "attributes_json": json.dumps(
                {"color": "red"},
            ),
        },
        {
            "event_id": "event-invalid",
            "product_id": "product-2",
            "seller_id": "seller-1",
            "observed_date": "2026-09-30",
            # Invalid: schema yêu cầu version >= 1
            "version": "0",
            "price_vnd": "200000",
            "original_price_vnd": "220000",
            "stock_qty": "20",
            "updated_at": "2026-09-30T10:01:00",
            "currency": "VND",
            "attributes_json": json.dumps(
                {"color": "blue"},
            ),
        },
        {
            "event_id": "event-3",
            "product_id": "product-3",
            "seller_id": "seller-2",
            "observed_date": "2026-09-30",
            "version": "1",
            "price_vnd": "300000",
            "original_price_vnd": "320000",
            "stock_qty": "30",
            "updated_at": "2026-09-30T10:02:00",
            "currency": "VND",
            "attributes_json": json.dumps(
                {"color": "green"},
            ),
        },
    ]

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)


def count_database_rows(db_path: Path) -> int:
    connection = sqlite3.connect(db_path)

    try:
        cursor = connection.execute(
            "SELECT COUNT(*) FROM price_records"
        )
        row = cursor.fetchone()

        assert row is not None

        return row[0]
    finally:
        connection.close()


def test_csv_to_sqlite_ingestion_is_idempotent(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "prices.csv"
    db_path = tmp_path / "prices.db"

    write_test_csv(csv_path)

    repository = SQLitePriceRepository(db_path)

    try:
        repository.initialize()

        # -------------------------
        # RUN 1
        # -------------------------

        source = CSVPriceSource(csv_path)

        session = IngestionSession(
            repository=repository,
            source=source,
            batch_size=2,
        )

        session.run()

        first_result = session.result()

        assert first_result.status is RunStatus.COMPLETED

        assert first_result.total_rows == 3
        assert first_result.inserted_rows == 2
        assert first_result.duplicate_rows == 0
        assert first_result.failed_rows == 1

        assert len(first_result.errors) == 1
        assert first_result.run_failed is None

        assert count_database_rows(db_path) == 2

        # -------------------------
        # RUN 2 - SAME CSV
        # -------------------------

        source = CSVPriceSource(csv_path)

        session = IngestionSession(
            repository=repository,
            source=source,
            batch_size=2,
        )

        session.run()

        second_result = session.result()

        assert second_result.status is RunStatus.COMPLETED

        assert second_result.total_rows == 3

        # Không insert thêm record nào
        assert second_result.inserted_rows == 0

        # 2 valid records giờ trở thành duplicate
        assert second_result.duplicate_rows == 2

        # Invalid row vẫn invalid
        assert second_result.failed_rows == 1

        assert len(second_result.errors) == 1
        assert second_result.run_failed is None

        # Database vẫn chỉ có đúng 2 rows
        assert count_database_rows(db_path) == 2

    finally:
        repository.close()
