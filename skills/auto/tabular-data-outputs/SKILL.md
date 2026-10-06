---
name: tabular-data-outputs
description: Use when analyzing tabular records and producing structured JSON or cleaned CSV outputs.
---
1. Always represent money values in `answer.json` as integer cents; write 1606.67 USD as `160667`.
2. Always include `meta` in `answer.json` with the structure `{"source": <input file name>, "rows_in": <number of data rows in the input file, duplicates included>, "rows_used": <number of distinct records with a known amount>}`.
3. Always write `workspace/clean.csv` with the header `order_id,timestamp_utc,region,amount_cents`.
4. Always write one CSV row per distinct record with a known amount; format `timestamp_utc` as `YYYY-MM-DDTHH:MM:SSZ` in UTC, use canonical region spelling (`North`, `South`, `East`, `West`), and store `amount_cents` as an integer.
5. Deduplicate records before counting used rows or aggregating; exclude records with unknown amounts from amount-based outputs.
6. Self-check: verify the JSON structure, row counts, deduplication, integer cents, CSV header, and UTC timestamps.
