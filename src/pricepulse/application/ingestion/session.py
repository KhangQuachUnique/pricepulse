from pricepulse.application.ingestion.models import (
    IngestionResult,
    IngestionStats,
    RunFailed,
    RunStatus,
)
from pricepulse.domain.price import PriceRecord
from pricepulse.ports.price_repository import (
    PriceRepository,
)
from pricepulse.ports.price_source import (
    PriceSource,
    SourceError,
    SourceFailure,
)


class IngestionSession:
    def __init__(
        self,
        repository: PriceRepository,
        source: PriceSource,
        batch_size: int = 500,
    ):
        self._repository = repository
        self._source = source
        self._stats = IngestionStats()
        self._errors: list[SourceError] = []
        self._status = RunStatus.PENDING
        self._run_failed: RunFailed | None = None

        if batch_size <= 0:
            raise ValueError("batch_size must be greater than 0")
        self._batch_size = batch_size

    def _save_batch(self, batch: list[PriceRecord]) -> None:
        result = self._repository.save_batch(batch)

        self._stats.inserted_rows += result.inserted
        self._stats.duplicate_rows += result.duplicates

    def run(self) -> None:
        if self._status is not RunStatus.PENDING:
            raise RuntimeError(
                "Ingestion session has already been started."
            )

        self._status = RunStatus.RUNNING

        batch: list[PriceRecord] = []

        try:
            for item in self._source.read():
                self._stats.total_rows += 1

                if isinstance(item, SourceFailure):
                    self._stats.failed_rows += 1
                    self._errors.append(item.error)
                    continue

                batch.append(item.record)

                if len(batch) >= self._batch_size:
                    self._save_batch(batch)
                    batch.clear()

            if batch:
                self._save_batch(batch)
        except Exception as e:
            self._status = RunStatus.FAILED
            self._run_failed = RunFailed(
                error_type=type(e).__name__, message=str(e)
            )
            raise

        self._status = RunStatus.COMPLETED

    def result(self) -> IngestionResult:
        if self._status in {
            RunStatus.PENDING,
            RunStatus.RUNNING,
        }:
            raise RuntimeError("Ingestion session has not finished.")

        return IngestionResult(
            status=self._status,
            total_rows=self._stats.total_rows,
            inserted_rows=self._stats.inserted_rows,
            duplicate_rows=self._stats.duplicate_rows,
            failed_rows=self._stats.failed_rows,
            errors=tuple(self._errors),
            run_failed=self._run_failed,
        )
