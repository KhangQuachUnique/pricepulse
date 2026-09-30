PricePulse

Python ingestion pipeline built as a capstone for learning
production-oriented Python fundamentals.

CSV
↓
CSVPriceSource
↓
IngestionSession
↓
PriceRepository
↓
SQLite

Features:

- Pydantic input validation
- Lazy source iteration
- Batch transactions
- Idempotent inserts
- Duplicate handling
- Row-level error handling
- Run lifecycle tracking
- Atomic rollback
- Repository / Source ports using Protocol
- Unit + integration tests
- Profiling experiments
