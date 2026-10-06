---
name: log-json-outputs
description: Use when parsing logs into structured JSON error records and service summaries.
---
1. Always write service names in lower-case, replacing `-` with `_`.
2. Always sort `errors` by service, then by `timestamp_utc`, ascending.
3. Always include top-level `"schema_version": 2` and `"generated_by": "log-triage"`.
4. Validate the JSON and check that service totals agree with the error records and their repeat counts.
5. Self-check: verify normalized service names, sort order, required top-level fields, and totals.
