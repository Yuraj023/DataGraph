---
type: BigQuery Table
title: Users
description: Master dimension table for all registered platform users.
owner: data-engineering@company.com
resource: bigquery://project-analytics.prod.users
partitioning: DATE(created_at)
pii_level: HIGH (Contains email)
---
# Users Table

## Schema Definition
| Column | Type | Description | Constraints / Notes |
|---|---|---|---|
| `id` | STRING | Primary Key (UUID) | Never null. |
| `email` | STRING | User's registered email address. | **PII**: Must be hashed or masked in non-prod environments. |
| `created_at` | TIMESTAMP | Account creation timestamp. | |
| `acquisition_channel` | STRING | How the user found us. | Allowed: `'organic'`, `'paid_search'`, `'social'`, `'referral'`. |
| `acquisition_campaign_id` | STRING | Links to `marketing_spend.campaign_id`. | Null for `'organic'` users. |
| `first_payment_date` | TIMESTAMP | Date of the first successful transaction. | Null if the user has never paid. |

## Join Patterns
- Always join to `subscriptions` on `users.id = subscriptions.user_id`.
- To calculate CAC, join to `marketing_spend` on `users.acquisition_campaign_id = marketing_spend.campaign_id`.