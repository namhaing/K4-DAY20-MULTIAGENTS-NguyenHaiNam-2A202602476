---
name: log-triage-output-conventions
description: Use when parsing application logs into structured error records and service summaries.
---
1. Always write service names in lower-case with `-` replaced by `_` (for example, `payment-service` becomes `payment_service`).
2. Always sort `errors` by service, then by `timestamp_utc`, ascending.
3. Always include top-level `"schema_version": 2` and `"generated_by": "log-triage"`.
4. Parse and normalize timestamps before sorting; preserve repeat counts and ensure service summaries use the normalized service names.
5. Self-check: top-level metadata is present; service names follow the convention; errors are sorted; summary totals agree with error records.
