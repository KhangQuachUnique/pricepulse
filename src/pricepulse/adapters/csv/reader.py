import csv
import json
from collections.abc import Iterator
from pathlib import Path

from pydantic import ValidationError

from pricepulse.adapters.csv.mapper import to_price_record
from pricepulse.adapters.csv.schema import PriceInputSchema
from pricepulse.ports.price_source import (
    SourceError,
    SourceFailure,
    SourceResult,
    SourceSuccess,
)


class CSVPriceSource:
    def __init__(self, file_path: Path):
        self._file_path = file_path

    def read(self) -> Iterator[SourceResult]:
        with self._file_path.open(
            "r", encoding="utf-8", newline=""
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    row["attributes_json"] = json.loads(
                        row["attributes_json"]
                    )

                    schema = PriceInputSchema.model_validate(row)

                    record = to_price_record(schema)

                    yield SourceSuccess(record=record)
                except (json.JSONDecodeError, ValidationError) as exc:
                    yield SourceFailure(
                        error=SourceError(
                            error_type=type(exc).__name__,
                            message=str(exc),
                            location=f"Line {reader.line_num}",
                        )
                    )
