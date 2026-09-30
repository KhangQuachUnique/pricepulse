import csv
import json
from collections.abc import Sequence
from pathlib import Path

import pytest

from pricepulse.adapters.csv.reader import CSVPriceSource
from pricepulse.application.ingestion.models import RunStatus
from pricepulse.application.ingestion.session import IngestionSession
from pricepulse.domain.price import PriceRecord
from pricepulse.ports.price_repository import BatchSaveResult


class FailingRepository:
    def __init__(self) -> None:
        self.calls = 0

    def save_batch(
        self,
        records: Sequence[PriceRecord],
    ) -> BatchSaveResult:
        self.calls += 1

        # Batch thứ 2 cố tình fail
        if self.calls == 2:
            raise RuntimeError("Database exploded")

        return BatchSaveResult(
            inserted=len(records),
            duplicates=0,
        )


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
            "attributes_json": json.dumps({"color": "red"}),
        },
        {
            "event_id": "event-2",
            "product_id": "product-2",
            "seller_id": "seller-1",
            "observed_date": "2026-09-30",
            "version": "1",
            "price_vnd": "200000",
            "original_price_vnd": "220000",
            "stock_qty": "20",
            "updated_at": "2026-09-30T10:01:00",
            "currency": "VND",
            "attributes_json": json.dumps({"color": "blue"}),
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
            "attributes_json": json.dumps({"color": "green"}),
        },
        {
            "event_id": "event-4",
            "product_id": "product-4",
            "seller_id": "seller-2",
            "observed_date": "2026-09-30",
            "version": "1",
            "price_vnd": "400000",
            "original_price_vnd": "420000",
            "stock_qty": "40",
            "updated_at": "2026-09-30T10:03:00",
            "currency": "VND",
            "attributes_json": json.dumps({"color": "black"}),
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


def test_session_becomes_failed_when_repository_fails(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "prices.csv"

    write_test_csv(csv_path)

    repository = FailingRepository()
    source = CSVPriceSource(csv_path)

    session = IngestionSession(
        source=source,
        repository=repository,
        batch_size=2,
    )

    with pytest.raises(
        RuntimeError,
        match="Database exploded",
    ):
        session.run()

    result = session.result()

    # Repository được gọi:
    # batch 1 -> success
    # batch 2 -> fail
    assert repository.calls == 2

    # Session phải chuyển sang FAILED
    assert result.status is RunStatus.FAILED

    # Error của cả run phải được lưu lại
    assert result.run_failed is not None
    assert result.run_failed.error_type == "RuntimeError"
    assert result.run_failed.message == "Database exploded"

    # 4 row đã được đọc trước khi batch thứ 2 fail
    assert result.total_rows == 4

    # Batch 1 gồm 2 row đã save thành công
    assert result.inserted_rows == 2

    assert result.duplicate_rows == 0
    assert result.failed_rows == 0
    assert result.errors == ()

    # Session đã fail thì không được chạy lại
    with pytest.raises(
        RuntimeError,
        match="already been started",
    ):
        session.run()
