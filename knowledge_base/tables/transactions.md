---
type: BigQuery Table
title: Transactions
description: Individual payment and refund records.
owner: data-engineering@company.com
resource: bigquery://project-analytics.prod.transactions
---
# Transactions Table

## Schema Definition
| Column | Type | Description | Constraints / Notes |
|---|---|---|---|
| `id` | STRING | Primary Key (Stripe Charge ID) | Idempotency guaranteed. |
| `user_id` | STRING | Foreign Key to `users.id` | |
| `subscription_id` | STRING | Foreign Key to `subscriptions.id` | Null for one-time purchases. |
| `amount` | FLOAT | Transaction amount in USD. | Always positive. Refunds are separate rows. |
| `status` | STRING | Payment outcome. | Allowed: `'success'`, `'failed'`, `'refunded'`. |
| `processed_at` | TIMESTAMP | When the payment gateway processed the charge. | Use this for revenue recognition, not `created_at`. |

## Critical Business Rule
A `'refunded'` transaction does **not** negate the original `'success'` transaction row. Instead, a *new* row is created with `status = 'refunded'` and a negative `amount`. When calculating gross revenue, you must `SUM(amount)` across all statuses, or explicitly filter out `'refunded'` for net revenue. See [Billing Logic](../runbooks/billing_logic.md).