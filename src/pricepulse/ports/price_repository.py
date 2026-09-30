from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from pricepulse.domain.price import PriceRecord


@dataclass
class BatchSaveResult:
    inserted: int
    duplicates: int


class PriceRepository(Protocol):
    def save_batch(
        self, records: Sequence[PriceRecord]
    ) -> BatchSaveResult: ...
