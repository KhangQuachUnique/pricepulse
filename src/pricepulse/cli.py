import argparse
from pathlib import Path

from pricepulse.adapters.csv.reader import CSVPriceSource
from pricepulse.adapters.storages.sqlite_repository import (
    SQLitePriceRepository,
)
from pricepulse.application.ingestion.session import IngestionSession


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--csv-path",
        type=Path,
        required=True,
        help="Path to input CSV file",
    )

    parser.add_argument(
        "--db",
        type=Path,
        default=Path("database/sqlite.db"),
        help="Path to SQLite database file",
    )

    args = parser.parse_args()

    repository = SQLitePriceRepository(args.db)

    try:
        repository.initialize()

        source = CSVPriceSource(args.csv_path)

        session = IngestionSession(
            repository=repository, source=source, batch_size=2000
        )

        session.run()

        result = session.result()

        print("Ingestion completed.")
        print(result)

    finally:
        repository.close()


if __name__ == "__main__":
    main()
