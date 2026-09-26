---
type: Metric
title: Customer Acquisition Cost (CAC)
description: The average cost to acquire a single new paying customer.
owner: growth-analytics@company.com
tags: [marketing, growth, efficiency]
related_tables: 
  - ../tables/users.md
  - ../tables/marketing_spend.md
---
# Customer Acquisition Cost (CAC)

## Definition
CAC is calculated by dividing the total `spend_amount` in the `marketing_spend` table by the count of *new, first-time paying users* in the same period.

## Calculation Logic
```sql
SELECT 
  DATE_TRUNC(spend_date, MONTH) as month,
  SUM(spend_amount) / COUNT(DISTINCT user_id) as cac
FROM `project-analytics.prod.marketing_spend` ms
JOIN `project-analytics.prod.users` u 
  ON ms.campaign_id = u.acquisition_campaign_id
WHERE u.first_payment_date IS NOT NULL