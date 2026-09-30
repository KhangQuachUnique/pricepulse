from dataclasses import dataclass
from enum import Enum, auto

from pricepulse.ports.price_source import SourceError


class RunStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()


@dataclass
class RunFailed:
    error_type: str
    message: str


@dataclass
class IngestionStats:
    total_rows: int = 0
    inserted_rows: int = 0
    duplicate_rows: int = 0
    failed_rows: int = 0


@dataclass(frozen=True)
class IngestionResult:
    status: RunStatus
    total_rows: int
    inserted_rows: int
    duplicate_rows: int
    failed_rows: int
    errors: tuple[SourceError, ...]
    run_failed: RunFailed | None
