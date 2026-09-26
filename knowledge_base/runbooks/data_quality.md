---
type: Runbook
title: Data Quality & SLA Standards
description: How to handle nulls, pipeline delays, and data anomalies.
owner: data-platform-team@company.com
---
# Data Quality & SLA Standards

## 1. Pipeline SLAs
- **Subscriptions & Users:** Updated every 4 hours. 99.9% of data is available by 06:00 UTC.
- **Marketing Spend:** Updated once daily at 08:00 UTC (48-hour attribution delay).

## 2. Handling NULLs
- `users.acquisition_campaign_id` will be `NULL` for organic users. This is expected. Do not filter them out unless specifically calculating *paid* CAC.
- `subscriptions.canceled_at` will be `NULL` for any subscription that is not in the `'canceled'` status.

## 3. Known Anomalies
- **August 2026 Stripe Migration:** Between `2026-08-10` and `2026-08-12`, some `transactions` were duplicated. 
- **Fix:** Always use `SELECT DISTINCT id` or `ROW_NUMBER() OVER(PARTITION BY id ORDER BY processed_at DESC) = 1` when querying the `transactions` table for dates in that range.