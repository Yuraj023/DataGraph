---
type: Runbook
title: Billing Logic & Edge Cases
description: Rules for handling trials, discounts, and refunds in SQL.
---
# Billing Logic & Edge Cases

When calculating revenue metrics (like MRR), you must apply the following rules:

1. **Free Trials:** Subscriptions with `status = 'trial'` MUST be excluded from all revenue calculations.
2. **Refunds:** If a transaction has `status = 'refunded'`, it should not be counted in gross revenue.
3. **Currency:** All amounts in the database are stored in USD. No conversion is needed.