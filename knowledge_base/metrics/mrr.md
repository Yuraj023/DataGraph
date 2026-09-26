---
type: Metric
title: Monthly Recurring Revenue (MRR)
description: Total recurring revenue from active subscriptions.
owner: data-team@company.com
tags: [finance, core-metric]
timestamp: 2026-09-26T10:00:00Z
---
# Monthly Recurring Revenue (MRR)

MRR is calculated by summing the `amount` column from the `subscriptions` table 
where the `status` is 'active'. 

**Dependencies & Context:**
- To understand the exact columns, see the [Subscriptions Table](../tables/subscriptions.md).
- For edge cases regarding trials and discounts, read the [Billing Logic Runbook](../runbooks/billing_logic.md).