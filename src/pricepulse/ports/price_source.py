from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol

from pricepulse.domain.price import PriceRecord


@dataclass(frozen=True)
class SourceError:
    error_type: str
    message: str
    location: str | None = None


@dataclass(frozen=True)
class SourceSuccess:
    record: PriceRecord


@dataclass(frozen=True)
class SourceFailure:
    error: SourceError


type SourceResult = SourceSuccess | SourceFailure


class PriceSource(Protocol):
    def read(self) -> Iterator[SourceResult]: ...
