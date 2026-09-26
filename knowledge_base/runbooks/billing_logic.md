---
type: Runbook
title: Billing Logic & Edge Cases
description: Definitive rules for handling trials, proration, refunds, and currency in SQL.
owner: finance-ops@company.com
last_reviewed: 2026-09-15
---
# Billing Logic & Edge Cases

When writing SQL for revenue or subscription metrics, you **MUST** apply the following rules. The LLM must not hallucinate logic that contradicts these rules.

## 1. Free Trials
- Subscriptions with `is_trial = TRUE` generate $0 MRR.
- Do not count them in `active_subscriptions` counts until `is_trial` flips to `FALSE` and `status` becomes `'active'`.

## 2. Proration Logic (Mid-month upgrades/downgrades)
- If a user upgrades mid-month, Stripe creates a prorated `amount` in the `subscriptions` table for the *remainder* of the month. 
- **Rule:** Always use the `amount` column *as-is* for the specific month. Do not attempt to annualized or multiply by 30. The `amount` column already reflects the prorated value for that specific billing cycle.

## 3. Refund Handling
- Refunds are recorded as separate rows in the `transactions` table with `status = 'refunded'` and a negative `amount`.
- **Gross Revenue:** `SUM(amount)` (includes refunds as negative numbers).
- **Net Revenue:** `SUM(CASE WHEN status != 'refunded' THEN amount ELSE 0 END)`.

## 4. Currency Conversion
- All tables (`subscriptions`, `transactions`, `marketing_spend`) are pre-converted to **USD** at the daily exchange rate by the ingestion pipeline.
- **Rule:** Never apply `USD_EUR_RATE` or other FX multipliers in your analytical queries. The data is already normalized.

## 5. Late-Arriving Data
- Subscription status changes can be delayed by up to 4 hours.
- For daily dashboards, always use `WHERE processed_at <= CURRENT_TIMESTAMP()` and be aware that the last 4 hours of data may be slightly volatile.