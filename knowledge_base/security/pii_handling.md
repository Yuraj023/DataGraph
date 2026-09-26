---
type: Security Policy
title: PII Handling Requirements
description: Mandatory rules for handling personally identifiable information in queries and exports.
owner: security-team@company.com
compliance: [GDPR, CCPA, SOC2]
last_audit: 2026-08-15
---
# PII Handling Requirements

## Mandatory Rules

### 1. Email Masking
- **NEVER** select raw `email` columns in analytical queries.
- Use `SHA256(email)` or `REGEXP_REPLACE(email, r'(@.*)', '@***')` for display purposes.
- Exception: Customer support queries with explicit audit logging.

### 2. User ID Anonymization
- For external reports or A/B test results, use anonymized user IDs: `CONCAT('user_', MD5(user_id))`.
- Internal dashboards may use raw `user_id` but must be access-controlled.

### 3. Geographic Data
- If querying IP addresses or location data, aggregate to city-level minimum.
- Never expose raw IP addresses in query results.

### 4. Audit Logging
- All queries touching PII tables (`users`, `user_events`) must be logged to `audit.query_log`.
- Include: query_hash, user_email, timestamp, tables_accessed.

## Enforcement
- Queries violating these rules will be blocked by the query validator.
- Repeated violations trigger automatic access revocation.