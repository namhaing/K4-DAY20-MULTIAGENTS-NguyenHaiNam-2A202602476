---
name: log-output-normalization
description: Use when parsing application logs into structured error records and service summaries with a prescribed JSON schema.
---
1. Inspect the required JSON schema before parsing; include every required top-level key and exact constant value.
2. Parse log records and continuation lines deliberately; preserve exception details and account for repeated-message counts.
3. Normalize service names to lower case and replace hyphens with underscores when required.
4. Convert timestamps to UTC in the required representation before ordering records.
5. Sort `errors` by service, then by `timestamp_utc`, ascending when specified.
6. Compute service totals from the same normalized service names and repeat-count rules used in the error records.
7. Validate JSON syntax, required fields, ordering, normalized names, and consistency of totals.
8. Self-check: schema exact; names normalized; records sorted; totals reconcile with repeat counts.
