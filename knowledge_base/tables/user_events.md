---
type: BigQuery Table
title: User Events
description: Behavioral event stream tracking user interactions with the platform.
owner: product-analytics@company.com
resource: bigquery://project-analytics.prod.user_events
partitioning: DATE(event_date)
clustering: [user_id, event_type]
contains_pii: true
retention: 2 years
related_security:
  - ../security/pii_handling.md
---
# User Events Table

## Schema Definition
| Column | Type | Description | Constraints / Notes |
|---|---|---|---|
| `event_id` | STRING | Primary Key (UUID) | Idempotency guaranteed by client SDK. |
| `user_id` | STRING | Foreign Key to `users.id` | **PII**: Must be anonymized in external reports. |
| `event_type` | STRING | Type of user action. | Allowed: `'login'`, `'page_view'`, `'feature_used'`, `'purchase'`, `'logout'`. |
| `event_date` | DATE | Date the event occurred. | Partitioning key. |
| `event_timestamp` | TIMESTAMP | Exact timestamp of the event. | |
| `page_url` | STRING | URL where the event occurred. | |
| `feature_name` | STRING | Name of the feature used (if applicable). | Null for non-feature events. |
| `metadata` | JSON | Additional event-specific data. | Schema varies by event_type. |

## Data Quality Notes
- **Latency**: Events have a 2-hour processing delay due to client batching.
- **Deduplication**: The ingestion pipeline automatically deduplicates events based on `event_id`.
- **Late-Arriving Events**: Events may arrive up to 24 hours late. Use `event_date` (not `processed_at`) for analysis.

## Common Query Patterns
- **Daily Active Users (DAU)**: `COUNT(DISTINCT user_id) WHERE event_date = CURRENT_DATE()`
- **Feature Adoption**: `COUNT(DISTINCT user_id) WHERE feature_name = 'xyz' AND event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)`

## Security Requirements
Because this table contains `user_id` (PII), all queries must comply with [PII Handling Policy](../security/pii_handling.md). External exports require anonymization.