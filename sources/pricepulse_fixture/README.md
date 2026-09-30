# PricePulse — Stage 1 Python Capstone Dataset

This is a *synthetic, deterministic* data fixture, not actual shop pricing or a ready-made solution.

## Scenario
A marketplace exports product/seller price observations as daily CSV files. Later corrections may update an older observed date. A replay can deliver the same old event again, and some rows are invalid. Build a reliable *streaming* ingestion pipeline with version-aware upsert and crash-safe replay.

## Files and order
Read `input/*.csv` in ascending filename order. `2026-09-01.csv` through `2026-09-10.csv` each contain 20,000 base rows. `2026-09-11_corrections.csv` contains version 2/3 changes to prior keys, deliberately shuffled (including v3 before v2 in some cases). `2026-09-12_replay_and_dirty.csv` contains old exact replays and invalid entries mixed together.

## Schema
- `event_id`: event identity; duplicate replays copy exactly the event_id and all fields of the original.
- `product_id`: product (P00001–P05000).
- `seller_id`: seller (S01–S04).
- `observed_date`: logical price snapshot date (ISO date).
- `version`: positive integer revision of the logical record (1, 2, or 3; bad rows use 4).
- `price_vnd`: nonnegative price in VND (valid rows >=1000).
- `original_price_vnd`: strictly positive original list price.
- `stock_qty`: nonnegative integer stock.
- `updated_at`: naive ISO datetime of event publication, not snapshot date.
- `currency`: VND.
- `attributes_json`: JSON object with category, brand, shipping_days, tags.

## Contract
Natural key = (`product_id`, `seller_id`, `observed_date`). Write only the **highest valid version** per key. Replayed lower/equal versions never replace a stored newer version. When version ties exist with different payloads, report a version conflict instead of silently choosing one. Invalid rows do not stop the whole run; keep their reason and source file/line. Source rows are not guaranteed to be version-sorted within a file. Explicitly define commit/checkpoint ordering to survive a crash between DB commit and checkpoint update.

## Expected facts (acceptance oracle)
- Physical CSV rows (excluding headers): 221,000.
- Base v1: 200,000; valid v2 corrections: 12,000; valid v3 corrections: 2,000.
- Exact old replays: 5,000 (replay old v1 rows).
- Invalid entries: 2,000 (500 negative price; 500 empty product_id; 500 malformed attributes_json; 500 bad observed_date).
- Valid logical keys after complete ingestion: 200,000.
- Latest-version distribution: v1=188,000; v2=10,000; v3=2,000.
- Reprocessing all files must not alter output rows (idempotency).

The fixture itself does not include a network delay simulator, API client, solution code or benchmark results; introduce controlled/mock latency and transient/permanent errors **only in the ingestion exercise** so tests are deterministic.
