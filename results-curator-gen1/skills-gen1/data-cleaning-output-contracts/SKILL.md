---
name: data-cleaning-output-contracts
description: Use when transforming tabular data into cleaned files and summary outputs with prescribed schemas or normalization rules.
---
1. Read the output contract first; preserve required filenames, keys, headers, and field types exactly.
2. Count input data rows before deduplication; distinguish those from distinct entities and entities with usable values.
3. Deduplicate using the specified entity key and handle conflicting duplicates deliberately rather than selecting arbitrarily.
4. Parse money with decimal arithmetic and emit integer cents wherever required; represent unknown amounts as specified and exclude them from totals when appropriate.
5. Normalize dates and times to UTC in the required format, and map categorical values to the prescribed canonical spelling.
6. Write each required output, including `clean.csv` with its exact header and row grain when specified.
7. Populate `answer.json` metadata with the required source name and row counts when specified.
8. Validate output types, row counts, deduplication, and totals against the cleaned records.
9. Self-check: schemas exact; currencies in required units; dates and categories normalized; metadata counts consistent.
